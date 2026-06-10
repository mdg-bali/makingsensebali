[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# DIY Node — sensor lokakarya

Sebuah node lingkungan berbiaya rendah yang dapat dirakit di fab lab, yang mempublikasikan data ke [platform Smart Citizen](https://smartcitizen.me/) melalui MQTT. Dibangun di sekitar **Seeed XIAO ESP32-S3** dan sebuah **BME680** (suhu, kelembapan, tekanan, gas/VOC), serta secara opsional diperluas dengan **Seeed Grove HM3301** untuk partikulat di luar ruangan. Tersedia dua varian:

- **Basic** (XIAO + BME680) — ~USD 15–25. Pemantauan kualitas udara dalam ruangan, iklim, risiko jamur, VOC, dan habitat nyamuk.
- **Plus** (Basic + HM3301) — ~USD 35–60. Menambahkan PM1 / PM2.5 / PM10 di luar ruangan untuk pembakaran, lalu lintas, dan debu konstruksi.

Firmware yang sama menjalankan kedua varian — untuk Basic, Anda cukup tidak menyambungkan HM3301 dan membiarkan ID sensornya tetap 0 pada konfigurasi. Waktu perakitan dalam lokakarya: ~2 jam untuk Basic, ~3 jam untuk Plus, dari kit hingga tampil aktif di dasbor.

Node ini adalah **titik masuk lokakarya** ke kampanye Making Sense Bali. Ini bukan pengganti [Smart Citizen Kit](https://smartcitizen.me/store) resmi (~USD 150) — melainkan pelengkap kepadatan spasial. Bersikaplah jujur tentang perbedaan ini kepada peserta lokakarya.

## Apa ini — dan apa yang bukan

DIY node ada untuk **melipatgandakan kepadatan spasial per dolar kampanye**. SCK 2.1 resmi seharga ~USD 150 adalah tulang punggung yang tepercaya — firmware yang teruji, penginderaan multi-parameter terkalibrasi, plug-and-play. Namun dengan uang yang sama untuk satu SCK, kampanye dapat mengirim 3–4 node DIY Plus atau 6–10 DIY Basic, yang dipasang oleh peserta di kamar kos, sekolah, warung, dan kompleks banjar mereka sendiri. Itulah daya ungkitnya: bukan "SCK terlalu mahal" (memang tidak, bagi tim kampanye), melainkan "kami tidak bisa menaruh satu SCK di setiap kos di Denpasar — dan tier DIY bisa mendekatinya." Sebuah Basic seharga USD 20, yang dibangun dalam lokakarya Fab Lab Bali dan dipasang di dinding peserta, membuat seorang warga non-teknis menghasilkan data publik di dasbor yang sama dalam waktu satu sore. Kepadatan itulah intinya.

Apa yang Anda dapatkan:

Apa yang Anda dapatkan dari kedua varian:

- **Suhu, kelembapan, dan tekanan barometrik** dengan akurasi yang memadai
- **Resistansi gas (indikator VOC)** — menangkap asap kayu, asap obat nyamuk bakar, emisi bahan bakar memasak, gas buang kendaraan, produk pembersih. Dipublikasikan sebagai resistansi gas mentah dalam ohm; semakin rendah = semakin banyak VOC. Firmware juga mempublikasikan sebuah **indeks IAQ terbuka** (0–500, semakin rendah = semakin bersih) yang dihitung di perangkat — sebuah perkiraan relatif, bukan indeks Bosch BSEC yang terkalibrasi. Lihat catatan penerapan.
- **Sebuah catatan perangkat Smart Citizen** yang muncul di dasbor kampanye bersama SCK resmi dan stasiun OpenAQ / Sensor.Community
- **Sebuah artefak pengajaran** — peserta meninggalkan lokakarya dengan memahami I²C, firmware ESP32, MQTT, dan apa arti "data Anda bersifat publik"

Apa yang Anda dapatkan tambahan dengan **Plus**:

- **Pembacaan PM1 / PM2.5 / PM10** yang cukup baik untuk mendeteksi peristiwa pembakaran padi, lonjakan lalu lintas, dan debu konstruksi
- **Triangulasi peristiwa pembakaran** — hanya mungkin dengan gas dan PM dalam node yang sama (lihat kasus penggunaan di bawah)

Apa yang tidak Anda dapatkan:

- Sensor kebisingan, eCO₂, cahaya, atau PM terkoreksi-tekanan ambien milik SCK
- Pembacaan terkalibrasi dan terkompensasi-penyimpangan milik SCK (penyimpangan sensor PM dalam kelembapan tropis itu nyata — lihat catatan penerapan)
- Wadah tahan cuaca IP65 (Anda akan mencetaknya di lokakarya; SCK resmi dikirim siap pakai)
- Lima tahun rekayasa firmware oleh tim Fab Lab Barcelona

Ketika kampanye melaporkan data DIY-node, data itu dilaporkan **sebagaimana adanya** — dengan penanda berbeda di dasbor dan tooltip yang menjelaskan kesetiaan yang lebih rendah. Mencampur kit DIY dan resmi secara diam-diam akan tidak jujur dan akan mengikis kredibilitas kampanye dalam percakapan dengan pemerintah daerah yang menjadi muara kampanye ini.

## Dua varian — Basic dan Plus

### Basic — XIAO ESP32-S3 + BME680 (~USD 15–25)

| Jml | Komponen | Tempat | Catatan |
|---|---|---|---|
| 1 | Seeed XIAO ESP32-S3 | Tokopedia (cari "XIAO ESP32S3"), Shopee, distributor Seeed Indonesia | ~Rp 250–350k. Varian Sense juga berfungsi tetapi kameranya tidak terpakai; XIAO standar lebih murah. |
| 1 | Breakout GY-BME680 (6-pin) | Cari "BME680" di Tokopedia, klon generik buatan Tiongkok berfungsi | ~Rp 150–300k. **Pastikan tanda IC tertulis BME680**, bukan BME280 atau BMP280 — penjual terkadang salah memberi label. BME680 adalah satu-satunya di keluarga itu yang memiliki sensor gas/VOC. |
| 1 | Kabel USB-C + catu daya 5V/1A | Di mana saja | Konsumsi daya kit Basic sederhana; pengisi daya ponsel cukup. |
| ~4 | Kabel jumper 22 AWG | Toko elektronik mana pun di Denpasar | Jaga tetap pendek — jumper panjang menambah derau I²C. |
| 1 | Breadboard tanpa solder (prototipe) + perfboard 4×6 cm (penerapan) | Tokopedia "PCB matrix board" | 4×6 cukup untuk XIAO + BME680 dengan ruang lega dan cocok dengan wadah cetakan. Rakitan 5×7 tetap berfungsi — buat ulang STL wadahnya dengan `pb_w=50, pb_h=70`. Atau langsung lanjut ke PCB cetakan pada mesin milling Fab Lab Bali untuk produksi batch. |
| — | Wadah cetak 3D (PETG, bukan PLA) | Fab Lab Bali | PLA melunak pada suhu atap Bali. PETG bertahan. Desain parametrik + STL + panduan cetak: [`enclosure/`](enclosure/). |

### Plus — Basic + sensor PM HM3301 (~USD 35–60)

Semua yang ada di Basic, ditambah:

| Jml | Komponen | Tempat | Catatan |
|---|---|---|---|
| 1 | Sensor PM2.5 laser Seeed Grove HM3301 v1.0 | Langsung dari Seeed, atau Tokopedia "Grove HM3301" | ~Rp 450–600k. Pendorong biaya terbesar kit ini. |
| (peningkatan) | Catu daya USB-C 5V/2A | Di mana saja | Kipas + laser HM3301 menarik arus puncak ~80 mA. Catu daya 1A yang cukup untuk Basic akan mengalami penurunan tegangan di bawah beban sensor PM. |

### Memilih di antara keduanya

**Basic** sudah cukup jika penerapannya di dalam ruangan (kamar kos, rumah tradisional, ruang kelas sekolah, lapak pasar), jika kasus penggunaannya adalah pemantauan jamur / habitat demam berdarah / tekanan panas / VOC dalam ruangan, atau jika anggaran lokakarya ketat — lebih banyak Basic = lebih banyak cakupan spasial.

**Plus** diperlukan untuk pemantauan kualitas udara luar ruangan (atap, kantor banjar, stasiun pesisir), untuk pertanyaan pembakaran padi dan polusi lalu lintas yang telah ditandai kampanye, atau untuk triangulasi gas+PM yang mengkarakterisasi *jenis* peristiwa polusi yang Anda lihat.

Untuk anggaran lokakarya 10 node sekitar ~USD 250, Anda dapat mengirim: 10 Basic, atau 4 Plus + 5 Basic, atau campuran apa pun. Strategi: pilih dulu lokasi penerapan berdasarkan matters-of-concern dari Fase 1, lalu pilih varian per lokasi.

**Catatan sumber pasokan untuk Bali:** HM3301 adalah pendorong biaya. Distributor Indonesia Seeed (Halo Robotics) menyediakannya tetapi markup-nya nyata. Untuk lokakarya yang memesan 5+ kit Plus, memesan langsung dari Seeed (Shenzhen → Denpasar) melalui jalur pengiriman Fab Lab Bali biasanya lebih murah daripada ritel. Anggarkan 3 minggu untuk pengiriman.

## Untuk apa data ini berguna — kasus penggunaan Bali

Nilai kit ini bukanlah pembacaannya — melainkan pembacaan yang ditafsirkan oleh orang-orang yang tinggal di suatu tempat dan bertindak atas apa yang mereka lihat. Berikut tampilan data untuk isu-isu yang benar-benar dilacak kampanye ini.

### Habitat nyamuk demam berdarah (Basic)

Aedes aegypti, vektor utama demam berdarah di Bali, berkembang biak secara optimal pada 25–30°C dan kelembapan relatif >70%. Kedua kondisi tersebut adalah keadaan default di dataran rendah Bali sepanjang sebagian besar tahun, itulah sebabnya demam berdarah bersifat endemik, bukan musiman seperti di tempat-tempat beriklim sedang.

Apa yang diberikan kit Basic bukanlah sebuah "alarm demam berdarah" — melainkan catatan hiperlokal tentang berapa jam suatu banjar, sekolah, atau kompleks kos tertentu menghabiskan waktu dalam kondisi optimal untuk perkembangbiakan nyamuk. Ditumpangkan dengan data kasus Dinas Kesehatan, pertanyaannya bergeser dari "berapa banyak kasus demam berdarah bulan ini" menjadi "iklim mikro mana yang memusatkan risiko, dan intervensi mana (jadwal fogging, pembersihan wadah air) yang benar-benar memutus siklus." Sebagian besar surveilans demam berdarah regional tertinggal dari pelaporan kasus selama 2–4 minggu; sinyal lingkungan bersifat waktu-nyata.

### Jamur dan kesehatan pernapasan (Basic)

Jamur tumbuh ketika RH berada di atas ~60% dengan suhu 20–30°C — kondisi default dalam ruangan di Bali sepanjang musim hujan Oktober–April di sebagian besar hunian non-AC. Spora jamur adalah pemicu asma dan rinitis alergi yang terdokumentasi, terutama bagi anak-anak.

Kit Basic memungkinkan seorang warga melihat, dengan data mereka sendiri, bahwa kamar tidur mereka kemarin menghabiskan 14 jam dalam kondisi yang mendukung pertumbuhan jamur. Itu dapat ditindaklanjuti: buka jendela pada sore hari ketika kelembapan turun, jalankan dehumidifier kecil, dorong pemilik rumah soal ventilasi. "Dokter saya bilang saya kena asma" sulit ditindaklanjuti. "Kamar tidur Anda telah berada di RH 78% selama seminggu terakhir" lebih mudah.

### Tekanan panas dan pekerjaan luar ruangan (Basic)

Tekanan panas bukan hanya soal suhu — melainkan suhu bola basah (wet-bulb), sebuah fungsi dari T dan RH bersama-sama. Pekerja luar ruangan di Bali (pemeliharaan banjar, konstruksi, pertanian, juru masak upacara) secara rutin mencapai kombinasi berbahaya pada sore hari musim kemarau. Suhu bola basah di atas 30°C secara signifikan mengganggu kerja fisik; di atas 33°C berbahaya dalam hitungan jam.

Kit Basic dapat menghitung indeks panas untuk lokasi penerapan mana pun. Dipasang di dekat lokasi konstruksi, pasar, atau titik kumpul banjar, kit ini memberi pekerja dan pemberi kerja mereka sinyal bersama: "lokasi ini berada dalam kondisi tekanan panas hari ini, jadwalkan pekerjaan berat lebih awal atau istirahat di tempat teduh."

### VOC dalam ruangan dan paparan pembakaran (Basic)

Sensor gas BME680 merespons senyawa organik volatil — asap obat nyamuk bakar, emisi memasak dengan minyak tanah, bahan kimia pembersih, pelarut cat, asap rokok, penguapan kapsaisin dari menggoreng sambal. Penelitian terdokumentasi (Liu dkk., 2003) menemukan bahwa satu obat nyamuk bakar semalaman melepaskan massa PM2.5 yang sebanding dengan membakar ~75–100 batang rokok, beserta formaldehida dalam jumlah substansial.

Kit Basic mempublikasikan resistansi gas mentah dalam ohm; semakin rendah = semakin banyak VOC. Sebuah node di dapur atau kamar tidur menunjukkan pola — "resistansi gas Anda turun setiap malam antara pukul 21.00 dan 05.00 karena obat nyamuk bakar." Itu adalah percakapan tentang alternatif (kelambu, vaporizer listrik, ventilasi), bukan kekhawatiran samar tentang "udara dalam ruangan".

### PM luar ruangan — pembakaran padi, lalu lintas, konstruksi (hanya Plus)

Periode kualitas udara luar ruangan terburuk di Bali terkait dengan pembakaran tunggul padi, biasanya Juli–Oktober ketika ladang pascapanen dibakar di seluruh Tabanan, Gianyar, dan Klungkung. Lonjakan PM2.5 sebesar 200–400 µg/m³ di hilir ladang yang terbakar bukanlah hal yang langka. Sensor gas kit Basic melihat ini sebagai sinyal VOC, tetapi konsentrasi partikulat — bagian dengan dampak kesehatan kardiopulmoner yang terdokumentasi — membutuhkan HM3301.

Kit Plus juga menangkap koridor lalu lintas (persimpangan Canggu, Seminyak, Kuta saat jam sibuk), debu konstruksi (lonjakan vila Ubud, pembangunan tepi pantai barat daya), dan gas buang diesel pesisir (lalu lintas perahu wisata di Sanur, Padangbai, Amed). Untuk penerapan apa pun yang pertanyaannya adalah PM luar ruangan, Plus diwajibkan.

### Triangulasi peristiwa pembakaran (Plus)

Ini adalah kemampuan analitis yang hanya Anda dapatkan dengan menjalankan gas dan PM dalam node yang sama. Peristiwa kualitas udara meninggalkan tanda tangan yang berbeda:

- **Resistansi gas turun DAN PM melonjak** = pembakaran. Membakar sampah, asap kayu, gas buang kendaraan. Keduanya dilepaskan bersamaan.
- **PM melonjak, gas stabil** = debu. Konstruksi, debu jalan yang terangkat lalu lintas, abu tanpa pembakaran aktif. Tanpa VOC.
- **Resistansi gas turun, PM stabil** = uap. Pelarut, cat, bahan bakar, produk pembersih. VOC tanpa partikulat pembakaran.

Analisis tanda tangan ini memungkinkan kampanye mengatakan lebih dari sekadar "udaranya buruk" — kampanye bisa mengatakan *jenis* keburukannya, yang memiliki implikasi kebijakan berbeda. Temuan "debu konstruksi" mendorong satu percakapan (penyemprotan air lokasi, batasan jam kerja); temuan "peristiwa pembakaran" mendorong yang lain (jadwal pengumpulan sampah, aturan pembakaran tingkat banjar); temuan "uap" mendorong yang ketiga (ventilasi tempat kerja, penyimpanan bahan kimia rumah tangga).

Triangulasi ini adalah kemampuan khusus kit Plus dan keluaran penelitian yang berarti melampaui apa yang diukur SCK resmi — SCK memiliki eCO₂ melalui CCS811 tetapi tidak memiliki resistansi gas mentah.

## Di mana ini cocok — tier sensor kampanye

DIY node bukanlah instrumen mandiri; ia adalah satu tier dari jaringan penginderaan multi-kesetiaan. Making Sense Bali dibangun (atau bertujuan untuk dibangun) dalam empat tier, setiap tier yang lebih rendah dirujuk terhadap yang di atasnya. Rantai rujukan itulah yang memisahkan "kampanye mempublikasikan dasbor" dari "kampanye mempublikasikan data yang dikutip pemerintah daerah dalam keputusan kebijakan." Tanpa itu, setiap pembacaan membawa tanda bintang; dengan itu, kampanye dapat mempublikasikan interval kepercayaan, menurunkan jumlah peristiwa, dan menjamin agregat musiman.

| Tier | Perangkat keras | Biaya | Peran | Jumlah tipikal |
|---|---|---|---|---|
| **0 — Referensi** | BAM-1020, Met One E-BAM, Aeroqual AQM 65, atau stasiun BMKG / Udayana yang dihosting | USD 5.000–25.000+ | Kebenaran dasar (ground truth). Tingkat regulasi atau mendekati regulasi. Jangkar kalibrasi untuk segala sesuatu di bawahnya. | 1 per bioregion, dihosting oleh mitra institusional |
| **1 — Smart Citizen Kit 2.1** | SCK resmi dari [smartcitizen.me](https://smartcitizen.me/store) | ~USD 150 | Tulang punggung multi-parameter tepercaya (PM, eCO₂, kebisingan, iklim, cahaya). Firmware teruji. | 3–10, dipasang oleh tim kampanye |
| **2 — DIY Plus** | Repo ini, dengan HM3301 | ~USD 35–60 | Kepadatan spasial di lokasi luar ruangan. Metrik PM + iklim yang sama dengan SCK tetapi kesetiaan lebih rendah. | 10–50, dipasang oleh peserta setelah lokakarya |
| **3 — DIY Basic** | Repo ini, tanpa HM3301 | ~USD 15–25 | Jangkauan maksimum. Kasus penggunaan AQ dalam ruangan, iklim, VOC, jamur / demam berdarah / panas / pembakaran dalam ruangan. | Banyak — sekolah, kos, banjar, rumah perorangan |

### Rantai kalibrasi

Setiap tier dikalibrasi terhadap tier di atasnya. **Koreksi berada di lapisan pemrosesan dasbor (`data.js`, Cloudflare Worker), bukan di firmware** — koreksi firmware tidak dapat diaudit, koreksi dasbor diberi versi dan dapat direproduksi.

**Tier 0 → Tier 1.** BAM-1020 langsung merupakan pembelian USD 25rb plus pemeliharaan tahunan, yang tidak akan ditanggung kampanye sendiri. Jalur pragmatis untuk Bali adalah kemitraan dengan **BMKG (Stasiun Klimatologi Bali, Sanglah)** untuk ko-lokasi di stasiun iklim referensi mereka yang sudah ada, atau dengan **Fakultas Teknik atau Fakultas Kesehatan Masyarakat Universitas Udayana** untuk menghosting instrumen tier-menengah seperti Aeroqual AQM 65 (~USD 8–15rb, tangguh dalam kelembapan tropis, pemeliharaan lebih rendah daripada BAM). Kedua rute itu adalah percakapan, bukan pengadaan.

**Tier 1 → Tier 2.** SCK resmi diko-lokasikan dengan referensi Tier 0 selama seminggu setiap musim (kemarau, hujan, peralihan). Dasbor menurunkan faktor koreksi per SCK per musim. Setelah sprint kalibrasi, SCK dipasang di seluruh bioregion sebagai tulang punggung tepercaya.

**Tier 2 → Tier 1.** Node DIY Plus diko-lokasikan dengan SCK terkalibrasi selama ~5 hari pada penerapan pertamanya. Faktor koreksi diturunkan untuk HM3301 node Plus terhadap SCK lokal. Sejak saat itu data Plus bersifat "terkoreksi-SCK" — dapat digunakan untuk analisis tren dan deteksi peristiwa, ditandai di dasbor sebagai turunan, bukan primer.

**Tier 3 → Tier 1.** Node DIY Basic tidak membawa PM, jadi kalibrasi PM tidak berlaku. Suhu dan kelembapan mendapat pemeriksaan kewajaran terhadap SCK terdekat; resistansi gas adalah sinyal relatif yang tidak memerlukan kalibrasi absolut (semakin rendah = semakin banyak VOC tetap benar terlepas dari referensinya).

### Seperti apa jaringan yang realistis

Untuk bioregion seukuran Bali selatan:

- 0–1 instrumen Tier 0 (tergantung kemitraan)
- 5–8 SCK Tier 1 di lokasi luar ruangan strategis (kantor banjar, Fab Lab mitra, node atap di iklim mikro berbeda)
- 20–40 DIY Plus Tier 2 di lokasi komunitas luar ruangan (sekolah, warung dekat jalan, tepi pantai)
- 50+ DIY Basic Tier 3 dalam ruangan (kamar kos, ruang kelas, rumah perorangan)

Itu sekitar ~75–100 node dengan biaya kira-kira setara 10–15 SCK saja. Data tetap bersandar pada Tier 0/1 untuk kredibilitas, tetapi resolusi spasiallah yang membuat dasbor berguna — Anda dapat melihat *lingkungan mana* yang membakar sampah pada Rabu malam, bukan sekadar bahwa "Bali selatan mengalami PM yang meningkat."

### Langkah pertama sebelum jaringan menjadi lebih besar

Tiga tindakan konkret, dalam urutan kepentingannya:

1. **Buka percakapan BMKG sekarang**, sebelum kampanye membutuhkan data referensi. BMKG Stasiun Klimatologi di Sanglah mengoperasikan instrumen iklim tingkat referensi. Permintaannya kecil — bisakah kampanye meng-ko-lokasikan satu atau dua SCK di lokasi BMKG selama satu minggu setiap musim? Rantai ko-lokasi tunggal itu membuka kredibilitas untuk seluruh jaringan hilir.
2. **Tetapkan satu SCK sebagai "referensi dalam jaringan" kampanye** bahkan sebelum Tier 0 tersedia. Pilih yang paling cermat dipelihara dan paling jarang dipindahkan. Pembacaannya menjadi jembatan hingga referensi yang sebenarnya ada.
3. **Jalankan lokakarya DIY pertama hanya setelah langkah 2** sehingga node Plus memiliki sesuatu untuk diko-lokasikan. Sebuah DIY Plus yang dipasang tanpa jalur referensi adalah node yang tidak dapat dipertahankan kampanye jika ditanya.

Faktor kalibrasi itu sendiri — kapan diambil, apa nilainya, bagaimana diterapkan di dasbor — berada di `docs/calibration.md` (akan ditulis; ini adalah dokumen yang paling dapat ditindaklanjuti berikutnya setelah README ini).

## Pengabelan

Skema di bawah menunjukkan pengabelan **Plus**. Untuk **Basic**, lewati separuh kanan — baris HM3301 pada tabel — dan hanya kabeli BME680.

Kedua sensor berada pada bus I²C yang sama ketika keduanya hadir. Empat kabel dari XIAO menuju kedua sensor secara paralel; daya berbeda (5V untuk kipas HM3301, 3.3V untuk logika BME680).

![Skema — XIAO ESP32-S3 + BME680 + HM3301 pada bus I²C bersama](schematic.svg)

| Pin XIAO | Label XIAO | Menuju | Net |
|---|---|---|---|
| 5V | `5V` | HM3301 VCC | Daya 5V (kipas + laser) |
| 3.3V | `3V3` | BME680 VCC | Daya 3.3V (logika) |
| GND | `GND` | HM3301 GND **dan** BME680 GND | Ground bersama |
| GPIO5 | `D4` | HM3301 SDA **dan** BME680 SDA | Data I²C (bersama) |
| GPIO6 | `D5` | HM3301 SCL **dan** BME680 SCL | Clock I²C (bersama) |

Breakout BME680 mengekspos pin SDO dan CS. Biarkan SDO mengambang (atau ikat ke GND) untuk alamat I²C `0x76`. Biarkan CS ditarik tinggi (sebagian besar breakout menangani ini secara internal). Abaikan pin SPI sepenuhnya.

**Alamat I²C pada bus ini:**

- BME680 → `0x76` (atau `0x77` jika Anda mengikat SDO ke 3V3 — hanya relevan jika Anda menempatkan dua BME pada satu bus)
- HM3301 → `0x40`

Jika Anda menjalankan `i2cdetect` pada laptop Linux atau ingin sebuah sketch, pindai bus terlebih dahulu untuk memastikan kedua alamat muncul. Jika hanya satu yang muncul, periksa daya, lalu periksa resistor pull-up (XIAO memiliki pull-up lemah internal tetapi kabel Grove HM3301 mengasumsikan adanya pull-up eksternal di suatu tempat pada bus — biasanya breakout BME680 menyediakannya).

## Platform Smart Citizen — daftarkan perangkat

Sebelum mem-flash, siapkan perangkat di Smart Citizen:

1. Masuk di [smartcitizen.me](https://smartcitizen.me/).
2. Tambahkan perangkat baru. Pilih **"Other devices"** → perangkat keras khusus. Beri nama seperti `Bali DIY Node — [location]`.
3. Tambahkan sensor yang akan Anda publikasikan. Untuk kit ini:

   **Kedua varian:**
   - **Temperature** (°C) — BME680
   - **Humidity** (%) — BME680
   - **Pressure** (hPa) — BME680 *(opsional, biarkan ID firmware tetap 0 untuk melewatinya)*
   - **Gas resistance** (Ω, mentah) — indikator VOC BME680
   - **IAQ** (indeks, 0–500) — BME680, dihitung di perangkat (perkiraan terbuka)

   **Hanya varian Plus — tambahkan ini juga:**
   - **PM1** (µg/m³) — HM3301
   - **PM2.5** (µg/m³) — HM3301
   - **PM10** (µg/m³) — HM3301

   Untuk kit Basic, cukup biarkan ID sensor PM tetap 0 dalam konfigurasi firmware; langkah publikasi melewati sensor apa pun dengan ID 0.
4. Atur lokasi ke koordinat penerapan (bukan geolokasi IP laptop Anda — atap yang sebenarnya).
5. Dari halaman dasbor perangkat, salin **token perangkat** (digunakan untuk autentikasi MQTT) ke dalam firmware. Anda tidak perlu menyalin ID sensor — firmware sudah menggunakan ID global-catalog Smart Citizen (233–241), dan platform memetakannya secara otomatis ke perangkat Anda pada publikasi pertama.

Token perangkat adalah yang mengautentikasi node terhadap platform. Token dapat dicabut dari dasbor jika sebuah kit hilang — perlakukan seperti kata sandi.

## Firmware

Dua sketch dalam repo ini. **Flash sketch pengujian terlebih dahulu.**

### Sketch pengujian — alat bring-up, tanpa platform

[`firmware/diy_node_test/diy_node_test.ino`](firmware/diy_node_test/diy_node_test.ino) adalah sketch khusus verifikasi. Ia memindai bus I²C, menyelidiki kedua sensor, dan mencetak pembacaan ke Serial Monitor setiap 5 detik. **Tidak perlu WiFi, MQTT, atau akun Smart Citizen.** Inilah yang di-flash peserta lokakarya segera setelah menyolder — jika angka yang masuk akal muncul di Serial Monitor, perangkat keras berfungsi dan mereka dapat melanjutkan ke firmware lengkap dengan percaya diri. Jika tidak, pemindaian I²C dan keluaran penyelidikan per-sensor dari sketch pengujian biasanya langsung menunjuk pada masalah pengabelan atau daya.

Berfungsi untuk kit Basic (BME680 saja) maupun Plus (BME680 + HM3301) — sketch pengujian mendeteksi sensor mana yang hadir dan hanya mencetak apa yang ditemukannya.

### Sketch produksi — mempublikasikan ke Smart Citizen

**Sketch yang sama menjalankan Basic dan Plus.** Untuk Basic, init HM3301 saat boot mengembalikan "NOT FOUND", firmware mencatatnya sekali, dan melewati publikasi PM untuk setiap siklus. Tanpa perubahan kode — cukup jangan sambungkan HM3301 dan biarkan ketiga ID sensornya tetap 0 dalam blok konfigurasi.

Sketch firmware produksi ada di [`firmware/diy_node/diy_node.ino`](firmware/diy_node/diy_node.ino). Ia:

- Menghidupkan I²C dan menyelidiki kedua sensor saat boot
- Terhubung ke WiFi dan menyinkronkan jam melalui NTP (platform memerlukan stempel waktu `recorded_at` yang sebenarnya)
- Membaca suhu, kelembapan, PM1, PM2.5, PM10 setiap 60 detik
- Mempublikasikan satu pesan MQTT per siklus ke `device/sck/{DEVICE_TOKEN}/readings` pada `mqtt.smartcitizen.me:8883` (TLS)
- Bentuk payload cocok dengan format yang didokumentasikan platform (`data` → `recorded_at` + `sensors[]`)

Pustaka Arduino yang diperlukan (instal melalui Library Manager):

- `Adafruit BME680 Library` (bergantung pada `Adafruit Unified Sensor`) — catatan: **bukan** pustaka BME280
- `PubSubClient` oleh Nick O'Leary (MQTT) — hanya dibutuhkan oleh sketch produksi
- `ArduinoJson` v7.x — hanya dibutuhkan oleh sketch produksi

HM3301 dibaca langsung melalui I²C — tidak perlu pustaka eksternal. Lihat catatan di bawah tentang alasannya.

Board: instal paket **esp32 by Espressif Systems** di board manager Arduino IDE, lalu pilih **XIAO_ESP32S3**.

**Mengapa tidak ada pustaka Seeed_HM330X?** Driver Arduino HM3301 dari Seeed ditulis terhadap toolchain Arduino AVR lama dan menggunakan alias tipe non-standar `u8` / `u16` / `u32` tanpa mendefinisikannya. Core arduino-esp32 modern tidak menyediakan typedef tersebut, sehingga berkas `.cpp` pustaka itu sendiri gagal dikompilasi dengan `error: 'u32' has not been declared`. Sebuah shim typedef dalam sketch tidak dapat memperbaiki ini — `.cpp` pustaka itu adalah unit terjemahan terpisah.

Daripada menambal pustaka vendor di setiap mesin pengembang, kedua sketch dalam repo ini berbicara ke HM3301 **langsung melalui I²C**. Cukup `Wire.write(0x88)` sekali saat boot untuk memilih mode I²C, lalu `Wire.requestFrom(0x40, 29)` untuk setiap bingkai data 29-byte. Tata letak bingkai (sesuai datasheet HM-3300/3600) didokumentasikan inline di atas fungsi `readHM3301` — PM1/PM2.5/PM10 atmosferik berada di buf[10..15], plus checksum di buf[28] yang kami verifikasi sebelum mempercayai pembacaan.

Total biaya: ~15 baris kode, nol ketergantungan eksternal untuk sensor ini.

Edit blok konfigurasi di bagian atas `diy_node.ino`. Anda hanya mengatur tiga nilai, semuanya ditandai dengan placeholder `YOUR_*`: `WIFI_SSID`, `WIFI_PASSWORD`, dan `SC_DEVICE_TOKEN` (dari halaman perangkat Anda). ID sensor (233–241) adalah ID global-catalog Smart Citizen dan sudah terisi — biarkan apa adanya; untuk kit Basic, atur ketiga ID PM (233/234/235) ke 0 untuk melewatinya. Flash, buka serial monitor pada 115200 baud, amati urutan koneksi. Dalam beberapa menit perangkat seharusnya muncul "online" di smartcitizen.me dengan pembacaan mengalir.

Jika pembacaan tidak muncul: periksa bahwa ID sensor di firmware sama persis dengan yang ada di halaman perangkat SC (bersifat numerik dan per-perangkat), dan bahwa perangkat belum ditandai "private" — public adalah default-nya.

## Jalur prototipe

Jangan lewati langkah. Masing-masing mengisolasi kelas bug yang berbeda.

**Tahap 1 — Breadboard, bertenaga USB, di lokakarya Anda. Sketch pengujian dulu, lalu produksi.** Kabeli dengan jumper. **Flash `diy_node_test.ino` terlebih dahulu** dan konfirmasi pembacaan yang masuk akal di Serial Monitor — ini membuktikan perangkat keras berfungsi secara terisolasi, tanpa perlu penyiapan cloud. Hanya setelah itu, beralih ke `diy_node.ino`, isi kredensial WiFi dan token perangkat / ID sensor Smart Citizen, lalu konfirmasi perangkat muncul di smartcitizen.me. Membagi bring-up dengan cara ini mengisolasi bug perangkat keras dari bug platform — jika keduanya berfungsi secara berurutan, Anda solid.

**Tahap 2 — Perfboard, bertenaga USB, dalam ruangan.** Solder ke papan matriks 4×6 cm (ukuran yang diasumsikan wadah cetakan). Gunakan **header female** untuk XIAO dan BME680 — keduanya adalah bagian yang paling mungkin mati akibat kesalahan pengabelan atau lonjakan, dan Anda ingin menggantinya tanpa menyolder ulang. Untuk rakitan Plus, solder empat kabel ke test pad pembawa HM3301 alih-alih menggunakan kabel Grove — wadah memasang modul dengan posisi soket menghadap ke bawah (lihat `enclosure/`). Jalankan selama 48 jam di dalam ruangan di samping referensi yang diketahui (aplikasi kualitas udara di ponsel yang diarahkan ke jendela cukup untuk pemeriksaan kewajaran). Konfirmasi pembacaan stabil, perangkat tidak me-reset, dan MQTT terhubung kembali setelah WiFi terputus.

**Tahap 3 — Wadah, dipasang.** Cetak 3D wadah PETG dari [`enclosure/`](enclosure/) — si "buah pinus" (pine cone): kulit bersisik biomimetik yang sekaligus menjadi peluruh hujan dan ventilasi, Grove HM3301 berdiri vertikal di balik kisi-kisi berjeruji, lokasi komponen ditandai oleh garis tapak cetakan alih-alih teks, dan bilik LiPo opsional. Bebas-penyangga, sambungan terkunci-sekrup, mencakup kedua varian; keempat desain sebelumnya berada di `enclosure/archive/` dengan penafian. Alasan desain dan panduan perakitan ada di folder itu; catatan penerapan Bali di bawah tetap berlaku. Pasang di tempat teduh, jangan pernah di bawah sinar matahari langsung. Beri daya melalui catu daya USB tahan cuaca atau panel surya 5V + konverter buck (yang terakhir adalah proyek terpisah; mulailah dengan daya dinding).

**Tahap 4 — PCB cetakan (opsional, untuk produksi batch).** Setelah sebuah desain berjalan andal di tahap 3 selama beberapa bulan, tata letak papan pembawa khusus di KiCad dan milling pada printer PCB Fab Lab Bali. Ini adalah tahap "kami berkomitmen memasang 20 unit ini", bukan rakitan pertama.

## Catatan penerapan Bali

Alasan kampanye ini ada adalah datanya, bukan firmware-nya. Tanggapi bagian ini dengan serius.

**Kelembapan.** Bali memiliki kelembapan relatif 80%+ sepanjang sebagian besar tahun. Papan tanpa pelapis berkarat dalam 6–12 bulan. Setelah tahap 2, **lapisi sisi tersolder perfboard dengan pelapis konformal silikon** (MG Chemicals 422B atau serupa — tersedia di Singapura, dikirim ke Bali). Tutupi (mask) bukaan sensor dan konektor USB-C sebelum menyemprot. Port kelembapan BME680 dan saluran masuk udara HM3301 harus tetap tidak tertutup. Langkah pelapisan konformal saja kira-kira menggandakan masa pakai penerapan.

**Penyimpangan sensor PM.** Sensor turunan Plantower (HM3301 termasuk keluarga ini) menyimpang naik seiring waktu dalam kelembapan tinggi — pembacaan merangkak 30–50% lebih tinggi setelah 12–18 bulan dalam kondisi Bali. **Firmware tidak mengompensasi ini.** Untuk kit lokakarya, itu kompromi yang dapat diterima. Untuk data yang digunakan kampanye dalam percakapan kebijakan, **ko-lokasikan node DIY dengan SCK resmi atau referensi yang diketahui selama setidaknya seminggu**, turunkan faktor koreksi, dan terapkan di lapisan pemrosesan dasbor (bukan di firmware — koreksi berada di pipeline data). Ini adalah pola yang sama yang digunakan Sensor.Community untuk jaringan biaya-rendah mereka.

**Burn-in sensor gas.** Sensor gas oksida-logam BME680 memerlukan ~24 jam operasi berkelanjutan sebelum pembacaannya stabil — pemanas membutuhkan waktu untuk membakar kontaminan permukaan dari proses manufaktur. Jangan percayai data resistansi gas hari pertama. Setelah itu, harapkan penyimpangan naik yang lambat selama berbulan-bulan seiring penuaan elemen sensor — **tren** lebih penting daripada nilai absolut. Untuk Bali, sinyal gas yang paling berguna adalah korelasi: penurunan resistansi gas yang bersamaan dengan lonjakan PM2.5 menunjuk pada pembakaran (membakar sampah, asap kayu); penurunan tanpa PM menunjuk pada pelarut atau uap bahan bakar.

**Wadah.** Sinar matahari + hujan Bali akan menghancurkan node yang terwadah buruk dalam hitungan minggu. Saluran masuk udara HM3301 harus menghadap ke bawah atau ke samping (jangan pernah ke atas — hujan) dan harus dilindungi dari masuknya serangga langsung (jaring stainless halus di atas saluran masuk membantu, tetapi periksa penumpukan penyumbatan setiap bulan). Sensor kelembapan BME680 membutuhkan aliran udara tetapi bukan air — pendekatan berkisi-kisi seperti Stevenson screen adalah pola yang tepat. Jangan memasang di atap seng di bawah sinar matahari langsung tanpa isolasi termal; BME680 akan membaca 15°C lebih tinggi.

**WiFi.** Keandalan WiFi Bali berkisar dari "baik-baik saja" hingga "kabel ke Singapura putus hari ini." Firmware harus terhubung kembali saat WiFi hilang dan menjaga perangkat tetap berjalan secara lokal bahkan saat offline. Firmware saat ini membuang pembacaan saat offline — menambahkan buffer kecil pembacaan yang belum terkirim adalah peningkatan yang diketahui (TODO).

**Daya.** Sebagian besar penerapan akan bertenaga dinding melalui catu daya 5V/2A. Kehilangan daya adalah penyebab paling umum "node menjadi senyap" — peserta mencabutnya untuk mengisi daya ponsel mereka. Pembingkaian lokakarya membantu: ini adalah bagian dari data, beri label catu daya dengan jelas `Smart Citizen — do not unplug`.

## Format lokakarya (disarankan)

Lokakarya setengah hari di Fab Lab Bali, 6–10 peserta, dua perakit per kit (satu menyolder, satu mem-flash; bergantian).

- **Jam 1** — pembingkaian kampanye (mengapa kita mengukur? apa kepentingan sebuah banjar dalam hal ini?), tur dasbor, lihat pembacaan yang ada bersama-sama
- **Jam 2** — perakitan kit (solder ke perfboard, kabeli, belum ada firmware)
- **Jam 3** — flash firmware, konfigurasi WiFi, pendaftaran perangkat di smartcitizen.me, pembacaan pertama
- **Jam 4** — keputusan wadah (di mana ini akan ditempatkan? menghadap apa? siapa yang mencolokkannya kembali jika jatuh dari dinding?)

Apa yang dibawa pulang peserta: sebuah node yang berfungsi, wadah cetakan, catu daya berlabel, dan selembar ringkasan cetak berisi URL perangkat di smartcitizen.me dan nomor WhatsApp kampanye untuk dihubungi jika berhenti berfungsi.

Apa yang diperoleh kampanye dari lokakarya: sebuah titik baru di dasbor, izin peserta untuk mempublikasikan, dan seseorang yang bertanggung jawab dengan nama jelas di lokasi penerapan.

## Lisensi

Sama seperti repo kampanye induk: kode MIT, dokumentasi CC-BY-SA 4.0. Fork untuk Making Sense [tempat Anda] dan beri tahu kami apa yang berubah.
