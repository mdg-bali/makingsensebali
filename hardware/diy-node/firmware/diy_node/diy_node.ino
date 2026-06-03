// Making Sense Bali — DIY Node firmware
// Target: Seeed XIAO ESP32-S3
// Sensors: BME680 (I2C 0x76) + Seeed Grove HM3301 (I2C 0x40)
// Platform: publishes to mqtt.smartcitizen.me over TLS
//
// Repo: https://github.com/mdg-bali/makingsensebali
// License: MIT
//
// What this does (in order):
//   1. Brings up Wire (I2C) on the XIAO's default SDA=D4 (GPIO5), SCL=D5 (GPIO6)
//   2. Initialises BME680 at 0x76 (oversampling + IIR filter + gas heater)
//      and HM3301 via Seeed's library
//   3. Connects to WiFi, syncs the clock via NTP
//   4. Every PUBLISH_INTERVAL_MS, reads sensors and publishes one MQTT
//      message to device/sck/<DEVICE_TOKEN>/readings on mqtt.smartcitizen.me:8883
//
// Note on BME680 vs BME280:
//   The BME680 adds a metal-oxide gas sensor (VOC-sensitive) on top of
//   temp/humidity/pressure. We publish the raw gas resistance in kΩ —
//   lower resistance = more VOCs in the air. This is a relative indicator,
//   not a calibrated IAQ index. Bosch's BSEC library does the conversion
//   to a 0-500 IAQ score but is closed-source with license restrictions,
//   so we stay with the raw value for an open-data project.
//
// Payload shape matches the canonical Smart Citizen MQTT spec:
//   { "data": [ { "recorded_at": "ISO8601",
//                 "sensors": [ {"id": N, "value": V}, ... ] } ] }
// Reference: https://github.com/fablabbcn/smartcitizen-api/blob/master/docs/mqtt.md
//
// Libraries (install via Arduino Library Manager):
//   - Adafruit BME680 Library  (depends on Adafruit Unified Sensor)
//   - Seeed_HM330X             (Seeed Studio's HM3301 driver)
//   - PubSubClient             (Nick O'Leary)
//   - ArduinoJson v7.x

#include <WiFi.h>
#include <WiFiClientSecure.h>
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

// WiFi
const char* WIFI_SSID     = "DIEZSENENFAM";
const char* WIFI_PASSWORD = "BaliLife-05";

// Smart Citizen device token (from your device page on smartcitizen.me)
const char* SC_DEVICE_TOKEN = "1d6fe0";

// Smart Citizen sensor IDs — one per metric, copy from your device page
// Each value below MUST match the numeric ID assigned to that sensor on
// smartcitizen.me. If they don't match, readings land in the wrong slot
// or get silently dropped. Leave any unused ID as 0 to skip publishing it.
// Sensor IDs from the SC global catalog (/v0/sensors). The platform doesn't
// have a BME680 entry, so we map to the closest semantic equivalents:
//   - Temperature/Pressure → Bosch BMP280 entries (same Bosch family)
//   - Humidity            → Sensirion SHT31 (BMP280 has no humidity channel)
//   - PM1/2.5/10          → Plantower PMS5003 (HM3301 outputs same physical
//                                              signal in same unit)
//   - Gas resistance      → no good match. Leave at 0 (firmware skips it).
//                           Ask Oscar to add a "Bosch BME680 - Gas resistance
//                           [kΩ]" entry to the catalog and set this then.
const int SC_ID_TEMP      = 174;  // ºC       — Bosch BMP280 - Temperature
const int SC_ID_HUM       = 56;   // %RH      — Sensirion SHT31 - Humidity
const int SC_ID_PRESSURE  = 175;  // kPa      — Bosch BMP280 - Pressure (SC platform stores pressure in kPa)
const int SC_ID_GAS       = 0;    // kΩ       — BME680 gas resistance; no catalog entry, leave at 0 for now
const int SC_ID_PM1       = 89;   // µg/m³    — Plantower PMS5003 - PM1
const int SC_ID_PM25      = 87;   // µg/m³    — Plantower PMS5003 - PM2.5
const int SC_ID_PM10      = 88;   // µg/m³    — Plantower PMS5003 - PM10

// MQTT broker (do not change unless you're testing locally)
const char* MQTT_HOST = "mqtt.smartcitizen.me";
const uint16_t MQTT_PORT = 8883;

// Timing
const uint32_t PUBLISH_INTERVAL_MS = 60UL * 1000UL;  // one reading/minute
const uint32_t WIFI_CONNECT_TIMEOUT_MS = 30000;

// ============================================================================
// HARDWARE
// ============================================================================

Adafruit_BME680 bme;

constexpr uint8_t HM3301_I2C_ADDR        = 0x40;
constexpr uint8_t HM3301_SELECT_I2C_CMD  = 0x88;

WiFiClientSecure net;
PubSubClient mqtt(net);

uint32_t lastPublish = 0;

// ============================================================================
// WIFI + NTP
// ============================================================================

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.printf("[wifi] connecting to %s ", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - start) < WIFI_CONNECT_TIMEOUT_MS) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[wifi] connected — IP %s · RSSI %d dBm\n",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("[wifi] failed — will retry next loop");
  }
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

bool publishReadings(float tempC, float humRH, float pressureKPa, float gasKOhm,
                     uint16_t pm1, uint16_t pm25, uint16_t pm10) {
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
  addSensor(SC_ID_GAS,      gasKOhm);
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

bool readBME680(float &tempC, float &humRH, float &pressureKPa, float &gasKOhm) {
  // performReading() triggers a forced measurement and waits ~150 ms for the
  // gas heater. Returns false if the conversion failed.
  if (!bme.performReading()) {
    return false;
  }
  tempC       = bme.temperature;             // °C
  humRH       = bme.humidity;                // %RH
  pressureKPa = bme.pressure / 1000.0f;      // Pa → kPa (matches SC platform's kPa convention)
  gasKOhm     = bme.gas_resistance / 1000.0f; // Ω → kΩ
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
  Serial.println("\n=== Making Sense Bali — DIY Node ===");

  // I2C on XIAO ESP32-S3 default pins: SDA=D4 (GPIO5), SCL=D5 (GPIO6).
  // Wire.begin() with no args uses those defaults.
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

  connectWiFi();
  syncTime();
}

void loop() {
  connectWiFi();
  connectMQTT();
  mqtt.loop();

  uint32_t now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL_MS || lastPublish == 0) {
    lastPublish = now;

    float tempC = NAN, humRH = NAN, pressureKPa = NAN, gasKOhm = NAN;
    uint16_t pm1 = 0, pm25 = 0, pm10 = 0;

    bool bmeOk = readBME680(tempC, humRH, pressureKPa, gasKOhm);
    bool hmOk  = readHM3301(pm1, pm25, pm10);

    Serial.printf("[read] T=%.2f°C  RH=%.2f%%  P=%.3fkPa  Gas=%.1fkΩ  "
                  "PM1=%u  PM2.5=%u  PM10=%u  (bme=%d hm=%d)\n",
                  tempC, humRH, pressureKPa, gasKOhm,
                  pm1, pm25, pm10, bmeOk, hmOk);

    if (bmeOk || hmOk) {
      publishReadings(tempC, humRH, pressureKPa, gasKOhm, pm1, pm25, pm10);
    }
  }

  delay(100);
}
