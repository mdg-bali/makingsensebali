# DIY-node enclosure — design log (Plus variant)

Wall-mounted outdoor air-quality node for Bali: hot, ~80%+ RH, monsoon, under
eaves. This log is the honest record of the 2026-06 design exercise — including
the wrong turn — so the next person doesn't repeat it.

## The brief, in priority order

Function is the form-giver. The cultural/visual reference is language, not driver.

1. **Sensor airflow.** Passive chimney: cool air in low, warm air (XIAO,
   regulator) out high, so component heat never bakes the BME680. The HM3301 has
   its own fan and its own air path.
2. **No water inside, ever.** No upward-facing aperture; rain sheds off every
   surface; no straight sightline into any opening.
3. **Print-efficient.** Thin walls, no supports, smallest honest envelope,
   grams and hours minimised.
4. **Modular / serviceable.** Monthly mesh + battery access; a damaged part is
   one reprint.

Hard constraints: PETG only (PLA softens on Bali roofs); support-free; ≤140 mm
tall; 2.5 mm wall (AirGradient production benchmark); keyhole wall mount;
replaceable insect mesh; footprint guides instead of text; two variants — Basic
(XIAO + BME680) and Plus (+ HM3301). Verified component dims and all frozen
decisions live in [`ICD.md`](ICD.md).

## What was tried (chronological, honest)

1. **Calibration coupons** (`coupons/`) sliced and ready — they gate every
   fit-critical dimension (ICD §5.1). Not yet printed/measured.
2. **Three concept directions** sketched as cheap massing
   ([`concept-sketch_pucuk-anyaman-tumpang.svg`](concept-sketch_pucuk-anyaman-tumpang.svg)):
   *Pucuk* (twisted faceted shard), *Anyaman* (woven lattice over a liner),
   *Tumpang* (faceted meru tiers). Tomas picked Pucuk.
3. **Pucuk built at fidelity** (`pucuk/`, `tools/enclosure_pucuk.py`): twisted
   faceted octagonal shard, fractal-graded louvers, sealed venting finial,
   validated internals, bottom bayonet. Watertight, interference 0, support-free,
   84.6 g / 3h36m. Section test-prints generated (`pucuk/sections/`).
4. **The correction (the point of this log).** Tomas, on review: *"all these
   designs do not make sense… too much focus on the form finding."* Right. The
   work had chased silhouette — "does the spiral read" — while the four
   fundamentals were inherited from the old candi build, not designed. The
   Ø71 cavity that drove Pucuk's 84 g existed because a round/faceted body wanted
   it, not because the boards needed it.
5. **Reset to fundamentals → the efficient version** (`efficient/`,
   `tools/enclosure_efficient.py`). Below.

## Current direction: `efficient/` — designed from the components out

| Fundamental | Decision |
|---|---|
| Cross-section | Sized to the boards + HM3301 rails: ~49×45.5 cavity, ~54×50.5 body. A compact filleted box, **not** a Ø71 shape. |
| Sensor placement = chimney | BME680 low (cool intake, true ambient); XIAO high (heat rises away from BME680); HM3301 vertical with its own fan duct so its exhaust never crosses the BME680. |
| Water | Every opening faces **down**. Intake = bottom cap (down-facing mesh). Exhaust = slots through the **underside of the roof eave** (shadowed by the roof above). HM3301 can grille on the front under a drip lip. No upward hole. |
| Print efficiency | Filleted box + hollow hipped roof whose eave underside is a 45° flare (support-free). 2.5 mm wall. Two parts. Prints upright, no supports. |

Validated internals carried unchanged: HM3301 in front C-rails + 2 pegs,
perfboard on back-wall standoffs, keyholes behind the boards, bottom bayonet cap.

### Numbers (slicer: CORE One HF0.4, Generic PETG, 0.15 SPEED)

| | Pucuk shard | **Efficient box** |
|---|---|---|
| Body | 84.6 g / 3h36m | **75.2 g / 3h03m** |
| Cap | 10.8 g / 23m | 7.9 g / 19m |
| Envelope | 82×71×129 mm | **54×55×114 mm** (62 wide incl. roof eave) |
| Parts | 2 | 2 |
| Supports | 0 | 0 |
| Watertight / interference | yes / 0.000 | yes / 0.000 |

### Honest limitations (not yet proven)

- **Mass only dropped ~11 %**, not the third first claimed. The grams are floored
  by a 114 mm height (the 80 mm HM3301 carrier forces it) × a 2.5 mm product
  wall. The real wins over Pucuk are simplicity, footprint, and function-first
  venting — not weight. Lighter than this needs a thinner wall (rejected) or a
  shorter body (the carrier won't allow it).
- **Water protection is geometry on screen, untested in rain.** The down-facing
  eave exhaust and the bottom intake follow the AirGradient rule, but only a hose
  test on a printed unit proves it.
- **Board access is bottom-loading** through the Ø44 cap opening — rehearse on
  the first print; if it fights, a removable roof (bosses already in the body)
  is the v2 fix.
- **All fits are `COUPON_TBD_*` placeholders** until the coupons are measured
  into ICD §5.1.

## Folder map

- `ICD.md` — interface control doc: verified component dims, frozen decisions, fits table, change log.
- `coupons/` — calibration coupons, sliced, **print first** (gate ICD §5.1).
- `efficient/` — current direction (`eff_body`, `eff_cap`; generator `tools/enclosure_efficient.py`).
- `pucuk/` — the Pucuk shard exploration + section test-prints (`tools/enclosure_pucuk.py`).
- `concepts/`, `archive/` — earlier concept sets and dead directions (candi, meru, gourd, pine-cone, lantern, box), each with its own notes.
- `ref_airgradient/`, `ref_form/` — reference enclosures (the professional benchmark).
- `tools/` — build123d generators + `run_model.py` (watertight + 6-view render) + `preview.py` + `mesh_io.py`.

## Next

1. Print the **coupons** → measure → fill ICD §5.1.
2. Print **`efficient/eff_body` + `eff_cap`**, hang it, hose-test the water path,
   rehearse board loading.
3. Fold the coupon numbers into the fits; fix whatever the plastic flunks.
4. Derive the **Basic** body (no PM bay) from the validated Plus.
