[English](SETUP.md) · **Bahasa Indonesia** · [Español](SETUP.es.md)

# Making Sense Bali — generator sinkronisasi data (mini)

Memanggang awal data situs sehingga pengunjung memuat secara instan alih-alih menggempur
API Smart Citizen secara langsung, dan membawa laporan warga yang disetujui dari NAS keluar
ke peta publik. Berjalan di **mini** (egress internet nyata + exo lokal).

Setiap lari menulis ke dalam repo dan mendorong (push):
- `data/sensors.json` — snapshot kit Smart Citizen yang dikenal (+ OpenAQ jika kunci diatur)
- `data/reports/` + `index.json` — profil Murmurations yang disetujui ditarik dari NAS
- `data/areas.json` — rekap per-lingkungan (jumlah, kategori, tag teratas, keparahan maksimum, PM2.5 terdekat) + narasi exo 2-kalimat opsional

Ia bersifat **fail-safe**: setiap tahap terisolasi; satu kegagalan tidak pernah memblokir yang lain, dan lari tidak pernah merusak jadwal.

## Penyiapan sekali saja (di mini)

1. **Kloning repo** di tempat yang stabil:
   ```
   git clone git@github.com:mdg-bali/makingsensebali.git ~/makingsensebali
   ```

2. **GitHub deploy key (akses push)** — agar mini dapat mendorong:
   ```
   ssh-keygen -t ed25519 -f ~/.ssh/msb_deploy -N ""
   ```
   Tambahkan `~/.ssh/msb_deploy.pub` ke repo di GitHub → **Settings → Deploy keys → Add → Allow write access**.
   Arahkan git ke sana (di `~/.ssh/config`):
   ```
   Host github.com
     IdentityFile ~/.ssh/msb_deploy
     IdentitiesOnly yes
   ```

3. **Kunci SSH mini → NAS (untuk penarikan laporan)** — agar `rsync` bekerja tanpa kata sandi:
   ```
   ssh-copy-id fablabbali@tx-nas-bali     # or append the mini's pubkey to the NAS authorized_keys
   rsync -az --include='AQ_*.json' --exclude='*' \
     fablabbali@tx-nas-bali:/volume1/docker/aq-reporter/data/profiles/ ~/tmp_test/   # verify it pulls
   ```
   (Konfirmasikan jalur profil NAS; pada penerapan ini jalurnya `/volume1/docker/aq-reporter/data/profiles/`.)

4. **Edit plist** `com.fabcity.makingsense-sync.plist` — perbaiki `MSB_REPO_DIR`, `MSB_NAS_RSYNC_SRC`, `MSB_NAS_PHOTOS_SRC` (foto publik yang sudah dibersihkan EXIF, agar peta dapat menampilkannya), jalur python, dan jalur log agar cocok dengan mini. Atur `MSB_NARRATIVE` ke `0` untuk mengirim rekap terstruktur saja (tanpa paragraf exo).

   **Jaringan kualitas-udara eksternal (inilah cara Anda melampaui keempat kit).** Masing-masing bersifat upaya-terbaik (best-effort): kegagalan dicatat dan dilewati, tidak pernah memblokir yang lain. **Rahasia ada di `.env` yang ter-gitignore di sebelah `generate.py` (BUKAN di plist yang terlacak — ini repo publik).** Salin kunci ke sana; `generate.py` memuatnya saat startup dan ia bertahan terhadap penerapan-ulang plist:

   ```
   # tools/makingsense-sync/.env   (gitignored)
   MSB_AQICN_TOKEN=...
   MSB_AQICN_STATIONS=-519205
   MSB_PURPLEAIR_KEY=...
   MSB_PURPLEAIR_IDS=36601,46949
   ```

   - **AirGradient** — aktif secara **default, tanpa kunci**. Menarik umpan data-terbuka AirGradient publik dan menyimpan lokasi-lokasi Bali — ini adalah sensor **Nafas Foundation** (Tonja, Pemogan, …). `pm02` adalah pembacaan µg/m³ nyata. Atur `MSB_AIRGRADIENT=0` untuk menonaktifkan.
   - `MSB_AQICN_TOKEN` — **referensi bernilai tertinggi.** Token gratis dari <https://aqicn.org/data-platform/token/> (hanya email). Menghasilkan **monitor pemerintah KLHK** resmi (stasiun WAQI Bali tidak terdaftar, jadi UID yang dikenal juga dipasang melalui `MSB_AQICN_STATIONS`). WAQI melaporkan PM2.5 sebagai sub-indeks US-AQI, jadi generator mengonversinya kembali ke µg/m³ (titik patah EPA pra-2024) dan menyimpan AQI mentah di `reading.aqi` dengan flag `pm25_from_aqi: true`. Periksa kewajaran lari pertama terhadap halaman stasiun di aqicn.org.
   - `MSB_PURPLEAIR_KEY` — kunci baca gratis dari <https://develop.purpleair.com/>. `MSB_PURPLEAIR_IDS` default ke `36601,46949` (Jimbaran + Klungkung Lumi Clinic); tambahkan indeks lain saat muncul di peta PurpleAir.
   - `MSB_OPENAQ_KEY` — dibiarkan terpasang tetapi **jangan mengharapkan apa pun**: kedua stasiun Bali OpenAQ satu-satunya (Ubud, Balangan) telah offline sejak 2025. Disimpan untuk hari ketika yang aktif muncul kembali.
   - Tidak ditambahkan (tidak ada jalur bersih/berdaulat): sensor vila pribadi **IQAir** (pemuat halaman ber-versi-build, rusak setiap penerapan) dan stasiun **Nafas** yang tidak ada di umpan publik AirGradient (realtime berada di balik autentikasi aplikasi). Gunakan AirGradient untuk Nafas; tinjau ulang IQAir hanya jika mereka mengekspos API yang nyata.

5. **Dry run** (semuanya kecuali push):
   ```
   MSB_REPO_DIR=~/makingsensebali python3 ~/makingsensebali/tools/makingsense-sync/generate.py --dry-run
   ```
   Periksa `data/sensors.json`, `data/areas.json`, dan `data/reports/index.json` terlihat benar, serta ringkasan `areas.json` terbaca dengan baik (jika tidak, atur `MSB_NARRATIVE=0`).

6. **Pasang jadwal** (setiap 15 menit):
   ```
   cp ~/makingsensebali/tools/makingsense-sync/com.fabcity.makingsense-sync.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.fabcity.makingsense-sync.plist
   ```

7. **Verifikasi**: `tail -f ~/makingsensebali/tools/makingsense-sync/sync.log` dan konfirmasi sebuah commit mendarat di GitHub.

## Catatan
- Deploy key dicakup ke satu repo ini saja (push saja). Tidak ada rahasia yang ada di repo.
- Irama adalah `StartInterval` (900s = 15 menit). Sensor tidak berubah cepat; laporan muncul dalam satu siklus setelah persetujuan.
- Jika mini sedang tidur, siklus dilewati dan dilanjutkan saat bangun — dapat diterima untuk situs kampanye, tetapi inilah alasan ini berada di mini, bukan di NAS yang selalu-aktif (yang ter-firewall dari GitHub + API SC).
- **Fase 2 (sisi situs, perubahan terpisah):** `data.js` harus memuat `data/sensors.json` terlebih dahulu (instan) sebelum penyegaran langsung apa pun, dan home/dashboard harus merender `data/areas.json`. Hingga saat itu generator memproduksi file tetapi situs tetap mengambil sensor secara langsung.
