# Handover: Making Sense Bali DIY-node enclosure — redesign (v3)

**From:** Claude (Cowork session with Tomas Diez, June 2026)
**To:** the next agent taking the enclosure from scratch
**Mandate:** clean sheet. You are not refining the existing design. You get the
brief, the verified component dimensions, and a working toolchain — everything
else is yours to invent. **But the brief below is law, and the process is law.**
**Spend your effort first on printability and assembly reality** — that is where
every prior attempt failed.

Repo: `hardware/diy-node/enclosure/` · local: `~/Documents/Claude/Projects/MDG/smartcitizenbali/`

---

## 0. Read this first — why you exist

Two sessions have now designed this enclosure. The first built five OpenSCAD
generations and printed several; Tomas called them "disappointing and
unprecise." The second (this one) built five *more* directions — banana-flower,
meru tower, candi tower, and a modular faceted shell — in build123d, with
interference checks and slicer reports. **It printed nothing.** Every direction
looked plausible in renders and none has touched a bed.

That is the failure mode. Renders cannot see stringing on a louver tip, a snap
that won't snap, elephant-foot eating a 0.3 mm clearance, or a chevron blade
sagging in PETG. The product's feedback loop is plastic; the agent's was pixels.
Your job is to break that pattern: **print cheap, print early, design around
what the plastic tells you.** If you produce a sixth beautiful render and no
test print, you have failed exactly as we did.

---

## 1. The brief (Tomas's words — binding)

Function is the form-giver. The cultural reference is the *language*, not the
driver. In priority order:

1. **Sensor airflow is paramount.** Passive chimney: cool air in low, warm air
   (XIAO, regulator heat) out high, so component heat never bakes the BME680.
   The HM3301 has its own fan and its own air path. This drives the whole form.
2. **No water inside, ever.** Wall-mounted outdoors in Bali — heat, ~80%+ RH,
   monsoon, under eaves. No upward-facing aperture. Rain sheds off every
   surface; no straight sightline into any opening; drip loops and shadowed
   seams. Water exclusion beats everything except airflow.
3. **Material and print time conscious.** Thin walls, no wasted infill, no
   supports, smallest honest envelope. It will be printed at workshop scale —
   grams and hours matter.
4. **Modular.** A good modular split — so variants share parts, a damaged piece
   is one reprint, and the design can evolve without reprinting everything.
5. **Aesthetic: keep the batik + fractal lineage.** Tomas explicitly wants
   **more triangulated surfaces — a digital aesthetic for a semi-organic
   design.** Faceted/low-poly, self-similar (fractal-graded) rhythm, Balinese
   resonance. Not smooth organic blobs, not a plain box. The triangulation is
   both look and print strategy (flat facets need no supports).

Carried hard constraints (non-negotiable, from the original spec):
PETG only (PLA softens on Bali roofs). Support-free, workshop-printable. ≤ 140 mm
tall. Keyhole wall mount. Insect mesh on apertures, replaceable. Monthly service
access (mesh, battery check). No text on parts — components locate by **printed
footprint guides** (real outlines, real pin patterns). Two variants: **Basic**
(XIAO + BME680) and **Plus** (+ HM3301).

---

## 2. Ground truth — design to these numbers (do not re-derive)

Verified component dimensions (mm). The HM3301 set is extracted from Seeed's
Eagle `.brd` (`ref_hm3301_board.pdf` in repo) — trust it.

| Component | Dimensions | Notes |
|---|---|---|
| Seeed XIAO ESP32-S3 | 21 × 17.8 | USB-C on one short edge |
| GY-BME680 breakout | ~16 × 12.5, 6-pin | clones vary ±2 mm — size to the envelope |
| Perfboard (both boards sit on it) | 40 × 60 × 1.6 | female headers |
| HM3301 carrier PCB | **80 × 40 × 1.6** | 4× Ø3.2 holes at (±36, ±16) from centre |
| HM3301 metal can | 40 × 38 × 15 | sits on carrier; **air ports on the can's top face** |
| HM3301 connectors | Grove socket left end, 1.25 mm pigtail right | |
| LiPo (optional) | 803040 → 40 × 30 × 8 | see lesson §5 — probably won't fit beside the module |

**Datasheet rules (HM3301):** ports face **down or sideways, never up**;
separate inlet from outlet; keep ports near the product aperture; the product
completes the rain protection. The carrier is 80 mm long — this single number
has driven every body to be tall. Plan for it from line one.

**Environment / print target:** Bali, under eaves. Printer is Tomas's **Prusa
CORE One**, **HF 0.4 mm nozzle**, enclosed chamber. Material **Generic PETG
@COREONE HF0.4**, profile **0.15mm SPEED** (use a faster DRAFT profile for hidden
structural parts, a finer one for visible faces). Bed is 250×220×270, but keep
the **workshop constraint of 220×220** so other printers can make it.

---

## 3. The toolchain already works — use it, don't rebuild it

A build123d (BREP kernel) pipeline is installed and proven on this machine.
**Do not use OpenSCAD / CSG** — the first session's "programmer geometry"
(no fillets, sharp everything) is exactly what Tomas rejected. BREP gives you
fillets, drafts, STEP, and scriptable interference detection.

- **venv:** `~/Documents/Claude/Projects/MDG/.cad-venv` (build123d, trimesh,
  pyrender, rtree, Pillow). Run scripts with that interpreter.
- **`tools/run_model.py`** — runs a model script in a subprocess, finds the STLs
  it wrote, renders a 6-view preview, checks watertightness, emits JSON.
  `--preview --strict` fails on non-watertight. This is your inner loop.
- **`tools/preview.py`** — 6-view technical render of any STL (toolchain-agnostic).
- **`tools/mesh_io.py`** — STL load with the **merge-before-watertight** step
  BREP exporters need (build123d writes topologically-unmerged but closed meshes;
  merge or every watertight check lies).
- **Slicer in the loop (mandatory, every candidate):**
  `PrusaSlicer` CLI at `/Applications/Original Prusa Drivers/PrusaSlicer.app/Contents/MacOS/PrusaSlicer`,
  `-g model.stl --datadir <PrusaSlicer cfg> --printer-profile "Prusa CORE One HF0.4 nozzle" --print-profile "0.15mm SPEED @COREONE HF0.4" --material-profile "Generic PETG @COREONE HF0.4" -o out.bgcode`.
  Pull time + grams from the bgcode strings; verify `;TYPE:Support` count is **0**.
  No STL ships to Tomas without its slicer report.

**build123d gotchas already paid for (save yourself the cycles):**
disjoint `Solid + Solid` returns a `ShapeList` — wrap unions in a `largest()`
helper or `Compound`; tilt a cutter **at the origin then translate out** (rotating
about the global origin flings it off the part); `RegularPolygon(rotation=22.5)`
puts flats at 45+45k, vertices at 22.5+45k — get this wrong and your features
land between facets; macOS prepends a state-banner line to stdout, so regex the
JSON out of `run_model` output, don't `json.load` the whole thing.

Run all CAD/render/slice on the **Mac** (the sandbox has no GPU and blocked
egress). Don't run git in the sandbox (it leaves stale lock files).

---

## 4. Process — this is not optional

The order that should have been followed from the start:

1. **Freeze a one-line-per-decision spec before CAD.** The ICD exists
   (`ICD.md`); update it, don't restart it. Any change is a versioned change,
   not a vibe.
2. **Print the calibration coupons FIRST.** They are built and already sliced:
   `coupons/coupon_A_fits.bgcode` (~48 min) and `coupon_B_print.bgcode` (~36 min),
   ~31 g total. They give you the real clearance ladder, hole shrink, max
   overhang, and PETG snap behaviour on *this* machine. **Write the measured
   numbers into `ICD.md §5.1`. Nothing fit-critical gets modelled before that.**
   Every clearance in your CAD is a named parameter (`COUPON_TBD_*`) until then.
3. **Cheap concepts before full models.** 2–3 disposable massing renders, get
   Tomas to pick a direction, *then* build at fidelity. We burned hours building
   full models of directions that a 2-minute concept would have killed.
4. **Section-print every novel interface before any full enclosure** — one
   louver band, the joint/bayonet, the mesh seat. Validate in plastic, then
   print the whole thing once.
5. **Review in hand with Tomas** before publishing. Renders are for you; plastic
   is for him.

---

## 5. Hard-won lessons (don't rediscover these)

- **The 80 mm carrier dictates a tall, narrow body.** A squat form forces the
  module sideways and packaging fails. Start tall.
- **No LiPo fits beside the vertical HM3301 in a sane diameter.** Interference
  math killed every placement. If a battery is wanted, make it a deeper
  **base/cap module**, not an internal bay. Confirm with Tomas whether v1 even
  needs a battery (current answer: no, USB-C powered).
- **A crown/top cap cannot be the service opening.** The flat back sits against
  the wall; anything that rotates (bayonet) swings its eaves into the wall.
  Monthly service belongs on the **bottom**.
- **Wall ≈ 2.5 mm.** Measured from AirGradient's production outdoor enclosure
  (`ref_airgradient/`, the professional benchmark — study it). 1.6 mm reads as a
  prototype; 2.5 is half the distance to "product."
- **Faceted + triangular louvers print clean and read "digital."** Smooth
  revolves read generic and Tomas rejected them. Down-and-out chevron louvers
  shed water *and* admit air *and* carry the aesthetic — but **their overhang
  undersides are unproven in plastic; section-print them.**
- **Keep the validated internal logic** (it's the one thing that survived every
  redesign): vertical HM3301 held by its 4× Ø3.2 holes and/or side rails,
  perfboard on standoffs against the back wall, keyholes behind the boards
  (hang the shell first, populate after), BME680 low / XIAO high for the chimney.

---

## 6. What NOT to do

Design only in renders. Skip the coupons. Re-derive the component dims instead of
using §2. Point any aperture up. Assume a rotating crown. Add an internal battery
bay. Use PLA. Use OpenSCAD/CSG. Build a full-fidelity model of an unapproved
direction. Let "modular" multiply joints you never water-test. Hand Tomas a
render and call it done.

---

## 7. What's in the repo (reference — NOT your starting point)

You have a clean sheet, but the record is honest and worth a read before you draw:

- `ICD.md` — interface-control doc, all decisions + the empty §5.1 fits table to fill.
- `ref_hm3301_board.pdf` — Seeed Eagle dims (ground truth).
- `ref_airgradient/` — the professional benchmark enclosure STLs + teardown numbers.
- `coupons/` — calibration set, **sliced and ready to print** (your step 2).
- `archive/` — every dead direction with an honest README: `concept-jantung-…`
  (banana flower, 4 gens), `concept-meru-gen1-…` (pine-tree reject),
  `v1-candi-tower-…` (first functional build, ~89 g/4 h, proved the packaging math).
- `v2/` — the modular faceted shell+spine+base+crown (Plus ~78 g/5 h, Basic
  ~48 g/3.5 h, support-free, watertight, never printed). Read its `BUILD.md` for
  what the chevron-louver skin was trying to be and where it's weak (heavy spine,
  unproven overhangs). Take the ideas you like; you owe it nothing.

---

## 8. First moves

1. Ask Tomas for: photos of any failed prints (still outstanding — real failure
   data this whole effort lacks), PETG brand/colour, and a yes/no on one-body-two-
   variants vs two bodies. Get his sign-off on the spec.
2. Print the coupons. Measure. Fill `ICD.md §5.1`. (No fit-critical CAD before this.)
3. Re-read §1. Sketch 2–3 cheap concepts that put airflow and water-shedding
   first and wear the triangulated/batik skin. Get Tomas to pick one.
4. Build the chosen direction in build123d with the toolchain; clearances from
   your measured numbers; interference-check against the §2 component dummies;
   slice every candidate.
5. Section-print the louver band, the joint, the mesh seat. Fix in plastic.
6. Print one full variant. Review in hand with Tomas. Then publish.

The epitaph from the first handover still holds: design for the full purchased
module, joints need hard stops and measured clearances, rain protection is
geometry — **and verify in the medium that matters.** Be more honest, earlier,
in plastic than we were.
