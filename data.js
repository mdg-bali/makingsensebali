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
// ADAPTER: OpenAQ
// https://api.openaq.org/v2/locations
// V2 is anonymous; v3 requires X-API-Key (free at explore.openaq.org/register).
// V2 covers AirGradient, AQICN/GAIA, KLHK ISPU, and most other Bali sources
// that Bali Air Dispatch aggregates.
// ============================================================
async function fetchOpenAQSensors(){
  // Filter Indonesia at the API; trim to Bali bbox client-side.
  // Sort by lastUpdated descending so freshest data appears first.
  const url = 'https://api.openaq.org/v2/locations?country=ID&limit=1000&order_by=lastUpdated&sort=desc';
  try {
    const r = await fetch(url, {headers:{'Accept':'application/json'}});
    if(!r.ok) throw new Error(`OpenAQ HTTP ${r.status}`);
    const data = await r.json();
    const results = (data && data.results) || [];

    const sensors = results.filter(loc => {
      const c = loc.coordinates;
      return c && inBali(c.latitude, c.longitude);
    }).map(loc => {
      const params = loc.parameters || [];
      const findParam = name => params.find(p => p.parameter === name);
      const pm25 = findParam('pm25');
      const pm10 = findParam('pm10');
      const temp = findParam('temperature');
      const rh   = findParam('humidity') || findParam('relativehumidity');

      const sourceNames = (loc.sources || []).map(s => s.name).filter(Boolean).join(', ');
      const sourceLabel = sourceNames ? `OpenAQ · ${sourceNames}` : 'OpenAQ';

      // Best last-update timestamp we can find
      const lastReading = loc.lastUpdated
        || (pm25 && pm25.lastUpdated)
        || (pm10 && pm10.lastUpdated)
        || null;

      return {
        id: `openaq-${loc.id}`,
        rawId: loc.id,
        source: 'openaq',
        sourceLabel,
        name: loc.name || `OpenAQ #${loc.id}`,
        description: [loc.city, sourceNames].filter(Boolean).join(' · '),
        lat: loc.coordinates.latitude,
        lng: loc.coordinates.longitude,
        lastReading,
        reading: {
          pm25: pm25 ? pm25.lastValue : null,
          pm10: pm10 ? pm10.lastValue : null,
          temp: temp ? temp.lastValue : null,
          rh:   rh   ? rh.lastValue   : null,
        },
        detailsUrl: `https://explore.openaq.org/locations/${loc.id}`,
      };
    });

    console.log(`[OpenAQ] ${sensors.length} sensor(s) in Bali (${results.length} ID-wide)`);
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

async function fetchSensorCommunitySensors(){
  // TODO. https://data.sensor.community/static/v2/data.json
  // Open, no key, ~5MB global response — filter to Bali client-side.
  return [];
}

// ============================================================
// AGGREGATOR
// ============================================================
async function fetchAllSensors(){
  const results = await Promise.all([
    fetchSmartCitizenSensors().catch(e => { console.error('[SCK]', e); return []; }),
    fetchOpenAQSensors().catch(e => { console.error('[OpenAQ]', e); return []; }),
    fetchPurpleAirSensors().catch(e => { console.error('[PurpleAir]', e); return []; }),
    fetchSensorCommunitySensors().catch(e => { console.error('[Sensor.Community]', e); return []; }),
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
  };
}
