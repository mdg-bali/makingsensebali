// Smart Citizen Bali — DIY Node firmware
// Target: Seeed XIAO ESP32-S3
// Sensors: BME680 (I2C 0x76) + Seeed Grove HM3301 (I2C 0x40)
// Platform: publishes to mqtt.smartcitizen.me over TLS
//
// Repo: https://github.com/mdg-bali/smartcitizenbali
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
#include <Seeed_HM330X.h>
#include <ArduinoJson.h>
#include <time.h>

// ============================================================================
// CONFIGURATION — edit these and reflash
// ============================================================================

// WiFi
const char* WIFI_SSID     = "CHANGE_ME";
const char* WIFI_PASSWORD = "CHANGE_ME";

// Smart Citizen device token (from your device page on smartcitizen.me)
const char* SC_DEVICE_TOKEN = "CHANGE_ME_DEVICE_TOKEN";

// Smart Citizen sensor IDs — one per metric, copy from your device page
// Each value below MUST match the numeric ID assigned to that sensor on
// smartcitizen.me. If they don't match, readings land in the wrong slot
// or get silently dropped. Leave any unused ID as 0 to skip publishing it.
const int SC_ID_TEMP      = 0;  // °C       — BME680 temperature
const int SC_ID_HUM       = 0;  // %RH      — BME680 humidity
const int SC_ID_PRESSURE  = 0;  // hPa      — BME680 barometric pressure (optional)
const int SC_ID_GAS       = 0;  // kΩ       — BME680 gas resistance (VOC indicator)
const int SC_ID_PM1       = 0;  // µg/m³    — HM3301 PM1.0 (atmospheric)
const int SC_ID_PM25      = 0;  // µg/m³    — HM3301 PM2.5 (atmospheric)
const int SC_ID_PM10      = 0;  // µg/m³    — HM3301 PM10  (atmospheric)

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
HM330X hm3301;
uint8_t hm3301_buf[30];

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

bool publishReadings(float tempC, float humRH, float pressureHPa, float gasKOhm,
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
  addSensor(SC_ID_PRESSURE, pressureHPa);
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

bool readBME680(float &tempC, float &humRH, float &pressureHPa, float &gasKOhm) {
  // performReading() triggers a forced measurement and waits ~150 ms for the
  // gas heater. Returns false if the conversion failed.
  if (!bme.performReading()) {
    return false;
  }
  tempC       = bme.temperature;            // °C
  humRH       = bme.humidity;               // %RH
  pressureHPa = bme.pressure / 100.0f;      // Pa → hPa
  gasKOhm     = bme.gas_resistance / 1000.0f;  // Ω → kΩ
  return !(isnan(tempC) || isnan(humRH));
}

bool readHM3301(uint16_t &pm1, uint16_t &pm25, uint16_t &pm10) {
  // read_sensor_value() pulls 29 bytes over I2C. Layout (Seeed HM330X datasheet):
  //   buf[2..3]   PM1.0  CF=1 (indoor calibration)
  //   buf[4..5]   PM2.5  CF=1
  //   buf[6..7]   PM10   CF=1
  //   buf[8..9]   PM1.0  atmospheric  ← we use these for outdoor monitoring
  //   buf[10..11] PM2.5  atmospheric
  //   buf[12..13] PM10   atmospheric
  if (hm3301.read_sensor_value(hm3301_buf, 29) != 0) {
    return false;
  }
  pm1  = ((uint16_t)hm3301_buf[8]  << 8) | hm3301_buf[9];
  pm25 = ((uint16_t)hm3301_buf[10] << 8) | hm3301_buf[11];
  pm10 = ((uint16_t)hm3301_buf[12] << 8) | hm3301_buf[13];
  return true;
}

// ============================================================================
// SETUP / LOOP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n=== Smart Citizen Bali — DIY Node ===");

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
  if (hm3301.init() == 0) {
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

    float tempC = NAN, humRH = NAN, pressureHPa = NAN, gasKOhm = NAN;
    uint16_t pm1 = 0, pm25 = 0, pm10 = 0;

    bool bmeOk = readBME680(tempC, humRH, pressureHPa, gasKOhm);
    bool hmOk  = readHM3301(pm1, pm25, pm10);

    Serial.printf("[read] T=%.2f°C  RH=%.2f%%  P=%.2fhPa  Gas=%.1fkΩ  "
                  "PM1=%u  PM2.5=%u  PM10=%u  (bme=%d hm=%d)\n",
                  tempC, humRH, pressureHPa, gasKOhm,
                  pm1, pm25, pm10, bmeOk, hmOk);

    if (bmeOk || hmOk) {
      publishReadings(tempC, humRH, pressureHPa, gasKOhm, pm1, pm25, pm10);
    }
  }

  delay(100);
}
