[English](PLATFORM_REVISION.md) · **Bahasa Indonesia** · [Español](PLATFORM_REVISION.es.md)

# Making Sense Bali · Ringkasan Revisi Platform (v2)

**Status:** ringkasan — belum dimulai.
**Penanggung jawab eksekusi:** Claude Code (atau pengembang yang bekerja di basis kode). Dokumen ini adalah serah terima; semua yang dibutuhkan Claude Code untuk mengerjakan pekerjaan ini seharusnya dapat diturunkan dari sini ditambah repo.
**Penanggung jawab maksud:** Tomas Diez (penanggung jawab Making Sense Bali). Baca [README.md](../README.md) terlebih dahulu jika Anda belum familier dengan kampanye ini.
**Terakhir diperbarui:** 2026-05-30.

---

## 1. Mengapa revisi ini

Dasbor saat ini di `mdg-bali.github.io/makingsensebali/dashboard/` bekerja sebagai tampilan *snapshot*: peta sensor dengan pembacaan terbarunya, daftar laporan warga yang ditampilkan sebagai kartu, beberapa panel rujukan. Ini membuktikan bahwa kampanye ada. Ini belum membantu siapa pun untuk *menginterpretasikan* apa yang terjadi secara lingkungan di Bali.

Pergeseran yang dihadirkan revisi ini: dari "berapa pembacaan PM2.5 saat ini di titik ini" menjadi "**apa yang berubah di lingkungan ini selama sehari terakhir, dan apakah itu terkait dengan apa yang dilaporkan orang?**" Pertanyaan itulah yang mengubah dasbor menjadi alat yang benar-benar dapat digunakan oleh koordinator banjar, analis Dinas Kesehatan, atau orang tua yang khawatir tentang asma anaknya.

Tiga kapabilitas konkret membuat pergeseran itu terjadi:

1. **Grafik deret waktu** per metrik sensor, pada dua jendela: 24 jam terakhir dan 7 hari terakhir. Nilai statis saat ini tidak memadai untuk keputusan lingkungan apa pun.
2. **Deteksi puncak/anomali** yang memunculkan momen-momen yang layak diselidiki, alih-alih meminta manusia mengamati grafik untuk menemukannya.
3. **Korelasi dua arah antara puncak sensor dan laporan warga.** Ketika lonjakan PM terjadi pada saat yang sama dengan seseorang melaporkan pembakaran sampah dua jalan dari sana, dasbor seharusnya menghubungkan kedua fakta itu. Ketika lonjakan terjadi tanpa laporan, dasbor seharusnya menyarankan "ini sepertinya ada sesuatu — adakah yang mau melaporkan apa yang mereka lihat?"

Bersama-sama, hal-hal ini mengubah dasbor dari tampilan pasif menjadi instrumen partisipatif yang sesungguhnya dibutuhkan oleh metodologi Making Sense kampanye ini.

Selain itu, komponen laporan membutuhkan perombakan UI — grid kartu saat ini terlalu berat untuk sesuatu yang secara konsep merupakan umpan observasi warga. Jadikan umpan, yang dapat diperluas saat diklik.

## 2. Keadaan saat ini — apa yang ada hari ini

| Permukaan | Berkas | Catatan |
|---|---|---|
| Halaman arahan | [`index.html`](../index.html) (1234 baris) | Pembingkaian metodologi, tautan survei, konteks proyek. Sebagian besar baik-baik saja; di luar cakupan revisi ini kecuali deret waktu/puncak butuh widget ringkasan di sini. |
| Dasbor | [`dashboard/index.html`](../dashboard/index.html) (779 baris) | Peta + statusbar + panel seleksi + umpan laporan + sensor terurut + standar rujukan + implikasi kesehatan. Inti dari revisi ini. |
| Lapisan data sensor | [`data.js`](../data.js) (609 baris) | Mengambil dari Smart Citizen (`fetchSmartCitizenSensors`, `fetchSmartCitizenDetail`), OpenAQ (`fetchOpenAQSensors`), PurpleAir, Sensor.Community. Juga mengambil laporan warga dari JSON statis di `data/reports/`. |
| CF Worker (proksi CORS) | [`worker/openaq-proxy.js`](../worker/openaq-proxy.js) (172 baris) | Proksi OpenAQ. Pola yang diikuti jika sumber lain butuh bypass CORS. |
| Komponen laporan | [`reports/`](../reports/) (~36KB dokumen + kode Python) | Bot WhatsApp + dasbor operator. **Di luar cakupan** revisi ini — front-end mengonsumsi laporan sebagai JSON statis, tidak diperlukan perubahan API. |
| Data laporan statis | `data/reports/*.json` | Laporan warga yang disetujui sebagai berkas JSON individual ditambah manifes `index.json`. Inilah yang dibaca `fetchReports()` di data.js. |

Pengkabelan yang sudah ada dan perlu diketahui:

- **Chart.js 4.4.0 sudah dimuat** di `dashboard/index.html` (baris 16). Saat ini belum digunakan. Tidak diperlukan dependensi charting baru.
- **Leaflet + leaflet-heat** dimuat untuk peta. Peta merender baik pin sensor maupun heatmap kepadatan laporan.
- **`state.reports`** menyimpan daftar laporan saat ini di JS dasbor (diisi oleh `fetchReports()` di data.js).
- **`state.sensors`** menyimpan sensor (pembacaan BME680/HM3301 masuk via API SC sebagai satu perangkat dengan beberapa jenis sensor).
- **Kotak pembatas Bali** dikonfigurasi di `BALI_BOUNDS` / `BALI_CENTER` di data.js — paginasi peta dunia memfilter berdasarkan ini.
- **ID sensor Smart Citizen** yang digunakan kampanye hari ini didokumentasikan di [`hardware/diy-node/firmware/diy_node/diy_node.ino`](../hardware/diy-node/firmware/diy_node/diy_node.ino) (174 = BMP280 Temp, 56 = SHT31 RH, 175 = BMP280 Pressure, 87/88/89 = PMS5003 PM2.5/10/1). Endpoint SC `/v0/sensors` adalah sumber otoritatif untuk ID baru saat kit lain mulai aktif.

Rendering laporan yang ada (`renderReportFeed()` di `dashboard/index.html` baris 501) sudah melakukan iterasi `state.reports` menjadi umpan HTML — jadi kerangkanya sudah ada, kartunya hanya perlu didesain ulang.

## 3. Keadaan sasaran — apa yang harus dibangun

### 3.1 Grafik deret waktu (per metrik, per perangkat)

Untuk setiap sensor yang ditampilkan di panel "Selected" pada peta, dasbor seharusnya menampilkan:

- Grafik **24 jam terakhir** — resolusi temporal tinggi (setiap pembacaan)
- Grafik **7 hari terakhir** — diturunkan resolusinya (bin per jam atau per 4 jam, tergantung kepadatan)

Grafik harus per-metrik (Temperatur, Kelembapan, Tekanan, PM1, PM2.5, PM10, resistansi gas bila tersedia). Render dengan Chart.js (sudah dimuat).

**Permukaan API untuk data historis:**

`/v0/devices/{id}/readings` milik Smart Citizen menerima:
- `sensor_id` — wajib, ID sensor global
- `from` — stempel waktu ISO 8601 (awal jendela)
- `to` — stempel waktu ISO 8601 (akhir jendela)
- `rollup` — pengelompokan opsional (mis. `5m`, `1h`)

Helper pengambilan riwayat berada di `data.js`:

```js
async function fetchSmartCitizenHistory(deviceId, sensorId, fromIso, toIso, rollup = null) {
  // Returns [{ recorded_at: ISO, value: number }, ...]
}
```

Untuk sumber OpenAQ dan Sensor.Community, endpoint riwayat memang ada tetapi memiliki bentuk yang berbeda. Perlakukan riwayat OpenAQ sebagai Fase 2 — untuk peluncuran v2, deret waktu hanya diperlukan untuk perangkat SC (yang mencakup node DIY). Sumber lain dapat menampilkan hanya nilai saat ini.

**Caching:** panggil `localStorage` untuk meng-cache pengambilan historis dengan TTL 5 menit. Mengambil ulang 7 hari riwayat pada setiap pemuatan halaman boros dan memakan kuota terhadap API SC.

**Penerimaan yang diperlukan:** membuka panel "Selected" peta untuk perangkat Smart Citizen menampilkan dua strip grafik (24j, 7h) untuk setiap sensor yang terpasang. Status pemuatan terlihat selama pengambilan. Status kosong dengan pesan yang masuk akal jika belum ada data historis (perangkat baru).

### 3.2 Deteksi puncak / anomali

Untuk setiap deret waktu yang ditampilkan, munculkan titik-titik yang anomali secara statistik atau semantik.

**Dua metode deteksi yang saling melengkapi, keduanya per-metrik:**

1. **Berbasis ambang** (semantik) — gunakan nilai rujukan terpublikasi yang sudah didokumentasikan di panel standar rujukan dasbor:
   - PM2.5: pedoman harian WHO 5 µg/m³, US AQI "moderate" 12, "unhealthy for sensitive groups" 35
   - PM10: pedoman harian WHO 45 µg/m³, US AQI moderate 55
   - Temperatur: kenyamanan dalam ruangan 24–28°C, perhatian tekanan panas >32°C
   - Kelembapan: ambang risiko jamur >60% RH berkelanjutan
   - Resistansi gas: relatif saja — tanpa ambang absolut, gunakan metode z-score
   
   Dokumentasikan ambang-ambang ini dalam satu tabel `THRESHOLDS` di data.js (atau modul `peaks.js` baru) agar nilai kanonis berada di satu tempat.

2. **Statistik** (relatif-anomali) — untuk setiap metrik, hitung garis dasar bergulir 7 hari (rata-rata + simpangan baku) untuk perangkat. Tandai setiap pembacaan lebih dari 2σ di atas (atau di bawah, untuk hal seperti resistansi gas di mana lebih rendah = lebih buruk) sebagai puncak. Hitung ulang garis dasar sekali per pemuatan halaman.

Untuk v1, **berbasis ambang menang di tempat yang sudah terdefinisi** (PM, T, RH). Statistik mengisi untuk resistansi gas dan metrik masa depan tanpa ambang absolut.

**Perlakuan visual pada grafik:**

- Titik puncak ditandai dengan simbol berbeda (mis. cincin merah)
- Arahkan/ketuk puncak untuk melihat: stempel waktu, nilai, ambang atau batas σ mana yang terlampaui
- Jumlah agregat "puncak dalam 24j terakhir" / "puncak dalam 7h terakhir" dimunculkan di statusbar bagian atas

**Penerimaan yang diperlukan:** jika PM2.5 melonjak ke 80 µg/m³ pukul 2 siang kemarin pada node DIY kantor, titik itu jelas ditandai merah pada grafik 24j, dan statusbar menampilkan "Active peaks (24h): 1" dengan klik-tembus ke tampilan daftar.

### 3.3 Laporan — desain ulang umpan

Keadaan saat ini: setiap laporan dirender sebagai kartu dengan thumbnail, lencana kategori, wilayah, pratinjau deskripsi, dan stempel waktu. Mereka memakan banyak ruang vertikal dan dasbor terasa berat.

Sasaran: **umpan padat berupa entri satu baris, yang dapat diperluas saat diklik.** Inspirasi: lini masa Twitter / Mastodon. Setiap baris menampilkan:

- Stempel waktu (relatif — "12m ago", "3h ago", "yesterday")
- Lencana kategori (chip berwarna)
- Wilayah
- Sekitar 80 karakter pertama dari deskripsi

Klik/ketuk memperluas ke detail penuh secara inline (foto, deskripsi penuh, analisis AI, sinkronisasi pin peta). Tutup saat diklik kedua kali.

**Perilaku:**

- Lazy-load foto hanya saat baris diperluas
- Urutkan berdasarkan `submittedAt` desc (sudah demikian)
- Gulir tak terbatas atau "Load more" jika ada >50 laporan
- Chip filter di bagian atas: kategori, tingkat keparahan, 24j terakhir / 7h terakhir / sepanjang waktu

Fungsi `renderReportFeed()` di `dashboard/index.html` (baris 501) adalah satu-satunya titik rendering. Kerjakan ulang di sana.

**Penerimaan yang diperlukan:** umpan memuat 20+ laporan dalam ruang vertikal yang sama dengan 5 kartu hari ini. Mengetuk baris memperluas inline dalam ~150ms dan menggeser peta ke lokasi itu (perilaku saat ini).

### 3.4 Korelasi dua arah antara puncak dan laporan

Kapabilitas yang paling bernilai strategis dari revisi ini.

**Arah A — puncak → laporan:** ketika grafik menampilkan puncak, ambil setiap laporan dalam:
- **Jendela waktu:** ±2 jam dari stempel waktu puncak
- **Radius geografis:** 1km dari lokasi sensor

Tampilkan laporan yang cocok sebagai chip kecil di bawah grafik: "2 nearby reports — [burning waste · 230m away · 35 min before peak] [smoke · 480m · 1h after]". Klik chip untuk melompat ke laporan itu di umpan.

Jika tidak ada laporan yang cocok, munculkan prompt aksi: **"This spike has no citizen report attached. If you're nearby right now, [report what you're seeing →]"** dengan tautan ke survei atau bot WhatsApp.

**Arah B — laporan → sensor:** ketika laporan diperluas di umpan, ambil pembacaan sensor dalam:
- **Jendela waktu:** ±1 jam dari stempel waktu pengiriman laporan
- **Radius geografis:** 1km

Tampilkan sensor yang cocok sebagai chip kecil di dalam laporan yang diperluas: "Nearby sensors: [DIY Node Office — PM2.5 16 µg/m³ at submission time] [OpenAQ Denpasar — PM2.5 22 µg/m³]". Klik untuk membuka tampilan riwayat sensor.

Jika sebuah sensor menunjukkan puncak di sekitar stempel waktu yang sama, munculkan dengan kuat: "**Sensor data corroborates this report** — PM2.5 spiked to 80 µg/m³ at the DIY Node 350m away, 12 minutes before this report was filed."

**Penerimaan yang diperlukan:** ketika peristiwa yang diketahui terjadi (mis. seseorang membakar sampah dekat node kantor), puncak pada grafik menautkan ke laporan warga tentang asap itu, dan sebaliknya. Uji ini dengan satu laporan sintetis yang dikaitkan dengan puncak nyata di data yang ada sebelum menyatakan selesai.

### 3.5 UX dwibahasa

String di dasbor seharusnya melewati lapisan terjemahan (fungsi `t(key)` sederhana yang didukung kamus JSON). Tombol bahasa di statusbar. Default: bahasa Inggris. Tambahkan minimal terjemahan **Bahasa Indonesia** untuk string yang menghadap publik (judul grafik, peringatan puncak, prompt aksi, lencana kategori, label statusbar).

Jangan terjemahkan label teknis (nama model sensor, "PM2.5", "kPa", "µg/m³" — semuanya tetap bahasa Inggris tanpa memandang lokal).

Ini adalah hal yang baik untuk dimiliki di v1, bukan penghambat. Jika waktu mepet, susun infrastruktur `t(key)` dengan string berbahasa Inggris saja dan dokumentasikan berkas kamus agar penerjemah mengisinya nanti.

## 4. Pentahapan yang disarankan

**Fase 1 — Infrastruktur deret waktu.** ~1 minggu.
- Helper `fetchSmartCitizenHistory` di data.js
- Lapisan caching `localStorage`
- Rendering grafik di panel Selected (24j + 7h per metrik)
- Status pemuatan dan kosong

**Fase 2 — Deteksi puncak.** ~3 hari.
- Tabel `THRESHOLDS` + komputasi garis dasar statistik
- Markup visual pada grafik
- Penghitung puncak di statusbar

**Fase 3 — Desain ulang umpan laporan.** ~2 hari.
- Tata letak baris padat
- Interaksi perluas-di-tempat
- Chip filter

**Fase 4 — Mesin korelasi.** ~1 minggu.
- Pencarian terdekat puncak → laporan
- Pencarian terdekat laporan → sensor
- Prompt "Report this peak"
- Pemunculan "Sensor data corroborates"

**Fase 5 — Pemolesan + dwibahasa.** ~3 hari.
- Lapisan terjemahan `t()`
- String Bahasa Indonesia
- Pemeriksaan QA seluler

Total: ~3 minggu kerja terfokus. Fase 1 dan 2 dapat dirilis secara independen dan merupakan titik awal yang paling berdaya ungkit.

## 5. Kriteria penerimaan — daftar periksa "selesai"

Revisi selesai ketika, pada dasbor langsung:

- [ ] Mengeklik perangkat Smart Citizen mana pun di peta menampilkan grafik deret waktu (24j + 7h) untuk semua sensor yang terpasang
- [ ] Setidaknya satu puncak PM2.5 terlihat disorot pada grafik dengan ambang WHO ditampilkan dalam keadaan arahan kursor
- [ ] Bagian laporan adalah umpan yang mudah dipindai di mana 20+ laporan muat dalam satu layar
- [ ] Laporan yang diperluas menampilkan sensor terdekat dan pembacaannya pada saat pengiriman
- [ ] Grafik dengan puncak menampilkan laporan terdekat (jika ada) atau prompt aksi untuk melapor (jika tidak ada)
- [ ] Statusbar menampilkan jumlah "Active peaks · 24h" dan "Active peaks · 7d"
- [ ] Di seluler (lebar 375px), dasbor tetap dapat digunakan — grafik dapat digulir horizontal jika perlu, tanpa gulir halaman horizontal
- [ ] Situs masih dimuat dalam <3 detik pada koneksi 3G yang disimulasikan (saat ini lolos; jangan membuat regresi)
- [ ] Tidak ada dependensi baru selain yang sudah dimuat (Chart.js, Leaflet, leaflet-heat); jangan tambahkan apa pun tanpa justifikasi

## 6. Bukan tujuan — apa yang TIDAK dilakukan dalam revisi ini

- **Jangan memperkenalkan kerangka kerja.** Tanpa React, Vue, Svelte, Next, Astro. Arsitektur HTML-statis-dengan-vanilla-JS bersifat disengaja — kampanye dapat direplikasi ke chapter Fab City lain via `git clone`, tanpa langkah build. Pertahankan properti itu.
- **Jangan menambahkan backend.** Cloudflare Workers hanya untuk proksi CORS. Tanpa server Node.js, tanpa server basis data di sisi server. Semua pemrosesan terjadi di peramban atau di platform SC.
- **Jangan mengubah komponen laporan (Python/Flask).** Revisi ini hanya front-end. Komponen laporan (bot WhatsApp + dasbor operator) adalah basis kode terpisah yang hanya menghasilkan JSON yang dikonsumsi dasbor. Hubungan baca-saja.
- **Jangan menulis ulang kode yang berfungsi demi alasan gaya.** Kode saat ini fungsional dan mudah dibaca. Lakukan refactor hanya ketika menambahkan kapabilitas baru mengharuskannya.
- **Jangan kehilangan pembingkaian metodologi.** README dan hero dasbor secara eksplisit memosisikan ini sebagai keturunan *Making Sense* — instrumen partisipatif, bukan sekadar penampil data. Jangan menghilangkan suara itu.
- **Jangan menambahkan login, autentikasi, atau keadaan per-pengguna.** Dasbor bersifat baca-publik untuk semua orang. Fitur operator tetap berada di komponen laporan.

## 7. Dependensi dan hal yang belum pasti

- **Batas laju `/v0/devices/{id}/readings` Smart Citizen** — tak terdokumentasi. Uji dengan beban realistis (10 perangkat × 7 hari × 6 sensor = 420 kueri riwayat pada pemuatan halaman pertama terlalu banyak). Cache localStorage harus sudah ada sebelum diluncurkan untuk menghindari mencapai batas dan diblokir.
- **Sintaks parameter `rollup` Smart Citizen** — verifikasi terhadap dokumen di https://developer.smartcitizen.me. Jika tidak seperti yang diasumsikan ringkasan ini, sesuaikan.
- **Stabilitas API laporan** — pola JSON statis (`data/reports/index.json` + berkas per-laporan) adalah yang dikonsumsi `fetchReports()`. Ini dimiliki oleh komponen laporan; koordinasikan dengan pengelolanya sebelum mengandalkan kolom baru.
- **Belum ada entri katalog BME680** — platform SC tidak memiliki entri Bosch BME680. Saat ini kami memublikasikan ke ID BMP280/SHT31/PMS5003 (lihat [hardware/diy-node/README.md](../hardware/diy-node/README.md)). Oscar (tim SC) mungkin menambahkan entri BME680 yang tepat di sisi server suatu saat. Bagaimanapun dasbor membaca ID sensor apa pun yang terpasang pada perangkat — tidak diperlukan kopling yang dikodekan secara keras.
- **Belum ada blueprint kit untuk perangkat DIY** — memengaruhi keterlihatan endpoint peta dunia SC. Daftar pengaman `KNOWN_BALI_SCK_IDS` dasbor (baris 42 data.js) adalah solusi sementaranya. Saat node DIY baru terpasang, tambahkan ID-nya di sana hingga Oscar memasang blueprint.

## 8. Cara memulai

1. Buat cabang kerja: `git checkout -b dashboard-v2`
2. Baca [`dashboard/index.html`](../dashboard/index.html) dan [`data.js`](../data.js) dari awal hingga akhir. Keduanya tidak besar; satu jam untuk menginternalisasi struktur saat ini akan terbayar di seluruh revisi.
3. Pindai rendering laporan yang ada (`renderReportFeed()` baris 501 di `dashboard/index.html`) — itulah kode yang paling banyak disentuh dalam revisi ini.
4. Mulai dengan Fase 1 (deret waktu). Buat satu grafik terender untuk node DIY kantor (perangkat 19651) sebelum menggeneralisasi.
5. PR ke `main`. GitHub Pages mengambil perubahan secara otomatis.

## 9. Ketika ini selesai

Perbarui ringkasan ini dengan header "Status: complete" dan ringkasan satu paragraf tentang apa yang telah dihasilkan. Jika ada hal dalam ringkasan ini yang ternyata salah (sebuah API tidak berperilaku seperti yang diharapkan, sebuah bukan-tujuan perlu ditinjau ulang), dokumentasikan di sini agar peninjau berikutnya belajar darinya. `REPLICATION.md` kampanye akan merujuk dasbor v2 sebagai versi yang difork chapter Fab City lainnya — akurasi itu penting.

## 10. Kontak

- Penanggung jawab kampanye: Tomas Diez · `tomas@fab.city`
- Penanggung jawab komponen laporan: Tim Fab Lab Bali · `fablabbali@gmail.com`
- Kontak platform Smart Citizen: Oscar (tim platform SC)

---

**Lampiran — referensi cepat untuk ID sensor yang digunakan saat ini (penempatan Bali)**

| ID Perangkat | Tipe | Catatan |
|---|---|---|
| 19236 | SCK 2.1 | Node rumah — penempatan kampanye pertama |
| 19600 | SCK 2.1 | Node kantor — penempatan kampanye kedua |
| 19618 | SCK 2.1 | Penambahan lebih awal; lihat README untuk konteks |
| **19651** | **DIY Plus (XIAO + BME680 + HM3301)** | **Node pertama yang dibangun di lokakarya DIY — kantor Tomas, Mei 2026** |

Node lokakarya DIY mendatang akan muncul di sini saat dipasang. Polanya sama: daftarkan via `hardware/diy-node/tools/register_device.py`, tambahkan ID ke `KNOWN_BALI_SCK_IDS` di data.js, flash firmware dengan ID sensor dari `hardware/diy-node/tools/find_sensor_ids.py`.
