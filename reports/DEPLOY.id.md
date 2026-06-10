[English](DEPLOY.md) · **Bahasa Indonesia** · [Español](DEPLOY.es.md)

# Panduan deploy — Making Sense Bali Reporter

Jalankan node PLANETAI Community-tier pertama di infrastruktur rumahan.

## Apa yang berjalan di mana

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

Bot tidak pernah memblokir karena inferensi. Jika M1 dalam keadaan tidur, foto menumpuk
di antrean dan diproses saat ia bangun. Jika M1 mati selama satu
minggu, bot tetap mengumpulkan laporan — laporan tersebut hanya tetap tak-terklasifikasi
sampai seseorang (atau worker fallback) memprosesnya.

## Prasyarat

- Synology DSM 7.2+ dengan Container Manager terpasang
- M1 MacBook (atau Mac Apple Silicon apa pun) dengan RAM minimal 16GB
- Sebuah nomor WhatsApp yang dapat Anda dedikasikan untuk bot (nomor pribadi Anda
  bisa digunakan untuk pilot, tetapi Anda akan menginginkan nomor terpisah sebelum penskalaan)
- Sebuah UPS untuk NAS — pemadaman listrik di Bukit itu nyata, ~$80 sekali bayar
- Hosting web `planetai.fab.city` siap menerima `/bali/profiles/*.json`

## 1. Pindahkan kode ke NAS

Dari laptop Anda:

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

## 2. Konfigurasikan secret

SSH ke NAS:

```bash
cd /volume1/docker/aq-reporter
cp .env.example .env

# Generate a strong API key — Evolution and the bot share it
openssl rand -hex 32  # paste into .env as EVOLUTION_API_KEY

# Edit config.json if you want to override defaults (node_id, etc.)
```

Buat `consent.json` dengan objek kosong agar bot dapat menulis ke dalamnya:

```bash
echo '{}' > consent.json
```

## 3. Jalankan kontainer

```bash
cd /volume1/docker/aq-reporter
docker compose up -d
docker compose logs -f evolution-api
```

Di log Evolution Anda akan melihat sebuah kode QR. **Buka WhatsApp di
ponsel yang Anda gunakan untuk bot → Settings → Linked Devices → Link a
Device → pindai QR-nya.**

Setelah terhubung:

```bash
docker compose logs -f aq-bot
```

Anda seharusnya melihat `AQBot ready — node=bali.fab.city listening on :5055/webhook`.

## 4. Kirim pesan uji

Dari akun WhatsApp mana pun, kirim pesan ke nomor bot:

> halo

Bot seharusnya merespons dengan prompt persetujuan (Bahasa + Inggris). Balas
**SETUJU**. Bot seharusnya mengonfirmasi. Lalu kirim:

> ada asap di pantai bingin

Bot seharusnya membalas dengan meminta lokasi Anda. Kirim sebuah lokasi (paperclip →
Location → Send your current location). Bot seharusnya membalas bahwa
laporan sudah lengkap.

Periksa NAS:

```bash
ls /volume1/docker/aq-reporter/data/reports/   # should have AQ_*.json
ls /volume1/docker/aq-reporter/data/profiles/  # should have matching profile
cat /volume1/docker/aq-reporter/data/profiles/AQ_*.json | jq .locality
# → "Bingin"
```

Jika Anda melihat `Bingin` (atau `Bukit` dari fallback bbox), bot telah terhubung
dari ujung ke ujung di sisi NAS.

## 5. Siapkan M1 vision worker

Di M1 MacBook:

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

Jalankan server MLX (ini memicu unduhan model pada run pertama, ~2.5GB):

```bash
cd ~/fablab-bali/aq-reporter
python mlx_vision_server.py
```

Di terminal kedua, jalankan worker:

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

(Agar Evolution dapat dijangkau dari M1, Anda perlu mengekspos port
8080 di LAN NAS — lihat bagian yang dikomentari di `docker-compose.yml`.)

## 6. Uji foto end-to-end

Kirim bot sebuah foto polusi apa pun (pemandangan berasap, tumpukan sampah,
debu konstruksi). Anda seharusnya melihat:

- Log bot (NAS): `msg from +62... type=image` → foto disimpan, diantrekan
- Log worker (M1): `analyzing AQ_... → burning / high (conf=0.85) in 6.3s`
- Bot membalas di WhatsApp: "🔥 Hasil analisis / Analysis: kategori burning..."
- Profil baru di `data/profiles/` dengan `ai_analysis` terisi

## 7. Siapkan sinkronisasi profil ke planetai.fab.city

Sunting `sync_profiles.sh` (atau atur env var di cron) untuk mengarah ke tempat
planetai.fab.city disajikan:

- Jika planetai di-hosting **di NAS yang sama** (Synology Web Station):
  `AQ_SYNC_TARGET=/volume1/web/planetai/bali/profiles/`
- Jika planetai di-hosting **di VPS** dengan akses SSH:
  `AQ_SYNC_TARGET=user@planetai.fab.city:/var/www/planetai/bali/profiles/`
  (siapkan SSH key terlebih dahulu agar cron dapat berjalan tanpa pengawasan)
- Jika planetai di-hosting di **static host** (Netlify/Vercel/Cloudflare
  Pages): alur berbasis git push mungkin lebih sederhana — arahkan skrip ke
  clone lokal dari repo situs dan push dari cron.

Uji sekali:

```bash
DRY_RUN=1 ./sync_profiles.sh   # shows what it would do
./sync_profiles.sh             # actually sync
```

Lalu daftarkan cron-nya. Di Synology: **Control Panel → Task Scheduler →
Create → Scheduled Task → User-defined script**:

```bash
/volume1/docker/aq-reporter/sync_profiles.sh >> /var/log/aq-sync.log 2>&1
```

Jadwal: setiap 5 menit.

## 8. Kirimkan skema ke Murmurations

Setelah profil dapat diakses publik di
`https://planetai.fab.city/bali/profiles/AQ_*.json`, kirim skema
ke test index terlebih dahulu:

```bash
curl -X POST https://test-index.murmurations.network/v2/nodes \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://planetai.fab.city/bali/profiles/<an-id>.json"}'
```

Ketika itu kembali dengan bersih (round-trip), ubah `murmurations_auto_index: true` di
`config.json` dan restart bot. Laporan baru akan otomatis terdaftar di
index.

## 9. Onboarding 5 pengguna pertama Anda

Pilih 5 orang dari Bukit yang Anda kenal baik — seorang pemimpin banjar, beberapa
tetangga, seseorang dari sekolah. Pandu mereka langsung secara tatap muka.
Perhatikan pertanyaan apa yang mereka ajukan. Celah umum yang dapat diperkirakan:

- Banyak yang tidak tahu cara berbagi lokasi → rekam panduan video 30 detik
- Pesan suara akan masuk dengan segera → jadwalkan sprint Whisper
- Orang akan mengirim foto tanpa konteks ("lihat ini!") → template balasan
  bot perlu memperjelas bahwa lokasi itu wajib

## Pemeriksaan operasional

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

## Pemecahan masalah

**Evolution API kehilangan sesi WhatsApp setelah reboot.**
Data sesi Baileys berada di `data/evolution/`. Selama volume tersebut
bertahan lintas restart kontainer, sesinya juga bertahan. Jika
sesi diinvalidasi oleh WhatsApp (mis. Anda membuka WhatsApp Web
di tempat lain), Anda perlu memasangkan ulang — periksa log untuk QR baru.

**Balasan bot tidak sampai ke pengguna.**
Periksa apakah `AQ_EVOLUTION_KEY` cocok di `.env` maupun di env bot. Verifikasi juga
bahwa `WEBHOOK_GLOBAL_URL` di Evolution mengarah ke `http://aq-bot:5055/webhook`
(nama container-network, bukan localhost).

**M1 worker mengisi antrean dengan hasil `:error`.**
Backend vision tidak dapat dijangkau. Periksa:
- `curl http://localhost:8000/health` dari M1 → apakah server MLX hidup?
- Apakah `AQ_VISION_ENDPOINT` worker cocok dengan port aktual server?
- Dapatkah worker menjangkau NAS melalui SMB? `ls /Volumes/aq-reporter`

**Sinkronisasi profil gagal dengan permission denied.**
Pengguna yang menjalankan cron memerlukan akses tulis ke path target. Di
Synology Web Station, web root biasanya dimiliki oleh `http:http`.
Jalankan sync sebagai pengguna tersebut, atau atur izin tulis grup.

## Sprint berikutnya (setelah pilot)

- **Voice notes** — Whisper.cpp atau MLX-Whisper di M1, transkripsi
  Bahasa, perlakukan transkrip sebagai laporan teks.
- **Integrasi Smart Citizen** — ambil data sensor dari Smart Citizen
  Kit yang di-deploy di Bukit, gabungkan dengan laporan komunitas.
- **Kit replikasi** — ekstrak bagian yang dapat dikonfigurasi ke dalam repo
  template yang dapat di-clone Fab Lab lain (target: Yucatán, Kerala, Detroit).
- **Dasbor bioregional** — agregator yang menarik dari semua Planet AI
  Community node melalui pencarian Murmurations.
- **Action loop** — definisikan dan instrumentasikan paruh "action" dari
  hipotesis latensi observasi→aksi. Pilih satu saluran aksi yang kredibel
  (laporan banjar bulanan, amplifikasi Fab City, program masker).
