#!/usr/bin/env python3
"""
register_device.py — register a custom DIY node on Smart Citizen via the API.

Bypasses the onboarding / admin-approval flow. POSTs directly to
https://api.smartcitizen.me/v0/devices with a self-generated device
token (the same path the official SCK tooling uses for custom hardware
— see fablabbcn/smartcitizen-tools/sck.py register()).

After this script runs, you have:
  - A device record on smartcitizen.me (no activation step needed)
  - A 6-char hex device token for the firmware config
  - A device ID for the platform URL

Usage:

    python3 register_device.py

Or non-interactive (Plus kit — both sensors connected):

    export SC_BEARER=your_user_api_token
    python3 register_device.py \\
        --name "Bali DIY Node — Office" \\
        --lat -8.65 --lon 115.21 --exposure indoor --kit plus

For a Basic kit (BME680 only), pass --kit basic. The default is plus.

The user bearer token comes from your smartcitizen.me account:
    My Profile → API → personal access token.

Requires: requests  →  pip3 install requests
"""

import argparse
import binascii
import os
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


def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--bearer", default=os.environ.get("SC_BEARER"),
                   help="Your SC user API bearer token (or set SC_BEARER env var)")
    p.add_argument("--name", help="Device name (e.g. 'Bali DIY Node — Office')")
    p.add_argument("--lat", type=float, help="Latitude (decimal degrees)")
    p.add_argument("--lon", type=float, help="Longitude (decimal degrees)")
    p.add_argument("--exposure", default="indoor", choices=["indoor", "outdoor"],
                   help="Where the device is deployed (default: indoor)")
    p.add_argument("--kit", default="plus", choices=["basic", "plus"],
                   help="Which DIY node variant — basic = BME680 only, "
                        "plus = + HM3301 PM sensor (default: plus)")
    p.add_argument("--description", default=None,
                   help="Short description for the device record")
    p.add_argument("--tags", default="",
                   help="Comma-separated user tags. WARNING: the SC platform "
                        "validates tags against a controlled vocabulary on its "
                        "side — passing tag names that don't already exist on "
                        "the platform causes the device create to fail with "
                        "'Couldn't find Tag'. Safest path: leave empty here and "
                        "add tags through the device page UI after creation. "
                        "(default: empty)")
    return p.parse_args()


def prompt(label, default=None):
    extra = f" [{default}]" if default is not None else ""
    val = input(f"{label}{extra}: ").strip()
    return val or default


def main():
    args = parse_args()

    bearer = args.bearer
    if not bearer:
        print("Smart Citizen user API bearer token needed.")
        print("Get it from: smartcitizen.me → My Profile → API → personal access token")
        print()
        bearer = prompt("Bearer")
    if not bearer:
        sys.stderr.write("ERROR: bearer token required\n")
        sys.exit(2)

    name = args.name or prompt("Device name", "Bali DIY Node")
    lat = args.lat if args.lat is not None else float(prompt("Latitude", "-8.65"))
    lon = args.lon if args.lon is not None else float(prompt("Longitude", "115.21"))
    exposure = args.exposure
    kit = args.kit

    description = args.description or (
        "DIY workshop node — Fab Lab Bali · "
        f"{'Plus (BME680 + HM3301 PM)' if kit == 'plus' else 'Basic (BME680 only)'}"
    )

    # Generate a 6-char hex device token — matches the SCK firmware convention.
    device_token = binascii.b2a_hex(os.urandom(3)).decode("ascii")

    payload = {
        "name": name,
        "device_token": device_token,
        "description": description,
        "latitude": lat,
        "longitude": lon,
        "exposure": exposure,
    }
    # Only include user_tags if the user explicitly provided some. The SC API
    # validates tag names against an existing-records list and returns HTTP 404
    # "Couldn't find Tag" if any tag in the array doesn't already exist on the
    # platform — sending an empty / unset tags list is safer.
    if args.tags.strip():
        payload["user_tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]

    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json;charset=UTF-8",
    }

    print()
    print(f"POST {SC_API}")
    print(f"     name         : {name}")
    print(f"     device_token : {device_token}")
    print(f"     exposure     : {exposure}")
    print(f"     kit variant  : {kit}")
    print(f"     location     : ({lat}, {lon})")
    print(f"     tags         : {payload.get('user_tags', '(none — add via UI)')}")
    print()

    try:
        r = requests.post(SC_API, headers=headers, json=payload, timeout=15)
    except requests.RequestException as e:
        sys.stderr.write(f"ERROR: request failed: {e}\n")
        sys.exit(3)

    if r.status_code not in (200, 201):
        sys.stderr.write(f"ERROR: API returned HTTP {r.status_code}\n")
        sys.stderr.write(r.text + "\n")
        sys.exit(4)

    data = r.json()
    device_id = data.get("id")

    print("✓ Device registered.")
    print()
    print(f"  Device ID    : {device_id}")
    print(f"  Device URL   : https://smartcitizen.me/kits/{device_id}")
    print(f"  Device Token : {device_token}")
    print(f"  MQTT topic   : device/sck/{device_token}/readings")
    print()

    # Sensor list tailored to the kit variant. The user will need each
    # sensor's numeric ID after attaching them on the device page.
    sensors = [
        ("Temperature",    "°C",     "BME680"),
        ("Humidity",       "%",      "BME680"),
        ("Pressure",       "hPa",    "BME680"),
        ("Gas resistance", "kΩ",     "BME680"),
    ]
    if kit == "plus":
        sensors += [
            ("PM1",            "µg/m³", "HM3301"),
            ("PM2.5",          "µg/m³", "HM3301"),
            ("PM10",           "µg/m³", "HM3301"),
        ]

    print("Next steps:")
    print(f"  1. Open the device URL above. If sensors aren't auto-attached,")
    print(f"     add the following {len(sensors)} sensors via the UI:")
    for label, unit, source in sensors:
        print(f"       - {label:<15} ({unit:<6}) — {source}")
    print(f"  2. Note each sensor's numeric ID from the device page.")
    print(f"  3. Paste device_token + sensor IDs into diy_node.ino's config block.")
    print(f"     The firmware config has slots for all 7 IDs; for a Basic kit you'd")
    print(f"     leave the 3 PM slots at 0, but on Plus you fill in everything.")
    print(f"  4. Flash, watch Serial Monitor — readings should appear on the")
    print(f"     device page within ~2 minutes.")
    print()
    print("Save these values somewhere safe — the device token is what")
    print("authenticates this kit against the SC platform; treat it like a")
    print("password.")


if __name__ == "__main__":
    main()
