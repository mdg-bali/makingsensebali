# Deploy guide — Making Sense Bali Reporter

Bring up the first PLANETAI Community-tier node on home infrastructure.

## What runs where

```
┌──────────────────────────────────────────────────────────┐
│ Synology DS725+ NAS — always on (UPS-backed)             │
│                                                          │
│   Container Manager:                                     │
│     • aq-evolution   (WhatsApp transport, Baileys)       │
│     • aq-bot         (Flask webhook + Murmurations)      │
│                                                          │
│   /volume1/docker/aq-reporter/                           │
│     ├── data/reports/   (canonical, NAS-only, has PII)   │
│     ├── data/profiles/  (sanitized, rsync source)        │
│     ├── data/images/    (raw photos, NAS-only)           │
│     └── data/vision_queue/   (jobs for the M1)           │
│                                                          │
│   Cron:                                                  │
│     */5 * * * *  sync_profiles.sh   → planetai.fab.city  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│ M1 MacBook Pro — when home                               │
│                                                          │
│   mlx_vision_server.py    (FastAPI, port 8000)           │
│     ← loads Phi-3.5-Vision-4bit (~2.5GB) at startup      │
│                                                          │
│   m1_vision_worker.py     (polls vision_queue)           │
│     ← mounts NAS folder via SMB                          │
│     ← calls localhost:8000/analyze for each photo        │
│     ← writes analysis back into report                   │
│     ← regenerates Murmurations profile                   │
│     ← optionally sends WhatsApp follow-up                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

The bot never blocks on inference. If the M1 is asleep, photos pile up
in the queue and get processed when it wakes. If the M1 is dead for a
week, the bot keeps collecting reports — they just stay un-classified
until someone (or a fallback worker) processes them.

## Prerequisites

- Synology DSM 7.2+ with Container Manager installed
- M1 MacBook (or any Apple Silicon Mac) with at least 16GB RAM
- A WhatsApp number you can dedicate to the bot (your personal number
  works for the pilot, but you'll want a separate one before scaling)
- A UPS for the NAS — Bukit power blackouts are real, ~$80 one-time
- `planetai.fab.city` web hosting ready to receive `/bali/profiles/*.json`

## 1. Get the code onto the NAS

From your laptop:

```bash
# Option A: rsync (recommended)
rsync -av --exclude='data' --exclude='.env' \
  ~/fablab-bali/aq-reporter/ \
  tomas@nas.local:/volume1/docker/aq-reporter/

# Option B: SSH + git clone if you've pushed this to a repo
ssh tomas@nas.local
cd /volume1/docker
git clone <your-repo> aq-reporter
```

## 2. Configure secrets

SSH into the NAS:

```bash
cd /volume1/docker/aq-reporter
cp .env.example .env

# Generate a strong API key — Evolution and the bot share it
openssl rand -hex 32  # paste into .env as EVOLUTION_API_KEY

# Edit config.json if you want to override defaults (node_id, etc.)
```

Create `consent.json` with an empty object so the bot can write to it:

```bash
echo '{}' > consent.json
```

## 3. Start the containers

```bash
cd /volume1/docker/aq-reporter
docker compose up -d
docker compose logs -f evolution-api
```

In the Evolution logs you'll see a QR code. **Open WhatsApp on the
phone you're using for the bot → Settings → Linked Devices → Link a
Device → scan the QR.**

Once linked:

```bash
docker compose logs -f aq-bot
```

You should see `AQBot ready — node=bali.fab.city listening on :5055/webhook`.

## 4. Send a test message

From any WhatsApp account, message the bot's number:

> halo

The bot should respond with the consent prompt (Bahasa + English). Reply
**SETUJU**. The bot should confirm. Then send:

> ada asap di pantai bingin

It should reply asking for your location. Send a location (paperclip →
Location → Send your current location). The bot should reply that the
report is complete.

Check the NAS:

```bash
ls /volume1/docker/aq-reporter/data/reports/   # should have AQ_*.json
ls /volume1/docker/aq-reporter/data/profiles/  # should have matching profile
cat /volume1/docker/aq-reporter/data/profiles/AQ_*.json | jq .locality
# → "Bingin"
```

If you see `Bingin` (or `Bukit` from the bbox fallback), the bot is wired
end-to-end on the NAS side.

## 5. Set up the M1 vision worker

On the M1 MacBook:

```bash
# Mount the NAS share
open smb://nas.local/aq-reporter
# (or use Finder → Go → Connect to Server → smb://nas.local)
# Mounts at /Volumes/aq-reporter

# Set up Python env
python3 -m venv ~/.venv/aq-vision
source ~/.venv/aq-vision/bin/activate
pip install mlx-vlm fastapi uvicorn pillow requests
```

Start the MLX server (this triggers the model download on first run, ~2.5GB):

```bash
cd ~/fablab-bali/aq-reporter
python mlx_vision_server.py
```

In a second terminal, start the worker:

```bash
source ~/.venv/aq-vision/bin/activate
AQ_REPO=/Volumes/aq-reporter \
AQ_VISION_BACKEND=mlx \
AQ_VISION_ENDPOINT=http://localhost:8000/analyze \
AQ_NOTIFY_USERS=1 \
AQ_EVOLUTION_BASE=http://nas.local:8080 \
AQ_EVOLUTION_INSTANCE=bali-aq \
AQ_EVOLUTION_KEY=<same-key-as-NAS-env> \
  python m1_vision_worker.py
```

(For Evolution to be reachable from the M1, you'll need to expose port
8080 on the NAS LAN — see the commented section in `docker-compose.yml`.)

## 6. End-to-end photo test

Send the bot a photo of any pollution (a smoky scene, a trash pile,
construction dust). You should see:

- Bot logs (NAS): `msg from +62... type=image` → photo saved, queued
- Worker logs (M1): `analyzing AQ_... → burning / high (conf=0.85) in 6.3s`
- Bot replies on WhatsApp: "🔥 Hasil analisis / Analysis: kategori burning..."
- New profile in `data/profiles/` with `ai_analysis` filled in

## 7. Set up profile sync to planetai.fab.city

Edit `sync_profiles.sh` (or set env vars in cron) to point at where
planetai.fab.city is served from:

- If planetai is hosted **on the same NAS** (Synology Web Station):
  `AQ_SYNC_TARGET=/volume1/web/planetai/bali/profiles/`
- If planetai is hosted **on a VPS** with SSH access:
  `AQ_SYNC_TARGET=user@planetai.fab.city:/var/www/planetai/bali/profiles/`
  (set up SSH keys first so the cron can run unattended)
- If planetai is hosted on a **static host** (Netlify/Vercel/Cloudflare
  Pages): a git push-based flow may be simpler — point the script at a
  local clone of the site repo and push from cron.

Test once:

```bash
DRY_RUN=1 ./sync_profiles.sh   # shows what it would do
./sync_profiles.sh             # actually sync
```

Then register the cron. On Synology: **Control Panel → Task Scheduler →
Create → Scheduled Task → User-defined script**:

```bash
/volume1/docker/aq-reporter/sync_profiles.sh >> /var/log/aq-sync.log 2>&1
```

Schedule: every 5 minutes.

## 8. Submit the schema to Murmurations

Once profiles are publicly accessible at
`https://planetai.fab.city/bali/profiles/AQ_*.json`, submit the schema
to the test index first:

```bash
curl -X POST https://test-index.murmurations.network/v2/nodes \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://planetai.fab.city/bali/profiles/<an-id>.json"}'
```

When that round-trips cleanly, flip `murmurations_auto_index: true` in
`config.json` and restart the bot. New reports will auto-register with
the index.

## 9. Onboard your first 5 users

Pick 5 people from Bukit you know well — a banjar leader, a couple of
neighbors, someone from the school. Walk them through it in person.
Watch which questions they ask. Common gaps to expect:

- Many won't know how to share location → record a 30-second video walkthrough
- Voice notes will come in immediately → schedule the Whisper sprint
- People will send context-free photos ("look at this!") → bot's reply
  template needs to make it clearer that location is required

## Operational checks

```bash
# Bot health
curl http://nas.local:5055/health

# Vision server health (from M1)
curl http://localhost:8000/health

# Queue depth
ls /Volumes/aq-reporter/vision_queue/AQ_*.json 2>/dev/null | wc -l

# Today's report count
ls /Volumes/aq-reporter/reports/AQ_$(date +%Y%m%d)*.json | wc -l

# Last sync
tail -5 /var/log/aq-sync.log
```

## Troubleshooting

**Evolution API loses WhatsApp session after a reboot.**
Baileys session data lives in `data/evolution/`. As long as that volume
persists across container restarts, the session does too. If the
session is invalidated by WhatsApp (e.g. you opened WhatsApp Web
elsewhere), you'll need to re-pair — check the logs for a new QR.

**Bot replies aren't reaching users.**
Check `AQ_EVOLUTION_KEY` matches in both `.env` and the bot's env. Also
verify `WEBHOOK_GLOBAL_URL` in Evolution points to `http://aq-bot:5055/webhook`
(container-network name, not localhost).

**M1 worker fills the queue with `:error` results.**
Vision backend is unreachable. Check:
- `curl http://localhost:8000/health` from the M1 → MLX server up?
- Worker's `AQ_VISION_ENDPOINT` matches the server's actual port?
- Worker can reach NAS over SMB? `ls /Volumes/aq-reporter`

**Profile sync fails with permission denied.**
The user running cron needs write access to the target path. On
Synology Web Station, the web root is typically owned by `http:http`.
Either run sync as that user, or set group write perms.

## Next sprints (after pilot)

- **Voice notes** — Whisper.cpp or MLX-Whisper on the M1, transcribe
  Bahasa, treat transcript as a text report.
- **Smart Citizen integration** — fetch sensor data from a Smart Citizen
  Kit deployed in Bukit, merge with community reports.
- **Replication kit** — extract the configurable bits into a template
  repo other Fab Labs can clone (target: Yucatán, Kerala, Detroit).
- **Bioregional dashboard** — aggregator pulling from all Planet AI
  Community nodes via Murmurations search.
- **Action loop** — define and instrument the "action" half of the
  observation→action latency hypothesis. Pick one credible action
  channel (monthly banjar report, Fab City amplification, mask program).
