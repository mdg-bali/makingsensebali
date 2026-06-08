# Calibration coupons — print these before any enclosure CAD

Two plates, sliced with your presets (CORE One HF0.4, Generic PETG, 0.15mm SPEED):

| File | Time | PETG | What it answers |
|---|---|---|---|
| `coupon_A_fits.bgcode` | ~48 min | 21 g | clearances, hole shrink, elephant foot |
| `coupon_B_print.bgcode` | ~36 min | 10 g | max overhang, horizontal holes, PETG snap spring |

Print both as-is, no supports, no brim changes. **Don't deburr or sand anything before measuring.**

## Coupon A — fits plate

- 7 holes labeled 0–6: nominal Ø5.00 plus 0.0–0.6 mm clearance.
- 7 edge slots, same labels: nominal 3.00 mm plus the same ladder.
- 3 loose pins (Ø5.00, printed vertical like the holes), 2 loose tabs (3.00 mm thick).

**Record:**
1. Lowest-numbered hole the pin **slides into with light push** → *sliding fit*
2. Lowest-numbered hole the pin **drops into freely** → *free fit*
3. Same two numbers for tab-in-slot
4. Caliper the pins (actual Ø) and hole 0 (actual Ø) → shrink numbers
5. Caliper the plate edge at the bottom vs mid-height → elephant foot

## Coupon B — print behavior

- 5 fins labeled 35/40/45/50/55 = degrees from vertical.
- Wall with 3 horizontal holes: Ø3.2 / Ø5 / Ø10 (keyhole + peg proxies).
- Snap stick: flex the beam up by hand, repeatedly, then harder.

**Record:**
1. Steepest fin whose **underside still looks acceptable** → max design overhang
2. Caliper the horizontal holes (height vs width — they print as slight ovals)
3. Snap stick: does it spring back? whiten? crack at the layer line?

## Report back

Tell Claude the numbers (or photograph the filled table). They go into `ICD.md §5.1` and every fit in the rebuild derives from them.
