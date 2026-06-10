[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Sense Making

**Komponen laporan dari [Making Sense Bali](../README.md) — perangkat pelaporan warga berbasis WhatsApp untuk node Fab City dan kampanye bioregional.**

> Folder ini adalah salah satu komponen dari kampanye Making Sense Bali. Untuk
> konteks kampanye selengkapnya — metodologi, sensor, kehadiran web, survei —
> lihat [README repo induk](../README.md). Berikut ini adalah
> referensi teknis khusus untuk komponen laporan.

Sense Making adalah komponen pelaporan dari sebuah kampanye penginderaan warga.
Warga mendeskripsikan masalah lingkungan dan perkotaan setempat — sampah, kebocoran air,
puing konstruksi, polusi kendaraan, pembakaran sampah, kebisingan — melalui antarmuka
yang familier (WhatsApp), dalam bahasa mereka sendiri. Seorang operator lokal
meninjau setiap laporan sebelum dipublikasikan. Laporan yang disetujui menjadi publik di
situs kampanye dan, ketika ada node terfederasi, dapat ditemukan lintas
bioregion melalui protokol Murmurations.

Perangkat ini sengaja dibuat kecil, berdaulat, dan dapat direplikasi. Perangkat ini berjalan di
infrastruktur kelas rumahan (sebuah NAS dan sebuah laptop), tidak menggunakan SaaS di jalur
kritis, tidak ada biaya API per pesan, dan dapat di-fork oleh Fab Lab lain dalam
satu sore. Antarmuka pelaporan secara default dwibahasa dan dikonfigurasi
per lokalitas.

Karya ini berakar dari proyek [Making Sense](https://making-sense.eu/)
(EU Horizon 2020, Fab Lab Barcelona / IAAC dan mitra, 2015–2017) — kerangka kerja
kanonik partisipatif untuk penginderaan lingkungan oleh warga. Sense
Making mengambil metodologi Making Sense dan mengemasnya sebagai kit terdistribusi
yang dapat di-deploy di rumah untuk lanskap Fab City 2026.

---

## Status

| | |
|---|---|
| **Deployment referensi** | Making Sense Bali · Bali, Indonesia · fase pilot, Q2 2026 |
| **Dijalankan oleh** | [Fab Lab Bali](https://fablabbali.com) sebagai lapisan pelaporan dari [Making Sense Bali](https://mdg-bali.github.io/makingsensebali/) |
| **Kit replikasi** | Tersedia — lihat [REPLICATION.md](REPLICATION.md) |
| **Rencana berikutnya** | Pelapor Barcelona · Fab Lab Barcelona · 2026 H2 |
| **Lapisan federasi** | PLANETAI · direncanakan, infrastruktur belum dibangun |

---

## Apa yang dialami warga

Sebuah percakapan WhatsApp. Bot membuka dengan komitmen privasi, lalu
menjelaskan alur tiga langkah:

```
Resident → halo

Bot     ← 🌴 Making Sense Bali
          🔒 Privacy is our top priority.
          Your phone number is NEVER STORED on our servers.

          This bot is run by Fab Lab Bali so residents can report
          environmental and community issues in your area — trash on
          streets, water leaks, smoke from burning, construction
          dust, vehicle pollution.

          How to report (3 steps):
          1️⃣ Write a description of the issue
          2️⃣ Share your location 📍
          3️⃣ Send a photo (optional)

          Reply AGREE to continue.
          Reply /optout anytime to leave.

Resident → SETUJU
Bot     ← ✅ Thanks! You can now report issues.

Resident → sampah berserakan di pantai bingin
Bot     ← 📝 Description received.
          Step 2/3: Share your location 📍

Resident → [shares location pin]
Bot     ← ✅ Location saved — your report is complete.
          Step 3/3 (optional): Send a photo 📸
```

Semua teks bot dwibahasa (bahasa lokal + bahasa Inggris dengan huruf miring di bawahnya). Bahasa
per node dikonfigurasi dengan menyunting satu file (`messages.py`); lokalitas
per node (lingkungan, bounding box) dikonfigurasi di `config.json` dan
tabel lokalitas adaptor.

---

## Apa yang dilihat operator

Sebuah dasbor web di jaringan lokal dengan tujuh tab:

- **Status** — kesehatan sistem (bot, pemasangan WhatsApp, antrean vision), jumlah laporan hari ini
- **Pending review** — laporan masuk yang menunggu persetujuan, dengan setujui/tolak sekali klik
- **Allowlist** — kelola siapa yang dapat berinteraksi dengan bot (nomor telepon dalam format E.164)
- **WhatsApp** — alur pemasangan, pindai QR, status koneksi, tanpa perlu SSH
- **Reports** — daftar laporan lengkap dengan kategori, tingkat keparahan, lokalitas, timestamp
- **Map** — tampilan geografis laporan yang disetujui (Leaflet, otomatis berpusat pada bioregion)
- **Consent** — buku besar persetujuan yang dianonimkan, cabut pengirim mana pun

Dasbor ini adalah satu file Flask dengan template inline, Pico.css untuk
penataan gaya, Leaflet untuk peta, basic auth dari sebuah variabel env. Tanpa langkah build.
Siapa pun yang bisa membaca Python dapat menyesuaikan tampilan atau perilakunya.

---

## Cara kerjanya

```
                      WhatsApp
                          │
                          ▼
┌─────────────────────────────────────────────┐    M1 / inference host
│ Always-on host (Synology NAS / VPS)         │    ┌──────────────────────┐
│ ┌─────────────────────────────────────────┐ │    │ MLX vision server    │
│ │ Evolution API · WhatsApp transport      │ │    │  Phi-3.5-Vision      │
│ ├─────────────────────────────────────────┤ │    │                      │
│ │ Sense Making bot · webhook → save       │─┼───▶│ Worker · pulls queue │
│ │   allowlist · consent · vision queue    │ │    │   updates report     │
│ ├─────────────────────────────────────────┤ │    └──────────────────────┘
│ │ Operator dashboard · approval UI        │ │
│ ├─────────────────────────────────────────┤ │    public:
│ │ Postgres + Redis (Evolution backing)    │ │    ┌──────────────────────┐
│ └─────────────────────────────────────────┘ │    │ campaign GitHub Pages│
│   reports/    canonical (with PII)          │    │  (approved only,     │
│   profiles/   approved + sanitized          │───▶│   sanitized)         │
└─────────────────────────────────────────────┘    └──────────────────────┘
                                                   future: PLANETAI federation
```

Lima kontainer Docker berjalan di always-on host. Inferensi vision berada di
mesin Apple Silicon terpisah sehingga always-on host tidak pernah memerlukan GPU —
bot mengantrekan pekerjaan vision, worker di Mac mengambilnya saat online.
Jika Mac dalam keadaan tidur, foto menumpuk di antrean dan diproses saat ia bangun.
Bot tidak pernah memblokir karena inferensi.

Mengapa bentuk ini: kedaulatan itu penting. Seluruh stack berjalan di infrastruktur
yang dimiliki oleh sebuah rumah tangga. Tidak ada API proprietary di jalurnya, tidak ada tagihan SaaS bulanan, tidak ada
vendor yang dapat men-deplatform kampanye ini. Bagi sebuah node Fab City, itu bukan
sekadar kebetulan — itulah intinya.

Untuk detail arsitektur, lihat [ARCHITECTURE.md](ARCHITECTURE.md).
Untuk deployment, lihat [DEPLOY.md](DEPLOY.md).

---

## Privasi

Tiga komitmen, ditegakkan oleh kode:

1. **Nomor telepon tidak pernah disimpan** dalam laporan atau profil publik.
   Bot hanya menyimpan hash SHA-256 satu arah untuk pelacakan persetujuan.
2. **Laporan disanitasi sebelum federasi.** Adaptor Murmurations
   menghapus semua PII (hash pengirim, path gambar lokal, kunci media) dari
   profil yang dipublikasikan ke situs publik.
3. **Tidak ada yang meninggalkan infrastruktur lokal tanpa persetujuan operator
   yang eksplisit.** Gerbang persetujuan di dasbor adalah batas
   publikasi. Laporan yang belum ditinjau tetap di NAS dan tidak pernah difederasi.

Alur persetujuan bersifat opt-in melalui balasan (`SETUJU` / `AGREE`), opt-out adalah satu
perintah (`/optout`), dan operator dapat mencabut persetujuan pengirim individual
mana pun melalui dasbor.

---

## Replikasi

Jika Anda menjalankan node Fab City, sebuah Fab Lab, atau kampanye penginderaan komunitas dan
Anda ingin deployment Anda sendiri, baca **[REPLICATION.md](REPLICATION.md)**.

Anda akan memerlukan:

- Sebuah always-on host dengan Docker (disarankan: Synology DS725+ NAS, ~$300, tetapi
  perangkat Linux apa pun dengan Docker juga bisa)
- Sebuah Mac Apple Silicon cadangan untuk inferensi vision (atau ganti dengan Claude Haiku
  vision API seharga ~$5/bulan)
- Sebuah nomor WhatsApp yang didedikasikan untuk bot (nomor pribadi bisa digunakan untuk
  fase pilot, nomor bisnis khusus disarankan untuk produksi)
- 4–6 jam waktu satu operator untuk menjalankannya dari ujung ke ujung
- Kenyamanan dengan terminal untuk pengaturan awal; operasi sehari-hari ada di
  dasbor

Biaya berulang pada infrastruktur rumahan: **~$10–20/bulan** (listrik,
perpanjangan domain, fallback vision-API opsional).

---

## Garis keturunan

| | |
|---|---|
| 2015–2017 | [Making Sense](https://making-sense.eu/) — kerangka kerja penginderaan warga EU Horizon 2020, dipimpin oleh Fab Lab Barcelona / IAAC dan mitra |
| 2013–sekarang | [Smart Citizen Kit](https://smartcitizen.me/) — platform sensor lingkungan open-hardware dari Fab Lab Barcelona |
| 2025–sekarang | Making Sense Bali — kampanye oleh Fab Lab Bali, kampanye induk untuk deployment Sense Making pertama |
| 2026–sekarang | Sense Making — kit pelaporan yang difaktorkan keluar untuk replikasi bioregional |

---

## Struktur repository

```
.
├── bot_murmurations.py       Flask bot — WhatsApp webhook, allowlist, consent
├── dashboard.py              Flask dashboard — approval UI, ops controls
├── murmurations_adapter.py   Federated profile generator (PII-sanitized)
├── vision_analyzer.py        Vision client (MLX / Ollama / Haiku / mock)
├── mlx_vision_server.py      MLX FastAPI server (runs on the Mac)
├── m1_vision_worker.py       Vision queue consumer
├── messages.py               All bilingual bot copy — translate for replication
├── docker-compose.yml        Five-container stack for the always-on host
├── Dockerfile                Shared image for bot + dashboard
├── schemas/
│   └── environmental_observation-v1.0.0.json   Murmurations schema
├── sync_profiles.sh          Push approved profiles to public sites
├── DEPLOY.md                 Detailed deployment steps
├── REPLICATION.md            Forking guide for new bioregions
├── ARCHITECTURE.md           Design decisions
└── OPERATIONS.md             Day-to-day operator playbook
```

---

## Lisensi

Kode: MIT.
Dokumentasi, skema, pesan: CC-BY-SA 4.0.

Keduanya mencerminkan pendekatan Making Sense dan Smart Citizen — cukup terbuka untuk di-fork
secara bebas, share-alike untuk apa yang didistribusikan secara publik.

---

Dibangun oleh [Fab Lab Bali](https://fablabbali.com), untuk jaringan
[Fab City](https://fab.city/).
