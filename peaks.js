// peaks.js — Making Sense Bali · peak/anomaly detection and correlation
// Loaded by dashboard/index.html. Pure functions, no DOM, no fetches.
//
// Two detection methods (per metric, per device):
//   1. Threshold-based — semantic, uses published health guidelines (WHO/EPA).
//      Wins where an absolute threshold is defined (PM, T, RH).
//   2. Statistical — rolling baseline (mean + stdev) over the series. Flags
//      readings >2σ from baseline. Used when no absolute threshold exists
//      (gas resistance, future metrics) or in addition for context.
//
// Normalized peak shape:
//   {
//     metric: 'pm25'|'pm10'|...,
//     recordedAt: ISO,
//     value: number,
//     reason: 'threshold'|'sigma',
//     thresholdLabel: string,           // human description (e.g. "> WHO 24h 15 µg/m³")
//     thresholdValue: number,           // the crossed value (only for threshold reason)
//     sigmaZ: number|null,              // z-score (only for sigma reason)
//   }

'use strict';

// ============================================================
// THRESHOLDS — canonical reference values
// ============================================================
// Keep these in lock-step with the "Reference standards" table in the
// dashboard. The dashboard panel and the peak detector must agree.
const THRESHOLDS = {
  pm25: [
    { value: 5,  label: 'WHO annual AQG',           direction: 'above', severity: 'info' },
    { value: 15, label: 'WHO 24h AQG',              direction: 'above', severity: 'warn' },
    { value: 35, label: 'US AQI unhealthy-sensitive', direction: 'above', severity: 'bad'  },
  ],
  pm10: [
    { value: 45, label: 'WHO 24h AQG',              direction: 'above', severity: 'warn' },
    { value: 55, label: 'US AQI moderate',          direction: 'above', severity: 'bad'  },
  ],
  pm1: [
    // No official guideline; use PM2.5 sensitive threshold as a proxy
    { value: 10, label: 'PM1 sensitive (proxy)',    direction: 'above', severity: 'warn' },
  ],
  temp: [
    { value: 32, label: 'Heat-stress concern',      direction: 'above', severity: 'warn' },
    { value: 18, label: 'Cold-comfort lower',       direction: 'below', severity: 'info' },
  ],
  rh: [
    { value: 60, label: 'Mold-risk sustained',      direction: 'above', severity: 'warn' },
    { value: 30, label: 'Dry-air lower bound',      direction: 'below', severity: 'info' },
  ],
  noise: [
    { value: 55, label: 'EPA daytime indoor',       direction: 'above', severity: 'warn' },
    { value: 85, label: 'NIOSH occupational ceiling', direction: 'above', severity: 'bad'  },
  ],
  // Gas resistance: lower = worse. No absolute threshold defined.
  // The statistical detector picks up anomalies (>2σ below baseline).
  gas: [],
  pressure: [],
};

// Map raw sensor names (Smart Citizen / OpenAQ) to our metric keys.
// Add patterns here when a new sensor type appears in the wild.
const METRIC_PATTERNS = [
  { key: 'pm25',     patterns: [/PM\s*2\.5/i, /pm25/i] },
  { key: 'pm10',     patterns: [/PM\s*10\b/i, /pm10/i] },
  { key: 'pm1',      patterns: [/PM\s*1\b/i,  /pm1/i] },
  { key: 'temp',     patterns: [/temperature/i, /\btemp\b/i] },
  { key: 'rh',       patterns: [/humidity/i, /\brh\b/i] },
  { key: 'pressure', patterns: [/pressure/i, /barometric/i] },
  { key: 'noise',    patterns: [/noise/i, /sound/i] },
  { key: 'gas',      patterns: [/gas\s*resistance/i, /\bvoc\b/i, /\bbme680\b/i] },
];

function classifyMetric(rawName){
  if (!rawName) return null;
  for (const { key, patterns } of METRIC_PATTERNS){
    if (patterns.some(p => p.test(rawName))) return key;
  }
  return null;
}

function metricUnit(key){
  return ({
    pm25: 'µg/m³', pm10: 'µg/m³', pm1: 'µg/m³',
    temp: '°C', rh: '%', pressure: 'kPa', noise: 'dBA',
    gas: 'Ω',
  })[key] || '';
}

function metricLabel(key){
  return ({
    pm25: 'PM2.5', pm10: 'PM10', pm1: 'PM1',
    temp: 'Temperature', rh: 'Humidity', pressure: 'Pressure',
    noise: 'Noise', gas: 'Gas resistance',
  })[key] || key;
}

// ============================================================
// PEAK DETECTION
// ============================================================
// series: [{ recordedAt: ISO, value: number }, ...]
// metric: key from THRESHOLDS
// opts.sigmaWindow: how many points to use as baseline (default: all)
// opts.sigmaThreshold: z-score boundary (default: 2)
function detectPeaks(series, metric, opts = {}){
  if (!Array.isArray(series) || !series.length) return [];

  const sigmaThreshold = opts.sigmaThreshold ?? 2;
  const peaks = [];

  // --- Threshold-based pass ---
  const thresholds = THRESHOLDS[metric] || [];
  for (const point of series){
    if (point.value == null || isNaN(point.value)) continue;
    // Find the highest-severity threshold this point crosses.
    let strongest = null;
    for (const t of thresholds){
      const crossed = t.direction === 'above'
        ? point.value > t.value
        : point.value < t.value;
      if (!crossed) continue;
      if (!strongest || severityRank(t.severity) > severityRank(strongest.severity)){
        strongest = t;
      }
    }
    if (strongest){
      peaks.push({
        metric,
        recordedAt: point.recordedAt,
        value: point.value,
        reason: 'threshold',
        thresholdLabel: `${strongest.direction === 'above' ? '>' : '<'} ${strongest.label} ${strongest.value} ${metricUnit(metric)}`,
        thresholdValue: strongest.value,
        severity: strongest.severity,
        sigmaZ: null,
      });
    }
  }

  // --- Statistical pass (always run, helps catch anomalies thresholds miss) ---
  const values = series.map(p => p.value).filter(v => typeof v === 'number' && !isNaN(v));
  if (values.length >= 8){
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((acc, v) => acc + (v - mean) ** 2, 0) / values.length;
    const stdev = Math.sqrt(variance);
    if (stdev > 0){
      for (const point of series){
        if (point.value == null || isNaN(point.value)) continue;
        const z = (point.value - mean) / stdev;
        if (Math.abs(z) >= sigmaThreshold){
          // Only add as a sigma peak if not already flagged by a threshold;
          // avoids double-marking the same point.
          const already = peaks.find(p => p.recordedAt === point.recordedAt);
          if (already){
            already.sigmaZ = +z.toFixed(2);
            continue;
          }
          peaks.push({
            metric,
            recordedAt: point.recordedAt,
            value: point.value,
            reason: 'sigma',
            thresholdLabel: `${z > 0 ? '+' : ''}${z.toFixed(1)}σ from baseline (μ=${mean.toFixed(1)})`,
            thresholdValue: null,
            severity: Math.abs(z) >= 3 ? 'bad' : 'warn',
            sigmaZ: +z.toFixed(2),
          });
        }
      }
    }
  }

  // Sort by time ascending for stable rendering
  peaks.sort((a, b) => new Date(a.recordedAt) - new Date(b.recordedAt));
  return peaks;
}

function severityRank(s){
  return { info: 1, warn: 2, bad: 3, crit: 4 }[s] || 0;
}

// ============================================================
// CORRELATION
// ============================================================
// Geographic distance — Haversine, km
function distanceKm(lat1, lng1, lat2, lng2){
  const R = 6371;
  const toRad = d => d * Math.PI / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a = Math.sin(dLat/2) ** 2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLng/2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

// Find reports near (lat,lng) and within ±windowHours of refTimeIso.
// reports: same shape as state.reports — must have lat, lng, submittedAt.
function reportsNear(reports, refTimeIso, lat, lng, radiusKm = 1, windowHours = 2){
  if (!refTimeIso || lat == null || lng == null) return [];
  const refMs = new Date(refTimeIso).getTime();
  const windowMs = windowHours * 3600 * 1000;
  const results = [];
  for (const r of (reports || [])){
    if (typeof r.lat !== 'number' || typeof r.lng !== 'number') continue;
    if (!r.submittedAt) continue;
    const dKm = distanceKm(lat, lng, r.lat, r.lng);
    if (dKm > radiusKm) continue;
    const dtMs = new Date(r.submittedAt).getTime() - refMs;
    if (Math.abs(dtMs) > windowMs) continue;
    results.push({ report: r, distanceKm: dKm, deltaMs: dtMs });
  }
  // Closest in space first, then closest in time
  results.sort((a, b) => a.distanceKm - b.distanceKm || Math.abs(a.deltaMs) - Math.abs(b.deltaMs));
  return results;
}

// Find sensors near a report. Pairs each near sensor with whether it has a
// matching peak around the report time (caller supplies peak lookup).
//   sensors: state.sensors
//   getPeaksForSensor: (sensor) => peaksArray (all metrics flattened)
function sensorsNear(sensors, refTimeIso, lat, lng, radiusKm = 1, windowHours = 1, getPeaksForSensor = null){
  if (!refTimeIso || lat == null || lng == null) return [];
  const refMs = new Date(refTimeIso).getTime();
  const windowMs = windowHours * 3600 * 1000;
  const results = [];
  for (const s of (sensors || [])){
    if (typeof s.lat !== 'number' || typeof s.lng !== 'number') continue;
    const dKm = distanceKm(lat, lng, s.lat, s.lng);
    if (dKm > radiusKm) continue;
    let corroboratingPeak = null;
    if (typeof getPeaksForSensor === 'function'){
      const peaks = getPeaksForSensor(s) || [];
      for (const p of peaks){
        const dtMs = new Date(p.recordedAt).getTime() - refMs;
        if (Math.abs(dtMs) <= windowMs){
          if (!corroboratingPeak || severityRank(p.severity) > severityRank(corroboratingPeak.severity)){
            corroboratingPeak = { ...p, deltaMs: dtMs };
          }
        }
      }
    }
    results.push({ sensor: s, distanceKm: dKm, corroboratingPeak });
  }
  results.sort((a, b) => a.distanceKm - b.distanceKm);
  return results;
}

// Relative-time helper, used by chips. Returns e.g. "12m before peak".
function formatDelta(deltaMs, anchorLabel = 'peak'){
  const abs = Math.abs(deltaMs);
  const mins = Math.round(abs / 60000);
  const before = deltaMs < 0;
  const direction = before ? 'before' : 'after';
  if (abs < 60000) return `at ${anchorLabel}`;
  if (mins < 60) return `${mins}m ${direction} ${anchorLabel}`;
  const hours = Math.round(mins / 60 * 10) / 10;
  if (mins < 24 * 60) return `${hours}h ${direction} ${anchorLabel}`;
  const days = Math.round(mins / 60 / 24);
  return `${days}d ${direction} ${anchorLabel}`;
}

function formatDistance(km){
  if (km < 1) return `${Math.round(km * 1000)}m`;
  return `${km.toFixed(1)}km`;
}

// ============================================================
// EXPORT
// ============================================================
if (typeof window !== 'undefined'){
  window.SCB_PEAKS = {
    THRESHOLDS, METRIC_PATTERNS,
    classifyMetric, metricUnit, metricLabel,
    detectPeaks,
    distanceKm, reportsNear, sensorsNear,
    formatDelta, formatDistance,
  };
}
