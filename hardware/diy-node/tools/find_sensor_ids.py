#!/usr/bin/env python3
"""
find_sensor_ids.py — search the Smart Citizen global sensor catalog for
the IDs needed in diy_node.ino's CONFIGURATION block.

Re-reading Oscar's note from May 2026: the SC platform was unified so
that device onboarding and data publishing are a single flow — *no
predefined blueprint needed*. The platform creates a device's
sensor mappings automatically on first MQTT publish, but you have to
publish using the **global sensor type IDs** from the SC catalog
(/v0/sensors). This tool helps you find them.

Usage:
    python3 find_sensor_ids.py              # default: search for the
                                            # DIY Plus kit's 7 metrics
    python3 find_sensor_ids.py BME680       # arbitrary search term(s)
    python3 find_sensor_ids.py PM Plantower

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


SC_API = "https://api.smartcitizen.me/v0/sensors"

# Default search groups for the DIY Plus kit. Each group has a label and
# a list of search terms — the first term that matches stops widening
# (so we prefer "bme680 temperature" over generic "temperature" if both
# exist in the catalog). Order matters: most specific first.
DEFAULT_SEARCHES = [
    ("SC_ID_TEMP      (BME680 temperature)",
     ["bme680 temperature", "bme680", "temperature"]),
    ("SC_ID_HUM       (BME680 humidity)",
     ["bme680 humidity", "humidity"]),
    ("SC_ID_PRESSURE  (BME680 barometric pressure)",
     ["bme680 pressure", "barometric", "pressure"]),
    ("SC_ID_GAS       (BME680 gas resistance / VOC)",
     ["bme680 voc", "bme680 gas", "gas resistance", "voc", "tvoc"]),
    ("SC_ID_PM1       (HM3301 / particulate matter PM1)",
     ["hm3301 pm1", "pm1.0", "pm1"]),
    ("SC_ID_PM25      (HM3301 / particulate matter PM2.5)",
     ["hm3301 pm2.5", "pm2.5", "pm 2.5"]),
    ("SC_ID_PM10      (HM3301 / particulate matter PM10)",
     ["hm3301 pm10", "pm10", "pm 10"]),
]


def fetch_catalog(per_page=500):
    # Smart Citizen's API is Rails-paginated and defaults to 25 per page,
    # so an unparametrised GET only returns a tiny slice of the catalog.
    # Pull a big chunk in one request.
    r = requests.get(SC_API, params={"per_page": per_page}, timeout=20)
    r.raise_for_status()
    return r.json()


def search(catalog, needle):
    """Return catalog entries whose name contains needle (case-insensitive)."""
    n = needle.lower()
    return [s for s in catalog if n in (s.get("name") or "").lower()]


def fmt_entry(entry):
    sid = entry.get("id", "?")
    name = entry.get("name", "?")
    unit = (entry.get("unit") or "").strip()
    measurement = entry.get("measurement") or {}
    meas_name = ""
    if isinstance(measurement, dict):
        meas_name = measurement.get("name", "")
    suffix = f"  ({meas_name})" if meas_name else ""
    return f"    {sid:>5}  {name}  [{unit}]{suffix}"


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("terms", nargs="*",
                   help="Search terms (default: search for DIY Plus kit's 7 metrics)")
    p.add_argument("--all", action="store_true",
                   help="Dump every sensor in the catalog, sorted by id")
    args = p.parse_args()

    print(f"Fetching {SC_API}?per_page=500 ...")
    try:
        catalog = fetch_catalog()
    except requests.RequestException as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(2)
    print(f"OK — {len(catalog)} sensors in the catalog\n")

    if args.all:
        # Dump every entry sorted by id. Useful for first-time exploration
        # when the kit's metrics don't show up under the default searches.
        print("Full sensor catalog (sorted by id):\n")
        for entry in sorted(catalog, key=lambda e: e.get("id", 0)):
            print(fmt_entry(entry))
        print()
        return

    if args.terms:
        # Custom search mode — show all matches per term.
        for term in args.terms:
            results = search(catalog, term)
            print(f"=== matches for '{term}' ({len(results)} hit(s)) ===")
            if not results:
                print("    (none)")
            else:
                for entry in results:
                    print(fmt_entry(entry))
            print()
        return

    # Default mode — find the kit's 7 metrics.
    print("Searching for DIY Plus kit metrics (BME680 + HM3301):\n")
    for label, needles in DEFAULT_SEARCHES:
        print(f"=== {label} ===")
        seen_ids = set()
        for needle in needles:
            matches = [e for e in search(catalog, needle)
                       if e.get("id") not in seen_ids]
            for entry in matches:
                seen_ids.add(entry.get("id"))
                print(f"{fmt_entry(entry)}   (matched: {needle!r})")
            if seen_ids:
                # Found something with this needle — don't widen the search
                # for this metric. The most-specific term wins.
                break
        if not seen_ids:
            print("    (no matches — try a broader term:")
            print(f"     python3 find_sensor_ids.py <keyword>)")
        print()

    print("─" * 70)
    print("Next step: pick the most-specific match for each metric (BME680-")
    print("prefixed entries are best where available), and paste the IDs into")
    print("the CONFIGURATION block in firmware/diy_node/diy_node.ino:")
    print()
    print("    const int SC_ID_TEMP      = <id>;")
    print("    const int SC_ID_HUM       = <id>;")
    print("    const int SC_ID_PRESSURE  = <id>;")
    print("    const int SC_ID_GAS       = <id>;")
    print("    const int SC_ID_PM1       = <id>;")
    print("    const int SC_ID_PM25      = <id>;")
    print("    const int SC_ID_PM10      = <id>;")
    print()
    print("Flash. Once the device publishes, the SC platform creates the")
    print("device-sensor mappings automatically from the payload — no admin")
    print("step required. Verify by re-running show_sensors.py 19651 a")
    print("minute later; the sensors array will populate.")


if __name__ == "__main__":
    main()
