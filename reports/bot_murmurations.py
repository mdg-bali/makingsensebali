#!/usr/bin/env python3
"""
Bali Air Quality Reporter — WhatsApp bot (PLANETAI Community node)

Transport:   Evolution API (Baileys-in-Docker) webhook → this Flask app
Storage:    reports/  (canonical, with sender, image paths — NAS-only)
            profiles/ (sanitized Murmurations profiles — public via rsync)
            images/   (raw user photos — NAS-only unless published with consent)
            vision_queue/ (jobs for the M1 worker)
Vision:     async — bot acknowledges immediately, M1 worker fills in later
Consent:    explicit opt-in (Bahasa primary), stored in consent.json,
            /optout supported. No data is federated for non-consented senders.

Run locally:
    pip install -r requirements.txt
    AQ_VISION_BACKEND=mock python bot_murmurations.py
    # then POST a test payload to http://localhost:5055/webhook
"""

import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from flask import Flask, jsonify, request

from murmurations_adapter import (
    MurmurationsConfig,
    PlanetAINode,
)
from vision_analyzer import analyze_pollution_image
from sessions import (
    AWAIT_CATEGORY,
    AWAIT_DETAIL,
    AWAIT_LOCATION,
    AWAIT_PHOTO,
    AWAIT_CONFIRM,
    SessionStore,
)
from messages import (
    CONSENT_PROMPT,
    CONSENT_CONFIRMED,
    CONSENT_KEYWORDS,
    OPTOUT_CONFIRMED,
    HELP_REPLY,
    STATS_REPLY,
    ABOUT_REPLY,
    UNKNOWN_COMMAND,
    LOCATION_INVALID,
    AUDIO_RECEIVED,
    # New guided-flow messages
    CATEGORY_MENU,
    CATEGORY_MENU_ITEMS,
    CATEGORY_CHOSEN,
    CATEGORY_EMOJI,
    INVALID_CATEGORY,
    DETAIL_SKIP_KEYWORDS,
    ASK_LOCATION,
    ASK_LOCATION_AFTER_SKIP,
    ASK_PHOTO,
    PHOTO_FETCH_FAILED,
    REPORT_SUMMARY,
    SUMMARY_DETAIL_LINE,
    CONFIRM_SEND_KEYWORDS,
    CONFIRM_CANCEL_KEYWORDS,
    REPORT_SUBMITTED,
    POSTSUBMIT_NEW_KEYWORDS,
    POSTSUBMIT_INFO_KEYWORDS,
    POSTSUBMIT_STATS_KEYWORDS,
    INFO_REPLY,
    CANCEL_CONFIRMED,
    WRONG_STEP_AWAIT_CATEGORY,
    WRONG_STEP_AWAIT_DETAIL,
    WRONG_STEP_AWAIT_LOCATION,
    WRONG_STEP_AWAIT_PHOTO,
    WRONG_STEP_AWAIT_CONFIRM,
)

# --- Paths -----------------------------------------------------------------

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "reports"
PROFILE_DIR = ROOT / "profiles"
IMAGE_DIR = ROOT / "images"
# EXIF-stripped photos that have been explicitly approved for public
# publication. sync_profiles.sh copies these into the GitHub repo.
# The raw photos in IMAGE_DIR never leave the NAS.
PROFILE_PHOTOS_DIR = ROOT / "profile_photos"
VISION_QUEUE = ROOT / "vision_queue"
CONFIG_FILE = ROOT / "config.json"
CONSENT_FILE = ROOT / "consent.json"
SESSIONS_FILE = ROOT / "sessions.json"

for d in (DATA_DIR, PROFILE_DIR, IMAGE_DIR, PROFILE_PHOTOS_DIR, VISION_QUEUE):
    d.mkdir(exist_ok=True)

# --- Logging ---------------------------------------------------------------

logging.basicConfig(
    level=os.environ.get("AQ_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("aq-bot")

# --- Config ----------------------------------------------------------------

DEFAULT_CONFIG = {
    "node_id": "bali.fab.city",
    "bioregion": "indo_pacific_coral_triangle",
    "primary_url": "https://planetai.fab.city/bali",
    "murmurations_auto_index": False,  # Flip to True once profiles are public
    "evolution_api": {
        # Outbound replies — Evolution API runs in Docker on the NAS
        "base_url": "http://localhost:8080",
        "instance": "bali-aq",
        "api_key": "",  # set in config.json or via AQ_EVOLUTION_KEY env
    },
    "synchronous_vision": False,  # If true, run vision inline (dev only)
    "admin_numbers": [],

    # --- Allowlist (critical when running on a personal WhatsApp number) ---
    # "open"   = everyone can message the bot (use only with a dedicated number)
    # "strict" = only senders in allowed_senders are processed; everyone else
    #            is silently ignored. No reports saved, no replies sent.
    "allowlist_mode": "strict",
    "allowed_senders": [],  # phone numbers in E.164 format, e.g. "+6281234567890"
}


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            cfg.update(json.loads(CONFIG_FILE.read_text()))
        except json.JSONDecodeError as e:
            log.warning("config.json parse error, using defaults: %s", e)
    # Env override for the API key — keeps secrets out of the repo
    env_key = os.environ.get("AQ_EVOLUTION_KEY")
    if env_key:
        cfg.setdefault("evolution_api", {})["api_key"] = env_key
    return cfg


# --- Consent ---------------------------------------------------------------
# All user-facing strings live in messages.py for native-speaker review.

def _load_consent() -> Dict[str, str]:
    if CONSENT_FILE.exists():
        try:
            return json.loads(CONSENT_FILE.read_text())
        except json.JSONDecodeError:
            log.warning("consent.json corrupt, starting fresh")
    return {}


def _save_consent(state: Dict[str, str]) -> None:
    CONSENT_FILE.write_text(json.dumps(state, indent=2))


def _sender_key(sender: str) -> str:
    """Stable, non-reversible key for consent tracking."""
    return hashlib.sha256(sender.encode()).hexdigest()[:16]


def get_consent(sender: str) -> str:
    """Returns 'granted', 'optout', or 'unknown'."""
    return _load_consent().get(_sender_key(sender), "unknown")


def set_consent(sender: str, status: str) -> None:
    state = _load_consent()
    state[_sender_key(sender)] = status
    _save_consent(state)


# --- Report storage --------------------------------------------------------

def _new_report_id() -> str:
    return f"AQ_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"


def save_report(data: Dict[str, Any]) -> str:
    """Persist a report to reports/ and return its id.

    New reports always start with review_status='pending'. They will not
    be published to profiles/ (and therefore not federated) until an
    admin approves them via /admin/approve-report.
    """
    report_id = data.get("id") or _new_report_id()
    data["id"] = report_id
    data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    data.setdefault("source", "whatsapp")
    # Approval gate — new reports are pending until reviewed
    data.setdefault("review_status", "pending")

    (DATA_DIR / f"{report_id}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False)
    )

    daily = DATA_DIR / f"reports_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with daily.open("a") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    return report_id


def load_report(report_id: str) -> Optional[Dict[str, Any]]:
    p = DATA_DIR / f"{report_id}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def update_report(report_id: str, **patch: Any) -> Optional[Dict[str, Any]]:
    r = load_report(report_id)
    if not r:
        return None
    r.update(patch)
    (DATA_DIR / f"{report_id}.json").write_text(
        json.dumps(r, indent=2, ensure_ascii=False)
    )
    return r


def merge_pending_location(sender_hash: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Attach a freshly-arrived location to the sender's most recent pending report."""
    candidates = sorted(
        DATA_DIR.glob("AQ_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for p in candidates[:50]:  # bound the scan
        r = json.loads(p.read_text())
        if r.get("sender_hash") == sender_hash and r.get("status") == "pending":
            r["location"] = {"lat": lat, "lon": lon}
            r["status"] = "complete"
            p.write_text(json.dumps(r, indent=2, ensure_ascii=False))
            return r
    return None


# --- Public-photo prep -----------------------------------------------------

def _exif_stripped_jpeg(src_path: Path, dst_path: Path) -> bool:
    """Re-encode a raw photo as a clean JPEG at dst with EXIF removed.

    We re-encode (rather than copying raw bytes) specifically to drop
    EXIF metadata — GPS coordinates, camera serial number, embedded
    thumbnails, all of which would de-anonymize the reporter even
    though we've already hashed their phone number.

    Pillow is the dependency. If it isn't available, we fail closed:
    return False, callers must NOT fall back to a raw byte-copy. The
    EXIF leak risk is bigger than the inconvenience of not publishing.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        log.error(
            "Pillow not available — refusing to publish photo without "
            "EXIF strip. Add `pillow` to requirements.txt and rebuild."
        )
        return False
    try:
        with Image.open(src_path) as img:
            # Apply orientation EXIF physically, then save without EXIF.
            img = ImageOps.exif_transpose(img)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(dst_path, "JPEG", quality=85, optimize=True)
        return True
    except Exception as e:  # noqa: BLE001 — any failure here means don't publish
        log.error("EXIF strip failed for %s: %s", src_path, e)
        return False


# --- Vision queue (async) --------------------------------------------------

def enqueue_vision_job(report_id: str, image_path: Path) -> None:
    job = {
        "report_id": report_id,
        "image_path": str(image_path),
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    (VISION_QUEUE / f"{report_id}.json").write_text(json.dumps(job, indent=2))


# --- WhatsApp send (Evolution API) ----------------------------------------

class WhatsAppSender:
    """Thin wrapper around Evolution API's text-send endpoint."""

    def __init__(self, cfg: Dict[str, Any]):
        api = cfg.get("evolution_api", {})
        self.base = api.get("base_url", "").rstrip("/")
        self.instance = api.get("instance", "")
        self.key = api.get("api_key", "")
        self.enabled = bool(self.base and self.instance)

    def send_text(self, number: str, text: str) -> bool:
        if not self.enabled:
            log.info("[DRY-RUN reply to %s] %s", number, text[:120])
            return True
        url = f"{self.base}/message/sendText/{self.instance}"
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["apikey"] = self.key
        try:
            r = requests.post(
                url,
                json={"number": number, "text": text},
                headers=headers,
                timeout=15,
            )
            r.raise_for_status()
            return True
        except requests.RequestException as e:
            log.error("send_text failed: %s", e)
            return False

    def download_media_decrypted(self, message_id: str) -> Optional[bytes]:
        """Fetch decrypted media bytes for a WhatsApp message.

        WhatsApp media is end-to-end encrypted. The `url` field in an
        imageMessage points to the *ciphertext* on WhatsApp's CDN —
        useless without the per-message media key. Evolution API
        exposes a server-side decrypt endpoint that returns the
        plaintext as base64.

        Returns the decoded bytes, or None if decrypt fails for any
        reason (callers should keep the user in AWAIT_PHOTO and ask
        them to retry rather than committing a broken report).
        """
        if not self.enabled or not message_id:
            return None
        url = f"{self.base}/chat/getBase64FromMediaMessage/{self.instance}"
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["apikey"] = self.key
        try:
            r = requests.post(
                url,
                json={
                    "message": {"key": {"id": message_id}},
                    "convertToMp4": False,
                },
                headers=headers,
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            log.error("media decrypt POST failed for %s: %s", message_id, e)
            return None
        except ValueError as e:  # JSON parse error
            log.error("media decrypt response not JSON for %s: %s", message_id, e)
            return None

        b64 = data.get("base64") if isinstance(data, dict) else None
        if not b64:
            log.warning("media decrypt returned no base64 for %s: %s", message_id, data)
            return None
        try:
            import base64 as _b64
            return _b64.b64decode(b64, validate=True)
        except (ValueError, TypeError) as e:
            log.error("base64 decode failed for %s: %s", message_id, e)
            return None


# --- Evolution API webhook parsing ----------------------------------------

_JID_RE = re.compile(r"^(\d+)@")


def _phone_from_jid(jid: str) -> str:
    m = _JID_RE.match(jid or "")
    return f"+{m.group(1)}" if m else (jid or "unknown")


def parse_evolution_webhook(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize an Evolution API message payload into our internal shape.
    Returns None if the event is something we don't handle (e.g. status updates).
    """
    if not isinstance(payload, dict):
        return None
    if payload.get("event") not in (None, "messages.upsert", "MESSAGES_UPSERT"):
        return None

    data = payload.get("data") or payload
    key = data.get("key") or {}
    if key.get("fromMe"):
        return None  # ignore our own outbound

    msg = data.get("message") or {}
    sender = _phone_from_jid(key.get("remoteJid", ""))
    sender_name = data.get("pushName") or ""
    ts = data.get("messageTimestamp")
    if isinstance(ts, (int, float)):
        ts_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    else:
        ts_iso = datetime.now(timezone.utc).isoformat()

    # Detect message type
    if "conversation" in msg or "extendedTextMessage" in msg:
        text = msg.get("conversation") or msg.get("extendedTextMessage", {}).get("text", "")
        return {
            "sender": sender,
            "sender_name": sender_name,
            "timestamp": ts_iso,
            "type": "text",
            "text": text,
        }
    if "imageMessage" in msg:
        im = msg["imageMessage"]
        return {
            "sender": sender,
            "sender_name": sender_name,
            "timestamp": ts_iso,
            "type": "image",
            "text": im.get("caption", ""),
            "image_url": im.get("url"),
            "media_key": key.get("id"),
            "mimetype": im.get("mimetype", "image/jpeg"),
        }
    if "locationMessage" in msg:
        lm = msg["locationMessage"]
        return {
            "sender": sender,
            "sender_name": sender_name,
            "timestamp": ts_iso,
            "type": "location",
            "latitude": lm.get("degreesLatitude"),
            "longitude": lm.get("degreesLongitude"),
        }
    if "audioMessage" in msg:
        return {
            "sender": sender,
            "sender_name": sender_name,
            "timestamp": ts_iso,
            "type": "audio",
            "media_key": key.get("id"),
            "mimetype": msg["audioMessage"].get("mimetype", "audio/ogg"),
        }
    return None


# --- Bot core --------------------------------------------------------------

class AQBot:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.sender = WhatsAppSender(cfg)
        self.node = PlanetAINode(
            MurmurationsConfig(
                node_id=cfg["node_id"],
                bioregion=cfg["bioregion"],
                primary_url=cfg["primary_url"],
                use_test_index=True,
                auto_index=cfg.get("murmurations_auto_index", False),
            )
        )
        # Per-sender draft sessions for the guided reporting flow.
        # One JSON file on disk, keyed by sender_hash. See sessions.py.
        self.sessions = SessionStore(SESSIONS_FILE)
        log.info("AQBot ready — node=%s", cfg["node_id"])

    # ---- allowlist / consent / commands ----

    def _is_allowed_sender(self, sender: str) -> bool:
        """
        Allowlist filter — critical for personal-number pilots.

        Modes:
          "open"   → everyone allowed (only safe with a dedicated bot number)
          "strict" → only senders in config["allowed_senders"] are processed
        """
        mode = self.cfg.get("allowlist_mode", "strict")
        if mode == "open":
            return True
        # strict mode
        allowed = self.cfg.get("allowed_senders", []) or []
        # Normalize — strip whitespace, ensure leading + (E.164 format)
        normalized = sender.strip() if sender else ""
        return normalized in [a.strip() for a in allowed]

    def _gate_consent(self, msg: Dict[str, Any]) -> Optional[str]:
        """
        Returns a reply string if we should respond now without processing,
        or None if the caller may proceed with normal handling.

        On a fresh consent grant we ALSO seed a new draft session and
        append the category menu, so the user sees the report flow start
        immediately rather than having to send a second message first.
        """
        sender = msg["sender"]
        status = get_consent(sender)
        text = (msg.get("text") or "").strip().lower()

        if text == "/optout":
            set_consent(sender, "optout")
            # If they had a draft in progress, drop it on opt-out.
            self.sessions.clear(_sender_key(sender))
            return OPTOUT_CONFIRMED

        if status == "granted":
            return None

        # Anything else from an opted-out user re-prompts consent
        if text in CONSENT_KEYWORDS:
            set_consent(sender, "granted")
            # Start a fresh draft so the very next message lands in
            # the category step without needing a second prompt.
            self.sessions.start(_sender_key(sender))
            return CONSENT_CONFIRMED + "\n\n" + CATEGORY_MENU

        return CONSENT_PROMPT

    # ---- universal commands (work at any session state) -----------------

    def _universal_command(self, msg: Dict[str, Any]) -> Optional[str]:
        """
        Slash-command shortcuts that should always work, regardless of
        what step of the report flow the user is in. Returns the reply
        text if a command was matched, or None to let the state machine
        handle the message normally.
        """
        text = (msg.get("text") or "").strip().lower()
        if not text.startswith("/"):
            return None
        cmd = text.split()[0]
        sender_hash = _sender_key(msg["sender"])

        if cmd in ("/batal", "/cancel"):
            had_draft = self.sessions.has_active(sender_hash)
            self.sessions.clear(sender_hash)
            return CANCEL_CONFIRMED if had_draft else (
                "Tidak ada laporan aktif untuk dibatalkan.\n"
                "_No active report to cancel._\n\n"
                "Ketik */baru* untuk mulai laporan, atau */info* untuk info.\n"
                "_Type */new* to start a report, or */info* for info._"
            )

        if cmd in ("/baru", "/new"):
            self.sessions.start(sender_hash)
            return CATEGORY_MENU

        if cmd == "/info":
            return INFO_REPLY

        if cmd == "/help":
            return HELP_REPLY

        if cmd == "/about":
            return ABOUT_REPLY

        if cmd == "/stats":
            return self._stats_reply()

        return UNKNOWN_COMMAND

    def _stats_reply(self) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        daily = DATA_DIR / f"reports_{today}.jsonl"
        count = sum(1 for _ in daily.open()) if daily.exists() else 0
        return STATS_REPLY.format(count=count)

    # ---- guided-flow state handlers -------------------------------------

    def _state_await_category(self, msg: Dict[str, Any], session) -> str:
        max_n = len(CATEGORY_MENU_ITEMS)
        if msg.get("type") != "text":
            return WRONG_STEP_AWAIT_CATEGORY.format(max=max_n)
        text = (msg.get("text") or "").strip()
        try:
            n = int(text)
        except ValueError:
            return INVALID_CATEGORY.format(max=max_n)
        if not (1 <= n <= max_n):
            return INVALID_CATEGORY.format(max=max_n)

        key, emoji, bah, eng = CATEGORY_MENU_ITEMS[n - 1]
        session.draft["category"] = key
        session.draft["category_label_bahasa"] = bah
        session.draft["category_label_en"] = eng
        session.state = AWAIT_DETAIL
        self.sessions.update(session)
        return CATEGORY_CHOSEN.format(
            cat_emoji=emoji, cat_label=bah, cat_label_en=eng
        )

    def _state_await_detail(self, msg: Dict[str, Any], session) -> str:
        if msg.get("type") != "text":
            return WRONG_STEP_AWAIT_DETAIL
        text = (msg.get("text") or "").strip()
        session.state = AWAIT_LOCATION
        if text.lower() in DETAIL_SKIP_KEYWORDS:
            self.sessions.update(session)
            return ASK_LOCATION_AFTER_SKIP
        session.draft["description"] = text
        self.sessions.update(session)
        return ASK_LOCATION

    def _state_await_location(self, msg: Dict[str, Any], session) -> str:
        if msg.get("type") != "location":
            return WRONG_STEP_AWAIT_LOCATION
        lat = msg.get("latitude")
        lon = msg.get("longitude")
        if lat is None or lon is None:
            return LOCATION_INVALID
        session.draft["location"] = {"lat": lat, "lon": lon}
        session.state = AWAIT_PHOTO
        self.sessions.update(session)
        return ASK_PHOTO

    def _state_await_photo(self, msg: Dict[str, Any], session) -> str:
        if msg.get("type") != "image":
            return WRONG_STEP_AWAIT_PHOTO

        # Reserve a stable report id at photo time so the image file and
        # the eventual saved report share an id.
        rid = session.draft.get("id") or _new_report_id()
        session.draft["id"] = rid

        # WhatsApp media is E2EE. The imageMessage.url field points at
        # encrypted ciphertext on WhatsApp's CDN; fetching it directly
        # gives unusable random bytes. We must use Evolution API's
        # decrypt endpoint, which returns plaintext as base64.
        media_id = msg.get("media_key")
        image_bytes = (
            self.sender.download_media_decrypted(media_id) if media_id else None
        )
        if not image_bytes:
            # Stay in AWAIT_PHOTO so the user can retry. Don't advance
            # to confirm — the report would be unreviewable without
            # a real photo.
            log.warning(
                "photo decrypt failed for sender_hash=%s media_id=%s — asking retry",
                session.sender_hash, media_id,
            )
            return PHOTO_FETCH_FAILED

        # Pick extension from declared mimetype, falling back to JPEG —
        # WhatsApp basically always sends JPEG for camera/gallery photos.
        mime = (msg.get("mimetype") or "image/jpeg").lower()
        if "png" in mime:
            ext = ".png"
        elif "webp" in mime:
            ext = ".webp"
        else:
            ext = ".jpg"
        image_path = IMAGE_DIR / f"{rid}{ext}"
        try:
            image_path.write_bytes(image_bytes)
        except OSError as e:
            log.error("could not write image %s: %s", image_path, e)
            return PHOTO_FETCH_FAILED

        session.draft["image_path"] = str(image_path)
        session.draft["media_key"] = media_id
        session.draft["mimetype"] = mime
        session.state = AWAIT_CONFIRM
        self.sessions.update(session)
        return self._format_summary(session)

    def _state_await_confirm(self, msg: Dict[str, Any], session) -> str:
        if msg.get("type") != "text":
            return WRONG_STEP_AWAIT_CONFIRM
        text = (msg.get("text") or "").strip().lower()
        if text in CONFIRM_SEND_KEYWORDS:
            rid = self._commit_draft(session)
            self.sessions.clear(session.sender_hash)
            log.info("report submitted: %s", rid)
            return REPORT_SUBMITTED
        if text in CONFIRM_CANCEL_KEYWORDS:
            self.sessions.clear(session.sender_hash)
            return CANCEL_CONFIRMED
        return WRONG_STEP_AWAIT_CONFIRM

    # ---- helpers -------------------------------------------------------

    def _format_summary(self, session) -> str:
        d = session.draft
        cat_key = d.get("category", "other")
        emoji = CATEGORY_EMOJI.get(cat_key, "📋")
        bah = d.get("category_label_bahasa", cat_key)
        eng = d.get("category_label_en", cat_key)
        detail = d.get("description", "")
        detail_line = SUMMARY_DETAIL_LINE.format(detail=detail) if detail else ""
        loc = d.get("location") or {}
        lat = float(loc.get("lat") or 0.0)
        lon = float(loc.get("lon") or 0.0)
        return REPORT_SUMMARY.format(
            cat_emoji=emoji,
            cat_label=bah,
            cat_label_en=eng,
            detail_line=detail_line,
            lat=lat,
            lon=lon,
        )

    def _commit_draft(self, session) -> str:
        """Persist the completed draft as a pending-review report.

        Approval flow is unchanged: review_status='pending' until an
        admin approves via /admin/approve-report. Only then is a profile
        published and synced to the public dashboard.
        """
        d = session.draft
        rid = d.get("id") or _new_report_id()
        report = {
            "id": rid,
            "sender_hash": session.sender_hash,
            "type": "photo",  # complete reports always include a photo
            "category": d.get("category"),
            "category_label_bahasa": d.get("category_label_bahasa"),
            "description": d.get("description", ""),
            "location": d.get("location"),
            "image_path": d.get("image_path"),
            "media_key": d.get("media_key"),
            "mimetype": d.get("mimetype"),
            "ai_analysis": None,
            "status": "complete",
        }
        save_report(report)

        # Hand off vision analysis (async via the M1 worker by default).
        image_path = d.get("image_path")
        if image_path and self.cfg.get("synchronous_vision"):
            try:
                result = analyze_pollution_image(image_path)
                update_report(
                    rid,
                    ai_analysis=result,
                    category_ai=result.get("category"),
                )
            except Exception as e:  # noqa: BLE001
                log.error("sync vision failed for %s: %s", rid, e)
        elif image_path:
            enqueue_vision_job(rid, Path(image_path))

        return rid

    # ---- federation ----------------------------------------------------

    def _publish_profile(self, report_id: str) -> None:
        """Convert the canonical report to a sanitized Murmurations profile."""
        report = load_report(report_id)
        if not report:
            return
        # The adapter ignores sender/sender_hash automatically; we also
        # strip image_path here to be doubly safe.
        sanitized = {k: v for k, v in report.items()
                     if k not in ("sender", "sender_hash", "image_path", "media_key")}
        try:
            self.node.process_report(sanitized)
        except Exception as e:  # noqa: BLE001
            log.error("publish failed for %s: %s", report_id, e)

    # ---- top-level dispatch -------------------------------------------

    def process(self, msg: Dict[str, Any]) -> Optional[str]:
        """Returns the reply text, or None if we shouldn't reply.

        Routing order:
          1. Allowlist gate (silent drop if not allowed)
          2. Consent gate (and seed session on fresh grant)
          3. Universal slash commands (/baru, /info, /help, /batal, ...)
          4. Post-submit menu shortcuts (1/2/3) when no active session
          5. State-machine dispatch on the active draft session
        """
        sender = msg.get("sender", "")

        # 1. Allowlist
        if not self._is_allowed_sender(sender):
            log.info("dropped (not in allowlist): %s", sender)
            return None

        # 2. Consent
        gate = self._gate_consent(msg)
        if gate is not None:
            return gate

        # 3. Universal commands
        cmd_reply = self._universal_command(msg)
        if cmd_reply is not None:
            return cmd_reply

        sender_hash = _sender_key(sender)
        session = self.sessions.get(sender_hash)

        # 4. Post-submit / no-active-session handling
        if session is None:
            if msg.get("type") == "text":
                text = (msg.get("text") or "").strip().lower()
                if text in POSTSUBMIT_NEW_KEYWORDS:
                    self.sessions.start(sender_hash)
                    return CATEGORY_MENU
                if text in POSTSUBMIT_INFO_KEYWORDS:
                    return INFO_REPLY
                if text in POSTSUBMIT_STATS_KEYWORDS:
                    return self._stats_reply()
            elif msg.get("type") == "audio":
                # We don't process audio (yet) — let the user know but
                # don't start a draft from it.
                return AUDIO_RECEIVED
            # Default: start a fresh report flow.
            self.sessions.start(sender_hash)
            return CATEGORY_MENU

        # 5. State dispatch
        handlers = {
            AWAIT_CATEGORY: self._state_await_category,
            AWAIT_DETAIL: self._state_await_detail,
            AWAIT_LOCATION: self._state_await_location,
            AWAIT_PHOTO: self._state_await_photo,
            AWAIT_CONFIRM: self._state_await_confirm,
        }
        handler = handlers.get(session.state)
        if not handler:
            # Defensive — corrupt state, reset and restart cleanly.
            log.error(
                "unknown session state %s for %s — restarting",
                session.state, sender_hash,
            )
            self.sessions.start(sender_hash)
            return CATEGORY_MENU

        # Audio is never a valid step input — bail out before handler so
        # the user gets a clear "not supported yet" reply.
        if msg.get("type") == "audio":
            return AUDIO_RECEIVED

        return handler(msg, session)


# --- Flask app -------------------------------------------------------------

def create_app(bot: Optional[AQBot] = None) -> Flask:
    app = Flask(__name__)
    cfg = load_config()
    bot = bot or AQBot(cfg)

    @app.get("/health")
    def health():
        return jsonify(ok=True, node=cfg["node_id"], time=datetime.now(timezone.utc).isoformat())

    @app.post("/webhook")
    def webhook():
        payload = request.get_json(silent=True) or {}
        msg = parse_evolution_webhook(payload)
        if not msg:
            return jsonify(ok=True, handled=False)

        log.info("msg from %s type=%s", msg["sender"], msg["type"])
        reply = bot.process(msg)
        if reply:
            bot.sender.send_text(msg["sender"], reply)
        return jsonify(ok=True, handled=True)

    def _check_admin_auth() -> bool:
        provided = request.headers.get("X-Admin-Key", "")
        expected = bot.cfg.get("evolution_api", {}).get("api_key", "") \
                    or os.environ.get("AQ_EVOLUTION_KEY", "")
        return bool(expected) and provided == expected

    @app.post("/admin/reload-config")
    def reload_config():
        """Re-read config.json. Used by dashboard after allowlist edits."""
        if not _check_admin_auth():
            return jsonify(ok=False, error="unauthorized"), 401
        try:
            bot.cfg = load_config()
            log.info(
                "config reloaded — allowlist mode=%s, %d allowed senders",
                bot.cfg.get("allowlist_mode"),
                len(bot.cfg.get("allowed_senders", [])),
            )
            return jsonify(
                ok=True,
                allowlist_mode=bot.cfg.get("allowlist_mode"),
                allowed_count=len(bot.cfg.get("allowed_senders", [])),
            )
        except Exception as e:  # noqa: BLE001
            log.exception("reload failed")
            return jsonify(ok=False, error=str(e)), 500

    @app.post("/admin/approve-report")
    def approve_report():
        """
        Mark a report as approved and publish its Murmurations profile.
        After this, the profile is in profiles/ and ready to be synced
        to planetai.fab.city and the public dashboard.

        Optional body field `include_photo` (bool, default false): when
        true, the photo is EXIF-stripped and written into PROFILE_PHOTOS_DIR
        so sync_profiles.sh can push it to the public repo. When false
        (the default), the photo stays NAS-only and the published
        profile has no photo_path.
        """
        if not _check_admin_auth():
            return jsonify(ok=False, error="unauthorized"), 401
        body = request.get_json(silent=True) or {}
        report_id = body.get("report_id", "")
        include_photo = bool(body.get("include_photo", False))
        if not report_id:
            return jsonify(ok=False, error="missing report_id"), 400

        report = load_report(report_id)
        if not report:
            return jsonify(ok=False, error="report not found"), 404

        # --- Optional: prep a public-safe copy of the photo --------------
        # We do this BEFORE marking the report approved so a failed
        # EXIF-strip doesn't leave us with an approved report whose
        # photo silently never reaches the public side.
        public_photo_relpath: Optional[str] = None
        if include_photo:
            src = report.get("image_path")
            if not src:
                return jsonify(
                    ok=False,
                    error="include_photo set but report has no image_path",
                ), 400
            src_p = Path(src)
            if not src_p.exists():
                return jsonify(
                    ok=False,
                    error=f"photo file missing on disk: {src}",
                ), 404
            # Always re-encode as JPEG for the public copy. Consistent
            # format on the public side, smaller files, and the re-encode
            # naturally drops everything Pillow doesn't recognize.
            dst_p = PROFILE_PHOTOS_DIR / f"{report_id}.jpg"
            if not _exif_stripped_jpeg(src_p, dst_p):
                return jsonify(
                    ok=False,
                    error="photo prep failed (EXIF strip)",
                ), 500
            public_photo_relpath = f"photos/{report_id}.jpg"

        # --- Mark approved on the canonical record -----------------------
        report["review_status"] = "approved"
        report["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        # Audit trail — easy to filter later for "which reports had
        # their photo published". Survives even if the public photo
        # is later removed from the repo.
        report["photo_published"] = bool(public_photo_relpath)
        if public_photo_relpath:
            report["photo_public_path"] = public_photo_relpath
        (DATA_DIR / f"{report_id}.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )

        # --- Sanitize for federation ------------------------------------
        # Strip everything that could de-anonymize: sender, sender_hash,
        # raw image_path (server-internal), media_key. Audit-only fields
        # (photo_published, photo_public_path) are also stripped from
        # the sanitized profile — they're for the operator, not the
        # public. If a photo IS being published, we expose it as
        # photo_path, a clean relative URL the public dashboard can use.
        _PRIVATE_KEYS = {
            "sender", "sender_hash", "image_path", "media_key",
            "photo_published", "photo_public_path",
        }
        sanitized = {k: v for k, v in report.items() if k not in _PRIVATE_KEYS}
        if public_photo_relpath:
            sanitized["photo_path"] = public_photo_relpath

        try:
            bot.node.process_report(sanitized)
            log.info(
                "approved + published: %s (photo=%s)",
                report_id, bool(public_photo_relpath),
            )
            return jsonify(
                ok=True,
                report_id=report_id,
                review_status="approved",
                photo_published=bool(public_photo_relpath),
            )
        except Exception as e:  # noqa: BLE001
            log.exception("publish failed for %s", report_id)
            return jsonify(ok=False, error=f"publish failed: {e}"), 500

    @app.post("/admin/reject-report")
    def reject_report():
        """
        Mark a report as rejected — does NOT publish a profile. The report
        stays in reports/ for the record but never becomes federated.
        """
        if not _check_admin_auth():
            return jsonify(ok=False, error="unauthorized"), 401
        body = request.get_json(silent=True) or {}
        report_id = body.get("report_id", "")
        reason = body.get("reason", "")
        if not report_id:
            return jsonify(ok=False, error="missing report_id"), 400

        report = load_report(report_id)
        if not report:
            return jsonify(ok=False, error="report not found"), 404

        report["review_status"] = "rejected"
        report["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        if reason:
            report["rejection_reason"] = reason
        (DATA_DIR / f"{report_id}.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )
        log.info("rejected: %s (%s)", report_id, reason or "no reason")
        return jsonify(ok=True, report_id=report_id, review_status="rejected")

    @app.post("/admin/delete-report")
    def delete_report():
        """
        Take an approved (already-published) report off the public site.

        - Removes the sanitized profile from PROFILE_DIR.
        - Removes the public photo from PROFILE_PHOTOS_DIR (if any).
        - Marks the canonical report as review_status="deleted" — the
          canonical JSON + raw image stay on the NAS so we keep an
          audit trail of what existed and was taken down.

        sync_profiles.sh's --delete-after rsyncs (for both JSON and JPG
        targets) propagate the removal to the GitHub clone on the next
        sync tick. Next push then removes them from the public site.
        """
        if not _check_admin_auth():
            return jsonify(ok=False, error="unauthorized"), 401
        body = request.get_json(silent=True) or {}
        report_id = body.get("report_id", "")
        reason = body.get("reason", "")
        if not report_id:
            return jsonify(ok=False, error="missing report_id"), 400

        report = load_report(report_id)
        if not report:
            return jsonify(ok=False, error="report not found"), 404

        # Pull both files off the publish side. Use missing_ok so the
        # endpoint is idempotent — admin can hit delete twice safely.
        profile_path = PROFILE_DIR / f"{report_id}.json"
        photo_path = PROFILE_PHOTOS_DIR / f"{report_id}.jpg"
        removed = []
        try:
            profile_path.unlink(missing_ok=True)
            removed.append("profile")
        except OSError as e:
            log.error("could not remove profile %s: %s", profile_path, e)
        try:
            photo_path.unlink(missing_ok=True)
            if photo_path.exists() is False:
                # We don't always have a profile photo; only log if
                # one was actually deleted.
                pass
            removed.append("profile_photo_if_present")
        except OSError as e:
            log.error("could not remove profile photo %s: %s", photo_path, e)

        # Audit trail: keep the canonical record + the raw image, but
        # mark the report as deleted from public.
        report["review_status"] = "deleted"
        report["deleted_at"] = datetime.now(timezone.utc).isoformat()
        if reason:
            report["deletion_reason"] = reason
        report["photo_published"] = False
        (DATA_DIR / f"{report_id}.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )
        log.info(
            "deleted from public: %s — removed=%s (%s)",
            report_id, removed, reason or "no reason",
        )
        return jsonify(
            ok=True,
            report_id=report_id,
            review_status="deleted",
            removed=removed,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("AQ_BOT_PORT", "5055"))
    log.info("listening on :%d/webhook", port)
    app.run(host="0.0.0.0", port=port)
