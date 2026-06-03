# Sense Making

**The reports component of [Making Sense Bali](../README.md) — a WhatsApp-based citizen reporting toolkit for Fab City nodes and bioregional campaigns.**

> This folder is one component of the Making Sense Bali campaign. For
> the full campaign context — methodology, sensors, web presence, survey —
> see the [parent repo's README](../README.md). What follows is the
> technical reference for the reports component specifically.

Sense Making is the reporting component of a citizen-sensing campaign.
Residents describe local environmental and urban issues — trash, water leaks,
construction debris, vehicle pollution, burning waste, noise — through a
familiar interface (WhatsApp), in their own language. A local operator
reviews each report before publication. Approved reports become public on the
campaign's site and, when federated nodes exist, become discoverable across
bioregions via the Murmurations protocol.

The toolkit is deliberately small, sovereign, and replicable. It runs on
home-grade infrastructure (a NAS and a laptop), uses no SaaS in the critical
path, has no per-message API costs, and can be forked by another Fab Lab in
an afternoon. The reporting interface is bilingual by default and configured
per locality.

This work descends from the [Making Sense](https://making-sense.eu/) project
(EU Horizon 2020, Fab Lab Barcelona / IAAC and partners, 2015–2017) — the
canonical participatory framework for citizen environmental sensing. Sense
Making takes Making Sense's methodology and packages it as a distributed,
home-deployable kit for the 2026 Fab City landscape.

---

## Status

| | |
|---|---|
| **Reference deployment** | Making Sense Bali · Bali, Indonesia · pilot phase, Q2 2026 |
| **Run by** | [Fab Lab Bali](https://fablabbali.com) as the reporting layer of [Making Sense Bali](https://mdg-bali.github.io/makingsensebali/) |
| **Replication kit** | Available — see [REPLICATION.md](REPLICATION.md) |
| **Planned next** | Pelapor Barcelona · Fab Lab Barcelona · 2026 H2 |
| **Federation layer** | PLANETAI · planned, infrastructure not yet built |

---

## What residents experience

A WhatsApp conversation. The bot leads with a privacy commitment, then
explains the three-step flow:

```
Resident → halo

Bot     ← 🌴 Making Sense Bali
          🔒 Privacy is our top priority.
          Your phone number is NEVER STORED on our servers.

          This bot is run by Fab Lab Bali so residents can report
          environmental and community issues in your area — trash on
          streets, water leaks, smoke from burning, construction
          dust, vehicle pollution.

          How to report (3 steps):
          1️⃣ Write a description of the issue
          2️⃣ Share your location 📍
          3️⃣ Send a photo (optional)

          Reply AGREE to continue.
          Reply /optout anytime to leave.

Resident → SETUJU
Bot     ← ✅ Thanks! You can now report issues.

Resident → sampah berserakan di pantai bingin
Bot     ← 📝 Description received.
          Step 2/3: Share your location 📍

Resident → [shares location pin]
Bot     ← ✅ Location saved — your report is complete.
          Step 3/3 (optional): Send a photo 📸
```

All bot copy is bilingual (local language + English italics underneath). Per-node
language is configured by editing a single file (`messages.py`); per-node
locality (neighborhoods, bounding box) is configured in `config.json` and the
adapter's locality table.

---

## What operators see

A web dashboard on the local network with seven tabs:

- **Status** — system health (bot, WhatsApp pairing, vision queue), today's report count
- **Pending review** — incoming reports awaiting approval, with one-click approve/reject
- **Allowlist** — manage who can interact with the bot (phone numbers in E.164)
- **WhatsApp** — pairing workflow, QR scan, connection state, no SSH required
- **Reports** — full report list with category, severity, locality, timestamp
- **Map** — geographic view of approved reports (Leaflet, auto-centers on the bioregion)
- **Consent** — anonymized consent ledger, revoke any sender

The dashboard is a single Flask file with inline templates, Pico.css for
styling, Leaflet for the map, basic auth from an env variable. No build step.
Anyone who reads Python can customize the look or behavior.

---

## How it works

```
                      WhatsApp
                          │
                          ▼
┌─────────────────────────────────────────────┐    M1 / inference host
│ Always-on host (Synology NAS / VPS)         │    ┌──────────────────────┐
│ ┌─────────────────────────────────────────┐ │    │ MLX vision server    │
│ │ Evolution API · WhatsApp transport      │ │    │  Phi-3.5-Vision      │
│ ├─────────────────────────────────────────┤ │    │                      │
│ │ Sense Making bot · webhook → save       │─┼───▶│ Worker · pulls queue │
│ │   allowlist · consent · vision queue    │ │    │   updates report     │
│ ├─────────────────────────────────────────┤ │    └──────────────────────┘
│ │ Operator dashboard · approval UI        │ │
│ ├─────────────────────────────────────────┤ │    public:
│ │ Postgres + Redis (Evolution backing)    │ │    ┌──────────────────────┐
│ └─────────────────────────────────────────┘ │    │ campaign GitHub Pages│
│   reports/    canonical (with PII)          │    │  (approved only,     │
│   profiles/   approved + sanitized          │───▶│   sanitized)         │
└─────────────────────────────────────────────┘    └──────────────────────┘
                                                   future: PLANETAI federation
```

Five Docker containers run on the always-on host. Vision inference lives on
a separate Apple Silicon machine so the always-on host never needs a GPU —
the bot queues a vision job, the worker on the Mac picks it up when online.
If the Mac is asleep, photos pile up in the queue and process when it wakes.
The bot never blocks on inference.

Why this shape: sovereignty matters. The whole stack runs on infrastructure
a household owns. No proprietary APIs in the path, no monthly SaaS bills, no
vendor that can deplatform the campaign. For a Fab City node that's not
incidental — it's the point.

For architecture detail, see [ARCHITECTURE.md](ARCHITECTURE.md).
For deployment, see [DEPLOY.md](DEPLOY.md).

---

## Privacy

Three commitments, enforced by the code:

1. **Phone numbers are never stored** in reports or public profiles.
   The bot stores only a one-way SHA-256 hash for consent tracking.
2. **Reports are sanitized before federation.** The Murmurations adapter
   strips all PII (sender hashes, local image paths, media keys) from the
   profiles published to public sites.
3. **Nothing leaves the local infrastructure without explicit operator
   approval.** The approval gate in the dashboard is the publication
   boundary. Unreviewed reports stay on the NAS and are never federated.

The consent flow is opt-in by reply (`SETUJU` / `AGREE`), opt-out is one
command (`/optout`), and the operator can revoke any individual sender's
consent through the dashboard.

---

## Replicate it

If you run a Fab City node, a Fab Lab, or a community sensing campaign and
you want your own deployment, read **[REPLICATION.md](REPLICATION.md)**.

You will need:

- An always-on host with Docker (recommended: Synology DS725+ NAS, ~$300, but
  any Linux box with Docker works)
- A spare Apple Silicon Mac for vision inference (or substitute Claude Haiku
  vision API for ~$5/month)
- A WhatsApp number to dedicate to the bot (a personal number works for
  pilot phase, a dedicated business number is recommended for production)
- 4–6 hours of one operator's time to bring it up end-to-end
- Comfort with a terminal for initial setup; day-to-day operation is in the
  dashboard

Recurring cost on home infrastructure: **~$10–20/month** (electricity,
domain renewal, optional vision-API fallback).

---

## Lineage

| | |
|---|---|
| 2015–2017 | [Making Sense](https://making-sense.eu/) — EU Horizon 2020 citizen-sensing framework, led by Fab Lab Barcelona / IAAC and partners |
| 2013–now | [Smart Citizen Kit](https://smartcitizen.me/) — open-hardware environmental sensor platform from Fab Lab Barcelona |
| 2025–now | Making Sense Bali — campaign by Fab Lab Bali, the host campaign for the first Sense Making deployment |
| 2026–now | Sense Making — reporting kit factored out for bioregional replication |

---

## Repository structure

```
.
├── bot_murmurations.py       Flask bot — WhatsApp webhook, allowlist, consent
├── dashboard.py              Flask dashboard — approval UI, ops controls
├── murmurations_adapter.py   Federated profile generator (PII-sanitized)
├── vision_analyzer.py        Vision client (MLX / Ollama / Haiku / mock)
├── mlx_vision_server.py      MLX FastAPI server (runs on the Mac)
├── m1_vision_worker.py       Vision queue consumer
├── messages.py               All bilingual bot copy — translate for replication
├── docker-compose.yml        Five-container stack for the always-on host
├── Dockerfile                Shared image for bot + dashboard
├── schemas/
│   └── environmental_observation-v1.0.0.json   Murmurations schema
├── sync_profiles.sh          Push approved profiles to public sites
├── DEPLOY.md                 Detailed deployment steps
├── REPLICATION.md            Forking guide for new bioregions
├── ARCHITECTURE.md           Design decisions
└── OPERATIONS.md             Day-to-day operator playbook
```

---

## License

Code: MIT.
Documentation, schemas, messages: CC-BY-SA 4.0.

Both mirror the Making Sense and Smart Citizen approach — open enough to fork
freely, share-alike on what's distributed publicly.

---

Built by [Fab Lab Bali](https://fablabbali.com), for the
[Fab City](https://fab.city/) network.
