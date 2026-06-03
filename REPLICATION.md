# Replicating Making Sense [your place]

A guide for **Fab City chapters with a host Fab Lab** who want to stand up their own bioregional instance of Making Sense — combining open-hardware sensors, public data networks, citizen reports, and a participatory survey under a single campaign.

The reference deployment is [Making Sense Bali](README.md), hosted by Fab Lab Bali within the Fab City Bali chapter. This document is the same campaign packaged as a kit. If you run a Fab City chapter and have a host Fab Lab willing to anchor the work, you can fork this repository, customize it for your bioregion, and deploy a working instance in roughly **3–6 months from decision to public launch**.

If you don't have the Fab City + Fab Lab combination — or don't want to — most of the underlying tools are useful on their own: the [Smart Citizen Kit](https://smartcitizen.me/) for sensors, OpenAQ / Sensor.Community for open data, the [Sense Making reports toolkit](reports/) for bot infrastructure. You can use any of those without operating a "Making Sense [place]" campaign. The campaign name and the federated network it joins are reserved for Fab City chapter instances, for reasons of accountability and governance set out below.

---

## 1. Is this for you?

Making Sense [your place] requires four commitments. If any of these is shaky, fix it before starting the technical work — the technical work is the easy half.

### Required institutional anchors

- **A Fab City chapter** for your bioregion. The chapter is the political and network home of the campaign. If your city is not yet a Fab City chapter, that's a separate conversation to have with [Fab City](https://fab.city/) first.
- **A host Fab Lab** willing to be the institutional anchor. The Fab Lab is named, accountable, and visible on the campaign — it's the legal, ethical, and operational home. Not an informal community group or a personal project.
- **A named campaign lead.** One person who owns the work, makes decisions, and is publicly contactable. Not a committee, not a rotating role. The named lead is what makes the campaign legible to media, government, and partners.

### Required operational capacity

- **A small technical team or operator** — not full-time, but someone with the comfort to operate a Synology NAS (or equivalent Linux box with Docker), customize a static website, deploy a few Smart Citizen Kits, manage an Airtable. No software development required for setup; comfort with following technical documentation is required.
- **Community engagement capacity** — someone (often the same person, sometimes a partner organization) who can run the Phase 1 survey, talk to residents, manage the report stream, and decide what gets approved and published. This is the human work that gives the data its meaning.
- **A few months of attention.** This isn't a weekend project. Phase 1 takes ~6 weeks of design and outreach to do well. Standing up the technical infrastructure is a week or two. Running the campaign is ongoing.

### What it isn't

- A turnkey product. You will make local decisions throughout — what neighborhoods to focus on, what language to operate in, what survey questions matter for your bioregion, what categories of pollution dominate your context.
- A research project. The data is for community use first, research downstream. If your primary goal is academic publication, this kit is overengineered for your needs.
- An advocacy campaign. Making Sense [your place] is participatory and evidence-building. It can feed advocacy, but the campaign itself is descriptive — it surfaces what residents notice, it doesn't pre-decide what the answer is.
- A short pilot. The federation network only works if instances stay alive across years. A Fab Lab signing on should expect to host the campaign for the long term.

---

## 2. The phases

Making Sense [your place] runs in three overlapping phases. They aren't strictly sequential — Phase 2 starts while Phase 1 is still gathering responses; Phase 3 begins as soon as you have enough data to act on — but the order of starting matters.

### Phase 1 — Matters of concern (weeks 1–8)

The campaign starts by asking residents what environmental issues affect their daily life. Not what we think they should care about — what they actually notice. This is the participatory grounding. Skip it and you've built an instrument campaign, not a community one.

**What you produce in Phase 1:**

- A survey hosted on Airtable (or equivalent) capturing matters of concern, locations, frequency, severity
- 50–500 responses from your bioregion, depending on city size and outreach
- A public summary on your campaign site: "Here's what residents told us they're concerned about"
- A short list of priorities that shape Phase 2's sensor placement and report bot copy

**Decisions in Phase 1:**

- Survey language(s) — local language always; English optional depending on audience
- Outreach channels — schools, neighborhood organizations (banjars, juntas vecinales, AC), social media, posters, partner orgs
- Survey duration — 3–8 weeks of active collection is typical
- What "done" looks like — a response threshold, a time window, or both

You can fork Making Sense Bali's survey questions as a starting point (see [docs/phase-1-survey.md](docs/phase-1-survey.md), and the **[live Bali survey form](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form)** for reference). The Bali survey is itself a work in progress, iterating as we learn what questions get useful answers. Fork the questions you find useful, adapt or replace the rest — your bioregion's matters of concern are not Bali's.

### Phase 2 — Sensing and reporting (weeks 4–ongoing)

While Phase 1 responses come in, you start the sensing and reporting layer. Two channels:

**Quantitative — Smart Citizen Kits.** Deploy your campaign-operated SCK nodes at strategic locations. Start with two or three (a campaign-operated home node, an office node, a partner-hosted node), expand based on Phase 1 priorities. Each unit costs ~$150, runs on WiFi, publishes openly to [smartcitizen.me](https://smartcitizen.me/). The campaign site's dashboard auto-discovers and renders your kits.

**Qualitative — citizen reports.** Stand up the [reports component](reports/) — a WhatsApp bot that residents can message about what they're seeing. Trash dumps, water leaks, smoke, construction debris, vehicle exhaust. Each report is reviewed by your operator before publication. Approved reports appear on your campaign site alongside the sensor data.

The two channels feed the same map. A burning event shows up as a sensor reading (PM2.5 spike) AND a resident report ("smoke at the south end of the beach since this morning"). Together they're stronger than either alone.

**Decisions in Phase 2:**

- Where to place SCKs (Phase 1 priorities should drive this)
- How many sensors to start with (3–5 is reasonable; can grow to 20+ over time)
- Whether to integrate OpenAQ / Sensor.Community / PurpleAir data — the site already does this for your bbox
- Bot operator schedule — who reviews reports daily, who responds to broken messages
- Pilot tester list — start with 5–10 trusted residents before opening up

### Phase 3 — Response and learning (ongoing, starts as data accumulates)

This is the phase the network is building toward and where Making Sense [your place] earns its keep. Data alone doesn't change anything; data interpreted by a community, with a named anchor, sometimes does.

What "response" looks like depends on your local context. Common patterns:

- **Awareness loops** — recurring reports back to residents who participated, so they know their input is being used
- **Pattern surfacing** — monthly summaries identifying recurring events ("trash burning every Wednesday at the south beach") that point at sources
- **Community organizing** — local action triggered by aggregated evidence (talking to the businesses doing the burning, organizing collective cleanups)
- **Policy advocacy** — taking the aggregated data to local government, banjars / neighborhood councils, environmental agencies
- **Federated learning** — when other Making Sense [place] instances exist, sharing patterns across bioregions (smoke corridor dynamics, monsoon-related water issues, etc.)

Phase 3 is the most local-context-dependent. We don't prescribe how to run it. We do require that you commit to running it — otherwise the campaign becomes data collection without consequence, which is corrosive to community trust.

---

## 3. Components — what to fork, what to deploy, what to configure

Making Sense [your place] is assembled from these parts:

| Component | What you do | Effort |
|---|---|---|
| **Campaign site** (`index.html`, CSS, copy) | Fork, customize text + locality + visual accents for your city | 1–2 days of careful editing |
| **Sensor data layer** (`data.js`) | Update bounding box for your bioregion, register your own SCK device IDs | 1–2 hours |
| **Smart Citizen Kits** | Buy, register at smartcitizen.me, deploy in your bioregion | Procurement ~2 weeks + 1 hour per deployment |
| **DIY workshop nodes** (optional) | Build low-cost XIAO ESP32-S3 + HM3301 + BME680 nodes for higher sensor density | Half-day workshop per cohort + parts ordering — see [`hardware/diy-node/`](hardware/diy-node/) |
| **Cloudflare Worker proxies** (`worker/`) | Optional — only if OpenAQ rate-limits hit you | 1–2 hours if needed |
| **Phase 1 survey** | Design questions for your context, host on Airtable (or alt) | 1 week of careful question design + ongoing data collection |
| **Reports component** (`reports/`) | Fork, configure locale + language + allowlist, deploy on NAS | 1 day of config + several hours of NAS deployment |
| **Murmurations identity** (`murmurations.json`) | Edit org name, partners, geolocation, tags; publish at your domain | 1 hour |

Total realistic effort to go from "we want to do this" to "we're publicly live with sensors + reports + a survey": **6–10 weeks** with one operator working part-time, or 3–4 weeks if you have a dedicated team for a sprint.

---

## 4. Fork the campaign — step by step

These are the high-level steps. Each step links to detailed docs where they exist.

### Step 1 — Establish institutional anchors

Before any code or hardware:

- Confirm your Fab City chapter status. If you're not yet a chapter, talk to [Fab City](https://fab.city/) first.
- Identify and confirm your host Fab Lab. Get explicit institutional commitment, not just enthusiasm.
- Name your campaign lead. Get this in writing somewhere internal.
- Decide your campaign name. Convention: **Making Sense [Place]** — *Making Sense Barcelona*, *Making Sense Yucatán*, *Making Sense Bangalore*. Keep the "Making Sense" prefix so the network is recognizable. One caution: this is the contemporary campaign **network**, distinct from the 2015–2017 EU **Making Sense** research project it descends from. Always credit that project *with its dates* in your lineage so the two don't blur — especially in Barcelona, where Fab Lab Barcelona ran the original EU pilot.

### Step 2 — Fork this repository

```bash
git clone https://github.com/mdg-bali/makingsensebali your-org/makingsense-yourplace
cd makingsense-yourplace

# Update the remote to your own GitHub org
git remote set-url origin git@github.com:your-org/makingsense-yourplace.git
git push -u origin main
```

GitHub Pages: enable on your fork. The site goes live at `your-org.github.io/makingsense-yourplace/`.

### Step 3 — Customize the campaign site

Edit `index.html` and `dashboard/index.html`:

- Replace "Bali" / "Bukit" with your city / bioregion throughout the copy
- Update hero text, methodology framing, hosted-by attribution
- Update color palette if you want — the current saffron + teal is Bali-inflected; Barcelona might prefer different
- Update bounding box and map center in `data.js` (`BALI_BOUNDS`, `BALI_CENTER`)
- Update `murmurations.json` with your org name, location, partners, tags

Detailed customization guide: [docs/web-presence.md](docs/web-presence.md).

### Step 4 — Deploy Smart Citizen Kits

- Buy 2–5 SCK units from [smartcitizen.me](https://smartcitizen.me/store) (~$150 each)
- Register them at smartcitizen.me, get your device IDs
- Deploy them — campaign office, host Fab Lab, partner location, your home
- Update `data.js` `KNOWN_BALI_SCK_IDS` → `KNOWN_[YOURCITY]_SCK_IDS` with your device IDs

Detailed guide: [docs/sensors.md](docs/sensors.md).

**Cheaper alternative — DIY workshop nodes.** For 5× spatial density per dollar relative to the SCK, the [`hardware/diy-node/`](hardware/diy-node/) folder documents two tiers: a ~$15–25 Basic (XIAO ESP32-S3 + BME680, indoor air quality + climate + VOC, no PM) and a ~$35–60 Plus (Basic + Grove HM3301, adds PM1/2.5/10). Lower fidelity than the SCK, half-day build in your host Fab Lab, accessible to non-technical participants. DIY nodes are not a replacement for the SCK — they're spatial-density nodes referenced against SCK calibration. See `hardware/diy-node/README.md` for the full tier strategy.

### Step 5 — Design and launch the Phase 1 survey

- Fork the Bali survey questions in [docs/phase-1-survey.md](docs/phase-1-survey.md)
- Adapt for your context — replace Bali-specific examples with your bioregion's relevant issues
- Translate to local language(s)
- Set up an Airtable base for responses (free tier covers ~1000 responses)
- Embed the survey on your campaign site or link out
- Begin outreach: schools, neighborhood councils, social media, partner orgs

### Step 6 — Stand up the reports component

This is the technical heavy lift. Read [`reports/README.md`](reports/README.md) and [`reports/DEPLOY.md`](reports/DEPLOY.md) end-to-end before starting.

You'll need:

- An always-on host with Docker — Synology DS725+ (~$300 + drives) is the reference; any Linux box with Docker works
- A spare Apple Silicon Mac for vision inference (or substitute Claude Haiku for ~$5/month)
- A WhatsApp number — dedicated SIM / business number recommended for production (personal works for the pilot phase)

Configuration changes from the Bali defaults:

- `reports/config.json` — `node_id`, `bioregion`, `primary_url`, allowlist for your testers
- `reports/messages.py` — translate all user-facing strings to your local language(s)
- `reports/murmurations_adapter.py` — update `BUKIT_BBOX` / `BALI_LOCALITIES` to your bioregion's bounding box and neighborhood names

### Step 7 — Publish your Murmurations profile

Edit `murmurations.json` for your campaign:

- `name`, `nickname`, `primary_url` — your campaign
- `tags` — your local context
- `description`, `mission` — your local framing
- `urls` — your campaign URLs
- `locality`, `region`, `country_iso_3166`, `geolocation` — your bioregion
- `contact_details` — your Fab Lab
- `relationships` — keep the schema-org relationships to fab.city, fablabs.io, making-sense.eu, smartcitizen.me; add any local partners

Then submit the profile URL to the [Murmurations Index](https://murmurations.network/) so your campaign is discoverable.

### Step 8 — Launch Phase 1 publicly

Tell people the campaign exists. Outreach through:

- The host Fab Lab's existing channels
- The Fab City chapter's network
- Local schools and community organizations
- Social media (whichever platforms your residents actually use)
- Press, if you have a media contact

Phase 1 is the most front-loaded engagement phase. Plan for it.

### Step 9 — Begin Phase 2 in parallel

Once SCKs are deployed and the reports bot is live with a small allowlist, start collecting data in parallel with the Phase 1 survey. The combined map (sensors + approved reports) on your campaign site becomes the public artifact.

---

## 5. Localization — what changes for your bioregion

The codebase is intentionally configurable, but several decisions are textual and require human judgment, not just code edits.

### Language

The reports bot's user-facing text is in [`reports/messages.py`](reports/messages.py). All strings are bilingual (local language first, English in italic underneath). For your deployment:

- Pick your primary local language (Catalan + Spanish for Barcelona, Yucatec Maya + Spanish for Yucatán, Kannada + English for Bangalore)
- Pick a secondary language (English is convention; could be different if your context warrants)
- Have a **native speaker review every string** before going public. Trust is built in the first reply.

The campaign site (`index.html`) has its own text, mostly English in the Bali reference deployment. For non-English-first audiences, translate it.

### Locality bounding box and neighborhoods

In `reports/murmurations_adapter.py`:

- `BUKIT_BBOX` → your city/bioregion bounding box (lat/lon min/max)
- `BALI_LOCALITIES` → list of neighborhood names that should be recognized in report descriptions

The bot uses these to auto-categorize where a report is set. Barcelona's localities are Eixample, Gràcia, Raval, Sant Antoni, Poblenou, Sants, Sarrià, Horta — and many more.

### Bioregion designation

In `reports/config.json` set `bioregion` to one of the Murmurations bioregion enum values (the schema in `reports/schemas/environmental_observation-v1.0.0.json` lists them). Barcelona's bioregion is `mediterranean_basin`. If your bioregion isn't in the enum, propose an extension via the schema.

### Visual identity

The current site palette (saffron + teal + cream paper) evokes Bali — sun, water, tropical paper. For your deployment you can keep it (signals network membership) or shift to local accents. CSS variables are defined at the top of `index.html` for easy palette swaps.

### Categories

The schema's `pollution_category` enum covers most environmental concerns: burning, trash, vehicle, construction, dust, industrial, chemical, water, noise, deforestation. If your bioregion has a category that doesn't fit (e.g., specific to your industry, climate, or geography), propose adding it to the schema rather than overloading existing categories.

### Governance and attribution

Three references your fork should update consistently:

- "Hosted by Fab Lab Bali" → hosted by your Fab Lab
- "Part of Fab City Bali" → part of your Fab City chapter
- Tomas Diez as named lead → your named lead

Keep references to Making Sense, Smart Citizen Kit, Fab Lab Barcelona / IAAC in the lineage — those are the shared upstream that all Making Sense [place] instances share.

---

## 6. Federation — joining the network

Each Making Sense [place] instance is independent but discoverable. Federation happens through two mechanisms today and one in the future:

### Today — Murmurations

Once you publish your `murmurations.json` and submit it to the [Murmurations Index](https://murmurations.network/), your campaign is discoverable in the broader Murmurations ecosystem. Any community-data network can query for `tags=citizen sensing` or `tags=fab lab` and find your instance alongside Making Sense Bali, Making Sense Barcelona, and others.

This is the lightest form of federation: your campaign is *findable* but each instance operates independently. No data sharing across nodes, no shared infrastructure.

### Today — bidirectional links

Each Making Sense [place] site links to the others through the Fab City and Fab Lab networks. The lineage section in each campaign's README acknowledges the shared methodology and platform. The network becomes visible through citation, not through technical integration.

### Future — PLANETAI federation

PLANETAI is the longer-term horizon: a federation layer that aggregates approved reports across Making Sense [place] instances, lets you query patterns across bioregions, and provides shared infrastructure (profile hosting, cross-instance discovery, optional AI services). PLANETAI infrastructure is not yet built — when it is, joining the federation is opt-in and configured in `reports/config.json`.

For now, design and operate your instance as if it will federate. The Murmurations schema is shared, the report shape is shared, the methodology is shared. When PLANETAI exists, the technical work to federate will be a config change, not a refactor.

---

## 7. Where to get help

- **Repository**: [github.com/mdg-bali/makingsensebali](https://github.com/mdg-bali/makingsensebali) — file issues, propose pull requests
- **Replication conversations**: [fablabbali@gmail.com](mailto:fablabbali@gmail.com) — the Fab Lab Bali inbox. Reach out before starting; a short call early saves weeks of guesswork.
- **Fab City network**: [fab.city](https://fab.city/) — for chapter status, partner introductions
- **Smart Citizen platform**: [smartcitizen.me](https://smartcitizen.me/) — hardware, account setup, sensor questions

If you're seriously considering replication, please reach out before starting. A short call early saves weeks of guesswork — and lets us coordinate launch timing, share materials, and connect you with adjacent chapters.

---

## 8. License and attribution

All code in this repository: **MIT**.
Documentation, schemas, surveys, and methodology: **CC-BY-SA 4.0**.

If you fork and run a Making Sense [place], we ask three things:

1. **Credit the lineage.** Making Sense (Fab Lab Barcelona / IAAC, 2015–2017), Smart Citizen (co-founded by Tomas Diez and Alex Posada, 2012), Making Sense Bali (Fab Lab Bali, 2026) in your README and on your campaign site.
2. **Keep the network legible.** Use the "Making Sense [place]" naming convention. Publish your Murmurations profile. Link to other instances.
3. **Share back.** Improvements to the code, the methodology, the docs — pull requests welcome. The kit gets better when each new instance contributes back what they learned.

---

Built by [Fab Lab Bali](https://fablabbali.com), for the [Fab City](https://fab.city/) network.
For Barcelona, Yucatán, Montreal, Goa, Santiago, and the other bioregional instances yet to come.
