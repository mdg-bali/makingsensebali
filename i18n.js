// i18n.js — Smart Citizen Bali · translation layer
// Tiny dictionary-backed t() function. No framework, no dependencies.
//
// Usage:
//   const t = window.SCB_I18N.t;
//   t('peak.active_24h')          → "Active peaks · 24h"
//   t('peak.active_24h', 'id')    → "Lonjakan aktif · 24 jam"
//   t('foo', 'id', 'fallback')    → fallback for unknown keys
//
// Add new strings: append the key to BOTH languages. English is canonical;
// Bahasa is a translation. Technical labels (units, sensor model names,
// "PM2.5", "kPa") stay English regardless of locale — don't add them here.
//
// Persistence: language preference is stored in localStorage under
// 'scb-lang'. Default: 'en'.

'use strict';

const DICTIONARIES = {
  en: {
    // statusbar
    'statusbar.connecting':    'CONNECTING…',
    'statusbar.live':          'LIVE',
    'statusbar.error':         'ERROR',
    'statusbar.syncing':       'SYNCING…',
    'statusbar.sensors':       'Sensors',
    'statusbar.active_24h':    'Active 24h',
    'statusbar.reports':       'Reports',
    'statusbar.peaks_24h':     'Active peaks · 24h',
    'statusbar.peaks_7d':      'Active peaks · 7d',
    'statusbar.lang':          'EN',
    'statusbar.lang_toggle':   'BHS',

    // hero / detail panel
    'detail.no_pin':           'No pin selected',
    'detail.select_prompt':    'Click any sensor or report on the map above',
    'detail.help_text':        'The detail panel will populate with current sensor readings or report content.',
    'detail.empty':            'Select a pin on the map to inspect it.',
    'detail.loading':          'Loading sensor detail…',
    'detail.fetch_failed':     'Could not fetch detail',

    // history / charts
    'history.title_24h':       'Last 24 hours',
    'history.title_7d':        'Last 7 days',
    'history.loading':         'Loading history…',
    'history.empty':           'No historical data yet — sensor may be too new.',
    'history.error':           'Could not load history.',
    'history.no_data':         'no data',
    'history.peaks_24h':       'Peaks · 24h',
    'history.peaks_7d':        'Peaks · 7d',

    // peaks
    'peak.label':              'Peak',
    'peak.threshold_crossed':  'Threshold crossed',
    'peak.statistical':        'Statistical anomaly',
    'peak.none':               'No peaks detected.',
    'peak.report_prompt':      'This spike has no citizen report attached. If you\'re nearby right now,',
    'peak.report_link':        'report what you\'re seeing →',
    'peak.nearby_reports':     'Nearby reports',
    'peak.nearby_sensors':     'Nearby sensors',
    'peak.corroborates':       'Sensor data corroborates this report',

    // reports feed
    'feed.title':              'Latest resident reports',
    'feed.empty':              'No citizen reports yet.',
    'feed.expand':             'Expand',
    'feed.collapse':           'Collapse',
    'feed.load_more':          'Load more',
    'feed.filter_all':         'All',
    'feed.filter_24h':         '24h',
    'feed.filter_7d':          '7d',
    'feed.filter_alltime':     'All time',
    'feed.filter_category':    'Category',
    'feed.relative_now':       'just now',
    'feed.relative_min_ago':   'm ago',
    'feed.relative_hr_ago':    'h ago',
    'feed.relative_day_ago':   'd ago',
    'feed.relative_yday':      'yesterday',

    // misc
    'action.take_part':        '+ Take part',
    'action.home':             '← Home',
    'action.report_now':       'Report what you\'re seeing →',
  },

  id: {
    'statusbar.connecting':    'MENYAMBUNG…',
    'statusbar.live':          'AKTIF',
    'statusbar.error':         'GALAT',
    'statusbar.syncing':       'MENYINKRONKAN…',
    'statusbar.sensors':       'Sensor',
    'statusbar.active_24h':    'Aktif 24 jam',
    'statusbar.reports':       'Laporan',
    'statusbar.peaks_24h':     'Lonjakan aktif · 24 jam',
    'statusbar.peaks_7d':      'Lonjakan aktif · 7 hari',
    'statusbar.lang':          'BHS',
    'statusbar.lang_toggle':   'EN',

    'detail.no_pin':           'Belum ada pin dipilih',
    'detail.select_prompt':    'Klik sensor atau laporan pada peta di atas',
    'detail.help_text':        'Panel detail akan menampilkan pembacaan sensor atau isi laporan.',
    'detail.empty':            'Pilih pin pada peta untuk melihat detailnya.',
    'detail.loading':          'Memuat detail sensor…',
    'detail.fetch_failed':     'Gagal memuat detail',

    'history.title_24h':       '24 jam terakhir',
    'history.title_7d':        '7 hari terakhir',
    'history.loading':         'Memuat riwayat…',
    'history.empty':           'Belum ada data riwayat — sensor mungkin masih baru.',
    'history.error':           'Tidak bisa memuat riwayat.',
    'history.no_data':         'tidak ada data',
    'history.peaks_24h':       'Lonjakan · 24 jam',
    'history.peaks_7d':        'Lonjakan · 7 hari',

    'peak.label':              'Lonjakan',
    'peak.threshold_crossed':  'Ambang batas terlampaui',
    'peak.statistical':        'Anomali statistik',
    'peak.none':               'Tidak ada lonjakan terdeteksi.',
    'peak.report_prompt':      'Lonjakan ini belum disertai laporan warga. Jika Anda berada di dekatnya sekarang,',
    'peak.report_link':        'laporkan apa yang Anda lihat →',
    'peak.nearby_reports':     'Laporan di sekitar',
    'peak.nearby_sensors':     'Sensor di sekitar',
    'peak.corroborates':       'Data sensor menguatkan laporan ini',

    'feed.title':              'Laporan warga terbaru',
    'feed.empty':              'Belum ada laporan warga.',
    'feed.expand':             'Buka',
    'feed.collapse':           'Tutup',
    'feed.load_more':          'Muat lebih banyak',
    'feed.filter_all':         'Semua',
    'feed.filter_24h':         '24 jam',
    'feed.filter_7d':          '7 hari',
    'feed.filter_alltime':     'Seluruh waktu',
    'feed.filter_category':    'Kategori',
    'feed.relative_now':       'baru saja',
    'feed.relative_min_ago':   'm lalu',
    'feed.relative_hr_ago':    'j lalu',
    'feed.relative_day_ago':   'h lalu',
    'feed.relative_yday':      'kemarin',

    'action.take_part':        '+ Ikut serta',
    'action.home':             '← Beranda',
    'action.report_now':       'Laporkan apa yang Anda lihat →',
  },
};

const LANG_STORAGE_KEY = 'scb-lang';

function currentLang(){
  try {
    const stored = localStorage.getItem(LANG_STORAGE_KEY);
    if (stored && DICTIONARIES[stored]) return stored;
  } catch(_){}
  return 'en';
}

function setLang(lang){
  if (!DICTIONARIES[lang]) return;
  try { localStorage.setItem(LANG_STORAGE_KEY, lang); } catch(_){}
}

function t(key, lang, fallback){
  const useLang = lang || currentLang();
  const dict = DICTIONARIES[useLang] || DICTIONARIES.en;
  if (dict[key] != null) return dict[key];
  if (DICTIONARIES.en[key] != null) return DICTIONARIES.en[key];
  return fallback != null ? fallback : key;
}

// Format a timestamp as a relative-time string in the current language.
// "12m ago", "3h ago", "yesterday", or absolute date if older than 7d.
function formatRelative(iso, lang){
  if (!iso) return '';
  const useLang = lang || currentLang();
  const then = new Date(iso).getTime();
  if (!isFinite(then)) return '';
  const diffMs = Date.now() - then;
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return t('feed.relative_now', useLang);
  if (mins < 60) return `${mins}${t('feed.relative_min_ago', useLang)}`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}${t('feed.relative_hr_ago', useLang)}`;
  if (hrs < 48) return t('feed.relative_yday', useLang);
  const days = Math.round(hrs / 24);
  if (days < 7) return `${days}${t('feed.relative_day_ago', useLang)}`;
  // Older than a week — fall back to absolute date in the current locale
  return new Date(iso).toLocaleDateString(useLang === 'id' ? 'id-ID' : 'en-GB');
}

if (typeof window !== 'undefined'){
  window.SCB_I18N = { t, currentLang, setLang, formatRelative, DICTIONARIES };
}
