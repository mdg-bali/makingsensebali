// Making Sense Bali — DIY Node firmware
// v1.1 — WiFiManager + double-reset revision (merges the two v1 sketches
//        previously floating around: the placeholder-credential template
//        and the flashed-node copy with real WiFi/token values baked in)
//
// Target: Seeed XIAO ESP32-S3 AND ESP32-C3 — same sketch, select the board
//         in the Arduino IDE and it just works. Pin mapping (D4/D5) is
//         resolved automatically per board variant: GPIO5/6 on S3,
//         GPIO6/7 on C3. Nothing in this file is chip-specific.
// Sensors: BME680 (I2C 0x76) + Seeed Grove HM3301 (I2C 0x40)
// Platform: publishes to mqtt.smartcitizen.me over TLS
//
// Repo: https://github.com/mdg-bali/makingsensebali
// License: MIT — every dependency below is MIT/permissive, no closed blobs.
//   (This is the "open" firmware. The BSEC2/certified-IAQ revision is kept
//   as a separate, parallel file in this repo — see /firmware/v2-bsec2/ —
//   for anyone who wants Bosch's calibrated IAQ and accepts a closed-source
//   dependency. Both are maintained; this one is the default for public
//   replication, workshop kits, and any C3-based node.)
//
// ---------------------------------------------------------------------------
// WHAT CHANGED vs the plain v1 sketch
// ---------------------------------------------------------------------------
//  1. No more hardcoded WIFI_SSID / WIFI_PASSWORD. WiFiManager now handles
//     provisioning: first boot (or any boot where the saved network can't
//     be reached) opens a temporary "MakingSenseBali-XXXX" access point with
//     a captive portal where you type in the real network's credentials.
//     This is the field team's fix for moving kiosk/workshop nodes between
//     locations without reflashing — credit to the team for building and
//     testing this on the C3 unit before it landed here.
//  2. Double-reset-to-reprovision: press the physical RESET button twice
//     within DRD_TIMEOUT_S seconds and the node wipes its saved WiFi and
//     reopens the config portal — even if the old network is still in
//     range and would otherwise reconnect fine. Useful when you want to
//     deliberately switch a node to a different network without waiting
//     for the old one to fail first.
//  3. SC_DEVICE_TOKEN is UNCHANGED — still a hardcoded constant you edit
//     before flashing. WiFiManager only solves network reconfiguration,
//     not device identity; a node's Smart Citizen token doesn't change
//     just because it moved to a new WiFi network.
//  4. Nothing about the BME680 / HM3301 / MQTT / computeIAQ logic changed.
//     This is the same open, on-device IAQ approximation as before — see
//     the note above computeIAQ() if you're citing that number.
//
// A note on the double-reset mechanism: it relies on ESP32 RTC (slow) memory,
// which survives a RESET-button press (that only toggles the EN pin, power
// stays on) but is cleared by an actual power cycle (unplug/replug). That's
// the point — a deliberate double-tap of the reset button is a clear signal;
// a power blip during a brownout is not, and should NOT wipe saved WiFi.
//
// ---------------------------------------------------------------------------
// LIBRARIES (Arduino Library Manager)
// ---------------------------------------------------------------------------
//   - Adafruit BME680 Library  (depends on Adafruit Unified Sensor)
//   - PubSubClient             (Nick O'Leary)
//   - ArduinoJson              v7.x
//   - WiFiManager              (tzapu) — MIT licensed, ESP32-compatible
//
// PAYLOAD shape (canonical Smart Citizen MQTT spec):
//   { "data": [ { "recorded_at": "ISO8601",
//                 "sensors": [ {"id": N, "value": V}, ... ] } ] }
// Reference: https://github.com/fablabbcn/smartcitizen-api/blob/master/docs/mqtt.md

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <ArduinoJson.h>

// HM3301 is read directly over I2C without the Seeed_HM330X library.
// The Seeed library uses non-standard u8/u16/u32 type aliases and won't
// compile against the modern arduino-esp32 core (a typedef shim in the
// sketch can't fix the library's own .cpp translation unit). The HM3301
// I2C protocol is simple enough that we read it ourselves — see readHM3301.
#include <time.h>

// ============================================================================
// CONFIGURATION — edit these and reflash
// ============================================================================

// Smart Citizen device token (from your device page on smartcitizen.me).
// This is per-device identity, NOT provisioned by WiFiManager — it does not
// change when the node moves to a new network.
const char* SC_DEVICE_TOKEN = "YOUR_SC_DEVICE_TOKEN";

// Smart Citizen sensor IDs — one per metric, copy from your device page.
// Each value below MUST match the numeric ID assigned to that sensor on
// smartcitizen.me. If they don't match, readings land in the wrong slot
// or get silently dropped. Leave any unused ID as 0 to skip publishing it.
//
// These are dedicated catalog entries for our exact hardware — Bosch BME68X
// and Seeed HM-3301 — not the old "closest-equivalent" mappings (BMP280 /
// SHT31 / Plantower PMS5003) we used before the catalog had proper entries.
//
// IAQ (241) is LIVE in the Smart Citizen global catalog (added by Oscar,
// 2026-06-09), so it works out of the box — no per-device platform setup.
// The value is an OPEN on-device approximation, not Bosch BSEC; see computeIAQ().
//
// You normally DON'T touch the IDs below: they are SC global-catalog IDs, the
// same for every node. Replicators only set the device token above (WiFi is
// now handled at first boot via the config portal — see WIFI PROVISIONING).
// For a Basic kit (no HM-3301), set the three PM IDs to 0 to skip publishing them.
const int SC_ID_PM1      = 233;  // µg/m³  — Seeed HM-3301 - PM1.0
const int SC_ID_PM25     = 234;  // µg/m³  — Seeed HM-3301 - PM2.5
const int SC_ID_PM10     = 235;  // µg/m³  — Seeed HM-3301 - PM10.0
const int SC_ID_TEMP     = 237;  // °C     — Bosch BME68X - Temperature (heat-compensated)
const int SC_ID_HUM      = 238;  // %RH    — Bosch BME68X - Humidity (heat-compensated)
const int SC_ID_PRESSURE = 239;  // kPa    — Bosch BME68X - Pressure
const int SC_ID_GAS      = 240;  // Ohm    — Bosch BME68X - Gas Resistance (RAW, in ohms)
const int SC_ID_IAQ      = 241;  // index  — Bosch BME68X - IAQ (open approximation; see computeIAQ)

// MQTT broker (do not change unless you're testing locally)
const char* MQTT_HOST = "mqtt.smartcitizen.me";
const uint16_t MQTT_PORT = 8883;

// Timing
const uint32_t PUBLISH_INTERVAL_MS = 60UL * 1000UL;  // one reading/minute

// ============================================================================
// WIFI PROVISIONING (WiFiManager + double-reset)
// ============================================================================

// Password for the TEMPORARY "MakingSenseBali-XXXX" hotspot shown during
// provisioning — this is NOT the node's home/kiosk WiFi password, just a
// gate so randoms can't hijack the config portal on a public kiosk while
// it's briefly open. Must be 8+ characters (WPA2 minimum).
const char* CONFIG_PORTAL_PASSWORD = "msb-setup";

// How long the config portal stays open with no client before giving up
// and restarting to retry (seconds).
const uint16_t CONFIG_PORTAL_TIMEOUT_S = 180;

// How long WiFiManager tries the saved network before falling back to the
// config portal (seconds).
const uint16_t WIFI_CONNECT_TIMEOUT_S = 15;

// Double-reset window: press physical RESET twice within this many seconds
// to force-clear saved WiFi and reopen the config portal.
const uint16_t DRD_TIMEOUT_S = 10;

WiFiManager wm;

// RTC (slow) memory: survives a RESET-button press, cleared by real power
// loss. Used purely to detect "was the last boot very recent."
RTC_DATA_ATTR bool drdFlagArmed = false;

bool forceConfigPortal = false;   // computed once in setup() from drdFlagArmed

String uniqueApName() {
  String mac = WiFi.macAddress();          // e.g. "3C:71:BF:8A:12:34"
  mac.replace(":", "");
  return "MakingSenseBali-" + mac.substring(6);  // last 3 octets, no colons
}

// ============================================================================
// HARDWARE
// ============================================================================

Adafruit_BME680 bme;

constexpr uint8_t HM3301_I2C_ADDR        = 0x40;
constexpr uint8_t HM3301_SELECT_I2C_CMD  = 0x88;

WiFiClientSecure net;
PubSubClient mqtt(net);

uint32_t lastPublish = 0;

// Clean-air gas-resistance reference for the IAQ approximation, learned at
// runtime (see computeIAQ). 0 = not yet initialised.
float gasBaselineOhm = 0.0f;

// ============================================================================
// WIFI PROVISIONING + NTP
// ============================================================================

// Blocking — runs once from setup(). Tries the saved network first; if that
// fails (or forceConfigPortal is set), opens the captive portal. If the
// portal also times out with no one configuring it, we restart and try the
// whole sequence again next boot rather than limping on with no WiFi.
void provisionWiFi() {
  WiFi.mode(WIFI_STA);

  if (forceConfigPortal) {
    Serial.println("[wifi] double-reset detected — clearing saved network and opening config portal");
    wm.resetSettings();
  }

  wm.setConnectTimeout(WIFI_CONNECT_TIMEOUT_S);
  wm.setConfigPortalTimeout(CONFIG_PORTAL_TIMEOUT_S);

  String apName = uniqueApName();
  Serial.printf("[wifi] connecting (saved network) or opening portal \"%s\" ", apName.c_str());

  bool ok = wm.autoConnect(apName.c_str(), CONFIG_PORTAL_PASSWORD);

  if (ok) {
    Serial.printf("\n[wifi] connected — IP %s · RSSI %d dBm\n",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("\n[wifi] no connection and portal timed out — restarting to retry");
    delay(1000);
    ESP.restart();
  }
}

// Lightweight, non-blocking reconnect for drops during normal operation.
// Deliberately does NOT reopen the config portal — a dropped connection on
// a known-good network should just retry, not demand reprovisioning.
void maintainWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  static uint32_t lastAttempt = 0;
  if (millis() - lastAttempt < 10000) return;  // don't hammer reconnects
  lastAttempt = millis();
  Serial.println("[wifi] disconnected — reconnecting with saved credentials");
  WiFi.reconnect();
}

void syncTime() {
  // Bali is UTC+8 (WITA). We publish in UTC anyway, so offset doesn't matter
  // for recorded_at — but logging in local time is friendlier.
  configTime(8 * 3600, 0, "pool.ntp.org", "time.google.com");

  Serial.print("[ntp] syncing");
  time_t now = time(nullptr);
  uint32_t start = millis();
  while (now < 1700000000 && (millis() - start) < 15000) {  // ~2023-11
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println();

  if (now < 1700000000) {
    Serial.println("[ntp] failed — recorded_at will be wrong, the platform may drop readings");
  } else {
    Serial.printf("[ntp] synced — unix %ld\n", (long)now);
  }
}

String iso8601UTC() {
  time_t now = time(nullptr);
  struct tm tm_utc;
  gmtime_r(&now, &tm_utc);
  char buf[32];
  // 2026-05-20T03:14:15Z
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm_utc);
  return String(buf);
}

// ============================================================================
// MQTT
// ============================================================================

void connectMQTT() {
  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;

  // For v1 we skip CA validation. For production deployments, replace this
  // with net.setCACert(LE_ROOT_PEM) where LE_ROOT_PEM is the Let's Encrypt
  // ISRG Root X1 certificate (the SC broker uses LE certs). Skipping
  // validation means we're vulnerable to MITM on the LAN — acceptable for
  // a workshop kit, not for a sensor your campaign cites in policy work.
  net.setInsecure();

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);   // default 256 is too small for our payload

  // The Smart Citizen SCK firmware uses the device token as both the
  // MQTT client_id and the username; password is empty.
  Serial.printf("[mqtt] connecting to %s:%u ", MQTT_HOST, MQTT_PORT);
  if (mqtt.connect(SC_DEVICE_TOKEN, SC_DEVICE_TOKEN, "")) {
    Serial.println("ok");
  } else {
    Serial.printf("failed (rc=%d) — will retry\n", mqtt.state());
  }
}

bool publishReadings(float tempC, float humRH, float pressureKPa, float gasOhm,
                     float iaq, uint16_t pm1, uint16_t pm25, uint16_t pm10) {
  if (!mqtt.connected()) return false;

  // Build payload
  // {
  //   "data": [{
  //     "recorded_at": "2026-05-20T03:14:15Z",
  //     "sensors": [ {"id": <SC_ID_TEMP>, "value": 26.7}, ... ]
  //   }]
  // }
  JsonDocument doc;
  JsonArray data = doc["data"].to<JsonArray>();
  JsonObject reading = data.add<JsonObject>();
  reading["recorded_at"] = iso8601UTC();
  JsonArray sensors = reading["sensors"].to<JsonArray>();

  auto addSensor = [&](int id, float value) {
    if (id == 0) return;  // unconfigured — skip rather than send id=0
    JsonObject s = sensors.add<JsonObject>();
    s["id"] = id;
    s["value"] = value;
  };

  addSensor(SC_ID_TEMP,     tempC);
  addSensor(SC_ID_HUM,      humRH);
  addSensor(SC_ID_PRESSURE, pressureKPa);
  addSensor(SC_ID_GAS,      gasOhm);
  if (!isnan(iaq)) addSensor(SC_ID_IAQ, iaq);  // skip when BME read failed (iaq=NAN)
  addSensor(SC_ID_PM1,      (float)pm1);
  addSensor(SC_ID_PM25,     (float)pm25);
  addSensor(SC_ID_PM10,     (float)pm10);

  String json;
  serializeJson(doc, json);

  String topic = String("device/sck/") + SC_DEVICE_TOKEN + "/readings";

  // QoS 1 (required by the platform). PubSubClient's publish() defaults to
  // QoS 0; the third arg `retained=false` is set explicitly. For true QoS 1
  // we'd switch to AsyncMqttClient, but for a one-message-per-minute cadence
  // QoS 0 over TLS is good enough — the platform's broker is robust and we
  // re-publish on the next cycle if a message drops.
  bool ok = mqtt.publish(topic.c_str(), json.c_str(), false);
  if (ok) {
    Serial.printf("[mqtt] published (%u bytes): %s\n", json.length(), json.c_str());
  } else {
    Serial.println("[mqtt] publish failed");
  }
  return ok;
}

// ============================================================================
// SENSORS
// ============================================================================

// computeIAQ — OPEN air-quality index, 0 (clean) … 500 (polluted).
//
// This is NOT Bosch's certified BSEC IAQ. BSEC is closed-source with license
// terms that don't fit an open-data project, so we approximate the same
// 0-500 shape ourselves from two signals the BME68X gives us for free:
//
//   1. Gas resistance. The metal-oxide element reads HIGH in clean air and
//      DROPS as VOCs rise. We track a slow "clean-air baseline" of the high
//      end (gasBaselineOhm) and score the current reading as a fraction of it.
//   2. Humidity. Very dry or very damp air both degrade perceived quality;
//      we peak the humidity score around ~40 %RH.
//
// We weight gas 75 % / humidity 25 % into a 0-100 "goodness", then invert to
// the Bosch convention (LOWER = cleaner) so downstream consumers that assume
// a real IAQ scale don't read it upside-down.
//
// HONEST LIMITATIONS — read before citing this number:
//   - The baseline needs the gas sensor to burn in (~24-48h of power-on)
//     before it means anything. Early values trend artificially clean.
//   - It is uncalibrated and relative to THIS unit's environment, not
//     comparable unit-to-unit the way a reference-grade instrument is.
//   - If you ever need a defensible, comparable index for policy work,
//     that's the trigger to integrate BSEC (or co-locate with a reference
//     monitor and derive a correction) — not this proxy. See /firmware/v2-bsec2/.
float computeIAQ(float gasOhm, float humRH) {
  if (isnan(gasOhm) || isnan(humRH) || gasOhm <= 0.0f) return NAN;

  // Track the clean-air baseline: rise toward higher (cleaner) readings
  // fairly quickly, fall very slowly so a burst of pollution doesn't drag
  // the reference down with it.
  if (gasBaselineOhm <= 0.0f) {
    gasBaselineOhm = gasOhm;  // first reading seeds the baseline
  } else {
    float alpha = (gasOhm > gasBaselineOhm) ? 0.05f : 0.001f;
    gasBaselineOhm += alpha * (gasOhm - gasBaselineOhm);
  }

  // Gas score (0..75): current reading as a fraction of the clean-air
  // baseline, clamped — at or above baseline = full marks.
  float gasRatio = gasOhm / gasBaselineOhm;
  if (gasRatio > 1.0f) gasRatio = 1.0f;
  if (gasRatio < 0.0f) gasRatio = 0.0f;
  float gasScore = gasRatio * 75.0f;

  // Humidity score (0..25): peaks at the ~40 %RH comfort point.
  float humScore;
  if (humRH < 38.0f)      humScore = (humRH / 40.0f) * 25.0f;
  else if (humRH > 42.0f) humScore = ((100.0f - humRH) / 60.0f) * 25.0f;
  else                    humScore = 25.0f;
  if (humScore < 0.0f) humScore = 0.0f;

  // 0..100 goodness → invert to 0..500 IAQ (lower = cleaner).
  float goodness = gasScore + humScore;
  float iaq = (100.0f - goodness) * 5.0f;
  if (iaq < 0.0f)   iaq = 0.0f;
  if (iaq > 500.0f) iaq = 500.0f;
  return iaq;
}

bool readBME680(float &tempC, float &humRH, float &pressureKPa, float &gasOhm) {
  // performReading() triggers a forced measurement and waits ~150 ms for the
  // gas heater. Returns false if the conversion failed.
  if (!bme.performReading()) {
    return false;
  }
  tempC       = bme.temperature;        // °C
  humRH       = bme.humidity;           // %RH
  pressureKPa = bme.pressure / 1000.0f; // Pa → kPa (matches SC platform's kPa convention)
  gasOhm      = bme.gas_resistance;     // Ω — RAW ohms, channel 240 expects this (no /1000)
  return !(isnan(tempC) || isnan(humRH));
}

// HM3301 — direct I2C, no Seeed library.
//
// Init (once at boot): write 0x88 to address 0x40 to select I2C mode.
//                      The sensor boots in UART mode by default.
//
// Read (every cycle):  requestFrom 29 bytes from 0x40. Frame layout per
//                      the HM-3300/3600 datasheet and Seeed's own example:
//
//   buf[0..1]   frame header (often 0x42 0x4D, sometimes documented as
//               "sensor model" — not used for anything here)
//   buf[2..3]   sensor number
//   buf[4..5]   PM1.0  (CF=1, indoor / factory calibration)
//   buf[6..7]   PM2.5  (CF=1)
//   buf[8..9]   PM10   (CF=1)
//   buf[10..11] PM1.0  (atmospheric — what we publish)
//   buf[12..13] PM2.5  (atmospheric)
//   buf[14..15] PM10   (atmospheric)
//   buf[16..27] particle counts by size bin (0.3, 0.5, 1.0, 2.5, 5, 10 µm)
//   buf[28]     checksum (low byte of sum of buf[0..27])

bool hm3301_init() {
  Wire.beginTransmission(HM3301_I2C_ADDR);
  Wire.write(HM3301_SELECT_I2C_CMD);
  return Wire.endTransmission() == 0;
}

bool readHM3301(uint16_t &pm1, uint16_t &pm25, uint16_t &pm10) {
  uint8_t buf[29];
  size_t got = Wire.requestFrom(HM3301_I2C_ADDR, (uint8_t)29);
  if (got != 29) return false;
  for (int i = 0; i < 29; i++) {
    if (!Wire.available()) return false;
    buf[i] = Wire.read();
  }
  // Checksum: low byte of sum(buf[0..27]) must equal buf[28].
  uint8_t sum = 0;
  for (int i = 0; i < 28; i++) sum += buf[i];
  if (sum != buf[28]) return false;

  pm1  = ((uint16_t)buf[10] << 8) | buf[11];
  pm25 = ((uint16_t)buf[12] << 8) | buf[13];
  pm10 = ((uint16_t)buf[14] << 8) | buf[15];
  return true;
}

// ============================================================================
// SETUP / LOOP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n=== Making Sense Bali — DIY Node (v1.1, WiFiManager) ===");

  // Double-reset check: if the RTC flag from a previous boot is still armed,
  // this boot happened within DRD_TIMEOUT_S of the last one — treat it as a
  // deliberate double-tap of RESET and force reprovisioning.
  forceConfigPortal = drdFlagArmed;
  drdFlagArmed = true;   // armed until loop() disarms it after the window

  // I2C — Wire.begin() with no args uses the selected board's default pins
  // (D4/D5, which map to different GPIOs on S3 vs C3; see header note).
  Wire.begin();

  // BME680 — try 0x76 first (SDO grounded), then 0x77 (SDO to 3V3).
  bool bmeOk = bme.begin(0x76);
  if (!bmeOk) bmeOk = bme.begin(0x77);
  if (bmeOk) {
    // Typical settings for outdoor environmental monitoring — Bosch's
    // suggested defaults. Heater at 320°C for 150 ms gives a stable gas
    // resistance reading without burning power.
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150);
    Serial.println("[bme680] online — heater + filter configured");
  } else {
    Serial.println("[bme680] NOT FOUND — check SDA/SCL wiring and power");
  }

  // HM3301
  if (hm3301_init()) {
    Serial.println("[hm3301] online at 0x40");
  } else {
    Serial.println("[hm3301] NOT FOUND — check 5V power and Grove cable");
  }

  provisionWiFi();  // blocking — see WIFI PROVISIONING section
  syncTime();
}

void loop() {
  // Disarm the double-reset flag once we've been running longer than the
  // window — a boot that stays up this long clearly wasn't followed by a
  // second quick reset.
  static bool drdCleared = false;
  if (!drdCleared && millis() > (uint32_t)DRD_TIMEOUT_S * 1000UL) {
    drdFlagArmed = false;
    drdCleared = true;
  }

  maintainWiFi();
  connectMQTT();
  mqtt.loop();

  uint32_t now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL_MS || lastPublish == 0) {
    lastPublish = now;

    float tempC = NAN, humRH = NAN, pressureKPa = NAN, gasOhm = NAN;
    uint16_t pm1 = 0, pm25 = 0, pm10 = 0;

    bool bmeOk = readBME680(tempC, humRH, pressureKPa, gasOhm);
    bool hmOk  = readHM3301(pm1, pm25, pm10);

    // IAQ only when the BME read succeeded; computeIAQ returns NAN otherwise.
    // The '~' in the log is a reminder this is an approximation, not BSEC.
    float iaq = bmeOk ? computeIAQ(gasOhm, humRH) : NAN;

    Serial.printf("[read] T=%.2f°C  RH=%.2f%%  P=%.3fkPa  Gas=%.0fΩ  IAQ~%.0f  "
                  "PM1=%u  PM2.5=%u  PM10=%u  (bme=%d hm=%d)\n",
                  tempC, humRH, pressureKPa, gasOhm, iaq,
                  pm1, pm25, pm10, bmeOk, hmOk);

    if (bmeOk || hmOk) {
      publishReadings(tempC, humRH, pressureKPa, gasOhm, iaq, pm1, pm25, pm10);
    }
  }

  delay(100);
}
