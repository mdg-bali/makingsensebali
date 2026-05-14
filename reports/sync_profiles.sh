#!/usr/bin/env bash
# sync_profiles.sh — push approved Murmurations profiles to BOTH sinks:
#
#   1. planetai.fab.city  (federation source for Murmurations Index)
#   2. mdg-bali.github.io (public-facing dashboard, GitHub Pages)
#
# Only profiles in ./data/profiles/ are synced, and profiles only
# exist there once an admin approves a report via the dashboard.
# So this script implicitly enforces the approval gate.
#
# Intended for cron on the Synology, every 5–10 minutes:
#   */5 * * * * /volume1/docker/aq-reporter/sync_profiles.sh \
#               >> /var/log/aq-sync.log 2>&1
#
# Either sink can be disabled by leaving its target env unset.
#
# Env
# ---
#   AQ_SYNC_SOURCE         default: ./data/profiles/
#   PLANETAI_TARGET        rsync target (e.g. user@host:/var/www/bali/profiles/)
#                          leave empty to skip planetai sync
#   GITHUB_REPO_DIR        local checkout of mdg-bali/smartcitizenbali
#                          leave empty to skip github sync
#   GITHUB_PROFILES_SUBDIR subdir inside the repo for profiles
#                          default: data/reports
#   GITHUB_COMMIT_AUTHOR   default: "AQ Bot <bot@fab.city>"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE="${AQ_SYNC_SOURCE:-$SCRIPT_DIR/data/profiles/}"
# Optional photo source — only photos explicitly approved with
# "Publish photo too" in the dashboard land here. EXIF already stripped.
PHOTO_SOURCE="${AQ_PHOTO_SOURCE:-$SCRIPT_DIR/data/profile_photos/}"
PLANETAI_TARGET="${PLANETAI_TARGET:-}"
GITHUB_REPO_DIR="${GITHUB_REPO_DIR:-}"
GITHUB_PROFILES_SUBDIR="${GITHUB_PROFILES_SUBDIR:-data/reports}"
GITHUB_PHOTOS_SUBDIR="${GITHUB_PHOTOS_SUBDIR:-data/reports/photos}"
GITHUB_COMMIT_AUTHOR="${GITHUB_COMMIT_AUTHOR:-AQ Bot <bot@fab.city>}"
LOCK_FILE="${AQ_SYNC_LOCK:-/tmp/aq-sync.lock}"
LOG_TAG="aq-sync"
SUMMARY_SCRIPT="${AQ_SUMMARY_SCRIPT:-$SCRIPT_DIR/generate_summary.py}"

log() {
  echo "[$LOG_TAG] $*" >&2
  if command -v logger >/dev/null 2>&1; then
    logger -t "$LOG_TAG" "$*" 2>/dev/null || true
  fi
}

# --- Defensive checks -----------------------------------------------------

if [[ ! -d "$SOURCE" ]]; then
  log "ERROR: source dir does not exist: $SOURCE"
  exit 1
fi

if [[ -z "$PLANETAI_TARGET" && -z "$GITHUB_REPO_DIR" ]]; then
  log "ERROR: neither PLANETAI_TARGET nor GITHUB_REPO_DIR is set — nothing to do"
  exit 1
fi

# --- Lock (single instance only) ------------------------------------------

if [[ -f "$LOCK_FILE" ]]; then
  PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
  if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
    log "previous run still active (PID $PID), skipping"
    exit 0
  fi
  rm -f "$LOCK_FILE"
fi

echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

# --- Count what we're working with ----------------------------------------

PENDING=$(find "$SOURCE" -maxdepth 1 -name 'AQ_*.json' -type f 2>/dev/null | wc -l)
log "syncing $PENDING approved profiles"

if [[ "$PENDING" -eq 0 ]]; then
  log "nothing to sync"
  exit 0
fi

# --- Sink 1: planetai.fab.city (Murmurations federation source) -----------

if [[ -n "$PLANETAI_TARGET" ]]; then
  log "→ planetai: $PLANETAI_TARGET"

  RSYNC_OPTS=(
    --archive
    --quiet
    --delete-after
    --include='AQ_*.json'
    --include='*/'
    --exclude='*'
  )
  [[ "${DRY_RUN:-0}" == "1" ]] && RSYNC_OPTS+=(--dry-run --verbose)

  if rsync "${RSYNC_OPTS[@]}" "$SOURCE" "$PLANETAI_TARGET"; then
    log "  planetai OK"
  else
    RC=$?
    log "  ERROR: planetai rsync exit $RC"
    # don't abort — still try github
  fi
fi

# --- Sink 2: mdg-bali.github.io (via local git clone) ---------------------

if [[ -n "$GITHUB_REPO_DIR" ]]; then
  log "→ github: $GITHUB_REPO_DIR/$GITHUB_PROFILES_SUBDIR"

  if [[ ! -d "$GITHUB_REPO_DIR/.git" ]]; then
    log "  ERROR: $GITHUB_REPO_DIR is not a git repository"
    log "  Clone the mdg-bali/smartcitizenbali repo there first, then re-run"
    exit 1
  fi

  TARGET_DIR="$GITHUB_REPO_DIR/$GITHUB_PROFILES_SUBDIR"
  mkdir -p "$TARGET_DIR"

  cd "$GITHUB_REPO_DIR"

  # Pull first so we don't clobber concurrent edits made on the repo
  if ! git pull --quiet --rebase 2>/dev/null; then
    log "  WARN: git pull failed (continuing — may diverge)"
  fi

  # Mirror the local profiles into the repo dir
  RSYNC_OPTS_GIT=(
    --archive
    --quiet
    --delete-after
    --include='AQ_*.json'
    --include='*/'
    --exclude='*'
  )
  rsync "${RSYNC_OPTS_GIT[@]}" "$SOURCE" "$TARGET_DIR/"

  # Mirror approved-for-public photos (if any). Photos in PHOTO_SOURCE
  # have already been EXIF-stripped by the bot at approve time. We do
  # NOT use --delete-after here — a publish toggle is meant to be
  # additive; removing photos requires explicit operator action.
  PHOTO_TARGET_DIR="$GITHUB_REPO_DIR/$GITHUB_PHOTOS_SUBDIR"
  if [[ -d "$PHOTO_SOURCE" ]]; then
    PHOTO_COUNT=$(find "$PHOTO_SOURCE" -maxdepth 1 -name 'AQ_*.jpg' -type f 2>/dev/null | wc -l)
    if [[ "$PHOTO_COUNT" -gt 0 ]]; then
      log "  syncing $PHOTO_COUNT approved photos"
      mkdir -p "$PHOTO_TARGET_DIR"
      rsync --archive --quiet \
            --include='AQ_*.jpg' \
            --include='*/' \
            --exclude='*' \
            "$PHOTO_SOURCE" "$PHOTO_TARGET_DIR/"
    fi
  fi

  # Generate an index.json so the github.io dashboard has a single
  # file to fetch (lists all profile filenames)
  python3 - <<PYEOF
import json, os
target = "$TARGET_DIR"
profiles = sorted(f for f in os.listdir(target) if f.startswith('AQ_') and f.endswith('.json'))
index = {
    "count": len(profiles),
    "profiles": profiles,
    "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
with open(os.path.join(target, 'index.json'), 'w') as f:
    json.dump(index, f, indent=2)
PYEOF

  # Refresh the daily/weekly summary. Templated for now (no LLM
  # dependency); summary.json is written next to index.json. If the
  # script is missing, log and skip — sync should not fail because
  # the summary helper is absent.
  if [[ -x "$SUMMARY_SCRIPT" || -f "$SUMMARY_SCRIPT" ]]; then
    if python3 "$SUMMARY_SCRIPT" "$SOURCE" "$TARGET_DIR/summary.json" 2>/dev/null; then
      log "  summary refreshed"
    else
      log "  WARN: summary refresh failed (continuing)"
    fi
  else
    log "  WARN: generate_summary.py not found at $SUMMARY_SCRIPT — skipping summary"
  fi

  # Stage. We add the profiles subdir (covers index.json + AQ_*.json +
  # photos/ underneath it) — `git add data/reports` picks up everything
  # under that path.
  git add "$GITHUB_PROFILES_SUBDIR"
  if git diff --cached --quiet; then
    log "  no changes to commit"
  else
    git -c user.name="$(echo "$GITHUB_COMMIT_AUTHOR" | sed 's/ <.*//')" \
        -c user.email="$(echo "$GITHUB_COMMIT_AUTHOR" | sed -n 's/.*<\(.*\)>.*/\1/p')" \
        commit -m "sync: $PENDING approved profiles ($(date -u +%Y-%m-%dT%H:%MZ))" \
        --quiet

    if [[ "${DRY_RUN:-0}" == "1" ]]; then
      log "  DRY_RUN — skipping push"
    elif git push --quiet; then
      log "  github push OK"
    else
      RC=$?
      log "  ERROR: git push exit $RC"
    fi
  fi
fi

log "DONE ($PENDING profiles processed)"
