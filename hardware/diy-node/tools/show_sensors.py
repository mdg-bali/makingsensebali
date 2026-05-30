#!/usr/bin/env python3
"""
show_sensors.py — print the sensors attached to a Smart Citizen device,
formatted for pasting into diy_node.ino's config block.

Usage:
    python3 show_sensors.py <device_id>

Reads https://api.smartcitizen.me/v0/devices/<id> (public, no auth needed)
and prints a clean table of attached sensors with their IDs, plus a
firmware-ready config block that drops straight into diy_node.ino.

If the sensors array is empty — the case for a freshly-created custom
device awaiting a blueprint — that's reported clearly so you know what
you're still waiting on.

Requires: requests  →  pip3 install requests
"""

import argparse
import sys

try:
    import requests
except ImportError:
    sys.stderr.write(
        "\nERROR: 'requests' not installed.\n"
        "Install with:\n"
        "    pip3 install requests\n\n"
    )
    sys.exit(1)


SC_API = "https://api.smartcitizen.me/v0/devices"

# Map SC sensor names (lowercase substring match) → firmware constants.
# Order matters — more specific patterns first so "pm2.5" matches before "pm".
NAME_TO_CONST = [
    (("pm2.5", "pm 2.5"),       "SC_ID_PM25"),
    (("pm10",  "pm 10"),        "SC_ID_PM10"),
    (("pm1",   "pm 1", "pm1.0"),"SC_ID_PM1"),
    (("gas", "voc"),            "SC_ID_GAS"),
    (("pressure",),             "SC_ID_PRESSURE"),
    (("humidity",),             "SC_ID_HUM"),
    (("temperature",),          "SC_ID_TEMP"),
]

# Order + comments match diy_node.ino's config block exactly so the printed
# paste is a drop-in replacement.
CONFIG_TEMPLATE = [
    ("SC_ID_TEMP",     "°C       — BME680 temperature"),
    ("SC_ID_HUM",      "%RH      — BME680 humidity"),
    ("SC_ID_PRESSURE", "hPa      — BME680 barometric pressure (optional)"),
    ("SC_ID_GAS",      "kΩ       — BME680 gas resistance (VOC indicator)"),
    ("SC_ID_PM1",      "µg/m³    — HM3301 PM1.0 (atmospheric)"),
    ("SC_ID_PM25",     "µg/m³    — HM3301 PM2.5 (atmospheric)"),
    ("SC_ID_PM10",     "µg/m³    — HM3301 PM10  (atmospheric)"),
]


def map_sensor_to_const(name):
    n = name.lower()
    for needles, const in NAME_TO_CONST:
        if any(needle in n for needle in needles):
            return const
    return None


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("device_id", help="Numeric SC device ID (e.g. 19651)")
    args = p.parse_args()

    url = f"{SC_API}/{args.device_id}"
    try:
        r = requests.get(url, timeout=15)
    except requests.RequestException as e:
        sys.stderr.write(f"ERROR: request failed: {e}\n")
        sys.exit(2)

    if r.status_code == 404:
        sys.stderr.write(f"ERROR: device {args.device_id} not found on SC platform\n")
        sys.exit(3)
    if r.status_code != 200:
        sys.stderr.write(f"ERROR: API returned HTTP {r.status_code}\n{r.text}\n")
        sys.exit(4)

    data = r.json()
    name = data.get("name", "(unnamed)")
    state = data.get("state", "?")
    last = data.get("last_reading_at") or "never"
    sensors = data.get("data", {}).get("sensors", [])

    print()
    print(f"Smart Citizen device {args.device_id} — {name}")
    print(f"  state : {state}")
    print(f"  last  : {last}")
    print(f"  count : {len(sensors)} sensor(s) attached")
    print(f"  url   : https://smartcitizen.me/kits/{args.device_id}")
    print()

    if not sensors:
        print("No sensors attached yet.")
        print()
        print("If this is a custom device created via the API, the SC platform")
        print("requires an admin to attach a hardware blueprint server-side")
        print("before sensors appear in this list. Ping the SC team with the")
        print("device URL above and the kit's sensor list (BME680: T/RH/P/Gas,")
        print("HM3301: PM1/PM2.5/PM10).")
        print()
        return

    # --- Table ---
    print(f"  {'ID':>6}  {'Name':<34}  {'Unit':<10}  Maps to")
    print(f"  {'─' * 6}  {'─' * 34}  {'─' * 10}  {'─' * 18}")
    matched = {}
    for s in sensors:
        sid = s.get("id", "?")
        sname = s.get("name", "?")
        sunit = (s.get("unit") or "").strip()
        const = map_sensor_to_const(sname)
        print(f"  {sid:>6}  {sname:<34}  {sunit:<10}  {const or '(no auto-map)'}")
        if const and const not in matched:
            matched[const] = sid
    print()

    # --- Firmware-ready paste block ---
    print("Paste into diy_node.ino — replace the SC_ID_* lines in the CONFIGURATION block:")
    print()
    for const, comment in CONFIG_TEMPLATE:
        if const in matched:
            print(f"  const int {const:<14} = {matched[const]:<6};  // {comment}")
        else:
            print(f"  const int {const:<14} = 0;       // {comment}  ← not attached")
    print()

    # Surface anything we couldn't map, so the user knows nothing was silently dropped.
    unmapped = [s for s in sensors if not map_sensor_to_const(s.get("name", ""))]
    if unmapped:
        print("Sensors with no firmware mapping (left out of the paste block):")
        for s in unmapped:
            print(f"  id={s.get('id')} name={s.get('name')!r}")
        print("Add them by hand if you want to publish them — they'd need new")
        print("SC_ID_* constants and a matching addSensor() call in publishReadings().")
        print()


if __name__ == "__main__":
    main()
