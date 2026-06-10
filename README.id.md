[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Making Sense Bali

**Kampanye penginderaan lingkungan yang dipimpin komunitas untuk Bali, berlandaskan Fab Lab Bali, di dalam chapter Fab City Bali.**

Making Sense Bali memadukan sensor lingkungan perangkat keras terbuka, data publik dari jaringan regional dan global, serta laporan warga tentang isu lingkungan yang teramati secara lokal — pembakaran sampah, peristiwa kualitas udara, kebocoran air, puing konstruksi, kebisingan, hal-hal yang menjadi perhatian orang-orang yang benar-benar tinggal di sini. Pekerjaan ini dilakukan di Indonesia, oleh orang-orang di Indonesia, atas keprihatinan yang diidentifikasi oleh orang-orang di Indonesia.

Kampanye ini diselenggarakan dan bertanggung jawab kepada **[Fab Lab Bali](https://fablabbali.com)**, laboratorium fabrikasi lokal di Denpasar, sebagai bagian dari chapter **Fab City Bali** dalam jaringan global [Fab City](https://fab.city/). Secara metodologis, pekerjaan ini berasal dari proyek **[Making Sense](https://making-sense.eu/)** (EU Horizon 2020, Fab Lab Barcelona / IAAC dan mitra, 2015–2017) serta menggunakan platform **[Smart Citizen Kit](https://smartcitizen.me/)**, yang ikut didirikan oleh Tomas Diez dan Alex Posada di Fab Lab Barcelona / IAAC pada tahun 2012. Making Sense Bali dipimpin oleh Tomas Diez — salah satu pendiri Smart Citizen, kini berdomisili di Bali — dan berjalan sebagai instance bioregional independen, dalam hubungan erat dengan proyek-proyek aslinya.

Live: **[mdg-bali.github.io/makingsensebali](https://mdg-bali.github.io/makingsensebali/)**

---

## Seperti apa wujud Making Sense Bali

Tiga permukaan, satu kampanye:

1. **Situs publik** di `mdg-bali.github.io/makingsensebali/` — beranda kampanye: metodologi, status, dashboard live, survei matters-of-concern, laporan warga, atribusi kepada jaringan yang lebih luas.

2. **Dashboard live** di `/dashboard/` — pembacaan sensor lingkungan secara real-time yang diagregasi dari berbagai jaringan terbuka: penyebaran Smart Citizen Kit yang dioperasikan oleh kampanye, stasiun OpenAQ di Bali, perangkat Sensor.Community, PurpleAir (saat dikonfigurasi). PM2.5, PM10, suhu, kelembapan, kebisingan. Setiap pin menampilkan sumber, pembacaan terakhir, dan tautan ke platform aslinya.

3. **Lapisan laporan** — warga mengirimkan observasi lingkungan ke bot WhatsApp ("Making Sense Bali" dalam penyebaran di Bali). Setiap laporan ditinjau oleh operator lokal sebelum dipublikasikan. Laporan yang disetujui muncul di situs publik sebagai data bersumber komunitas berdampingan dengan pembacaan sensor. Nomor telepon tidak pernah disimpan.

---

## Metodologinya

Making Sense Bali mengikuti pendekatan bertahap yang diturunkan dari Making Sense, diadaptasi untuk Bali:

**Fase 1 — Matters of concern.** Sebuah survei, yang saat ini di-host di Airtable, menanyakan kepada warga isu lingkungan apa yang memengaruhi kehidupan sehari-hari mereka. Hasilnya bukan daftar peringkat "masalah yang harus dipecahkan" — melainkan peta perhatian. Di mana orang menyadari adanya pembakaran sampah? Di mana kebisingan tak tertahankan? Di mana air terasa tidak enak? Survei ini menegaskan bahwa kampanye merespons keprihatinan yang ditentukan komunitas, bukan memaksakan agenda dari luar.

**Fase 2 — Penginderaan dan pelaporan.** Dua kanal berjalan paralel. Sensor perangkat keras terbuka (Smart Citizen Kits) dipasang di lokasi-lokasi strategis — saat ini node rumah dan node kantor yang dioperasikan kampanye, dengan kapasitas untuk meluas ke sekolah dan lokasi komunitas. Secara paralel, bot laporan mengumpulkan observasi kualitatif warga: foto, lokasi, deskripsi isu yang tak bisa dilihat sensor. Kumpulan data gabungan dipublikasikan secara terbuka.

**Fase 3 — Respons dan pembelajaran.** Inilah fase yang sedang dibangun jaringan ini. Data teragregasi dan pola laporan menginformasikan aksi lokal — dari kesadaran individu (rumah Anda berada di koridor asap) hingga pengorganisasian komunitas (pembakaran sampah ini adalah peristiwa berulang dengan sumber yang diketahui) hingga advokasi kebijakan (pemerintah daerah memiliki data yang dapat ditindaklanjuti). Pembelajaran terfederasi lintas-bioregion adalah horizon jangka panjang.

---

## Komponen

Making Sense Bali dirakit dari bagian-bagian berikut. Masing-masing memiliki cakupan dan kisah penyebarannya sendiri:

| Komponen | Apa fungsinya | Di mana letaknya |
|---|---|---|
| **Situs kampanye** | Halaman arahan publik, metodologi, dashboard sensor, laporan, atribusi | Repo ini · GitHub Pages |
| **Lapisan data sensor** | Mengagregasi Smart Citizen Kit + OpenAQ + Sensor.Community via Cloudflare Workers | Repo ini · [`data.js`](data.js), [`worker/`](worker/) |
| **Smart Citizen Kits** | Sensor kualitas udara + kebisingan + iklim perangkat keras terbuka yang dipasang di Bali | [smartcitizen.me](https://smartcitizen.me/) — node rumah 19236, node kantor 19600 |
| **Node DIY workshop** | Sensor hasil rakitan workshop dalam dua tingkat — Basic (XIAO + BME680, ~USD 15–25, AQ dalam ruangan + iklim + VOC) dan Plus (Basic + HM3301, ~USD 35–60, menambah PM luar ruangan). Lapisan kepadatan spasial yang terjangkau untuk banjar, sekolah, warung. | [`hardware/diy-node/`](hardware/diy-node/) |
| **Survei matters-of-concern** | Masukan komunitas Fase 1 tentang keprihatinan lingkungan | Airtable (backend proprietary, formulir publik) |
| **Komponen laporan** | Bot WhatsApp + dashboard operator untuk laporan warga | [`reports/`](reports/) — toolkit Sense Making |
| **Identitas Murmurations** | Profil organisasi terfederasi, dapat ditemukan di seluruh jaringan data komunitas | [`murmurations.json`](murmurations.json) di repo ini |

---

## Perangkat keras — dengan apa kita melakukan penginderaan

Kampanye ini tidak terikat pada satu model sensor saja. Ini adalah jaringan berjenjang dengan instrumen rujukan, Smart Citizen Kit siap pakai, dan node DIY hasil rakitan workshop yang memasok dashboard yang sama dengan flag fidelitas yang sesuai. Setiap tingkat yang lebih rendah dikalibrasi terhadap tingkat di atasnya; koreksi berada di lapisan pemrosesan dashboard, bukan di firmware.

| Tingkat | Perangkat keras | Biaya | Peran |
|---|---|---|---|
| **0 — Rujukan** | BAM-1020, Aeroqual AQM 65, atau stasiun BMKG / Udayana yang di-host | USD 5.000–25.000+ | Kebenaran lapangan (ground truth). Kelas regulasi. Jangkar kalibrasi untuk semua yang di bawahnya. Dikejar melalui kemitraan dengan **BMKG Stasiun Klimatologi Bali** (Sanglah) atau **Universitas Udayana**. |
| **1 — Smart Citizen Kit 2.3** | SCK resmi dari [smartcitizen.me](https://smartcitizen.me/store) | ~USD 150 | Tulang punggung multi-parameter terpercaya — PM, eCO₂, kebisingan, iklim, cahaya. Firmware yang telah teruji. Node-node kampanye yang saat ini terpasang (rumah 19236, kantor 19600). |
| **2 — DIY Plus** | XIAO ESP32-S3 + BME680 + HM3301 | ~USD 35–60 | Kepadatan spasial luar ruangan. PM + iklim + gas/VOC. Dapat dirakit di workshop di Fab Lab Bali. |
| **3 — DIY Basic** | XIAO ESP32-S3 + BME680 | ~USD 15–25 | Jangkauan maksimum — AQ dalam ruangan, jamur/dengue/panas/VOC. Kit yang paling mudah diakses. |

Dengan uang yang sama untuk 10 SCK resmi, kampanye dapat mengirimkan ~75–100 node yang memadukan berbagai tingkat — memberikan kredibilitas rujukan (Tingkat 0/1) sekaligus resolusi spasial yang memungkinkan dashboard menyatakan *lingkungan mana* yang membakar sampah pada Rabu malam, bukan sekadar "Bali selatan mengalami PM yang meningkat."

Dokumentasi perangkat keras lengkap — BOM, skema, firmware, rantai kalibrasi, dan kasus penggunaan khas Bali (habitat nyamuk dengue, jamur dan kesehatan pernapasan, stres panas, paparan VOC dalam ruangan, polusi udara luar ruangan, triangulasi peristiwa pembakaran) — ada di [`hardware/diy-node/README.md`](hardware/diy-node/).

---

## Garis keturunan dan tata kelola

Making Sense Bali berada dalam garis keturunan yang spesifik. Hal ini penting karena membentuk siapa yang bertanggung jawab, asumsi apa yang dibawa kampanye, dan jaringan mana yang difederasikan.

- **2012–sekarang** — Smart Citizen, yang ikut didirikan oleh **Tomas Diez** dan **Alex Posada** di Fab Lab Barcelona / IAAC. Platform sensor perangkat keras terbuka yang digunakan kampanye ini.
- **2015–2017** — Making Sense (EU Horizon 2020), Fab Lab Barcelona / IAAC dan mitra (Waag, JKU Linz, University of Dundee). Kerangka partisipatif yang kami terapkan.
- **2026–sekarang** — Making Sense Bali. Dipimpin oleh Tomas Diez (salah satu pendiri Smart Citizen, kini berdomisili di Bali), dengan Fab Lab Bali sebagai tuan rumah institusional dan Fab City Bali sebagai konteks chapter.

Platform Smart Citizen asli dan Fab Lab Barcelona kini dikelola oleh tim lain; Making Sense Bali bersifat independen tetapi terkoordinasi, bukan satelit atau waralaba. Kedua proyek tetap berlanjut, di bioregion yang berbeda, di bawah tim yang berbeda, dengan metodologi yang tumpang tindih dan estetika bersama berupa perangkat keras terbuka, data terbuka, dan akuntabilitas komunitas.

Catatan penamaan, karena kata-katanya tumpang tindih: **jaringan** kampanye yang dapat direplikasi menggunakan konvensi **Making Sense [tempat]** — Making Sense Bali, Making Sense Barcelona, dan seterusnya. Kampanye kontemporer ini membawa metodologi EU Making Sense ke bioregion baru; kampanye ini *bukan* proyek EU 2015–2017 itu sendiri, yang tetap menjadi asal-usul yang dikreditkan (selalu dikutip beserta tanggalnya). Sensornya, pada gilirannya, adalah **Smart Citizen Kits** — perangkat keras terbuka — yang merupakan hal terpisah lagi.

Struktur akuntabilitas Making Sense Bali:

- **Institusi tuan rumah**: Fab Lab Bali
- **Konteks chapter**: Fab City Bali
- **Keanggotaan jaringan**: jaringan global [Fab City](https://fab.city/) · [Fab Lab Network](https://fablabs.io/)
- **Kontak**: (mailto:fablabbali@gmail.com)

---

## Status

Kampanye saat ini berada pada awal transisi Fase 1 → Fase 2 (Q2 2026):

- Survei Fase 1 sudah live dan mengumpulkan tanggapan
- Dashboard sensor beroperasi dengan dua node SCK kampanye dan agregasi live dari OpenAQ, Sensor.Community
- Jalur perangkat keras node DIY terdokumentasi dan dipublikasikan — varian Basic (XIAO + BME680) dan Plus (menambah HM3301) siap untuk workshop pertama di Fab Lab Bali, menunggu jalur rujukan Tingkat 0
- Komponen laporan (Sense Making) dalam tahap pilot — bot berjalan di infrastruktur Fab Lab Bali, dibatasi allowlist untuk penguji awal, gerbang persetujuan sudah aktif
- Laporan publik mengalir ke situs kampanye setelah ditinjau operator

---

## Replikasikan — Making Sense [tempat Anda]

Making Sense Bali sengaja dibuat agar dapat direplikasi. Chapter Fab City lain yang memiliki Fab Lab tuan rumah dapat mem-fork template kampanye ini untuk bioregion mereka.

**Yang Anda butuhkan:**

- Sebuah **chapter Fab City** untuk kota atau bioregion Anda ([fab.city/network](https://fab.city/))
- Sebuah **Fab Lab tuan rumah** yang bersedia menjadi jangkar institusional dan pihak yang bertanggung jawab
- **Kehadiran sensor tertentu** — minimal satu Smart Citizen Kit (atau beberapa node DIY workshop — lihat [`hardware/diy-node/`](hardware/diy-node/) untuk jalur murahnya), ditambah opsi untuk menampilkan data OpenAQ / Sensor.Community / PurpleAir yang sudah ada di wilayah Anda
- **Kapasitas teknis yang sederhana** — seseorang yang dapat menjalankan NAS, Cloudflare Worker, dan menyebarkan bot laporan (tidak perlu pengembangan perangkat lunak, tetapi perlu kenyamanan operasional)
- **Adaptasi bahasa lokal** — menerjemahkan situs kampanye dan teks bot laporan

Panduan replikasi lengkap ada di **[REPLICATION.md](REPLICATION.md)**.

Saat ini dalam pembicaraan: **Making Sense Barcelona** (Fab Lab Barcelona, semester kedua 2026). Chapter Fab City lain yang sedang didekati meliputi Yucatán, Montreal, Goa, dan Santiago. Setiap Making Sense [tempat] adalah kampanyenya sendiri, di-host oleh Fab Lab-nya sendiri, berlandaskan bioregionnya sendiri, berbagi metodologi dan memfederasikan data yang dapat ditemukan — itulah jaringan yang sedang dibangun proyek ini, satu chapter pada satu waktu.

---

## Struktur repositori

Semuanya berada dalam satu repo sehingga sebuah Fab Lab yang mem-fork Making Sense [tempat mereka]
mendapatkan keseluruhan stack dengan satu kali `git clone`.

```
.
├── README.md              this file — campaign overview
├── REPLICATION.md         how to stand up Making Sense [your place]
├── docs/
│   ├── methodology.md     Making Sense, adapted for bioregional deployment
│   ├── phase-1-survey.md  running the matters-of-concern survey
│   ├── sensors.md         deploying SCK + integrating OpenAQ / Sensor.Community
│   ├── reports.md         operating the reports component
│   ├── web-presence.md    customizing the campaign site
│   └── federation.md      Murmurations identity, future PLANETAI
│
├── index.html             campaign home page
├── data.js                sensor data aggregator (SCK + OpenAQ + Sensor.Community)
├── dashboard/             live sensor dashboard
│   └── index.html
├── worker/                Cloudflare Worker proxies (OpenAQ, SCK)
│   └── openaq-proxy.js
├── murmurations.json      federated organization profile
│
└── reports/               Sense Making · the reports component
    ├── README.md          toolkit overview
    ├── bot_murmurations.py
    ├── dashboard.py
    ├── docker-compose.yml
    └── ...                see reports/README.md for the full layout
```

---

## Lisensi

Kode: MIT.
Dokumentasi, metodologi, skema, survei: CC-BY-SA 4.0.

Pola lisensi yang sama seperti Making Sense dan Smart Citizen Kit. Fork-lah,
adaptasikan untuk bioregion Anda, bagikan kembali apa yang Anda bangun — itulah intinya.

---

Diselenggarakan oleh [Fab Lab Bali](https://fablabbali.com) · Bagian dari [Fab City Bali](https://fab.city/) · Anggota jaringan [Fab City](https://fab.city/) dan [Fab Lab Network](https://fablabs.io/).
