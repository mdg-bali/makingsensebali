# Making Sense Bali · Platform Revision Brief (v2)

**Status:** brief — not started.
**Owner of execution:** Claude Code (or a developer working in the codebase). This document is the handover; everything Claude Code needs to do the work should be derivable from here plus the repo.
**Owner of intent:** Tomas Diez (Making Sense Bali lead). Read [README.md](../README.md) first if you're unfamiliar with the campaign.
**Last updated:** 2026-05-30.

---

## 1. Why this revision

The current dashboard at `mdg-bali.github.io/smartcitizenbali/dashboard/` works as a *snapshot* view: a map of sensors with their latest readings, a list of citizen reports rendered as cards, a few reference panels. It proves the campaign exists. It does not yet help anyone *interpret* what's happening environmentally in Bali.

The shift this revision delivers: from "what is the current PM2.5 reading at this pin" to "**what changed in this neighbourhood over the last day, and is that connected to what people are reporting?**" That question is what turns a dashboard into a tool a banjar coordinator, a Dinas Kesehatan analyst, or a parent worried about their kid's asthma can actually use.

Three concrete capabilities make that shift:

1. **Time-series charts** per sensor metric, at two windows: last 24 hours and last 7 days. Static current values are insufficient for any environmental decision.
2. **Peak/anomaly detection** that surfaces moments worth investigating, rather than asking a human to eyeball charts to find them.
3. **Bidirectional correlation between sensor peaks and citizen reports.** When a PM spike happens at the same time someone reports rubbish burning two streets away, the dashboard should connect those two facts. When a spike happens with no report, the dashboard should suggest "this looks like something — anyone want to report what they're seeing?"

Together these turn the dashboard from a passive display into the participatory instrument that the campaign's Making Sense methodology actually requires.

Alongside those, the reports component needs a UI rework — the current card grid is too heavy for what is, conceptually, a feed of resident observations. Make it a feed, expandable on click.

## 2. Current state — what exists today

| Surface | File(s) | Notes |
|---|---|---|
| Landing page | [`index.html`](../index.html) (1234 lines) | Methodology framing, survey link, project context. Mostly fine; out of scope for this revision unless time-series/peaks need a summary widget here. |
| Dashboard | [`dashboard/index.html`](../dashboard/index.html) (779 lines) | Map + statusbar + selection panel + reports feed + sensors ranked + reference standards + health implications. The bulk of this revision. |
| Sensor data layer | [`data.js`](../data.js) (609 lines) | Fetches from Smart Citizen (`fetchSmartCitizenSensors`, `fetchSmartCitizenDetail`), OpenAQ (`fetchOpenAQSensors`), PurpleAir, Sensor.Community. Also fetches citizen reports from static JSON in `data/reports/`. |
| CF Worker (CORS proxy) | [`worker/openaq-proxy.js`](../worker/openaq-proxy.js) (172 lines) | OpenAQ proxy. Pattern to follow if any other source needs CORS bypass. |
| Reports component | [`reports/`](../reports/) (~36KB docs + Python code) | WhatsApp bot + operator dashboard. **Out of scope** for this revision — the front-end consumes the reports as static JSON, no API changes needed. |
| Static reports data | `data/reports/*.json` | Approved citizen reports as individual JSON files plus an `index.json` manifest. This is what `fetchReports()` in data.js reads. |

Key existing wiring worth knowing about:

- **Chart.js 4.4.0 is already loaded** in `dashboard/index.html` (line 16). It's currently unused. No new charting dependency needed.
- **Leaflet + leaflet-heat** is loaded for the map. The map renders both sensor pins and a report-density heatmap.
- **`state.reports`** holds the current report list in the dashboard JS (populated by `fetchReports()` in data.js).
- **`state.sensors`** holds sensors (BME680/HM3301 readings come in via the SC API as one device with multiple sensor types).
- **Bali bounding box** is configured at `BALI_BOUNDS` / `BALI_CENTER` in data.js — the world-map pagination filters on this.
- **Smart Citizen sensor IDs** the campaign uses today are documented in [`hardware/diy-node/firmware/diy_node/diy_node.ino`](../hardware/diy-node/firmware/diy_node/diy_node.ino) (174 = BMP280 Temp, 56 = SHT31 RH, 175 = BMP280 Pressure, 87/88/89 = PMS5003 PM2.5/10/1). The SC `/v0/sensors` endpoint is the authoritative source for new IDs as other kits come online.

Existing report rendering (`renderReportFeed()` in `dashboard/index.html` line 501) already iterates `state.reports` into an HTML feed — so the scaffold is there, the cards just need a redesign.

## 3. Target state — what to build

### 3.1 Time-series charts (per metric, per device)

For each sensor displayed in the map's "Selected" panel, the dashboard should show:

- **Last 24 hours** chart — high temporal resolution (every reading)
- **Last 7 days** chart — downsampled (hourly or 4-hourly bins, depending on density)

Charts must be per-metric (Temperature, Humidity, Pressure, PM1, PM2.5, PM10, gas resistance when available). Render with Chart.js (already loaded).

**API surface for historical data:**

Smart Citizen's `/v0/devices/{id}/readings` accepts:
- `sensor_id` — required, the global sensor ID
- `from` — ISO 8601 timestamp (start of window)
- `to` — ISO 8601 timestamp (end of window)
- `rollup` — optional bucketing (e.g., `5m`, `1h`)

A history fetch helper belongs in `data.js`:

```js
async function fetchSmartCitizenHistory(deviceId, sensorId, fromIso, toIso, rollup = null) {
  // Returns [{ recorded_at: ISO, value: number }, ...]
}
```

For OpenAQ and Sensor.Community sources, history endpoints exist but have different shapes. Treat OpenAQ history as Phase 2 — for v2-launch, time-series only required for SC devices (which includes the DIY nodes). The other sources can show only current values.

**Caching:** call `localStorage` to cache historical fetches with a 5-minute TTL. Re-fetching 7 days of history on every page load is wasteful and quota-eating against the SC API.

**Required acceptance:** opening the map's "Selected" panel for a Smart Citizen device shows two chart strips (24h, 7d) for each of its attached sensors. Loading state visible while fetching. Empty state with sensible message if no historical data exists yet (new device).

### 3.2 Peak / anomaly detection

For each time series displayed, surface points that are statistically or semantically anomalous.

**Two complementary detection methods, both per-metric:**

1. **Threshold-based** (semantic) — use the published reference values already documented in the dashboard's reference standards panel:
   - PM2.5: WHO daily guideline 5 µg/m³, US AQI "moderate" 12, "unhealthy for sensitive groups" 35
   - PM10: WHO daily guideline 45 µg/m³, US AQI moderate 55
   - Temperature: indoor comfort 24–28°C, heat-stress concern >32°C
   - Humidity: mold-risk threshold >60% RH sustained
   - Gas resistance: relative only — no absolute threshold, use the z-score method
   
   Document these thresholds in a single `THRESHOLDS` table in data.js (or a new `peaks.js` module) so the canonical values live in one place.

2. **Statistical** (anomaly-relative) — for each metric, compute a rolling 7-day baseline (mean + standard deviation) for the device. Flag any reading more than 2σ above (or below, for things like gas resistance where lower = worse) as a peak. Re-compute the baseline once per page load.

For v1, **threshold-based wins where it's defined** (PM, T, RH). Statistical fills in for gas resistance and any future metric without an absolute threshold.

**Visual treatment on the chart:**

- Peak points marked with a distinct symbol (e.g., red ring)
- Hover/tap the peak to see: timestamp, value, which threshold or σ-bound was crossed
- Aggregate "peaks in last 24h" / "peaks in last 7d" count surfaced in the statusbar at the top

**Required acceptance:** if PM2.5 spiked to 80 µg/m³ at 2pm yesterday on the office DIY node, that point is clearly marked red on the 24h chart, and the statusbar shows "Active peaks (24h): 1" with click-through to a list view.

### 3.3 Reports — feed redesign

Current state: each report renders as a card with a thumbnail, category badge, locality, description preview, and timestamp. They take a lot of vertical space and the dashboard feels heavy.

Target: **compact feed of one-line entries, expandable on click.** Inspiration: Twitter / Mastodon timeline. Each row shows:

- Timestamp (relative — "12m ago", "3h ago", "yesterday")
- Category badge (colored chip)
- Locality
- First ~80 characters of the description

Click/tap expands to full detail inline (photo, full description, AI analysis, map pin sync). Collapse on second click.

**Behaviour:**

- Lazy-load the photo only when the row is expanded
- Sort by `submittedAt` desc (already the case)
- Infinite scroll or "Load more" if there are >50 reports
- Filter chips at the top: category, severity, last 24h / last 7d / all time

The `renderReportFeed()` function in `dashboard/index.html` (line 501) is the single rendering site. Rework there.

**Required acceptance:** the feed fits 20+ reports in the same vertical space as 5 cards do today. Tapping a row expands inline within ~150ms and pans the map to that location (current behaviour).

### 3.4 Bidirectional correlation between peaks and reports

The most strategically valuable capability of the revision.

**Direction A — peak → report:** when a chart shows a peak, fetch any reports within:
- **Time window:** ±2 hours of the peak's timestamp
- **Geographic radius:** 1km of the sensor's location

Display matching reports as small chips below the chart: "2 nearby reports — [burning waste · 230m away · 35 min before peak] [smoke · 480m · 1h after]". Click a chip to jump to that report in the feed.

If no matching reports exist, surface an action prompt: **"This spike has no citizen report attached. If you're nearby right now, [report what you're seeing →]"** with a link to the survey or the WhatsApp bot.

**Direction B — report → sensor:** when a report is expanded in the feed, fetch sensor readings within:
- **Time window:** ±1 hour of the report's submitted timestamp
- **Geographic radius:** 1km

Display matching sensors as small chips inside the expanded report: "Nearby sensors: [DIY Node Office — PM2.5 16 µg/m³ at submission time] [OpenAQ Denpasar — PM2.5 22 µg/m³]". Click to open the sensor's history view.

If a sensor shows a peak around the same timestamp, surface it strongly: "**Sensor data corroborates this report** — PM2.5 spiked to 80 µg/m³ at the DIY Node 350m away, 12 minutes before this report was filed."

**Required acceptance:** when a known event happens (e.g. someone burns rubbish near the office node), the peak on the chart links to the resident report of the smoke, and vice versa. Test this with one synthetic report tied to a real peak in the existing data before declaring done.

### 3.5 Bilingual UX

Strings in the dashboard should pass through a translation layer (a simple `t(key)` function backed by a JSON dictionary). Language toggle in the statusbar. Default: English. Add at minimum **Bahasa Indonesia** translations for the public-facing strings (chart titles, peak alerts, action prompts, category badges, statusbar labels).

Don't translate technical labels (sensor model names, "PM2.5", "kPa", "µg/m³" — those stay English regardless of locale).

This is a v1 nice-to-have, not a blocker. If time is tight, scaffold the `t(key)` infrastructure with English-only strings and document the dictionary file for translators to fill in later.

## 4. Suggested phasing

**Phase 1 — Time-series infrastructure.** ~1 week.
- `fetchSmartCitizenHistory` helper in data.js
- `localStorage` caching layer
- Chart rendering in the Selected panel (24h + 7d per metric)
- Loading and empty states

**Phase 2 — Peak detection.** ~3 days.
- `THRESHOLDS` table + statistical baseline computation
- Visual markup on charts
- Statusbar peak counter

**Phase 3 — Reports feed redesign.** ~2 days.
- Compact row layout
- Expand-in-place interaction
- Filter chips

**Phase 4 — Correlation engine.** ~1 week.
- Peak → report nearby search
- Report → sensor nearby search
- "Report this peak" prompt
- "Sensor data corroborates" surfacing

**Phase 5 — Polish + bilingual.** ~3 days.
- `t()` translation layer
- Bahasa Indonesia strings
- Mobile QA pass

Total: ~3 weeks of focused work. Phases 1 and 2 can ship independently and are the highest-leverage starts.

## 5. Acceptance criteria — the "done" checklist

The revision is done when, on the live dashboard:

- [ ] Clicking any Smart Citizen device on the map shows time-series charts (24h + 7d) for all its attached sensors
- [ ] At least one PM2.5 peak is visibly highlighted on a chart with the WHO threshold called out in the hover state
- [ ] The reports section is a scannable feed where 20+ reports fit on one screen
- [ ] An expanded report shows nearby sensors and their readings at the time of submission
- [ ] A chart with a peak shows nearby reports (if any) or an action prompt to report (if none)
- [ ] The statusbar shows "Active peaks · 24h" and "Active peaks · 7d" counts
- [ ] On mobile (375px wide), the dashboard remains usable — charts scrollable horizontally if needed, no horizontal page scroll
- [ ] The site still loads in <3 seconds on a 3G simulated connection (currently passes; don't regress)
- [ ] No new dependencies beyond what's already loaded (Chart.js, Leaflet, leaflet-heat); add nothing without justification

## 6. Non-goals — what to NOT do in this revision

- **Don't introduce a framework.** No React, Vue, Svelte, Next, Astro. The static-HTML-with-vanilla-JS architecture is intentional — the campaign is replicable to other Fab City chapters via a `git clone`, no build step required. Keep that property.
- **Don't add a backend.** Cloudflare Workers for CORS proxying only. No Node.js server, no database server-side. All processing happens in the browser or in the SC platform.
- **Don't modify the reports component (Python/Flask).** This revision is front-end only. The reports component (WhatsApp bot + operator dashboard) is a separate codebase that just produces JSON the dashboard consumes. Read-only relationship.
- **Don't rewrite working code for style reasons.** The current code is functional and readable. Only refactor when adding new capability requires it.
- **Don't lose the methodology framing.** The README and dashboard hero explicitly position this as a *Making Sense* descendant — a participatory instrument, not just a data viewer. Don't strip that voice.
- **Don't add login, auth, or per-user state.** The dashboard is public-read for everyone. Operator features stay in the reports component.

## 7. Dependencies and unknowns

- **Smart Citizen `/v0/devices/{id}/readings` rate limits** — undocumented. Test with realistic load (10 devices × 7 days × 6 sensors = 420 history queries on first page load is too many). The localStorage cache must be in place before going live to avoid hitting limits and getting blocked.
- **Smart Citizen `rollup` parameter syntax** — verify against the docs at https://developer.smartcitizen.me. If it's not what this brief assumes, adjust.
- **Reports API stability** — the static JSON pattern (`data/reports/index.json` + per-report files) is what `fetchReports()` consumes. This is owned by the reports component; coordinate with whoever maintains that before relying on new fields.
- **No BME680 catalog entry yet** — the SC platform doesn't have a Bosch BME680 entry. Currently we publish to BMP280/SHT31/PMS5003 IDs (see [hardware/diy-node/README.md](../hardware/diy-node/README.md)). Oscar (SC team) may add proper BME680 entries server-side at some point. Either way the dashboard reads whatever sensor IDs the device has attached — no hardcoded coupling required.
- **No kit blueprint set for DIY devices** — affects the SC world-map endpoint's discoverability. The dashboard's `KNOWN_BALI_SCK_IDS` safety list (line 42 of data.js) is the workaround. When new DIY nodes deploy, add their IDs there until Oscar attaches blueprints.

## 8. How to start

1. Spin up a working branch: `git checkout -b dashboard-v2`
2. Read [`dashboard/index.html`](../dashboard/index.html) and [`data.js`](../data.js) end-to-end. They're not large; an hour to internalise the current structure pays off across the whole revision.
3. Skim the existing reports rendering (`renderReportFeed()` line 501 in `dashboard/index.html`) — that's the most-touched code in this revision.
4. Start with Phase 1 (time-series). Get one chart rendering for the DIY office node (device 19651) before generalising.
5. PR to `main`. GitHub Pages picks up changes automatically.

## 9. When this is done

Update this brief with a "Status: complete" header and a one-paragraph summary of what landed. If anything in this brief turned out to be wrong (an API didn't behave as expected, a non-goal needed revisiting), document it here so the next reviser learns from it. The campaign's `REPLICATION.md` will reference the dashboard v2 as the version other Fab City chapters fork — accuracy matters.

## 10. Contact

- Campaign lead: Tomas Diez · `tomas@fab.city`
- Reports component owner: Fab Lab Bali team · `fablabbali@gmail.com`
- Smart Citizen platform contact: Oscar (SC platform team)

---

**Appendix — quick reference for current sensor IDs in use (Bali deployment)**

| Device ID | Type | Notes |
|---|---|---|
| 19236 | SCK 2.1 | House node — first campaign deployment |
| 19600 | SCK 2.1 | Office node — second campaign deployment |
| 19618 | SCK 2.1 | Earlier addition; check the README for context |
| **19651** | **DIY Plus (XIAO + BME680 + HM3301)** | **First DIY workshop-built node — Tomas's office, May 2026** |

Future DIY workshop nodes will appear here as they deploy. The pattern is the same: register via `hardware/diy-node/tools/register_device.py`, add ID to `KNOWN_BALI_SCK_IDS` in data.js, flash firmware with sensor IDs from `hardware/diy-node/tools/find_sensor_ids.py`.
