// data.js — Smart Citizen Bali · sensor data layer
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

// Private/personal sensors — never shown publicly
const EXCLUDED_DEVICE_IDS = new Set([19236, 19600]);

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
// https://api.smartcitizen.me/v0
// ============================================================
async function fetchSmartCitizenSensors(){
  const collected = [];
  try {
    let page = 1, gotMore = true, safety = 0;
    while(gotMore && safety < 5){
      const url = `https://api.smartcitizen.me/v0/devices/world_map?per_page=500&page=${page}`;
      const r = await fetch(url, {headers:{'Accept':'application/json'}});
      if(!r.ok) break;
      const arr = await r.json();
      if(!Array.isArray(arr) || !arr.length){ gotMore = false; break; }
      collected.push(...arr);
      gotMore = arr.length === 500;
      page++; safety++;
    }
  } catch(e){ console.warn('[SCK] world_map failed:', e); }

  return collected.filter(d => {
    const lat = d.latitude ?? d.lat;
    const lng = d.longitude ?? d.lng ?? d.lon;
    if(!inBali(lat, lng)) return false;
    if(EXCLUDED_DEVICE_IDS.has(d.id)) return false;
    return true;
  }).map(d => ({
    id: `sck-${d.id}`,
    rawId: d.id,
    source: 'smartcitizen',
    sourceLabel: 'Smart Citizen',
    name: d.name || `Device ${d.id}`,
    description: d.description || '',
    lat: d.latitude ?? d.lat,
    lng: d.longitude ?? d.lng ?? d.lon,
    lastReading: d.last_reading_at || null,
    reading: {},  // Smart Citizen requires per-device call for live values
    detailsUrl: `https://smartcitizen.me/kits/${d.id}`,
  }));
}

// Per-device detail call (used by dashboard's "click pin" panel)
async function fetchSmartCitizenDetail(rawId){
  const r = await fetch(`https://api.smartcitizen.me/v0/devices/${rawId}`);
  if(!r.ok) throw new Error(`SCK ${rawId}: ${r.status}`);
  return r.json();
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
// REPORTS (placeholder)
// ============================================================
async function fetchReports(){
  // TODO. Cloudflare Worker proxy reading published reports from Airtable.
  return [];
}

// ============================================================
// EXPORT
// ============================================================
if(typeof window !== 'undefined'){
  window.SCB_DATA = {
    BALI_BOUNDS, BALI_CENTER, EXCLUDED_DEVICE_IDS,
    escapeHtml, classifyPM25, inBali, isActive,
    fetchSmartCitizenSensors, fetchSmartCitizenDetail,
    fetchOpenAQSensors,
    fetchPurpleAirSensors, fetchSensorCommunitySensors,
    fetchAllSensors,
    fetchReports,
    SOURCE_STATUS,  // exposed for in-page diagnostic
  };
}
