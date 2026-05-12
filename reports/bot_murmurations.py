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
from messages import (
    CONSENT_PROMPT,
    CONSENT_CONFIRMED,
    CONSENT_KEYWORDS,
    OPTOUT_CONFIRMED,
    HELP_REPLY,
    STATS_REPLY,
    ABOUT_REPLY,
    UNKNOWN_COMMAND,
    TEXT_RECEIVED,
    PHOTO_RECEIVED,
    LOCATION_RECEIVED_MERGED,
    LOCATION_RECEIVED_STANDALONE,
    LOCATION_INVALID,
    AUDIO_RECEIVED,
)

# --- Paths -----------------------------------------------------------------

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "reports"
PROFILE_DIR = ROOT / "profiles"
IMAGE_DIR = ROOT / "images"
VISION_QUEUE = ROOT / "vision_queue"
CONFIG_FILE = ROOT / "config.json"
CONSENT_FILE = ROOT / "consent.json"

for d in (DATA_DIR, PROFILE_DIR, IMAGE_DIR, VISION_QUEUE):
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
        """
        sender = msg["sender"]
        status = get_consent(sender)
        text = (msg.get("text") or "").strip().lower()

        if text == "/optout":
            set_consent(sender, "optout")
            return OPTOUT_CONFIRMED

        if status == "granted":
            return None

        # Anything else from an opted-out user re-prompts consent
        if text in CONSENT_KEYWORDS:
            set_consent(sender, "granted")
            return CONSENT_CONFIRMED

        return CONSENT_PROMPT

    def _handle_command(self, msg: Dict[str, Any]) -> Optional[str]:
        text = (msg.get("text") or "").strip().lower()
        if not text.startswith("/"):
            return None
        cmd = text.split()[0]
        if cmd == "/help":
            return HELP_REPLY
        if cmd == "/stats":
            today = datetime.now().strftime("%Y-%m-%d")
            daily = DATA_DIR / f"reports_{today}.jsonl"
            count = sum(1 for _ in daily.open()) if daily.exists() else 0
            return STATS_REPLY.format(count=count)
        if cmd == "/about":
            return ABOUT_REPLY
        return UNKNOWN_COMMAND

    # ---- per-type handlers ----

    def _handle_text(self, msg: Dict[str, Any]) -> str:
        sender_hash = _sender_key(msg["sender"])
        report = {
            "sender_hash": sender_hash,
            "type": "text",
            "description": msg.get("text", ""),
            "status": "pending",
        }
        rid = save_report(report)
        # Profile is NOT published here. The report goes into the
        # review queue (review_status='pending') and only gets federated
        # after admin approval via /admin/approve-report.
        return TEXT_RECEIVED

    def _handle_image(self, msg: Dict[str, Any]) -> str:
        sender_hash = _sender_key(msg["sender"])
        rid = _new_report_id()

        # Download image if Evolution API gave us a URL we can fetch.
        # Some configurations send base64 in a different field; the M1
        # worker also has access to Evolution's media-download endpoint.
        image_path: Optional[Path] = None
        url = msg.get("image_url")
        if url:
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                ext = ".jpg" if "jpeg" in msg.get("mimetype", "") else ".png"
                image_path = IMAGE_DIR / f"{rid}{ext}"
                image_path.write_bytes(resp.content)
            except requests.RequestException as e:
                log.warning("image fetch failed for %s: %s", rid, e)

        report = {
            "id": rid,
            "sender_hash": sender_hash,
            "type": "photo",
            "description": msg.get("text", ""),
            "image_path": str(image_path) if image_path else None,
            "media_key": msg.get("media_key"),
            "ai_analysis": None,
            "status": "pending",
        }
        save_report(report)

        # Either run vision inline (dev) or hand off to the M1 worker
        if self.cfg.get("synchronous_vision") and image_path:
            result = analyze_pollution_image(str(image_path))
            update_report(rid, ai_analysis=result, category=result.get("category"))
        elif image_path:
            enqueue_vision_job(rid, image_path)

        # No auto-publish — awaits admin approval
        return PHOTO_RECEIVED

    def _handle_location(self, msg: Dict[str, Any]) -> str:
        sender_hash = _sender_key(msg["sender"])
        lat, lon = msg.get("latitude"), msg.get("longitude")
        if lat is None or lon is None:
            return LOCATION_INVALID

        merged = merge_pending_location(sender_hash, lat, lon)
        if merged:
            # Report is now complete; awaits admin approval.
            return LOCATION_RECEIVED_MERGED

        # Standalone location report — also awaits approval
        save_report({
            "sender_hash": sender_hash,
            "type": "location",
            "location": {"lat": lat, "lon": lon},
            "status": "pending",
        })
        return LOCATION_RECEIVED_STANDALONE

    def _handle_audio(self, msg: Dict[str, Any]) -> str:
        # Voice notes are huge in Indonesian WhatsApp — transcription
        # comes in a later sprint (whisper.cpp / MLX-Whisper on the M1).
        sender_hash = _sender_key(msg["sender"])
        save_report({
            "sender_hash": sender_hash,
            "type": "audio",
            "media_key": msg.get("media_key"),
            "status": "pending",
            "ai_analysis": {"description": "Voice note — transcription pending"},
        })
        return AUDIO_RECEIVED

    # ---- federation ----

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

    # ---- dispatch ----

    def process(self, msg: Dict[str, Any]) -> Optional[str]:
        """Returns the reply text, or None if we shouldn't reply."""
        # Allowlist gate — critical when running on a personal WhatsApp
        # number. Drops messages from anyone not explicitly approved.
        if not self._is_allowed_sender(msg.get("sender", "")):
            log.info("dropped (not in allowlist): %s", msg.get("sender"))
            return None

        gate = self._gate_consent(msg)
        if gate is not None:
            return gate

        cmd_reply = self._handle_command(msg)
        if cmd_reply is not None:
            return cmd_reply

        handler = {
            "text": self._handle_text,
            "image": self._handle_image,
            "location": self._handle_location,
            "audio": self._handle_audio,
        }.get(msg.get("type"))
        if not handler:
            return None
        return handler(msg)


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
        """
        if not _check_admin_auth():
            return jsonify(ok=False, error="unauthorized"), 401
        report_id = (request.get_json(silent=True) or {}).get("report_id", "")
        if not report_id:
            return jsonify(ok=False, error="missing report_id"), 400

        report = load_report(report_id)
        if not report:
            return jsonify(ok=False, error="report not found"), 404

        # Mark approved
        report["review_status"] = "approved"
        report["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        (DATA_DIR / f"{report_id}.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )

        # Now publish the Murmurations profile (sanitized — adapter
        # strips PII even though we also strip here)
        sanitized = {k: v for k, v in report.items()
                     if k not in ("sender", "sender_hash", "image_path", "media_key")}
        try:
            bot.node.process_report(sanitized)
            log.info("approved + published: %s", report_id)
            return jsonify(ok=True, report_id=report_id, review_status="approved")
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

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("AQ_BOT_PORT", "5055"))
    log.info("listening on :%d/webhook", port)
    app.run(host="0.0.0.0", port=port)
