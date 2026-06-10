[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# `data/reports/` — profil laporan warga yang disetujui

Direktori ini menyimpan profil Murmurations yang sudah dibersihkan dari
laporan warga yang telah disetujui oleh operator kampanye. Berkas di sini
adalah artefak publik — halaman beranda (`index.html`) dan dasbor
(`dashboard/index.html`) mengambilnya melalui `fetchReports()` milik `data.js`
dan menampilkannya di peta bersama pin sensor.

## Berkas

- **`index.json`** — manifes yang mendaftar semua nama berkas profil yang disetujui.
  Diperbarui secara otomatis oleh `reports/sync_profiles.sh` setelah setiap
  siklus persetujuan.
- **`AQ_<timestamp_id>.json`** — satu berkas per laporan yang disetujui. Formatnya
  adalah skema Murmurations [`environmental_observation-v1.0.0`](../../reports/schemas/environmental_observation-v1.0.0.json).
  Sudah dibersihkan dari PII oleh adapter Sense Making.

## Bagaimana profil sampai di sini

1. Seorang warga mengirim laporan WhatsApp ke bot
2. Bot menyimpannya secara lokal sebagai `pending_review`
3. Operator meninjau laporan di dasbor lokal dan mengeklik
   **Approve**
4. Bot menulis profil Murmurations yang sudah dibersihkan ke direktori
   `profiles/` lokalnya
5. `reports/sync_profiles.sh` (dijalankan oleh cron di NAS) menyalin profil
   baru ke direktori `data/reports/` ini, membuat ulang
   `index.json`, melakukan commit, dan mendorong ke GitHub
6. GitHub Pages membangun ulang; peta menampilkan laporan baru

Tidak ada apa pun di sini yang boleh disunting secara manual kecuali untuk
penghapusan darurat (mis., laporan yang disetujui karena keliru). Untuk menghapus profil,
hapus berkasnya dan hilangkan nama berkas itu dari `index.json`, lalu
lakukan commit dan dorong.

## Jaminan privasi

- Profil-profil ini sudah dibersihkan dari nomor telepon pengirim,
  hash pengirim, jalur gambar lokal, dan kunci media Evolution API
  oleh `reports/murmurations_adapter.py` sebelum ditulis.
- Identitas pelapor tidak pernah dapat dipulihkan dari apa pun di
  direktori ini.
- Untuk detailnya, lihat `reports/README.md` dan bagian privasi pada
  `../../REPLICATION.md`.
