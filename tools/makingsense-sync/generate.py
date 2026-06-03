#!/usr/bin/env python3
"""
Making Sense Bali — static data generator (runs on the mini).

Why this exists
---------------
The public site is static (GitHub Pages) but was doing LIVE Smart Citizen API
fan-out on every visit (slow), and approved citizen reports never travelled
from the NAS to the repo (so the map was stale). This job fixes both: it
pre-bakes the data into static JSON the site loads instantly, and it carries
approved reports out to the public map. It runs on the mini because the mini
has real internet egress (the NAS is firewalled) and runs exo locally for the
optional neighbourhood narrative.

Each cycle:
  1. SENSORS  → fetch the known Smart Citizen kits + OpenAQ in the Bali bbox,
                write data/sensors.json (the snapshot the site loads first).
  2. REPORTS  → rsync approved Murmurations profiles from the NAS, copy into
                data/reports/, regenerate index.json.
  3. AREAS    → roll up reports by locality (counts, categories, dominant tags,
                max severity) + nearby PM2.5, with an OPTIONAL 2-sentence exo
                narrative, write data/areas.json.
  4. PUBLISH  → git add data/ ; commit ; push  (no-op if nothing changed).

Design rules: stdlib only, never crash the cron (each stage is isolated and
logged), and never block publishing of one stage on the failure of another.

Config is via env (see SETUP.md). Run `python3 generate.py --dry-run` to do
everything except the git push.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

# ----------------------------------------------------------------------------
# Config (env-overridable; defaults match the Bali reference deployment)
# ----------------------------------------------------------------------------
REPO_DIR      = os.environ.get("MSB_REPO_DIR", os.path.expanduser("~/makingsensebali"))
SCK_IDS       = [int(x) for x in os.environ.get("MSB_SCK_IDS", "19236,19600,19618,19651").split(",") if x.strip()]
BBOX          = os.environ.get("MSB_BBOX", "114.4,-8.95,115.75,-8.05")  # minLon,minLat,maxLon,maxLat
SC_API        = os.environ.get("MSB_SC_API", "https://api.smartcitizen.me/v0")
OPENAQ_API    = os.environ.get("MSB_OPENAQ_API", "https://api.openaq.org/v3")
OPENAQ_KEY    = os.environ.get("MSB_OPENAQ_KEY", "")
# NAS report source for rsync (mini→NAS over Tailscale; key set up by operator)
NAS_RSYNC_SRC = os.environ.get("MSB_NAS_RSYNC_SRC", "")  # e.g. fablabbali@tx-nas-bali:/volume1/docker/aq-reporter/data/profiles/
# NAS published-photo source — the EXIF-stripped public photos the bot writes on
# approve+publish. These must travel to data/reports/photos/ for the map to show them.
NAS_PHOTOS_SRC = os.environ.get("MSB_NAS_PHOTOS_SRC", "")  # e.g. fablabbali@tx-nas-bali:/volume1/docker/aq-reporter/data/profile_photos/
# exo (local on the mini) for the optional area narrative
EXO_URL       = os.environ.get("MSB_EXO_URL", "http://127.0.0.1:52415/v1/chat/completions")
EXO_MODEL     = os.environ.get("MSB_EXO_MODEL", "mlx-community/gemma-4-e4b-it-6bit")
USE_NARRATIVE = os.environ.get("MSB_NARRATIVE", "1") not in ("0", "", "false")
HTTP_TIMEOUT  = float(os.environ.get("MSB_HTTP_TIMEOUT", "20"))
WHO_PM25_24H  = 15.0

DATA_DIR    = os.path.join(REPO_DIR, "data")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
WITA        = timezone(timedelta(hours=8))


def log(msg: str) -> None:
    print(f"[{datetime.now(WITA).strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def _get_json(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


# ----------------------------------------------------------------------------
# 1. SENSORS
# ----------------------------------------------------------------------------
def _sck_reading(detail: dict) -> dict:
    sensors = (detail.get("data") or {}).get("sensors") or detail.get("sensors") or []
    def find(names):
        for s in sensors:
            nm = (s.get("name") or "")
            if any(n in nm for n in names) and isinstance(s.get("value"), (int, float)):
                return s["value"]
        return None
    return {
        "pm25":  find(["PM 2.5", "PM2.5"]),
        "pm10":  find(["PM 10", "PM10"]),
        "temp":  find(["Air Temperature", "Temperature"]),
        "rh":    find(["Relative Humidity", "Humidity"]),
        "noise": find(["Noise"]),
    }


def fetch_sensors() -> list:
    out = []
    for sid in SCK_IDS:
        try:
            d = _get_json(f"{SC_API}/devices/{sid}")
            lat = d.get("latitude") or (d.get("location") or {}).get("latitude")
            lon = d.get("longitude") or (d.get("location") or {}).get("longitude")
            if lat is None or lon is None:
                log(f"  SCK {sid}: no coords, skipping"); continue
            out.append({
                "id": f"sck-{d.get('id', sid)}", "rawId": d.get("id", sid),
                "source": "smartcitizen", "sourceLabel": "Smart Citizen",
                "name": d.get("name") or f"Device {sid}",
                "lat": float(lat), "lng": float(lon),
                "lastReading": (d.get("data") or {}).get("recorded_at") or d.get("last_reading_at"),
                "reading": _sck_reading(d),
                "detailsUrl": f"https://smartcitizen.me/kits/{d.get('id', sid)}",
            })
            log(f"  SCK {sid}: ok")
        except Exception as e:
            log(f"  SCK {sid}: FAILED {type(e).__name__}: {str(e)[:80]}")
    # OpenAQ (best-effort; only if a key is configured)
    if OPENAQ_KEY:
        try:
            url = f"{OPENAQ_API}/locations?bbox={BBOX}&limit=100"
            j = _get_json(url, {"X-API-Key": OPENAQ_KEY})
            for loc in j.get("results", []):
                coords = loc.get("coordinates") or {}
                if coords.get("latitude") is None:
                    continue
                out.append({
                    "id": f"openaq-{loc.get('id')}", "source": "openaq",
                    "sourceLabel": "OpenAQ", "name": loc.get("name") or "OpenAQ station",
                    "lat": coords["latitude"], "lng": coords["longitude"],
                    "reading": {}, "lastReading": (loc.get("datetimeLast") or {}).get("utc"),
                })
            log(f"  OpenAQ: {len(j.get('results', []))} stations")
        except Exception as e:
            log(f"  OpenAQ: FAILED {type(e).__name__}: {str(e)[:80]}")
    return out


def write_sensors(sensors: list) -> None:
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "count": len(sensors), "sensors": sensors}
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "sensors.json"), "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log(f"sensors.json: {len(sensors)} sensors")


# ----------------------------------------------------------------------------
# 2. REPORTS (pull approved Murmurations profiles from the NAS)
# ----------------------------------------------------------------------------
def sync_reports() -> int:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    if NAS_RSYNC_SRC:
        try:
            # Pull only profile JSONs; --delete keeps the public set in step with
            # what's approved on the NAS. SSH key auth (no password) is required.
            subprocess.run(
                ["rsync", "-az", "--include=AQ_*.json", "--exclude=*",
                 NAS_RSYNC_SRC, REPORTS_DIR + "/"],
                check=True, timeout=60,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
        except Exception as e:
            log(f"  report rsync FAILED ({type(e).__name__}: {str(e)[:80]}) — keeping existing reports")
    else:
        log("  MSB_NAS_RSYNC_SRC unset — skipping report pull (using whatever is in data/reports/)")
    # Pull the EXIF-stripped public photos (bot writes them on approve+publish).
    # photo_path in each profile is "photos/<id>.jpg" relative to data/reports/.
    if NAS_PHOTOS_SRC:
        photos_dir = os.path.join(REPORTS_DIR, "photos")
        os.makedirs(photos_dir, exist_ok=True)
        try:
            subprocess.run(
                ["rsync", "-az", "--include=*.jpg", "--include=*.jpeg", "--exclude=*",
                 NAS_PHOTOS_SRC, photos_dir + "/"],
                check=True, timeout=120,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
            log(f"  photos synced → {photos_dir}")
        except Exception as e:
            log(f"  photo rsync FAILED ({type(e).__name__}: {str(e)[:80]})")
    profiles = sorted(f for f in os.listdir(REPORTS_DIR) if f.startswith("AQ_") and f.endswith(".json"))
    idx = {"count": len(profiles), "profiles": profiles,
           "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(REPORTS_DIR, "index.json"), "w") as f:
        json.dump(idx, f, indent=2)
    log(f"reports: {len(profiles)} profiles indexed")
    return len(profiles)


# ----------------------------------------------------------------------------
# 3. AREAS (roll up reports by locality + nearby sensor PM2.5 + optional exo)
# ----------------------------------------------------------------------------
SEV_RANK = {"low": 1, "medium": 2, "high": 3}


def _load_reports() -> list:
    out = []
    for fn in os.listdir(REPORTS_DIR):
        if not (fn.startswith("AQ_") and fn.endswith(".json")):
            continue
        try:
            out.append(json.load(open(os.path.join(REPORTS_DIR, fn))))
        except Exception:
            pass
    return out


def _area_pm25(lat: float, lon: float, sensors: list) -> float | None:
    """Mean PM2.5 of sensors within ~5km of the area centroid."""
    vals = []
    for s in sensors:
        pm = (s.get("reading") or {}).get("pm25")
        if pm is None:
            continue
        # crude planar distance in degrees (~0.045deg ≈ 5km at this latitude)
        if abs(s["lat"] - lat) < 0.045 and abs(s["lng"] - lon) < 0.045:
            vals.append(pm)
    return round(sum(vals) / len(vals), 1) if vals else None


def _narrative(locality: str, reps: list, pm: float | None) -> str | None:
    if not USE_NARRATIVE:
        return None
    lines = []
    for r in reps[:8]:
        ai = r.get("ai_analysis") or {}
        lines.append(f"- {r.get('pollution_category','?')} ({ai.get('severity','?')}): "
                     f"{(ai.get('description') or '').strip()}")
    sensor_line = (f"PM2.5 {pm} ug/m3 (WHO 24h guideline {WHO_PM25_24H:.0f})"
                   if pm is not None else "no nearby air sensor")
    prompt = (
        f"Write exactly two short, grounded sentences for residents about environmental "
        f"conditions in {locality}, Bali. Use only the data below. No advice, no filler, "
        f"no preamble.\n\nCitizen reports (recent):\n" + "\n".join(lines) +
        f"\n\nAir sensor: {sensor_line}."
    )
    try:
        payload = json.dumps({"model": EXO_MODEL,
                              "messages": [{"role": "user", "content": prompt}],
                              "max_tokens": 140, "temperature": 0.4}).encode()
        req = urllib.request.Request(EXO_URL, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            txt = json.load(r)["choices"][0]["message"]["content"].strip()
        # Guard against degenerate output (model echoing a tag / a single word).
        # Better to show the structured rollup with no narrative than a bad one.
        if len(txt) < 40 or " " not in txt:
            log(f"  narrative for {locality}: degenerate output {txt!r}, skipping")
            return None
        return txt
    except Exception as e:
        log(f"  narrative for {locality} FAILED ({type(e).__name__}: {str(e)[:60]})")
        return None


def build_areas(sensors: list) -> None:
    reports = _load_reports()
    by_loc: dict[str, list] = {}
    for r in reports:
        by_loc.setdefault(r.get("locality") or "Unknown", []).append(r)

    areas = []
    for locality, reps in sorted(by_loc.items()):
        cats: dict[str, int] = {}
        tags: dict[str, int] = {}
        max_sev = 0
        lat = sum(r.get("latitude", 0) for r in reps) / len(reps)
        lon = sum(r.get("longitude", 0) for r in reps) / len(reps)
        for r in reps:
            c = r.get("pollution_category", "other")
            cats[c] = cats.get(c, 0) + 1
            ai = r.get("ai_analysis") or {}
            for ind in (ai.get("indicators") or []):
                tags[ind] = tags.get(ind, 0) + 1
            max_sev = max(max_sev, SEV_RANK.get(ai.get("severity"), 0))
        pm = _area_pm25(lat, lon, sensors)
        areas.append({
            "locality": locality, "lat": round(lat, 6), "lon": round(lon, 6),
            "report_count": len(reps),
            "categories": dict(sorted(cats.items(), key=lambda kv: -kv[1])),
            "top_tags": [t for t, _ in sorted(tags.items(), key=lambda kv: -kv[1])[:6]],
            "max_severity": {1: "low", 2: "medium", 3: "high"}.get(max_sev),
            "pm25": pm,
            "summary": _narrative(locality, reps, pm),
        })
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "areas": areas}
    with open(os.path.join(DATA_DIR, "areas.json"), "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log(f"areas.json: {len(areas)} localities")


# ----------------------------------------------------------------------------
# 4. PUBLISH
# ----------------------------------------------------------------------------
def publish(dry_run: bool) -> None:
    def git(*args):
        return subprocess.run(["git", "-C", REPO_DIR, *args],
                              check=True, capture_output=True, text=True)
    try:
        git("add", "data/")
        status = git("status", "--porcelain", "data/").stdout.strip()
        if not status:
            log("publish: no changes"); return
        if dry_run:
            log(f"publish: DRY-RUN, would commit:\n{status}"); return
        git("commit", "-m", f"data: auto-sync {datetime.now(WITA).strftime('%Y-%m-%d %H:%M WITA')}")
        git("push", "origin", "main")
        log("publish: pushed")
    except subprocess.CalledProcessError as e:
        log(f"publish FAILED: {e.stderr.strip()[:200]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="do everything except git push")
    args = ap.parse_args()
    log(f"=== makingsense-sync start (repo={REPO_DIR}) ===")
    try:
        write_sensors(fetch_sensors())
    except Exception as e:
        log(f"sensors stage FAILED: {type(e).__name__}: {str(e)[:120]}")
    try:
        sync_reports()
    except Exception as e:
        log(f"reports stage FAILED: {type(e).__name__}: {str(e)[:120]}")
    try:
        # reload sensors we just wrote, for area PM matching
        s = json.load(open(os.path.join(DATA_DIR, "sensors.json"))).get("sensors", []) \
            if os.path.exists(os.path.join(DATA_DIR, "sensors.json")) else []
        build_areas(s)
    except Exception as e:
        log(f"areas stage FAILED: {type(e).__name__}: {str(e)[:120]}")
    publish(args.dry_run)
    log("=== done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
