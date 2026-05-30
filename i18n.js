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

    // home — severity hero
    'home.hero.checking':         'Reading Bali…',
    'home.hero.locality_prompt':  'Pick your neighbourhood',
    'home.hero.bali_wide':        'Bali, network-wide',
    'home.hero.use_my_location':  'Use my location',
    'home.hero.peaked_at':        'PM2.5 peaked at',
    'home.hero.who_guideline':    'WHO daily guideline: 5 µg/m³',
    'home.hero.no_data':          'No nearby sensor reporting · pick a neighbourhood, or check the Bali-wide view.',
    'home.hero.no_nearby':        'No sensor near {{loc}} yet — pick a different neighbourhood, or check the Bali-wide view.',
    'home.hero.median_across':    'median across',
    'home.hero.active_sensors':   'active sensors',
    'home.hero.worst_right_now':  'worst right now',
    'home.hero.btn_report':       'Report what you see →',
    'home.hero.btn_near_me':      'What\'s happening near me →',

    'home.severity.green.label':  'Clean',
    'home.severity.green.text':   'Air is clean today in {{loc}}. Outdoor play is fine.',
    'home.severity.yellow.label': 'Moderate',
    'home.severity.yellow.text':  'Air is moderate today in {{loc}}. Sensitive groups (kids, asthma, elderly) should limit prolonged outdoor activity.',
    'home.severity.orange.label': 'Unhealthy',
    'home.severity.orange.text':  'Air is unhealthy in {{loc}} today. Masks recommended outdoors, especially for kids.',
    'home.severity.red.label':    'Dangerous',
    'home.severity.red.text':     'Air is dangerous today in {{loc}}. Stay indoors, windows closed, mask outside.',
    'home.severity.unknown.label':'Live',
    'home.severity.unknown.text': 'Sensors are reporting across Bali. Pick a neighbourhood below to see specifics.',

    // home — 4 CTAs
    'home.cta.title':             'Four ways to take part',
    'home.cta.report.title':      'Report what you\'re seeing',
    'home.cta.report.desc':       'Smell smoke? See burning waste? Notice a smell that wasn\'t there yesterday? Send one WhatsApp message to our bot, our local team verifies, and it joins the public map.',
    'home.cta.report.action':     'Open WhatsApp →',
    'home.cta.report.action_fallback': 'Open the survey (WhatsApp reporting opens in Phase 2) →',
    'home.hero.btn_report_fallback':   'Take the survey → (reporting bot coming soon)',
    'home.cta.survey.title':      'Tell us what matters',
    'home.cta.survey.desc':       'The Phase 1 survey asks residents what environmental issues affect daily life. Eight questions, 5 minutes, shapes where we put sensors next.',
    'home.cta.survey.action':     'Open the survey →',
    'home.cta.workshop.title':    'Get involved with sensors',
    'home.cta.workshop.desc':     'We run sensor-building workshops at Fab Lab Bali — assemble a low-cost air quality node in an afternoon, deploy it on your roof or in your classroom. Sign up to hear about the next workshop.',
    'home.cta.workshop.action':   'Workshop signup →',
    'home.cta.share.title':       'Share what\'s happening',
    'home.cta.share.desc':        'Generate a shareable card about today\'s air in your neighbourhood and post it where the conversation already lives — WhatsApp, Instagram, Telegram. Each share helps more people see the data.',
    'home.cta.share.action':      'Create a card →',

    // home — daily correlation panel
    'home.story.section':         'Today\'s story · sensors meet residents',
    'home.story.fallback_title':  'When the data and the residents tell the same story',
    'home.story.fallback_body':   'Each day we pick the most-striking correlation between sensor peaks and citizen reports. When a PM spike has a matching report — burning waste, construction, traffic — the campaign treats it as a confirmed signal. Check back tomorrow.',
    'home.story.read_data':       'See the data →',
    'home.story.read_report':     'Read the report →',
    'home.story.report_yours':    'Report what you\'re seeing →',

    // home — audience sections
    'home.audience.families.label':     'For families and residents',
    'home.audience.families.title':     'Today in your neighbourhood',
    'home.audience.families.subtitle':  'What\'s happening in the air where your kids play, sleep, study.',
    'home.audience.teachers.label':     'For teachers and schools',
    'home.audience.teachers.title':     'Bring the data into your classroom',
    'home.audience.teachers.subtitle':  'Real local data to teach the science of where students live.',
    'home.audience.officials.label':    'For policymakers and analysts',
    'home.audience.officials.title':    'Evidence you can act on',
    'home.audience.officials.subtitle': 'Aggregate data, citation guidance, and direct contact with the campaign team.',

    'home.families.nearby_reports':     'Most recent nearby reports',
    'home.families.guidance':           'Plain-language guidance',
    'home.families.guidance_windows':   'Keep windows closed when PM2.5 is above 35 µg/m³.',
    'home.families.guidance_masks':     'Use a N95 / KF94 mask for kids and elderly when readings are unhealthy.',
    'home.families.guidance_humidity':  'Indoor humidity above 60% sustained → mold risk. Run a dehumidifier or open windows on dry days.',
    'home.families.mold_label':         'Mold-risk indicator',
    'home.families.mold_ok':            'Humidity within safe range across the network.',
    'home.families.mold_warning':       'Humidity has been above 60% for 24h+ in your area. Check for damp corners, run a dehumidifier in bedrooms.',

    'home.teachers.lesson_title':       'A lesson plan using local Bali air quality data',
    'home.teachers.lesson_pitch':       'A 45-minute lesson where students compare your school\'s last-24h PM2.5 reading to the WHO daily guideline — then to a reference school in Barcelona via Smart Citizen\'s global network.',
    'home.teachers.lesson_download':    'Download the lesson plan (PDF) →',
    'home.teachers.workshop_title':     'Smart Citizen Bali for schools',
    'home.teachers.workshop_pitch':     'A half-day workshop at Fab Lab Bali for one or two teachers per school. Build the sensor, install it on a classroom wall, integrate the live readings into a science unit.',
    'home.teachers.example_title':      'A concrete example',
    'home.teachers.example_body':       'Your students measure PM2.5 in the schoolyard over a week. They calculate the average. They compare it to WHO\'s 5 µg/m³ annual guideline. Then they pull last week\'s average from a school in Barcelona via Smart Citizen\'s public API, and they discuss the difference. Citizenship through data.',

    'home.officials.lineage_label':     'Data lineage',
    'home.officials.downloads_title':   'Aggregate downloads',
    'home.officials.csv_30d':           'Last 30 days CSV →',
    'home.officials.summary_pdf':       'Monthly summary PDF →',
    'home.officials.cite_title':        'How to cite Smart Citizen Bali data',
    'home.officials.cite_body':         'Smart Citizen Bali (Fab Lab Bali, {{year}}). Open environmental sensor network and citizen reports, Bali, Indonesia. Retrieved from https://mdg-bali.github.io/smartcitizenbali/ on [date].',
    'home.officials.dashboard_link':    'Open the analytical dashboard →',
    'home.officials.contact':           'Direct engagement:',

    // home — shareable cards
    'home.share.section':         'Shareable cards',
    'home.share.title':           'Make what\'s happening visible',
    'home.share.subtitle':        'Pick a template, pick a neighbourhood, share where the conversation already is.',
    'home.share.tpl_today':       'Today in {{loc}}',
    'home.share.tpl_week':        'This week in {{loc}}',
    'home.share.tpl_mold':        'Mold risk: {{loc}}',
    'home.share.tpl_burn':        'Burning corridor: {{loc}}',
    'home.share.download':        '⬇ Download PNG',
    'home.share.wa':              'Share on WhatsApp',
    'home.share.copy':            'Copy link',
    'home.share.copied':          'Copied',
    'home.share.choose_loc':      'Choose neighbourhood',
    'home.share.as_of':           'as of {{time}} WITA',
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

    'home.hero.checking':         'Membaca Bali…',
    'home.hero.locality_prompt':  'Pilih daerah Anda',
    'home.hero.bali_wide':        'Bali, seluruh jaringan',
    'home.hero.use_my_location':  'Gunakan lokasi saya',
    'home.hero.peaked_at':        'PM2.5 memuncak di',
    'home.hero.who_guideline':    'Panduan harian WHO: 5 µg/m³',
    'home.hero.no_data':          'Tidak ada sensor terdekat · pilih daerah, atau lihat tampilan seluruh Bali.',
    'home.hero.no_nearby':        'Belum ada sensor dekat {{loc}} — pilih daerah lain, atau lihat tampilan seluruh Bali.',
    'home.hero.median_across':    'median dari',
    'home.hero.active_sensors':   'sensor aktif',
    'home.hero.worst_right_now':  'tertinggi sekarang',
    'home.hero.btn_report':       'Laporkan apa yang Anda lihat →',
    'home.hero.btn_near_me':      'Apa yang terjadi di sekitar saya →',

    'home.severity.green.label':  'Bersih',
    'home.severity.green.text':   'Udara bersih hari ini di {{loc}}. Bermain di luar aman.',
    'home.severity.yellow.label': 'Sedang',
    'home.severity.yellow.text':  'Udara sedang hari ini di {{loc}}. Kelompok sensitif (anak, asma, lansia) sebaiknya batasi aktivitas luar yang lama.',
    'home.severity.orange.label': 'Tidak sehat',
    'home.severity.orange.text':  'Udara tidak sehat di {{loc}} hari ini. Disarankan memakai masker di luar, terutama untuk anak.',
    'home.severity.red.label':    'Berbahaya',
    'home.severity.red.text':     'Udara berbahaya hari ini di {{loc}}. Tetap di dalam, jendela tertutup, pakai masker bila keluar.',
    'home.severity.unknown.label':'Aktif',
    'home.severity.unknown.text': 'Sensor sedang melaporkan di seluruh Bali. Pilih daerah di bawah untuk detail.',

    'home.cta.title':             'Empat cara untuk ikut serta',
    'home.cta.report.title':      'Laporkan apa yang Anda lihat',
    'home.cta.report.desc':       'Tercium asap? Lihat sampah dibakar? Cium bau yang kemarin tidak ada? Kirim satu pesan WhatsApp ke bot kami, tim lokal kami verifikasi, lalu masuk ke peta publik.',
    'home.cta.report.action':     'Buka WhatsApp →',
    'home.cta.report.action_fallback': 'Buka survei (pelaporan WhatsApp dibuka di Fase 2) →',
    'home.hero.btn_report_fallback':   'Ikuti survei → (bot pelaporan segera hadir)',
    'home.cta.survey.title':      'Beri tahu kami apa yang penting',
    'home.cta.survey.desc':       'Survei Fase 1 menanyakan kepada warga isu lingkungan apa yang berdampak pada kehidupan sehari-hari. Delapan pertanyaan, 5 menit, menentukan letak sensor berikutnya.',
    'home.cta.survey.action':     'Buka survei →',
    'home.cta.workshop.title':    'Terlibat dengan sensor',
    'home.cta.workshop.desc':     'Kami menjalankan lokakarya pembuatan sensor di Fab Lab Bali — rakit sensor kualitas udara murah dalam satu sore, pasang di atap rumah atau di kelas Anda. Daftar untuk mendengar lokakarya berikutnya.',
    'home.cta.workshop.action':   'Daftar lokakarya →',
    'home.cta.share.title':       'Bagikan apa yang terjadi',
    'home.cta.share.desc':        'Buat kartu yang dapat dibagikan tentang udara di daerah Anda hari ini dan posting di tempat percakapan sudah hidup — WhatsApp, Instagram, Telegram. Tiap bagikan membantu lebih banyak orang melihat datanya.',
    'home.cta.share.action':      'Buat kartu →',

    'home.story.section':         'Cerita hari ini · sensor bertemu warga',
    'home.story.fallback_title':  'Ketika data dan warga menceritakan kisah yang sama',
    'home.story.fallback_body':   'Setiap hari kami memilih korelasi paling mencolok antara lonjakan sensor dan laporan warga. Ketika lonjakan PM bertemu laporan yang cocok — pembakaran sampah, konstruksi, lalu lintas — kampanye memperlakukannya sebagai sinyal terkonfirmasi. Cek lagi besok.',
    'home.story.read_data':       'Lihat data →',
    'home.story.read_report':     'Baca laporan →',
    'home.story.report_yours':    'Laporkan apa yang Anda lihat →',

    'home.audience.families.label':     'Untuk keluarga dan warga',
    'home.audience.families.title':     'Hari ini di daerah Anda',
    'home.audience.families.subtitle':  'Apa yang terjadi di udara tempat anak Anda bermain, tidur, belajar.',
    'home.audience.teachers.label':     'Untuk guru dan sekolah',
    'home.audience.teachers.title':     'Bawa data ke ruang kelas',
    'home.audience.teachers.subtitle':  'Data lokal nyata untuk mengajarkan sains tempat tinggal siswa.',
    'home.audience.officials.label':    'Untuk pembuat kebijakan dan analis',
    'home.audience.officials.title':    'Bukti yang bisa Anda gunakan',
    'home.audience.officials.subtitle': 'Data agregat, panduan sitasi, dan kontak langsung tim kampanye.',

    'home.families.nearby_reports':     'Laporan terdekat terbaru',
    'home.families.guidance':           'Panduan dalam bahasa sehari-hari',
    'home.families.guidance_windows':   'Tutup jendela saat PM2.5 di atas 35 µg/m³.',
    'home.families.guidance_masks':     'Pakai masker N95 / KF94 untuk anak dan lansia saat udara tidak sehat.',
    'home.families.guidance_humidity':  'Kelembaban dalam ruangan di atas 60% terus-menerus → risiko jamur. Jalankan dehumidifier atau buka jendela saat cuaca kering.',
    'home.families.mold_label':         'Indikator risiko jamur',
    'home.families.mold_ok':            'Kelembaban masih dalam rentang aman di jaringan.',
    'home.families.mold_warning':       'Kelembaban di atas 60% selama 24 jam+ di daerah Anda. Periksa sudut lembab, jalankan dehumidifier di kamar tidur.',

    'home.teachers.lesson_title':       'Rencana pelajaran menggunakan data udara Bali setempat',
    'home.teachers.lesson_pitch':       'Pelajaran 45 menit di mana siswa membandingkan PM2.5 sekolah Anda 24 jam terakhir dengan panduan harian WHO — lalu dengan sekolah referensi di Barcelona melalui jaringan global Smart Citizen.',
    'home.teachers.lesson_download':    'Unduh rencana pelajaran (PDF) →',
    'home.teachers.workshop_title':     'Smart Citizen Bali untuk sekolah',
    'home.teachers.workshop_pitch':     'Lokakarya setengah hari di Fab Lab Bali untuk satu atau dua guru per sekolah. Rakit sensor, pasang di dinding kelas, integrasikan bacaan langsung ke dalam unit sains.',
    'home.teachers.example_title':      'Contoh konkret',
    'home.teachers.example_body':       'Siswa mengukur PM2.5 di halaman sekolah selama seminggu. Mereka menghitung rata-rata. Mereka bandingkan dengan panduan tahunan WHO 5 µg/m³. Lalu mereka ambil rata-rata pekan lalu dari sekolah di Barcelona melalui API publik Smart Citizen, dan mereka mendiskusikan selisihnya. Kewargaan melalui data.',

    'home.officials.lineage_label':     'Silsilah data',
    'home.officials.downloads_title':   'Unduhan agregat',
    'home.officials.csv_30d':           'CSV 30 hari terakhir →',
    'home.officials.summary_pdf':       'Ringkasan bulanan PDF →',
    'home.officials.cite_title':        'Cara mensitasi data Smart Citizen Bali',
    'home.officials.cite_body':         'Smart Citizen Bali (Fab Lab Bali, {{year}}). Jaringan sensor lingkungan terbuka dan laporan warga, Bali, Indonesia. Diakses dari https://mdg-bali.github.io/smartcitizenbali/ pada [tanggal].',
    'home.officials.dashboard_link':    'Buka dasbor analitis →',
    'home.officials.contact':           'Engagement langsung:',

    'home.share.section':         'Kartu untuk dibagikan',
    'home.share.title':           'Jadikan apa yang terjadi terlihat',
    'home.share.subtitle':        'Pilih template, pilih daerah, bagikan di tempat percakapan sudah hidup.',
    'home.share.tpl_today':       'Hari ini di {{loc}}',
    'home.share.tpl_week':        'Pekan ini di {{loc}}',
    'home.share.tpl_mold':        'Risiko jamur: {{loc}}',
    'home.share.tpl_burn':        'Koridor pembakaran: {{loc}}',
    'home.share.download':        '⬇ Unduh PNG',
    'home.share.wa':              'Bagikan via WhatsApp',
    'home.share.copy':            'Salin tautan',
    'home.share.copied':          'Tersalin',
    'home.share.choose_loc':      'Pilih daerah',
    'home.share.as_of':           'per {{time}} WITA',
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
  // P1-1: keep the document language attribute in sync so screen readers
  // switch pronunciation when the user toggles language.
  if (typeof document !== 'undefined' && document.documentElement){
    document.documentElement.lang = lang;
  }
}

function t(key, lang, fallback, vars){
  // Allow t(key, vars) shorthand when 2nd arg looks like a dict, not a lang code
  if (lang && typeof lang === 'object' && !Array.isArray(lang)){
    vars = lang;
    lang = null;
  }
  const useLang = lang || currentLang();
  const dict = DICTIONARIES[useLang] || DICTIONARIES.en;
  let s = dict[key] != null ? dict[key]
        : DICTIONARIES.en[key] != null ? DICTIONARIES.en[key]
        : (fallback != null ? fallback : key);
  if (vars && typeof s === 'string'){
    s = s.replace(/\{\{(\w+)\}\}/g, (_, name) => vars[name] != null ? String(vars[name]) : '');
  }
  return s;
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
