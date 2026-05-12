# Smart Citizen Bali

**A community-led environmental sensing campaign for Bali, anchored by Fab Lab Bali, within the Fab City Bali chapter.**

Smart Citizen Bali combines open-hardware environmental sensors, public data from regional and global networks, and resident reports of locally observed environmental issues — burning waste, air quality events, water leaks, construction debris, noise, the matters of concern raised by people who actually live here. The work is done in Indonesia, by people in Indonesia, on concerns identified by people in Indonesia.

The campaign is hosted and accountable to **[Fab Lab Bali](https://fablabbali.com)**, the local fabrication laboratory in Denpasar, as part of the **Fab City Bali** chapter of the global [Fab City](https://fab.city/) network. Methodologically the work descends from the **[Making Sense](https://making-sense.eu/)** project (EU Horizon 2020, Fab Lab Barcelona / IAAC and partners, 2015–2017) and uses the **[Smart Citizen Kit](https://smartcitizen.me/)** platform, co-founded by Tomas Diez and Alex Posada at Fab Lab Barcelona / IAAC in 2012. Smart Citizen Bali is led by Tomas Diez — Smart Citizen co-founder, now resident in Bali — and runs as an independent bioregional instance, in close relationship with the original projects.

Live: **[mdg-bali.github.io/smartcitizenbali](https://mdg-bali.github.io/smartcitizenbali/)**

---

## What Smart Citizen Bali looks like

Three surfaces, one campaign:

1. **The public site** at `mdg-bali.github.io/smartcitizenbali/` — the campaign's home: methodology, status, the live dashboard, the matters-of-concern survey, the residents' reports, attribution to the broader network.

2. **The live dashboard** at `/dashboard/` — real-time environmental sensor readings aggregated from multiple open networks: Smart Citizen Kit deployments operated by the campaign, OpenAQ stations in Bali, Sensor.Community devices, PurpleAir (when configured). PM2.5, PM10, temperature, humidity, noise. Each pin shows source, last reading, links to the original platform.

3. **The reports layer** — residents send environmental observations to a WhatsApp bot ("Pelapor Bukit" in the Bali deployment). Each report is reviewed by the local operator before publication. Approved reports appear on the public site as community-sourced data alongside the sensor readings. Phone numbers are never stored.

---

## The methodology

Smart Citizen Bali follows a phased Making Sense-derived approach, adapted for Bali:

**Phase 1 — Matters of concern.** A survey, currently hosted on Airtable, asks residents what environmental issues affect their daily life. The output isn't a ranked list of "problems to solve" — it's a map of attention. Where do people notice burning waste? Where is the noise unbearable? Where does the water taste bad? The survey establishes that the campaign is responding to community-defined concerns, not imposing an external agenda.

**Phase 2 — Sensing and reporting.** Two channels run in parallel. Open-hardware sensors (Smart Citizen Kits) are deployed at strategic locations — currently a campaign-operated house node and office node, with capacity to expand to schools and community sites. In parallel, the reports bot collects qualitative resident observations: photos, locations, descriptions of issues that sensors can't see. The combined dataset is published openly.

**Phase 3 — Response and learning.** This is the phase the network is building toward. Aggregated data and report patterns inform local action — from individual awareness (your home is in a smoke corridor) to community organizing (this trash burning is a recurring event with a known source) to policy advocacy (the regional government has data it can act on). Federated cross-bioregion learning is the longer-term horizon.

---

## Components

Smart Citizen Bali is assembled from these parts. Each has its own scope and its own deployment story:

| Component | What it does | Where it lives |
|---|---|---|
| **Campaign site** | Public landing page, methodology, sensor dashboard, reports, attribution | This repo · GitHub Pages |
| **Sensor data layer** | Aggregates Smart Citizen Kit + OpenAQ + Sensor.Community via Cloudflare Workers | This repo · [`data.js`](data.js), [`worker/`](worker/) |
| **Smart Citizen Kits** | Open-hardware air quality + noise + climate sensors deployed in Bali | [smartcitizen.me](https://smartcitizen.me/) — house node 19236, office node 19600 |
| **Matters-of-concern survey** | Phase 1 community input on environmental concerns | Airtable (proprietary backend, public-facing form) |
| **Reports component** | WhatsApp bot + operator dashboard for citizen reports | [`reports/`](reports/) — Sense Making toolkit |
| **Murmurations identity** | Federated org profile, discoverable across community-data networks | [`murmurations.json`](murmurations.json) in this repo |

---

## Lineage and governance

Smart Citizen Bali sits within a specific lineage. It matters because it shapes who is accountable, what assumptions the campaign carries, and which network it federates with.

- **2012–present** — Smart Citizen, co-founded by **Tomas Diez** and **Alex Posada** at Fab Lab Barcelona / IAAC. The open-hardware sensor platform that this campaign uses.
- **2015–2017** — Making Sense (EU Horizon 2020), Fab Lab Barcelona / IAAC and partners (Waag, JKU Linz, University of Dundee). The participatory framework we apply.
- **2026–present** — Smart Citizen Bali. Led by Tomas Diez (Smart Citizen co-founder, now resident in Bali), with Fab Lab Bali as institutional host and Fab City Bali as the chapter context.

The original Smart Citizen platform and Fab Lab Barcelona are stewarded by other teams today; Smart Citizen Bali is independent but coordinated, not a satellite or franchise. Both projects continue, in different bioregions, under different teams, with overlapping methodology and a shared aesthetic of open hardware, open data, and community accountability.

Smart Citizen Bali's accountability structure:

- **Host institution**: Fab Lab Bali
- **Chapter context**: Fab City Bali
- **Network membership**: [Fab City](https://fab.city/) global network · [Fab Lab Network](https://fablabs.io/)
- **Contact**: (mailto:fablabbali@gmail.com)

---

## Status

The campaign is currently in early Phase 1 → Phase 2 transition (Q2 2026):

- Phase 1 survey is live and collecting responses
- Sensor dashboard is operational with the campaign's two SCK nodes and live aggregation from OpenAQ, Sensor.Community
- Reports component (Sense Making) is in pilot — bot running on Fab Lab Bali's infrastructure, allowlist-restricted to early testers, approval gate in place
- Public reports stream into the campaign site after operator review

---

## Replicate it — Smart Citizen [your city]

Smart Citizen Bali is intentionally replicable. Other Fab City chapters with a host Fab Lab can fork this campaign template for their bioregion.

**You will need:**

- A **Fab City chapter** for your city or bioregion ([fab.city/network](https://fab.city/))
- A **host Fab Lab** willing to be the institutional anchor and accountable party
- **Some sensor presence** — at minimum one Smart Citizen Kit, plus the option to surface existing OpenAQ / Sensor.Community / PurpleAir data already in your region
- **Modest tech capacity** — someone who can run a NAS, a Cloudflare Worker, and deploy the reports bot (no software development required, but operational comfort)
- **Local language adaptation** — translating the campaign site and reports bot copy

The full replication guide is in **[REPLICATION.md](REPLICATION.md)**.

Currently in conversation: **Smart Citizen Barcelona** (Fab Lab Barcelona, 2026 H2). Other Fab City chapters being approached include Yucatán, Montreal, Goa, and Santiago. Each Smart Citizen [city] is its own campaign, hosted by its own Fab Lab, anchored in its own bioregion, sharing methodology and federating discoverable data — that's the network the project is building toward, one chapter at a time.

---

## Repository structure

Everything lives in one repo so a Fab Lab forking Smart Citizen [their city]
gets the whole stack with a single `git clone`.

```
.
├── README.md              this file — campaign overview
├── REPLICATION.md         how to stand up Smart Citizen [your city]
├── docs/
│   ├── methodology.md     Making Sense, adapted for bioregional deployment
│   ├── phase-1-survey.md  running the matters-of-concern survey
│   ├── sensors.md         deploying SCK + integrating OpenAQ / Sensor.Community
│   ├── reports.md         operating the reports component
│   ├── web-presence.md    customizing the campaign site
│   └── federation.md      Murmurations identity, future PLANETAI
│
├── index.html             campaign home page
├── data.js                sensor data aggregator (SCK + OpenAQ + Sensor.Community)
├── dashboard/             live sensor dashboard
│   └── index.html
├── worker/                Cloudflare Worker proxies (OpenAQ, SCK)
│   └── openaq-proxy.js
├── murmurations.json      federated organization profile
│
└── reports/               Sense Making · the reports component
    ├── README.md          toolkit overview
    ├── bot_murmurations.py
    ├── dashboard.py
    ├── docker-compose.yml
    └── ...                see reports/README.md for the full layout
```

---

## License

Code: MIT.
Documentation, methodology, schemas, surveys: CC-BY-SA 4.0.

The same license pattern as Making Sense and Smart Citizen Kit. Fork it,
adapt it for your bioregion, share what you build back — that's the point.

---

Hosted by [Fab Lab Bali](https://fablabbali.com) · Part of [Fab City Bali](https://fab.city/) · A member of the [Fab City](https://fab.city/) network and the [Fab Lab Network](https://fablabs.io/).
