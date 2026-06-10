[English](REPLICATION.md) · **Bahasa Indonesia** · [Español](REPLICATION.es.md)

# Mereplikasi Making Sense [tempat Anda]

Panduan untuk **chapter Fab City yang memiliki Fab Lab tuan rumah** yang ingin mendirikan instance bioregional Making Sense versi mereka sendiri — memadukan sensor perangkat keras terbuka, jaringan data publik, laporan warga, dan survei partisipatif dalam satu kampanye.

Penyebaran rujukannya adalah [Making Sense Bali](README.md), yang di-host oleh Fab Lab Bali di dalam chapter Fab City Bali. Dokumen ini adalah kampanye yang sama, dikemas sebagai sebuah kit. Jika Anda menjalankan sebuah chapter Fab City dan memiliki Fab Lab tuan rumah yang bersedia menjangkar pekerjaan ini, Anda dapat mem-fork repositori ini, menyesuaikannya untuk bioregion Anda, dan menyebarkan instance yang berfungsi dalam waktu kira-kira **3–6 bulan dari keputusan hingga peluncuran publik**.

Jika Anda tidak memiliki kombinasi Fab City + Fab Lab — atau tidak menginginkannya — sebagian besar perangkat dasarnya tetap berguna secara mandiri: [Smart Citizen Kit](https://smartcitizen.me/) untuk sensor, OpenAQ / Sensor.Community untuk data terbuka, [toolkit laporan Sense Making](reports/) untuk infrastruktur bot. Anda dapat menggunakan salah satunya tanpa menjalankan kampanye "Making Sense [tempat]". Nama kampanye dan jaringan terfederasi yang diikutinya disediakan khusus untuk instance chapter Fab City, demi alasan akuntabilitas dan tata kelola yang dijelaskan di bawah.

---

## 1. Apakah ini untuk Anda?

Making Sense [tempat Anda] memerlukan empat komitmen. Jika salah satu dari ini goyah, perbaiki sebelum memulai pekerjaan teknis — pekerjaan teknis adalah paruh yang mudah.

### Jangkar institusional yang diperlukan

- **Sebuah chapter Fab City** untuk bioregion Anda. Chapter adalah rumah politik dan jaringan dari kampanye. Jika kota Anda belum menjadi chapter Fab City, itu adalah percakapan terpisah yang harus dibicarakan dengan [Fab City](https://fab.city/) terlebih dahulu.
- **Sebuah Fab Lab tuan rumah** yang bersedia menjadi jangkar institusional. Fab Lab disebutkan namanya, bertanggung jawab, dan tampak pada kampanye — ini adalah rumah legal, etis, dan operasional. Bukan kelompok komunitas informal atau proyek pribadi.
- **Seorang pemimpin kampanye yang ditunjuk.** Satu orang yang memiliki pekerjaan ini, mengambil keputusan, dan dapat dihubungi secara publik. Bukan komite, bukan peran bergilir. Pemimpin yang ditunjuk inilah yang membuat kampanye dapat dipahami oleh media, pemerintah, dan mitra.

### Kapasitas operasional yang diperlukan

- **Tim teknis kecil atau seorang operator** — tidak harus penuh waktu, tetapi seseorang yang nyaman mengoperasikan Synology NAS (atau kotak Linux setara dengan Docker), menyesuaikan situs web statis, menyebarkan beberapa Smart Citizen Kit, mengelola Airtable. Tidak perlu pengembangan perangkat lunak untuk penyiapan; kenyamanan mengikuti dokumentasi teknis diperlukan.
- **Kapasitas keterlibatan komunitas** — seseorang (sering kali orang yang sama, terkadang organisasi mitra) yang dapat menjalankan survei Fase 1, berbicara dengan warga, mengelola aliran laporan, dan memutuskan apa yang disetujui dan dipublikasikan. Inilah pekerjaan manusiawi yang memberi makna pada data.
- **Perhatian selama beberapa bulan.** Ini bukan proyek akhir pekan. Fase 1 memakan ~6 minggu perancangan dan penjangkauan untuk dilakukan dengan baik. Mendirikan infrastruktur teknis memakan satu atau dua minggu. Menjalankan kampanye bersifat berkelanjutan.

### Apa yang bukan

- Sebuah produk siap pakai. Anda akan membuat keputusan lokal sepanjang jalan — lingkungan mana yang difokuskan, dalam bahasa apa beroperasi, pertanyaan survei apa yang penting untuk bioregion Anda, kategori polusi apa yang mendominasi konteks Anda.
- Sebuah proyek riset. Data ini untuk penggunaan komunitas terlebih dahulu, riset di hilir. Jika tujuan utama Anda adalah publikasi akademis, kit ini terlalu rumit untuk kebutuhan Anda.
- Sebuah kampanye advokasi. Making Sense [tempat Anda] bersifat partisipatif dan membangun bukti. Ia dapat memberi makan advokasi, tetapi kampanye itu sendiri bersifat deskriptif — ia menampilkan apa yang disadari warga, ia tidak menentukan jawaban di awal.
- Sebuah pilot singkat. Jaringan federasi hanya berfungsi jika instance-nya tetap hidup selama bertahun-tahun. Fab Lab yang ikut serta sebaiknya bersiap menjadi tuan rumah kampanye untuk jangka panjang.

---

## 2. Fase-fasenya

Making Sense [tempat Anda] berjalan dalam tiga fase yang tumpang tindih. Fase-fase ini tidak ketat berurutan — Fase 2 dimulai saat Fase 1 masih mengumpulkan tanggapan; Fase 3 dimulai segera setelah Anda memiliki cukup data untuk ditindaklanjuti — tetapi urutan memulainya penting.

### Fase 1 — Matters of concern (minggu 1–8)

Kampanye dimulai dengan menanyakan kepada warga isu lingkungan apa yang memengaruhi kehidupan sehari-hari mereka. Bukan apa yang menurut kita harus mereka pedulikan — melainkan apa yang benar-benar mereka sadari. Inilah landasan partisipatif. Lewati ini dan Anda telah membangun kampanye instrumen, bukan kampanye komunitas.

**Apa yang Anda hasilkan di Fase 1:**

- Sebuah survei yang di-host di Airtable (atau setara) yang menangkap matters of concern, lokasi, frekuensi, tingkat keparahan
- 50–500 tanggapan dari bioregion Anda, tergantung ukuran kota dan penjangkauan
- Ringkasan publik di situs kampanye Anda: "Inilah yang warga sampaikan menjadi keprihatinan mereka"
- Daftar singkat prioritas yang membentuk penempatan sensor Fase 2 dan teks bot laporan

**Keputusan di Fase 1:**

- Bahasa survei — bahasa lokal selalu; bahasa Inggris opsional tergantung audiens
- Kanal penjangkauan — sekolah, organisasi kewilayahan (banjar, juntas vecinales, AC), media sosial, poster, organisasi mitra
- Durasi survei — 3–8 minggu pengumpulan aktif adalah lazim
- Seperti apa "selesai" itu — ambang jumlah tanggapan, jendela waktu, atau keduanya

Anda dapat mem-fork pertanyaan survei Making Sense Bali sebagai titik awal (lihat [docs/phase-1-survey.md](docs/phase-1-survey.md), dan **[formulir survei live Bali](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form)** sebagai rujukan). Survei Bali sendiri masih dalam proses pengerjaan, beriterasi seiring kami belajar pertanyaan mana yang menghasilkan jawaban berguna. Fork pertanyaan yang Anda anggap berguna, adaptasi atau ganti sisanya — matters of concern di bioregion Anda bukanlah milik Bali.

### Fase 2 — Penginderaan dan pelaporan (minggu 4–berkelanjutan)

Sementara tanggapan Fase 1 masuk, Anda mulai lapisan penginderaan dan pelaporan. Dua kanal:

**Kuantitatif — Smart Citizen Kits.** Sebarkan node SCK yang dioperasikan kampanye Anda di lokasi strategis. Mulailah dengan dua atau tiga (node rumah yang dioperasikan kampanye, node kantor, node yang di-host mitra), lalu perluas berdasarkan prioritas Fase 1. Setiap unit berbiaya ~$150, berjalan di WiFi, mempublikasikan secara terbuka ke [smartcitizen.me](https://smartcitizen.me/). Dashboard situs kampanye otomatis menemukan dan menampilkan kit Anda.

**Kualitatif — laporan warga.** Dirikan [komponen laporan](reports/) — bot WhatsApp yang dapat dikirimi pesan oleh warga tentang apa yang mereka lihat. Tumpukan sampah, kebocoran air, asap, puing konstruksi, gas buang kendaraan. Setiap laporan ditinjau oleh operator Anda sebelum dipublikasikan. Laporan yang disetujui muncul di situs kampanye Anda berdampingan dengan data sensor.

Kedua kanal memasok peta yang sama. Sebuah peristiwa pembakaran muncul sebagai pembacaan sensor (lonjakan PM2.5) DAN laporan warga ("asap di ujung selatan pantai sejak pagi"). Bersama-sama keduanya lebih kuat ketimbang masing-masing sendiri.

**Keputusan di Fase 2:**

- Di mana menempatkan SCK (prioritas Fase 1 harus mengarahkan ini)
- Berapa banyak sensor untuk memulai (3–5 cukup masuk akal; bisa tumbuh hingga 20+ seiring waktu)
- Apakah akan mengintegrasikan data OpenAQ / Sensor.Community / PurpleAir — situs sudah melakukan ini untuk bbox Anda
- Jadwal operator bot — siapa yang meninjau laporan setiap hari, siapa yang merespons pesan yang rusak
- Daftar tester pilot — mulai dengan 5–10 warga tepercaya sebelum membukanya lebih luas

### Fase 3 — Respons dan pembelajaran (berkelanjutan, dimulai saat data menumpuk)

Inilah fase yang sedang dibangun jaringan ini dan tempat Making Sense [tempat Anda] membuktikan nilainya. Data saja tidak mengubah apa pun; data yang ditafsirkan oleh sebuah komunitas, dengan jangkar yang ditunjuk, terkadang mengubahnya.

Seperti apa "respons" itu bergantung pada konteks lokal Anda. Pola umum:

- **Lingkar kesadaran** — laporan berulang yang dikembalikan kepada warga yang berpartisipasi, agar mereka tahu masukan mereka digunakan
- **Penampilan pola** — ringkasan bulanan yang mengidentifikasi peristiwa berulang ("pembakaran sampah setiap Rabu di pantai selatan") yang menunjuk pada sumbernya
- **Pengorganisasian komunitas** — aksi lokal yang dipicu oleh bukti teragregasi (berbicara dengan pelaku usaha yang melakukan pembakaran, mengorganisasi pembersihan kolektif)
- **Advokasi kebijakan** — membawa data teragregasi ke pemerintah daerah, banjar / dewan kewilayahan, lembaga lingkungan
- **Pembelajaran terfederasi** — ketika instance Making Sense [tempat] lain ada, berbagi pola lintas bioregion (dinamika koridor asap, isu air terkait musim hujan, dll.)

Fase 3 paling bergantung pada konteks lokal. Kami tidak menentukan cara menjalankannya. Kami memang mensyaratkan Anda berkomitmen menjalankannya — jika tidak, kampanye menjadi pengumpulan data tanpa konsekuensi, yang merusak kepercayaan komunitas.

---

## 3. Komponen — apa yang di-fork, apa yang disebarkan, apa yang dikonfigurasi

Making Sense [tempat Anda] dirakit dari bagian-bagian berikut:

| Komponen | Apa yang Anda lakukan | Upaya |
|---|---|---|
| **Situs kampanye** (`index.html`, CSS, teks) | Fork, sesuaikan teks + lokalitas + aksen visual untuk kota Anda | 1–2 hari penyuntingan cermat |
| **Lapisan data sensor** (`data.js`) | Perbarui bounding box untuk bioregion Anda, daftarkan ID perangkat SCK Anda sendiri | 1–2 jam |
| **Smart Citizen Kits** | Beli, daftarkan di smartcitizen.me, sebarkan di bioregion Anda | Pengadaan ~2 minggu + 1 jam per penyebaran |
| **Node DIY workshop** (opsional) | Bangun node XIAO ESP32-S3 + HM3301 + BME680 berbiaya rendah untuk kepadatan sensor lebih tinggi | Workshop setengah hari per kelompok + pemesanan komponen — lihat [`hardware/diy-node/`](hardware/diy-node/) |
| **Proxy Cloudflare Worker** (`worker/`) | Opsional — hanya jika rate-limit OpenAQ mengganggu Anda | 1–2 jam jika diperlukan |
| **Survei Fase 1** | Rancang pertanyaan untuk konteks Anda, host di Airtable (atau alternatif) | 1 minggu perancangan pertanyaan yang cermat + pengumpulan data berkelanjutan |
| **Komponen laporan** (`reports/`) | Fork, konfigurasikan lokal + bahasa + allowlist, sebarkan di NAS | 1 hari konfigurasi + beberapa jam penyebaran NAS |
| **Identitas Murmurations** (`murmurations.json`) | Sunting nama org, mitra, geolokasi, tag; publikasikan di domain Anda | 1 jam |

Total upaya realistis untuk beranjak dari "kami ingin melakukan ini" menjadi "kami sudah live secara publik dengan sensor + laporan + survei": **6–10 minggu** dengan satu operator yang bekerja paruh waktu, atau 3–4 minggu jika Anda memiliki tim khusus untuk sebuah sprint.

---

## 4. Fork kampanye — langkah demi langkah

Ini adalah langkah-langkah tingkat tinggi. Setiap langkah menautkan ke dokumen rinci jika ada.

### Langkah 1 — Tegakkan jangkar institusional

Sebelum kode atau perangkat keras apa pun:

- Konfirmasikan status chapter Fab City Anda. Jika Anda belum menjadi chapter, bicaralah dengan [Fab City](https://fab.city/) terlebih dahulu.
- Identifikasi dan konfirmasikan Fab Lab tuan rumah Anda. Dapatkan komitmen institusional yang eksplisit, bukan sekadar antusiasme.
- Tunjuk pemimpin kampanye Anda. Catat ini secara tertulis di suatu tempat internal.
- Tetapkan nama kampanye Anda. Konvensi: **Making Sense [Tempat]** — *Making Sense Barcelona*, *Making Sense Yucatán*, *Making Sense Bangalore*. Pertahankan awalan "Making Sense" agar jaringan dapat dikenali. Satu peringatan: ini adalah **jaringan** kampanye kontemporer, berbeda dari proyek riset **Making Sense** EU 2015–2017 yang menjadi asal-usulnya. Selalu kreditkan proyek itu *beserta tanggalnya* dalam garis keturunan Anda agar keduanya tidak rancu — terutama di Barcelona, tempat Fab Lab Barcelona menjalankan pilot EU yang asli.

### Langkah 2 — Fork repositori ini

```bash
git clone https://github.com/mdg-bali/makingsensebali your-org/makingsense-yourplace
cd makingsense-yourplace

# Update the remote to your own GitHub org
git remote set-url origin git@github.com:your-org/makingsense-yourplace.git
git push -u origin main
```

GitHub Pages: aktifkan pada fork Anda. Situs menjadi live di `your-org.github.io/makingsense-yourplace/`.

### Langkah 3 — Sesuaikan situs kampanye

Sunting `index.html` dan `dashboard/index.html`:

- Ganti "Bali" / "Bukit" dengan kota / bioregion Anda di seluruh teks
- Perbarui teks hero, kerangka metodologi, atribusi hosted-by
- Perbarui palet warna jika mau — saffron + teal saat ini bernuansa Bali; Barcelona mungkin lebih suka yang lain
- Perbarui bounding box dan pusat peta di `data.js` (`BALI_BOUNDS`, `BALI_CENTER`)
- Perbarui `murmurations.json` dengan nama org, lokasi, mitra, dan tag Anda

Panduan penyesuaian rinci: [docs/web-presence.md](docs/web-presence.md).

### Langkah 4 — Sebarkan Smart Citizen Kits

- Beli 2–5 unit SCK dari [smartcitizen.me](https://smartcitizen.me/store) (~$150 masing-masing)
- Daftarkan di smartcitizen.me, dapatkan ID perangkat Anda
- Sebarkan — kantor kampanye, Fab Lab tuan rumah, lokasi mitra, rumah Anda
- Perbarui `data.js` `KNOWN_BALI_SCK_IDS` → `KNOWN_[YOURCITY]_SCK_IDS` dengan ID perangkat Anda

Panduan rinci: [docs/sensors.md](docs/sensors.md).

**Alternatif lebih murah — node DIY workshop.** Untuk kepadatan spasial 5× per dolar dibanding SCK, folder [`hardware/diy-node/`](hardware/diy-node/) mendokumentasikan dua tingkat: Basic ~$15–25 (XIAO ESP32-S3 + BME680, kualitas udara dalam ruangan + iklim + VOC, tanpa PM) dan Plus ~$35–60 (Basic + Grove HM3301, menambah PM1/2.5/10). Fidelitas lebih rendah dari SCK, rakitan setengah hari di Fab Lab tuan rumah Anda, dapat diakses peserta non-teknis. Node DIY bukan pengganti SCK — keduanya adalah node kepadatan spasial yang dirujuk terhadap kalibrasi SCK. Lihat `hardware/diy-node/README.md` untuk strategi tingkat lengkap.

### Langkah 5 — Rancang dan luncurkan survei Fase 1

- Fork pertanyaan survei Bali di [docs/phase-1-survey.md](docs/phase-1-survey.md)
- Adaptasikan untuk konteks Anda — ganti contoh khas Bali dengan isu relevan di bioregion Anda
- Terjemahkan ke bahasa lokal
- Siapkan basis Airtable untuk tanggapan (tier gratis mencakup ~1000 tanggapan)
- Sematkan survei di situs kampanye Anda atau tautkan keluar
- Mulai penjangkauan: sekolah, dewan kewilayahan, media sosial, organisasi mitra

### Langkah 6 — Dirikan komponen laporan

Inilah beban teknis terberat. Baca [`reports/README.md`](reports/README.md) dan [`reports/DEPLOY.md`](reports/DEPLOY.md) secara menyeluruh sebelum memulai.

Anda akan membutuhkan:

- Host yang selalu menyala dengan Docker — Synology DS725+ (~$300 + drive) adalah rujukannya; kotak Linux mana pun dengan Docker bisa
- Sebuah Mac Apple Silicon cadangan untuk inferensi vision (atau ganti dengan Claude Haiku seharga ~$5/bulan)
- Sebuah nomor WhatsApp — SIM khusus / nomor bisnis direkomendasikan untuk produksi (nomor pribadi cukup untuk fase pilot)

Perubahan konfigurasi dari pengaturan default Bali:

- `reports/config.json` — `node_id`, `bioregion`, `primary_url`, allowlist untuk tester Anda
- `reports/messages.py` — terjemahkan semua string yang dilihat pengguna ke bahasa lokal Anda
- `reports/murmurations_adapter.py` — perbarui `BUKIT_BBOX` / `BALI_LOCALITIES` ke bounding box dan nama-nama lingkungan bioregion Anda

### Langkah 7 — Publikasikan profil Murmurations Anda

Sunting `murmurations.json` untuk kampanye Anda:

- `name`, `nickname`, `primary_url` — kampanye Anda
- `tags` — konteks lokal Anda
- `description`, `mission` — kerangka lokal Anda
- `urls` — URL kampanye Anda
- `locality`, `region`, `country_iso_3166`, `geolocation` — bioregion Anda
- `contact_details` — Fab Lab Anda
- `relationships` — pertahankan relasi schema-org ke fab.city, fablabs.io, making-sense.eu, smartcitizen.me; tambahkan mitra lokal mana pun

Lalu kirimkan URL profil ke [Murmurations Index](https://murmurations.network/) agar kampanye Anda dapat ditemukan.

### Langkah 8 — Luncurkan Fase 1 secara publik

Beri tahu orang-orang bahwa kampanye ini ada. Penjangkauan melalui:

- Kanal yang sudah dimiliki Fab Lab tuan rumah
- Jaringan chapter Fab City
- Sekolah lokal dan organisasi komunitas
- Media sosial (platform apa pun yang benar-benar digunakan warga Anda)
- Pers, jika Anda memiliki kontak media

Fase 1 adalah fase keterlibatan yang paling padat di awal. Rencanakan untuk itu.

### Langkah 9 — Mulai Fase 2 secara paralel

Begitu SCK terpasang dan bot laporan sudah live dengan allowlist kecil, mulailah mengumpulkan data secara paralel dengan survei Fase 1. Peta gabungan (sensor + laporan yang disetujui) di situs kampanye Anda menjadi artefak publiknya.

---

## 5. Lokalisasi — apa yang berubah untuk bioregion Anda

Basis kode ini sengaja dibuat dapat dikonfigurasi, tetapi beberapa keputusan bersifat tekstual dan memerlukan pertimbangan manusia, bukan sekadar penyuntingan kode.

### Bahasa

Teks bot laporan yang dilihat pengguna ada di [`reports/messages.py`](reports/messages.py). Semua string bersifat dwibahasa (bahasa lokal lebih dahulu, bahasa Inggris dengan huruf miring di bawahnya). Untuk penyebaran Anda:

- Pilih bahasa lokal utama Anda (Catalan + Spanyol untuk Barcelona, Yucatec Maya + Spanyol untuk Yucatán, Kannada + Inggris untuk Bangalore)
- Pilih bahasa sekunder (Inggris adalah konvensi; bisa berbeda jika konteks Anda menuntutnya)
- Minta **penutur asli meninjau setiap string** sebelum dipublikasikan. Kepercayaan dibangun pada balasan pertama.

Situs kampanye (`index.html`) memiliki teksnya sendiri, sebagian besar bahasa Inggris dalam penyebaran rujukan Bali. Untuk audiens yang tidak mengutamakan bahasa Inggris, terjemahkan.

### Bounding box dan lingkungan lokalitas

Di `reports/murmurations_adapter.py`:

- `BUKIT_BBOX` → bounding box kota/bioregion Anda (lat/lon min/max)
- `BALI_LOCALITIES` → daftar nama lingkungan yang harus dikenali dalam deskripsi laporan

Bot menggunakan ini untuk otomatis mengkategorikan di mana sebuah laporan berada. Lokalitas Barcelona adalah Eixample, Gràcia, Raval, Sant Antoni, Poblenou, Sants, Sarrià, Horta — dan masih banyak lagi.

### Penetapan bioregion

Di `reports/config.json`, atur `bioregion` ke salah satu nilai enum bioregion Murmurations (skema di `reports/schemas/environmental_observation-v1.0.0.json` mencantumkannya). Bioregion Barcelona adalah `mediterranean_basin`. Jika bioregion Anda tidak ada dalam enum, ajukan perluasan melalui skema.

### Identitas visual

Palet situs saat ini (saffron + teal + kertas krem) membangkitkan suasana Bali — matahari, air, kertas tropis. Untuk penyebaran Anda, Anda dapat mempertahankannya (menandakan keanggotaan jaringan) atau beralih ke aksen lokal. Variabel CSS didefinisikan di bagian atas `index.html` untuk pergantian palet yang mudah.

### Kategori

Enum `pollution_category` pada skema mencakup sebagian besar keprihatinan lingkungan: pembakaran, sampah, kendaraan, konstruksi, debu, industri, kimia, air, kebisingan, deforestasi. Jika bioregion Anda memiliki kategori yang tidak cocok (mis., khusus untuk industri, iklim, atau geografi Anda), ajukan penambahannya ke skema alih-alih membebani kategori yang ada.

### Tata kelola dan atribusi

Tiga rujukan yang harus diperbarui fork Anda secara konsisten:

- "Hosted by Fab Lab Bali" → di-host oleh Fab Lab Anda
- "Part of Fab City Bali" → bagian dari chapter Fab City Anda
- Tomas Diez sebagai pemimpin yang ditunjuk → pemimpin yang Anda tunjuk

Pertahankan rujukan ke Making Sense, Smart Citizen Kit, Fab Lab Barcelona / IAAC dalam garis keturunan — itulah hulu bersama yang dibagikan semua instance Making Sense [tempat].

---

## 6. Federasi — bergabung dengan jaringan

Setiap instance Making Sense [tempat] bersifat independen tetapi dapat ditemukan. Federasi terjadi melalui dua mekanisme saat ini dan satu di masa depan:

### Saat ini — Murmurations

Begitu Anda mempublikasikan `murmurations.json` dan mengirimkannya ke [Murmurations Index](https://murmurations.network/), kampanye Anda dapat ditemukan dalam ekosistem Murmurations yang lebih luas. Jaringan data komunitas mana pun dapat melakukan kueri `tags=citizen sensing` atau `tags=fab lab` dan menemukan instance Anda berdampingan dengan Making Sense Bali, Making Sense Barcelona, dan lainnya.

Ini adalah bentuk federasi yang paling ringan: kampanye Anda *dapat ditemukan* tetapi setiap instance beroperasi secara independen. Tidak ada berbagi data antar node, tidak ada infrastruktur bersama.

### Saat ini — tautan dua arah

Setiap situs Making Sense [tempat] menautkan ke yang lain melalui jaringan Fab City dan Fab Lab. Bagian garis keturunan di README setiap kampanye mengakui metodologi dan platform bersama. Jaringan menjadi tampak melalui kutipan, bukan melalui integrasi teknis.

### Masa depan — federasi PLANETAI

PLANETAI adalah horizon jangka panjang: lapisan federasi yang mengagregasi laporan yang disetujui di seluruh instance Making Sense [tempat], memungkinkan Anda melakukan kueri pola lintas bioregion, dan menyediakan infrastruktur bersama (hosting profil, penemuan lintas-instance, layanan AI opsional). Infrastruktur PLANETAI belum dibangun — ketika sudah, bergabung dengan federasi bersifat opt-in dan dikonfigurasi di `reports/config.json`.

Untuk saat ini, rancang dan operasikan instance Anda seolah-olah ia akan berfederasi. Skema Murmurations dibagikan, bentuk laporan dibagikan, metodologi dibagikan. Ketika PLANETAI ada, pekerjaan teknis untuk berfederasi akan menjadi perubahan konfigurasi, bukan refactor.

---

## 7. Di mana mendapatkan bantuan

- **Repositori**: [github.com/mdg-bali/makingsensebali](https://github.com/mdg-bali/makingsensebali) — ajukan issue, usulkan pull request
- **Percakapan replikasi**: [fablabbali@gmail.com](mailto:fablabbali@gmail.com) — inbox Fab Lab Bali. Hubungi sebelum memulai; panggilan singkat di awal menghemat berminggu-minggu menebak-nebak.
- **Jaringan Fab City**: [fab.city](https://fab.city/) — untuk status chapter, perkenalan mitra
- **Platform Smart Citizen**: [smartcitizen.me](https://smartcitizen.me/) — perangkat keras, penyiapan akun, pertanyaan sensor

Jika Anda serius mempertimbangkan replikasi, mohon hubungi kami sebelum memulai. Panggilan singkat di awal menghemat berminggu-minggu menebak-nebak — dan memungkinkan kami mengoordinasikan waktu peluncuran, berbagi materi, serta menghubungkan Anda dengan chapter yang berdekatan.

---

## 8. Lisensi dan atribusi

Semua kode di repositori ini: **MIT**.
Dokumentasi, skema, survei, dan metodologi: **CC-BY-SA 4.0**.

Jika Anda mem-fork dan menjalankan Making Sense [tempat], kami meminta tiga hal:

1. **Kreditkan garis keturunannya.** Making Sense (Fab Lab Barcelona / IAAC, 2015–2017), Smart Citizen (ikut didirikan oleh Tomas Diez dan Alex Posada, 2012), Making Sense Bali (Fab Lab Bali, 2026) di README Anda dan di situs kampanye Anda.
2. **Jaga agar jaringan tetap dapat dipahami.** Gunakan konvensi penamaan "Making Sense [tempat]". Publikasikan profil Murmurations Anda. Tautkan ke instance lain.
3. **Bagikan kembali.** Perbaikan pada kode, metodologi, dokumen — pull request kami sambut. Kit ini menjadi lebih baik ketika setiap instance baru menyumbangkan kembali apa yang mereka pelajari.

---

Dibangun oleh [Fab Lab Bali](https://fablabbali.com), untuk jaringan [Fab City](https://fab.city/).
Untuk Barcelona, Yucatán, Montreal, Goa, Santiago, dan instance bioregional lain yang belum hadir.
