[English](HOME_REVISION.md) · **Bahasa Indonesia** · [Español](HOME_REVISION.es.md)

# Making Sense Bali · Ringkasan Revisi Halaman Beranda (v2)

**Status:** ringkasan — belum dimulai.
**Penanggung jawab eksekusi:** Claude Code.
**Penanggung jawab maksud:** Tomas Diez (penanggung jawab Making Sense Bali).
**Ringkasan pendamping:** [`docs/PLATFORM_REVISION.md`](PLATFORM_REVISION.md) — revisi dasbor yang baru saja dirilis. Revisi halaman beranda dibangun di atas kapabilitas analitis yang kini disediakan oleh dasbor tersebut, tetapi menyasar audiens yang berbeda dan mode keterlibatan yang berbeda.
**Terakhir diperbarui:** 2026-05-30.

---

## 1. Mengapa revisi ini

Halaman beranda saat ini (`index.html`, 1234 baris) terbaca seperti esai editorial — bentuk panjang, sadar metodologi, dan dibuat dengan baik untuk seseorang yang bersedia menggulir dan terlibat. Audiens itu memang ada (peneliti, sesama chapter Fab City, jurnalis) dan teks yang ada melayani mereka dengan baik. **Namun itu bukan audiens utama yang perlu ditumbuhkan oleh kampanye ini.**

Jangkauan nyata kampanye terjadi melalui tiga audiens yang tidak membaca situs editorial dari awal hingga akhir:

- **Para ibu di kos Denpasar / Canggu / Ubud** yang bertanya "apakah udara hari ini buruk untuk anak saya yang asma?"
- **Para guru** yang bertanya "bisakah saya menunjukkan kepada kelas saya data lokal yang nyata tentang sesuatu yang mereka hirup setiap hari?"
- **Pejabat pemerintah di Dinas Kesehatan dan DLHK** yang bertanya "adakah bukti di sini yang bisa saya tindaklanjuti?"

Bagi audiens ini halaman saat ini terlalu padat, terlalu tidak terstruktur, dan — yang paling penting — **terlalu minim ajakan bertindak**. Mereka tidak butuh bagian metodologi yang lebih panjang. Mereka perlu mendarat di halaman, langsung melihat sesuatu yang relevan dengan tempat tinggal mereka, dan memiliki satu langkah berikutnya yang jelas.

Revisi ini menghadirkan:

1. **Hero yang mengutamakan tingkat keparahan** yang menjawab "apakah buruk sekarang di tempat saya?" dalam waktu kurang dari tiga detik, dalam bahasa yang jelas, dengan kejelasan lampu lalu lintas.
2. **Empat ajakan bertindak yang jelas** yang bekerja untuk setiap audiens: lapor, survei, terlibat dengan sensor, bagikan apa yang sedang terjadi.
3. **Kartu yang bisa dibagikan** — visual yang dibuat otomatis tentang apa yang terjadi di lingkungan / waktu tertentu, dirancang untuk menyebar di WhatsApp dan Instagram tempat audiens sudah berada.
4. **Bagian khusus audiens** — bukan pemilih ("apakah Anda seorang ibu atau guru?"), tetapi bagian yang tersusun rapi sehingga setiap audiens dapat menemukan apa yang mereka butuhkan tanpa harus menggulir melewati yang tidak mereka butuhkan.

Revisi dasbor mengubah data menjadi sebuah alat. Revisi ini mengubah halaman beranda menjadi **mekanisme distribusi** untuk apa yang ditemukan oleh alat tersebut. Tanpa ini, kampanye menghasilkan data yang baik yang tidak dilihat oleh siapa pun di luar lingkaran analis.

## 2. Keadaan saat ini — apa yang ada hari ini

| Bagian | Baris | Catatan |
|---|---|---|
| Hero ("Bali, made visible") | ~400–410 | Mengedepankan merek. Tidak ada personalisasi lokasi. Tidak ada indikator tingkat keparahan. |
| Bagian peta | ~410–440 | Berada di beranda; menduplikasi apa yang sudah lebih mampu ditangani oleh dasbor. Tentukan apakah tetap dipertahankan. |
| Umpan laporan | ~440–447 | Disembunyikan secara bawaan (`display:none`) — berasal dari pekerjaan dasbor, belum dimunculkan di beranda. |
| "The state of Bali's air" | ~451–479 | Ringkasan editorial. Berguna untuk konteks, saat ini terlalu padat prosa. |
| "The reading, translated" | ~479–548 | Bantuan interpretasi — sudah melakukan sebagian pekerjaan yang dibutuhkan para ibu. Susun ulang agar mengutamakan tingkat keparahan. |
| "Listen. Show. Act." | ~548–589 | Pembingkaian metodologi. Penting bagi pejabat, kurang penting bagi para ibu. Tempatkan ulang. |
| "Local lead, credited methodology" | ~589–620 | Asal-usul / tata kelola. Penting untuk kredibilitas, terutama bagi pejabat. |
| "Where we are" | ~620–638 | Cakupan jaringan. |
| "Concerns" + Survei | ~638–672 | Tautan survei Fase 1. **Salah satu dari empat CTA.** Saat ini terkubur di baris 664. |
| "Eight questions" / Beyond survey | ~674–714 | Detail survei + kontak. |
| "Need more detail?" | ~715+ | Tautan dasbor. |

Pengkabelan yang sudah ada dan layak dipertahankan:

- **Variabel CSS** untuk palet merek (saffron + teal + kertas krem) berada di bagian atas berkas dan digunakan secara konsisten. Pertahankan.
- **`<script src="data.js">`** sudah dimuat — halaman beranda sudah memiliki akses ke keadaan sensor + laporan langsung, hanya belum dimunculkan secara visual selain pada peta.
- **Lapisan terjemahan dwibahasa** dari revisi dasbor sebaiknya dibawa ke halaman beranda sejak hari pertama. Jangan merilis beranda berbahasa Inggris saja yang sebenarnya sudah bisa disajikan dasbor dalam Bahasa Indonesia.
- **Tautan survei** sudah terhubung melalui `#surveyLink` → formulir Airtable eksternal.

Halaman ini berfungsi dan koheren dengan merek. Revisi ini **bukan penulisan ulang dari nol** — ini adalah penataan ulang dengan beberapa komponen baru dan hierarki yang lebih tajam.

## 3. Keadaan sasaran — apa yang harus dibangun

### 3.1 Hero yang mengutamakan tingkat keparahan

Ganti blok hero saat ini dengan blok yang, saat halaman dimuat, mencoba mendeteksi lingkungan pengunjung (API geolokasi, dengan fallback yang anggun ke dropdown "pilih lingkungan Anda") dan menampilkan:

- **Satu angka utama** — pembacaan PM2.5 terburuk hari ini di wilayah pengunjung, dengan pita tingkat keparahan berkode warna (hijau / kuning / oranye / merah, sesuai pedoman paparan harian WHO)
- **Satu baris berbahasa sederhana** dalam bahasa yang dipilih pengunjung — contoh:
  - HIJAU: *"Udara bersih hari ini di Denpasar. Bermain di luar ruangan aman."*
  - KUNING: *"Udara sedang hari ini di Canggu. Kelompok sensitif (anak-anak, asma, lansia) sebaiknya membatasi aktivitas luar ruangan yang berkepanjangan."*
  - ORANYE: *"Udara tidak sehat di Ubud hari ini. Masker disarankan di luar ruangan, terutama untuk anak-anak."*
  - MERAH: *"Udara berbahaya hari ini di Sanglah. Tetap di dalam ruangan, jendela tertutup, pakai masker di luar."*
- **Satu baris konteks kecil** — "PM2.5 memuncak pada 47 µg/m³ pukul 14:32 · Pedoman harian WHO: 5 µg/m³"
- **Dua tombol utama** di hero: "Report what you see →" (deeplink WhatsApp) dan "What's happening near me →" (gulir/lompat ke bagian terlokalisasi di bawah)

Jika geolokasi ditolak atau tidak ada sensor di dekat pengunjung, gunakan default agregat seluruh Bali ("Air across Bali today: moderate · worst reading: Ubud") dan dropdown "Pick your area" yang menonjol.

Hero harus berfungsi mengutamakan seluler (lebar 375px); di sinilah sebagian besar pengunjung akan melihatnya.

### 3.2 Empat ajakan bertindak

Munculkan keempat CTA di atas lipatan ATAU dalam satu layar gulir — tidak terkubur di baris 664 seperti survei saat ini. Setiap CTA adalah kartu dengan satu kata kerja yang jelas dan satu deskripsi singkat. Usulan kata-kata (tunduk pada peninjauan suara merek):

1. **"Report what you're seeing →"**
   *Mencium asap? Melihat pembakaran sampah? Memperhatikan bau yang kemarin tidak ada? Kirim satu pesan WhatsApp ke bot kami, tim lokal kami memverifikasi, dan laporan itu bergabung dengan peta publik.*
   Aksi: deeplink WhatsApp ke nomor bot (sudah ada di `reports/config.json`).

2. **"Tell us what matters →"**
   *Survei Fase 1 menanyakan kepada warga isu lingkungan apa yang memengaruhi kehidupan sehari-hari. Delapan pertanyaan, 5 menit, menentukan ke mana kami menempatkan sensor berikutnya.*
   Aksi: membuka formulir survei Airtable yang ada di tab baru.

3. **"Get involved with sensors →"**
   *Kami menyelenggarakan lokakarya pembuatan sensor di Fab Lab Bali — rakit sebuah node kualitas udara berbiaya rendah dalam satu sore, pasang di atap rumah atau di kelas Anda. Daftar untuk mendapatkan info lokakarya berikutnya.*
   Aksi: membuka formulir pendaftaran (Airtable atau sejenisnya — koordinasikan dengan tim komponen laporan). Ke depan: ini menjadi halaman pembelian kit; rancang kartu agar bisa beralih ke sana tanpa penulisan ulang.

4. **"Share what's happening →"**
   *Buat kartu yang bisa dibagikan tentang udara hari ini di lingkungan Anda dan posting di tempat percakapan sudah berlangsung — WhatsApp, Instagram, Telegram. Setiap pembagian membantu lebih banyak orang melihat data.*
   Aksi: membuka bagian kartu yang bisa dibagikan (3.4 di bawah).

CTA harus terasa seperti opsi berbobot setara, bukan satu CTA hero dengan tiga pelengkap. Tata letak bergaya kartu, empat sejajar di desktop, dua kali dua atau bertumpuk di seluler.

### 3.3 Bagian khusus audiens (tiga bacaan)

Di bawah hero + CTA, tiga bagian substantif — masing-masing diberi judul yang jelas agar pengunjung tahu mana yang ditujukan untuk mereka, tetapi semuanya terlihat (tidak di balik tab atau pemilih):

**Untuk keluarga dan warga** — "Hari ini di lingkungan Anda"
- Widget tingkat keparahan dari hero, diperluas dengan grafik 24 jam terakhir untuk PM2.5 (tautan ke dasbor untuk tampilan lebih mendalam)
- Laporan terdekat sebagai umpan singkat (3–5 terbaru dalam radius ~2km)
- Panduan bahasa sederhana: kapan harus menutup jendela, kapan menggunakan masker untuk anak-anak, apa arti tingkat kelembapan bagi penderita asma
- Indikator risiko jamur jika kelembapan lingkungan telah >60% selama >24 jam berturut-turut
- CTA "Report what you see" diulang di akhir bagian ini

**Untuk guru dan sekolah** — "Bawa data ke dalam kelas Anda"
- "Rencana pembelajaran menggunakan data kualitas udara lokal Bali" — pitch singkat + PDF yang bisa diunduh (tulis rencana pembelajaran v1 minimal jika belum ada; tidak perlu rumit, cukup nyata)
- Pembingkaian lokakarya — "Making Sense Bali untuk sekolah" — bahkan jika masih aspiratif, sebutkan apa yang ditawarkan
- Satu contoh konkret: "Murid Anda membandingkan PM2.5 sekolah Anda dengan pedoman WHO, lalu dengan sekolah di Barcelona melalui jaringan global Smart Citizen"
- CTA "Get involved with sensors" diulang di akhir bagian ini

**Untuk pembuat kebijakan dan analis** — "Bukti yang bisa Anda tindaklanjuti"
- Kebijakan data / asal-usul kampanye (sebagian besar bagian "Local lead, credited methodology" saat ini dipindahkan ke sini)
- Unduhan agregat — CSV 30 hari terakhir, ringkasan bulanan PDF (dapat dibuat otomatis tiap malam melalui infrastruktur `generate_summary.py` yang ada di `reports/`)
- "Cara mengutip data Making Sense Bali dalam kebijakan" — paragraf singkat dengan format kutipan yang disarankan dan email kontak
- Tautan ke dasbor untuk analisis langsung
- Baris kontak untuk keterlibatan langsung dengan tim kampanye

Setiap bagian sebaiknya memiliki jangkar visual yang jelas (ikon, aksen warna) agar pengunjung dapat memindai dan melewati jika mereka bukan audiensnya.

### 3.4 Kartu yang bisa dibagikan — mekanisme pertumbuhan

Ini adalah bagian paling baru dari revisi ini dan mungkin layak diberi waktu satu minggu tersendiri.

**Konsep:** menghasilkan kartu visual yang dirancang otomatis yang merangkum apa yang terjadi di sebuah wilayah Bali, dalam format yang dioptimalkan untuk dibagikan di grup WhatsApp, Instagram stories, dan kanal Telegram — tempat audiens sasaran kampanye sudah menghabiskan waktu.

**Templat kartu (mulai dengan keempat ini):**

1. **"Today in [neighbourhood]"** — PM2.5 saat ini + pita tingkat keparahan + interpretasi satu baris + referensi pedoman WHO + logo Making Sense Bali + URL
2. **"This week in [neighbourhood]"** — grafik tren PM2.5 7 hari (sparkline) + jumlah puncak + kategori laporan paling umum + URL
3. **"Mold risk: [neighbourhood]"** — tren RH + jumlah hari di atas 60% RH + catatan risiko bahasa sederhana + URL
4. **"Burning corridor: [neighbourhood]"** — lonjakan PM gabungan + jumlah laporan + cuplikan peta yang menunjukkan area sumber + URL

Setiap kartu memiliki:
- Tanda visual kampanye (palet + tipografi dari variabel CSS yang ada)
- Stempel waktu ("as of 14:32 WITA, 2026-05-30")
- Wordmark Making Sense Bali + URL pendek
- Kode QR (kecil, di sudut) yang menautkan ke tampilan dasbor yang relevan

**Opsi rendering:**

Opsi A (disarankan untuk v1): rendering HTML canvas di sisi klien. Kartu dibangun sebagai HTML bergaya, dikonversi ke PNG via `html2canvas` atau sejenisnya, diunduh melalui tombol "Download card". Ditambah tombol "Share to WhatsApp" yang menggunakan skema URL berbagi WhatsApp yang membuka WhatsApp pengguna dengan teks yang sudah terisi dan tautan kembali ke situs.

Opsi B (Fase 2): Cloudflare Worker yang merender SVG → PNG sesuai permintaan di URL seperti `/share/today/canggu.png`. Ini memungkinkan tag meta og:image di situs menunjuk ke kartu yang baru dirender, sehingga ketika siapa pun membagikan URL situs di mana pun, pratinjau tautannya adalah kartu terlokalisasi yang terkini. Berdampak lebih besar tetapi membutuhkan infrastruktur lebih banyak.

**Penerimaan yang diperlukan:** pengunjung di Canggu dapat mengeklik "Share what's happening" di hero, melihat empat opsi kartu, memilih "Today in Canggu", dan mengunduhnya atau membagikannya ke WhatsApp dalam dua ketukan. Kartu tersebut terlihat cukup khas sehingga seseorang yang melihatnya di grup WhatsApp mengenalinya sebagai Making Sense Bali (bukan tangkapan layar kualitas udara generik).

### 3.5 Korelasi yang dimunculkan di halaman beranda

Dasbor kini menampilkan korelasi antara puncak sensor dan laporan warga. Halaman beranda sebaiknya memunculkan **satu korelasi terbaru yang paling mencolok** sebagai panel naratif, yang disegarkan setiap hari. Contoh teks:

> **"Data dan warga menceritakan kisah yang sama kemarin."**
>
> Pukul 14:30 di Canggu, sensor kualitas udara di Jl. Pantai Berawa mencatat lonjakan tajam PM2.5 — dari 12 menjadi 78 µg/m³ dalam dua puluh menit, jauh melewati ambang tidak sehat WHO. Dua belas menit kemudian, seorang warga dua jalan dari sana melaporkan asap dari lokasi konstruksi yang membakar bahan sampah. Kedua sinyal itu saling mengonfirmasi. Fab Lab Bali memberi tahu Banjar Berawa untuk tindak lanjut.
>
> [See the data →](/dashboard/) [Read the report →](/dashboard/#report-id) [Report what you're seeing →](whatsapp://...)

Pilih korelasi bermakna terbaru setiap hari (puncak tertinggi dengan laporan yang cocok, atau wilayah yang paling sering dikunjungi). Panel naratif membuat nilai kampanye terasa nyata dengan cara yang tidak akan pernah dilakukan grafik abstrak — bagi audiens pejabat terutama, inilah artefak yang dikutip dalam percakapan.

Untuk v1, narasi ini dapat **dikurasi manusia** (operator Fab Lab Bali memilih kisah harian dari mesin korelasi dasbor). Pembuatan otomatis adalah Fase 2.

## 4. Pentahapan yang disarankan

**Fase 1 — Hero yang mengutamakan tingkat keparahan + empat CTA.** ~4 hari.
- Geolokasi + deteksi wilayah (dengan fallback manual)
- Widget tingkat keparahan dengan interpretasi berbasis pita
- Empat kartu CTA di atas lipatan
- Tata letak mengutamakan seluler

**Fase 2 — Penataan ulang bagian audiens.** ~3 hari.
- Susun ulang bagian-bagian yang ada menjadi tiga blok khusus audiens
- Tambahkan bagian yang hilang (placeholder rencana pembelajaran, panduan kutipan, widget risiko jamur)
- Jangan kehilangan konten metodologi yang ada — pindahkan saja

**Fase 3 — Kartu yang bisa dibagikan (rendering sisi klien).** ~1 minggu.
- Empat templat kartu sebagai HTML bergaya
- Unduhan PNG dengan `html2canvas`
- Integrasi URL berbagi WhatsApp
- Bagian "Share what's happening" sebagai UI induk

**Fase 4 — Narasi korelasi harian.** ~3 hari.
- Alur kurasi manual terlebih dahulu (berkas JSON yang diedit operator seperti `data/daily_story.json`)
- Render otomatis di beranda dari JSON
- Fase 2: pilih otomatis dari keluaran korelasi dasbor

**Fase 5 — Pemolesan + Bahasa + og:image.** ~4 hari.
- String dwibahasa (manfaatkan infrastruktur `t()` dasbor)
- Pembuatan og:image (Cloudflare Worker, Opsi B dari §3.4)
- QA seluler, pemeriksaan aksesibilitas
- Performa: halaman beranda tetap dimuat <3 detik pada 3G

Total: ~3,5 minggu. Fase 1 dan 2 memberikan peningkatan yang paling terasa dan dapat dirilis sebelum fase 3–5 hadir.

## 5. Kriteria penerimaan

Revisi selesai ketika:

- [ ] Pengunjung mendarat di halaman beranda di seluler dan dalam satu detik tahu apakah udara baik di lingkungannya (dengan asumsi izin geolokasi atau default yang masuk akal)
- [ ] Keempat CTA terlihat di atas lipatan atau dalam satu gulir pada ponsel selebar 375px
- [ ] Seorang guru dapat menemukan rencana pembelajaran yang bisa diunduh dari halaman beranda dalam waktu kurang dari 30 detik
- [ ] Seorang pembuat kebijakan dapat menemukan panduan pengutipan data dan unduhan CSV dalam waktu kurang dari 30 detik
- [ ] Pengunjung dapat membuat dan mengunduh kartu yang bisa dibagikan untuk lingkungannya dalam kurang dari tiga ketukan
- [ ] Pengunjung yang membagikan URL situs di WhatsApp melihat kartu pratinjau tautan yang relevan dengan wilayah (pekerjaan og:image Fase 5)
- [ ] Narasi korelasi harian terlihat di atas lipatan pada halaman beranda
- [ ] Halaman beranda berfungsi baik dalam bahasa Inggris maupun Bahasa Indonesia menggunakan infrastruktur terjemahan yang sama yang kini digunakan dasbor
- [ ] Tidak ada regresi dalam waktu muat (saat ini cepat; jangan membengkak dengan pustaka gambar — `html2canvas` adalah satu-satunya dependensi berat yang baru)

## 6. Bukan tujuan

- **Tanpa modal pemilih audiens atau sistem tab** ("Apakah Anda seorang ibu, guru, atau pejabat?"). Itu mengada-ada. Susun halaman agar setiap audiens menemukan bagiannya dengan memindai, bukan dengan mengidentifikasi diri di awal.
- **Tanpa e-commerce.** "Get involved with sensors" saat ini adalah pendaftaran lokakarya, bukan pembelian kit. Rancang CTA agar bisa beralih ke alur pembelian nanti tanpa penulisan ulang halaman, tetapi jangan bangun alur pembeliannya dulu.
- **Tanpa menghapus konten metodologi editorial.** Pindahkan, ringkas, tetapi jangan kehilangannya — itulah yang memberi kampanye kredibilitas terutama dengan audiens pejabat. Bagian "Local lead, credited methodology" menjadi bagian dari blok pembuat kebijakan.
- **Tanpa menggantikan kedalaman analitis dasbor di halaman beranda.** Beranda menampilkan ringkasan dan korelasi yang paling mencolok; dasbor tetap menjadi tempat untuk analisis serius. Jangan coba menjadikan halaman beranda sebagai dasbor kedua.
- **Tanpa kerangka kerja baru.** Batasan yang sama dengan ringkasan dasbor — vanilla JS, situs statis, tanpa React/Vue/dll.
- **Tanpa login atau keadaan per-pengguna di halaman beranda.** Beranda bersifat baca-publik, sepenuhnya dapat di-cache, tanpa data per-pengunjung selain cookie/localStorage wilayah untuk "ingat lingkungan saya".

## 7. Dependensi dan hal yang belum pasti

- **Alur izin geolokasi.** Sebagian besar pengunjung akan menolaknya saat ditanya pertama kali. Sediakan fallback yang masuk akal ("Agregat seluruh Bali · pilih wilayah Anda di bawah") dan UX permintaan yang jelas serta tidak mengganggu.
- **Batas wilayah.** Dasbor menggunakan daftar `BALI_LOCALITIES` (di `reports/murmurations_adapter.py`) — gunakan kembali untuk dropdown wilayah halaman beranda. Jika perlu menambahkan wilayah baru, lakukan di satu tempat dan impor ke mana-mana.
- **Tujuan pendaftaran lokakarya.** Putuskan sebelum memulai Fase 1: formulir Airtable, Tally, Formspree sederhana, atau endpoint kustom? Rekomendasi: Airtable agar sesuai dengan infrastruktur survei.
- **Konten rencana pembelajaran.** v1 dapat dirilis dengan PDF satu halaman yang hanya menampilkan "bandingkan pembacaan PM2.5 24 jam terakhir sekolah Anda dengan pedoman harian WHO dan dengan sekolah rujukan di Barcelona melalui jaringan global Smart Citizen." Tidak perlu rumit; perlu ada. Mitra pendidik dapat menyempurnakannya nanti.
- **Kurasi korelasi harian.** Hingga mesin korelasi dasbor memilih kisah harian secara otomatis, putuskan siapa di Fab Lab Bali yang secara manual memilih dan menulisnya setiap hari, dan di mana JSON-nya berada. Saran: `data/daily_story.json` diperbarui melalui jalur admin yang sama dengan laporan.
- **Format URL berbagi WhatsApp di iOS Safari** — kadang tidak stabil. Uji di perangkat sungguhan, gunakan fallback ke API `navigator.share()` jika tersedia.

## 8. Cara memulai

1. Buat cabang kerja: `git checkout -b home-v2`
2. Baca [`index.html`](../index.html) dari awal hingga akhir. Identifikasi apa yang tetap, apa yang pindah, apa yang baru. Buat catatan — berkasnya 1234 baris dan penataan ulang adalah bagian terbesar dari pekerjaan, bukan komponen barunya.
3. Baca ringkasan ini ditambah [`PLATFORM_REVISION.md`](PLATFORM_REVISION.md) agar revisi halaman beranda mendarat konsisten dengan pekerjaan dasbor yang baru saja dirilis.
4. Mulai dengan Fase 1 (hero + CTA). Rilis itu sebelum menyentuh bagian audiens; peningkatan yang langsung terlihat, risiko regresi rendah.
5. PR ke `main`. GitHub Pages mengambil perubahan secara otomatis.

## 9. Ketika ini selesai

Perbarui ringkasan ini dengan header "Status: complete" dan ringkasan satu paragraf tentang apa yang telah dihasilkan. Catat setiap penyimpangan dari ringkasan (templat kartu yang tidak berhasil, fase yang perlu ditata ulang cakupannya, asumsi yang ternyata salah). `REPLICATION.md` kampanye akan merujuk ini sebagai versi halaman beranda yang difork chapter Fab City lainnya — akurasi itu penting.

Jika mekanisme kartu yang bisa dibagikan ternyata benar-benar mendorong keterlibatan (yang akan kita ketahui dari analitik rujukan dalam sebulan setelah peluncuran), tim Fab Lab Barcelona sebaiknya diberi tahu — ini bisa menjadi pola yang ingin mereka bawa kembali ke platform Smart Citizen yang asli.

## 10. Kontak

- Penanggung jawab kampanye: Tomas Diez · `tomas@fab.city`
- Penanggung jawab komponen laporan: Tim Fab Lab Bali · `fablabbali@gmail.com`
- Fab Lab Barcelona (tim platform Smart Citizen): `info@smartcitizen.me`
