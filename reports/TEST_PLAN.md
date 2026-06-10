**English** · [Bahasa Indonesia](TEST_PLAN.id.md) · [Español](TEST_PLAN.es.md)

# Pre-beta test plan — MLX + bot end-to-end

This is the sit-down-with-coffee checklist. Run it in order on a normal
morning — should take 1–2 hours total. By the end you'll know whether
the system is ready for the first 3–5 Bukit beta users.

You don't need the NAS for steps 1–5. The MLX side is self-contained
and can be tested on its own first.

---

## Phase A — MLX server (M1 only, ~30 min)

### A1. Set up the Python environment

```bash
cd ~/fablab-bali/aq-reporter

python3 -m venv ~/.venv/aq-vision
source ~/.venv/aq-vision/bin/activate

pip install --upgrade pip
pip install mlx-vlm fastapi uvicorn pillow requests
```

✅ Success: `pip list` shows mlx-vlm, fastapi, uvicorn, pillow, requests.

⚠️ If mlx-vlm fails to install: you're not on Apple Silicon, or your
macOS is older than 13.5. Fix the env before continuing.

### A2. Verify mlx-vlm can load a model standalone

Don't trust our wrapper yet — test mlx-vlm itself first:

```bash
python3 -c "
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
print('mlx-vlm imports OK')
print('Loading Phi-3.5-Vision-4bit (~2.5GB, first run downloads it)...')
model, processor = load('mlx-community/Phi-3.5-vision-instruct-4bit')
config = load_config('mlx-community/Phi-3.5-vision-instruct-4bit')
print('Model loaded OK')
"
```

✅ Success: prints `Model loaded OK` after a 1–5 minute download.

⚠️ If `apply_chat_template` import fails: mlx-vlm changed its API.
Check `python3 -c "import mlx_vlm; print(mlx_vlm.__version__)"` and
search the mlx-vlm changelog. Likely fix: adjust the import line in
`mlx_vision_server.py` to whatever the new path is.

### A3. Run our server and hit /health

```bash
cd ~/fablab-bali/aq-reporter
python mlx_vision_server.py
```

Wait for `model ready in N.Ns` in the logs. In a second terminal:

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

✅ Success:
```json
{
  "ok": true,
  "model": "mlx-community/Phi-3.5-vision-instruct-4bit",
  "mlx_available": true
}
```

### A4. Send a real image to /analyze

Find any photo on your Mac (a real Bukit photo is best). Then:

```bash
# Encode a test image to base64
IMG="$HOME/Desktop/some_photo.jpg"   # ← change to a real path

python3 -c "
import base64, json, requests, sys
img_b64 = base64.b64encode(open(sys.argv[1], 'rb').read()).decode()
prompt = '''Classify this image. Respond with ONLY a JSON object:
{
  \"detected\": true|false,
  \"category\": one of [burning, trash, vehicle, construction, industrial, dust, other, none],
  \"confidence\": 0.0 to 1.0,
  \"indicators\": [short phrases],
  \"description\": one short sentence,
  \"severity\": one of [low, medium, high, critical]
}'''
r = requests.post('http://localhost:8000/analyze',
                  json={'image_b64': img_b64, 'prompt': prompt},
                  timeout=120)
print(json.dumps(r.json(), indent=2))
" "$IMG"
```

✅ Success: response is a valid JSON object with `category`, `severity`,
`confidence`, `indicators`. Latency on M1 16GB should be 5–15 seconds
for Phi-3.5-Vision-4bit.

⚠️ If the response is `{"detected": false, "category": "other", ...
"model_version": "...:parse_error"}`: the model returned prose instead
of JSON. Phi-3.5 occasionally does this. If it happens for more than
~1 in 5 photos, consider switching to Qwen2-VL-7B-4bit (set
`AQ_MLX_MODEL=mlx-community/Qwen2-VL-7B-Instruct-4bit`).

### A5. Test classification quality on 5 deliberate examples

This is the most important step. Find 5 photos that cover the spectrum:

1. Obvious trash burning (smoke + visible fire)
2. Construction dust / building site
3. Traffic / motorbike exhaust scene
4. A normal Bukit landscape (no pollution) — false-positive test
5. Indoor selfie or food photo — irrelevance test

Run each through `/analyze` and write down the result. Don't expect
perfection. Expect:

- Burning trash → `category: burning, severity: high or critical`
- Construction → `category: construction, severity: medium`
- Traffic → `category: vehicle, severity: medium`
- Clean landscape → `category: none, detected: false`
- Selfie → `category: none or other, detected: false`

If 4/5 land in the right bucket, ship. If 3/5, the prompt needs work.
If 2/5 or worse, switch model.

---

## Phase B — Worker → MLX integration (~20 min)

### B1. Stop the MLX server briefly, then restart in background

```bash
# Ctrl-C the running server
# Then start it as a background process:
cd ~/fablab-bali/aq-reporter
nohup python mlx_vision_server.py > /tmp/mlx-server.log 2>&1 &
echo $! > /tmp/mlx-server.pid

# Verify it came back up
sleep 5 && curl -s http://localhost:8000/health
```

### B2. Run the worker against a local fake queue (no NAS needed)

```bash
# Set up a fake repo locally for testing
mkdir -p /tmp/aq-test/{reports,profiles,images,vision_queue}
mkdir -p /tmp/aq-test/vision_queue/{processing,done,failed}

# Copy code into it
cp ~/fablab-bali/aq-reporter/*.py /tmp/aq-test/
cp ~/fablab-bali/aq-reporter/config.json /tmp/aq-test/ 2>/dev/null || \
  echo '{"node_id":"bali.fab.city","bioregion":"indo_pacific_coral_triangle","primary_url":"https://planetai.fab.city/bali"}' \
  > /tmp/aq-test/config.json

# Put a real photo into images/ — use one of your A5 test photos
cp ~/Desktop/some_photo.jpg /tmp/aq-test/images/test1.jpg

# Create a fake report
cat > /tmp/aq-test/reports/AQ_LOCAL_001.json <<EOF
{
  "id": "AQ_LOCAL_001",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "source": "whatsapp",
  "sender_hash": "testsender",
  "type": "photo",
  "description": "test photo from Pecatu",
  "image_path": "/tmp/aq-test/images/test1.jpg",
  "ai_analysis": null,
  "status": "pending",
  "location": {"lat": -8.83, "lon": 115.10}
}
EOF

# Enqueue the vision job
cat > /tmp/aq-test/vision_queue/AQ_LOCAL_001.json <<EOF
{
  "report_id": "AQ_LOCAL_001",
  "image_path": "/tmp/aq-test/images/test1.jpg",
  "queued_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# Run the worker (it processes the queue and exits when empty if we wrap it)
AQ_REPO=/tmp/aq-test \
AQ_VISION_BACKEND=mlx \
AQ_VISION_ENDPOINT=http://localhost:8000/analyze \
AQ_POLL_INTERVAL=1 \
  timeout 60 python ~/fablab-bali/aq-reporter/m1_vision_worker.py
```

The worker runs forever — kill it with Ctrl-C once you've seen it
process the job (`timeout 60` will kill it after 60s anyway).

✅ Success: you see log lines like
```
analyzing AQ_LOCAL_001 (test1.jpg)
  → burning / high (conf=0.82) in 7.4s
```

### B3. Inspect what the worker wrote

```bash
# Report should now have ai_analysis filled in
cat /tmp/aq-test/reports/AQ_LOCAL_001.json | python3 -m json.tool

# Profile should be in profiles/ (sanitized, no sender info)
cat /tmp/aq-test/profiles/AQ_LOCAL_001.json | python3 -m json.tool

# Job should be in vision_queue/done/ with notify_jid stripped
ls /tmp/aq-test/vision_queue/done/
cat /tmp/aq-test/vision_queue/done/AQ_LOCAL_001.json
```

✅ Success: the report has `ai_analysis` populated, the profile is
sanitized (no `sender_hash`, no `image_path`), and the job is archived
in `done/` without `notify_jid`.

---

## Phase C — Bot end-to-end via curl-as-WhatsApp (~20 min)

Skip this if your NAS isn't ready yet. Otherwise this validates the
whole pipeline before any real WhatsApp message hits the system.

### C1. Start the bot locally

Easier than spinning up Docker for testing:

```bash
cd ~/fablab-bali/aq-reporter
pip install flask  # if not already
# Override paths so this test uses /tmp/aq-test, not your real data
AQ_VISION_BACKEND=mock python bot_murmurations.py
```

(We use `mock` here because the bot doesn't call vision — the M1 worker
does. The bot's vision call only fires if `synchronous_vision=true` in
config, which we'd avoid in production anyway.)

### C2. Simulate WhatsApp messages with curl

Bot listens on `:5055/webhook`. Send it Evolution-shaped payloads:

```bash
# First contact — should get consent prompt
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t1","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "pushName":"Test User",
      "messageTimestamp": '$(date +%s)',
      "message":{"conversation":"halo"}
    }
  }'
```

Watch the bot logs. You should see `msg from +6281555000111 type=text`
and a dry-run reply about the consent prompt.

```bash
# Grant consent
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t2","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "messageTimestamp": '$(date +%s)',
      "message":{"conversation":"SETUJU"}
    }
  }'

# Send a text report
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t3","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "messageTimestamp": '$(date +%s)',
      "message":{"conversation":"ada asap di pantai bingin"}
    }
  }'

# Share location (Bingin)
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t4","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "messageTimestamp": '$(date +%s)',
      "message":{"locationMessage":{"degreesLatitude":-8.806,"degreesLongitude":115.130}}
    }
  }'
```

✅ Success: `reports/` has a new AQ_*.json, `profiles/` has a matching
profile with `locality: "Bingin"`, no PII fields.

---

## Phase D — Privacy + safety audit (~15 min)

Don't skip this. Run before any real user hits the system.

### D1. PII sweep on profiles

```bash
cd ~/fablab-bali/aq-reporter
python3 -c "
import json, glob
bad = 0
for p in glob.glob('profiles/AQ_*.json'):
    prof = json.load(open(p))
    leaks = [k for k in prof if k in ('sender','sender_hash','image_path','media_key','phone','number')]
    leaks += [k for k in prof if k.startswith('_')]
    if leaks:
        print(f'LEAK in {p}: {leaks}')
        bad += 1
print(f'{bad} leaks found')
"
```

✅ Success: `0 leaks found`.

### D2. Consent gate sanity check

```bash
# A sender who never consented should NEVER have a report in profiles/.
# Pull a sample sender_hash and check.
python3 -c "
import json, glob, hashlib
# Phone number you tested with above
test_phone = '+6281555000111'
expected_hash = hashlib.sha256(test_phone.encode()).hexdigest()[:16]

# Did they grant consent?
consent = json.load(open('consent.json')) if open('consent.json') else {}
print('Consent status:', consent.get(expected_hash, 'unknown'))

# Are their reports in the canonical store?
for r_path in glob.glob('reports/AQ_*.json'):
    r = json.load(open(r_path))
    if r.get('sender_hash') == expected_hash:
        print('  Found report:', r_path)
"
```

If the sender has `granted` consent and reports exist, that's expected.
If the sender has `unknown` consent but their reports made it through,
that's a bug — flag it before going to users.

### D3. Image file inspection

Open one of the photos that came through and check:

- Is the EXIF GPS data in the file? `exiftool images/AQ_*.jpg | grep GPS`
  → if yes, you should add EXIF stripping before publishing images
- Are there identifiable faces visible? → defer auto-blur to a later
  sprint, but make sure your consent doc tells users their photos may
  show people

### D4. Bahasa text review

Open `bot_murmurations.py`, find:

- `CONSENT_PROMPT`
- `CONSENT_CONFIRMED`
- `OPTOUT_CONFIRMED`
- The reply strings in `_handle_text`, `_handle_image`, `_handle_location`,
  `_handle_audio`, `_handle_command`

**Send these to a native Bahasa speaker before users see them.** This
is non-negotiable. Trust starts with the first reply.

---

## Phase E — Beta-user readiness checklist (5 min)

Before inviting your first 3–5 users, verify:

- [ ] MLX server runs reliably for at least 1 hour (no crashes, no OOM)
- [ ] Worker processes 10+ test photos without crashing
- [ ] Average inference latency is under 20 seconds (else users will think it's broken)
- [ ] Bot replies are in good Bahasa (D4 above)
- [ ] Profile sync to planetai.fab.city is working (run `./sync_profiles.sh` once, then verify a URL like `https://planetai.fab.city/bali/profiles/AQ_<id>.json` actually loads)
- [ ] You have a way to monitor what's happening (`tail -f` on bot + worker logs, or a simple dashboard)
- [ ] You have a way to remove a user's data if they ask (search by sender_hash; delete report + profile + re-rsync to update the public mirror)
- [ ] You have a way to broadcast to all consented users in case you need to (e.g. "the bot will be down for maintenance Sunday") — this likely means a small one-off script using Evolution API's send endpoint
- [ ] Power: NAS is on a UPS, M1 is plugged in (or you've accepted that vision pauses when M1 sleeps)
- [ ] You've personally been a user for at least 24 hours and sent ~10 real reports without surprises

---

## Beta launch protocol

When you're ready, don't blast a banjar group with the bot number.
Onboard in this order:

1. **You** (already done by the time you read this)
2. **One partner** — Elaine or Tafia, someone who'll tell you the truth
3. **Three friendly Bukit neighbors** you can talk to in person
4. **Five more, by referral** from the first three
5. **One small banjar/school group** (10–20 people) — only after the above feel stable for a week

At each step, watch the failure modes:
- Are people sending location? If not, the UX needs to push harder
- Are photos coming with useful context? If not, the prompt needs work
- Are people sending voice notes? Build Whisper next sprint
- What ratio of reports actually classify cleanly? If <60%, model swap
- Is anyone confused by the consent prompt? Rewrite it

When you have 50+ reports from 10+ real users and the system has run
unattended for a week, you've cleared the pilot bar and can start
talking to other Fab Labs about a sister node.
