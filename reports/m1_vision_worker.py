#!/usr/bin/env python3
"""
M1 vision worker — drains the NAS vision queue.

Runs on the M1 MacBook (or any machine that can reach the queue dir).
Reads pending vision jobs from vision_queue/, calls the configured
vision backend (typically the local MLX server on this same M1), writes
the analysis back into the report, republishes the Murmurations profile,
and — if configured — sends a follow-up WhatsApp message so the user
sees the result.

The worker is designed to be safe to crash and restart at any moment:
  - Jobs are atomically moved from pending/ to processing/ to done/
  - Failed jobs go to failed/ with the error logged
  - Multiple worker instances are fine (atomic rename = soft lock)

Setup (M1)
----------
    # 1. Mount the NAS share so AQ_REPO points at the live data dir
    #    open smb://<nas>/aq-reporter
    #    or use Tailscale + SMB

    # 2. Make sure the MLX server is running (mlx_vision_server.py)
    #    or set AQ_VISION_BACKEND=ollama if you'd rather use Ollama

    # 3. Run the worker
    AQ_REPO=/Volumes/aq-reporter python m1_vision_worker.py

Env
---
    AQ_REPO              path to the aq-reporter directory (default: cwd)
    AQ_VISION_BACKEND    forwarded to vision_analyzer (default: mlx)
    AQ_POLL_INTERVAL     seconds between queue scans (default: 5)
    AQ_NOTIFY_USERS      "1" to send follow-up WhatsApp messages (default: 0)
    AQ_EVOLUTION_BASE    Evolution API base url, used only when notifying
    AQ_EVOLUTION_INSTANCE
    AQ_EVOLUTION_KEY
"""

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests

# --- Paths -----------------------------------------------------------------

REPO = Path(os.environ.get("AQ_REPO", ".")).resolve()
QUEUE = REPO / "vision_queue"
PROCESSING = QUEUE / "processing"
DONE = QUEUE / "done"
FAILED = QUEUE / "failed"
REPORTS = REPO / "reports"
# The bot writes container-internal paths into queue files (e.g.
# "/app/images/AQ_xxx.jpg") because that's its own view. The worker
# sees the same files at $AQ_REPO/images/AQ_xxx.jpg via SMB or local
# mount. _resolve_image_path() handles the remap so the worker doesn't
# need a fragile /app symlink on the host machine.
BOT_CONTAINER_ROOT = "/app/"

for d in (QUEUE, PROCESSING, DONE, FAILED):
    d.mkdir(parents=True, exist_ok=True)


def _resolve_image_path(image_path: str) -> Path:
    """Translate a queue file's image_path into the worker's filesystem view.

    Bot writes /app/images/AQ_xxx.jpg (its container's view). Worker
    sees the same file at AQ_REPO/images/AQ_xxx.jpg. If the path is
    already absolute on the worker's filesystem (e.g. local dev with
    AQ_REPO=cwd, full path resolves), we just use it as-is.
    """
    if image_path.startswith(BOT_CONTAINER_ROOT):
        return REPO / image_path[len(BOT_CONTAINER_ROOT):]
    return Path(image_path)

# Make adapter + analyzer importable when running from anywhere
sys.path.insert(0, str(REPO))

from murmurations_adapter import MurmurationsConfig, PlanetAINode  # noqa: E402
from vision_analyzer import analyze_pollution_image  # noqa: E402
from messages import (  # noqa: E402
    ANALYSIS_FOLLOWUP_TEMPLATE,
    ANALYSIS_INDICATORS_LINE,
    ANALYSIS_DESCRIPTION_LINE,
    CATEGORY_EMOJI,
    SEVERITY_EMOJI,
)

# --- Config ----------------------------------------------------------------

POLL = float(os.environ.get("AQ_POLL_INTERVAL", "5"))
NOTIFY = os.environ.get("AQ_NOTIFY_USERS", "0") == "1"
EVOLUTION_BASE = os.environ.get("AQ_EVOLUTION_BASE", "").rstrip("/")
EVOLUTION_INSTANCE = os.environ.get("AQ_EVOLUTION_INSTANCE", "")
EVOLUTION_KEY = os.environ.get("AQ_EVOLUTION_KEY", "")

logging.basicConfig(
    level=os.environ.get("AQ_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("vision-worker")

_running = True


def _stop(*_: Any) -> None:
    global _running
    _running = False
    log.info("stopping after current job")


signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)


# --- Murmurations republishing --------------------------------------------

def _load_node() -> PlanetAINode:
    cfg_path = REPO / "config.json"
    cfg: Dict[str, Any] = {}
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
        except json.JSONDecodeError:
            log.warning("config.json corrupt — using defaults")
    return PlanetAINode(
        MurmurationsConfig(
            node_id=cfg.get("node_id", "bali.fab.city"),
            bioregion=cfg.get("bioregion", "indo_pacific_coral_triangle"),
            primary_url=cfg.get("primary_url", "https://planetai.fab.city/bali"),
            use_test_index=True,
            auto_index=cfg.get("murmurations_auto_index", False),
        )
    )


# --- WhatsApp follow-up notification --------------------------------------

# We don't have the original sender phone (only sender_hash) in the
# report — that's the privacy guarantee. To send a follow-up, the bot
# needs to know who to message. Two options handled here:
#  1. The job file optionally carries a `notify_jid` field — the bot
#     writes this when it enqueues, allowing per-job recipient targeting
#     without persisting the phone in the report.
#  2. Otherwise, no message is sent (pilot acceptable — user can check
#     the dashboard).

def _send_followup(jid: str, text: str) -> None:
    if not NOTIFY or not EVOLUTION_BASE or not EVOLUTION_INSTANCE or not jid:
        log.debug("notify skipped (jid=%s notify=%s)", jid, NOTIFY)
        return
    url = f"{EVOLUTION_BASE}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {"Content-Type": "application/json"}
    if EVOLUTION_KEY:
        headers["apikey"] = EVOLUTION_KEY
    try:
        r = requests.post(
            url, json={"number": jid, "text": text}, headers=headers, timeout=10
        )
        r.raise_for_status()
    except requests.RequestException as e:
        log.warning("follow-up to %s failed: %s", jid, e)


def _format_followup(analysis: Dict[str, Any]) -> str:
    """Build the post-analysis WhatsApp reply from the template in messages.py."""
    cat = analysis.get("category", "other")
    sev = analysis.get("severity", "low")
    desc = analysis.get("description", "")
    indicators = ", ".join(analysis.get("indicators", []))

    indicators_line = (
        ANALYSIS_INDICATORS_LINE.format(indicators=indicators) if indicators else ""
    )
    description_line = (
        ANALYSIS_DESCRIPTION_LINE.format(description=desc) if desc else ""
    )

    return ANALYSIS_FOLLOWUP_TEMPLATE.format(
        cat_emoji=CATEGORY_EMOJI.get(cat, "📋"),
        category=cat,
        sev_emoji=SEVERITY_EMOJI.get(sev, "⚪"),
        severity=sev,
        indicators_line=indicators_line,
        description_line=description_line,
    )


# --- Job processing -------------------------------------------------------

MAX_RETRIES = int(os.environ.get("AQ_MAX_RETRIES", "3"))
STALE_CLAIM_SECS = int(os.environ.get("AQ_STALE_CLAIM_SECS", "600"))  # 10 min


def _claim(job_path: Path) -> Optional[Path]:
    """Atomically move a job from pending to processing — soft lock."""
    target = PROCESSING / job_path.name
    try:
        job_path.rename(target)
        return target
    except FileNotFoundError:
        return None  # another worker beat us to it
    except OSError as e:
        log.warning("claim failed for %s: %s", job_path.name, e)
        return None


def _recover_stuck_jobs() -> None:
    """Move processing/ jobs older than STALE_CLAIM_SECS back to the queue.
    Assumes a previous worker crashed before finishing them."""
    cutoff = time.time() - STALE_CLAIM_SECS
    for stale in PROCESSING.glob("AQ_*.json"):
        try:
            if stale.stat().st_mtime < cutoff:
                target = QUEUE / stale.name
                stale.rename(target)
                log.info("recovered stuck job %s", stale.name)
        except OSError as e:
            log.warning("could not recover %s: %s", stale.name, e)


def _retry_or_fail(job_path: Path) -> None:
    """A transient failure — bump retry count and either requeue or fail."""
    try:
        job = json.loads(job_path.read_text())
    except (OSError, json.JSONDecodeError):
        job = {}
    retries = int(job.get("retries", 0)) + 1
    job["retries"] = retries
    # Backoff before requeue so a downed backend can't burn all retries in
    # milliseconds and dump real reports to failed/. Grows with each retry.
    time.sleep(min(60, 10 * retries))
    if retries >= MAX_RETRIES:
        log.error("%s exceeded %d retries — moving to failed/", job_path.name, MAX_RETRIES)
        try:
            job_path.write_text(json.dumps(job, indent=2))
            job_path.rename(FAILED / job_path.name)
        except OSError as e:
            log.warning("could not move %s to failed: %s", job_path.name, e)
        return
    # Requeue
    try:
        job_path.write_text(json.dumps(job, indent=2))
        job_path.rename(QUEUE / job_path.name)
        log.info("requeued %s (retry %d/%d)", job_path.name, retries, MAX_RETRIES)
    except OSError as e:
        log.warning("could not requeue %s: %s", job_path.name, e)


def _finish_success(job_path: Path) -> None:
    """Strip PII from the job file and move it to done/."""
    try:
        job = json.loads(job_path.read_text())
        # notify_jid is the only PII in the job — drop it once we're done
        job.pop("notify_jid", None)
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
        job_path.write_text(json.dumps(job, indent=2))
        job_path.rename(DONE / job_path.name)
    except OSError as e:
        log.warning("could not finalize %s: %s", job_path.name, e)


def _finish_permanent_fail(job_path: Path, reason: str) -> None:
    """A non-retryable failure — log reason, strip PII, move to failed/."""
    try:
        job = json.loads(job_path.read_text())
        job.pop("notify_jid", None)
        job["failed_reason"] = reason
        job["failed_at"] = datetime.now(timezone.utc).isoformat()
        job_path.write_text(json.dumps(job, indent=2))
        job_path.rename(FAILED / job_path.name)
    except OSError as e:
        log.warning("could not move %s to failed: %s", job_path.name, e)


def _update_report(report_id: str, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    p = REPORTS / f"{report_id}.json"
    if not p.exists():
        log.warning("report %s missing — vision result orphaned", report_id)
        return None
    report = json.loads(p.read_text())
    report["ai_analysis"] = analysis
    # Promote category up to the top level so the adapter picks it up
    report["category"] = analysis.get("category", report.get("category"))
    report["vision_completed_at"] = datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _republish(node: PlanetAINode, report: Dict[str, Any]) -> None:
    """Refresh the sanitized profile so the public dashboard picks up AI analysis.

    NOTE: we deliberately don't call node.process_report() here — that
    would route through MurmurationsProfile.save(), which uses
    LOCAL_PROFILE_DIR = Path(__file__).parent / "profiles". For the
    worker running on the M1 Mac, __file__ resolves to
    ~/Documents/.../makingsensebali/reports/, NOT the SMB-mounted NAS
    profiles dir. The "republished" file would land in a folder nobody
    reads and the public dashboard would keep showing the pre-analysis
    profile. We build the profile via from_aq_report (which still
    sanitizes) and write it directly to REPO/profiles/ — the same
    physical location the bot's container writes to via its /app
    bind mount.
    """
    sanitized = {
        k: v for k, v in report.items()
        if k not in ("sender", "sender_hash", "image_path", "media_key",
                     "photo_published", "photo_public_path")
    }
    # Preserve photo_path explicitly — the bot sets this when the
    # admin opts to publish the photo. from_aq_report propagates it
    # only after our adapter patch (see Bug 2 / 2026-05-21).
    if report.get("photo_public_path"):
        sanitized["photo_path"] = report["photo_public_path"]

    report_id = report.get("id")
    if not report_id:
        log.error("republish: report missing id, skipping")
        return
    try:
        profile = node.profile_gen.from_aq_report(sanitized)
        out_dir = REPO / "profiles"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{report_id}.json"
        out_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
        log.info("republished %s → %s", report_id, out_path)
    except Exception as e:  # noqa: BLE001
        log.error("republish failed for %s: %s", report_id, e)


# Outcome enum returned by process_job
OK = "ok"
RETRY = "retry"            # transient failure (model down, etc.)
PERMANENT = "permanent"    # report missing, bad job format


def process_job(job_path: Path, node: PlanetAINode) -> str:
    job = json.loads(job_path.read_text())
    report_id = job.get("report_id")
    image_path_raw = job.get("image_path")
    notify_jid = job.get("notify_jid")

    if not report_id or not image_path_raw:
        log.error("bad job %s: %s", job_path.name, job)
        return PERMANENT

    # Remap bot's container-internal /app/... path to the worker's view.
    image_path_local = _resolve_image_path(image_path_raw)
    if not image_path_local.exists():
        log.error(
            "image not found for %s — bot wrote %r, worker resolved to %s. "
            "Check AQ_REPO mount and image existence on disk.",
            report_id, image_path_raw, image_path_local,
        )
        return PERMANENT

    log.info("analyzing %s (%s)", report_id, image_path_local.name)
    t0 = time.time()
    analysis = analyze_pollution_image(str(image_path_local))
    log.info(
        "  → %s / %s (conf=%.2f) in %.1fs",
        analysis.get("category"),
        analysis.get("severity"),
        analysis.get("confidence", 0),
        time.time() - t0,
    )

    if analysis.get("model_version", "").endswith(":error"):
        # vision_analyzer returns this for unreachable backend / timeouts /
        # missing image — all retryable except "image not found" which we
        # treat as permanent below
        if "image not found" in analysis.get("description", ""):
            return PERMANENT
        return RETRY

    report = _update_report(report_id, analysis)
    if not report:
        return PERMANENT  # report file vanished — nothing to publish

    _republish(node, report)

    if notify_jid:
        _send_followup(notify_jid, _format_followup(analysis))

    return OK


# --- Main loop ------------------------------------------------------------

def main() -> None:
    log.info("worker starting — repo=%s poll=%.1fs notify=%s", REPO, POLL, NOTIFY)
    _recover_stuck_jobs()
    node = _load_node()

    while _running:
        jobs = sorted(QUEUE.glob("AQ_*.json"))
        if not jobs:
            time.sleep(POLL)
            continue

        for job_path in jobs:
            if not _running:
                break
            claimed = _claim(job_path)
            if not claimed:
                continue
            try:
                outcome = process_job(claimed, node)
            except Exception as e:  # noqa: BLE001
                log.exception("worker error on %s: %s", claimed.name, e)
                outcome = RETRY  # unknown exception — give it another try

            if outcome == OK:
                _finish_success(claimed)
            elif outcome == RETRY:
                _retry_or_fail(claimed)
            else:
                _finish_permanent_fail(claimed, reason="permanent")

    log.info("worker stopped")


if __name__ == "__main__":
    main()
