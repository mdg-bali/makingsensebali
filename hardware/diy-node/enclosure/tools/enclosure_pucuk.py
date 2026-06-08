#!/usr/bin/env python3
"""Making Sense Bali — PLUS enclosure, C1 "Pucuk" (ICD 1.4-DRAFT, 2026-06-08).

A twisted faceted shard: stacked octagonal sections rotate (twist) and shrink
as they rise, ruled-lofted so every side facet is a flat triangle-pair — the
"semi-organic digital" skin Tomas asked for. Converges to a sealed faceted
finial that side-vents the chimney near the top (exhaust high, NO up-aperture).
Open at the bottom; one bottom bayonet cap closes it, carries the down-facing
mesh intake + USB drip exit, and is the monthly-service opening. Two parts
total (body + cap) — the fewest-parts promise of C1.

Internals are the VALIDATED candi-tower layout, transplanted unchanged (same
Z-up frame, flat back at y=-back_y, inner_r cavity, frozen component dummies):
HM3301 vertical in front C-rails + 2 registration pegs, perfboard on back-wall
standoffs, keyholes behind the boards, bottom bayonet cap.

PRINT ORIENTATION: UPRIGHT (open rim on bed, finial up). Twisted facets stay
near-vertical; the spire narrows going up (self-supporting); louvers are the
only overhang and are capped at LOUVER_SLOPE_DEG — section-print to confirm.

ALL FITS PLACEHOLDERS — COUPON_TBD_*, swap with measured numbers (ICD 5.1).
NOTE (open): boards load from the BOTTOM through the Ø~48 cap opening — rehearse
on the first print; if it fights, pass 2 promotes the finial to a removable cap.
"""
import os
import math
from build123d import *  # noqa: F403

OUT = os.path.join(os.path.dirname(__file__), "..", "pucuk")
os.makedirs(OUT, exist_ok=True)

# ============================================================
# COUPON-TBD FIT PARAMETERS (ICD 5.1) — placeholders, PETG-conservative
# ============================================================
COUPON_TBD_SLIDE = 0.30
COUPON_TBD_FREE = 0.45
COUPON_TBD_PRESS = -0.05
COUPON_TBD_PILOT_M2 = 1.75
COUPON_TBD_PILOT_M3 = 2.65

# ============================================================
# FROZEN COMPONENT DIMENSIONS (ICD 2)
# ============================================================
perf_w, perf_h, perf_t = 40.0, 60.0, 1.6
hm_w, hm_h, hm_t = 40.0, 80.0, 1.6
can_w, can_h, can_d = 38.0, 40.0, 15.2
hm_hole_d = 3.2

# ============================================================
# SHELL / LAYOUT  (Z up; +Y = front, flat back at y=-back_y)
# ============================================================
wall = 2.5
back_y = 16.0
inner_r = 35.5                  # frozen: cavity radius (module corner 35.34)
back_inner = back_y - wall

floor_z = 12.0
hm_z0 = 13.0
hm_carrier_y = 13.0
perf_back_gap = 4.0
perf_z0, perf_cx = 18.0, 0.0
key_x, key_z = 16.0, 64.0

# twisted faceted shell
N = 8                           # octagon
TWIST_DEG = 85.0                # legible spiral; ~25 deg facet lean at r38 (printable)
BASE_ROT = 22.5                 # a facet center faces +Y (front) at the base
Z0 = 6.0                        # bottom rim (slight drip kick)
ZTOP = 132.0                    # finial point
CAV_TOP = 96.0                  # top of straight cavity (clears 80 mm carrier)
NECK_TOP = 118.0                # chimney neck closes here; finial solid above

# (z, inradius) profile of the outer octagon sections
shell_profile = [
    (6.0, 40.0),                # base, proud -> drip edge
    (12.0, 38.0),               # floor / wall start
    (42.0, 38.0),               # facet seams grade tighter going up (fractal)
    (66.0, 38.0),
    (84.0, 38.0),
    (96.0, 37.0),               # top of component zone -> begin neck
    (110.0, 29.0),
    (120.0, 17.0),
    (128.0, 8.0),
    (132.0, 1.4),               # near-point finial (non-degenerate)
]

LOUVER_SLOPE_DEG = 0.0          # pass 1: straight slots; tilt added after coupons
cap_r = 27.0
cap_window_r = 16.0
n_lugs = 3


# ============================================================
# HELPERS (from validated candi build)
# ============================================================
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


def radial_cutter(profile_face, az_deg, r_from, depth):
    f = Plane.XZ.offset(-r_from) * profile_face
    cut = extrude(f, amount=depth)
    return Rot(0, 0, az_deg - 90.0) * cut


def clover(cx, cz, s):
    lobes = []
    for ang in (0, 90):
        e = Ellipse(s * 1.45, s * 0.62)
        lobes.append(Pos(cx, cz, 0) * Rot(0, 0, ang + 45) * e)
    return lobes + [Pos(cx, cz, 0) * Circle(s * 0.42)]


def rot_at(z):
    return BASE_ROT + TWIST_DEG * (z - Z0) / (ZTOP - Z0)


def facet_az(z, target=90.0):
    """Nearest octagon facet-centre azimuth to `target` at height z."""
    base = rot_at(z) + 22.5
    k = round((target - base) / (360.0 / N))
    return base + (360.0 / N) * k


def slot_face(zc, w, h):
    return make_face([
        Line((-w / 2, zc - h / 2), (w / 2, zc - h / 2)),
        Line((w / 2, zc - h / 2), (w / 2, zc + h / 2)),
        Line((w / 2, zc + h / 2), (-w / 2, zc + h / 2)),
        Line((-w / 2, zc + h / 2), (-w / 2, zc - h / 2)),
    ])


# ============================================================
# COMPONENT DUMMIES (frozen, ICD 2)
# ============================================================
hm_carrier = Pos(0, hm_carrier_y, hm_z0) * Box(
    hm_w, hm_t, hm_h, align=(Align.CENTER, Align.MIN, Align.MIN))
hm_can = Pos(0, hm_carrier_y + hm_t, hm_z0 + (hm_h - can_h) / 2) * Box(
    can_w, can_d, can_h, align=(Align.CENTER, Align.MIN, Align.MIN))
hm_module = hm_carrier + hm_can
can_face_z0 = hm_z0 + (hm_h - can_h) / 2          # 33.0

perf_y0 = -back_inner + perf_back_gap
perfboard = Pos(perf_cx, perf_y0, perf_z0) * Box(
    perf_w, perf_t, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
perf_env = Pos(perf_cx, perf_y0 + perf_t, perf_z0) * Box(
    perf_w, 12.0, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))


# ============================================================
# BODY — twisted faceted shard
# ============================================================
def octa(z, inr, rot):
    circ = inr / math.cos(math.pi / N)            # inradius -> circumradius
    return Pos(0, 0, z) * RegularPolygon(circ, N, rotation=rot)


sections = [octa(z, inr, rot_at(z)) for (z, inr) in shell_profile]
outer = loft(sections, ruled=True)

# faceted inner cavity (octagon offset inward ~wall): constant wall, hollows the
# facet corners the round cavity left solid -> lighter. Clears components
# (octagon inradius = inner_r; corners sit outside the R=inner_r module envelope).
inner_profile = [
    (floor_z - wall, inner_r),
    (12.0, inner_r),
    (42.0, inner_r),
    (66.0, inner_r),
    (84.0, inner_r),
    (CAV_TOP, inner_r - 1.0),
]
cavity = loft([octa(z, inr, rot_at(z)) for (z, inr) in inner_profile], ruled=True)
neck = revolve(Plane.XZ * make_face([      # round neck, overlaps cavity top
    Line((inner_r, CAV_TOP - 2.0), (5.0, NECK_TOP)),
    Line((5.0, NECK_TOP), (0, NECK_TOP)),
    Line((0, NECK_TOP), (0, CAV_TOP - 2.0)),
    Line((0, CAV_TOP - 2.0), (inner_r, CAV_TOP - 2.0)),
]), Axis.Z)
cavity = cavity + neck
cavity = back_cut(cavity, -back_inner)

body = back_cut(outer, -back_y)                   # flat back against wall
body = largest_solid(body - cavity)

# floor plate with the cap opening
floor_plate = Pos(0, 0, floor_z - wall) * Cylinder(
    inner_r + 0.1, wall, align=(Align.CENTER, Align.CENTER, Align.MIN))
floor_plate = back_cut(floor_plate, -back_inner)
floor_plate = largest_solid(
    floor_plate - Cylinder(cap_r - 3.0, 100,
                           align=(Align.CENTER, Align.CENTER, Align.CENTER)))
body = body + floor_plate

# cap seat ring (bayonet) — reused verbatim
cap_seat = Pos(0, 0, floor_z - wall - 6.0) * Cylinder(
    cap_r + wall + COUPON_TBD_SLIDE, 6.0,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
cap_seat = largest_solid(
    cap_seat - Pos(0, 0, floor_z - wall - 6.1) * Cylinder(
        cap_r + COUPON_TBD_SLIDE, 6.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN)))
body = body + cap_seat

# HM3301 rails + registration pegs
rail_gap = hm_t + COUPON_TBD_SLIDE
for sx in (-1, 1):
    post = Pos(sx * (hm_w / 2 + 2.0), hm_carrier_y + rail_gap / 2, hm_z0 - 1) * Box(
        4.0, rail_gap + 5.0, hm_h + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    slot = Pos(sx * (hm_w / 2 - 1.0), hm_carrier_y - 0.05, hm_z0 - 1.5) * Box(
        6.0, rail_gap, hm_h + 4.0,
        align=(Align.CENTER, Align.MIN, Align.MIN))
    body = largest_solid(body + post - slot)
for sx in (-1, 1):
    peg = Pos(sx * 16.0, hm_carrier_y - 0.02, hm_z0 + 4.0) * Rot(-90, 0, 0) * \
        Cylinder((hm_hole_d + COUPON_TBD_PRESS) / 2, hm_t + 1.2,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body + peg

# perfboard standoffs (M2 self-tap) against the back wall
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
usb = Pos(0, 0, 18.0) * Rot(0, 0, 210) * (
    Pos(0, -42.0, 0) * Rot(35, 0, 0) * Cylinder(
        4.25, wall + 24, align=(Align.CENTER, Align.CENTER, Align.MIN)))
body = largest_solid(body - usb)

# fan grille: clover pair on the can face, on the front facet at the can height
for cz in (can_face_z0 + 12, can_face_z0 + 28):
    az = facet_az(cz, 90.0)
    for f in clover(0, cz, 4.4):
        body = largest_solid(body - radial_cutter(f, az, 44, wall + 11))

# louvers = the skin's rhythm: fractal-graded bands (slot height shrinks going
# up), intake low (below the can, near the chimney foot), exhaust high in the
# neck. Front + sides only; back stays solid against the wall. Cut from well
# outside (r_from=60) deep enough to always open into the cavity.
louver_bands = [
    (16.0, 3.4, (90, 45, 135)),     # intake, low
    (24.0, 2.9, (67.5, 112.5)),
    (31.0, 2.5, (90, 45, 135)),
    (100.0, 3.0, (90, 45, 135)),    # exhaust, neck
    (108.0, 2.6, (67.5, 112.5)),
    (115.0, 2.2, (90, 45, 135)),
]
for zc, h, targets in louver_bands:
    for t in targets:
        az = facet_az(zc, float(t))
        body = largest_solid(
            body - radial_cutter(slot_face(zc, 15.0, h), az, 60.0, 56.0))

# ============================================================
# CAP  (reused verbatim from the validated candi bayonet)
# ============================================================
cap = Cylinder(cap_r, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
cap = cap + Cylinder(cap_r + 4.0, 1.6,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
stem = Pos(0, 0, 3.0) * Cylinder(
    cap_r, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
stem = largest_solid(stem - Pos(0, 0, 2.9) * Cylinder(
    cap_r - wall, 7.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
cap = cap + stem
for k in range(n_lugs):
    lug = Pos(0, 0, 7.6) * Rot(0, 0, k * 120) * (
        Pos(cap_r + 1.2, 0, 0) * Box(
            2.4, 8.0, 2.4, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    cap = cap + lug
cap = largest_solid(cap - Cylinder(
    cap_window_r, 30, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
seat = Pos(0, 0, 3.0) * Cylinder(
    cap_window_r + 3.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
seat = largest_solid(seat - Cylinder(
    cap_window_r - 1.5, 30, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
cap = cap + seat

# L-slots in the body cap seat (bayonet receivers)
for k in range(n_lugs):
    entry = Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 6.2) * Box(
        3.4, 9.0, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    turn = Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 3.4) * Box(
        3.4, 22.0, 3.2, align=(Align.CENTER, Align.MIN, Align.MIN)))
    body = largest_solid(largest_solid(body - entry) - turn)

# ============================================================
# INTERFERENCE CHECKS (ICD gate)
# ============================================================
def check(name, a, b, limit=0.02):
    inter = a & b
    v = 0.0
    try:
        v = sum(s.volume for s in inter.solids()) / 1000.0
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
print("ALL OK" if ok else "INTERFERENCE FAILURES — fix before trusting STLs")

# ============================================================
# EXPORTS  (body prints upright: open rim on bed, finial up)
# ============================================================
cap_placed = Pos(0, 0, floor_z - wall - 6.0 - 1.6) * cap
assembly = Compound([body, cap_placed, hm_module, perfboard])
half = Box(300, 300, 400, align=(Align.MAX, Align.CENTER, Align.MIN))
cutaway = Compound([largest_solid(body - half), hm_module, perfboard])

body_print = body  # already upright; open rim sits at z = floor_z-wall-6

REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)
for name, part, outdir in [
        ("pucuk_body", body, OUT),
        ("pucuk_cap", cap, OUT),
        ("pucuk_assembly", assembly, REVIEW),    # review-only: interpenetrating
        ("pucuk_cutaway", cutaway, REVIEW)]:      # dummies, exempt from strict
    export_stl(part, os.path.join(outdir, f"{name}.stl"))
    if name in ("pucuk_body", "pucuk_cap"):
        export_step(part, os.path.join(outdir, f"{name}.step"))
    bb = part.bounding_box()
    print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")

# ============================================================
# SECTION TEST PRINTS — cheap plastic before any full body (ICD gate 4)
#   base: bayonet L-slots + floor + rail roots + intake louver overhangs
#   neck: exhaust louver overhangs + converging finial tip
# Pair the base section with pucuk_cap to test the bayonet (clearance is the
# COUPON_TBD_SLIDE placeholder — reprint this ring once §5.1 is measured).
# ============================================================
SEC = os.path.join(OUT, "sections")
os.makedirs(SEC, exist_ok=True)


def zslab(lo, hi):
    return Pos(0, 0, lo) * Box(
        300, 300, hi - lo, align=(Align.CENTER, Align.CENTER, Align.MIN))


sec_base = largest_solid(body & zslab(0.0, 42.0))
sec_neck = largest_solid(body & zslab(92.0, 133.0))
nb = sec_neck.bounding_box()
sec_neck = Pos(0, 0, -nb.min.Z) * sec_neck          # drop to bed
for nm, prt in [("pucuk_sec_base", sec_base), ("pucuk_sec_neck", sec_neck)]:
    export_stl(prt, os.path.join(SEC, f"{nm}.stl"))
    bb = prt.bounding_box()
    print(f"{nm}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
