**English** · [Bahasa Indonesia](phase-1-survey.id.md) · [Español](phase-1-survey.es.md)

# Phase 1 — Matters of concern survey

The design, methodology, and operational guide for the Phase 1 community survey of a Making Sense [place] campaign. Documents the live Bali survey as the reference design, with proposed enhancements for the next iteration.

> **Live form**: [airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form)
> **Base**: `appwQPP3ywSp4uu25` · Table: `Matters of Concern`

---

## Why a Phase 1 survey

Making Sense [place] doesn't start by deploying sensors or by writing a press release about air quality. It starts by asking residents what environmental issues *they* notice in their daily life. This grounding matters more than it might seem.

The methodological lineage is **[Making Sense](https://making-sense.eu/)** (EU Horizon 2020, 2015–2017), which adapted Bruno Latour's "matters of concern" framing into a participatory citizen-sensing protocol. The core distinction is between *matters of fact* (what science measures — PM2.5, dB, ppm) and *matters of concern* (what people actually worry about — the smoke that wakes them up, the water that tastes wrong, the noise that makes their kids cry).

A sensing campaign that starts with matters of fact builds an instrument. A sensing campaign that starts with matters of concern builds a community. The first is a tool. The second has political legitimacy and the standing to actually change anything.

Phase 1 produces three things:

1. **A picture of resident-defined attention** — what concerns surface, where, who they affect, what evidence already exists
2. **Authentic priorities for Phase 2** — which neighborhoods to sense first, which categories the report bot should foreground, which partner orgs to invite
3. **A constituency** — a list of residents who participated and want to be involved further (host a sensor, send reports, translate, attend workshops)

Skip Phase 1 and you've inverted the order: you're telling residents what they should care about based on what's easy to measure. That's a research project, not a community campaign.

---

## Design principle: one row = one concern

The Bali survey is structured so that **one form submission represents one concern**, not one respondent. A resident with three environmental concerns submits the form three times — once per concern. Each row in the Airtable captures the full narrative for that specific concern: what it is, where, who it affects, what evidence exists, what would change if it were made visible.

This is a deliberate choice with three benefits:

- **Richer per-concern detail** than would fit in a multi-select grid
- **Analysis by concern is natural** — group by category, by location, by "most affected" without unpacking nested data
- **Respondents who care about one issue can submit quickly**; those with several aren't forced into one constrained answer

The cost is that respondents who submit multiple concerns enter their identifying info (name, email, etc.) multiple times. The optional contact section keeps this short, and most respondents are anonymous anyway.

---

## The current Bali survey

### Fields, in form order

| # | Field | Type | Required | Purpose |
|---|---|---|---|---|
| 1 | **Concern** | Single line text | Yes | One-line summary — what's the issue? Becomes the row's primary identifier. |
| 2 | **Categories** | Multi-select | Yes | Which environmental category or categories this falls under |
| 3 | **Description** | Long text | Optional | The narrative — what specifically have you observed, when, what does it look/sound/smell like, in your own words |
| 4 | **Location** | Long text | Optional | Where it happens — neighborhood, road, beach, school, time of day if relevant |
| 5 | **Most affected** | Multi-select | Optional | Who is most affected by this issue |
| 6 | **Existing evidence** | Long text | Optional | What evidence already exists — own observations, reports from others, news, official data |
| 7 | **What would change** | Long text | Optional | Theory of change — what would change if data made this visible, and who should the data go to |
| 8 | **Willing to participate** | Multi-select | Optional | How the respondent wants to be involved further (sensor host, reporter, workshops, translation, outreach, just informed, decline) |
| 9 | **Preferred languages** | Multi-select | Optional | Which languages the campaign should support |
| 10 | **Name** | Single line text | Optional | Leave blank to stay anonymous |
| 11 | **Email** | Email | Optional | Only if contacted about next steps |
| 12 | **Phone / WhatsApp** | Phone | Optional | Only used if respondent asks for follow-up |
| 13 | **Affiliation** | Single line text | Optional | School, NGO, fab lab, neighborhood association, organization |

Internal-only fields (not in the form, filled in by the team after submission):

- **Status** — review state: New → Reviewed → Contacted → Workshop invited → Closed / archived (or Spam / invalid)
- **Submitted at** — auto from form
- **Internal notes** — triage notes, follow-up actions, contact assignment

### Select options as deployed (Bali)

**Categories** — Burning waste · Air quality · Water · Noise · Heat & humidity · Plastic & solid waste · Soil & agriculture · Light pollution · Other

**Most affected** — Me personally · My family · Children / students · Elderly / vulnerable people · Workers · Neighbors / community · Animals / wildlife · Visitors / tourists · Other

**Willing to participate** — Host a sensor · Share reports via the bot · Attend workshops · Translate / localize · Connect us to my school / org · Just keep me informed · Prefer not to participate further

**Preferred languages** — Bahasa Indonesia · English · Bahasa Bali · Other

**Status (internal)** — New · Reviewed · Contacted · Workshop invited · Closed / archived · Spam / invalid

---

## Rationale — why these fields, in this order

The form is ordered to lower abandonment: the easy / most important questions come first, the optional / personal questions come last. A resident who only fills the first three fields (Concern, Categories, Description) still gives the campaign useful data.

- **Concern first** — a one-line summary forces respondents to articulate what they're reporting before they get into details. Acts as both data and self-clarification.
- **Categories second** — structured taxonomy for downstream analysis. The "Other" option keeps it open.
- **Description, Location, Most affected** — the *what / where / who* triangle. All optional individually so partial responses are still useful.
- **Existing evidence** — a respect signal. The question assumes residents already know things; the campaign isn't starting from zero. This often produces the richest text, with people naming sources, dates, and prior reports.
- **What would change** — the theory-of-change prompt. Notably *no structured intervention catalog* — this is intentional. Residents tell us in their own words what they think would help and to whom data should go. Structured options would prime them toward our existing assumptions.
- **Willing to participate** — the Phase 2 on-ramp. Granular enough to match different commitment levels.
- **Preferred languages** — informs both the bot's translation priorities and outreach channel decisions.
- **Contact fields last** — optional, never required, never reasonable to require for a "what concerns you" survey.

### What's intentionally not asked

- **Demographics (age, gender)** — Bali pilot trialed these in an earlier draft, dropped them after low completion impact. May add back as optional once response volume warrants stratification.
- **Specific PM2.5 / dB tolerances** — that's matters of fact, not matters of concern. Belongs in Phase 2 instrumentation, not Phase 1 survey.
- **Multiple choice "what would help"** — would prime answers. Free text instead.

---

## Field additions — what's in the live base now

Seven new fields were added to the live Bali base on 2026-05-12. They exist in the table but **have NOT yet been added to the form view** — that's a manual step in Airtable's form editor, deliberately separated so the team can review the field order and any reword before exposing them to respondents.

New fields:

| Field | Type | Purpose |
|---|---|---|
| **Neighborhood** | Single-select | Structured locality picker covering Bukit (Uluwatu, Pecatu, Ungasan, Bingin, Balangan, Padang Padang, Jimbaran, Nusa Dua, Kutuh, Benoa) plus rest of Bali. Replaces unstructured Location for analysis; Location stays as free-text complement. |
| **How long have you lived here** | Single-select | <1yr / 1–5yr / 5–10yr / >10yr / visitor / prefer not to say. Distinguishes recent-newcomer perception from long-term residence. |
| **How did you hear about us** | Multi-select | Friend, school, banjar, Instagram, WhatsApp, Facebook, partner org, press, poster, found directly, other. Outreach channel feedback. |
| **How often does this happen** | Single-select | Daily / weekly / monthly / seasonal / one-off / not sure. Frequency lens. |
| **When is it worst** | Multi-select | Early morning through night, plus weekend/weekday/all-day. Critical for Phase 2 sensor placement decisions. |
| **What you've tried** | Long text | What residents have personally done — talked to neighbors, reported, joined a group, changed routine, bought equipment. Surfaces community wisdom that `Existing evidence` was conflating with documentation. |
| **Outcome of what you tried** | Single-select | It helped / partly / didn't / too soon / haven't tried / not applicable. Structured complement to the free-text. |

**Next step (manual)**: open the Airtable form view in the base editor and drag these into the form in this recommended order:

- After `Location`: insert `Neighborhood` (so respondents get the structured picker right where they already think about place)
- After `Categories`: insert `How often does this happen` and `When is it worst`
- After `Existing evidence`: insert `What you've tried` and `Outcome of what you tried`
- Near the bottom, after `Affiliation`: insert `How long have you lived here` and `How did you hear about us`

All seven should be **optional** in the form view — none required. The form's only required fields stay Concern and Categories.

### Things deliberately NOT added

- Demographic fields (age, gender, household income) — increases friction without analytical value at pilot scale.
- "Severity 1–10" sliders for the concern — quantifying subjective severity adds noise, not signal. Resident narrative is more useful.
- Map pin via third-party widget — possible via Softr / Stacker integration, deferred until response volume warrants the integration overhead.

---

## Replication — schema for forking the survey

For another Fab City chapter forking the Bali survey for their own bioregion, here's the Airtable schema you'll replicate. The base ID is per-deployment; the structure is shared.

### Base: `Making Sense [Your Place] · Matters of Concern`

### Table: `Matters of Concern` — one row per submitted concern

Replicate the field list above. The structural fields (Concern, Categories, Description, Location, Most affected, Existing evidence, What would change, Willing to participate, Preferred languages, Name, Email, Phone, Affiliation, Status, Submitted at, Internal notes) port directly.

What you customize for your bioregion:

- **Categories** — adapt the list to your context. Bali's includes "Heat & humidity" (relevant in the tropics) and "Soil & agriculture" (rice paddies, plantations). Barcelona might drop those and add "Heritage / built environment" or "Heatwaves" (different urgency). Yucatán might add "Cenote contamination." Keep "Other" always.
- **Most affected** — adapt the demographic categories. "Visitors / tourists" matters in Bali because tourism is a major economic and environmental force; less applicable in non-tourist cities. "Workers" should usually stay (informal workers, market sellers).
- **Willing to participate** — keep the structure. Adapt wording to local conventions ("Connect us to my banjar" → "Connect us to my junta vecinal" etc.).
- **Preferred languages** — your local language(s) instead of Bahasa Indonesia + Bahasa Bali. English is conventional as a secondary option.

### Replicating the live form

Airtable's built-in form view is the simplest path:

1. Create the base + table with the schema above
2. Create a Form view, drag the fields in the order shown in the form-order table
3. Mark Concern and Categories as required; everything else optional
4. Set the form's submit confirmation message in the host Fab Lab's voice
5. Embed on your campaign site, or share the form URL directly in outreach

### Per-neighborhood prefill (optional)

For neighborhood-specific outreach, append a query parameter to the form URL to pre-fill the Location or Neighborhood field:

```
[your-form-url]?prefill_Neighborhood=Eixample
[your-form-url]?prefill_Neighborhood=Gràcia
```

Send the prefilled URL to neighborhood-specific outreach channels (banjar WhatsApp groups, school parent lists, etc.) — fewer fields to fill, better completion rates.

---

## Outreach playbook

Survey design doesn't matter if no one fills it in. Phase 1 outreach is the load-bearing work of the campaign.

### Channel mix

A working outreach mix for a bioregion of 50,000–500,000 people:

| Channel | Reach | Effort | Conversion |
|---|---|---|---|
| Host Fab Lab's existing channels | medium | low | high |
| Partner schools (parent groups, faculty) | high | medium | high |
| Neighborhood councils / banjars / juntas | medium | medium-high | very high |
| WhatsApp community groups (existing local ones) | high | medium | medium |
| Instagram / local social media | high | low | low |
| Posters in shops, markets, community boards | medium | medium | low (but legitimacy-building) |
| Local press / radio | high | high | low (but legitimacy-building) |
| Direct in-person outreach (markets, events) | low | high | very high |

The high-conversion channels are the slow ones that build trust. The high-reach channels are weak on conversion. A campaign that only does social media will get noisy responses from a narrow demographic; one that only does in-person will get rich responses from a small number of people. Mix both, and weight toward what your host Fab Lab is good at.

### Timeline

A workable Phase 1 outreach calendar:

- **Week –2**: design survey, translate, set up Airtable, create poster + social assets
- **Week –1**: brief partners, draft outreach messages, set up internal tracking
- **Week 1**: soft launch through Fab Lab + closest partners. Goal: ~30 responses to test the form
- **Week 2**: revise form if needed based on early feedback (typos, broken logic, low completion sections), then **full launch**
- **Weeks 2–6**: active outreach through all channels, weekly partner sync, share early findings publicly to show the survey is being read
- **Week 6**: soft close — campaign ramps down active outreach but keeps form open
- **Week 8**: hard close — final response count, begin analysis

Total: 8 weeks of active collection, plus 2 weeks of setup before and 2–4 weeks of analysis + publication after.

### Translation

Phase 1 survey copy must be reviewed by **native speakers from your bioregion** before going public. The questions you wrote in English will lose nuance, gain accidental implications, and miss locally specific framings when translated. Budget 1–2 weeks for the translation review cycle, not 1 day.

For Bali: Bahasa Indonesia primary, English secondary. Bahasa Bali is offered as a language preference but the form itself is currently Bahasa + English — adding a Balinese form version is a future enhancement.

For Barcelona: Catalan primary, Spanish secondary, English optional. Be aware that survey copy that "feels OK" in Spanish may read as exclusionary in Catalan-first neighborhoods (Gràcia, parts of Eixample) — and vice versa.

### Incentives

Three working approaches:

1. **No incentive, framed as civic contribution.** Works in dense communities with active civic culture. Honest about what the campaign asks.
2. **Optional thank-you in the form** — a digital download (an air quality dashboard PDF, a guide to environmental issues in the city) sent automatically on submission. Low cost, signals reciprocity.
3. **Physical thank-you at events** — at the markets, schools, or partner sites where you're collecting in person, a small bottle, sticker, or branded item.

Avoid paying for responses. It changes the demographic mix toward people who needed the money rather than people who cared about the issues, and it sets up the wrong relationship for Phase 2.

### Outreach copy template

The single most-used outreach asset will be a short paragraph you adapt for each channel. Template:

> 🌴 *Making Sense [Place]* — Fab Lab [City]'s campaign on environmental issues in our neighborhoods.
>
> We're asking residents what environmental issues affect their daily life — air, water, noise, waste, anything. This is *Phase 1*: building a picture of what neighbors actually notice, before we deploy any sensors. Your input shapes where we focus next.
>
> 🔒 Anonymous unless you choose to follow up. ~5 minutes per concern.
>
> 📝 [link to survey]
>
> *Run by Fab Lab [City] · Part of [Fab City [City]] · Made by neighbors, for neighbors.*

Translate, adapt, post.

---

## Analysis and publication

Phase 1 is incomplete without closing the loop. Residents who participated need to see the campaign reading their input. Not doing this — collecting and disappearing — is the most common failure mode of community surveys.

### What to analyze

Three layers:

1. **The catalog of concerns** — count of concerns per category, visualized as a horizontal bar chart on the public summary page. Because the survey is one-row-per-concern, this is a direct sum rather than a multi-select unpacking.
2. **The geography** — which locations (extracted from Location free-text, or from Neighborhood once added) recur. Simple heatmap or annotated list. Cross-reference with Categories for category × location patterns.
3. **The narrative** — selected quotes from Description, Existing evidence, and What would change. Edited for length and clarity, anonymized to "*Resident, [neighborhood], [tenure]*" style attribution. The most powerful artifact for press, policy, and community conversations.

Optional further analysis once you have 100+ concerns:

- Cross-tabs (Categories × Most affected — does "Burning waste" most often affect children, animals, or elderly?)
- Action gaps (once `What you've tried` field is added — what residents tried vs what worked, surfacing where collective action is needed)
- Theory-of-change clusters (qualitative coding of the `What would change` free-text — does the community want enforcement, organizing, information, or infrastructure?)

### What to publish

The Phase 1 results page on your campaign site should include:

- Number of concerns submitted, number of unique respondents (if known), dates of collection
- The catalog of concerns visualization
- The geographic pattern
- 5–10 selected resident quotes
- A clear statement of what Phase 2 will do in response

The last point is critical. "We heard X is the top concern in [neighborhood], so Phase 2 will deploy sensors there, will prioritize Z categories in the reports bot, will work with [partner] on [action]." That's the loop closing.

### Sharing back with respondents

A short email to respondents who opted into follow-up, summarizing findings and inviting them to Phase 2. Make this email genuinely interesting — not corporate-template — and from a named person at the host Fab Lab.

---

## Iteration — what we'll learn in Bali

The Bali Phase 1 survey is in its earliest phase as of 2026-05-12 — the form is live, the schema has been expanded with the new fields above, and active outreach is about to begin. This section will fill in as real responses arrive.

What we're watching for, based on prior citizen-sensing literature and the Making Sense project:

- **Length and quality of free-text responses.** The hypothesis is that `What would change` and `Existing evidence` will get the longest, most thoughtful answers — residents have theories of change and they have local knowledge; the survey is one of the few places that asks. If completion is high on these fields, the design is working.
- **Opt-in rate for Phase 2.** What percentage tick at least one option in `Willing to participate`? Naive expectation from typical civic-tech projects is 15–30%; if higher, the campaign framing is unusually resonant; if lower, something in the messaging is failing.
- **Category mix.** Which Categories accumulate fastest? In Bali we expect Burning waste, Plastic & solid waste, and Air quality to lead. Surprises here directly shape Phase 2 sensor priorities.
- **Anonymous vs identified submissions.** What share skip the contact fields entirely? This signals the level of trust in the form and the host institution.
- **Geographic distribution.** Once `Neighborhood` is added to the form, which bbox locations report which categories? Patterns here drive sensor placement and outreach focus.

This list will be replaced with concrete lessons as the campaign matures. PRs to this document with observations from other Fab Labs welcomed.

---

## Forking for your city — concrete steps

1. **Read this document in full.** Then look at the [live Bali form](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form) to see how the design feels as a respondent.
2. **Create a new Airtable base** in your workspace. Replicate the `Matters of Concern` table schema (15 fields including the 3 internal-only ones) per the table above.
3. **Adapt the select options** to your bioregion. Categories, Most affected, Willing to participate (wording for local councils), Preferred languages.
4. **Translate the field descriptions and form copy** to your local language(s). Native-speaker review before public launch.
5. **Adapt the form's submit message** to feel local. ("Terima kasih!" in Bali → "Gràcies!" in Barcelona → etc.)
6. **Design your outreach mix** — channels, partners, timeline. Sanity-check with the host Fab Lab and named campaign lead before launching.
7. **Soft-launch** with ~10–30 responses from trusted neighbors. Fix issues with the form before going wide.
8. **Full launch** through your channel mix. Active period 6–8 weeks.
9. **Analyze and publish** within 4 weeks of close. Make Phase 2 commitments clear.

The point of Phase 1 is to ground Phase 2. Don't rush past it, and don't let it become a permanent state — the survey is a tool, not an end.

---

## License

This document and the question design: **CC-BY-SA 4.0**. Fork it, adapt it for your bioregion, share back what you learn.

---

Part of [Making Sense Bali](../README.md). For the full campaign context see the [parent README](../README.md). For replication see [REPLICATION.md](../REPLICATION.md).
