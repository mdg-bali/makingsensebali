// data.js — Making Sense Bali · sensor data layer
// Aggregates environmental sensor data from multiple public networks for Bali.
// Loaded by both index.html (home) and dashboard/index.html.
//
// Adding a new source: write a fetch* function returning the normalized shape
// described below, then add it to fetchAllSensors() Promise.all.
//
// Normalized sensor shape:
//   {
//     id: string                  unique cross-source ID, prefixed by source
//     rawId: number|string        original platform ID (for direct API calls)
//     source: string              'smartcitizen' | 'openaq' | 'purpleair' | ...
//     sourceLabel: string         human label for popup attribution
//     name: string                sensor name
//     description: string         optional contextual text
//     lat: number, lng: number
//     lastReading: ISO string|null
//     reading: { pm25?, pm10?, temp?, rh?, noise? }   pre-fetched values where available
//     detailsUrl: string          public URL on the source platform
//   }

'use strict';

// ============================================================
// CONFIG
// ============================================================
const BALI_BOUNDS = {
  minLat: -8.95, maxLat: -8.00,
  minLng: 114.40, maxLng: 115.85,
};
const BALI_CENTER = [-8.4095, 115.1889];

// Private/personal sensors — never shown publicly.
// (Currently empty: Tomas's house + office sensors are part of the public network.)
const EXCLUDED_DEVICE_IDS = new Set([]);

// Known Bali devices to add explicitly even if the world_map endpoint
// doesn't return them (or returns them without coordinates). This is a
// safety net — the pagination in fetchSmartCitizenSensors() below
// should catch all Bali devices automatically. Only add here if a
// sensor needs to appear even when world_map is broken / unreachable.
const KNOWN_BALI_SCK_IDS = [19236, 19600, 19618, 19651];

// ============================================================
// HELPERS
// ============================================================
function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

// Classify PM2.5 reading against WHO 2021 24-hour guideline (15 µg/m³).
// Returns 'good' | 'warn' | 'bad' | 'unknown'.
function classifyPM25(v){
  if(v == null || isNaN(v)) return 'unknown';
  if(v <= 15) return 'good';        // WHO 24h
  if(v <= 30) return 'warn';        // 1–2× WHO
  return 'bad';                     // > 2× WHO
}

function inBali(lat, lng){
  if(typeof lat !== 'number' || typeof lng !== 'number') return false;
  if(lat < BALI_BOUNDS.minLat || lat > BALI_BOUNDS.maxLat) return false;
  if(lng < BALI_BOUNDS.minLng || lng > BALI_BOUNDS.maxLng) return false;
  return true;
}

// Sensor "active" if reading within last 14 days (matches Bali Air Dispatch's
// "Archive of Silence" threshold of 2 weeks before considering a sensor dark).
function isActive(lastReadingIso){
  if(!lastReadingIso) return false;
  const ageMs = Date.now() - new Date(lastReadingIso).getTime();
  return ageMs <= 14 * 24 * 3600 * 1000;
}

// ============================================================
// ADAPTER: Smart Citizen Platform
// Direct: https://api.smartcitizen.me/v0
// Via Cloudflare Worker proxy: ${SCK_PROXY_BASE} (same worker as OpenAQ)
//
// We default to the proxy because api.smartcitizen.me's CORS policy can
// block browser calls from github.io origins. The proxy also caches
// responses for ~60s at the Cloudflare edge.
// ============================================================
const SCK_PROXY_BASE = 'https://scb-bali.tomas-74b.workers.dev/sck';

async function sckFetch(path){
  const base = SCK_PROXY_BASE || 'https://api.smartcitizen.me/v0';
  const url = base + path;
  const r = await fetch(url, {headers:{'Accept':'application/json'}});
  if(!r.ok) throw new Error(`SCK HTTP ${r.status} at ${path}`);
  return r.json();
}

async function fetchSmartCitizenSensors(){
  // Strategy:
  //   1. Seed with the known Bali devices (safety net for when discovery breaks)
  //   2. Paginate world_map until empty/short — discovers any new Bali sensors
  //      that get registered with Smart Citizen, no code change required

  const ids = new Set(KNOWN_BALI_SCK_IDS.filter(id => !EXCLUDED_DEVICE_IDS.has(id)));

  // Pagination cap — Smart Citizen has ~5–10k devices globally, well under
  // this ceiling. The cap exists to prevent a runaway loop if the API ever
  // returns the same page indefinitely (cache poisoning etc.).
  const SCK_PAGE_SIZE = 500;
  const SCK_MAX_PAGES = 30;

  let pagesFetched = 0;
  let totalReturned = 0;
  let baliFound = 0;
  let lastError = null;

  for (let page = 1; page <= SCK_MAX_PAGES; page++) {
    let batch;
    try {
      batch = await sckFetch(`/devices/world_map?per_page=${SCK_PAGE_SIZE}&page=${page}`);
    } catch (e) {
      lastError = e;
      console.log(`[SCK] world_map page ${page} failed: ${e.message}`);
      break;
    }
    if (!Array.isArray(batch)) {
      console.log(`[SCK] world_map page ${page} returned non-array, stopping`);
      break;
    }
    pagesFetched++;
    totalReturned += batch.length;
    for (const d of batch) {
      const lat = d.latitude ?? d.lat;
      const lng = d.longitude ?? d.lng ?? d.lon;
      if (!inBali(lat, lng)) continue;
      if (EXCLUDED_DEVICE_IDS.has(d.id)) continue;
      if (!ids.has(d.id)) baliFound++;
      ids.add(d.id);
    }
    // Stop when we get a short page (API has no more) — saves the
    // remaining cap when nothing's left to fetch.
    if (batch.length < SCK_PAGE_SIZE) break;
  }
  console.log(
    `[SCK] world_map: ${pagesFetched} page(s), ${totalReturned} devices scanned, `
    + `${baliFound} new in Bali bbox (plus ${KNOWN_BALI_SCK_IDS.length} known) → ${ids.size} total to fetch`
    + (lastError ? ` (last error: ${lastError.message})` : '')
  );

  // Helper: extract coords from any of several response shapes
  function extractCoords(detail){
    // Try multiple field locations and types — Smart Citizen has shipped
    // different shapes over the years
    const candidates = [
      [detail.latitude, detail.longitude],
      [detail.lat, detail.lng],
      [detail.location && detail.location.latitude, detail.location && detail.location.longitude],
      [detail.location && detail.location.lat, detail.location && detail.location.lng],
      [detail.data && detail.data.location && detail.data.location.latitude, detail.data && detail.data.location && detail.data.location.longitude],
    ];
    for(const [la, ln] of candidates){
      const latNum = typeof la === 'string' ? parseFloat(la) : la;
      const lngNum = typeof ln === 'string' ? parseFloat(ln) : ln;
      if(typeof latNum === 'number' && typeof lngNum === 'number' && !isNaN(latNum) && !isNaN(lngNum)){
        return [latNum, lngNum];
      }
    }
    return [null, null];
  }

  // Fetch each device's full detail (parallel)
  const isKnown = id => KNOWN_BALI_SCK_IDS.includes(id);
  const results = await Promise.all([...ids].map(async id => {
    try {
      const detail = await sckFetch(`/devices/${id}`);

      const [lat, lng] = extractCoords(detail);
      console.log(`[SCK] device ${id}: coords (${lat}, ${lng}), keys: [${Object.keys(detail).slice(0, 10).join(',')}]`);

      if(lat == null || lng == null){
        console.warn(`[SCK] device ${id}: no coordinates found`);
        return null;
      }
      // Trust known IDs even if outside the bbox heuristic — they're explicitly
      // listed because we know they're in Bali, even if coords look weird.
      if(!isKnown(id) && !inBali(lat, lng)){
        console.warn(`[SCK] device ${id}: outside Bali bbox (${lat}, ${lng})`);
        return null;
      }

      const sensors = (detail.data && detail.data.sensors) || detail.sensors || [];
      const findVal = names => {
        const m = sensors.find(x => names.some(n => (x.name||'').includes(n)));
        return m && typeof m.value === 'number' ? m.value : null;
      };

      return {
        id: `sck-${detail.id || id}`,
        rawId: detail.id || id,
        source: 'smartcitizen',
        sourceLabel: 'Smart Citizen',
        name: detail.name || `Device ${detail.id || id}`,
        description: detail.description || '',
        lat, lng,
        lastReading: (detail.data && detail.data.recorded_at) || detail.last_reading_at || null,
        reading: {
          pm25: findVal(['PM 2.5','PM2.5']),
          pm10: findVal(['PM 10','PM10']),
          temp: findVal(['Air Temperature','Temperature']),
          rh:   findVal(['Relative Humidity','Humidity']),
          noise: findVal(['Noise']),
        },
        detailsUrl: `https://smartcitizen.me/kits/${detail.id || id}`,
      };
    } catch(e){
      console.warn(`[SCK] device ${id} failed:`, e.message);
      return null;
    }
  }));

  const valid = results.filter(Boolean);
  console.log(`[SCK] returning ${valid.length} sensor(s)`);
  return valid;
}

// Per-device detail call (used by dashboard's "click pin" panel)
async function fetchSmartCitizenDetail(rawId){
  return sckFetch(`/devices/${rawId}`);
}

// ------------------------------------------------------------
// Historical readings (used for dashboard time-series charts)
//
// Smart Citizen's /v0/devices/{id}/readings endpoint takes:
//   sensor_id  required, global sensor catalog ID
//   from / to  ISO 8601 window bounds
//   rollup     optional bucketing — '5m', '1h', etc.
//
// Response shape (observed):
//   {
//     device_id, sensor_key, sensor_id, rollup, from, to,
//     readings: [[ ISO_timestamp, value ], ...],     // chronological
//   }
//
// We normalize to [{ recordedAt, value }, ...] for the charting code.
//
// CACHING (localStorage):
//   Key: scb-sckhist:{deviceId}:{sensorId}:{rollup}:{from}:{to}
//   TTL: 5 minutes. Reduces SC API pressure when the dashboard auto-refreshes
//   and when users toggle between sensors on the same device.
// ------------------------------------------------------------
const SCK_HISTORY_TTL_MS = 5 * 60 * 1000;
const SCK_HISTORY_KEY_PREFIX = 'scb-sckhist:';

function _historyCacheKey(deviceId, sensorId, fromIso, toIso, rollup){
  return `${SCK_HISTORY_KEY_PREFIX}${deviceId}:${sensorId}:${rollup || 'raw'}:${fromIso}:${toIso}`;
}

function _historyCacheGet(key){
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (!obj || typeof obj.savedAt !== 'number') return null;
    if (Date.now() - obj.savedAt > SCK_HISTORY_TTL_MS) {
      localStorage.removeItem(key);
      return null;
    }
    return Array.isArray(obj.points) ? obj.points : null;
  } catch (_){
    return null;
  }
}

function _historyCachePut(key, points){
  try {
    localStorage.setItem(key, JSON.stringify({ savedAt: Date.now(), points }));
  } catch (_){
    // Quota exhausted — best-effort GC of our own keys, then give up silently.
    try {
      for (let i = localStorage.length - 1; i >= 0; i--){
        const k = localStorage.key(i);
        if (k && k.startsWith(SCK_HISTORY_KEY_PREFIX)) localStorage.removeItem(k);
      }
    } catch(_){}
  }
}

// fetchSmartCitizenHistory(19651, 87, '2026-05-29T...', '2026-05-30T...', '5m')
async function fetchSmartCitizenHistory(deviceId, sensorId, fromIso, toIso, rollup = null){
  const cacheKey = _historyCacheKey(deviceId, sensorId, fromIso, toIso, rollup);
  const cached = _historyCacheGet(cacheKey);
  if (cached) return cached;

  const params = new URLSearchParams();
  params.set('sensor_id', String(sensorId));
  params.set('from', fromIso);
  params.set('to', toIso);
  if (rollup) params.set('rollup', rollup);
  const path = `/devices/${deviceId}/readings?${params.toString()}`;

  let data;
  try {
    data = await sckFetch(path);
  } catch (e){
    console.warn(`[SCK history] device=${deviceId} sensor=${sensorId} failed:`, e.message);
    return [];
  }

  // Defensive: the API has shipped multiple shapes over the years.
  const rawReadings =
    (Array.isArray(data && data.readings) && data.readings) ||
    (Array.isArray(data) && data) ||
    [];

  const points = rawReadings.map(r => {
    // Each reading is typically [iso, value] but some endpoints return objects.
    if (Array.isArray(r)) return { recordedAt: r[0], value: typeof r[1] === 'number' ? r[1] : parseFloat(r[1]) };
    if (r && typeof r === 'object'){
      const recordedAt = r.recorded_at || r.timestamp || r[0];
      const value = r.value != null ? r.value : r[1];
      return { recordedAt, value: typeof value === 'number' ? value : parseFloat(value) };
    }
    return null;
  }).filter(p => p && p.recordedAt && typeof p.value === 'number' && !isNaN(p.value));

  _historyCachePut(cacheKey, points);
  return points;
}

// Fetch history for ALL sensors on a device in parallel, returned as
// { [sensorId]: [{recordedAt, value}, ...] }. Pass the sensor list from
// the device's detail call. Used by the "Selected" panel.
async function fetchSmartCitizenHistoryBulk(deviceId, sensorIds, fromIso, toIso, rollup = null){
  const ids = Array.from(new Set(sensorIds.filter(id => id != null)));
  const entries = await Promise.all(ids.map(async sid => {
    const points = await fetchSmartCitizenHistory(deviceId, sid, fromIso, toIso, rollup);
    return [sid, points];
  }));
  const out = {};
  for (const [sid, points] of entries) out[sid] = points;
  return out;
}

// ============================================================
// ADAPTER: OpenAQ v3 (via Cloudflare Worker proxy)
// https://api.openaq.org/v3 doesn't support CORS preflight for X-API-Key,
// so the browser can't call it directly. We route through a Cloudflare
// Worker that adds the API key server-side and returns CORS headers.
//
// Configure: set OPENAQ_PROXY_BASE to your worker URL + '/openaq'.
// If left empty, the adapter falls back to direct fetch (will fail with CORS,
// but won't break the page — error shows in the source-status diagnostic).
// ============================================================
const OPENAQ_PROXY_BASE = 'https://scb-bali.tomas-74b.workers.dev/openaq';
const OPENAQ_API_KEY    = 'd85c862e2685ab786503f7648fc9581158527bcc617383e6b95db460594baf6f';

async function fetchOpenAQSensors(){
  const useProxy = !!OPENAQ_PROXY_BASE;
  const baseUrl  = useProxy ? OPENAQ_PROXY_BASE : 'https://api.openaq.org/v3';
  const headers  = useProxy
    ? {'Accept': 'application/json'}                                // worker adds the key
    : {'X-API-Key': OPENAQ_API_KEY, 'Accept': 'application/json'};  // direct (will hit CORS)
  const bbox = `${BALI_BOUNDS.minLng},${BALI_BOUNDS.minLat},${BALI_BOUNDS.maxLng},${BALI_BOUNDS.maxLat}`;

  try {
    // Step 1: locations in Bali bounding box
    const locUrl = `${baseUrl}/locations?bbox=${bbox}&limit=1000`;
    const r = await fetch(locUrl, {headers});
    if(!r.ok){
      const body = await r.text().catch(()=>'');
      throw new Error(`OpenAQ locations HTTP ${r.status} ${body.slice(0,200)}`);
    }
    const data = await r.json();
    const locations = (data && data.results) || [];

    if(!locations.length){
      console.log('[OpenAQ] no locations in Bali bbox');
      return [];
    }
    console.log(`[OpenAQ] ${locations.length} location(s) in Bali bbox — fetching latest values`);

    // Step 2: for each location, fetch latest measurements (parallel)
    const enriched = await Promise.all(locations.map(async loc => {
      // Build sensorId → parameter.name map from location's sensors[] array
      const sensorParamMap = {};
      for(const s of (loc.sensors || [])){
        if(s.parameter && s.parameter.name && s.id != null){
          sensorParamMap[s.id] = s.parameter.name;
        }
      }

      try {
        const lr = await fetch(`${baseUrl}/locations/${loc.id}/latest`, {headers});
        if(!lr.ok) return {loc, readings: {}};
        const ldata = await lr.json();
        const measurements = (ldata && ldata.results) || [];
        const readings = {};
        for(const m of measurements){
          const param = sensorParamMap[m.sensorsId];
          if(param && typeof m.value === 'number'){
            readings[param] = {
              value: m.value,
              datetime: (m.datetime && m.datetime.utc) || null,
            };
          }
        }
        return {loc, readings};
      } catch(e){
        console.warn(`[OpenAQ] latest ${loc.id} failed:`, e);
        return {loc, readings: {}};
      }
    }));

    // Step 3: normalize to our common shape
    const sensors = enriched.map(({loc, readings}) => {
      const lat = loc.coordinates && loc.coordinates.latitude;
      const lng = loc.coordinates && loc.coordinates.longitude;
      if(typeof lat !== 'number' || typeof lng !== 'number') return null;

      const providerNames = (loc.providers || []).map(p => p && p.name).filter(Boolean).join(', ');
      const sourceLabel = providerNames ? `OpenAQ · ${providerNames}` : 'OpenAQ';

      // Latest reading datetime — prefer freshest from measurements,
      // fall back to location's datetimeLast metadata.
      let lastReading = (loc.datetimeLast && loc.datetimeLast.utc) || null;
      for(const v of Object.values(readings)){
        if(v.datetime && (!lastReading || v.datetime > lastReading)) lastReading = v.datetime;
      }

      return {
        id: `openaq-${loc.id}`,
        rawId: loc.id,
        source: 'openaq',
        sourceLabel,
        name: loc.name || `OpenAQ #${loc.id}`,
        description: [loc.locality, providerNames].filter(Boolean).join(' · '),
        lat, lng,
        lastReading,
        reading: {
          pm25: readings.pm25 ? readings.pm25.value : null,
          pm10: readings.pm10 ? readings.pm10.value : null,
          temp: readings.temperature ? readings.temperature.value : null,
          rh:   readings.relativehumidity ? readings.relativehumidity.value :
                (readings.humidity ? readings.humidity.value : null),
        },
        detailsUrl: `https://explore.openaq.org/locations/${loc.id}`,
      };
    }).filter(Boolean);

    console.log(`[OpenAQ] returning ${sensors.length} normalized sensor(s)`);
    return sensors;
  } catch(e){
    console.warn('[OpenAQ] fetch failed:', e);
    return [];
  }
}

// ============================================================
// ADAPTERS — TODO
// ============================================================
async function fetchPurpleAirSensors(){
  // TODO. https://api.purpleair.com/v1/sensors?bbox=...
  // Requires free X-API-Key. Two known active Bali devices (Jimbaran, Klungkung).
  return [];
}

// ============================================================
// ADAPTER: Sensor.Community
// https://data.sensor.community/static/v2/data.json
// Static global feed, refreshed every ~5 minutes, no auth, CORS-friendly.
// Returns the most recent reading per sensor worldwide (~5-15MB JSON).
// We filter to Bali client-side, group measurements by location.
//
// Sensor.Community uses non-standard parameter codes:
//   P1 = PM10   ·   P2 = PM2.5   ·   temperature, humidity, pressure
// ============================================================
async function fetchSensorCommunitySensors(){
  const url = 'https://data.sensor.community/static/v2/data.json';
  try {
    const r = await fetch(url, {headers: {'Accept':'application/json'}});
    if(!r.ok) throw new Error(`Sensor.Community HTTP ${r.status}`);
    const items = await r.json();
    if(!Array.isArray(items)) throw new Error('unexpected response shape');

    // Group measurements by location
    const byLoc = new Map();
    for(const it of items){
      const loc = it.location;
      if(!loc) continue;
      const lat = parseFloat(loc.latitude);
      const lng = parseFloat(loc.longitude);
      if(!inBali(lat, lng)) continue;

      if(!byLoc.has(loc.id)){
        byLoc.set(loc.id, {
          locId: loc.id, lat, lng, country: loc.country,
          city: loc.city || loc.name || '',
          measurements: [],
        });
      }
      byLoc.get(loc.id).measurements.push({
        timestamp: it.timestamp,
        sensorType: it.sensor && it.sensor.sensor_type && it.sensor.sensor_type.name,
        values: it.sensordatavalues || [],
      });
    }

    const sensors = [];
    for(const agg of byLoc.values()){
      let pm25 = null, pm10 = null, temp = null, rh = null, latestTs = null;
      for(const m of agg.measurements){
        for(const v of m.values){
          const val = parseFloat(v.value);
          if(isNaN(val)) continue;
          if(v.value_type === 'P2' && pm25 === null) pm25 = val;     // PM2.5
          if(v.value_type === 'P1' && pm10 === null) pm10 = val;     // PM10
          if(/temperature/i.test(v.value_type) && temp === null) temp = val;
          if(/humidity/i.test(v.value_type) && rh === null) rh = val;
        }
        if(!latestTs || m.timestamp > latestTs) latestTs = m.timestamp;
      }

      const sensorTypes = [...new Set(agg.measurements.map(m => m.sensorType).filter(Boolean))];
      sensors.push({
        id: `sensorcomm-${agg.locId}`,
        rawId: agg.locId,
        source: 'sensor_community',
        sourceLabel: 'Sensor.Community',
        name: sensorTypes.length ? `${sensorTypes[0]} · #${agg.locId}` : `Sensor.Community #${agg.locId}`,
        description: [agg.city, sensorTypes.join(', ')].filter(Boolean).join(' · '),
        lat: agg.lat, lng: agg.lng,
        lastReading: latestTs ? new Date(latestTs.replace(' ','T') + 'Z').toISOString() : null,
        reading: { pm25, pm10, temp, rh },
        detailsUrl: `https://maps.sensor.community/#13/${agg.lat}/${agg.lng}`,
      });
    }

    console.log(`[SensorCommunity] ${sensors.length} sensor(s) in Bali (${items.length} global measurements)`);
    return sensors;
  } catch(e){
    console.warn('[SensorCommunity] fetch failed:', e);
    return [];
  }
}

// ============================================================
// AGGREGATOR
// ============================================================
// Diagnostic: track per-source results so the UI can show what worked
const SOURCE_STATUS = {
  smartcitizen:     {count: 0, error: null},
  openaq:           {count: 0, error: null},
  sensor_community: {count: 0, error: null},
  purpleair:        {count: 0, error: 'not configured'},
};

async function tracked(key, fn){
  try {
    const r = await fn();
    SOURCE_STATUS[key].count = r.length;
    SOURCE_STATUS[key].error = null;
    return r;
  } catch(e){
    SOURCE_STATUS[key].error = String(e.message || e);
    console.error(`[${key}]`, e);
    return [];
  }
}

async function fetchAllSensors(){
  const results = await Promise.all([
    tracked('smartcitizen',     fetchSmartCitizenSensors),
    tracked('openaq',           fetchOpenAQSensors),
    tracked('sensor_community', fetchSensorCommunitySensors),
    // tracked('purpleair', fetchPurpleAirSensors),  // not configured
  ]);
  const all = results.flat();

  // Deduplicate by approx coordinate (~10m precision) — handles cases where
  // the same physical sensor publishes to two networks.
  const seen = new Set();
  const deduped = all.filter(s => {
    if(typeof s.lat !== 'number' || typeof s.lng !== 'number') return false;
    const key = `${s.lat.toFixed(4)},${s.lng.toFixed(4)}`;
    if(seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  console.log(`[SCB] aggregated ${deduped.length} unique sensors across ${results.filter(r=>r.length).length} sources`);
  return deduped;
}

// ============================================================
// REPORTS — citizen observations via WhatsApp bot
// ============================================================
// Approved reports from the Sense Making bot (reports/ component) are
// published to data/reports/ in this repo by the bot's sync_profiles.sh
// script. Each report is a sanitized Murmurations profile (PII-stripped).
//
// File layout in the repo:
//   data/reports/index.json          — { profiles: ["AQ_…json", …], count: N, generated_at: ISO }
//   data/reports/AQ_<id>.json        — one Murmurations profile per approved report
//
// This function reads the index, fetches each profile, and normalizes
// to the report shape the map renderer expects (lat, lng, title,
// description, category, severity, submittedAt, locality).

// Resolve the data/reports/ URL relative to the current page. Home page
// is at the repo root; dashboard is one level deeper.
function reportsBaseUrl(){
  const path = window.location.pathname;
  // Match any path that ends in /dashboard or /dashboard/ (with optional trailing index.html)
  if(/\/dashboard\/?(index\.html)?$/.test(path)) return '../data/reports';
  return './data/reports';
}

function profileToReport(profile){
  if(!profile) return null;
  const lat = profile.latitude;
  const lng = profile.longitude;
  if(typeof lat !== 'number' || typeof lng !== 'number') return null;

  const ai = profile.ai_analysis || {};
  const id = profile.primary_url
    ? profile.primary_url.split('/').pop().replace('.json','')
    : (profile.name || 'report');

  // photo_path is only present when the operator explicitly checked
  // "Publish photo too" at approval time. Resolves to an absolute URL
  // the browser can load, sitting in the same data/reports/ tree as
  // the profile JSON itself.
  let photoUrl = null;
  if(typeof profile.photo_path === 'string' && profile.photo_path){
    photoUrl = `${reportsBaseUrl()}/${profile.photo_path.replace(/^\/+/, '')}`;
  }

  return {
    id,
    lat, lng,
    title: profile.name || 'Citizen report',
    description: profile.description || '',
    category: profile.pollution_category || 'other',
    severity: ai.severity || null,
    // The model's natural-language description of the scene. Often
    // useful to compare against the reporter's own description.
    aiDescription: (ai.description || '').trim() || null,
    indicators: Array.isArray(ai.indicators) ? ai.indicators : [],
    // Worker writes this when MLX inference succeeds — handy on the
    // admin side to filter "AI-analyzed" vs "needs review" reports.
    aiConfidence: typeof ai.confidence === 'number' ? ai.confidence : null,
    submittedAt: profile.date_added || null,
    locality: profile.locality || '',
    photoUrl,
    source: 'whatsapp_bot',
    sourceLabel: 'Resident report',
    profileUrl: profile.primary_url || null,
  };
}

async function fetchReports(){
  const base = reportsBaseUrl();
  try {
    const indexResp = await fetch(`${base}/index.json`, {cache: 'no-cache'});
    if(!indexResp.ok){
      // 404 just means no approved reports yet — silent
      if(indexResp.status === 404) return [];
      throw new Error(`reports index HTTP ${indexResp.status}`);
    }
    const index = await indexResp.json();
    const filenames = Array.isArray(index.profiles) ? index.profiles : [];
    if(!filenames.length) return [];

    console.log(`[reports] fetching ${filenames.length} approved profile(s)`);

    const results = await Promise.all(filenames.map(async fn => {
      try {
        const r = await fetch(`${base}/${fn}`, {cache: 'no-cache'});
        if(!r.ok) return null;
        const profile = await r.json();
        return profileToReport(profile);
      } catch(e){
        console.warn(`[reports] failed to fetch ${fn}:`, e.message);
        return null;
      }
    }));

    const valid = results.filter(Boolean);
    console.log(`[reports] returning ${valid.length} valid report(s)`);
    return valid;
  } catch(e){
    console.warn('[reports] fetch failed:', e);
    return [];
  }
}

// Daily/weekly summary written by sync_profiles.sh via generate_summary.py.
// Optional — if the file is missing (older deployments, sync not yet run),
// callers should fall back to their existing category-count rendering.
async function fetchReportsSummary(){
  const base = reportsBaseUrl();
  try {
    const r = await fetch(`${base}/summary.json`, {cache: 'no-cache'});
    if(!r.ok) return null;
    return await r.json();
  } catch(e){
    console.warn('[reports] summary fetch failed:', e);
    return null;
  }
}

// ============================================================
// EXPORT
// ============================================================
if(typeof window !== 'undefined'){
  window.SCB_DATA = {
    BALI_BOUNDS, BALI_CENTER, EXCLUDED_DEVICE_IDS,
    escapeHtml, classifyPM25, inBali, isActive,
    fetchSmartCitizenSensors, fetchSmartCitizenDetail,
    fetchSmartCitizenHistory, fetchSmartCitizenHistoryBulk,
    fetchOpenAQSensors,
    fetchPurpleAirSensors, fetchSensorCommunitySensors,
    fetchAllSensors,
    fetchReports, fetchReportsSummary, profileToReport, reportsBaseUrl,
    SOURCE_STATUS,  // exposed for in-page diagnostic
  };
}
