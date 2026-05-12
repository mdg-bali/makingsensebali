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
    "✅ Terima kasih! Sekarang Anda bisa melaporkan masalah.\n"
    "_Thanks! You can now report issues._\n\n"
    "*Mulai dengan menulis deskripsi singkat tentang apa yang Anda lihat.*\n"
    "_*Start by writing a short description of what you see.*_\n\n"
    "Setelah itu, bot akan meminta lokasi 📍 dan kemudian foto (opsional).\n"
    "_Then the bot will ask for a location 📍, then a photo (optional)._\n\n"
    "Perintah / commands:\n"
    "  /help  — bantuan / help\n"
    "  /stats — laporan hari ini / today's reports\n"
    "  /optout — berhenti / leave"
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
    "🌴 *Cara melapor:*\n"
    "1️⃣ Tulis deskripsi masalah\n"
    "2️⃣ Bagikan lokasi 📍\n"
    "3️⃣ Kirim foto (opsional)\n\n"
    "_*How to report:*_\n"
    "_1️⃣ Write a description_\n"
    "_2️⃣ Share your location 📍_\n"
    "_3️⃣ Send a photo (optional)_\n\n"
    "Perintah / commands:\n"
    "/stats  — laporan hari ini / today's reports\n"
    "/about  — tentang / about\n"
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
