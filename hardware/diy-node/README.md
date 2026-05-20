# DIY Node — the workshop sensor

A low-cost, fab-lab-buildable environmental node that publishes to the [Smart Citizen platform](https://smartcitizen.me/) over MQTT. Built around a **Seeed XIAO ESP32-S3**, a **BME280** (temperature, humidity, pressure), and a **Seeed Grove HM3301** (PM1 / PM2.5 / PM10). Total parts cost: roughly **USD 30–50** depending on where you source. Assembly time in a workshop: about **3 hours** from kit to live-on-the-dashboard.

This node is the **workshop entry point** to the Smart Citizen Bali campaign. It is not a replacement for an official [Smart Citizen Kit](https://smartcitizen.me/store) (~USD 300). Be honest about that distinction with workshop participants.

## What this is — and isn't

The DIY node exists to **lower the price floor** of the campaign. A USD 300 SCK is out of reach for most banjars, schools, and warungs in Bali. A USD 30 DIY node, built in a Fab Lab Bali workshop and deployed on the participant's roof, gets a non-technical resident producing public data on the same dashboard within an afternoon. That accessibility is the point.

What you get:

- **Real PM2.5 / PM10 readings** good enough to detect burning events, traffic spikes, and seasonal patterns
- **Temperature and humidity** with reasonable accuracy
- **A Smart Citizen device record** that appears in the campaign dashboard alongside official SCKs and OpenAQ / Sensor.Community stations
- **A teaching artifact** — participants leave the workshop understanding I²C, ESP32 firmware, MQTT, and what "your data is public" means

What you do not get:

- The SCK's noise sensor, eCO₂, light, or ambient pressure-corrected PM
- The SCK's calibrated, drift-compensated readings (PM sensor drift in tropical humidity is real — see the deployment notes)
- A weatherproof IP65 enclosure (you'll print one in the workshop; the official SCK ships ready)
- Five years of firmware engineering by the Fab Lab Barcelona team

When the campaign reports DIY-node data, it is reported **as such** — with a different marker on the dashboard and a tooltip explaining the lower fidelity. Mixing DIY and official kits silently would be dishonest and would erode the campaign's credibility with the regional government conversations the campaign feeds.

## Bill of materials

| Qty | Part | Where | Notes |
|---|---|---|---|
| 1 | Seeed XIAO ESP32-S3 | Tokopedia (search "XIAO ESP32S3"), Shopee, Seeed Indonesia distributor | ~Rp 250–350k. The Sense variant works too but the camera is unused; standard XIAO is cheaper. |
| 1 | GY-BME280 breakout (6-pin) | Tokopedia, generic Chinese clone is fine | ~Rp 40–80k. Make sure it's BME280, not BMP280 — BMP280 has no humidity. |
| 1 | Seeed Grove HM3301 laser PM2.5 sensor v1.0 | Seeed direct, or Tokopedia "Grove HM3301" | ~Rp 450–600k. This is the single most expensive part. |
| 1 | USB-C cable + 5V/2A power supply | Anywhere | The HM3301's fan + laser draws ~80 mA peaks. Cheap 1A USB chargers brown out. Use a real 2A supply. |
| ~6 | 22 AWG jumper wires (M-F or F-F depending on your prototyping stage) | Any electronics shop in Denpasar | Keep short — long jumpers + the fan = noisy readings |
| 1 | Solderless breadboard (prototyping only) | — | For workshop bring-up; not for deployment |
| 1 | Perfboard 5×7 cm (deployment) | Tokopedia "PCB matrix board" | Or skip straight to a printed PCB from Fab Lab Bali's mill |
| — | 3D-printed enclosure (PETG, not PLA) | Fab Lab Bali | PLA softens in Bali's roof temperatures. PETG holds up. STL files: TODO. |

**Sourcing note for Bali:** the HM3301 is the only part that's genuinely expensive locally. Seeed's Indonesian distributor (Halo Robotics) carries it but markup is real. For a workshop of 10 nodes, ordering directly from Seeed (Shenzhen → Denpasar) via the Fab Lab Bali shipping pipeline is usually cheaper than buying 10× at retail. Budget 3 weeks for shipping.

## Wiring

Both sensors live on the same I²C bus. Four wires from the XIAO go to both sensors in parallel; power differs (5V for HM3301's fan, 3.3V for BME280 logic).

![Schematic — XIAO ESP32-S3 + BME280 + HM3301 on shared I²C bus](schematic.svg)

| XIAO pin | XIAO label | Goes to | Net |
|---|---|---|---|
| 5V | `5V` | HM3301 VCC | 5V power (fan + laser) |
| 3.3V | `3V3` | BME280 VCC | 3.3V power (logic) |
| GND | `GND` | HM3301 GND **and** BME280 GND | Common ground |
| GPIO5 | `D4` | HM3301 SDA **and** BME280 SDA | I²C data (shared) |
| GPIO6 | `D5` | HM3301 SCL **and** BME280 SCL | I²C clock (shared) |

The BME280 breakout exposes SDO and CS pins. Leave SDO floating (or tie to GND) for I²C address `0x76`. Leave CS pulled high (most breakouts handle this internally). Ignore the SPI pins entirely.

**I²C addresses on this bus:**

- BME280 → `0x76` (or `0x77` if you tie SDO to 3V3 — only relevant if you bus two BMEs)
- HM3301 → `0x40`

If you have `i2cdetect` running on a Linux laptop or want a sketch, scan the bus first to confirm both addresses show up. If only one appears, check power, then check the pull-up resistors (the XIAO has internal weak pull-ups but the HM3301's Grove cable assumes external pull-ups exist somewhere on the bus — usually the BME280 breakout provides them).

## Smart Citizen platform — register the device

Before flashing, set up the device on Smart Citizen:

1. Sign in at [smartcitizen.me](https://smartcitizen.me/).
2. Add a new device. Pick **"Other devices"** → custom hardware. Give it a name like `Bali DIY Node — [location]`.
3. Add the sensors you'll publish. For this kit:
   - **Temperature** (°C)
   - **Humidity** (%)
   - **PM1** (µg/m³)
   - **PM2.5** (µg/m³)
   - **PM10** (µg/m³)
4. Set the location to the deployment coordinates (not your laptop's IP geolocation — the actual rooftop).
5. From the device's dashboard page, copy:
   - The **device token** (used for MQTT auth)
   - Each **sensor's numeric ID** (you'll paste these into the firmware)

The device token is what authenticates the node against the platform. It can be revoked from the dashboard if a kit goes missing — treat it like a password.

## Firmware

The firmware sketch is at [`firmware/diy_node/diy_node.ino`](firmware/diy_node/diy_node.ino). It:

- Brings up I²C and probes both sensors at boot
- Connects to WiFi and syncs the clock via NTP (the platform requires real `recorded_at` timestamps)
- Reads temp, humidity, PM1, PM2.5, PM10 every 60 seconds
- Publishes one MQTT message per cycle to `device/sck/{DEVICE_TOKEN}/readings` on `mqtt.smartcitizen.me:8883` (TLS)
- Payload shape matches the platform's documented format (`data` → `recorded_at` + `sensors[]`)

Required Arduino libraries (install via Library Manager):

- `Adafruit BME280 Library` (depends on `Adafruit Unified Sensor`)
- `Seeed_HM330X` (Seeed's official driver for HM3301)
- `PubSubClient` by Nick O'Leary (MQTT)
- `ArduinoJson` v7.x

Board: install the **esp32 by Espressif Systems** package in Arduino IDE board manager, then select **XIAO_ESP32S3**.

Edit the configuration block at the top of `diy_node.ino` — WiFi credentials, the device token, and the five sensor IDs from the SC dashboard. Flash, open serial monitor at 115200 baud, watch the connection sequence. Within a couple of minutes the device should appear "online" on smartcitizen.me with readings flowing.

If readings don't appear: check that the sensor IDs in the firmware match exactly what's on the SC device page (they're numeric and per-device), and that the device hasn't been marked "private" — public is the default.

## Prototyping path

Do not skip steps. Each one isolates a different class of bug.

**Stage 1 — Breadboard, USB-powered, in your workshop.** Wire it up with jumpers. Flash the firmware with WiFi pointing to the lab's network. Confirm both sensors are detected on the I²C scan, that NTP syncs, and that the device shows up on smartcitizen.me. This stage is purely software bring-up — if it works here it'll work everywhere else.

**Stage 2 — Perfboard, USB-powered, indoor.** Solder onto a 5×7 cm matrix board. Use **female headers** for the XIAO and the BME280 — they're the parts most likely to die from a wiring mistake or surge, and you want to swap without desoldering. The HM3301 stays connected via its Grove cable. Run it for 48 hours indoors next to a known reference (a phone's air quality app pointed at a window will do for a sanity check). Confirm readings are stable, the device doesn't reset, and MQTT reconnects after WiFi drops.

**Stage 3 — Enclosure, deployed.** 3D-print a PETG enclosure with vents for the PM sensor inlet and the BME280's pressure port. The enclosure is its own design problem — see the Bali deployment notes below. Mount it under shade, never in direct sun. Power via a weatherproof USB supply or a 5V solar panel + buck converter (the latter is a separate project; start with wall power).

**Stage 4 — Printed PCB (optional, for batch builds).** Once a design has run reliably in stage 3 for a few months, layout a custom carrier board in KiCad and mill it on Fab Lab Bali's PCB printer. This is the "we're committing to deploying 20 of these" stage, not the first build.

## Bali deployment notes

The reason the campaign exists is the data, not the firmware. Take this part seriously.

**Humidity.** Bali is 80%+ relative humidity for most of the year. Uncoated boards corrode in 6–12 months. After stage 2, **coat the soldered side of the perfboard with silicone conformal coating** (MG Chemicals 422B or similar — it's available in Singapore, ships to Bali). Mask the sensor openings and the USB-C connector before spraying. The BME280's humidity port and the HM3301's air inlet must stay uncovered. The conformal coating step alone roughly doubles deployment lifetime.

**PM sensor drift.** Plantower-derived sensors (the HM3301 is in this family) drift up over time in high humidity — readings creep 30–50% high after 12–18 months in Bali conditions. **The firmware does not compensate for this.** For a workshop kit, that's an acceptable tradeoff. For data the campaign uses in policy conversations, **co-locate the DIY node with an official SCK or a known reference for at least a week**, derive a correction factor, and apply it in the dashboard's processing layer (not in the firmware — corrections belong in the data pipeline). This is the same pattern Sensor.Community uses for their low-cost network.

**Enclosure.** Sun + Bali rains will destroy a poorly enclosed node in weeks. The HM3301's air inlet must face down or sideways (never up — rain) and must be protected from direct insect entry (a fine stainless mesh over the inlet helps, but check for clog buildup monthly). The BME280's humidity sensor needs airflow but not water — a Stevenson-screen-like louvered approach is the right pattern. Don't deploy on a tin roof in direct sun without thermal isolation; the BME280 will read 15°C high.

**WiFi.** Bali's WiFi reliability ranges from "fine" to "the cable to Singapore is out today." The firmware must reconnect on WiFi loss and keep the device running locally even when offline. Current firmware drops readings when offline — adding a small buffer of unsent readings is a known enhancement (TODO).

**Power.** Most deployments will be wall-powered via a 5V/2A supply. A power loss is the most common cause of "the node went silent" — the participant unplugged it to charge their phone. Workshop framing helps: this is part of the data, label the supply clearly with `Smart Citizen — do not unplug`.

## Workshop format (suggested)

A half-day workshop at Fab Lab Bali, 6–10 participants, two builders per kit (one solders, one flashes; rotate).

- **Hour 1** — campaign framing (why are we measuring? what's a banjar's stake in this?), tour of the dashboard, look at existing readings together
- **Hour 2** — kit assembly (solder onto perfboard, wire it up, no firmware yet)
- **Hour 3** — firmware flash, WiFi config, device registration on smartcitizen.me, first reading
- **Hour 4** — enclosure decisions (where will this live? what does it face? who plugs it back in if it falls off the wall?)

What the participant takes home: a working node, a printed enclosure, a labeled USB supply, and a printed one-pager with the device's URL on smartcitizen.me and the campaign's WhatsApp number to call if it stops working.

What the campaign takes from the workshop: a new dot on the dashboard, the participant's permission to publish, and a named accountable person at the deployment location.

## License

Same as the parent campaign repo: code MIT, docs CC-BY-SA 4.0. Fork it for Smart Citizen [your city] and tell us what changed.
