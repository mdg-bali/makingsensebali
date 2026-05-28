// Smart Citizen Bali — DIY Node SENSOR TEST
// Target: Seeed XIAO ESP32-S3
// Sensors: BME680 (I2C 0x76) + Seeed Grove HM3301 (I2C 0x40, Plus kit only)
//
// What this does:
//   Reads both sensors every 5 seconds and prints readings to Serial in
//   human-readable form. NO WiFi, NO MQTT, NO Smart Citizen connection.
//
//   Use this BEFORE flashing the full diy_node.ino — it verifies the
//   hardware works on its own, isolated from any platform setup. If this
//   sketch produces sensible readings, the kit is wired correctly and the
//   sensors are alive; if it doesn't, fix the hardware before touching
//   WiFi or MQTT.
//
// Works for both Basic and Plus kits:
//   - Basic (XIAO + BME680): you'll see "[hm3301] NOT FOUND" once at boot.
//     That's expected. Only the BME680 readings will appear in the loop.
//   - Plus (Basic + HM3301):  both sensors will be detected and printed.
//
// Quick start:
//   1. Arduino IDE → Tools → Board → "XIAO_ESP32S3"
//   2. Tools → Port → (the XIAO's serial port)
//   3. Upload this sketch
//   4. Tools → Serial Monitor, set baud to 115200
//   5. You should see an I2C scan and sensor readings within ~10 seconds
//
// Troubleshooting from serial output:
//   "[i2c] no devices found"
//     → SDA/SCL not connected, or sensors not powered. Check wiring.
//   "[bme680] NOT FOUND"
//     → BME680 not on the bus. Check 3V3 power, SDA/SCL pin assignment.
//        On many breakouts SDO must be tied to GND (for 0x76) or 3V3
//        (for 0x77). Both are probed.
//   "[hm3301] NOT FOUND" on a Plus kit
//     → HM3301 not on the bus. Check 5V power (1A USB chargers brown out),
//        check Grove cable, listen for the fan — if silent, no power.
//
// Libraries (install via Arduino Library Manager):
//   - Adafruit BME680 Library  (depends on Adafruit Unified Sensor)
//
// HM3301 is read directly over I2C without an external library — the Seeed
// HM330X library won't compile against modern arduino-esp32 (uses undefined
// u8/u16/u32 aliases), and the sensor's I2C protocol is simple enough that
// reading it ourselves is the cleaner path.

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>

Adafruit_BME680 bme;

constexpr uint8_t HM3301_I2C_ADDR       = 0x40;
constexpr uint8_t HM3301_SELECT_I2C_CMD = 0x88;

bool bme_present = false;
bool hm3301_present = false;

void i2cScan() {
  Serial.println("[i2c] scanning bus...");
  uint8_t count = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("       device at 0x%02X\n", addr);
      count++;
    }
  }
  if (count == 0) {
    Serial.println("       no devices found — check SDA/SCL wiring and power");
  } else {
    Serial.printf("[i2c] %u device(s) on the bus\n", count);
    Serial.println("       expected: 0x40 (HM3301, Plus only), 0x76 or 0x77 (BME680)");
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);  // give the Serial Monitor time to attach

  Serial.println();
  Serial.println("========================================");
  Serial.println("Smart Citizen Bali — DIY Node SENSOR TEST");
  Serial.println("========================================");
  Serial.println();

  // I2C on XIAO ESP32-S3 default pins: SDA=D4 (GPIO5), SCL=D5 (GPIO6).
  Wire.begin();
  i2cScan();
  Serial.println();

  // --- BME680 ---
  Serial.println("[bme680] probing 0x76...");
  if (bme.begin(0x76)) {
    bme_present = true;
    Serial.println("[bme680] online at 0x76");
  } else if (bme.begin(0x77)) {
    bme_present = true;
    Serial.println("[bme680] online at 0x77 (SDO is tied high)");
  } else {
    Serial.println("[bme680] NOT FOUND at 0x76 or 0x77");
  }

  if (bme_present) {
    // Bosch's suggested defaults for environmental monitoring.
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150);  // 320°C for 150 ms
  }

  Serial.println();

  // --- HM3301 ---
  // Init = send 0x88 to the sensor at 0x40 to select I2C mode (it boots
  // in UART mode by default). After that, every Wire.requestFrom returns
  // the 29-byte data frame.
  Serial.println("[hm3301] probing 0x40 (sending I2C select 0x88)...");
  Wire.beginTransmission(HM3301_I2C_ADDR);
  Wire.write(HM3301_SELECT_I2C_CMD);
  if (Wire.endTransmission() == 0) {
    hm3301_present = true;
    Serial.println("[hm3301] online at 0x40");
  } else {
    Serial.println("[hm3301] NOT FOUND");
    Serial.println("         OK if you're building the Basic kit (no PM sensor).");
    Serial.println("         For Plus kit: check 5V power, Grove cable, and that");
    Serial.println("         the fan is audibly spinning.");
  }

  Serial.println();
  Serial.println("----------------------------------------");
  Serial.println("Reading every 5 seconds.");
  Serial.println("Tip: Tools → Serial Plotter shows readings as live graphs.");
  Serial.println("----------------------------------------");
  Serial.println();
}

void loop() {
  bool printed = false;

  // --- BME680 ---
  if (bme_present) {
    if (bme.performReading()) {
      Serial.printf("[bme680]  T=%6.2f °C   RH=%5.2f %%   P=%7.2f hPa   Gas=%7.1f kΩ\n",
                    bme.temperature,
                    bme.humidity,
                    bme.pressure / 100.0f,
                    bme.gas_resistance / 1000.0f);
      printed = true;
    } else {
      Serial.println("[bme680]  read failed");
    }
  }

  // --- HM3301 ---
  // Frame layout per HM-3300/3600 datasheet and Seeed's example sketch:
  //   buf[0..1]   frame header / sensor model (unused here)
  //   buf[2..3]   sensor number
  //   buf[4..5]   PM1.0  (CF=1)
  //   buf[6..7]   PM2.5  (CF=1)
  //   buf[8..9]   PM10   (CF=1)
  //   buf[10..11] PM1.0  atmospheric  ← outdoor values, what we print
  //   buf[12..13] PM2.5  atmospheric
  //   buf[14..15] PM10   atmospheric
  //   buf[16..27] particle counts per 0.1L by size bin (0.3..10 µm)
  //   buf[28]     checksum (low byte of sum(buf[0..27]))
  if (hm3301_present) {
    uint8_t buf[29];
    size_t got = Wire.requestFrom(HM3301_I2C_ADDR, (uint8_t)29);
    bool ok = (got == 29);
    for (int i = 0; ok && i < 29; i++) {
      if (!Wire.available()) { ok = false; break; }
      buf[i] = Wire.read();
    }
    if (ok) {
      uint8_t sum = 0;
      for (int i = 0; i < 28; i++) sum += buf[i];
      if (sum != buf[28]) {
        Serial.println("[hm3301]  read returned bad checksum — frame corrupted");
      } else {
        uint16_t pm1  = ((uint16_t)buf[10] << 8) | buf[11];
        uint16_t pm25 = ((uint16_t)buf[12] << 8) | buf[13];
        uint16_t pm10 = ((uint16_t)buf[14] << 8) | buf[15];
        Serial.printf("[hm3301]  PM1=%4u µg/m³   PM2.5=%4u µg/m³   PM10=%4u µg/m³\n",
                      pm1, pm25, pm10);
        printed = true;
      }
    } else {
      Serial.println("[hm3301]  read failed");
    }
  }

  if (!printed) {
    Serial.println("(no sensors detected — fix wiring/power, then press reset)");
  }

  Serial.println();  // blank line between cycles for readability
  delay(5000);
}
