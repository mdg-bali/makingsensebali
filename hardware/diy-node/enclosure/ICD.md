# Interface Control Document — Making Sense Bali DIY-Node Enclosure

**Version:** SPEC-1.0-DRAFT (becomes 1.0-FROZEN on Tomas's sign-off + coupon numbers)
**Date:** 2026-06-08
**Rule:** No enclosure CAD is modeled against this spec until it is FROZEN. Any later change is a versioned spec change (1.1, 1.2…), recorded in the change log at the bottom — not a vibe.

---

## 1. Mission

Wall-mounted outdoor enclosure for a workshop-built air-quality node. Bali climate: hot (to ~35°C ambient, hotter under roofs), ~80%+ RH, monsoon rain, insects. Deployed under eaves. Two variants from one design. The printed object must read as a product someone is proud to hang on their house — not a programmer's geometry exercise.

## 2. Components (verified dimensions)

| Component | Dimensions (mm) | Source | Notes |
|---|---|---|---|
| Seeed XIAO ESP32-S3 | 21.0 × 17.8, USB-C on short edge | Seeed datasheet | On female headers, perfboard top zone (exhaust side) |
| GY-BME680 breakout | ~16 × 12.5, 6-pin | measured; clones ±2 mm | On female headers, perfboard bottom zone (intake side). Clone variance → footprint guide sized for envelope |
| Perfboard | 40 × 60 × 1.6 | spec (frozen v3) | Carries both modules on female headers |
| Grove HM3301 module (Plus only) | carrier PCB 80 × 40 × 1.6; 4× Ø3.2 holes at (±36, ±16) from board centre; metal can 40 × 38 × 15 on top; Grove socket left end; 1.25 mm pigtail right | Seeed Eagle .brd (`ref_hm3301_board.pdf`) | Can's air inlet+outlet on TOP face of can. Module mounts vertically in rails; two Ø3.2 registration pegs |
| LiPo 803040 (provision only) | 40 × 30 × 8 | standard cell spec | DEC-04: floor lip/frame + cable space designed in; no battery in v1 build |
| Insect mesh | aperture ≤ 1.2 mm | — | Stainless or nylon; serviceable monthly |
| USB-C cable | Ø ~4.5 boot, bend radius ≥ 15 | typical | Exit with drip loop, faces down |

## 3. Frozen decisions (2026-06-08, Tomas)

| ID | Decision | Value |
|---|---|---|
| DEC-01 | Form reference | **v1.1 (2026-06-08): Batik-fractal meru.** Self-similar stacked tiers (meru/pagoda logic) carry rain + airflow; pierced batik-derived pattern bands (kawung-class geometry, abstracted — no sacred motif copied) in the rain-shadow under each tier. Organic, curved tier profiles — not hard cones. Register: batik language, pan-Indonesian. ~~v1.0: banana flower (jantung pisang)~~ → archived in `archive/concept-jantung-2026-06/` |
| DEC-02 | Size envelope | **≤ 140 mm tall**, target footprint ≤ Ø100 incl. tiers |
| DEC-03 | Service gesture | **v1.3: split access.** Monthly (mesh, battery): tool-free **bottom bayonet cap** Ø~56, fully rotational below the flat-back zone, one-handed ON the wall. Deep (boards, rare): unhook from keyholes, **2× M3** release the crown. Rationale: crown rotation is geometrically impossible against the wall. Clearances from coupons only |
| DEC-04 | Battery | **v1.3: provision deferred entirely.** Interference math: no LiPo placement coexists with the vertical HM3301 in a Ø76 body. Future battery = a deeper **battery-cap** variant of the bottom bayonet cap. Plus v1 is USB-C only |
| DEC-05 | Variant strategy | **v1.3 (Tomas): TWO bodies.** Plus = full N1 lima with PM bay; Basic = own smaller enclosure, no PM bay (family proposal: Basic as tumpang telu). Plus designed and validated first; Basic derived |
| DEC-06 | Mechanical CAD | **build123d** (BREP kernel, STEP+STL out). OpenSCAD CSG retired for enclosure bodies |
| DEC-07 | Skin method | Bracts as **BREP lofts/sweeps in build123d** first; Blender geometry-nodes is plan B if BREP reads too geometric in hand |
| DEC-08 | Material | **PETG only.** PLA banned (softens on Bali roofs) |
| DEC-09 | ~~Phase-1 base form: N1 lima meru~~ | Superseded by DEC-10 (v2). N1 was a single smooth-revolve tower; v1 functional build archived in `archive/v1-candi-tower-2026-06/` |
| DEC-10 | **v2 architecture (2026-06-08, Tomas): function-first, modular, faceted** | Four-part family: (a) **spine** — open chassis + flat back + keyholes + HM3301 rails + perfboard standoffs (validated internals carried from v1); (b) **shell** — faceted octagonal louver sleeve, the variant + aesthetic part, slides over spine, D-open back; (c) **base cap** — down-intake + cable + bayonet (shared); (d) **crown cap** — exhaust finial (shared). Basic = short spine+shell; Plus = tall. Decouples validated chassis from evolving aesthetic skin |
| DEC-11 | **Aesthetic: octagonal fractal-subdivided, triangulated** | 8-fold faceted body, twisted ruled-loft facets read as low-poly triangulation; batik/fractal lineage via self-similar (fractal-graded) louver rhythm. "Semi-organic digital" |
| DEC-12 | **Louvers = the facets** | Down-and-out angled triangular louver slots in fractal-graded bands ARE the skin: rain sheds off every facet, air enters the gaps, chimney draws bottom→top. Form=function=aesthetic. Thin-wall, support-free, material-minimal |
| DEC-13 | **Performance priorities (Tomas, explicit)** | 1) sensor airflow (chimney: BME680 low/intake, XIAO high/exhaust, HM3301 own duct); 2) zero water ingress (no up-facing apertures, louver shed, back-seam in wall shadow); 3) material + print-time economy (thin faceted walls, no infill, modular reprints); 4) modularity |

## 4. Environmental + functional requirements

| Req | Statement | Verification |
|---|---|---|
| F-01 | Rain shall have no sight line to any opening at any angle ≥ horizontal | Section render + hose test on printed unit |
| F-02 | All primary apertures face down or into bract rain-shadow (AirGradient pattern: down-only is the benchmark) | Geometry review |
| F-03 | Passive chimney: intake low (BME680 zone), exhaust high (XIAO zone); XIAO/regulator heat must not bake the BME680 | Temp cross-check vs reference sensor after deploy |
| F-04 | HM3301 fan gets a dedicated aperture path; can ports face down/sideways per datasheet, never up; inlet and outlet airflow separated; ports close to product aperture | Geometry review + PM co-location sanity check |
| F-05 | USB-C exits downward with drip loop space | Geometry review |
| F-06 | Keyhole wall mount behind boards: hang shell first, boards in after (v4 pattern, validated) | Hang test |
| F-07 | Insect mesh on all apertures, replaceable at monthly service | Service rehearsal |
| F-08 | Monthly service one-handed: bayonet open, mesh + battery check, close — no tools, nothing dropped | Service rehearsal on ladder |
| F-09 | Workshop-printable: support-free, fits 220 × 220 bed, ≤ 2 print plates per variant | Slicer report |
| F-10 | No text labels on parts; components locate by printed footprints (real outlines, real pin patterns — v5.1 spec) | Assembly rehearsal by a non-expert |

## 5. Printer truth (Tomas's machine — prototyping reference)

| Item | Value |
|---|---|
| Printer | Prusa CORE One, enclosed chamber |
| Nozzle | HF 0.4 mm (high-flow) |
| Bed | 250 × 220 × 270 (workshop constraint remains 220 × 220) |
| Slicer | PrusaSlicer 2.9.5, CLI in loop |
| Material profile | Generic PETG @COREONE HF0.4 |
| Draft profile | 0.15mm SPEED (prototypes) |
| Finish profile | 0.15mm or 0.10mm QUALITY-class for visible bract surfaces (seam paint/rear, slowed external perimeters) — to be defined at first skin print |

### 5.1 Measured fit numbers — **TBD FROM COUPONS (blocking)**

To be filled from the printed calibration set before any fit is modeled:

| Parameter | Coupon | Value |
|---|---|---|
| Sliding fit clearance (bayonet) | clearance ladder 0.10–0.60 | **TBD** |
| Free fit clearance (lids, inserts) | clearance ladder | **TBD** |
| Press fit interference (pegs in Ø3.2) | pin gauge | **TBD** |
| Horizontal hole shrink (Ø3.2, Ø5, Ø10) | hole gauge | **TBD** |
| Max clean overhang angle | 40/45/50° wedge | **TBD** |
| Min self-supporting bract edge thickness | fin wedge | **TBD** |
| Elephant-foot first-layer spread | base coupon edge | **TBD** |

## 6. Wall + structure rules (from AirGradient teardown, 2026-06-08)

Measured from their published outdoor enclosure STLs (`ref_airgradient/`, CC BY-SA 4.0):

- **Nominal wall: 2.5 mm** (their median 2.49–2.82; we adopt 2.5). Not 1.6. This is half the gap between "prototype" and "product."
- Bosses/ribs: 4–6 mm where fasteners or stress concentrate.
- Their architecture: perforated functional floor + collar + blind slide-over hood; **structure and weather skin are separate parts**. Validates our v4-core + bract-skin split.
- Every fillet visible. No raw cylinder bosses, no knife-edge wall junctions in the rebuild. Min visible fillet R1.5; structural junctions R2+.

## 7. Validated architecture carried forward (do not re-litigate)

From v4/v5 (see `archive/`): vertical HM3301 in front rails beside perfboard; keyholes behind boards; footprint guides (XIAO outline + 2×7-pin rows @2.54 + USB-C oval; BME680 outline + 6-pin row; battery frame; 2 pegs into carrier Ø3.2 holes); chimney stack BME-low/XIAO-high; apertures in bract rain-shadows.

## 8. Process gates (how this stays professional)

1. **Coupons before fits** — §5.1 filled, then CAD.
2. **Slicer in loop** — every candidate STL gets a PrusaSlicer CLI report (time, mass, thin walls, seam, supports) before Tomas sees it. No STL ships without it.
3. **Multi-view render + watertight gate** — `tools/run_model.py --preview --strict` on every iteration.
4. **Section prints before whole prints** — bayonet ring alone, one bract band alone, grille alone. Plastic validates each interface; full body prints once.
5. **Checkpoint reviews** — base form → features → final, Tomas approves at each gate (cad-skill pattern). No full-fidelity surprises.

## 9. Open items

| ID | Item | Owner | Status |
|---|---|---|---|
| OPEN-01 | DEC-05 variant strategy sign-off | Tomas | ✅ resolved v1.3: two bodies |
| OPEN-02 | Failure decomposition of previous prints (surfaces / fits / gestalt) + photos | Tomas | ⏭️ waived 2026-06-08 (Tomas: proceed on coupons alone) |
| OPEN-03 | ~~Banana flower reference~~ → superseded by meru form (DEC-09) | — | closed |
| OPEN-04 | Coupon measurements → §5.1 (**blocks all fit-critical prints**) | Tomas prints, both measure | pending |
| OPEN-05 | PETG brand/color for final units (Generic profile now) | Tomas | pending |
| OPEN-06 | Section prints of bayonet / reveal band / crown skirt before full Plus | Tomas prints, review | pending |
| OPEN-07 | ~~Phase-2 kawung pattern~~ → replaced by v2 chevron-louver skin (DEC-12) | — | closed |
| OPEN-08 | Section-print one chevron louver band — confirm down-out overhangs print clean (Pucuk base+neck sections sliced support-free, `pucuk/sections/`) | Tomas | STL ready, print pending |
| OPEN-09 | Lighten spine_plus (38 g/2h15 solid back plate) — rib + DRAFT profile | Claude | pending |
| OPEN-10 | v2 fits (bayonet, rails, back-lip capture, crown legs) ← coupons §5.1 | Tomas + Claude | pending |
| OPEN-11 | Pick Plus concept direction (C1 Pucuk / C2 Anyaman / C3 Tumpang massing) — gates the fidelity build → **C1 Pucuk**, fidelity build done, form LOCKED 2026-06-08 | Tomas | ✅ resolved |

## 10. Change log

| Version | Date | Change |
|---|---|---|
| 1.0-DRAFT | 2026-06-08 | Initial spec from handover §1 + frozen DEC-01…08 + AirGradient teardown numbers |
| 1.1-DRAFT | 2026-06-08 | DEC-01 re-frozen by Tomas: banana flower → batik-fractal meru (tiered self-similar form, pierced batik-derived vent bands, organic profiles). Engineering decisions DEC-02…08 unchanged; USB-at-tip superseded (silhouette freed — cable exit returns to underside, F-05 unchanged). Jantung arc archived: `archive/concept-jantung-2026-06/` |
| 1.2-DRAFT | 2026-06-08 | DEC-09: Tomas picked N1 lima (5 roofs) as Phase-1 base form, after gen3 retune (crisper flatter roofs, murda spire). Meru arc: gen1 ground-up taper rejected (pine tree), gen2 body+crown composition, gen3 approved |
| 1.3-DRAFT | 2026-06-08 | DEC-03 refined (bottom bayonet cap + screwed crown — wall blocks crown rotation); DEC-05 resolved by Tomas: two bodies, Plus first. Functional CAD authorized with placeholder clearances as named COUPON-TBD parameters; nothing fit-critical prints before §5.1 is measured |
| 1.4-DRAFT | 2026-06-08 | Direction reset (Tomas, post-handover): v2 four-part chevron-louver skin (DEC-10/DEC-12) retired as the frozen form — explore 2–3 fresh concept massing studies for the Plus body instead. Retained: faceted/triangulated principle (DEC-11), two bodies / Plus-first (DEC-05), all performance priorities (DEC-13), validated internals (§7). OPEN-02 failure-photo decomposition waived by Tomas — proceed on coupon numbers alone. New gating design decision = concept pick (OPEN-11) |
| 1.5-DRAFT | 2026-06-08 | C1 Pucuk built at fidelity (`tools/enclosure_pucuk.py`) and base-form gate CLEARED by Tomas — silhouette LOCKED. Twisted faceted octagonal shard (85° twist), fractal-graded louver bands, sealed side-venting finial, faceted inner cavity, validated candi internals transplanted, bottom bayonet. Watertight, interference 0.000 cm³, support-free (slicer); 82×71×129 mm; body 84.6 g/3h36m + cap 10.8 g/23m. Mass parked (grams are in the 2.5 mm wall perimeters of a tall shell, not the cavity). Section test-prints sliced support-free in `pucuk/sections/`: base (bayonet+floor+intake louvers, 32 g/1h21m), neck (exhaust louvers+finial, 22.6 g/1h). DEC-01 form ref now = Pucuk. |

---
*References: `ref_hm3301_board.pdf` (Seeed Eagle dims), `ref_airgradient/` (CC BY-SA 4.0 AirGradient Co. Ltd.), `archive/` (v1–v5.1 lessons), AirGradient Open Air assembly docs, HM3301 datasheet siting rules.*
