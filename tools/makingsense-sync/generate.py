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


def _load_env_file() -> None:
    """Load KEY=VALUE lines from a gitignored `.env` next to this script into
    os.environ (without overriding values already set, e.g. by the plist). Keeps
    API keys out of the git-tracked plist + repo, and survives plist re-deploys."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(p) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass


_load_env_file()

# ----------------------------------------------------------------------------
# Config (env-overridable; defaults match the Bali reference deployment)
# ----------------------------------------------------------------------------
REPO_DIR      = os.environ.get("MSB_REPO_DIR", os.path.expanduser("~/makingsensebali"))
SCK_IDS       = [int(x) for x in os.environ.get("MSB_SCK_IDS", "19236,19600,19618,19651").split(",") if x.strip()]
BBOX          = os.environ.get("MSB_BBOX", "114.4,-8.95,115.75,-8.05")  # minLon,minLat,maxLon,maxLat
SC_API        = os.environ.get("MSB_SC_API", "https://api.smartcitizen.me/v0")
OPENAQ_API    = os.environ.get("MSB_OPENAQ_API", "https://api.openaq.org/v3")
OPENAQ_KEY    = os.environ.get("MSB_OPENAQ_KEY", "")
# AQICN / World Air Quality Index — one free token (aqicn.org/data-platform/token)
# covers the official KLHK government monitor + whatever else WAQI aggregates in
# the Bali bbox. This is the highest-value external source: OpenAQ is effectively
# empty in Bali (its only two island stations have been offline for >6 months).
AQICN_API     = os.environ.get("MSB_AQICN_API", "https://api.waqi.info")
AQICN_TOKEN   = os.environ.get("MSB_AQICN_TOKEN", "")
# Optional comma-separated WAQI station UIDs to pin (e.g. "-519205"). Bali's WAQI
# stations are unlisted — discovery is flaky — so pinning the known KLHK monitor
# guarantees it even if the bounds query comes back empty.
AQICN_STATIONS = [s.strip() for s in os.environ.get("MSB_AQICN_STATIONS", "").split(",") if s.strip()]
# PurpleAir — free X-API-Key (develop.purpleair.com). We read a known set of Bali
# community sensor indices; defaults are the two Lumi Clinic devices the site map
# already knows about (Jimbaran 36601, Klungkung 46949).
PURPLEAIR_API = os.environ.get("MSB_PURPLEAIR_API", "https://api.purpleair.com/v1")
PURPLEAIR_KEY = os.environ.get("MSB_PURPLEAIR_KEY", "")
PURPLEAIR_IDS = [int(x) for x in os.environ.get("MSB_PURPLEAIR_IDS", "36601,46949").split(",") if x.strip()]
# AirGradient public open-data API — KEYLESS. Returns every public AirGradient
# location worldwide; we filter to the Bali bbox. In Bali these are the Nafas
# Foundation sensors (Tonja, Pemogan, …). This is the sovereign way to get Nafas
# data: documented, public, no scrape, no token, no ToS grey area.
AIRGRADIENT_API = os.environ.get("MSB_AIRGRADIENT_API", "https://api.airgradient.com/public/api/v1")
AIRGRADIENT_ENABLED = os.environ.get("MSB_AIRGRADIENT", "1") not in ("0", "", "false")
# --- Average-quality filter -------------------------------------------------
# Network + area AVERAGES should reflect realistic OUTDOOR ambient, so indoor /
# filtered sensors (which read near-zero) and faulty outliers are tagged
# excluded_from_avg and skipped by the stats — but STILL shown on the map.
INDOOR_FLOOR       = float(os.environ.get("MSB_INDOOR_FLOOR", "5"))         # µg/m³; below this outdoors is implausible in Bali
OUTLIER_K          = float(os.environ.get("MSB_OUTLIER_K", "4.0"))          # robust (MAD) multiplier for outlier bounds
OUTLIER_MIN_SPREAD = float(os.environ.get("MSB_OUTLIER_MIN_SPREAD", "12"))  # µg/m³ floor on the robust spread (small-N guard)
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
    # Smart Citizen sits behind Cloudflare, which 403s the default
    # "Python-urllib/x.y" User-Agent. Send a normal browser UA (curl works for
    # the same reason — the block is UA-specific, not IP- or auth-based).
    h = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
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


# --- Sovereign local store (PLANETAI zero-layer ingestion on the NAS) --------
# When MSB_LOCAL_STORE points at the ingestor's readings/ dir, our own kits are
# read straight off the NAS — no cloud in the path. Empty by default, so this is
# a no-op in the cloud Action and only activates where the store is mounted
# (the NAS, or the mini over its NAS mount). See PLANETAI-local-ingest/.
LOCAL_STORE = os.environ.get("MSB_LOCAL_STORE", "")


def fetch_local_store() -> list:
    """Read readings/<device>/latest.json from the local ingestion store.
    Coords come from the payload if present, else from an optional sites.json
    ({device: {name, lat, lng}}) in the store dir. Uncalibrated kits are still
    shown on the map but flagged (in flag_quality) so they don't enter the
    averages/index — real as Detect, not index-grade until colocated."""
    if not LOCAL_STORE:
        return []
    if not os.path.isdir(LOCAL_STORE):
        log(f"  local store: {LOCAL_STORE} not present — skipping")
        return []
    sites = {}
    sp = os.path.join(LOCAL_STORE, "sites.json")
    if os.path.exists(sp):
        try:
            sites = json.load(open(sp))
        except Exception as e:
            log(f"  local store: sites.json unreadable ({e})")
    out = []
    for dev in sorted(os.listdir(LOCAL_STORE)):
        latest = os.path.join(LOCAL_STORE, dev, "latest.json")
        if not os.path.isfile(latest):
            continue
        try:
            r = json.load(open(latest))
        except Exception as e:
            log(f"  local {dev}: bad latest.json ({e})")
            continue
        site = sites.get(dev, {})
        lat = r.get("lat") if r.get("lat") is not None else site.get("lat")
        lon = r.get("lng") if r.get("lng") is not None else r.get("lon")
        if lon is None:
            lon = site.get("lng") if site.get("lng") is not None else site.get("lon")
        if lat is None or lon is None:
            log(f"  local {dev}: no coords (add it to sites.json) — skipping")
            continue
        out.append({
            "id": f"local-{dev}", "rawId": dev,
            "source": "local", "sourceLabel": "Making Sense Bali (local)",
            "name": r.get("name") or site.get("name") or dev,
            "lat": float(lat), "lng": float(lon),
            "lastReading": r.get("received_at") or r.get("ts"),
            "reading": {
                "pm25": r.get("pm25"), "pm10": r.get("pm10"),
                "temp": r.get("temp"), "rh": r.get("rh"), "noise": r.get("noise"),
            },
            "calibrated": bool(r.get("calibrated", False)),
            "detailsUrl": "https://mdg-bali.github.io/makingsensebali/dashboard/",
        })
    log(f"  local store: {len(out)} sovereign kit(s)")
    return out


def fetch_sensors() -> list:
    out = []
    out.extend(fetch_local_store())   # our own kits first — sovereign, no cloud
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
    # AQICN + PurpleAir (each fully isolated: a failure logs and returns [],
    # never blocks the kits or each other).
    out.extend(fetch_aqicn())
    out.extend(fetch_purpleair())
    out.extend(fetch_airgradient())
    flag_quality(out)
    return out


# ----------------------------------------------------------------------------
# 1a. EXTERNAL NETWORKS (AQICN / WAQI + PurpleAir)
# Each returns the same normalized shape as the Smart Citizen kits so the rest
# of the pipeline (sensors.json, area PM2.5 rollups, the map) treats them
# uniformly. Both are best-effort and gated on a key being present.
# ----------------------------------------------------------------------------

# US EPA PM2.5 AQI breakpoints (the pre-2024 table WAQI computes its AQI with,
# and the one the public PM2.5 µg/m³ colour scales are drawn against). We invert
# it to turn WAQI's AQI sub-index back into a µg/m³ concentration, so AQICN
# stations are directly comparable to the kits' real readings and the WHO line.
_PM25_AQI_BP = [
    (0,   50,  0.0,   12.0),
    (51,  100, 12.1,  35.4),
    (101, 150, 35.5,  55.4),
    (151, 200, 55.5,  150.4),
    (201, 300, 150.5, 250.4),
    (301, 400, 250.5, 350.4),
    (401, 500, 350.5, 500.4),
]


def _aqi_to_pm25(aqi):
    """Invert a US-EPA PM2.5 AQI sub-index to a µg/m³ concentration."""
    try:
        a = float(aqi)
    except (TypeError, ValueError):
        return None
    for ilo, ihi, clo, chi in _PM25_AQI_BP:
        if ilo <= a <= ihi:
            return round(clo + (a - ilo) * (chi - clo) / (ihi - ilo), 1)
    if a > 500:  # above the table — linear extrapolation off the top band
        return round(500.4 + (a - 500) * (500.4 - 350.5) / (500 - 401), 1)
    return None


def fetch_aqicn() -> list:
    """AQICN / World Air Quality Index. WAQI reports PM2.5 as a US-AQI sub-index,
    NOT µg/m³ — we convert it back (see _aqi_to_pm25) and keep the raw AQI in the
    reading for transparency. Discovers stations dynamically via the map/bounds
    box, then pulls each station's feed for the pollutant + met values."""
    if not AQICN_TOKEN:
        log("  AQICN: no MSB_AQICN_TOKEN — skipping")
        return []
    # BBOX is "minLon,minLat,maxLon,maxLat"; WAQI wants latlng="lat1,lng1,lat2,lng2".
    try:
        lon1, lat1, lon2, lat2 = [float(x) for x in BBOX.split(",")]
    except Exception:
        log("  AQICN: bad BBOX, skipping"); return []
    latlng = f"{lat1},{lon1},{lat2},{lon2}"

    def _in_bbox(la, lo):
        return (la is not None and lo is not None
                and lat1 <= la <= lat2 and lon1 <= lo <= lon2)

    # Discover station UIDs. Bali's WAQI stations are unlisted: plain search/geo
    # and the v1 map/bounds all miss them — only the v2 map/bounds with
    # networks=all surfaces them. We then merge any UIDs pinned via
    # MSB_AQICN_STATIONS (the KLHK monitor is reachable by UID even when the
    # bounds query is empty), dedupe, and bbox-filter each feed to drop the Java
    # strays that the nearby/search lists otherwise pull in.
    uids = []
    try:
        j = _get_json(f"{AQICN_API}/v2/map/bounds/?latlng={latlng}&networks=all&token={AQICN_TOKEN}")
        for st in ((j.get("data") or []) if isinstance(j, dict) else []):
            if st.get("uid") is not None:
                uids.append(st["uid"])
        log(f"  AQICN: {len(uids)} station(s) from bounds")
    except Exception as e:
        log(f"  AQICN: bounds FAILED {type(e).__name__}: {str(e)[:80]}")
    for s in AQICN_STATIONS:
        try:
            u = int(s)
        except ValueError:
            continue
        if u not in uids:
            uids.append(u)

    out = []
    for uid in uids[:30]:
        try:
            fd = _get_json(f"{AQICN_API}/feed/@{uid}/?token={AQICN_TOKEN}")
            d = (fd.get("data") or {}) if isinstance(fd, dict) else {}
            if not isinstance(d, dict):
                continue
            geo = (d.get("city") or {}).get("geo") or []
            la = float(geo[0]) if len(geo) >= 2 else None
            lo = float(geo[1]) if len(geo) >= 2 else None
            if not _in_bbox(la, lo):
                continue
            iaqi = d.get("iaqi") or {}
            pm25 = _aqi_to_pm25((iaqi.get("pm25") or {}).get("v"))
            out.append({
                "id": f"aqicn-{uid}", "rawId": uid,
                "source": "aqicn", "sourceLabel": "AQICN",
                "name": (d.get("city") or {}).get("name") or f"AQICN #{uid}",
                "lat": la, "lng": lo,
                "lastReading": (d.get("time") or {}).get("iso"),
                "reading": {
                    "pm25": pm25,
                    "pm10": None,  # WAQI pm10 is also an AQI sub-index — not converted
                    "temp": (iaqi.get("t") or {}).get("v"),
                    "rh":   (iaqi.get("h") or {}).get("v"),
                    "aqi":  d.get("aqi"),               # raw overall US-AQI, kept for transparency
                    "pm25_from_aqi": pm25 is not None,  # pm25 above is converted, not measured
                },
                "detailsUrl": (d.get("city") or {}).get("url") or f"https://aqicn.org/station/@{uid}",
            })
        except Exception as e:
            log(f"  AQICN feed @{uid}: FAILED {type(e).__name__}: {str(e)[:60]}")
    log(f"  AQICN: {len(out)} station(s) normalized")
    return out


def fetch_purpleair() -> list:
    """PurpleAir community sensors (real µg/m³ PM2.5). Reads a fixed set of Bali
    sensor indices. Temperature is °F at the raw sensor — converted to °C."""
    if not PURPLEAIR_KEY:
        log("  PurpleAir: no MSB_PURPLEAIR_KEY — skipping")
        return []
    if not PURPLEAIR_IDS:
        return []
    fields = "name,latitude,longitude,pm2.5,pm2.5_60minute,humidity,temperature,last_seen,location_type"
    show = ",".join(str(i) for i in PURPLEAIR_IDS)
    url = f"{PURPLEAIR_API}/sensors?show_only={show}&fields={urllib.parse.quote(fields)}"
    out = []
    try:
        j = _get_json(url, {"X-API-Key": PURPLEAIR_KEY})
        cols = j.get("fields") or []
        idx = {name: i for i, name in enumerate(cols)}

        def col(row, name):
            i = idx.get(name)
            return row[i] if (i is not None and i < len(row)) else None

        for row in (j.get("data") or []):
            lat, lon = col(row, "latitude"), col(row, "longitude")
            if lat is None or lon is None:
                continue
            pm25 = col(row, "pm2.5_60minute")
            if pm25 is None:
                pm25 = col(row, "pm2.5")
            tF = col(row, "temperature")
            temp = round((tF - 32) * 5 / 9, 1) if isinstance(tF, (int, float)) else None
            ls = col(row, "last_seen")
            last_iso = (datetime.fromtimestamp(ls, tz=timezone.utc).isoformat()
                        if isinstance(ls, (int, float)) else None)
            sid = col(row, "sensor_index")
            if sid is None:  # PurpleAir returns sensor_index as the first column
                sid = row[0] if row else None
            out.append({
                "id": f"purpleair-{sid}", "rawId": sid,
                "source": "purpleair", "sourceLabel": "PurpleAir",
                "indoor": (col(row, "location_type") == 1),  # PurpleAir: 0=outside, 1=inside
                "name": col(row, "name") or f"PurpleAir #{sid}",
                "lat": float(lat), "lng": float(lon),
                "lastReading": last_iso,
                "reading": {
                    "pm25": round(pm25, 1) if isinstance(pm25, (int, float)) else None,
                    "pm10": None,
                    "temp": temp,
                    "rh":   col(row, "humidity"),
                },
                "detailsUrl": f"https://map.purpleair.com/?select={sid}",
            })
        log(f"  PurpleAir: {len(out)} sensor(s)")
    except Exception as e:
        log(f"  PurpleAir: FAILED {type(e).__name__}: {str(e)[:80]}")
    return out


def fetch_airgradient() -> list:
    """AirGradient public open-data API (keyless). The /world endpoint returns
    every public AirGradient location worldwide; we filter to the Bali bbox.
    In Bali these are the Nafas Foundation sensors. pm02 is a real µg/m³ PM2.5
    concentration; atmp/rhum are ambient °C / %. Offline locations are kept (so
    the map can show them dark) but carry pm25=None, so they don't skew the
    area roll-ups. Sovereign: documented public API, no scrape, no token."""
    if not AIRGRADIENT_ENABLED:
        log("  AirGradient: disabled (MSB_AIRGRADIENT=0)")
        return []
    try:
        lon1, lat1, lon2, lat2 = [float(x) for x in BBOX.split(",")]
    except Exception:
        log("  AirGradient: bad BBOX, skipping"); return []
    out = []
    try:
        j = _get_json(f"{AIRGRADIENT_API}/world/locations/measures/current")
        rows = j if isinstance(j, list) else (j.get("data") or j.get("locations") or [])
        n = 0
        for r in rows:
            if not isinstance(r, dict):
                continue
            try:
                lat = float(r.get("latitude")); lon = float(r.get("longitude"))
            except (TypeError, ValueError):
                continue
            if not (lat1 <= lat <= lat2 and lon1 <= lon <= lon2):
                continue
            n += 1
            lid = r.get("locationId")
            offline = bool(r.get("offline"))
            pm25 = r.get("pm02")
            pm10 = r.get("pm10")
            out.append({
                "id": f"airgradient-{lid}", "rawId": lid,
                "source": "airgradient", "sourceLabel": "AirGradient",
                "name": r.get("publicLocationName") or r.get("locationName") or f"AirGradient #{lid}",
                "lat": lat, "lng": lon,
                "offline": offline,
                "lastReading": r.get("timestamp"),
                "reading": {
                    "pm25": round(pm25, 1) if (not offline and isinstance(pm25, (int, float))) else None,
                    "pm10": round(pm10, 1) if (not offline and isinstance(pm10, (int, float))) else None,
                    "temp": r.get("atmp") if not offline else None,
                    "rh":   r.get("rhum") if not offline else None,
                },
                "detailsUrl": r.get("publicPlaceUrl") or "https://www.airgradient.com/map/",
            })
        log(f"  AirGradient: {n} Bali location(s)")
    except Exception as e:
        log(f"  AirGradient: FAILED {type(e).__name__}: {str(e)[:80]}")
    return out


# ----------------------------------------------------------------------------
# 1c. QUALITY FLAG — exclude indoor + outlier sensors from the AVERAGES
# (the map still shows every sensor; this only changes the network/area stats).
# ----------------------------------------------------------------------------
_INDOOR_NAME_HINTS = ("office", "indoor", "in-door", "dalam ruang")


def _median(xs: list):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def flag_quality(sensors: list) -> None:
    """Tag each sensor excluded_from_avg (+ exclusion_reason) so the network and
    area AVERAGES skip indoor and unrealistic sensors. The map still shows them.
      • indoor: explicit flag (e.g. PurpleAir location_type=inside), an
        office/indoor name, or a reading below INDOOR_FLOOR — Bali outdoor
        ambient is essentially never that clean, so it's filtered/indoor air.
      • outlier: a reading far from the network's robust centre (median ± K·MAD,
        with a spread floor). Catches faulty sensors either direction; a genuine
        cluster of high readings survives because the sensors agree with each other."""
    for s in sensors:
        pm = (s.get("reading") or {}).get("pm25")
        pm = pm if isinstance(pm, (int, float)) else None
        s["_pm"] = pm
        reason = None
        if s.get("source") == "local" and s.get("calibrated") is False:
            reason = "uncalibrated"   # shown on the map, kept out of averages/index
        elif s.get("indoor") is True:
            reason = "indoor"
        elif any(h in (s.get("name") or "").lower() for h in _INDOOR_NAME_HINTS):
            reason = "indoor"
        elif pm is not None and pm < INDOOR_FLOOR:
            reason = "indoor_suspected"
        s["excluded_from_avg"] = reason is not None
        s["exclusion_reason"] = reason
    # Robust outlier pass over the sensors not already excluded.
    vals = [s["_pm"] for s in sensors if s["_pm"] is not None and not s["excluded_from_avg"]]
    med = _median(vals)
    if med is not None and len(vals) >= 4:
        mad = _median([abs(v - med) for v in vals]) or 0.0
        spread = max(1.4826 * mad, OUTLIER_MIN_SPREAD)
        lo, hi = med - OUTLIER_K * spread, med + OUTLIER_K * spread
        for s in sensors:
            if s["excluded_from_avg"] or s["_pm"] is None:
                continue
            if s["_pm"] < lo or s["_pm"] > hi:
                s["excluded_from_avg"] = True
                s["exclusion_reason"] = "outlier_low" if s["_pm"] < lo else "outlier_high"
    for s in sensors:
        s.pop("_pm", None)
    reasons = [s["exclusion_reason"] for s in sensors if s.get("excluded_from_avg")]
    log(f"quality: {len(reasons)}/{len(sensors)} excluded from averages ({', '.join(reasons) or 'none'})")


def write_sensors(sensors: list) -> None:
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "count": len(sensors), "sensors": sensors}
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "sensors.json"), "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log(f"sensors.json: {len(sensors)} sensors")


# ----------------------------------------------------------------------------
# 1b. HISTORY (per-kit PM2.5 time series, pre-baked)
# The site's charts must NOT call Smart Citizen's /readings endpoint live — it
# is slow/hangs through the Cloudflare worker. We fetch it here on the mini
# (direct egress to api.smartcitizen.me, no worker) and write a static
# data/history.json the charts load instantly. 24h @ 1h rollup + 7d @ 3h.
# ----------------------------------------------------------------------------
def _sck_pm25_sensor_id(detail: dict):
    sensors = (detail.get("data") or {}).get("sensors") or detail.get("sensors") or []
    for s in sensors:
        nm = (s.get("name") or "")
        if ("PM2.5" in nm or "PM 2.5" in nm) and s.get("id") is not None:
            return s["id"]
    return None


def _fetch_readings(dev_id, sensor_id, frm, to, rollup):
    q = urllib.parse.urlencode({"sensor_id": sensor_id, "from": frm, "to": to, "rollup": rollup})
    j = _get_json(f"{SC_API}/devices/{dev_id}/readings?{q}")
    raw = (j.get("readings") if isinstance(j, dict) else j) or []
    out = []
    for r in raw:
        ts = val = None
        if isinstance(r, list) and len(r) >= 2:
            ts, val = r[0], r[1]
        elif isinstance(r, dict):
            ts, val = (r.get("recorded_at") or r.get("timestamp")), r.get("value")
        try:
            v = float(val)
        except (TypeError, ValueError):
            continue
        if ts:
            out.append([ts, round(v, 1)])
    return out


def fetch_history() -> dict:
    now = datetime.now(timezone.utc)
    to = now.isoformat()
    h24_from = (now - timedelta(hours=24)).isoformat()
    d7_from  = (now - timedelta(days=7)).isoformat()
    sensors = {}
    for sid in SCK_IDS:
        try:
            d = _get_json(f"{SC_API}/devices/{sid}")
            pm = _sck_pm25_sensor_id(d)
            if pm is None:
                log(f"  history {sid}: no PM2.5 channel"); continue
            h24 = _fetch_readings(sid, pm, h24_from, to, "1h")
            d7  = _fetch_readings(sid, pm, d7_from,  to, "3h")
            sensors[str(sid)] = {
                "name": d.get("name") or f"Device {sid}",
                "rawId": d.get("id", sid),
                "pm25_sensor_id": pm,
                "h24": h24, "d7": d7,
            }
            log(f"  history {sid}: 24h={len(h24)} 7d={len(d7)}")
        except Exception as e:
            log(f"  history {sid}: FAILED {type(e).__name__}: {str(e)[:80]}")
    return sensors


def write_history(sensors: dict) -> None:
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "sensors": sensors}
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "history.json"), "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log(f"history.json: {len(sensors)} kit histories")


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
        if s.get("excluded_from_avg"):   # skip indoor / outlier sensors in the rollup
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
        # Stay in sync with pushes from elsewhere before pushing our data commit.
        # The aq-reporter pushes approved profiles to this same branch and both it
        # and this job write data/reports/index.json, so a plain rebase used to
        # conflict and stall for hours (the 13-commit backlog of 2026-06-08).
        # --strategy-option=ours keeps the reporter's report index on conflict (it
        # owns reports); our sensors/history/areas don't conflict and apply cleanly,
        # and index.json re-converges next cycle. So the pipeline self-heals instead
        # of stalling. (Proper long-term fix: single-writer ownership of index.json.)
        try:
            git("pull", "--rebase", "--strategy-option=ours", "origin", "main")
        except subprocess.CalledProcessError as e:
            log(f"publish: pull --rebase failed, aborting + retrying next cycle: {e.stderr.strip()[:120]}")
            try: git("rebase", "--abort")
            except subprocess.CalledProcessError: pass
            return
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
        write_history(fetch_history())
    except Exception as e:
        log(f"history stage FAILED: {type(e).__name__}: {str(e)[:120]}")
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
