[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Arsip enklosur — versi yang telah digantikan

Ini adalah desain-desain yang muncul sebelum yang sekarang. **Tidak satu pun dari mereka boleh dicetak untuk penerapan apa adanya** — masing-masing digantikan karena alasan yang konkret, disimpan di sini karena garis keturunannya sendiri merupakan bahan lokakarya: setiap folder adalah pelajaran dalam mendesain untuk FDM dan untuk bagian-bagian nyata. Tinjau, perbaiki, atau kanibalisasi — jangan mencetak secara membabi buta.

| Versi | Apa itu | Mengapa digantikan |
|---|---|---|
| [`v1-box/`](v1-box/) | Kotak Stevenson-screen berkisi-kisi, 3 bagian datar | Tidak pernah dicetak. Panel datar + kisi celah adalah pemikiran pemotong laser — ia kurang memanfaatkan printer. Juga diukur untuk kaleng HM3301 telanjang dan perfboard 5×7. |
| [`v2-lantern/`](v2-lantern/) | Lentera putar penampang-D, 2 bagian, snap-fit | Dicetak dan gagal. Bay PM pas dengan kaleng telanjang 40×38, tetapi modul Grove adalah kaleng pada **PCB carrier 80×40**. Sambungan snap macet: kelonggaran 0,2 mm, menara pemandu menabrak dinding cangkir. |
| [`v3-gourd/`](v3-gourd/) | Lentera dengan kaki persegi-panjang-membulat lebar untuk modul penuh, sambungan disekrup | Berhasil di atas kertas, pas dengan modul sungguhan, sambungan diperbaiki — tetapi kaki 88×48 membuatnya besar. Digantikan oleh kolom modul-vertikal. |
| [`v4-column/`](v4-column/) | Kolom ramping Ø66, modul vertikal di balik kisi berkisi-cincin, label teks, bay LiPo | Secara fungsional baik — arsitektur intinya berlanjut. Digantikan secara estetis: cincin halus dan teks ter-deboss memberi jalan kepada kulit sisik buah pinus dan panduan jejak fisik. Cetak yang satu ini jika Anda menginginkan build yang paling polos dan paling cepat. |

Setiap folder memiliki `enclosure.scad` parametrik; regenerasi STL dengan perintah-perintah di [README enklosur](../README.md) utama. Dimensi acuan untuk modul Grove HM3301 (dari berkas Eagle Seeed, lihat [`../ref_hm3301_board.pdf`](../ref_hm3301_board.pdf)): carrier 80 × 40 mm, lubang Ø3,2 pada ±36/±16, kaleng telanjang 40 × 38 × 15 di atas.

Pelajaran yang berulang, agar fork berikutnya tidak mengulanginya: desain untuk **modul lengkap yang dibeli**, bukan sensor telanjang dalam lembar data; sambungan memerlukan penahan keras (hard stop), kelonggaran radial ≥0,5 mm, dan pengarah masuk berpinggul (chamfered lead-in) pada toleransi FDM; perlindungan dari hujan adalah geometri (skirt, pemutus garis pandang, bukaan menghadap bawah), bukan gasket; dan verifikasi dengan render penuh — pratinjau OpenSCAD berbohong tentang `intersection()` + `rotate_extrude`.
