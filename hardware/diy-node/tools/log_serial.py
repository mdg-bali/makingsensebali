#!/usr/bin/env python3
"""
log_serial.py — log Smart Citizen Bali DIY node readings from USB serial to CSV.

Reads the test sketch's serial output (or the production sketch's serial
diagnostics — same line format) and appends timestamped rows to a CSV.
Works with both Basic (BME680 only) and Plus (BME680 + HM3301) kits —
PM columns are left empty when the HM3301 isn't present.

Usage:

    python3 log_serial.py
    python3 log_serial.py --out office_burnin.csv
    python3 log_serial.py --port /dev/cu.usbmodem1101 --baud 115200

If --port is not given, the script scans /dev/cu.usbmodem* on macOS and
/dev/ttyACM* / /dev/ttyUSB* on Linux. If --out is not given, it writes
to readings_YYYYMMDD_HHMMSS.csv in the current directory.

Output CSV columns:
    timestamp_iso, t_c, rh_pct, p_hpa, gas_kohm, pm1, pm2_5, pm10

Ctrl-C to stop; the file is flushed and closed cleanly.

Requires: pyserial  →  pip3 install pyserial
"""

import argparse
import csv
import glob
import re
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import serial
except ImportError:
    sys.stderr.write(
        "\nERROR: pyserial not installed.\n"
        "Install with:\n"
        "    pip3 install pyserial\n\n"
    )
    sys.exit(1)


# --- Parsing ----------------------------------------------------------------

# Matches lines like:
#   [bme680]  T= 29.03 °C   RH=54.81 %   P=1009.49 hPa   Gas=    3.1 kΩ
BME_RE = re.compile(
    r"\[bme680\]\s+"
    r"T=\s*(-?\d+\.\d+)\s*°?C\s+"
    r"RH=\s*(-?\d+\.\d+)\s*%\s+"
    r"P=\s*(-?\d+\.\d+)\s*hPa\s+"
    r"Gas=\s*(-?\d+\.\d+)\s*k"  # tolerate Ω / Ohm / ohms / variants
)

# Matches lines like:
#   [hm3301]  PM1=   2 µg/m³   PM2.5=   4 µg/m³   PM10=   5 µg/m³
HM_RE = re.compile(
    r"\[hm3301\]\s+"
    r"PM1=\s*(\d+)\s*µ?g/m\D*\s+"
    r"PM2\.5=\s*(\d+)\s*µ?g/m\D*\s+"
    r"PM10=\s*(\d+)\s*µ?g/m\D*"
)


# --- Port handling ----------------------------------------------------------

def autodetect_port():
    """Scan common serial-port locations for a USB-connected MCU."""
    candidates = (
        glob.glob("/dev/cu.usbmodem*")      # macOS — XIAO ESP32-S3 native USB-CDC
        + glob.glob("/dev/cu.usbserial*")   # macOS — older USB-serial bridges
        + glob.glob("/dev/cu.SLAB_USBtoUART")  # macOS with CP210x driver
        + glob.glob("/dev/ttyACM*")         # Linux — USB-CDC (what the XIAO uses)
        + glob.glob("/dev/ttyUSB*")         # Linux — USB-serial bridges
    )
    return candidates[0] if candidates else None


def open_serial(port, baud):
    """Open the port, retrying every 2s if it isn't ready yet."""
    while True:
        try:
            return serial.Serial(port, baud, timeout=2)
        except serial.SerialException as e:
            sys.stderr.write(f"[log] could not open {port} ({e}). Retrying in 2s...\n")
            time.sleep(2)


# --- Main loop --------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--port", default=None,
                   help="serial port (autodetected if omitted)")
    p.add_argument("--baud", type=int, default=115200,
                   help="serial baud rate (default 115200)")
    p.add_argument("--out", default=None,
                   help="output CSV path (default: readings_<timestamp>.csv)")
    return p.parse_args()


def main():
    args = parse_args()

    port = args.port or autodetect_port()
    if port is None:
        sys.stderr.write(
            "ERROR: no serial port given and autodetection failed.\n"
            "       Try `ls /dev/cu.*` (macOS) or `ls /dev/tty*` (Linux)\n"
            "       and pass --port /dev/cu.usbmodem...\n"
        )
        sys.exit(2)

    out_path = Path(
        args.out
        or f"readings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    print(f"[log] port = {port}")
    print(f"[log] baud = {args.baud}")
    print(f"[log] file = {out_path.resolve()}")
    print(f"[log] Ctrl-C to stop\n")

    ser = open_serial(port, args.baud)

    is_new = not out_path.exists()
    fp = out_path.open("a", newline="")
    writer = csv.writer(fp)
    if is_new:
        writer.writerow([
            "timestamp_iso",
            "t_c", "rh_pct", "p_hpa", "gas_kohm",
            "pm1", "pm2_5", "pm10",
        ])
        fp.flush()

    # State: collect one BME reading and (optionally) one HM reading per cycle.
    # Write the row when an HM line arrives OR when ~3.5s elapse with only
    # a BME line (handles the Basic kit, which never emits HM lines).
    pending = {}
    last_seen = time.time()
    FLUSH_TIMEOUT = 3.5  # seconds; the firmware reads every 5s

    def write_row():
        if not pending:
            return
        writer.writerow([
            pending.get("ts", ""),
            pending.get("t_c", ""),
            pending.get("rh_pct", ""),
            pending.get("p_hpa", ""),
            pending.get("gas_kohm", ""),
            pending.get("pm1", ""),
            pending.get("pm2_5", ""),
            pending.get("pm10", ""),
        ])
        fp.flush()
        print(
            f"[log] wrote  "
            f"t={pending.get('t_c', '-')}°C  "
            f"rh={pending.get('rh_pct', '-')}%  "
            f"p={pending.get('p_hpa', '-')}hPa  "
            f"gas={pending.get('gas_kohm', '-')}kΩ  "
            f"pm1={pending.get('pm1', '-')}  "
            f"pm25={pending.get('pm2_5', '-')}  "
            f"pm10={pending.get('pm10', '-')}"
        )
        pending.clear()

    def on_sigint(_sig, _frame):
        print("\n[log] stopping — flushing CSV...")
        write_row()
        fp.close()
        try:
            ser.close()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, on_sigint)

    while True:
        try:
            raw = ser.readline()
        except serial.SerialException as e:
            sys.stderr.write(f"[log] serial error ({e}). Reconnecting...\n")
            try:
                ser.close()
            except Exception:
                pass
            time.sleep(2)
            ser = open_serial(port, args.baud)
            continue

        line = raw.decode("utf-8", errors="replace").rstrip()

        # No data this poll — flush a pending row if it's been waiting too long.
        if not line:
            if pending and (time.time() - last_seen) > FLUSH_TIMEOUT:
                write_row()
            continue

        m = BME_RE.search(line)
        if m:
            # If we already had a BME row pending (Basic kit case), write it
            # before starting a new one.
            if pending:
                write_row()
            pending["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            pending["t_c"] = float(m.group(1))
            pending["rh_pct"] = float(m.group(2))
            pending["p_hpa"] = float(m.group(3))
            pending["gas_kohm"] = float(m.group(4))
            last_seen = time.time()
            continue

        m = HM_RE.search(line)
        if m:
            pending["pm1"] = int(m.group(1))
            pending["pm2_5"] = int(m.group(2))
            pending["pm10"] = int(m.group(3))
            write_row()
            last_seen = time.time()
            continue

        # Anything else (boot banner, I2C scan results, "NOT FOUND" messages,
        # blank cycle separators) — echo to stdout for visibility, don't parse.
        print(f"[log] (info) {line}")


if __name__ == "__main__":
    main()
