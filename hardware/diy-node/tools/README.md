# DIY node — workshop tools

Small utilities for working with DIY node kits during bring-up,
burn-in, and calibration. Not required for normal operation; the
production firmware publishes directly to Smart Citizen.

## `log_serial.py` — USB serial → CSV logger

Reads the test sketch's (or production sketch's) Serial output over
USB and appends timestamped rows to a CSV. Works with both Basic
(BME680 only) and Plus (BME680 + HM3301) kits — PM columns are left
empty when the HM3301 isn't present.

**When to use it:**

- Burn-in characterisation — capture 24–48h of readings to see the
  BME680's gas sensor stabilise from its initial low-resistance state.
- Workshop verification — give participants a CSV of their first
  hour of data so they can plot it and see the sensor working.
- Calibration sprints — when a DIY Plus is co-located with an
  official SCK to derive a correction factor, record both timestamped
  to align series later.

**Setup (one-time):**

```bash
pip3 install pyserial
```

**Run:**

```bash
# Autodetect port, write to readings_<timestamp>.csv in cwd
python3 log_serial.py

# Custom output path
python3 log_serial.py --out office_burnin.csv

# Specify port explicitly (use `ls /dev/cu.*` on macOS to find it)
python3 log_serial.py --port /dev/cu.usbmodem1101
```

Ctrl-C to stop. The CSV is flushed cleanly on exit.

**CSV columns:**

| Column | Unit | Source |
|---|---|---|
| `timestamp_iso` | UTC ISO 8601 | Mac's clock at moment of read |
| `t_c` | °C | BME680 |
| `rh_pct` | %RH | BME680 |
| `p_hpa` | hPa | BME680 |
| `gas_kohm` | kΩ | BME680 (VOC indicator) |
| `pm1` | µg/m³ | HM3301 (empty for Basic kit) |
| `pm2_5` | µg/m³ | HM3301 (empty for Basic kit) |
| `pm10` | µg/m³ | HM3301 (empty for Basic kit) |

**Plotting:**

Drop the CSV into your favourite tool — Numbers, Excel, Google Sheets,
or:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("readings_20260520_184530.csv", parse_dates=["timestamp_iso"])
df.set_index("timestamp_iso").plot(subplots=True, figsize=(12, 10))
plt.show()
```

For burn-in runs, the gas resistance curve is the most interesting
view — you should see it climb from a few kΩ to tens or hundreds of
kΩ over the first 24 hours, then settle into a baseline with small
diurnal swings tied to your indoor activity (cooking, cleaning,
electronics, occupancy).
