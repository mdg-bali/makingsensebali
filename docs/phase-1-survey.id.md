[English](phase-1-survey.md) · **Bahasa Indonesia** · [Español](phase-1-survey.es.md)

# Fase 1 — Survei hal-hal yang menjadi perhatian

Panduan desain, metodologi, dan operasional untuk survei komunitas Fase 1 dalam kampanye Making Sense [tempat]. Mendokumentasikan survei Bali yang sedang berjalan sebagai desain acuan, lengkap dengan usulan penyempurnaan untuk iterasi berikutnya.

> **Formulir aktif**: [airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form)
> **Base**: `appwQPP3ywSp4uu25` · Tabel: `Matters of Concern`

---

## Mengapa survei Fase 1

Making Sense [tempat] tidak dimulai dengan memasang sensor atau menulis siaran pers tentang kualitas udara. Ia dimulai dengan menanyakan kepada warga isu lingkungan apa yang *mereka* perhatikan dalam kehidupan sehari-hari. Pijakan ini lebih penting daripada yang mungkin terlihat.

Garis keturunan metodologisnya adalah **[Making Sense](https://making-sense.eu/)** (EU Horizon 2020, 2015–2017), yang mengadaptasi kerangka "matters of concern" dari Bruno Latour menjadi protokol citizen-sensing partisipatif. Perbedaan intinya adalah antara *matters of fact* (apa yang diukur sains — PM2.5, dB, ppm) dan *matters of concern* (apa yang benar-benar dikhawatirkan orang — asap yang membangunkan mereka, air yang terasa aneh, kebisingan yang membuat anak-anak mereka menangis).

Sebuah kampanye penginderaan yang dimulai dari matters of fact membangun sebuah instrumen. Sebuah kampanye penginderaan yang dimulai dari matters of concern membangun sebuah komunitas. Yang pertama adalah alat. Yang kedua memiliki legitimasi politik dan pijakan untuk benar-benar mengubah sesuatu.

Fase 1 menghasilkan tiga hal:

1. **Gambaran tentang perhatian yang didefinisikan warga** — perhatian apa yang muncul, di mana, siapa yang terdampak, bukti apa yang sudah ada
2. **Prioritas otentik untuk Fase 2** — lingkungan mana yang harus dideteksi lebih dulu, kategori mana yang harus ditonjolkan oleh bot laporan, organisasi mitra mana yang harus diundang
3. **Sebuah konstituensi** — daftar warga yang berpartisipasi dan ingin terlibat lebih jauh (menjadi tuan rumah sensor, mengirim laporan, menerjemahkan, menghadiri lokakarya)

Lewati Fase 1 dan Anda telah membalik urutannya: Anda memberi tahu warga apa yang seharusnya mereka pedulikan berdasarkan apa yang mudah diukur. Itu sebuah proyek riset, bukan kampanye komunitas.

---

## Prinsip desain: satu baris = satu perhatian

Survei Bali disusun sedemikian rupa sehingga **satu kiriman formulir mewakili satu perhatian**, bukan satu responden. Seorang warga dengan tiga perhatian lingkungan mengirimkan formulir tiga kali — satu kali per perhatian. Setiap baris dalam Airtable menangkap narasi lengkap untuk perhatian tertentu itu: apa isunya, di mana, siapa yang terdampak, bukti apa yang ada, apa yang akan berubah jika hal itu dibuat terlihat.

Ini adalah pilihan yang disengaja dengan tiga manfaat:

- **Detail per perhatian lebih kaya** dibandingkan yang muat dalam grid multi-pilihan
- **Analisis per perhatian menjadi alami** — kelompokkan berdasarkan kategori, lokasi, atau "paling terdampak" tanpa membongkar data bersarang
- **Responden yang peduli pada satu isu dapat mengirim dengan cepat**; mereka yang punya beberapa isu tidak dipaksa masuk ke satu jawaban yang terbatas

Biayanya adalah responden yang mengirimkan beberapa perhatian harus memasukkan informasi identitas mereka (nama, email, dll.) berkali-kali. Bagian kontak yang opsional membuat ini tetap singkat, dan kebanyakan responden tetap anonim.

---

## Survei Bali saat ini

### Bidang isian, dalam urutan formulir

| # | Bidang | Tipe | Wajib | Tujuan |
|---|---|---|---|---|
| 1 | **Concern** | Teks satu baris | Ya | Ringkasan satu baris — apa isunya? Menjadi pengenal utama baris tersebut. |
| 2 | **Categories** | Multi-pilihan | Ya | Kategori lingkungan mana atau kategori-kategori mana yang sesuai dengan ini |
| 3 | **Description** | Teks panjang | Opsional | Narasinya — apa yang secara spesifik Anda amati, kapan, seperti apa tampilan/suara/baunya, dengan kata-kata Anda sendiri |
| 4 | **Location** | Teks panjang | Opsional | Di mana hal itu terjadi — lingkungan, jalan, pantai, sekolah, waktu dalam sehari jika relevan |
| 5 | **Most affected** | Multi-pilihan | Opsional | Siapa yang paling terdampak oleh isu ini |
| 6 | **Existing evidence** | Teks panjang | Opsional | Bukti apa yang sudah ada — pengamatan sendiri, laporan dari orang lain, berita, data resmi |
| 7 | **What would change** | Teks panjang | Opsional | Teori perubahan — apa yang akan berubah jika data membuat hal ini terlihat, dan kepada siapa data itu seharusnya diberikan |
| 8 | **Willing to participate** | Multi-pilihan | Opsional | Bagaimana responden ingin terlibat lebih jauh (tuan rumah sensor, pelapor, lokakarya, penerjemahan, penjangkauan, sekadar diberi info, menolak) |
| 9 | **Preferred languages** | Multi-pilihan | Opsional | Bahasa mana yang sebaiknya didukung kampanye |
| 10 | **Name** | Teks satu baris | Opsional | Kosongkan untuk tetap anonim |
| 11 | **Email** | Email | Opsional | Hanya jika dihubungi tentang langkah berikutnya |
| 12 | **Phone / WhatsApp** | Telepon | Opsional | Hanya digunakan jika responden meminta tindak lanjut |
| 13 | **Affiliation** | Teks satu baris | Opsional | Sekolah, LSM, fab lab, perkumpulan warga, organisasi |

Bidang khusus internal (tidak ada dalam formulir, diisi oleh tim setelah pengiriman):

- **Status** — status peninjauan: New → Reviewed → Contacted → Workshop invited → Closed / archived (atau Spam / invalid)
- **Submitted at** — otomatis dari formulir
- **Internal notes** — catatan triase, tindakan tindak lanjut, penugasan kontak

### Opsi pilihan sebagaimana diterapkan (Bali)

**Categories** — Burning waste · Air quality · Water · Noise · Heat & humidity · Plastic & solid waste · Soil & agriculture · Light pollution · Other

**Most affected** — Me personally · My family · Children / students · Elderly / vulnerable people · Workers · Neighbors / community · Animals / wildlife · Visitors / tourists · Other

**Willing to participate** — Host a sensor · Share reports via the bot · Attend workshops · Translate / localize · Connect us to my school / org · Just keep me informed · Prefer not to participate further

**Preferred languages** — Bahasa Indonesia · English · Bahasa Bali · Other

**Status (internal)** — New · Reviewed · Contacted · Workshop invited · Closed / archived · Spam / invalid

---

## Rasional — mengapa bidang-bidang ini, dalam urutan ini

Formulir diurutkan untuk menekan tingkat pengabaian: pertanyaan yang mudah / paling penting muncul lebih dulu, pertanyaan yang opsional / pribadi muncul terakhir. Seorang warga yang hanya mengisi tiga bidang pertama (Concern, Categories, Description) tetap memberi kampanye data yang berguna.

- **Concern lebih dulu** — ringkasan satu baris memaksa responden mengartikulasikan apa yang mereka laporkan sebelum masuk ke detail. Berfungsi sebagai data sekaligus klarifikasi diri.
- **Categories kedua** — taksonomi terstruktur untuk analisis di tahap berikutnya. Opsi "Other" menjaganya tetap terbuka.
- **Description, Location, Most affected** — segitiga *apa / di mana / siapa*. Semuanya opsional secara individual sehingga respons sebagian tetap berguna.
- **Existing evidence** — sinyal penghormatan. Pertanyaan ini mengandaikan warga sudah tahu banyak hal; kampanye tidak dimulai dari nol. Bagian ini sering menghasilkan teks paling kaya, dengan orang menyebutkan sumber, tanggal, dan laporan sebelumnya.
- **What would change** — pemantik teori perubahan. Yang patut dicatat, *tidak ada katalog intervensi terstruktur* — ini disengaja. Warga memberi tahu kami dengan kata-kata mereka sendiri apa yang menurut mereka akan membantu dan kepada siapa data seharusnya diberikan. Opsi terstruktur akan mengarahkan mereka pada asumsi yang sudah kami miliki.
- **Willing to participate** — jalan masuk menuju Fase 2. Cukup terperinci untuk menyesuaikan dengan berbagai tingkat komitmen.
- **Preferred languages** — menjadi masukan baik untuk prioritas penerjemahan bot maupun keputusan saluran penjangkauan.
- **Bidang kontak terakhir** — opsional, tidak pernah wajib, tidak pernah masuk akal untuk diwajibkan dalam survei "apa yang Anda khawatirkan".

### Apa yang sengaja tidak ditanyakan

- **Demografi (usia, jenis kelamin)** — pilot Bali mencobanya dalam draf sebelumnya, lalu menghapusnya karena dampaknya rendah terhadap penyelesaian. Mungkin akan ditambahkan kembali sebagai opsional begitu volume respons membenarkan stratifikasi.
- **Toleransi spesifik PM2.5 / dB** — itu matters of fact, bukan matters of concern. Tempatnya di instrumentasi Fase 2, bukan survei Fase 1.
- **Pilihan ganda "apa yang akan membantu"** — akan mengarahkan jawaban. Gunakan teks bebas sebagai gantinya.

---

## Penambahan bidang — apa yang ada di base aktif sekarang

Tujuh bidang baru ditambahkan ke base Bali yang aktif pada 2026-05-12. Bidang-bidang itu ada di dalam tabel tetapi **BELUM ditambahkan ke tampilan formulir** — itu langkah manual di editor formulir Airtable, sengaja dipisahkan agar tim dapat meninjau urutan bidang dan setiap penataan ulang kata sebelum menampilkannya kepada responden.

Bidang baru:

| Bidang | Tipe | Tujuan |
|---|---|---|
| **Neighborhood** | Pilihan tunggal | Pemilih lokalitas terstruktur yang mencakup Bukit (Uluwatu, Pecatu, Ungasan, Bingin, Balangan, Padang Padang, Jimbaran, Nusa Dua, Kutuh, Benoa) ditambah sisa Bali. Menggantikan Location yang tidak terstruktur untuk analisis; Location tetap ada sebagai pelengkap teks bebas. |
| **How long have you lived here** | Pilihan tunggal | <1th / 1–5th / 5–10th / >10th / pengunjung / lebih suka tidak menjawab. Membedakan persepsi pendatang baru dari penduduk lama. |
| **How did you hear about us** | Multi-pilihan | Teman, sekolah, banjar, Instagram, WhatsApp, Facebook, organisasi mitra, pers, poster, ditemukan langsung, lainnya. Umpan balik saluran penjangkauan. |
| **How often does this happen** | Pilihan tunggal | Harian / mingguan / bulanan / musiman / sekali saja / tidak yakin. Sudut pandang frekuensi. |
| **When is it worst** | Multi-pilihan | Pagi-pagi sekali hingga malam, ditambah akhir pekan/hari kerja/sepanjang hari. Penting untuk keputusan penempatan sensor Fase 2. |
| **What you've tried** | Teks panjang | Apa yang telah dilakukan warga secara pribadi — berbicara dengan tetangga, melapor, bergabung dengan kelompok, mengubah rutinitas, membeli peralatan. Memunculkan kearifan komunitas yang sebelumnya dicampuradukkan oleh `Existing evidence` dengan dokumentasi. |
| **Outcome of what you tried** | Pilihan tunggal | Membantu / sebagian / tidak / terlalu dini / belum dicoba / tidak berlaku. Pelengkap terstruktur untuk teks bebas. |

**Langkah berikutnya (manual)**: buka tampilan formulir Airtable di editor base dan seret bidang-bidang ini ke dalam formulir dengan urutan yang direkomendasikan ini:

- Setelah `Location`: sisipkan `Neighborhood` (agar responden mendapatkan pemilih terstruktur tepat saat mereka sedang memikirkan tempat)
- Setelah `Categories`: sisipkan `How often does this happen` dan `When is it worst`
- Setelah `Existing evidence`: sisipkan `What you've tried` dan `Outcome of what you tried`
- Di dekat bagian bawah, setelah `Affiliation`: sisipkan `How long have you lived here` dan `How did you hear about us`

Ketujuhnya harus **opsional** dalam tampilan formulir — tidak ada yang wajib. Satu-satunya bidang wajib formulir tetap Concern dan Categories.

### Hal-hal yang sengaja TIDAK ditambahkan

- Bidang demografi (usia, jenis kelamin, pendapatan rumah tangga) — menambah hambatan tanpa nilai analitis pada skala pilot.
- Slider "Tingkat keparahan 1–10" untuk perhatian — mengkuantifikasi keparahan subjektif menambah derau, bukan sinyal. Narasi warga lebih berguna.
- Pin peta melalui widget pihak ketiga — mungkin dilakukan via integrasi Softr / Stacker, ditangguhkan sampai volume respons membenarkan beban integrasi.

---

## Replikasi — skema untuk fork survei

Untuk chapter Fab City lain yang mem-fork survei Bali untuk bioregion mereka sendiri, berikut skema Airtable yang akan Anda replikasi. ID base bersifat per-deployment; strukturnya bersama.

### Base: `Making Sense [Tempat Anda] · Matters of Concern`

### Tabel: `Matters of Concern` — satu baris per perhatian yang dikirim

Replikasi daftar bidang di atas. Bidang struktural (Concern, Categories, Description, Location, Most affected, Existing evidence, What would change, Willing to participate, Preferred languages, Name, Email, Phone, Affiliation, Status, Submitted at, Internal notes) berpindah langsung.

Yang Anda sesuaikan untuk bioregion Anda:

- **Categories** — sesuaikan daftarnya dengan konteks Anda. Daftar Bali mencakup "Heat & humidity" (relevan di daerah tropis) dan "Soil & agriculture" (sawah, perkebunan). Barcelona mungkin menghapus itu dan menambahkan "Heritage / built environment" atau "Heatwaves" (urgensi berbeda). Yucatán mungkin menambahkan "Cenote contamination." Selalu pertahankan "Other".
- **Most affected** — sesuaikan kategori demografisnya. "Visitors / tourists" penting di Bali karena pariwisata adalah kekuatan ekonomi dan lingkungan yang besar; kurang berlaku di kota non-wisata. "Workers" biasanya sebaiknya tetap ada (pekerja informal, pedagang pasar).
- **Willing to participate** — pertahankan strukturnya. Sesuaikan kata-katanya dengan konvensi lokal ("Connect us to my banjar" → "Connect us to my junta vecinal" dll.).
- **Preferred languages** — bahasa lokal Anda alih-alih Bahasa Indonesia + Bahasa Bali. English lazim sebagai opsi sekunder.

### Mereplikasi formulir aktif

Tampilan formulir bawaan Airtable adalah jalur paling sederhana:

1. Buat base + tabel dengan skema di atas
2. Buat tampilan Form, seret bidang-bidang dalam urutan yang ditunjukkan pada tabel urutan formulir
3. Tandai Concern dan Categories sebagai wajib; sisanya opsional
4. Atur pesan konfirmasi pengiriman formulir dengan suara Fab Lab tuan rumah
5. Sematkan di situs kampanye Anda, atau bagikan URL formulir langsung dalam penjangkauan

### Prabuat per lingkungan (opsional)

Untuk penjangkauan khusus lingkungan, tambahkan parameter kueri ke URL formulir untuk mengisi otomatis bidang Location atau Neighborhood:

```
[your-form-url]?prefill_Neighborhood=Eixample
[your-form-url]?prefill_Neighborhood=Gràcia
```

Kirim URL yang sudah terisi ke saluran penjangkauan khusus lingkungan (grup WhatsApp banjar, daftar orang tua sekolah, dll.) — lebih sedikit bidang yang harus diisi, tingkat penyelesaian lebih baik.

---

## Panduan penjangkauan

Desain survei tidak ada artinya jika tidak ada yang mengisinya. Penjangkauan Fase 1 adalah pekerjaan penopang utama kampanye.

### Bauran saluran

Bauran penjangkauan yang berfungsi untuk bioregion berpenduduk 50.000–500.000 orang:

| Saluran | Jangkauan | Upaya | Konversi |
|---|---|---|---|
| Saluran yang sudah dimiliki Fab Lab tuan rumah | sedang | rendah | tinggi |
| Sekolah mitra (grup orang tua, staf pengajar) | tinggi | sedang | tinggi |
| Dewan lingkungan / banjar / junta | sedang | sedang-tinggi | sangat tinggi |
| Grup komunitas WhatsApp (yang sudah ada secara lokal) | tinggi | sedang | sedang |
| Instagram / media sosial lokal | tinggi | rendah | rendah |
| Poster di toko, pasar, papan komunitas | sedang | sedang | rendah (tetapi membangun legitimasi) |
| Pers / radio lokal | tinggi | tinggi | rendah (tetapi membangun legitimasi) |
| Penjangkauan langsung tatap muka (pasar, acara) | rendah | tinggi | sangat tinggi |

Saluran berkonversi tinggi adalah saluran yang lambat dan membangun kepercayaan. Saluran berjangkauan tinggi lemah dalam konversi. Kampanye yang hanya mengandalkan media sosial akan mendapat respons berisik dari demografi yang sempit; yang hanya mengandalkan tatap muka akan mendapat respons kaya dari sedikit orang. Padukan keduanya, dan beri bobot pada apa yang dikuasai Fab Lab tuan rumah Anda.

### Lini masa

Kalender penjangkauan Fase 1 yang dapat dijalankan:

- **Minggu –2**: rancang survei, terjemahkan, siapkan Airtable, buat poster + aset media sosial
- **Minggu –1**: beri arahan kepada mitra, susun pesan penjangkauan, siapkan pelacakan internal
- **Minggu 1**: peluncuran lunak melalui Fab Lab + mitra terdekat. Sasaran: ~30 respons untuk menguji formulir
- **Minggu 2**: revisi formulir jika perlu berdasarkan umpan balik awal (salah ketik, logika rusak, bagian dengan penyelesaian rendah), lalu **peluncuran penuh**
- **Minggu 2–6**: penjangkauan aktif melalui semua saluran, sinkronisasi mingguan dengan mitra, bagikan temuan awal secara publik untuk menunjukkan bahwa survei sedang dibaca
- **Minggu 6**: penutupan lunak — kampanye mengurangi penjangkauan aktif tetapi menjaga formulir tetap terbuka
- **Minggu 8**: penutupan keras — hitung respons akhir, mulai analisis

Total: 8 minggu pengumpulan aktif, ditambah 2 minggu persiapan sebelumnya dan 2–4 minggu analisis + publikasi sesudahnya.

### Penerjemahan

Naskah survei Fase 1 harus ditinjau oleh **penutur asli dari bioregion Anda** sebelum dipublikasikan. Pertanyaan yang Anda tulis dalam bahasa Inggris akan kehilangan nuansa, memunculkan implikasi yang tidak disengaja, dan melewatkan kerangka spesifik lokal saat diterjemahkan. Anggarkan 1–2 minggu untuk siklus peninjauan terjemahan, bukan 1 hari.

Untuk Bali: Bahasa Indonesia utama, English sekunder. Bahasa Bali ditawarkan sebagai preferensi bahasa tetapi formulirnya sendiri saat ini Bahasa + English — menambahkan versi formulir berbahasa Bali adalah penyempurnaan di masa depan.

Untuk Barcelona: Catalan utama, Spanish sekunder, English opsional. Sadarilah bahwa naskah survei yang "terasa baik" dalam bahasa Spanyol bisa terbaca eksklusif di lingkungan yang mengutamakan Catalan (Gràcia, sebagian Eixample) — dan sebaliknya.

### Insentif

Tiga pendekatan yang berfungsi:

1. **Tanpa insentif, dibingkai sebagai kontribusi sipil.** Berhasil di komunitas padat dengan budaya sipil yang aktif. Jujur tentang apa yang diminta kampanye.
2. **Ucapan terima kasih opsional dalam formulir** — unduhan digital (PDF dasbor kualitas udara, panduan isu lingkungan di kota) yang dikirim otomatis saat pengiriman. Biaya rendah, menandakan timbal balik.
3. **Ucapan terima kasih fisik di acara** — di pasar, sekolah, atau lokasi mitra tempat Anda mengumpulkan secara langsung, sebotol kecil, stiker, atau barang bermerek.

Hindari membayar untuk respons. Itu menggeser bauran demografis ke arah orang yang membutuhkan uang alih-alih orang yang peduli pada isunya, dan itu membangun hubungan yang salah untuk Fase 2.

### Templat naskah penjangkauan

Aset penjangkauan yang paling sering dipakai adalah paragraf pendek yang Anda sesuaikan untuk setiap saluran. Templat:

> 🌴 *Making Sense [Tempat]* — kampanye Fab Lab [Kota] tentang isu lingkungan di lingkungan kita.
>
> Kami menanyakan kepada warga isu lingkungan apa yang memengaruhi kehidupan sehari-hari mereka — udara, air, kebisingan, sampah, apa saja. Ini adalah *Fase 1*: membangun gambaran tentang apa yang sebenarnya diperhatikan tetangga, sebelum kami memasang sensor apa pun. Masukan Anda membentuk ke mana kami akan berfokus selanjutnya.
>
> 🔒 Anonim kecuali Anda memilih untuk ditindaklanjuti. ~5 menit per perhatian.
>
> 📝 [tautan ke survei]
>
> *Dijalankan oleh Fab Lab [Kota] · Bagian dari [Fab City [Kota]] · Dibuat oleh tetangga, untuk tetangga.*

Terjemahkan, sesuaikan, unggah.

---

## Analisis dan publikasi

Fase 1 tidak lengkap tanpa menutup lingkaran. Warga yang berpartisipasi perlu melihat kampanye membaca masukan mereka. Tidak melakukan ini — mengumpulkan lalu menghilang — adalah mode kegagalan paling umum dari survei komunitas.

### Apa yang dianalisis

Tiga lapisan:

1. **Katalog perhatian** — jumlah perhatian per kategori, divisualisasikan sebagai diagram batang horizontal di halaman ringkasan publik. Karena survei satu baris per perhatian, ini adalah penjumlahan langsung alih-alih membongkar multi-pilihan.
2. **Geografi** — lokasi mana (diekstraksi dari teks bebas Location, atau dari Neighborhood setelah ditambahkan) yang berulang. Heatmap sederhana atau daftar beranotasi. Silangkan dengan Categories untuk pola kategori × lokasi.
3. **Narasi** — kutipan terpilih dari Description, Existing evidence, dan What would change. Disunting agar ringkas dan jelas, dianonimkan dengan gaya atribusi "*Warga, [lingkungan], [masa tinggal]*". Artefak paling kuat untuk pers, kebijakan, dan percakapan komunitas.

Analisis lanjutan opsional setelah Anda memiliki 100+ perhatian:

- Tabulasi silang (Categories × Most affected — apakah "Burning waste" paling sering memengaruhi anak-anak, hewan, atau lansia?)
- Kesenjangan tindakan (setelah bidang `What you've tried` ditambahkan — apa yang dicoba warga vs apa yang berhasil, memunculkan di mana aksi kolektif dibutuhkan)
- Klaster teori perubahan (pengodean kualitatif atas teks bebas `What would change` — apakah komunitas menginginkan penegakan, pengorganisasian, informasi, atau infrastruktur?)

### Apa yang dipublikasikan

Halaman hasil Fase 1 di situs kampanye Anda sebaiknya mencakup:

- Jumlah perhatian yang dikirim, jumlah responden unik (jika diketahui), tanggal pengumpulan
- Visualisasi katalog perhatian
- Pola geografis
- 5–10 kutipan warga terpilih
- Pernyataan yang jelas tentang apa yang akan dilakukan Fase 2 sebagai respons

Poin terakhir krusial. "Kami mendengar X adalah perhatian utama di [lingkungan], jadi Fase 2 akan memasang sensor di sana, akan memprioritaskan kategori Z dalam bot laporan, akan bekerja dengan [mitra] pada [aksi]." Itulah lingkaran yang tertutup.

### Berbagi kembali dengan responden

Email singkat kepada responden yang memilih untuk ditindaklanjuti, merangkum temuan dan mengundang mereka ke Fase 2. Buat email ini benar-benar menarik — bukan templat korporat — dan dari orang yang disebut namanya di Fab Lab tuan rumah.

---

## Iterasi — apa yang akan kita pelajari di Bali

Survei Fase 1 Bali berada pada fase paling awalnya per 2026-05-12 — formulir sudah aktif, skema telah diperluas dengan bidang-bidang baru di atas, dan penjangkauan aktif akan segera dimulai. Bagian ini akan terisi seiring respons nyata berdatangan.

Apa yang kami pantau, berdasarkan literatur citizen-sensing sebelumnya dan proyek Making Sense:

- **Panjang dan kualitas respons teks bebas.** Hipotesisnya adalah `What would change` dan `Existing evidence` akan mendapatkan jawaban terpanjang dan paling matang — warga punya teori perubahan dan punya pengetahuan lokal; survei ini adalah salah satu dari sedikit tempat yang menanyakannya. Jika penyelesaian tinggi pada bidang-bidang ini, desainnya berhasil.
- **Tingkat opt-in untuk Fase 2.** Berapa persen yang mencentang setidaknya satu opsi di `Willing to participate`? Ekspektasi naif dari proyek civic-tech umumnya adalah 15–30%; jika lebih tinggi, pembingkaian kampanye luar biasa beresonansi; jika lebih rendah, ada sesuatu dalam pesan yang gagal.
- **Bauran kategori.** Categories mana yang menumpuk paling cepat? Di Bali kami memperkirakan Burning waste, Plastic & solid waste, dan Air quality akan memimpin. Kejutan di sini secara langsung membentuk prioritas sensor Fase 2.
- **Kiriman anonim vs teridentifikasi.** Berapa banyak yang melewatkan bidang kontak sepenuhnya? Ini menandakan tingkat kepercayaan terhadap formulir dan lembaga tuan rumah.
- **Distribusi geografis.** Setelah `Neighborhood` ditambahkan ke formulir, lokasi bbox mana yang melaporkan kategori mana? Pola di sini mendorong penempatan sensor dan fokus penjangkauan.

Daftar ini akan diganti dengan pelajaran konkret seiring kampanye matang. PR ke dokumen ini berisi pengamatan dari Fab Lab lain disambut baik.

---

## Mem-fork untuk kota Anda — langkah konkret

1. **Baca dokumen ini secara lengkap.** Lalu lihat [formulir Bali yang aktif](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form) untuk merasakan bagaimana desainnya sebagai seorang responden.
2. **Buat base Airtable baru** di ruang kerja Anda. Replikasi skema tabel `Matters of Concern` (15 bidang termasuk 3 bidang khusus internal) sesuai tabel di atas.
3. **Sesuaikan opsi pilihan** dengan bioregion Anda. Categories, Most affected, Willing to participate (kata-kata untuk dewan lokal), Preferred languages.
4. **Terjemahkan deskripsi bidang dan naskah formulir** ke bahasa lokal Anda. Tinjauan penutur asli sebelum peluncuran publik.
5. **Sesuaikan pesan pengiriman formulir** agar terasa lokal. ("Terima kasih!" di Bali → "Gràcies!" di Barcelona → dst.)
6. **Rancang bauran penjangkauan Anda** — saluran, mitra, lini masa. Periksa kewajaran bersama Fab Lab tuan rumah dan pemimpin kampanye yang ditunjuk sebelum meluncurkan.
7. **Peluncuran lunak** dengan ~10–30 respons dari tetangga tepercaya. Perbaiki masalah pada formulir sebelum menyebarluaskannya.
8. **Peluncuran penuh** melalui bauran saluran Anda. Periode aktif 6–8 minggu.
9. **Analisis dan publikasikan** dalam 4 minggu setelah penutupan. Buat komitmen Fase 2 menjadi jelas.

Inti dari Fase 1 adalah memberi pijakan bagi Fase 2. Jangan terburu-buru melewatinya, dan jangan biarkan ia menjadi keadaan permanen — survei adalah alat, bukan tujuan akhir.

---

## Lisensi

Dokumen ini dan desain pertanyaannya: **CC-BY-SA 4.0**. Fork, sesuaikan untuk bioregion Anda, bagikan kembali apa yang Anda pelajari.

---

Bagian dari [Making Sense Bali](../README.md). Untuk konteks kampanye lengkap lihat [README induk](../README.md). Untuk replikasi lihat [REPLICATION.md](../REPLICATION.md).
