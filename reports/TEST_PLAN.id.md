[English](TEST_PLAN.md) · **Bahasa Indonesia** · [Español](TEST_PLAN.es.md)

# Rencana uji pra-beta — MLX + bot end-to-end

Ini adalah checklist duduk-sambil-minum-kopi. Jalankan secara berurutan pada pagi
yang biasa — seharusnya memakan total 1–2 jam. Pada akhirnya Anda akan tahu apakah
sistem siap untuk 3–5 pengguna beta Bukit pertama.

Anda tidak memerlukan NAS untuk langkah 1–5. Sisi MLX bersifat mandiri
dan dapat diuji sendiri terlebih dahulu.

---

## Fase A — Server MLX (M1 saja, ~30 menit)

### A1. Siapkan lingkungan Python

```bash
cd ~/fablab-bali/aq-reporter

python3 -m venv ~/.venv/aq-vision
source ~/.venv/aq-vision/bin/activate

pip install --upgrade pip
pip install mlx-vlm fastapi uvicorn pillow requests
```

✅ Berhasil: `pip list` menampilkan mlx-vlm, fastapi, uvicorn, pillow, requests.

⚠️ Jika mlx-vlm gagal terpasang: Anda tidak menggunakan Apple Silicon, atau
macOS Anda lebih lama dari 13.5. Perbaiki env sebelum melanjutkan.

### A2. Verifikasi mlx-vlm dapat memuat model secara mandiri

Jangan percaya wrapper kami dulu — uji mlx-vlm itu sendiri terlebih dahulu:

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

✅ Berhasil: mencetak `Model loaded OK` setelah unduhan 1–5 menit.

⚠️ Jika impor `apply_chat_template` gagal: mlx-vlm mengubah API-nya.
Periksa `python3 -c "import mlx_vlm; print(mlx_vlm.__version__)"` dan
cari di changelog mlx-vlm. Perbaikan yang mungkin: sesuaikan baris impor di
`mlx_vision_server.py` ke path baru yang sesuai.

### A3. Jalankan server kami dan akses /health

```bash
cd ~/fablab-bali/aq-reporter
python mlx_vision_server.py
```

Tunggu `model ready in N.Ns` di log. Di terminal kedua:

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

✅ Berhasil:
```json
{
  "ok": true,
  "model": "mlx-community/Phi-3.5-vision-instruct-4bit",
  "mlx_available": true
}
```

### A4. Kirim gambar nyata ke /analyze

Temukan foto apa pun di Mac Anda (foto Bukit asli adalah yang terbaik). Lalu:

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

✅ Berhasil: respons adalah objek JSON yang valid dengan `category`, `severity`,
`confidence`, `indicators`. Latensi pada M1 16GB seharusnya 5–15 detik
untuk Phi-3.5-Vision-4bit.

⚠️ Jika responsnya `{"detected": false, "category": "other", ...
"model_version": "...:parse_error"}`: model mengembalikan prosa alih-alih
JSON. Phi-3.5 sesekali melakukan ini. Jika terjadi pada lebih dari
~1 dari 5 foto, pertimbangkan beralih ke Qwen2-VL-7B-4bit (atur
`AQ_MLX_MODEL=mlx-community/Qwen2-VL-7B-Instruct-4bit`).

### A5. Uji kualitas klasifikasi pada 5 contoh yang sengaja dipilih

Ini adalah langkah terpenting. Temukan 5 foto yang mencakup spektrumnya:

1. Pembakaran sampah yang jelas (asap + api terlihat)
2. Debu konstruksi / lokasi bangunan
3. Pemandangan lalu lintas / asap knalpot motor
4. Lanskap Bukit normal (tanpa polusi) — uji false-positive
5. Selfie di dalam ruangan atau foto makanan — uji ketidakrelevanan

Jalankan masing-masing melalui `/analyze` dan catat hasilnya. Jangan harapkan
kesempurnaan. Harapkan:

- Pembakaran sampah → `category: burning, severity: high or critical`
- Konstruksi → `category: construction, severity: medium`
- Lalu lintas → `category: vehicle, severity: medium`
- Lanskap bersih → `category: none, detected: false`
- Selfie → `category: none or other, detected: false`

Jika 4/5 masuk ke kelompok yang benar, ship. Jika 3/5, prompt-nya perlu diperbaiki.
Jika 2/5 atau lebih buruk, ganti model.

---

## Fase B — Integrasi Worker → MLX (~20 menit)

### B1. Hentikan server MLX sebentar, lalu restart di latar belakang

```bash
# Ctrl-C the running server
# Then start it as a background process:
cd ~/fablab-bali/aq-reporter
nohup python mlx_vision_server.py > /tmp/mlx-server.log 2>&1 &
echo $! > /tmp/mlx-server.pid

# Verify it came back up
sleep 5 && curl -s http://localhost:8000/health
```

### B2. Jalankan worker terhadap antrean palsu lokal (tanpa perlu NAS)

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

Worker berjalan selamanya — hentikan dengan Ctrl-C setelah Anda melihatnya
memproses pekerjaan (`timeout 60` akan mematikannya setelah 60 detik bagaimanapun juga).

✅ Berhasil: Anda melihat baris log seperti
```
analyzing AQ_LOCAL_001 (test1.jpg)
  → burning / high (conf=0.82) in 7.4s
```

### B3. Periksa apa yang ditulis worker

```bash
# Report should now have ai_analysis filled in
cat /tmp/aq-test/reports/AQ_LOCAL_001.json | python3 -m json.tool

# Profile should be in profiles/ (sanitized, no sender info)
cat /tmp/aq-test/profiles/AQ_LOCAL_001.json | python3 -m json.tool

# Job should be in vision_queue/done/ with notify_jid stripped
ls /tmp/aq-test/vision_queue/done/
cat /tmp/aq-test/vision_queue/done/AQ_LOCAL_001.json
```

✅ Berhasil: laporan memiliki `ai_analysis` yang terisi, profil sudah
disanitasi (tanpa `sender_hash`, tanpa `image_path`), dan pekerjaan diarsipkan
di `done/` tanpa `notify_jid`.

---

## Fase C — Bot end-to-end via curl-sebagai-WhatsApp (~20 menit)

Lewati ini jika NAS Anda belum siap. Jika tidak, ini memvalidasi
seluruh pipeline sebelum ada pesan WhatsApp nyata mengenai sistem.

### C1. Jalankan bot secara lokal

Lebih mudah daripada menjalankan Docker untuk pengujian:

```bash
cd ~/fablab-bali/aq-reporter
pip install flask  # if not already
# Override paths so this test uses /tmp/aq-test, not your real data
AQ_VISION_BACKEND=mock python bot_murmurations.py
```

(Kami menggunakan `mock` di sini karena bot tidak memanggil vision — M1 worker
yang melakukannya. Panggilan vision bot hanya menyala jika `synchronous_vision=true` di
config, yang bagaimanapun akan kami hindari di produksi.)

### C2. Simulasikan pesan WhatsApp dengan curl

Bot mendengarkan di `:5055/webhook`. Kirimkan payload berbentuk Evolution:

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

Perhatikan log bot. Anda seharusnya melihat `msg from +6281555000111 type=text`
dan balasan dry-run tentang prompt persetujuan.

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

✅ Berhasil: `reports/` memiliki AQ_*.json baru, `profiles/` memiliki profil
yang cocok dengan `locality: "Bingin"`, tanpa field PII.

---

## Fase D — Audit privasi + keamanan (~15 menit)

Jangan lewati ini. Jalankan sebelum ada pengguna nyata yang mengenai sistem.

### D1. Penyapuan PII pada profil

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

✅ Berhasil: `0 leaks found`.

### D2. Pemeriksaan kewarasan gerbang persetujuan

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

Jika pengirim memiliki persetujuan `granted` dan laporan ada, itu yang diharapkan.
Jika pengirim memiliki persetujuan `unknown` tetapi laporan mereka berhasil lolos,
itu adalah bug — tandai sebelum diberikan ke pengguna.

### D3. Inspeksi file gambar

Buka salah satu foto yang masuk dan periksa:

- Apakah data EXIF GPS ada di file? `exiftool images/AQ_*.jpg | grep GPS`
  → jika ya, Anda sebaiknya menambahkan penghapusan EXIF sebelum mempublikasikan gambar
- Apakah ada wajah yang dapat diidentifikasi terlihat? → tunda auto-blur ke sprint
  berikutnya, tetapi pastikan dokumen persetujuan Anda memberi tahu pengguna bahwa foto mereka mungkin
  menampilkan orang

### D4. Tinjauan teks Bahasa

Buka `bot_murmurations.py`, temukan:

- `CONSENT_PROMPT`
- `CONSENT_CONFIRMED`
- `OPTOUT_CONFIRMED`
- String balasan di `_handle_text`, `_handle_image`, `_handle_location`,
  `_handle_audio`, `_handle_command`

**Kirimkan ini ke penutur asli Bahasa sebelum dilihat pengguna.** Ini
tidak bisa ditawar. Kepercayaan dimulai dari balasan pertama.

---

## Fase E — Checklist kesiapan pengguna beta (5 menit)

Sebelum mengundang 3–5 pengguna pertama Anda, verifikasi:

- [ ] Server MLX berjalan andal selama setidaknya 1 jam (tanpa crash, tanpa OOM)
- [ ] Worker memproses 10+ foto uji tanpa crash
- [ ] Latensi inferensi rata-rata di bawah 20 detik (jika tidak, pengguna akan mengira ini rusak)
- [ ] Balasan bot dalam Bahasa yang baik (D4 di atas)
- [ ] Sinkronisasi profil ke planetai.fab.city berjalan (jalankan `./sync_profiles.sh` sekali, lalu verifikasi sebuah URL seperti `https://planetai.fab.city/bali/profiles/AQ_<id>.json` benar-benar termuat)
- [ ] Anda memiliki cara untuk memantau apa yang terjadi (`tail -f` pada log bot + worker, atau dasbor sederhana)
- [ ] Anda memiliki cara untuk menghapus data pengguna jika mereka meminta (cari berdasarkan sender_hash; hapus report + profile + re-rsync untuk memperbarui mirror publik)
- [ ] Anda memiliki cara untuk menyiarkan ke semua pengguna yang telah menyetujui jika perlu (mis. "bot akan mati untuk pemeliharaan Minggu") — ini kemungkinan berarti skrip kecil sekali pakai menggunakan endpoint send dari Evolution API
- [ ] Daya: NAS pada UPS, M1 tercolok (atau Anda telah menerima bahwa vision berhenti sementara saat M1 tidur)
- [ ] Anda secara pribadi telah menjadi pengguna selama setidaknya 24 jam dan mengirim ~10 laporan nyata tanpa kejutan

---

## Protokol peluncuran beta

Ketika Anda siap, jangan menyebarkan nomor bot ke grup banjar.
Onboarding dalam urutan ini:

1. **Anda** (sudah selesai saat Anda membaca ini)
2. **Satu mitra** — Elaine atau Tafia, seseorang yang akan mengatakan kebenaran kepada Anda
3. **Tiga tetangga Bukit yang bersahabat** yang dapat Anda ajak bicara langsung
4. **Lima lagi, melalui rujukan** dari tiga yang pertama
5. **Satu grup banjar/sekolah kecil** (10–20 orang) — hanya setelah yang di atas terasa stabil selama satu minggu

Di setiap langkah, perhatikan mode kegagalan:
- Apakah orang mengirim lokasi? Jika tidak, UX perlu mendorong lebih keras
- Apakah foto datang dengan konteks yang berguna? Jika tidak, prompt perlu diperbaiki
- Apakah orang mengirim pesan suara? Bangun Whisper di sprint berikutnya
- Berapa rasio laporan yang benar-benar terklasifikasi dengan bersih? Jika <60%, ganti model
- Adakah yang bingung dengan prompt persetujuan? Tulis ulang

Ketika Anda memiliki 50+ laporan dari 10+ pengguna nyata dan sistem telah berjalan
tanpa pengawasan selama satu minggu, Anda telah melewati batas pilot dan dapat mulai
berbicara dengan Fab Lab lain tentang sebuah sister node.
