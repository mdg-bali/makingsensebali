# Enclosure v2 — modular faceted (function-first)

Generator: `tools/enclosure_v2.py` (set `MSB_VARIANT=plus|basic`).
Status: **geometry complete, watertight, interference-clean, slicer-verified
support-free. NOT yet validated in plastic.** Fits are `COUPON_TBD_*` (ICD §5.1).

## The idea

Function is the form-giver; batik/fractal is the language it's spoken in.
The skin is a field of **triangulated chevron louvers** — apex-up triangles
that shed rain off their inverted-V blades while the gaps admit air, graded
fractally (big intake low → fine exhaust high). Octagonal faceting + staggered
rows give the "semi-organic digital" read. The louvers ARE the surface, not
decoration on it.

## Four modules (DEC-10)

| Part | Role | Shared? |
|---|---|---|
| **spine** | open chassis: flat back, keyholes, HM3301 rails, perfboard standoffs, crown bosses, USB chase | per-variant height |
| **shell** | faceted octagonal chevron-louver sleeve, D-open back, slides over spine — the aesthetic + weather + airflow skin | per-variant (the look lives here) |
| **base** | bottom cap: down-facing intake, cable, bayonet, mesh seat | **shared Plus/Basic** |
| **crown** | faceted finial on 3 legs → continuous ring-gap exhaust, 2× M3 to spine | **shared Plus/Basic** |

The win: the validated chassis is **decoupled from the evolving skin** — reprint
shells to iterate the batik look without touching the working spine; print the
fiddly caps once and reuse across variants and reprints.

## Performance (DEC-13 priorities)

1. **Airflow** — chimney: down-intake at the base (cool air, by the BME680 low) → up the open chassis → out the high exhaust chevrons + the crown ring-gap (by the XIAO). HM3301 can ports face the front fan-grille band (sideways = datasheet-legal). Open back = unobstructed vertical flow.
2. **Water** — every chevron leans down-and-out (sheds + no straight sightline); rows overlap; no up-facing aperture anywhere; crown overhangs the rim 5 mm over its exhaust gap; the shell↔spine seam is at the back, in the wall's rain shadow.
3. **Material/time** — 1.8 mm faceted walls, no infill, open back removes a quarter of the sleeve; the louvers remove ~4 cm³ more.
4. **Modularity** — see above.

## Print summary (CORE One, PETG, 0.15 SPEED, support-free, watertight)

| | spine | shell | base | crown | **total** |
|---|---|---|---|---|---|
| **Plus** | 38.4 g / 2h15 | 25.6 g / 2h00 | 4.6 g / 15m | 9.1 g / 27m | **≈78 g / ~5h** |
| **Basic** | 16.6 g / 1h23 | 17.8 g / 1h23 | *(shared)* | *(shared)* | **≈48 g / ~3.5h** |

vs v1 monolith: ~89 g. Basic shares base+crown, so its marginal cost is just
the spine+shell. Print parts in parallel across a print farm / multiple sessions.

## Assembly

1. Hang **spine** on two wall screws (keyholes).
2. **Plus only:** slide HM3301 carrier down the rails; pegs set depth.
3. Screw **perfboard** to the four standoffs (M2 self-tap). BME680 low, XIAO high.
4. Route **USB-C** out the angled-down chase (drip loop).
5. Slide **shell** down over the spine (D-back mates to the spine plate; back lips capture it).
6. **Crown** on top, 2× M3 from inside the back into the crown legs/bosses.
7. **Base** cap from below: insert, quarter-turn bayonet. Holds the intake mesh. Monthly-service opening.

## HONEST status — what's proven vs not

Proven digitally: all parts watertight; every component clears every wall and
neighbour (interference = 0.000 cm³); slicer confirms support-free with real
time/mass; whole stack 127 mm (< 140 cap), flat back.

NOT proven (needs plastic):
- **Every fit is a placeholder** (`COUPON_TBD_*`): bayonet, rails, pegs, M2/M3
  pilots, shell↔spine back-lip capture, crown legs, mesh seat. Coupons
  (`../coupons/`) must be printed + measured → ICD §5.1 → before fit-critical prints.
- **Chevron louver overhangs:** slicer says support-free, but the down-out blade
  undersides need a real print to confirm they don't sag/string at the tips.
  **Section-print one louver band first.**
- Real airflow + rain behaviour: hose test + sensor co-location after a full build.
- The shell↔spine back capture and the crown ring-gap rain-shadow are modeled,
  never tested — section-print the shell top + crown, and the shell back + spine edge.

Next physical step: section prints (one louver band; the bayonet base + shell
foot; the crown + shell rim), not a full tower. Cheap plastic, real answers.

## Known optimisation targets (next iteration)

- **spine_plus is the heavy/slow part** (38 g / 2h15): solid back plate. Rib/
  lighten it, and print it on a fast DRAFT profile (it's hidden) — easy ~30% off.
- Twist the facets (currently 0°) for more organic shear, once the look is approved.
