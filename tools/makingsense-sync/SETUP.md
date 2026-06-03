# Making Sense Bali — data sync generator (mini)

Pre-bakes the site's data so visitors load instantly instead of hammering the
Smart Citizen API live, and carries approved citizen reports from the NAS out
to the public map. Runs on the **mini** (real internet egress + exo local).

Each run writes into the repo and pushes:
- `data/sensors.json` — snapshot of the known Smart Citizen kits (+ OpenAQ if a key is set)
- `data/reports/` + `index.json` — approved Murmurations profiles pulled from the NAS
- `data/areas.json` — per-neighbourhood roll-up (counts, categories, top tags, max severity, nearby PM2.5) + an optional 2-sentence exo narrative

It is **fail-safe**: each stage is isolated; one failing never blocks the others, and the run never crashes the schedule.

## One-time setup (on the mini)

1. **Clone the repo** somewhere stable:
   ```
   git clone git@github.com:mdg-bali/makingsensebali.git ~/makingsensebali
   ```

2. **GitHub deploy key (push access)** — so the mini can push:
   ```
   ssh-keygen -t ed25519 -f ~/.ssh/msb_deploy -N ""
   ```
   Add `~/.ssh/msb_deploy.pub` to the repo on GitHub → **Settings → Deploy keys → Add → Allow write access**.
   Point git at it (in `~/.ssh/config`):
   ```
   Host github.com
     IdentityFile ~/.ssh/msb_deploy
     IdentitiesOnly yes
   ```

3. **mini → NAS SSH key (for the report pull)** — so `rsync` works without a password:
   ```
   ssh-copy-id fablabbali@tx-nas-bali     # or append the mini's pubkey to the NAS authorized_keys
   rsync -az --include='AQ_*.json' --exclude='*' \
     fablabbali@tx-nas-bali:/volume1/docker/aq-reporter/data/profiles/ ~/tmp_test/   # verify it pulls
   ```
   (Confirm the NAS profiles path; on this deployment it's `/volume1/docker/aq-reporter/data/profiles/`.)

4. **Edit the plist** `com.fabcity.makingsense-sync.plist` — fix `MSB_REPO_DIR`, `MSB_NAS_RSYNC_SRC`, `MSB_NAS_PHOTOS_SRC` (the EXIF-stripped public photos, so the map can show them), the python path, and the log paths to match the mini. Optional: add `MSB_OPENAQ_KEY`; set `MSB_NARRATIVE` to `0` to ship structured roll-ups only (no exo paragraph).

5. **Dry run** (everything except the push):
   ```
   MSB_REPO_DIR=~/makingsensebali python3 ~/makingsensebali/tools/makingsense-sync/generate.py --dry-run
   ```
   Check `data/sensors.json`, `data/areas.json`, and `data/reports/index.json` look right, and that `areas.json` summaries read well (if not, set `MSB_NARRATIVE=0`).

6. **Install the schedule** (every 15 min):
   ```
   cp ~/makingsensebali/tools/makingsense-sync/com.fabcity.makingsense-sync.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.fabcity.makingsense-sync.plist
   ```

7. **Verify**: `tail -f ~/makingsensebali/tools/makingsense-sync/sync.log` and confirm a commit lands on GitHub.

## Notes
- The deploy key is scoped to this one repo (push only). No secrets live in the repo.
- Cadence is `StartInterval` (900s = 15 min). Sensors don't change fast; reports appear within a cycle of approval.
- If the mini is asleep, the cycle is skipped and resumes on wake — acceptable for a campaign site, but it's the reason this lives on the mini, not the always-on NAS (which is firewalled from GitHub + the SC API).
- **Phase 2 (site side, separate change):** `data.js` must load `data/sensors.json` first (instant) before any live refresh, and the home/dashboard must render `data/areas.json`. Until then the generator produces the files but the site still fetches sensors live.
