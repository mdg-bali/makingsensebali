"""
All user-facing text the Making Sense Bali reporter ever sends — trilingual.

This file exists so native speakers can review every message the bot
will send to real users, in one place, without reading Python code.

Languages: "en" (English), "id" (Bahasa Indonesia), "es" (Español).

═══════════════════════════════════════════════════════════════════════
 STRUCTURE
═══════════════════════════════════════════════════════════════════════
Every user-facing message is an entry in MESSAGES, keyed first by
language code, then by a message id. To fetch a message in code, use:

    t("category_menu", lang, max=7)

`t(key, lang, **kwargs)` looks up MESSAGES[lang][key] (falling back to
English if the language or key is missing), then .format(**kwargs)s it.

Things in {curly_braces} are variables the code fills in (counts,
categories, etc.) — keep them but you can move them around in the text.

WhatsApp markdown reminders:
  *bold*    _italic_    ~strike~    ```code```

═══════════════════════════════════════════════════════════════════════
 PLEASE REVIEW
═══════════════════════════════════════════════════════════════════════
  • Bahasa: natural for Bali users (mixed local/expat), neither too
    formal (kaku) nor slangy. Run by Fab Lab Bali — community-led,
    not bureaucratic.
  • Español: written by the assistant for Tomas (native speaker) to
    review — warm, community-led, natural, matching the English tone.
  • Consent tone: honest, not threatening — people should feel free to
    say yes or no.
  • Emojis: keep or drop? They anchor visually but may feel toy-ish.
"""

# =====================================================================
# Non-localized lookups (shared across languages)
# =====================================================================

# Emoji by category — visual anchor in replies
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
# Category menu items — keyed by language for the labels
# =====================================================================
# The first element of each tuple is the schema category key (stable,
# used by vision_analyzer). The labels are per-language.
#   key, emoji, {"en": label, "id": label, "es": label}
CATEGORY_MENU_ITEMS = [
    ("burning",      "🔥",  {"en": "Burning trash",          "id": "Pembakaran sampah",  "es": "Quema de basura"}),
    ("trash",        "🚮",  {"en": "Trash pile / dumping",   "id": "Tumpukan sampah",    "es": "Basura acumulada / vertido"}),
    ("water",        "💧",  {"en": "Water pollution",        "id": "Polusi air",         "es": "Contaminación del agua"}),
    ("construction", "🏗️",  {"en": "Construction dust",      "id": "Debu konstruksi",    "es": "Polvo de construcción"}),
    ("vehicle",      "🚗",  {"en": "Vehicle smoke",          "id": "Asap kendaraan",     "es": "Humo de vehículos"}),
    ("industrial",   "🏭",  {"en": "Industrial pollution",   "id": "Polusi industri",    "es": "Contaminación industrial"}),
    ("other",        "📋",  {"en": "Other",                  "id": "Lain-lain",          "es": "Otro"}),
]


def category_label(category_key: str, lang: str) -> str:
    """Localized label for a category key (defaults to English / the key)."""
    for key, _emoji, labels in CATEGORY_MENU_ITEMS:
        if key == category_key:
            return labels.get(lang) or labels.get("en") or category_key
    return category_key


def format_category_menu(lang: str) -> str:
    lines = []
    for idx, (_key, emoji, labels) in enumerate(CATEGORY_MENU_ITEMS, start=1):
        label = labels.get(lang) or labels.get("en")
        lines.append(f"  *{idx}.* {emoji} {label}")
    return "\n".join(lines)


# =====================================================================
# Keyword sets (language-agnostic; accept all variants)
# =====================================================================

# Words the bot accepts as "yes, I consent". Case-insensitive.
CONSENT_KEYWORDS = {"setuju", "agree", "yes", "ya", "ok", "okay", "si", "sí", "acepto"}

# Words that mean "skip the optional comment step".
COMMENT_SKIP_KEYWORDS = {"lewati", "skip", "lanjut", "next", "-", "omitir", "saltar"}

# Words accepted as "submit now"
CONFIRM_SEND_KEYWORDS = {"kirim", "send", "ya", "yes", "ok", "submit", "enviar", "si", "sí"}
# Words accepted as "cancel"
CONFIRM_CANCEL_KEYWORDS = {"batal", "cancel", "tidak", "no", "stop", "cancelar"}

# Yes / No for the optional "did this just happen now?" incident-time step.
INCIDENT_TIME_YES_KEYWORDS = {
    "yes", "y", "yeah", "yep", "now", "just now",
    "ya", "iya", "sekarang", "barusan",
    "sí", "si", "ahora",
}
INCIDENT_TIME_NO_KEYWORDS = {
    "no", "n", "nope", "not now", "earlier",
    "tidak", "nggak", "enggak", "tadi",
    "antes",
}
INCIDENT_TIME_SKIP_KEYWORDS = COMMENT_SKIP_KEYWORDS

# Post-submit menu shortcuts
POSTSUBMIT_NEW_KEYWORDS = {"1", "baru", "new", "lagi", "another", "otro", "nuevo"}
POSTSUBMIT_LEARN_KEYWORDS = {"2", "learn", "more", "info", "belajar", "aprender"}
POSTSUBMIT_FEEDBACK_KEYWORDS = {"3", "feedback", "masukan", "comentario", "comentarios"}

# Language picker — accepted answers per language code.
LANG_PICK = {
    "en": {"1", "en", "eng", "english", "inggris"},
    "id": {"2", "id", "ind", "indonesia", "indonesian", "bahasa", "bahasa indonesia"},
    "es": {"3", "es", "esp", "espanol", "español", "spanish", "castellano"},
}


def parse_language_choice(text: str) -> str:
    """Map a free-text reply to a language code, or "" if not recognized."""
    t_ = (text or "").strip().lower()
    for code, accepted in LANG_PICK.items():
        if t_ in accepted:
            return code
    return ""


# =====================================================================
# THE MESSAGE TABLE
# =====================================================================
# MESSAGES[lang][message_id] -> template string.

MESSAGES = {
    # -----------------------------------------------------------------
    # ENGLISH
    # -----------------------------------------------------------------
    "en": {
        # --- language picker (also exists per-language for re-prompts) ---
        "language_picker": (
            "🌴 *Making Sense Bali*\n\n"
            "Choose your language / Pilih bahasa / Elige tu idioma:\n\n"
            "  *1.* English\n"
            "  *2.* Bahasa Indonesia\n"
            "  *3.* Español\n\n"
            "Reply 1, 2, or 3."
        ),

        # --- consent ---
        "consent_prompt": (
            "🌴 *Making Sense Bali*\n\n"
            "🔒 *Privacy is our top priority.*\n"
            "Your phone number is *NEVER STORED* on our servers. Reports are "
            "shared without sender identity.\n\n"
            "This bot is run by Fab Lab Bali so residents can report "
            "environmental and community issues in your area — trash on streets, "
            "water leaks, smoke from burning, construction dust, vehicle "
            "pollution, and similar concerns.\n\n"
            "*How to report (3 steps):*\n"
            "1️⃣ Pick the issue type\n"
            "2️⃣ Send a photo 📸\n"
            "3️⃣ Share your location 📍\n\n"
            "To continue, reply *AGREE*.\n\n"
            "To stop at any time, reply */optout*."
        ),
        "consent_confirmed": "✅ Thanks! Let's start your report.\n",
        "optout_confirmed": (
            "👋 You have opted out. Existing anonymous reports remain stored. "
            "Send any message to rejoin."
        ),

        # --- commands ---
        "help_reply": (
            "🌴 *How to report*\n\n"
            "The bot guides you in 3 steps:\n\n"
            "1️⃣ Pick the issue type from the menu\n"
            "2️⃣ Send a photo 📸\n"
            "3️⃣ Share your location 📍\n\n"
            "You can then add an optional one-line comment, then reply "
            "*SEND* to submit or *CANCEL* to discard.\n\n"
            "Commands:\n"
            "/baru   — new report\n"
            "/about  — about\n"
            "/batal  — cancel current report\n"
            "/optout — leave"
        ),
        "about_reply": (
            "🌴 *Making Sense Bali*\n"
            "Fab Lab Bali · community environmental watch\n\n"
            "🔒 Phone numbers are never stored."
        ),
        "unknown_command": "Unknown command. Type /help for the list.",

        # --- per-message acknowledgments ---
        "audio_received": (
            "🎙️ Voice note received.\n\n"
            "Auto-transcription is coming soon. For now, please write a short "
            "comment as text, or continue the steps."
        ),

        # --- guided flow ---
        "category_menu": (
            "*Step 1/3: Issue type*\n\n"
            "What do you see? Reply with a number:\n\n"
            "{menu}"
        ),
        "category_chosen": (
            "{cat_emoji} *{cat_label}* selected.\n\n"
            "*Step 2/3: Photo 📸*\n\n"
            "Send one photo of the issue (required for auto-analysis)."
        ),
        "invalid_category": (
            "❓ Please reply with a number (1–{max}).\n\n"
            "Or type */batal* to abort."
        ),
        "photo_received": (
            "📸 Photo received.\n\n"
            "*Step 3/3: Location 📍*\n\n"
            "Share where this is, in any of these ways:\n"
            "  📎 Attach → Location → Send current location\n"
            "  🔗 Paste a Google Maps link\n"
            "  📝 Or type the coordinates as `lat, lon`"
        ),
        "photo_fetch_failed": (
            "⚠️ The photo couldn't be downloaded from WhatsApp.\n\n"
            "Please send the photo one more time."
        ),
        "ask_comment": (
            "*Optional:* add a short comment (e.g. \"on the side of Pantai "
            "road\"), or reply *SKIP* to continue."
        ),
        "location_invalid": (
            "❓ I couldn't read that as a location.\n\n"
            "Please send it in one of these ways:\n"
            "  📎 Attach → Location → Send current location\n"
            "  🔗 Paste a Google Maps link\n"
            "  📝 Or type the coordinates as `lat, lon` "
            "(e.g. `-8.8290, 115.0850`)"
        ),
        "location_link_unresolved": (
            "🔗 That looks like a shortened map link I can't open here.\n\n"
            "Please send the location pin instead (📎 Attach → Location), "
            "or paste the coordinates as `lat, lon`, or the expanded link."
        ),
        "report_summary": (
            "📋 *Report summary*\n\n"
            "Type: {cat_emoji} {cat_label}\n"
            "Photo: ✅ saved\n"
            "Location: {lat:.5f}, {lon:.5f}\n"
            "{time_line}"
            "{comment_line}"
            "\n"
            "Reply *SEND* to submit to the Fab Lab Bali team.\n\n"
            "Or *CANCEL* to discard."
        ),
        "summary_comment_line": "Comment: _{comment}_\n",
        "summary_time_line": "When: {when}\n",
        "ask_incident_time": (
            "✅ Location saved.\n\n"
            "*Did this just happen now?* Reply *yes* or *no*."
        ),
        "ask_incident_time_detail": (
            "🕒 Roughly when did it happen?\n\n"
            "For example: _2pm today_, _yesterday evening_, _3 hours ago_.\n"
            "Or reply *skip* if you're not sure."
        ),
        "report_submitted": (
            "✅ *Report submitted, thank you!* 🙏\n\n"
            "Your report is pending team review before being published "
            "anonymously.\n\n"
            "*What next?*\n"
            "  *1.* 📝 Report another issue\n"
            "  *2.* ℹ️  Learn more → https://mdg-bali.github.io/makingsensebali/\n"
            "  *3.* 💬 Give feedback"
        ),
        "feedback_prompt": (
            "💬 We'd love your feedback.\n\n"
            "Type your message and it will be shared anonymously with the "
            "Fab Lab Bali team (no phone number stored)."
        ),
        "feedback_thanks": (
            "🙏 Thank you for your feedback!\n\n"
            "*What next?*\n"
            "  *1.* 📝 Report another issue\n"
            "  *2.* ℹ️  Learn more → https://mdg-bali.github.io/makingsensebali/\n"
            "  *3.* 💬 Give feedback"
        ),
        "cancel_confirmed": (
            "🗑️ Report cancelled.\n\n"
            "Type */baru* to start a new report."
        ),
        "no_active_to_cancel": (
            "No active report to cancel.\n\n"
            "Type */baru* to start a report."
        ),

        # --- wrong-step reminders ---
        "wrong_step_category": (
            "⏳ We're at *Step 1/3* — pick the issue type.\n\n"
            "Reply with a number (1–{max}), or */batal* to abort."
        ),
        "wrong_step_photo": (
            "⏳ We're at *Step 2/3* — send one photo 📸."
        ),
        "wrong_step_location": (
            "⏳ We're at *Step 3/3* — share your location 📍.\n\n"
            "📎 Attach → Location → Send current location, paste a Google "
            "Maps link, or type the coordinates as `lat, lon`."
        ),
        "wrong_step_confirm": (
            "⏳ Almost done — reply *SEND* to submit, or *CANCEL* to discard."
        ),

        # --- approval notifications ---
        "report_approved": (
            "✅ Your report has been approved and published anonymously.\n\n"
            "Thank you for contributing to the Bali community. 🙏"
        ),
        "report_rejected": (
            "ℹ️ Your report was reviewed but not published at this time.\n\n"
            "This does not affect your ability to send other reports."
        ),
    },

    # -----------------------------------------------------------------
    # BAHASA INDONESIA
    # -----------------------------------------------------------------
    "id": {
        "language_picker": (
            "🌴 *Making Sense Bali*\n\n"
            "Choose your language / Pilih bahasa / Elige tu idioma:\n\n"
            "  *1.* English\n"
            "  *2.* Bahasa Indonesia\n"
            "  *3.* Español\n\n"
            "Balas 1, 2, atau 3."
        ),

        "consent_prompt": (
            "🌴 *Making Sense Bali*\n\n"
            "🔒 *Privasi adalah prioritas utama kami.*\n"
            "Nomor telepon Anda *TIDAK DISIMPAN* di server kami. Laporan "
            "dibagikan tanpa identitas pengirim.\n\n"
            "Bot ini dijalankan oleh Fab Lab Bali agar warga dapat melaporkan "
            "masalah lingkungan dan komunitas di wilayah Anda — sampah di jalan, "
            "kebocoran air, asap pembakaran, debu konstruksi, polusi kendaraan, "
            "dan masalah serupa.\n\n"
            "*Cara melapor (3 langkah):*\n"
            "1️⃣ Pilih jenis masalah\n"
            "2️⃣ Kirim foto 📸\n"
            "3️⃣ Bagikan lokasi 📍\n\n"
            "Untuk melanjutkan, balas *SETUJU*.\n\n"
            "Untuk berhenti kapan saja, balas */optout*."
        ),
        "consent_confirmed": "✅ Terima kasih! Mari mulai laporan Anda.\n",
        "optout_confirmed": (
            "👋 Anda telah keluar. Laporan Anda yang sudah ada tetap tersimpan "
            "secara anonim. Kirim pesan apa pun untuk bergabung kembali."
        ),

        "help_reply": (
            "🌴 *Cara melapor*\n\n"
            "Bot akan memandu Anda dalam 3 langkah:\n\n"
            "1️⃣ Pilih jenis masalah dari menu\n"
            "2️⃣ Kirim foto 📸\n"
            "3️⃣ Bagikan lokasi 📍\n\n"
            "Anda lalu dapat menambahkan satu kalimat komentar (opsional), "
            "lalu balas *KIRIM* untuk mengirim atau *BATAL* untuk membatalkan.\n\n"
            "Perintah:\n"
            "/baru   — laporan baru\n"
            "/about  — tentang\n"
            "/batal  — batalkan laporan saat ini\n"
            "/optout — berhenti"
        ),
        "about_reply": (
            "🌴 *Making Sense Bali*\n"
            "Fab Lab Bali · komunitas memantau lingkungan\n\n"
            "🔒 Nomor telepon tidak pernah disimpan."
        ),
        "unknown_command": "Perintah tidak dikenal. Ketik /help untuk daftar.",

        "audio_received": (
            "🎙️ Pesan suara diterima.\n\n"
            "Fitur transkripsi otomatis akan segera tersedia. Untuk saat ini, "
            "silakan tulis komentar singkat sebagai teks, atau lanjutkan langkah."
        ),

        "category_menu": (
            "*Langkah 1/3: Jenis masalah*\n\n"
            "Apa yang Anda lihat? Balas dengan nomor:\n\n"
            "{menu}"
        ),
        "category_chosen": (
            "{cat_emoji} *{cat_label}* dipilih.\n\n"
            "*Langkah 2/3: Foto 📸*\n\n"
            "Kirim satu foto masalah ini (wajib untuk analisis otomatis)."
        ),
        "invalid_category": (
            "❓ Mohon balas dengan nomor (1–{max}).\n\n"
            "Atau ketik */batal* untuk membatalkan."
        ),
        "photo_received": (
            "📸 Foto diterima.\n\n"
            "*Langkah 3/3: Lokasi 📍*\n\n"
            "Bagikan lokasinya, dengan salah satu cara berikut:\n"
            "  📎 Lampiran → Lokasi → Kirim lokasi saat ini\n"
            "  🔗 Tempel tautan Google Maps\n"
            "  📝 Atau ketik koordinat sebagai `lat, lon`"
        ),
        "photo_fetch_failed": (
            "⚠️ Foto belum berhasil diunduh dari WhatsApp.\n\n"
            "Silakan kirim foto sekali lagi."
        ),
        "ask_comment": (
            "*Opsional:* tambahkan komentar singkat (misal: \"di pinggir Jalan "
            "Pantai\"), atau balas *LEWATI* untuk melanjutkan."
        ),
        "location_invalid": (
            "❓ Saya tidak dapat membaca itu sebagai lokasi.\n\n"
            "Silakan kirim dengan salah satu cara berikut:\n"
            "  📎 Lampiran → Lokasi → Kirim lokasi saat ini\n"
            "  🔗 Tempel tautan Google Maps\n"
            "  📝 Atau ketik koordinat sebagai `lat, lon` "
            "(misal: `-8.8290, 115.0850`)"
        ),
        "location_link_unresolved": (
            "🔗 Itu tampak seperti tautan peta yang dipersingkat yang tidak "
            "dapat saya buka di sini.\n\n"
            "Silakan kirim pin lokasi (📎 Lampiran → Lokasi), atau tempel "
            "koordinat sebagai `lat, lon`, atau tautan lengkapnya."
        ),
        "report_summary": (
            "📋 *Ringkasan laporan*\n\n"
            "Jenis: {cat_emoji} {cat_label}\n"
            "Foto: ✅ tersimpan\n"
            "Lokasi: {lat:.5f}, {lon:.5f}\n"
            "{time_line}"
            "{comment_line}"
            "\n"
            "Balas *KIRIM* untuk mengirim ke tim Fab Lab Bali.\n\n"
            "Atau *BATAL* untuk membatalkan."
        ),
        "summary_comment_line": "Komentar: _{comment}_\n",
        "summary_time_line": "Waktu: {when}\n",
        "ask_incident_time": (
            "✅ Lokasi tersimpan.\n\n"
            "*Apakah ini baru saja terjadi?* Balas *ya* atau *tidak*."
        ),
        "ask_incident_time_detail": (
            "🕒 Kira-kira kapan kejadiannya?\n\n"
            "Contoh: _jam 2 siang_, _kemarin malam_, _3 jam lalu_.\n"
            "Atau balas *lewati* jika tidak yakin."
        ),
        "report_submitted": (
            "✅ *Laporan terkirim, terima kasih!* 🙏\n\n"
            "Laporan Anda menunggu peninjauan tim sebelum dipublikasikan "
            "secara anonim.\n\n"
            "*Apa selanjutnya?*\n"
            "  *1.* 📝 Laporkan masalah lain\n"
            "  *2.* ℹ️  Pelajari lebih lanjut → https://mdg-bali.github.io/makingsensebali/\n"
            "  *3.* 💬 Beri masukan"
        ),
        "feedback_prompt": (
            "💬 Kami senang menerima masukan Anda.\n\n"
            "Tulis pesan Anda dan akan dibagikan secara anonim kepada tim "
            "Fab Lab Bali (tanpa menyimpan nomor telepon)."
        ),
        "feedback_thanks": (
            "🙏 Terima kasih atas masukan Anda!\n\n"
            "*Apa selanjutnya?*\n"
            "  *1.* 📝 Laporkan masalah lain\n"
            "  *2.* ℹ️  Pelajari lebih lanjut → https://mdg-bali.github.io/makingsensebali/\n"
            "  *3.* 💬 Beri masukan"
        ),
        "cancel_confirmed": (
            "🗑️ Laporan dibatalkan.\n\n"
            "Ketik */baru* untuk mulai laporan baru."
        ),
        "no_active_to_cancel": (
            "Tidak ada laporan aktif untuk dibatalkan.\n\n"
            "Ketik */baru* untuk mulai laporan."
        ),

        "wrong_step_category": (
            "⏳ Kita di *Langkah 1/3* — pilih jenis masalah.\n\n"
            "Balas dengan nomor (1–{max}), atau */batal* untuk membatalkan."
        ),
        "wrong_step_photo": (
            "⏳ Kita di *Langkah 2/3* — kirim satu foto 📸."
        ),
        "wrong_step_location": (
            "⏳ Kita di *Langkah 3/3* — bagikan lokasi 📍.\n\n"
            "📎 Lampiran → Lokasi → Kirim lokasi saat ini, tempel tautan "
            "Google Maps, atau ketik koordinat sebagai `lat, lon`."
        ),
        "wrong_step_confirm": (
            "⏳ Hampir selesai — balas *KIRIM* untuk mengirim, atau *BATAL* "
            "untuk membatalkan."
        ),

        "report_approved": (
            "✅ Laporan Anda telah disetujui dan dipublikasikan secara anonim.\n\n"
            "Terima kasih telah berkontribusi pada komunitas Bali. 🙏"
        ),
        "report_rejected": (
            "ℹ️ Laporan Anda telah ditinjau tetapi tidak dipublikasikan saat ini.\n\n"
            "Ini tidak memengaruhi kemampuan Anda mengirim laporan lain."
        ),
    },

    # -----------------------------------------------------------------
    # ESPAÑOL  (assistant-written — needs Tomas's review)
    # -----------------------------------------------------------------
    "es": {
        "language_picker": (
            "🌴 *Making Sense Bali*\n\n"
            "Choose your language / Pilih bahasa / Elige tu idioma:\n\n"
            "  *1.* English\n"
            "  *2.* Bahasa Indonesia\n"
            "  *3.* Español\n\n"
            "Responde 1, 2 o 3."
        ),

        "consent_prompt": (
            "🌴 *Making Sense Bali*\n\n"
            "🔒 *Tu privacidad es nuestra prioridad.*\n"
            "Tu número de teléfono *NUNCA SE GUARDA* en nuestros servidores. "
            "Los reportes se comparten sin identificar a quien los envía.\n\n"
            "Este bot lo gestiona Fab Lab Bali para que los vecinos puedan "
            "reportar problemas ambientales y comunitarios en tu zona — basura "
            "en las calles, fugas de agua, humo de quemas, polvo de obras, "
            "humo de vehículos y problemas similares.\n\n"
            "*Cómo reportar (3 pasos):*\n"
            "1️⃣ Elige el tipo de problema\n"
            "2️⃣ Envía una foto 📸\n"
            "3️⃣ Comparte tu ubicación 📍\n\n"
            "Para continuar, responde *ACEPTO*.\n\n"
            "Para salir en cualquier momento, responde */optout*."
        ),
        "consent_confirmed": "✅ ¡Gracias! Empecemos tu reporte.\n",
        "optout_confirmed": (
            "👋 Has salido. Tus reportes anónimos ya enviados se conservan. "
            "Envía cualquier mensaje para volver a unirte."
        ),

        "help_reply": (
            "🌴 *Cómo reportar*\n\n"
            "El bot te guía en 3 pasos:\n\n"
            "1️⃣ Elige el tipo de problema del menú\n"
            "2️⃣ Envía una foto 📸\n"
            "3️⃣ Comparte tu ubicación 📍\n\n"
            "Después puedes añadir un comentario breve (opcional) y responder "
            "*ENVIAR* para mandarlo o *CANCELAR* para descartarlo.\n\n"
            "Comandos:\n"
            "/baru   — nuevo reporte\n"
            "/about  — acerca de\n"
            "/batal  — cancelar el reporte actual\n"
            "/optout — salir"
        ),
        "about_reply": (
            "🌴 *Making Sense Bali*\n"
            "Fab Lab Bali · vigilancia ambiental comunitaria\n\n"
            "🔒 Los números de teléfono nunca se guardan."
        ),
        "unknown_command": "Comando desconocido. Escribe /help para ver la lista.",

        "audio_received": (
            "🎙️ Nota de voz recibida.\n\n"
            "La transcripción automática llegará pronto. Por ahora, escribe un "
            "comentario breve como texto, o continúa con los pasos."
        ),

        "category_menu": (
            "*Paso 1/3: Tipo de problema*\n\n"
            "¿Qué ves? Responde con un número:\n\n"
            "{menu}"
        ),
        "category_chosen": (
            "{cat_emoji} *{cat_label}* seleccionado.\n\n"
            "*Paso 2/3: Foto 📸*\n\n"
            "Envía una foto del problema (necesaria para el análisis automático)."
        ),
        "invalid_category": (
            "❓ Por favor responde con un número (1–{max}).\n\n"
            "O escribe */batal* para cancelar."
        ),
        "photo_received": (
            "📸 Foto recibida.\n\n"
            "*Paso 3/3: Ubicación 📍*\n\n"
            "Comparte dónde es, de cualquiera de estas formas:\n"
            "  📎 Adjuntar → Ubicación → Enviar ubicación actual\n"
            "  🔗 Pega un enlace de Google Maps\n"
            "  📝 O escribe las coordenadas como `lat, lon`"
        ),
        "photo_fetch_failed": (
            "⚠️ No se pudo descargar la foto desde WhatsApp.\n\n"
            "Por favor envía la foto una vez más."
        ),
        "ask_comment": (
            "*Opcional:* añade un comentario breve (por ejemplo, \"al lado de "
            "la calle Pantai\"), o responde *OMITIR* para continuar."
        ),
        "location_invalid": (
            "❓ No pude leer eso como una ubicación.\n\n"
            "Por favor envíala de una de estas formas:\n"
            "  📎 Adjuntar → Ubicación → Enviar ubicación actual\n"
            "  🔗 Pega un enlace de Google Maps\n"
            "  📝 O escribe las coordenadas como `lat, lon` "
            "(por ejemplo, `-8.8290, 115.0850`)"
        ),
        "location_link_unresolved": (
            "🔗 Eso parece un enlace de mapa acortado que no puedo abrir aquí.\n\n"
            "Por favor envía el pin de ubicación (📎 Adjuntar → Ubicación), "
            "o pega las coordenadas como `lat, lon`, o el enlace completo."
        ),
        "report_summary": (
            "📋 *Resumen del reporte*\n\n"
            "Tipo: {cat_emoji} {cat_label}\n"
            "Foto: ✅ guardada\n"
            "Ubicación: {lat:.5f}, {lon:.5f}\n"
            "{time_line}"
            "{comment_line}"
            "\n"
            "Responde *ENVIAR* para mandarlo al equipo de Fab Lab Bali.\n\n"
            "O *CANCELAR* para descartarlo."
        ),
        "summary_comment_line": "Comentario: _{comment}_\n",
        "summary_time_line": "Cuándo: {when}\n",
        "ask_incident_time": (
            "✅ Ubicación guardada.\n\n"
            "*¿Acaba de ocurrir ahora?* Responde *sí* o *no*."
        ),
        "ask_incident_time_detail": (
            "🕒 ¿Aproximadamente cuándo ocurrió?\n\n"
            "Por ejemplo: _2pm hoy_, _ayer por la tarde_, _hace 3 horas_.\n"
            "O responde *omitir* si no estás seguro."
        ),
        "report_submitted": (
            "✅ *¡Reporte enviado, gracias!* 🙏\n\n"
            "Tu reporte está pendiente de revisión por el equipo antes de "
            "publicarse de forma anónima.\n\n"
            "*¿Qué sigue?*\n"
            "  *1.* 📝 Reportar otro problema\n"
            "  *2.* ℹ️  Saber más → https://mdg-bali.github.io/makingsensebali/\n"
            "  *3.* 💬 Dejar un comentario"
        ),
        "feedback_prompt": (
            "💬 Nos encantaría conocer tu opinión.\n\n"
            "Escribe tu mensaje y se compartirá de forma anónima con el equipo "
            "de Fab Lab Bali (sin guardar tu número de teléfono)."
        ),
        "feedback_thanks": (
            "🙏 ¡Gracias por tu opinión!\n\n"
            "*¿Qué sigue?*\n"
            "  *1.* 📝 Reportar otro problema\n"
            "  *2.* ℹ️  Saber más → https://mdg-bali.github.io/makingsensebali/\n"
            "  *3.* 💬 Dejar un comentario"
        ),
        "cancel_confirmed": (
            "🗑️ Reporte cancelado.\n\n"
            "Escribe */baru* para empezar un nuevo reporte."
        ),
        "no_active_to_cancel": (
            "No hay ningún reporte activo que cancelar.\n\n"
            "Escribe */baru* para empezar un reporte."
        ),

        "wrong_step_category": (
            "⏳ Estamos en el *Paso 1/3* — elige el tipo de problema.\n\n"
            "Responde con un número (1–{max}), o */batal* para cancelar."
        ),
        "wrong_step_photo": (
            "⏳ Estamos en el *Paso 2/3* — envía una foto 📸."
        ),
        "wrong_step_location": (
            "⏳ Estamos en el *Paso 3/3* — comparte tu ubicación 📍.\n\n"
            "📎 Adjuntar → Ubicación → Enviar ubicación actual, pega un enlace "
            "de Google Maps, o escribe las coordenadas como `lat, lon`."
        ),
        "wrong_step_confirm": (
            "⏳ Casi listo — responde *ENVIAR* para mandarlo, o *CANCELAR* "
            "para descartarlo."
        ),

        "report_approved": (
            "✅ Tu reporte ha sido aprobado y publicado de forma anónima.\n\n"
            "Gracias por contribuir a la comunidad de Bali. 🙏"
        ),
        "report_rejected": (
            "ℹ️ Tu reporte fue revisado pero no se publicó en este momento.\n\n"
            "Esto no afecta tu posibilidad de enviar otros reportes."
        ),
    },
}


# =====================================================================
# Vision analysis follow-up & approval — templates (kept trilingual via t())
# =====================================================================
# These are sent by the M1 worker / admin flow. The worker formats them
# using t() with the report's stored lang (falling back to "en"/"id").

# Optional indicator/description lines for the analysis follow-up.
ANALYSIS_INDICATORS_LINE = "\nTerdeteksi / detected: {indicators}"
ANALYSIS_DESCRIPTION_LINE = "\n_{description}_"

ANALYSIS_FOLLOWUP_TEMPLATE = (
    "{cat_emoji} *Hasil analisis / Analysis*\n"
    "Kategori / category: *{category}*\n"
    "Tingkat / severity: {sev_emoji} {severity}"
    "{indicators_line}"
    "{description_line}"
)


# =====================================================================
# Lookup helper
# =====================================================================

DEFAULT_LANG = "en"


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: object) -> str:
    """Return MESSAGES[lang][key].format(**kwargs).

    Falls back to English if the language or the key is missing in the
    requested language. Unknown keys raise KeyError so typos surface in
    tests rather than silently sending nothing.
    """
    lang = lang if lang in MESSAGES else DEFAULT_LANG
    table = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    template = table.get(key)
    if template is None:
        template = MESSAGES[DEFAULT_LANG].get(key)
    if template is None:
        raise KeyError(f"unknown message key: {key!r}")
    if kwargs:
        return template.format(**kwargs)
    return template
