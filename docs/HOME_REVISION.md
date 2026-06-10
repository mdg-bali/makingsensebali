**English** · [Bahasa Indonesia](HOME_REVISION.id.md) · [Español](HOME_REVISION.es.md)

# Making Sense Bali · Home Page Revision Brief (v2)

**Status:** brief — not started.
**Owner of execution:** Claude Code.
**Owner of intent:** Tomas Diez (Making Sense Bali lead).
**Companion brief:** [`docs/PLATFORM_REVISION.md`](PLATFORM_REVISION.md) — the dashboard revision that just shipped. The home page revision builds on the analytical capability that dashboard now provides, but addresses a different audience and a different mode of engagement.
**Last updated:** 2026-05-30.

---

## 1. Why this revision

The current home page (`index.html`, 1234 lines) reads like an editorial essay — long-form, methodologically self-aware, well-crafted for someone willing to scroll and engage. That audience exists (researchers, fellow Fab City chapters, journalists) and the existing copy serves them well. **But it's not the primary audience the campaign needs to grow into.**

The campaign's real reach happens through three audiences who don't read editorial sites end-to-end:

- **Moms in Denpasar / Canggu / Ubud kos** asking "is the air bad today for my kid with asthma?"
- **Teachers** asking "can I show my class real local data about something they breathe every day?"
- **Government officials at Dinas Kesehatan and DLHK** asking "is there evidence here I can act on?"

For these audiences the current page is too dense, too unstructured, and — most importantly — **too low on calls to action**. They don't need a longer methodology section. They need to land on the page, immediately see something relevant to where they live, and have one obvious next step.

The revision delivers:

1. **A severity-first hero** that answers "is it bad right now where I am?" in under three seconds, in plain language, with traffic-light clarity.
2. **Four clear calls to action** that work for each audience: report, survey, get involved with sensors, share what's happening.
3. **Shareable cards** — auto-generated visuals about what's happening at a specific neighbourhood / time, designed to spread on WhatsApp and Instagram where the audience already lives.
4. **Audience-specific sections** — not a chooser ("are you a mom or a teacher?"), but cleanly structured sections that each audience can find what they need without scrolling through what they don't.

The dashboard revision turned the data into a tool. This revision turns the home page into a **distribution mechanism** for what the tool is finding. Without this, the campaign produces good data that no one outside the analyst loop sees.

## 2. Current state — what exists today

| Section | Lines | Notes |
|---|---|---|
| Hero ("Bali, made visible") | ~400–410 | Brand-forward. No location personalisation. No severity indicator. |
| Map section | ~410–440 | Lives on home; duplicates what the dashboard has more capably. Decide if it stays. |
| Reports feed | ~440–447 | Hidden by default (`display:none`) — comes from the dashboard work, not surfaced yet on home. |
| "The state of Bali's air" | ~451–479 | Editorial summary. Useful for context, currently too prose-heavy. |
| "The reading, translated" | ~479–548 | Interpretation help — already does some of the work moms need. Refactor to severity-first. |
| "Listen. Show. Act." | ~548–589 | Methodology framing. Important for officials, less so for moms. Reposition. |
| "Local lead, credited methodology" | ~589–620 | Lineage / governance. Important for credibility, especially with officials. |
| "Where we are" | ~620–638 | Network coverage. |
| "Concerns" + Survey | ~638–672 | Phase 1 survey link. **One of the four CTAs.** Currently buried at line 664. |
| "Eight questions" / Beyond survey | ~674–714 | Survey detail + contact. |
| "Need more detail?" | ~715+ | Dashboard link. |

Key existing wiring worth preserving:

- **CSS variables** for the brand palette (saffron + teal + cream paper) are at the top of the file and used consistently. Keep them.
- **`<script src="data.js">`** is loaded — the home page already has access to live sensor + reports state, just isn't surfacing it visually beyond the map.
- **Bilingual translation layer** from the dashboard revision should be ported to the home page from day one. Don't ship an English-only home that the dashboard could already serve in Bahasa Indonesia.
- **Survey link** is already wired through `#surveyLink` → external Airtable form.

The page is functional and brand-coherent. This revision is **not a rewrite from scratch** — it's a restructure with a few new components and a sharper hierarchy.

## 3. Target state — what to build

### 3.1 Severity-first hero

Replace the current hero block with one that, on page load, attempts to detect the visitor's neighbourhood (geolocation API, with a graceful fallback to a "pick your neighbourhood" dropdown) and shows:

- **One headline number** — today's worst PM2.5 reading in the visitor's locality, with a colour-coded severity band (green / yellow / orange / red, matching the WHO daily-exposure guidelines)
- **One plain-language line** in the visitor's selected language — examples:
  - GREEN: *"Air is clean today in Denpasar. Outdoor play is fine."*
  - YELLOW: *"Air is moderate today in Canggu. Sensitive groups (kids, asthma, elderly) should limit prolonged outdoor activity."*
  - ORANGE: *"Air is unhealthy in Ubud today. Masks recommended outdoors, especially for kids."*
  - RED: *"Air is dangerous today in Sanglah. Stay indoors, windows closed, mask outside."*
- **A small context line** — "PM2.5 peaked at 47 µg/m³ at 14:32 · WHO daily guideline: 5 µg/m³"
- **Two primary buttons** in the hero: "Report what you see →" (WhatsApp deeplink) and "What's happening near me →" (scroll/jump to the localised section below)

If geolocation is denied or no sensor exists near the visitor, default to a Bali-wide aggregate ("Air across Bali today: moderate · worst reading: Ubud") and a prominent "Pick your area" dropdown.

The hero must work on mobile-first (375px wide); this is where most visitors will see it.

### 3.2 The four calls to action

Surface all four CTAs above the fold OR within a single screen of scrolling — not buried at line 664 like the survey currently is. Each CTA is a card with one clear verb and one short description. Suggested wording (subject to brand voice review):

1. **"Report what you're seeing →"**
   *Smell smoke? See burning waste? Notice a smell that wasn't there yesterday? Send one WhatsApp message to our bot, our local team verifies, and it joins the public map.*
   Action: WhatsApp deeplink to the bot's number (already in `reports/config.json`).

2. **"Tell us what matters →"**
   *The Phase 1 survey asks residents what environmental issues affect daily life. Eight questions, 5 minutes, shapes where we put sensors next.*
   Action: opens the existing Airtable survey form in a new tab.

3. **"Get involved with sensors →"**
   *We run sensor-building workshops at Fab Lab Bali — assemble a low-cost air quality node in an afternoon, deploy it on your roof or in your classroom. Sign up to hear about the next workshop.*
   Action: opens a signup form (Airtable or similar — coordinate with reports component team). Future: this becomes a kit purchase page; design the card so it can swap to that without rewrite.

4. **"Share what's happening →"**
   *Generate a shareable card about today's air in your neighbourhood and post it where the conversation already lives — WhatsApp, Instagram, Telegram. Each share helps more people see the data.*
   Action: opens the shareable cards section (3.4 below).

The CTAs should feel like equal-weight options, not a hero CTA with three afterthoughts. Card-style layout, four in a row on desktop, two-by-two or stacked on mobile.

### 3.3 Audience-specific sections (the three reads)

Below the hero + CTAs, three substantive sections — each clearly headed so the visitor knows which one is for them, but all visible (not behind tabs or a chooser):

**For families and residents** — "Today in your neighbourhood"
- The severity widget from the hero, expanded with the last-24h chart for PM2.5 (link to the dashboard for deeper view)
- Nearby reports as a short feed (3–5 most recent within ~2km)
- Plain-language guidance: when to keep windows closed, when to use masks for kids, what humidity levels mean for asthma
- Mold-risk indicator if the neighbourhood's humidity has been >60% for >24h sustained
- The "Report what you see" CTA repeated at the end of this section

**For teachers and schools** — "Bring the data into your classroom"
- "A lesson plan using local Bali air quality data" — short pitch + downloadable PDF (write a minimal v1 lesson plan if none exists; doesn't need to be elaborate, just real)
- Workshop framing — "Making Sense Bali for schools" — even if it's aspirational, name what's being offered
- One concrete example: "Your students compare your school's PM2.5 to WHO's guideline, then to a school in Barcelona via Smart Citizen's global network"
- The "Get involved with sensors" CTA repeated at the end of this section

**For policymakers and analysts** — "Evidence you can act on"
- The campaign's data-policy / lineage (much of the current "Local lead, credited methodology" section moves here)
- Aggregate downloads — CSV of last 30 days, monthly summary PDF (can be auto-generated nightly via existing `generate_summary.py` infrastructure in `reports/`)
- "How to cite Making Sense Bali data in policy" — short paragraph with the suggested citation format and contact email
- Link to the dashboard for live analysis
- Contact line for direct engagement with the campaign team

Each section should have a clear visual anchor (icon, colour accent) so the visitor can scan-and-skip if they're not the audience.

### 3.4 Shareable cards — the growth mechanism

This is the most novel piece of the revision and probably worth its own week.

**Concept:** generate auto-designed visual cards summarising what's happening in a Bali locality, in a format optimised for sharing on WhatsApp groups, Instagram stories, and Telegram channels — where the campaign's target audiences already spend time.

**Card templates (start with these four):**

1. **"Today in [neighbourhood]"** — current PM2.5 + severity band + one-line interpretation + WHO guideline reference + Making Sense Bali logo + URL
2. **"This week in [neighbourhood]"** — 7-day PM2.5 trend chart (sparkline) + peak count + most common report category + URL
3. **"Mold risk: [neighbourhood]"** — RH trend + days above 60% RH + plain-language risk note + URL
4. **"Burning corridor: [neighbourhood]"** — combined PM spike + report count + map snippet showing source area + URL

Each card has:
- The campaign's visual signature (palette + typography from the existing CSS variables)
- A timestamp ("as of 14:32 WITA, 2026-05-30")
- The Making Sense Bali wordmark + the short URL
- A QR code (small, corner) linking to the dashboard's relevant view

**Rendering options:**

Option A (recommended for v1): client-side HTML canvas rendering. Cards built as styled HTML, converted to PNG via `html2canvas` or similar, downloaded via the "Download card" button. Plus a "Share to WhatsApp" button using the WhatsApp share URL scheme that opens the user's WhatsApp with the text pre-filled and a link back to the site.

Option B (Phase 2): Cloudflare Worker that renders an SVG → PNG on demand at a URL like `/share/today/canggu.png`. This lets the og:image meta tag on the site point at a fresh-rendered card, so when anyone shares the site URL anywhere, the link preview is a current, localised card. Higher-impact but more infrastructure.

**Required acceptance:** a visitor in Canggu can click "Share what's happening" in the hero, see four card options, pick "Today in Canggu", and either download it or share to WhatsApp in two taps. The card looks distinctive enough that someone seeing it in a WhatsApp group recognises it as Making Sense Bali (not a generic air quality screenshot).

### 3.5 Correlations made visible on the home page

The dashboard now shows correlation between sensor peaks and citizen reports. The home page should surface a **single most-striking recent correlation** as a narrative panel, refreshed daily. Example copy:

> **"The data and the residents told the same story yesterday."**
>
> At 14:30 in Canggu, the air quality sensor on Jl. Pantai Berawa recorded a sharp PM2.5 spike — from 12 to 78 µg/m³ in twenty minutes, well past the WHO unhealthy threshold. Twelve minutes later, a resident two streets away reported smoke from a construction site burning waste materials. The two signals confirm each other. Fab Lab Bali notified the Banjar of Berawa for follow-up.
>
> [See the data →](/dashboard/) [Read the report →](/dashboard/#report-id) [Report what you're seeing →](whatsapp://...)

Pick the most recent meaningful correlation each day (highest peak with a matching report, or most-visited locality). The narrative panel makes the campaign's value tangible in a way that abstract charts never will — for the official audience especially, this is the artifact that gets cited in conversations.

For v1, this narrative can be **human-curated** (Fab Lab Bali operator picks the daily story from the dashboard's correlation engine). Auto-generation is Phase 2.

## 4. Suggested phasing

**Phase 1 — Severity-first hero + four CTAs.** ~4 days.
- Geolocation + locality detection (with manual fallback)
- Severity widget with band-based interpretation
- Four CTA cards above the fold
- Mobile-first layout

**Phase 2 — Audience sections restructure.** ~3 days.
- Refactor existing sections into the three audience-specific blocks
- Add the missing pieces (lesson plan placeholder, citation guidance, mold-risk widget)
- Don't lose any existing methodology content — relocate it

**Phase 3 — Shareable cards (client-side rendering).** ~1 week.
- Four card templates as styled HTML
- `html2canvas` PNG download
- WhatsApp share URL integration
- "Share what's happening" section as the host UI

**Phase 4 — Daily correlation narrative.** ~3 days.
- Manual curation flow first (operator-edited JSON file like `data/daily_story.json`)
- Auto-render on home from the JSON
- Phase 2: auto-pick from the dashboard's correlation output

**Phase 5 — Polish + Bahasa + og:image.** ~4 days.
- Bilingual strings (lean on the dashboard's `t()` infrastructure)
- og:image generation (Cloudflare Worker, Option B from §3.4)
- Mobile QA, accessibility pass
- Performance: home page still loads <3s on 3G

Total: ~3.5 weeks. Phases 1 and 2 deliver the biggest perceived improvement and can ship before phases 3–5 land.

## 5. Acceptance criteria

The revision is done when:

- [ ] A visitor lands on the home page on mobile and within one second knows whether the air is OK in their neighbourhood (assuming geolocation permission or a sensible default)
- [ ] All four CTAs are visible above the fold or within one scroll on a 375px-wide phone
- [ ] A teacher can find a downloadable lesson plan from the home page in under 30 seconds
- [ ] A policymaker can find the data-citation guidance and the CSV download in under 30 seconds
- [ ] A visitor can generate and download a shareable card for their neighbourhood in under three taps
- [ ] A visitor sharing the site URL on WhatsApp sees a locality-relevant link preview card (Phase 5 og:image work)
- [ ] The daily correlation narrative is visible above the fold on the home page
- [ ] The home page works in both English and Bahasa Indonesia using the same translation infrastructure the dashboard now uses
- [ ] No regression in load time (currently fast; don't bloat with image libraries — `html2canvas` is the only new heavy dep)

## 6. Non-goals

- **No audience-chooser modal or tab system** ("Are you a mom, teacher, or official?"). It's gimmicky. Structure the page so each audience finds their section by scanning, not by self-identifying upfront.
- **No e-commerce.** "Get involved with sensors" is currently a workshop signup, not a kit purchase. Design the CTA so it can swap to a purchase flow later without page rewrite, but don't build the purchase flow yet.
- **No removal of the editorial methodology content.** Move it, condense it, but don't lose it — it's what gives the campaign credibility with the official audience especially. The "Local lead, credited methodology" section becomes part of the policymaker block.
- **No replacement of the dashboard's analytical depth on the home page.** The home shows summaries and the most-striking correlation; the dashboard remains the place for serious analysis. Don't try to make the home page a second dashboard.
- **No new framework.** Same constraint as the dashboard brief — vanilla JS, static site, no React/Vue/etc.
- **No login or per-user state on the home page.** The home is public-read, fully cacheable, no per-visitor data beyond the locality cookie/localStorage for "remember my neighbourhood".

## 7. Dependencies and unknowns

- **Geolocation permission flow.** Most visitors will deny it on first ask. Have a sensible fallback ("Bali-wide aggregate · pick your area below") and a clear, non-nagging request UX.
- **Locality boundaries.** The dashboard uses a `BALI_LOCALITIES` list (in `reports/murmurations_adapter.py`) — reuse for the home page's locality dropdown. If a new locality needs adding, do it in one place and import everywhere.
- **Workshop signup destination.** Decide before starting Phase 1: Airtable form, Tally, simple Formspree, or a custom endpoint? Recommendation: Airtable to match the survey infrastructure.
- **Lesson plan content.** v1 can ship with a one-page PDF that just shows "compare your school's last 24h PM2.5 reading to the WHO daily guideline and to a reference school in Barcelona via Smart Citizen's global network." Doesn't need to be elaborate; needs to exist. Educator partner can refine later.
- **Daily correlation curation.** Until the dashboard's correlation engine auto-picks the daily story, decide who at Fab Lab Bali manually picks and writes it each day, and where the JSON lives. Suggest `data/daily_story.json` updated via the same admin path as the reports.
- **WhatsApp share URL format on iOS Safari** — sometimes flaky. Test on actual devices, fall back to the `navigator.share()` API where available.

## 8. How to start

1. Spin up a working branch: `git checkout -b home-v2`
2. Read [`index.html`](../index.html) end-to-end. Identify what stays, what moves, what's new. Take notes — the file is 1234 lines and the restructure is the bulk of the work, not the new components.
3. Read this brief plus [`PLATFORM_REVISION.md`](PLATFORM_REVISION.md) so the home page revision lands consistent with the dashboard work that just shipped.
4. Start with Phase 1 (hero + CTAs). Ship that before touching audience sections; instant visible improvement, low risk of regression.
5. PR to `main`. GitHub Pages picks up changes automatically.

## 9. When this is done

Update this brief with a "Status: complete" header and a one-paragraph summary of what landed. Note any deviations from the brief (a card template that didn't work, a phase that needed re-scoping, an assumption that proved wrong). The campaign's `REPLICATION.md` will reference this as the home-page version other Fab City chapters fork — accuracy matters.

If the shareable-cards mechanism turns out to actually drive engagement (which we'll know from referral analytics within a month of launch), the Fab Lab Barcelona team should be told — this could become a pattern they want to bring back to the original Smart Citizen platform.

## 10. Contact

- Campaign lead: Tomas Diez · `tomas@fab.city`
- Reports component owner: Fab Lab Bali team · `fablabbali@gmail.com`
- Fab Lab Barcelona (Smart Citizen platform team): `info@smartcitizen.me`
