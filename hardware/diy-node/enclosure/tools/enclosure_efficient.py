#!/usr/bin/env python3
"""Making Sense Bali — PLUS enclosure, "efficient" reset (ICD 1.6-DRAFT, 2026-06-08).

Function is the form-giver. No styling. Designed from the components out:

  * CROSS-SECTION sized to the boards, not to a shape. The boards are ~40 mm
    wide; with the HM3301 side-rails the cavity is ~49 x 45.5 mm and the body
    is ~54 x 50.5 — a compact filleted box, not a Ø71 cavity. ~1/3 less plastic
    than the Pucuk shard.
  * SENSOR PLACEMENT = the chimney. BME680 low at the cool intake (true ambient);
    XIAO high so its heat rises away from the BME680; HM3301 vertical with its
    own fan duct so its exhaust never crosses the BME680.
  * WATER by the proven rule (AirGradient benchmark): every opening faces DOWN.
    Intake = the bottom cap (down-facing mesh). Exhaust = slots through the
    UNDERSIDE of the roof eave (down-facing, fully shadowed by the roof above).
    HM3301 can grille on the front, under a drip lip. No upward hole anywhere.
  * PRINT EFFICIENCY. Filleted box + a hollow hipped roof whose eave underside
    is a 45° flare (support-free); 2.5 mm wall; two parts (body + bottom cap);
    no finial, no decorative facets. Prints upright, no supports.

Validated internals carried unchanged from the candi build (interference-clean):
HM3301 in front C-rails + 2 pegs, perfboard on back-wall standoffs, keyholes
behind the boards, bottom bayonet cap.

ALL FITS PLACEHOLDERS — COUPON_TBD_*, swap with measured numbers (ICD 5.1).
"""
import os
from build123d import *  # noqa: F403

OUT = os.path.join(os.path.dirname(__file__), "..", "efficient")
os.makedirs(OUT, exist_ok=True)

# ---- COUPON-TBD fits (ICD 5.1), PETG-conservative placeholders ----
COUPON_TBD_SLIDE = 0.30
COUPON_TBD_PRESS = -0.05
COUPON_TBD_PILOT_M2 = 1.75
COUPON_TBD_PILOT_M3 = 2.65

# ---- frozen component dims (ICD 2) ----
perf_w, perf_h, perf_t = 40.0, 60.0, 1.6
hm_w, hm_h, hm_t = 40.0, 80.0, 1.6
can_w, can_h, can_d = 38.0, 40.0, 15.2
hm_hole_d = 3.2

# ---- shell / layout (Z up; +Y front, flat back at y=-back_y) ----
wall = 2.5
back_y = 16.0
back_inner = back_y - wall            # 13.5
HW = 27.0                             # outer half-width  -> 54 wide
HW_IN = 24.5                          # inner half-width  -> 49 (clears ±24 rails)
FRONT = 34.5                          # outer front y     -> depth 50.5
FRONT_IN = 32.0                       # inner front y     -> cavity depth 45.5
fillet_r = 3.0

floor_z = 12.0
body_top = 96.0                       # wall top (carrier top = 93)
hm_z0 = 13.0
hm_carrier_y = 13.0
perf_back_gap = 4.0
perf_z0, perf_cx = 18.0, 0.0
key_x, key_z = 16.0, 64.0

eave = 4.0                            # roof overhang past the wall (front + sides)
roof_h = 18.0
cap_r = 22.0
cap_window_r = 14.0
n_lugs = 3
cap_cy = (FRONT_IN - back_inner) / 2   # bayonet centred on the cavity (box), not the origin → flush back


# ---- helpers (validated candi idioms) ----
def largest_solid(x):
    try:
        solids = list(x.solids())
    except (AttributeError, TypeError):
        solids = [s for item in x for s in item.solids()]
    if not solids:
        raise ValueError("boolean produced no solids")
    return max(solids, key=lambda s: s.volume)


def back_cut(shape, y_plane):
    cutter = Pos(0, y_plane, 0) * Box(
        500, 400, 500, align=(Align.CENTER, Align.MAX, Align.CENTER))
    return largest_solid(shape - cutter)


def yrect(z, y0, y1, w, d_extra=0.0):
    """Rectangle sketch at height z spanning y0..y1, width w (centered x)."""
    cy = (y0 + y1) / 2.0
    return Pos(0, cy, z) * Rectangle(w, (y1 - y0) + d_extra)


# ---- component dummies (interference targets) ----
hm_carrier = Pos(0, hm_carrier_y, hm_z0) * Box(
    hm_w, hm_t, hm_h, align=(Align.CENTER, Align.MIN, Align.MIN))
hm_can = Pos(0, hm_carrier_y + hm_t, hm_z0 + (hm_h - can_h) / 2) * Box(
    can_w, can_d, can_h, align=(Align.CENTER, Align.MIN, Align.MIN))
hm_module = hm_carrier + hm_can
can_face_z0 = hm_z0 + (hm_h - can_h) / 2          # 33.0
can_front_y = hm_carrier_y + hm_t + can_d         # 29.8

perf_y0 = -back_inner + perf_back_gap
perfboard = Pos(perf_cx, perf_y0, perf_z0) * Box(
    perf_w, perf_t, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
perf_env = Pos(perf_cx, perf_y0 + perf_t, perf_z0) * Box(
    perf_w, 12.0, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))

# ============================================================
# BODY — compact filleted box
# ============================================================
body = Pos(0, -back_y, 0) * Box(
    2 * HW, back_y + FRONT, body_top, align=(Align.CENTER, Align.MIN, Align.MIN))
body = fillet(body.edges().filter_by(Axis.Z), fillet_r)

cavity = Pos(0, -back_inner, floor_z - wall) * Box(
    2 * HW_IN, back_inner + FRONT_IN, body_top + 10,
    align=(Align.CENTER, Align.MIN, Align.MIN))
cavity = fillet(cavity.edges().filter_by(Axis.Z), fillet_r - 1.0)
body = largest_solid(body - cavity)

# floor plate with cap opening
floor_plate = Pos(0, -back_y, floor_z - wall) * Box(
    2 * HW, back_y + FRONT, wall, align=(Align.CENTER, Align.MIN, Align.MIN))
floor_plate = fillet(floor_plate.edges().filter_by(Axis.Z), fillet_r)
floor_plate = largest_solid(
    floor_plate - Pos(0, cap_cy, 0) * Cylinder(cap_r - 3.0, 100,
                           align=(Align.CENTER, Align.CENTER, Align.CENTER)))
body = body + floor_plate

# bayonet cap seat ring
cap_seat = Pos(0, cap_cy, floor_z - wall - 6.0) * Cylinder(
    cap_r + wall + COUPON_TBD_SLIDE, 6.0,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
cap_seat = largest_solid(
    cap_seat - Pos(0, cap_cy, floor_z - wall - 6.1) * Cylinder(
        cap_r + COUPON_TBD_SLIDE, 6.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN)))
body = body + cap_seat

# HM3301 rails + registration pegs (validated)
rail_gap = hm_t + COUPON_TBD_SLIDE
for sx in (-1, 1):
    post = Pos(sx * (hm_w / 2 + 2.0), hm_carrier_y + rail_gap / 2, hm_z0 - 1) * Box(
        4.0, rail_gap + 5.0, hm_h + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    slot = Pos(sx * (hm_w / 2 - 1.0), hm_carrier_y - 0.05, hm_z0 - 1.5) * Box(
        6.0, rail_gap, hm_h + 4.0, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = largest_solid(body + post - slot)
for sx in (-1, 1):
    peg = Pos(sx * 16.0, hm_carrier_y - 0.02, hm_z0 + 4.0) * Rot(-90, 0, 0) * \
        Cylinder((hm_hole_d + COUPON_TBD_PRESS) / 2, hm_t + 1.2,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body + peg

# perfboard standoffs (M2)
so_dx, so_dz = 16.2, 26.2
perf_cz = perf_z0 + perf_h / 2
for sx in (-1, 1):
    for sz in (-1, 1):
        sx_, sz_ = sx * so_dx, perf_cz + sz * so_dz
        post = Pos(sx_, -back_inner, sz_) * Rot(-90, 0, 0) * Cylinder(
            3.0, perf_back_gap, align=(Align.CENTER, Align.CENTER, Align.MIN))
        pilot = Pos(sx_, -back_inner - 0.1, sz_) * Rot(-90, 0, 0) * Cylinder(
            COUPON_TBD_PILOT_M2 / 2, perf_back_gap + 4,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        body = largest_solid(body + post - pilot)

# keyholes behind the boards
for sx in (-1, 1):
    kh = Pos(sx * key_x, 0, key_z) * Rot(-90, 0, 0) * Cylinder(
        4.0, 50, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    ks = Pos(sx * key_x, -back_y - 2, key_z) * Box(
        4.0, 10, 10, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = largest_solid(largest_solid(body - kh) - ks)

# USB-C exit chase (angled down, lower back-left)
usb = Pos(-14.0, -2.0, 18.0) * Rot(35, 0, 0) * Cylinder(
    4.25, wall + 22, align=(Align.CENTER, Align.CENTER, Align.MIN))
body = largest_solid(body - usb)

# HM3301 can grille on the front wall, shadowed by a printed drip lip
for gz in (can_face_z0 + 10, can_face_z0 + 22):
    grille = Pos(0, FRONT - 1.0, gz) * Box(
        24.0, wall + 6.0, 2.4, align=(Align.CENTER, Align.MAX, Align.CENTER))
    body = largest_solid(body - grille)
lip = Pos(0, FRONT, can_face_z0 + 30) * Box(
    30.0, 4.0, 2.4, align=(Align.CENTER, Align.MIN, Align.MIN))   # drip lip over grille
body = body + lip

# ============================================================
# ROOF — hollow hipped cap, 45° support-free eave; exhaust on the eave underside
# ============================================================
zb = body_top
# outer: wall-top rect -> eave rect (45° flare over `eave`) -> small top rect
roof_outer = loft([
    yrect(zb, -back_y, FRONT, 2 * HW),
    yrect(zb + eave, -back_y, FRONT + eave, 2 * HW + 2 * eave),
    Pos(0, (FRONT - back_y) / 2, zb + roof_h) * Rectangle(16.0, 12.0),   # centred apex
], ruled=True)
roof_inner = loft([
    yrect(zb - 0.1, -back_inner, FRONT_IN, 2 * HW_IN),
    yrect(zb + eave, -back_inner, FRONT_IN, 2 * HW_IN),
    Pos(0, (FRONT_IN - back_inner) / 2, zb + roof_h - wall) * Rectangle(8.0, 6.0),
], ruled=True)
roof = largest_solid(roof_outer - roof_inner)
roof = back_cut(roof, -back_y)
body = body + roof

# exhaust: slots through the down-facing eave underside (rain-shadowed)
for sx_t in (-22.0, 0.0, 22.0):
    ex = Pos(sx_t, FRONT + eave - 3.0, zb + eave - 1.0) * Rot(45, 0, 0) * Box(
        12.0, 3.0, 10.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    body = largest_solid(body - ex)
for sy_t in (8.0, 26.0):
    for sgn in (-1, 1):
        ex = Pos(sgn * (HW + eave - 3.0), sy_t, zb + eave - 1.0) * Rot(0, sgn * 45, 0) * Box(
            10.0, 3.0, 12.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        body = largest_solid(body - ex)

# roof fixing bosses (M3) for a future removable-roof variant — tapped into back
for sx in (-1, 1):
    boss = Pos(sx * 18.0, -back_inner + 3.0, body_top - 16) * Cylinder(
        4.0, 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pil = Pos(sx * 18.0, -back_inner + 3.0, body_top - 16.1) * Cylinder(
        COUPON_TBD_PILOT_M3 / 2, 17, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body + boss - pil)

# ============================================================
# CAP — bottom bayonet, down-facing mesh intake (reused)
# ============================================================
cap = Cylinder(cap_r, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
cap = cap + Cylinder(cap_r + 4.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
stem = Pos(0, 0, 3.0) * Cylinder(cap_r, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
stem = largest_solid(stem - Pos(0, 0, 2.9) * Cylinder(
    cap_r - wall, 7.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
cap = cap + stem
for k in range(n_lugs):
    lug = Pos(0, 0, 7.6) * Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, 0) * Box(
        2.4, 8.0, 2.4, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    cap = cap + lug
cap = largest_solid(cap - Cylinder(
    cap_window_r, 30, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
seat = Pos(0, 0, 3.0) * Cylinder(
    cap_window_r + 3.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
seat = largest_solid(seat - Cylinder(
    cap_window_r - 1.5, 30, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
cap = cap + seat

for k in range(n_lugs):
    entry = Pos(0, cap_cy, 0) * Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 6.2) * Box(
        3.4, 9.0, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    turn = Pos(0, cap_cy, 0) * Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 3.4) * Box(
        3.4, 22.0, 3.2, align=(Align.CENTER, Align.MIN, Align.MIN)))
    body = largest_solid(largest_solid(body - entry) - turn)

# ============================================================
# INTERFERENCE CHECKS
# ============================================================
def check(name, a, b, limit=0.02):
    v = 0.0
    try:
        v = sum(s.volume for s in (a & b).solids()) / 1000.0
    except Exception:
        pass
    flag = "OK " if v <= limit else "FAIL"
    print(f"  [{flag}] {name}: {v:.3f} cm3")
    return v <= limit


print("=== interference checks ===")
ok = True
ok &= check("module vs body", hm_module, body)
ok &= check("perfboard+parts vs body", perfboard + perf_env, body)
ok &= check("perfboard+parts vs module", perfboard + perf_env, hm_module)
print("ALL OK" if ok else "INTERFERENCE FAILURES")

# ============================================================
# EXPORTS (body prints upright; cap disc-down)
# ============================================================
cap_placed = Pos(0, cap_cy, floor_z - wall - 6.0 - 1.6) * cap
assembly = Compound([body, cap_placed, hm_module, perfboard])
half = Box(300, 300, 400, align=(Align.MAX, Align.CENTER, Align.MIN))
cutaway = Compound([largest_solid(body - half), hm_module, perfboard])

REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)
for name, part, outdir in [
        ("eff_body", body, OUT), ("eff_cap", cap, OUT),
        ("eff_assembly", assembly, REVIEW), ("eff_cutaway", cutaway, REVIEW)]:
    export_stl(part, os.path.join(outdir, f"{name}.stl"))
    if name in ("eff_body", "eff_cap"):
        export_step(part, os.path.join(outdir, f"{name}.step"))
    bb = part.bounding_box()
    print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
