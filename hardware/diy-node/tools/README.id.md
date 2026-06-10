[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# DIY node — alat lokakarya

Utilitas kecil untuk bekerja dengan kit DIY node selama bring-up,
burn-in, kalibrasi, dan onboarding. Tidak diperlukan untuk operasi normal
setelah kit berjalan; firmware produksi mempublikasikan langsung ke
Smart Citizen.

## `register_device.py` — melewati alur onboarding

Mendaftarkan DIY node kustom di platform Smart Citizen melalui API,
tanpa melalui alur onboarding web dan gerbang aktivasi yang
menyertainya. Ini adalah jalur yang digunakan perkakas SCK resmi untuk
perangkat keras kustom (lihat `fablabbcn/smartcitizen-tools` → `sck.py:register()`).

**Kapan menggunakannya:**

- Anda menerapkan node kustom (bukan SCK siap pakai) dan tidak
  ingin menunggu persetujuan admin pada alur onboarding web.
- Anda menjalankan lokakarya di mana setiap peserta perlu perangkat
  mereka sendiri terdaftar dalam hitungan menit, bukan hari.
- Anda membangun otomasi seputar penyediaan perangkat.

**Penyiapan (sekali saja):**

```bash
pip3 install requests
```

Kemudian dapatkan token API pengguna SC Anda dari `smartcitizen.me → My Profile →
API → personal access token`. Berikan dengan `--bearer` atau atur
di lingkungan Anda sebagai `SC_BEARER`.

**Jalankan:**

```bash
# Interactive
python3 register_device.py

# Non-interactive — Plus kit (BME680 + HM3301)
export SC_BEARER=your_user_api_token
python3 register_device.py \
    --name "Bali DIY Node — Office" \
    --lat -8.65 --lon 115.21 --exposure indoor --kit plus

# Basic kit (BME680 only) — only 4 sensors to attach
python3 register_device.py --kit basic ...
```

Keluaran mencetak ID perangkat, URL, token MQTT, topik, dan daftar
sensor yang disesuaikan dengan varian kit (4 sensor untuk Basic, 7 untuk Plus).
Setelah pendaftaran, buka URL perangkat di smartcitizen.me, tambahkan
sensor yang terdaftar melalui UI jika belum terpasang otomatis, salin
ID sensor ke dalam konfigurasi firmware, dan flash.

## `show_sensors.py` — ambil ID sensor siap tempel

Setelah sebuah perangkat memiliki sensor terpasang di platform SC, skrip ini
mengambil JSON perangkat, mencetak tabel rapi sensor yang terpasang
dengan nama dan ID, serta menghasilkan blok konfigurasi siap-firmware yang dapat
Anda tempel langsung ke `diy_node.ino`. Memetakan otomatis nama sensor SC ke
konstanta `SC_ID_*` yang sesuai (Temperature, Humidity, Pressure, Gas
resistance, PM1, PM2.5, PM10).

**Jalankan:**

```bash
pip3 install requests       # one-time
python3 show_sensors.py 19651
```

Keluaran untuk perangkat yang belum memiliki sensor (keadaan tipikal tepat
setelah pendaftaran API, sebelum tim platform memasang
blueprint perangkat keras):

```
Smart Citizen device 19651 — Bali DIY Node — Office
  state : never_published
  last  : never
  count : 0 sensor(s) attached
  ...

No sensors attached yet. (Ping the SC team with the device URL...)
```

Keluaran setelah sensor terpasang:

```
  ID      Name                                Unit        Maps to
  ─────   ──────────────────────────────      ─────       ─────────────────
   14     Temperature                         °C          SC_ID_TEMP
   56     Humidity                            %           SC_ID_HUM
   58     Barometric pressure                 hPa         SC_ID_PRESSURE
   ...

Paste into diy_node.ino — replace the SC_ID_* lines in the CONFIGURATION block:

  const int SC_ID_TEMP       = 14    ;  // °C       — BME680 temperature
  const int SC_ID_HUM        = 56    ;  // %RH      — BME680 humidity
  ...
```

Gunakan ini setiap kali konfigurasi sisi-platform berubah (sensor
ditambah/dihapus, blueprint ditugaskan ulang) — ambil ulang dan tempel ulang.

## `find_sensor_ids.py` — temukan ID sensor SC global untuk mempublikasikan

Ingest MQTT platform Smart Citizen membuat asosiasi sensor
sebuah perangkat secara otomatis dari ID dalam payload publikasi
— tetapi ID-ID itu harus berasal dari katalog sensor global
platform (`/v0/sensors`), bukan dibuat-buat secara lokal. Alat ini
mengambil katalog dan membantu Anda menemukan ID yang tepat untuk
metrik kit DIY.

**Jalankan:**

```bash
pip3 install requests       # one-time
python3 find_sensor_ids.py
```

Mode default mencari ketujuh metrik Plus-kit (Temperature,
Humidity, Pressure, Gas resistance, PM1, PM2.5, PM10), mengutamakan
entri spesifik-BME680 di mana ada dalam katalog.

Untuk pencarian sembarang:

```bash
python3 find_sensor_ids.py BME680
python3 find_sensor_ids.py PM Plantower
```

Keluaran menampilkan setiap kecocokan dengan `id  name  [unit]` sehingga Anda dapat memilih
entri yang paling spesifik dan menempelkan ID-nya ke `diy_node.ino`.

**Alur kerja (pasca-baca-ulang-Oscar):**

1. `register_device.py` → catatan perangkat dibuat di SC (✓)
2. **`find_sensor_ids.py`** → temukan ID global untuk metrik kit Anda
3. Tempel ID ke blok CONFIGURATION `diy_node.ino`
4. Flash → perangkat mempublikasikan → platform membuat otomatis pemetaan perangkat-sensor
5. `show_sensors.py <device_id>` → verifikasi sensor kini muncul di catatan perangkat

## `log_serial.py` — pencatat USB serial → CSV

Membaca keluaran Serial sketsa uji (atau sketsa produksi) melalui
USB dan menambahkan baris bercap waktu ke sebuah CSV. Berfungsi dengan baik pada Basic
(BME680 saja) maupun Plus (BME680 + HM3301) — kolom PM dibiarkan
kosong saat HM3301 tidak ada.

**Kapan menggunakannya:**

- Karakterisasi burn-in — tangkap 24–48 jam pembacaan untuk melihat
  sensor gas BME680 stabil dari keadaan resistansi-rendah awalnya.
- Verifikasi lokakarya — berikan peserta sebuah CSV dari jam pertama
  data mereka agar mereka dapat memplotnya dan melihat sensor bekerja.
- Sprint kalibrasi — saat DIY Plus diko-lokasikan dengan
  SCK resmi untuk menurunkan faktor koreksi, rekam keduanya bercap waktu
  agar dapat menyelaraskan seri di kemudian hari.

**Penyiapan (sekali saja):**

```bash
pip3 install pyserial
```

**Jalankan:**

```bash
# Autodetect port, write to readings_<timestamp>.csv in cwd
python3 log_serial.py

# Custom output path
python3 log_serial.py --out office_burnin.csv

# Specify port explicitly (use `ls /dev/cu.*` on macOS to find it)
python3 log_serial.py --port /dev/cu.usbmodem1101
```

Ctrl-C untuk berhenti. CSV di-flush secara bersih saat keluar.

**Kolom CSV:**

| Kolom | Satuan | Sumber |
|---|---|---|
| `timestamp_iso` | UTC ISO 8601 | Jam Mac pada saat pembacaan |
| `t_c` | °C | BME680 |
| `rh_pct` | %RH | BME680 |
| `p_hpa` | hPa | BME680 |
| `gas_kohm` | kΩ | BME680 (indikator VOC) |
| `pm1` | µg/m³ | HM3301 (kosong untuk kit Basic) |
| `pm2_5` | µg/m³ | HM3301 (kosong untuk kit Basic) |
| `pm10` | µg/m³ | HM3301 (kosong untuk kit Basic) |

**Pemplotan:**

Masukkan CSV ke alat favorit Anda — Numbers, Excel, Google Sheets,
atau:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("readings_20260520_184530.csv", parse_dates=["timestamp_iso"])
df.set_index("timestamp_iso").plot(subplots=True, figsize=(12, 10))
plt.show()
```

Untuk lari burn-in, kurva resistansi gas adalah tampilan yang paling menarik
— Anda seharusnya melihatnya naik dari beberapa kΩ ke puluhan atau ratusan
kΩ selama 24 jam pertama, lalu menetap ke garis dasar dengan ayunan
diurnal kecil yang terkait dengan aktivitas dalam ruangan Anda (memasak, membersihkan,
elektronik, hunian).
