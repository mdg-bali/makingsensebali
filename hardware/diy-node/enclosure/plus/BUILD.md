# Plus enclosure — functional build R1 "candi tower"

Generator: `tools/enclosure_plus.py` → STL + STEP in this folder.
Status: **geometry complete, watertight, support-free, interference-clean.
NOT yet validated in plastic.** Fits are placeholders (ICD §5.1 coupons gate).

## What it is

A stepped candi/meru tower that holds the full Plus sensor stack. The body
*is* the fractal — five battered registers with projecting reveal rings —
so the form reads as Balinese architecture, not a box wearing a hat. A
five-roof crest with a murda spire crowns it; a twist-off cap underneath
handles monthly service.

Assembled: **90 × 74 × 127 mm**, flat back, hangs on two keyhole slots.

## Three printed parts (PETG, CORE One HF0.4, 0.15 SPEED, no supports)

| Part | File (print) | Time | PETG | Orientation |
|---|---|---|---|---|
| Body | `plus_body_print.stl` | 2h 51m | 69 g | **inverted** (rim on bed) — reveals & dome chamfer print support-free |
| Crown | `plus_crown.stl` | 44 m | 9 g | upright (skirt on bed) — 42° conical roof undersides, no supports |
| Cap | `plus_cap.stl` | 23 m | 11 g | upright (disc on bed) |

`plus_body.stl` is the same body in as-designed (upright) orientation for
viewing; print `plus_body_print.stl`. Total ~4h, ~89 g for one Plus node.

## How the parts go together

1. **Hang the body** on two wall screws via the keyholes (behind the board
   zone — hang first, populate after).
2. **Slide the HM3301 carrier** down the two internal C-rails, can facing
   front; the two pegs enter the carrier's lower Ø3.2 holes and set depth.
3. **Screw the perfboard** to its four back-wall standoffs (M2 self-tap).
   BME680 sits low (intake), XIAO high (exhaust) — the chimney runs past
   them bottom-to-top.
4. **Route USB-C** out the angled-down chase at lower back-left (drip loop).
5. **Crown on** over the body rim, 2× M3 from inside the back into the
   crown bosses — deep service only.
6. **Cap on** from below: insert, quarter-turn to lock (bayonet). Holds the
   intake mesh ring. This is the monthly-service opening.

## Performance features (ICD §4) and where they live

- **Chimney (F-03):** intake at the bottom cap → past BME680 (low) → up the
  hollow body and crown chimney → exhaust at the pierced body bands (high,
  in reveal shadow). Component heat rises away from the BME680.
- **Rain (F-01/F-02):** every aperture sits under a projecting reveal ring
  or eave; cap intake faces straight down behind a drip brim.
- **PM fan (F-04):** dedicated clover grille on the can face, register 2,
  separated from the chimney exhaust path.
- **Service (F-08):** bottom bayonet cap, one-handed, on the wall.
- **Mesh (F-07):** seats in the cap window, replaceable at service.

## HONEST status — what is and isn't proven

Proven (digitally): geometry compiles, all parts watertight, every
component clears every wall and neighbour (interference = 0.000 cm³),
slicer confirms support-free with real time/mass.

NOT proven (needs plastic):
- **Every fit is a guess** (COUPON_TBD_* placeholders): bayonet, rails,
  pegs, M2/M3 pilots, mesh seat. The coupons (`../coupons/`) must be printed
  and measured, numbers written to ICD §5.1, before any fit-critical print.
- Bayonet lug/slot engagement is modeled, never tested — print the cap +
  the floor ring as a section first.
- Reveal overhang printability (the ring undersides, inverted) — section
  print one register band.
- Real airflow and rain behaviour — hose test + co-location after a full
  print.
- **Aesthetics are functional-grade, not final.** Pattern bands are simple
  clover piercings; Phase 2 develops the kawung fractal properly.

Recommended next physical step: **section prints**, not a full tower —
(a) cap + floor ring (bayonet), (b) one reveal-ring band (overhang + a
pierced vent), (c) crown skirt + roof 0 (eave + chimney). Cheap plastic,
real answers, before 4 hours of full print.
