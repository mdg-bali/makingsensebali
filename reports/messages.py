"""
All user-facing text the Bukit AQ Reporter ever sends.

This file exists so a native Bahasa Indonesia speaker can review every
message the bot will send to real users, in one place, without having
to read Python code.

═══════════════════════════════════════════════════════════════════════
 PLEASE REVIEW
═══════════════════════════════════════════════════════════════════════
For each message below, please check:

  1. Bahasa is grammatically correct and feels natural for Bukit users
     (mixed local/expat communities — Balinese, Javanese, Indonesian
     residents from elsewhere, foreign residents who read Bahasa).

  2. Word choice is right — neither overly formal (kaku) nor too casual.
     This bot is run by Fab Lab Bali, so it should feel community-led,
     not bureaucratic and not slangy.

  3. The English glosses (in _italics_) accurately match the Bahasa.

  4. The tone of the consent prompt is honest and not threatening —
     people should feel comfortable saying yes, but also feel free to
     say no.

  5. Technical terms — is "laporan" right for "report"? "Polusi" for
     "pollution"? Or are there more colloquial words a banjar leader
     would use?

  6. Cultural concerns — is anything inadvertently rude, condescending,
     or off-key for the Bukit context?

  7. Emojis — keep them or remove them? They anchor the message
     visually but may feel toy-ish in formal contexts.

═══════════════════════════════════════════════════════════════════════
 HOW TO EDIT
═══════════════════════════════════════════════════════════════════════
Just rewrite any string below. Things in {curly_braces} are variables
the code fills in (counts, categories, etc.) — keep them but you can
move them around within the text.

WhatsApp markdown reminders:
  *bold*    _italic_    ~strike~    ```code```
"""

# =====================================================================
# CONSENT FLOW
# =====================================================================
# Shown on first contact, OR any time someone messages who hasn't yet
# said SETUJU. Reminds opted-out users they need to re-grant.

CONSENT_PROMPT = (
    "🌴 *Pelapor Bukit*\n"
    "_Bukit Reports_\n\n"
    # --- Privacy first, prominently ---
    "🔒 *Privasi adalah prioritas utama kami.*\n"
    "Nomor telepon Anda *TIDAK DISIMPAN* di server kami. Laporan "
    "dibagikan tanpa identitas pengirim.\n\n"
    "_🔒 *Privacy is our top priority.*\n"
    "Your phone number is *NEVER STORED* on our servers. Reports are "
    "shared without sender identity._\n\n"
    # --- What the bot is for ---
    "Bot ini dijalankan oleh Fab Lab Bali agar warga dapat melaporkan "
    "masalah lingkungan dan komunitas di Bukit — sampah di jalan, "
    "kebocoran air, asap pembakaran, debu konstruksi, polusi kendaraan, "
    "dan masalah serupa.\n\n"
    "_This bot is run by Fab Lab Bali so residents can report "
    "environmental and community issues in Bukit — trash on streets, "
    "water leaks, smoke from burning, construction dust, vehicle "
    "pollution, and similar concerns._\n\n"
    # --- The 3 steps ---
    "*Cara melapor (3 langkah):*\n"
    "1️⃣ Tulis deskripsi masalah\n"
    "2️⃣ Bagikan lokasi 📍\n"
    "3️⃣ Kirim foto (opsional)\n\n"
    "_*How to report (3 steps):*_\n"
    "_1️⃣ Write a description of the issue_\n"
    "_2️⃣ Share your location 📍_\n"
    "_3️⃣ Send a photo (optional)_\n\n"
    # --- Consent action ---
    "Untuk melanjutkan, balas *SETUJU*.\n"
    "_To continue, reply *AGREE*._\n\n"
    "Untuk berhenti kapan saja, balas */optout*."
)

# Sent right after the user replies with one of CONSENT_KEYWORDS below.

CONSENT_CONFIRMED = (
    "✅ Terima kasih! Mari mulai laporan Anda.\n"
    "_Thanks! Let's start your report._\n"
    # The category menu is sent immediately after, in the same reply.
)

# Sent after /optout.

OPTOUT_CONFIRMED = (
    "👋 Anda telah keluar. Laporan Anda yang sudah ada tetap tersimpan "
    "secara anonim. Kirim pesan apa pun untuk bergabung kembali.\n"
    "_You have opted out. Existing anonymous reports remain stored. "
    "Send any message to rejoin._"
)

# Words the bot accepts as "yes, I consent". Case-insensitive.
# REVIEWER: should we add other Bahasa affirmatives? "boleh"? "iya"?
# Should we accept Balinese-language words?
CONSENT_KEYWORDS = {"setuju", "agree", "yes", "ya", "ok", "okay"}


# =====================================================================
# COMMANDS — replies to /help, /stats, /about, and unknown commands
# =====================================================================

HELP_REPLY = (
    "🌴 *Cara melapor / How to report*\n\n"
    "Bot akan memandu Anda dalam 4 langkah:\n"
    "_The bot will guide you in 4 steps:_\n\n"
    "1️⃣ Pilih jenis masalah dari menu\n"
    "   _Pick the issue type from the menu_\n"
    "2️⃣ Tulis detail singkat (opsional)\n"
    "   _Write a short detail (optional)_\n"
    "3️⃣ Bagikan lokasi 📍\n"
    "   _Share your location 📍_\n"
    "4️⃣ Kirim foto 📸\n"
    "   _Send a photo 📸_\n\n"
    "Lalu balas *KIRIM* untuk mengirim, atau *BATAL* untuk membatalkan.\n"
    "_Then reply *SEND* to submit, or *CANCEL* to discard._\n\n"
    "Perintah / commands:\n"
    "/baru   — laporan baru / new report\n"
    "/info   — info kampanye / campaign info\n"
    "/stats  — laporan hari ini / today's reports\n"
    "/about  — tentang / about\n"
    "/batal  — batalkan laporan saat ini / cancel current report\n"
    "/optout — berhenti / leave"
)

# {count} is filled in with today's report count
STATS_REPLY = "📊 Hari ini / today: {count} laporan / reports."

ABOUT_REPLY = (
    "🌴 *Pelapor Bukit / Bukit Reports*\n"
    "Fab Lab Bali · komunitas memantau lingkungan\n"
    "_Fab Lab Bali · community environmental watch_\n\n"
    "🔒 Nomor telepon tidak pernah disimpan.\n"
    "_🔒 Phone numbers are never stored._"
)

UNKNOWN_COMMAND = "Perintah tidak dikenal. /help untuk daftar."


# =====================================================================
# PER-MESSAGE-TYPE ACKNOWLEDGMENTS
# =====================================================================
# These are the bot's first reply after a user sends each kind of
# message. They should feel quick, warm, and tell the user what to do
# next.

# After a text-only report (step 1 done; ask for step 2 — location)
TEXT_RECEIVED = (
    "📝 Deskripsi diterima.\n"
    "_Description received._\n\n"
    "*Langkah 2/3:* Bagikan lokasi 📍\n"
    "_*Step 2/3:* Share your location 📍_\n\n"
    "(Lampiran → Lokasi → Kirim lokasi saat ini)\n"
    "_(Attach → Location → Send current location)_"
)

# After a photo, before vision analysis arrives. The analysis follow-up
# (see ANALYSIS_FOLLOWUP_* below) is sent later by the M1 worker.
PHOTO_RECEIVED = (
    "📸 Foto diterima — sedang dianalisis.\n"
    "_Photo received — analyzing._\n\n"
    "Jika belum, bagikan lokasi 📍 untuk melengkapi laporan.\n"
    "_If not yet, share your location 📍 to complete the report._"
)

# After a location pin, when there's a pending report to merge it with
LOCATION_RECEIVED_MERGED = (
    "✅ Lokasi tersimpan — laporan Anda lengkap.\n"
    "_Location saved — your report is complete._\n\n"
    "*Opsional / Optional:* Langkah 3/3 — kirim foto 📸\n"
    "_*Step 3/3:* Send a photo 📸_\n\n"
    "Terima kasih atas kontribusi Anda! 🙏\n"
    "_Thank you for your contribution!_"
)

# After a standalone location pin (no recent text/photo to merge with)
LOCATION_RECEIVED_STANDALONE = (
    "📍 Lokasi diterima.\n"
    "_Location received._\n\n"
    "*Mulai dengan deskripsi:* tulis apa yang Anda lihat di lokasi ini.\n"
    "_*Start with a description:* write what you see at this location._"
)

# If a location message has no lat/lon (rare edge case)
LOCATION_INVALID = "Lokasi tidak terbaca. Coba kirim lagi. / Location unreadable. Try again."

# After a voice note (transcription not yet implemented)
AUDIO_RECEIVED = (
    "🎙️ Pesan suara diterima.\n"
    "_Voice note received._\n\n"
    "Fitur transkripsi otomatis akan segera tersedia. Untuk saat ini, "
    "silakan tulis deskripsi singkat sebagai teks.\n"
    "_Auto-transcription coming soon. For now, please write a short "
    "description as text._"
)


# =====================================================================
# VISION ANALYSIS FOLLOW-UP
# =====================================================================
# Sent by the M1 worker after a photo has been classified. Variables:
#   {cat_emoji} — emoji for the detected category (see CATEGORY_EMOJI)
#   {category}  — schema-valid category name in English
#   {sev_emoji} — colored circle for severity (see SEVERITY_EMOJI)
#   {severity}  — low / medium / high / critical
#   {indicators_line} — optional "Terdeteksi: smoke, fire" line, or ""
#   {description_line} — optional model description italic, or ""
#
# REVIEWER: should category names be translated to Bahasa
# (burning -> pembakaran, trash -> sampah, vehicle -> kendaraan)?

ANALYSIS_FOLLOWUP_TEMPLATE = (
    "{cat_emoji} *Hasil analisis / Analysis*\n"
    "Kategori / category: *{category}*\n"
    "Tingkat / severity: {sev_emoji} {severity}"
    "{indicators_line}"
    "{description_line}"
)

# =====================================================================
# APPROVAL NOTIFICATIONS
# =====================================================================
# Sent when an admin approves or rejects a report in the dashboard.
# Optional — only sent if the bot has a way to reach the original sender
# (notify_jid in the job file, similar to vision follow-up pattern).

REPORT_APPROVED = (
    "✅ Laporan Anda telah disetujui dan dipublikasikan secara anonim.\n"
    "_Your report has been approved and published anonymously._\n\n"
    "Terima kasih telah berkontribusi pada komunitas Bukit. 🙏\n"
    "_Thank you for contributing to the Bukit community._"
)

REPORT_REJECTED = (
    "ℹ️ Laporan Anda telah ditinjau tetapi tidak dipublikasikan saat ini.\n"
    "_Your report was reviewed but not published at this time._\n\n"
    "Ini tidak memengaruhi kemampuan Anda mengirim laporan lain.\n"
    "_This does not affect your ability to send other reports._"
)

# Optional lines — added only when there's content. Leading \n included.
ANALYSIS_INDICATORS_LINE = "\nTerdeteksi / detected: {indicators}"
ANALYSIS_DESCRIPTION_LINE = "\n_{description}_"

# Emoji by category — visual anchor in the reply
CATEGORY_EMOJI = {
    "burning": "🔥",
    "trash": "🚮",
    "water": "💧",
    "vehicle": "🚗",
    "construction": "🏗️",
    "industrial": "🏭",
    "dust": "🌫️",
    "other": "📋",
    "none": "✅",
}

# Color circles for severity, low→critical
SEVERITY_EMOJI = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🟠",
    "critical": "🔴",
}


# =====================================================================
# OPTIONAL: Bahasa category labels
# =====================================================================
# Right now the follow-up shows "Kategori: burning" in English.
# REVIEWER: would Bukit users prefer to see the Bahasa label, e.g.
# "Kategori: pembakaran"? If so, edit these and we'll wire them up:

CATEGORY_BAHASA = {
    "burning": "pembakaran",
    "trash": "sampah",
    "water": "polusi air",
    "vehicle": "kendaraan",
    "construction": "konstruksi",
    "industrial": "industri",
    "dust": "debu",
    "other": "lain-lain",
    "none": "tidak ada",
}

SEVERITY_BAHASA = {
    "low": "rendah",
    "medium": "sedang",
    "high": "tinggi",
    "critical": "kritis",
}


# =====================================================================
# GUIDED REPORTING FLOW — strict-order state machine
# =====================================================================
# The bot walks the user through one report at a time:
#   1. category menu  → user replies with a number 1..N
#   2. optional detail  → free text, or 'lanjut'/'skip' to move on
#   3. location pin    → required
#   4. photo           → required
#   5. confirm         → 'kirim' (send) or 'batal' (cancel)
#
# Wrong-type messages at any step get a polite reminder of what's next,
# NOT a new partial report.

# ---- step 1 of 4: choose category ----------------------------------------
# Numbered list keyed by the same category names used by vision_analyzer
# CATEGORIES. Order here is the order users see in WhatsApp.
CATEGORY_MENU_ITEMS = [
    ("burning",      "🔥",  "Pembakaran sampah",  "Burning trash"),
    ("trash",        "🚮",  "Tumpukan sampah",    "Trash pile / dumping"),
    ("water",        "💧",  "Polusi air",         "Water pollution"),
    ("construction", "🏗️",  "Debu konstruksi",    "Construction dust"),
    ("vehicle",      "🚗",  "Asap kendaraan",     "Vehicle smoke"),
    ("industrial",   "🏭",  "Polusi industri",    "Industrial pollution"),
    ("other",        "📋",  "Lain-lain",          "Other"),
]


def _format_category_menu() -> str:
    lines = []
    for idx, (_key, emoji, bah, eng) in enumerate(CATEGORY_MENU_ITEMS, start=1):
        lines.append(f"  *{idx}.* {emoji} {bah} / _{eng}_")
    return "\n".join(lines)


CATEGORY_MENU = (
    "*Langkah 1/4: Jenis masalah*\n"
    "_*Step 1/4: Issue type*_\n\n"
    "Apa yang Anda lihat? Balas dengan nomor:\n"
    "_What do you see? Reply with a number:_\n\n"
    f"{_format_category_menu()}"
)

# Sent after the bot accepts a valid number. {cat_emoji} and {cat_label}
# get filled in by the dispatcher.
CATEGORY_CHOSEN = (
    "{cat_emoji} *{cat_label}* dipilih.\n"
    "_{cat_emoji} *{cat_label_en}* selected._\n\n"
    "*Langkah 2/4: Detail singkat (opsional)*\n"
    "_*Step 2/4: Short detail (optional)*_\n\n"
    "Tulis satu kalimat tambahan (misal: _\"di pinggir Jalan Pantai \"_), "
    "atau balas *LANJUT* untuk melewati langkah ini.\n"
    "_Type one extra line (e.g. \"on the side of Pantai road\"), "
    "or reply *NEXT* to skip this step._"
)

INVALID_CATEGORY = (
    "❓ Mohon balas dengan nomor (1–{max}).\n"
    "_Please reply with a number (1–{max})._\n\n"
    "Atau ketik */batal* untuk membatalkan.\n"
    "_Or type */cancel* to abort._"
)

# Words that mean "skip the detail step and move on".
DETAIL_SKIP_KEYWORDS = {"lanjut", "skip", "next", "lewati", "-"}

# ---- step 3 of 4: location -----------------------------------------------
ASK_LOCATION = (
    "📝 Detail tersimpan.\n"
    "_Detail saved._\n\n"
    "*Langkah 3/4: Lokasi 📍*\n"
    "_*Step 3/4: Location 📍*_\n\n"
    "Bagikan lokasi WhatsApp Anda:\n"
    "_Share your WhatsApp location:_\n"
    "  📎 Lampiran → Lokasi → Kirim lokasi saat ini\n"
    "  _📎 Attach → Location → Send current location_"
)

ASK_LOCATION_AFTER_SKIP = (
    "⏭️ Dilewati.\n"
    "_Skipped._\n\n"
    "*Langkah 3/4: Lokasi 📍*\n"
    "_*Step 3/4: Location 📍*_\n\n"
    "Bagikan lokasi WhatsApp Anda:\n"
    "_Share your WhatsApp location:_\n"
    "  📎 Lampiran → Lokasi → Kirim lokasi saat ini\n"
    "  _📎 Attach → Location → Send current location_"
)

# ---- step 4 of 4: photo --------------------------------------------------
ASK_PHOTO = (
    "📍 Lokasi tersimpan.\n"
    "_Location saved._\n\n"
    "*Langkah 4/4: Foto 📸*\n"
    "_*Step 4/4: Photo 📸*_\n\n"
    "Kirim satu foto masalah ini (wajib untuk analisis otomatis).\n"
    "_Send one photo of the issue (required for auto-analysis)._"
)

# Sent when the bot couldn't fetch/decrypt the photo from WhatsApp.
# WhatsApp media is E2EE; the bot decrypts via Evolution's
# /chat/getBase64FromMediaMessage endpoint, which can fail (network,
# instance restart, transient WhatsApp issue). User stays at step 4/4
# so they can simply re-send the photo.
PHOTO_FETCH_FAILED = (
    "⚠️ Foto belum berhasil diunduh dari WhatsApp.\n"
    "_Photo couldn't be downloaded from WhatsApp._\n\n"
    "Silakan kirim foto sekali lagi.\n"
    "_Please send the photo one more time._"
)

# ---- confirm / summary ---------------------------------------------------
# {cat_emoji} {cat_label} {detail_line} {lat} {lon}
REPORT_SUMMARY = (
    "📋 *Ringkasan laporan / Report summary*\n\n"
    "Jenis / type: {cat_emoji} {cat_label} / _{cat_label_en}_\n"
    "{detail_line}"
    "Lokasi / location: {lat:.5f}, {lon:.5f}\n"
    "Foto / photo: ✅ tersimpan / saved\n\n"
    "Balas *KIRIM* untuk mengirim ke tim Fab Lab Bali.\n"
    "_Reply *SEND* to submit to the Fab Lab Bali team._\n\n"
    "Atau *BATAL* untuk membatalkan.\n"
    "_Or *CANCEL* to discard._"
)

# Optional detail line in summary
SUMMARY_DETAIL_LINE = "Detail: _{detail}_\n"

# Words accepted as "submit now"
CONFIRM_SEND_KEYWORDS = {"kirim", "send", "ya", "yes", "ok", "submit"}
# Words accepted as "cancel"
CONFIRM_CANCEL_KEYWORDS = {"batal", "cancel", "tidak", "no", "stop"}

# ---- post-submit menu ----------------------------------------------------
REPORT_SUBMITTED = (
    "✅ *Laporan terkirim, terima kasih!* 🙏\n"
    "_Report submitted, thank you!_\n\n"
    "Laporan Anda menunggu peninjauan tim sebelum dipublikasikan "
    "secara anonim.\n"
    "_Your report is pending team review before being published "
    "anonymously._\n\n"
    "*Apa selanjutnya? / What next?*\n"
    "  *1.* 📝 Laporkan masalah lain / Report another issue\n"
    "  *2.* ℹ️  Info kampanye / Campaign info\n"
    "  *3.* 📊 Statistik hari ini / Today's stats\n\n"
    "Atau kunjungi situs kami / Or visit our site:\n"
    "🔗 https://mdg-bali.github.io/smartcitizenbali/"
)

# Numeric shortcuts for the post-submit menu
POSTSUBMIT_NEW_KEYWORDS = {"1", "baru", "new", "lagi", "another"}
POSTSUBMIT_INFO_KEYWORDS = {"2", "info"}
POSTSUBMIT_STATS_KEYWORDS = {"3", "stats", "statistik"}

# ---- info / campaign reply ----------------------------------------------
INFO_REPLY = (
    "🌴 *Smart Citizen Bali*\n"
    "Sebuah inisiatif Fab Lab Bali untuk memantau lingkungan secara "
    "kolaboratif di Bukit.\n"
    "_A Fab Lab Bali initiative for collaborative environmental "
    "monitoring in the Bukit._\n\n"
    "Apa yang kami lakukan:\n"
    "_What we do:_\n"
    "  • Mengumpulkan laporan warga tentang polusi dan masalah lingkungan\n"
    "    _Collect citizen reports on pollution and environmental issues_\n"
    "  • Memetakan dan menganalisis pola dengan komunitas\n"
    "    _Map and analyze patterns together with the community_\n"
    "  • Mendukung tindakan lokal dengan data terbuka\n"
    "    _Support local action with open data_\n\n"
    "🔗 *Lihat peta & data:* https://mdg-bali.github.io/smartcitizenbali/\n"
    "_See the map & data at the link above._\n\n"
    "Untuk laporan baru: ketik */baru*.\n"
    "_For a new report: type */new*._"
)

# ---- cancel --------------------------------------------------------------
CANCEL_CONFIRMED = (
    "🗑️ Laporan dibatalkan.\n"
    "_Report cancelled._\n\n"
    "Ketik */baru* untuk mulai laporan baru, atau */info* untuk info kampanye.\n"
    "_Type */new* to start a new report, or */info* for campaign info._"
)

# ---- wrong-step reminders (strict order) ---------------------------------
# Sent when a user sends a message type that doesn't match the current
# state — e.g. a photo when we're awaiting a category number.

WRONG_STEP_AWAIT_CATEGORY = (
    "⏳ Kita di *Langkah 1/4* — pilih jenis masalah.\n"
    "_We're at *Step 1/4* — pick the issue type._\n\n"
    "Balas dengan nomor (1–{max}), atau */batal* untuk membatalkan.\n"
    "_Reply with a number (1–{max}), or */cancel* to abort._"
)

WRONG_STEP_AWAIT_DETAIL = (
    "⏳ Kita di *Langkah 2/4* — tulis satu kalimat detail, "
    "atau balas *LANJUT* untuk melewati.\n"
    "_We're at *Step 2/4* — type one line of detail, "
    "or reply *NEXT* to skip._"
)

WRONG_STEP_AWAIT_LOCATION = (
    "⏳ Kita di *Langkah 3/4* — bagikan lokasi 📍.\n"
    "_We're at *Step 3/4* — share your location 📍._\n\n"
    "📎 Lampiran → Lokasi → Kirim lokasi saat ini.\n"
    "_📎 Attach → Location → Send current location._"
)

WRONG_STEP_AWAIT_PHOTO = (
    "⏳ Kita di *Langkah 4/4* — kirim satu foto 📸.\n"
    "_We're at *Step 4/4* — send one photo 📸._"
)

WRONG_STEP_AWAIT_CONFIRM = (
    "⏳ Hampir selesai — balas *KIRIM* untuk mengirim, atau *BATAL* untuk membatalkan.\n"
    "_Almost done — reply *SEND* to submit, or *CANCEL* to discard._"
)
