# DIY node — workshop tools

Small utilities for working with DIY node kits during bring-up,
burn-in, calibration, and onboarding. Not required for normal operation
once the kit is running; the production firmware publishes directly to
Smart Citizen.

## `register_device.py` — bypass the onboarding flow

Registers a custom DIY node on the Smart Citizen platform via the API,
without going through the web onboarding flow and its associated
activation gate. This is the path the official SCK tooling uses for
custom hardware (see `fablabbcn/smartcitizen-tools` → `sck.py:register()`).

**When to use it:**

- You're deploying a custom node (not an off-the-shelf SCK) and don't
  want to wait for admin approval on the web onboarding flow.
- You're running a workshop where each participant needs their own
  device registered in minutes, not days.
- You're building automation around device provisioning.

**Setup (one-time):**

```bash
pip3 install requests
```

Then get your SC user API token from `smartcitizen.me → My Profile →
API → personal access token`. Either pass it with `--bearer` or set
it in your environment as `SC_BEARER`.

**Run:**

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

Output prints the device ID, URL, MQTT token, topic, and a sensor
list tailored to the kit variant (4 sensors for Basic, 7 for Plus).
After registration, open the device URL on smartcitizen.me, add the
listed sensors via the UI if they aren't auto-attached, copy the
sensor IDs into the firmware config, and flash.

## `show_sensors.py` — fetch sensor IDs ready to paste

Once a device has sensors attached on the SC platform, this script
fetches the device JSON, prints a clean table of attached sensors
with names and IDs, and emits a firmware-ready config block you can
paste straight into `diy_node.ino`. Auto-maps SC sensor names to the
matching `SC_ID_*` constants (Temperature, Humidity, Pressure, Gas
resistance, PM1, PM2.5, PM10).

**Run:**

```bash
pip3 install requests       # one-time
python3 show_sensors.py 19651
```

Output for a device with no sensors yet (the typical state right
after API registration, before the platform team attaches a hardware
blueprint):

```
Smart Citizen device 19651 — Bali DIY Node — Office
  state : never_published
  last  : never
  count : 0 sensor(s) attached
  ...

No sensors attached yet. (Ping the SC team with the device URL...)
```

Output once sensors are attached:

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

Use this any time the platform-side configuration changes (sensor
added/removed, blueprint reassigned) — re-fetch and re-paste.

## `find_sensor_ids.py` — find global SC sensor IDs to publish under

The Smart Citizen platform's MQTT ingest creates a device's
sensor associations automatically from the IDs in the publish
payload — but those IDs must come from the platform's global
sensor catalog (`/v0/sensors`), not made up locally. This tool
fetches the catalog and helps you find the right IDs for the
DIY kit's metrics.

**Run:**

```bash
pip3 install requests       # one-time
python3 find_sensor_ids.py
```

Default mode searches for all seven Plus-kit metrics (Temperature,
Humidity, Pressure, Gas resistance, PM1, PM2.5, PM10), preferring
BME680-specific entries where they exist in the catalog.

For arbitrary searches:

```bash
python3 find_sensor_ids.py BME680
python3 find_sensor_ids.py PM Plantower
```

Output shows each match with `id  name  [unit]` so you can pick
the most-specific entry and paste its ID into `diy_node.ino`.

**Workflow (post-Oscar-reread):**

1. `register_device.py` → device record created on SC (✓)
2. **`find_sensor_ids.py`** → find global IDs for your kit's metrics
3. Paste IDs into `diy_node.ino`'s CONFIGURATION block
4. Flash → device publishes → platform auto-creates the device-sensor mappings
5. `show_sensors.py <device_id>` → verify sensors now appear on the device record

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
