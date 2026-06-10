[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Enklosur DIY Node v5 — sang buah pinus

Satu model OpenSCAD parametrik ([`enclosure.scad`](enclosure.scad)) menghasilkan kedua varian — **Basic** (XIAO ESP32-S3 + BME680 di atas perfboard 4×6 cm) dan **Plus** (menambahkan modul PM Grove HM3301, vertikal). STL ada di [`stl/`](stl/), pratinjau di [`img/`](img/), keempat desain sebelumnya di [`archive/`](archive/) dengan peringatan untuk meninjau sebelum mencetak.

Buah pinus sudah merupakan enklosur luar ruangan: sisik-sisik yang saling tumpang tindih membuang air hujan keluar dan terbuka untuk meloloskan udara. v5 meminjam seluruh gagasan itu dengan tepat **sepuluh daun besar** — empat di bawah menutupi slot masukan, sepasang mengapit kisi (tiga di lengkung tengah pada Basic), empat di atas menyatu menjadi tudung di atas saluran buang. Perlindungan dari hujan dan ventilasi memiliki geometri yang sama: setiap slot pernapasan tersembunyi dalam bayangan hujan sebuah daun. Setiap daun dicetak tanpa penyangga — saat dibalik, ia menjadi sirip naik ~40°. Jitter terunggun (seeded) pada ukuran, sudut, dan azimut menjaga bentuk tetap organik tanpa mengorbankan reproduksibilitas: `scale_seed` yang sama, pohon yang sama; tabel `leaves_plus` / `leaves_basic` dalam kode sumber adalah tata letaknya jika Anda ingin mengarahkan seni Anda sendiri.

| | Basic | Plus |
|---|---|---|
| Ø badan (dinding inti) | 66 mm | 66 mm |
| Selubung sisik | ~Ø90 | ~Ø90 |
| Tinggi | 99 mm | 119 mm |
| Bagian yang dicetak | inti + tudung | inti + tudung |

![Perakitan Plus](img/v5_plus_front.png)

## Kulit itulah fungsinya

**Hujan:** setiap sisik menaungi pita dinding di bawahnya pada sudut lebih baik dari 45°; tudung menutupi baris-baris atas; ambang 45° membuang bibir bawah kisi. Tidak ada garis pandang horizontal ke bukaan mana pun. **Udara:** slot-slot kecil bersembunyi dalam bayangan hujan di bawah baris sisik — masukan rendah pada tinggi BME680, buang tinggi di bawah tudung — sehingga cerobong bekerja tanpa ventilasi yang terlihat. **Kisi PM** berada di petak bebas sisik: batang gecko vertikal, tiga cincin naungan garis-sisik, dan muka kaleng logam modul berada 3–4 mm di belakang dengan tambalan jaring halus diplester menutupi port-portnya. Lembar data HM3301 mengizinkan port menyamping; burn-in dan ko-lokasi SCK (README induk) tetap merupakan kalibrasi yang sesungguhnya.

## Tanpa label — jejak (footprint)

Komponen diletakkan berdasarkan bentuk, bukan teks, dan bentuk-bentuk itu nyata. Pada tulang punggung: **jejak XIAO ESP32-S3** — garis luar sebenarnya 21 × 17,8, dua baris header 7-pin-nya pada pitch 2,54 mm (sejajar dengan kisi perfboard saat dilihat melalui lubang), dan oval USB-C di sisi kabel; **jejak BME680** — garis luar, baris header 6-pin, kotak tutup sensor; sebuah **piktogram baterai** pada tinggi sel. Pada lantai: sebuah **piktogram USB** pada lengkungan kabel, **bibir/rangka LiPo** yang secara fisik meletakkan sel, dan dua **pasak registrasi** pada posisi lubang Ø3,2 carrier Grove yang terverifikasi Eagle — saat modul mencapai dasar relnya, pasak-pasak itu mengeklik masuk, dan itulah pemeriksaan terpasang-dan-terorientasi.

## LiPo, dengan mata terbuka

803040 opsional (~1000 mAh) disambungkan ke pad BAT XIAO sebelum perakitan. Basic: berdiri dalam rangka lantai tercetak, diikat dengan zip tie. Plus: ditempel busa ke punggung carrier di dalam garis luar tercetaknya; bibir lantai menahannya agar tidak meluncur. Sel kantung (pouch cell) menua cepat dalam panas Bali — gunakan hanya sel terlindungi berkualitas, periksa saat membersihkan jaring, USB tetap menjadi catu daya permanen. `with_battery=false` menghapus penyediaannya.

## Pencetakan

PETG putih (atau PLA+ ber-isi-kayu untuk buah pinus demo dalam ruangan — luar ruangan tetap PETG), lapisan 0,2 mm, 4 perimeter, tanpa penyangga, pendinginan bagian menyala.

| Bagian | Orientasi | Catatan |
|---|---|---|
| core | seperti diekspor — berdiri | brim 5 mm |
| hood | seperti diekspor — tudung menghadap bawah | **brim 10 mm**; sisik dicetak sebagai sirip naik, perimeter luar yang lambat membantu ujung-ujungnya |

Tudung memakan ~4–5 jam — sepuluh daun jauh lebih murah daripada eksperimen sisik-rapat yang digantikannya. Cetakan pertama: jeda inti pada ~20 mm, uji-pas potongan sisa perfboard dan carrier Grove; `fit` / `drop` adalah tombol pengaturnya; `can_cx` memindahkan kisi; `scale_seed` mengocok ulang buah pinusnya.

```sh
openscad -o stl/diy-node-plus-hood.stl -D 'variant="plus"' -D 'part="hood"' enclosure.scad
```

bagian: `core` / `hood` / `plate` / `assembly` · varian: `basic` / `plus` · flag: `with_battery`, `scale_seed`

## Apa lagi yang Anda butuhkan

| Jml | Barang | Catatan |
|---|---|---|
| 1 | tambalan jaring stainless halus ~40 × 40 mm | Plus: diplester ke muka kaleng menutupi port |
| 2 | sekrup self-tapping M3 × 8 | sambungan |
| 4 | sekrup dinding + fischer, kepala pan ≤ Ø8 | lubang kunci, standoff ~4 mm |
| 2–3 | zip tie | pelepas regangan USB; rangka baterai Basic |
| opsi | LiPo 803040 + selotip busa | lihat di atas |

## Perakitan

1. Gantung inti pada 4 sekrup dinding yang sudah dipasang sebelumnya — lubang kunci berada di belakang papan (pasangan atas berjarak 30 mm).
2. Solder keempat kabel modul ke pad uji carrier-nya; baterai (jika ada) ke pad BAT XIAO; letakkan komponen pada jejak tulang punggungnya sebelum menyolder perfboard.
3. Perfboard turun melalui alur belakang — XIAO pada garis luarnya (atas), BME680 pada garis luarnya (bawah), USB-C menghadap kanan.
4. Plus: modul turun melalui alur depan hingga pasak lantai mengeklik ke lubang pemasangannya (itulah pemeriksaan orientasi). Tambalan jaring sudah ada di muka kaleng.
5. Kabel USB keluar melalui lengkungan lantai — ikuti piktogram — diikat zip tie pada tiang, drip loop di luar.
6. Tudung turun menutupi tulang punggung hingga duduk pada bahu cangkir; dua sekrup M3 menembus kerah.

## Aturan penempatan

Di bawah teritis pada dinding teduh, lebih dari 20 cm dari tanah, titik ideal 1,5–2 m, jangan pernah di atas atap seng telanjang. Arahkan kisi menjauhi angin muson yang berlaku. Periksa tambalan jaring dan lubang tiris setiap bulan; sapu serasah daun dari sisik selagi Anda di sana — sisik mengumpulkannya persis seperti buah pinus sungguhan.

## Batasan yang diketahui, secara jujur

Bukan IP65 — pelapisan konformal (README induk) melindungi elektronik, sisik melindungi aliran udara. Tudung bersisik memakan lebih banyak plastik (~55 g vs 40 pada v4) dan waktu cetak; itulah harga dari kulit ini, dan `archive/v4-column/` tetap merupakan build polos yang cepat. Ujung sisik adalah bagian yang akan tersangkut saat Anda membawanya — tebalnya 1,35 mm dan bertahan terhadap penanganan, tetapi jangan menumpuk tudung dalam kotak. Pembaruan SEN54 mendapat revisinya sendiri saat divalidasi.

Lisensi: MIT, repo induk. Referensi papan Seeed: [`ref_hm3301_board.pdf`](ref_hm3301_board.pdf) (CC-BY-SA). Fork untuk Making Sense [tempat Anda] — dan kocok ulang `scale_seed` agar hutan Anda memiliki pohon-pohon yang berbeda.
