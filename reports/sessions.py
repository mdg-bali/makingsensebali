#!/usr/bin/env python3
"""
Per-sender draft sessions for the Bukit AQ Reporter.

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
    await_category  → user must reply with a menu number (1..N)
    await_detail    → optional one-line free-text detail, or 'lanjut'/'skip'
    await_location  → user must share a WhatsApp location pin
    await_photo     → user must send a photo (photo is required, not optional)
    await_confirm   → user replies 'kirim' (send) or 'batal' (cancel)

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

AWAIT_CATEGORY = "await_category"
AWAIT_DETAIL = "await_detail"
AWAIT_LOCATION = "await_location"
AWAIT_PHOTO = "await_photo"
AWAIT_CONFIRM = "await_confirm"

# Order matters — used to print "Step N/4" prompts and to validate transitions.
FLOW_ORDER = [
    AWAIT_CATEGORY,
    AWAIT_DETAIL,
    AWAIT_LOCATION,
    AWAIT_PHOTO,
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
    state: str = AWAIT_CATEGORY
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

    def start(self, sender_hash: str) -> Session:
        """Begin (or restart) a draft for this sender."""
        sessions = self._load_all()
        s = Session(sender_hash=sender_hash, state=AWAIT_CATEGORY, draft={})
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
