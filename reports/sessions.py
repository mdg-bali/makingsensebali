#!/usr/bin/env python3
"""
Per-sender draft sessions for the Making Sense Bali reporter.

Why this exists
---------------
WhatsApp conversations are stateful, but the bot was originally written
as if each inbound message were independent — text, location, and photo
were each saved as their own report and stitched together with brittle
"merge into the most recent pending" logic. Result: users who sent
description → location → photo ended up with TWO reports and got asked
for location a second time.

This module gives the bot a single source of truth for "where is sender
X in the report flow, and what have they given me so far?" — one draft
report being filled in step by step, committed when the user confirms.

State machine (strict order, per Tomas's call):
    await_language  → user picks 1/2/3 (en/id/es) — FIRST, before consent
    await_category  → user must reply with a menu number (1..N)
    await_photo     → user must send a photo (photo is required, comes first)
    await_location  → location pin, Google Maps link, or typed coordinates
    await_comment   → optional one-line comment, or 'skip'/'lewati'/'omitir'
    await_confirm   → user replies 'kirim' (send) or 'batal' (cancel)
    await_feedback  → post-submit: next text captured anonymously as feedback

Wrong-step messages get a polite reminder, NOT a new report.

Storage
-------
sessions.json sits next to consent.json. Keyed by sender_hash (the same
non-reversible hash used by consent). Sessions older than SESSION_TTL
seconds are auto-evicted on load so a user who walks away mid-flow and
comes back the next day starts fresh.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

log = logging.getLogger("aq-bot.sessions")

# --- State constants -------------------------------------------------------

AWAIT_LANGUAGE = "await_language"
AWAIT_CATEGORY = "await_category"
AWAIT_PHOTO = "await_photo"
AWAIT_LOCATION = "await_location"
AWAIT_INCIDENT_TIME = "await_incident_time"
AWAIT_INCIDENT_TIME_DETAIL = "await_incident_time_detail"
AWAIT_COMMENT = "await_comment"
AWAIT_CONFIRM = "await_confirm"
AWAIT_FEEDBACK = "await_feedback"

# Order matters — used to print step prompts and to validate transitions.
# Mandatory user-visible steps are category → photo → location (1/3, 2/3,
# 3/3). The comment step is optional and not numbered. Language is picked
# before consent; feedback is a post-submit branch, not part of the linear
# report flow.
FLOW_ORDER = [
    AWAIT_LANGUAGE,
    AWAIT_CATEGORY,
    AWAIT_PHOTO,
    AWAIT_LOCATION,
    AWAIT_INCIDENT_TIME,
    AWAIT_INCIDENT_TIME_DETAIL,
    AWAIT_COMMENT,
    AWAIT_CONFIRM,
]

# Sessions older than this are considered abandoned and auto-evicted.
# 24h is generous — covers "started yesterday evening, finishing this morning".
SESSION_TTL_SECONDS = 24 * 60 * 60


# --- Data model ------------------------------------------------------------

@dataclass
class Session:
    """A user's in-progress draft report."""

    sender_hash: str
    state: str = AWAIT_LANGUAGE
    lang: str = ""  # "" until the user picks en/id/es; then persisted
    draft: Dict[str, Any] = field(default_factory=dict)
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def is_stale(self) -> bool:
        try:
            ts = datetime.fromisoformat(self.updated_at)
        except ValueError:
            return True
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        return age > SESSION_TTL_SECONDS


# --- Store -----------------------------------------------------------------

class SessionStore:
    """File-backed session storage. One JSON dict, keyed by sender_hash.

    Not async-safe for concurrent webhook calls — but the bot is single-
    process Flask with one worker on the NAS, and WhatsApp users don't
    fire faster than the disk can keep up. If we ever need concurrency
    we can swap this for SQLite without changing the public API.
    """

    def __init__(self, path: Path):
        self.path = path
        self._cache: Optional[Dict[str, Session]] = None

    # ---- persistence ----

    def _load_all(self) -> Dict[str, Session]:
        if self._cache is not None:
            return self._cache
        if not self.path.exists():
            self._cache = {}
            return self._cache
        try:
            raw = json.loads(self.path.read_text())
        except json.JSONDecodeError as e:
            log.warning("sessions.json corrupt, starting fresh: %s", e)
            self._cache = {}
            return self._cache

        sessions: Dict[str, Session] = {}
        for sh, blob in raw.items():
            try:
                s = Session(sender_hash=sh, **blob)
                if not s.is_stale():
                    sessions[sh] = s
            except TypeError:
                # Schema drift between deploys — drop the entry.
                log.warning("dropping malformed session for %s", sh)
        self._cache = sessions
        return self._cache

    def _save_all(self) -> None:
        assert self._cache is not None, "must load before saving"
        # Strip sender_hash from blob (it's the key) for compactness.
        serializable = {
            sh: {k: v for k, v in asdict(s).items() if k != "sender_hash"}
            for sh, s in self._cache.items()
        }
        self.path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False))

    # ---- public API ----

    def get(self, sender_hash: str) -> Optional[Session]:
        return self._load_all().get(sender_hash)

    def start(self, sender_hash: str, lang: str = "", state: str = AWAIT_CATEGORY) -> Session:
        """Begin (or restart) a session for this sender.

        `state` defaults to AWAIT_CATEGORY because callers normally start
        the report flow after language + consent are already settled. Pass
        AWAIT_LANGUAGE to begin with the language picker on first contact.
        `lang` carries the chosen language forward when restarting a draft.
        """
        sessions = self._load_all()
        s = Session(sender_hash=sender_hash, state=state, lang=lang, draft={})
        sessions[sender_hash] = s
        self._save_all()
        return s

    def update(self, session: Session) -> None:
        sessions = self._load_all()
        session.touch()
        sessions[session.sender_hash] = session
        self._save_all()

    def clear(self, sender_hash: str) -> None:
        sessions = self._load_all()
        sessions.pop(sender_hash, None)
        self._save_all()

    def has_active(self, sender_hash: str) -> bool:
        s = self.get(sender_hash)
        return s is not None and not s.is_stale()
