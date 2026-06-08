#!/usr/bin/env python3
"""Offline tests for the AQICN + PurpleAir source adapters in generate.py.

No network: we monkeypatch generate._get_json with captured-shape payloads
(modeled on the live WAQI + PurpleAir responses) and assert the normalized
output. Run:  python3 test_sources.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as g

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


# --- _aqi_to_pm25: boundary points on the (pre-2024) EPA PM2.5 table ----------
check("aqi 0 -> 0.0",    g._aqi_to_pm25(0) == 0.0,    g._aqi_to_pm25(0))
check("aqi 50 -> 12.0",  g._aqi_to_pm25(50) == 12.0,  g._aqi_to_pm25(50))
check("aqi 100 -> 35.4", g._aqi_to_pm25(100) == 35.4, g._aqi_to_pm25(100))
check("aqi 150 -> 55.4", g._aqi_to_pm25(150) == 55.4, g._aqi_to_pm25(150))
check("aqi None -> None", g._aqi_to_pm25(None) is None)
check("aqi '75' midband ~23.6", abs(g._aqi_to_pm25("75") - 23.6) < 0.2, g._aqi_to_pm25("75"))


# --- fake transport -----------------------------------------------------------
WAQI_BOUNDS = {"status": "ok", "data": [
    {"lat": -8.6039, "lon": 115.178, "uid": -519205,
     "aqi": "50", "station": {"name": "Kabupaten Badung Sempidi"}},
]}
WAQI_FEED = {"status": "ok", "data": {
    "aqi": 50, "idx": -519205,
    "city": {"geo": [-8.6039, 115.178], "name": "Kabupaten Badung Sempidi",
             "url": "https://aqicn.org/city/indonesia/bali/badung"},
    "iaqi": {"pm25": {"v": 50}, "t": {"v": 27.3}, "h": {"v": 70}},
    "time": {"iso": "2026-06-08T14:00:00+08:00"},
}}
PA_SENSORS = {
    "fields": ["sensor_index", "name", "latitude", "longitude",
               "pm2.5", "pm2.5_60minute", "humidity", "temperature", "last_seen"],
    "data": [
        [36601, "Jimbaran by Lumi Clinic", -8.7912, 115.1674, 0.6, 0.5, 55, 88, 1749369552],
        [46949, "Klungkung by Lumi Clinic", -8.5336, 115.3997, 41.0, 40.4, 60, 86, 1749369472],
    ],
}
AG_WORLD = [
    {"locationId": 77247, "locationName": "Tonja - Nafas", "publicLocationName": "Tonja - Nafas",
     "latitude": -8.632781, "longitude": 115.229004, "offline": False,
     "pm01": 20.0, "pm02": 28.5, "pm10": 31.8, "atmp": 31.4, "rhum": 65.3,
     "timestamp": "2026-06-08T07:18:04.000Z", "publicPlaceUrl": "https://app.airgradient.com/place/x"},
    {"locationId": 77245, "locationName": "Pemogan - Nafas", "publicLocationName": "Pemogan - Nafas",
     "latitude": -8.707819, "longitude": 115.205047, "offline": True,
     "pm02": None, "pm10": None, "atmp": None, "rhum": None,
     "timestamp": "2026-06-08T05:00:00.000Z"},
    {"locationId": 999, "locationName": "Bangkok HQ", "publicLocationName": "Bangkok HQ",
     "latitude": 13.7563, "longitude": 100.5018, "offline": False, "pm02": 40.0,
     "timestamp": "2026-06-08T07:00:00.000Z"},  # outside Bali bbox -> must be filtered
]


def fake_get_json(url, headers=None):
    if "map/bounds" in url:
        return WAQI_BOUNDS
    if "/feed/@" in url:
        return WAQI_FEED
    if "purpleair" in url or "/sensors?" in url:
        return PA_SENSORS
    if "world/locations" in url or "airgradient" in url:
        return AG_WORLD
    raise AssertionError(f"unexpected url {url}")


g._get_json = fake_get_json
g.AQICN_TOKEN = "test-token"
g.PURPLEAIR_KEY = "test-key"
g.PURPLEAIR_IDS = [36601, 46949]

# --- AQICN --------------------------------------------------------------------
aq = g.fetch_aqicn()
check("aqicn returns 1 station", len(aq) == 1, len(aq))
if aq:
    s = aq[0]
    check("aqicn id", s["id"] == "aqicn--519205", s["id"])
    check("aqicn source", s["source"] == "aqicn")
    check("aqicn pm25 converted 50->12.0", s["reading"]["pm25"] == 12.0, s["reading"]["pm25"])
    check("aqicn raw aqi kept", s["reading"]["aqi"] == 50, s["reading"]["aqi"])
    check("aqicn pm25_from_aqi flag", s["reading"]["pm25_from_aqi"] is True)
    check("aqicn temp/rh real", s["reading"]["temp"] == 27.3 and s["reading"]["rh"] == 70)
    check("aqicn coords", abs(s["lat"] + 8.6039) < 1e-6 and abs(s["lng"] - 115.178) < 1e-6)
    check("aqicn pm25 != raw aqi (conversion actually ran)", s["reading"]["pm25"] != s["reading"]["aqi"])

# --- PurpleAir ----------------------------------------------------------------
pa = g.fetch_purpleair()
check("purpleair returns 2 sensors", len(pa) == 2, len(pa))
if len(pa) == 2:
    a, b = pa
    check("pa id", a["id"] == "purpleair-36601", a["id"])
    check("pa uses 60min avg (0.5 not 0.6)", a["reading"]["pm25"] == 0.5, a["reading"]["pm25"])
    check("pa klungkung pm25 40.4", b["reading"]["pm25"] == 40.4, b["reading"]["pm25"])
    check("pa temp F->C (88F~31.1C)", abs(a["reading"]["temp"] - 31.1) < 0.2, a["reading"]["temp"])
    check("pa rh passthrough", a["reading"]["rh"] == 55)
    check("pa lastReading iso", isinstance(a["lastReading"], str) and a["lastReading"].endswith("+00:00"))

# --- AirGradient (keyless; Bali-bbox filter; offline handling) -----------------
g.AIRGRADIENT_ENABLED = True
ag = g.fetch_airgradient()
check("airgradient returns 2 Bali (Bangkok filtered out)", len(ag) == 2, len(ag))
if len(ag) == 2:
    tonja = [x for x in ag if x["rawId"] == 77247][0]
    pemog = [x for x in ag if x["rawId"] == 77245][0]
    check("ag id", tonja["id"] == "airgradient-77247", tonja["id"])
    check("ag source", tonja["source"] == "airgradient")
    check("ag pm25 from pm02 (28.5)", tonja["reading"]["pm25"] == 28.5, tonja["reading"]["pm25"])
    check("ag temp from atmp", tonja["reading"]["temp"] == 31.4, tonja["reading"]["temp"])
    check("ag name carries Nafas provenance", "Nafas" in tonja["name"], tonja["name"])
    check("ag offline kept with pm25=None", pemog["offline"] is True and pemog["reading"]["pm25"] is None)
g.AIRGRADIENT_ENABLED = False
check("airgradient disabled -> []", g.fetch_airgradient() == [])
g.AIRGRADIENT_ENABLED = True

# --- gating: no key -> clean skip ---------------------------------------------
g.AQICN_TOKEN = ""
g.PURPLEAIR_KEY = ""
check("aqicn skips with no token", g.fetch_aqicn() == [])
check("purpleair skips with no key", g.fetch_purpleair() == [])

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
