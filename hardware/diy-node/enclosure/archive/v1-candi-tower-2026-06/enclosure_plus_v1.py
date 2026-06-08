#!/usr/bin/env python3
"""Making Sense Bali — PLUS enclosure, functional build R1 "candi tower"
(ICD v1.3 + R1 revision, 2026-06-08).

R1: the body is the fractal. Stepped tower registers with projecting reveal
rings (each reveal = real rain shadow for the pierced band beneath it),
gently battered walls, 5-roof crest with PRINTABLE 42-degree conical roof
undersides, murda spire. Internals identical to the validated v1 layout
(all interference checks green): HM3301 vertical in front rails + pegs,
perfboard on back-wall standoffs, keyholes behind boards, bottom bayonet
cap (monthly service), crown on 2x M3 (deep service).

PRINT ORIENTATIONS (decided, not vibes):
  plus_body_print.stl   INVERTED (rim on bed): reveals become flat tops,
                        45-degree dome chamfer prints support-free
  plus_crown.stl        upright (skirt on bed): conical roof undersides
  plus_cap.stl          upright (disc on bed)

ALL FITS PLACEHOLDERS — COUPON_TBD_*, swap with measured numbers (ICD 5.1).
"""
import os
import math
from build123d import *  # noqa: F403

OUT = os.path.join(os.path.dirname(__file__), "..", "plus")
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
# SHELL / LAYOUT
# ============================================================
wall = 2.5
back_y = 16.0
inner_r = 35.5                  # frozen: cavity radius (module corner 35.34)
back_inner = back_y - wall

dome_h = 9.0                    # 45-degree chamfer ring (printable inverted)
floor_z = 12.0
body_top = 94.0
hm_z0 = 13.0
hm_carrier_y = 13.0
perf_back_gap = 4.0
perf_z0, perf_cx = 18.0, 0.0
key_x, key_z = 16.0, 64.0

# tower registers: (z_start, z_end, outer_r); reveals at the joints
registers = [
    (dome_h, 27.0, 39.6),
    (27.0, 44.0, 39.1),
    (44.0, 61.0, 38.6),
    (61.0, 78.0, 38.1),
    (78.0, body_top, 37.6),
]
reveal_proj = 3.2               # ring projection beyond its register
reveal_h = 4.2                  # ring height (chamfered top half)

cap_r = 27.0
cap_window_r = 16.0
n_lugs = 3

crown_base = body_top
crown_skirt_h = 8.0
n_roofs = 5
ratio = 0.84
eave0 = 47.0
roof_h0 = 5.4
band_h0 = 2.4
band_recess = 0.64
lip = 1.2
underside_deg = 42.0            # conical roof underside (support-free)
sp_h = 8.0


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


# ============================================================
# COMPONENT DUMMIES
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
# BODY — candi tower
# ============================================================
# stepped outer profile (revolved), battered registers
prof_pts = []
for (z0_, z1_, r_) in registers:
    prof_pts += [(r_, z0_), (r_, z1_)]
outer_edges = [Line(prof_pts[i], prof_pts[i + 1])
               for i in range(len(prof_pts) - 1)]
prof = make_face(
    [Line((0, dome_h), prof_pts[0])] + outer_edges +
    [Line(prof_pts[-1], (0, body_top)), Line((0, body_top), (0, dome_h))])
body = revolve(Plane.XZ * prof, Axis.Z)

# 45-degree dome chamfer ring: cap zone Ø(cap_r+3) at z0 to register0 at dome_h
dome_face = make_face([
    Line((cap_r + 3.0, 0), (registers[0][2], dome_h)),
    Line((registers[0][2], dome_h), (cap_r + 3.0, dome_h)),
    Line((cap_r + 3.0, dome_h), (cap_r + 3.0, 0)),
])
body = body + revolve(Plane.XZ * dome_face, Axis.Z)

# reveal rings at register joints (chamfer top, flat bottom = shadow shelf)
for (z0_, z1_, r_) in registers[1:]:
    rr = r_ + 0.5 + reveal_proj
    ring = make_face([
        Line((r_ - 1.0, z0_ - reveal_h), (rr, z0_ - reveal_h)),
        Line((rr, z0_ - reveal_h), (rr, z0_ - reveal_h / 2)),
        Line((rr, z0_ - reveal_h / 2), (r_ - 1.0, z0_ + reveal_h * 0.4)),
        Line((r_ - 1.0, z0_ + reveal_h * 0.4), (r_ - 1.0, z0_ - reveal_h)),
    ])
    body = body + revolve(Plane.XZ * ring, Axis.Z)

# flat back + cavity
body = back_cut(body, -back_y)
cavity = Pos(0, 0, floor_z - wall) * Cylinder(
    inner_r, body_top, align=(Align.CENTER, Align.CENTER, Align.MIN))
cavity = back_cut(cavity, -back_inner)
body = largest_solid(body - cavity)

# floor plate with cap opening
floor_plate = Pos(0, 0, floor_z - wall) * Cylinder(
    inner_r + 0.1, wall, align=(Align.CENTER, Align.CENTER, Align.MIN))
floor_plate = back_cut(floor_plate, -back_inner)
floor_plate = largest_solid(
    floor_plate - Cylinder(cap_r - 3.0, 100,
                           align=(Align.CENTER, Align.CENTER, Align.CENTER)))
body = body + floor_plate

# cap seat ring (bayonet)
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

# perfboard standoffs (M2 self-tap)
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

# keyholes
for sx in (-1, 1):
    kh = Pos(sx * key_x, 0, key_z) * Rot(-90, 0, 0) * Cylinder(
        4.0, 50, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    ks = Pos(sx * key_x, -back_y - 2, key_z) * Box(
        4.0, 10, 10, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = largest_solid(largest_solid(body - kh) - ks)

# USB-C exit chase
usb = Pos(0, 0, 18.0) * Rot(0, 0, 210) * (
    Pos(0, -42.0, 0) * Rot(35, 0, 0) * Cylinder(
        4.25, wall + 24, align=(Align.CENTER, Align.CENTER, Align.MIN)))
body = largest_solid(body - usb)

# fan grille: clover pair on can face (register 2, az 90)
for cz in (can_face_z0 + 12, can_face_z0 + 28):
    for f in clover(0, cz, 4.4):
        body = largest_solid(body - radial_cutter(f, 90, 44, wall + 9))

# pierced kawung bands under reveals 2..4 (front 100 deg, in reveal shadow)
vent_registers = [44.0, 61.0, 78.0]
for vz in vent_registers:
    for az in (60, 90, 120):
        for f in clover(0, vz - reveal_h - 4.5, 3.4):
            body = largest_solid(body - radial_cutter(f, az, 44, wall + 9))

# crown bosses (M3)
for sx in (-1, 1):
    boss = Pos(sx * 24.0, -back_inner + 3.0, body_top - 14) * Cylinder(
        4.5, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pil = Pos(sx * 24.0, -back_inner + 3.0, body_top - 14.1) * Cylinder(
        COUPON_TBD_PILOT_M3 / 2, 15,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body + boss - pil)

# ============================================================
# CROWN — printable roofs (conical undersides)
# ============================================================
def roof_solid(r_apex, r_eave, h, z_base):
    """Ogee top, 42-deg conical underside rising inward from the eave."""
    rise = (r_eave - r_apex) * math.tan(math.radians(90 - underside_deg))
    zt = z_base + h + lip
    mid = (r_apex + (r_eave - r_apex) * 0.45, zt - h * 0.58)
    z_under_apex = min(z_base + rise, zt - 1.0)
    face = make_face([
        Line((0, zt), (r_apex, zt)),
        Spline((r_apex, zt), mid, (r_eave, z_base + lip)),
        Line((r_eave, z_base + lip), (r_eave, z_base)),
        Line((r_eave, z_base), (r_apex, z_under_apex)),     # conical underside
        Line((r_apex, z_under_apex), (0, z_under_apex)),
        Line((0, z_under_apex), (0, zt)),
    ])
    return revolve(Plane.XZ * face, Axis.Z)


eaves = [eave0 * ratio**i for i in range(n_roofs)]
bands = [e * band_recess for e in eaves[1:]]
rhs = [roof_h0 * ratio**i for i in range(n_roofs)]
bhs = [band_h0 * ratio**i for i in range(n_roofs - 1)]

crown = Pos(0, 0, crown_base - crown_skirt_h) * Cylinder(
    37.6 + wall + COUPON_TBD_SLIDE, crown_skirt_h,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
z = crown_base
pierce_jobs = []
for i in range(n_roofs):
    r_apex = bands[i] if i < len(bands) else 6.5
    crown = crown + roof_solid(r_apex, eaves[i], rhs[i], z)
    z += rhs[i] + lip
    if i < len(bands):
        crown = crown + Pos(0, 0, z) * Cylinder(
            bands[i], bhs[i], align=(Align.CENTER, Align.CENTER, Align.MIN))
        if i < 2:
            pierce_jobs.append((bands[i], z + bhs[i] / 2, bhs[i]))
        z += bhs[i]
sp = make_face([
    Spline((6.5, 0), (2.4, sp_h * 0.42), (0.01, sp_h)),
    Line((0.01, sp_h), (0, sp_h)), Line((0, sp_h), (0, 0)),
    Line((0, 0), (6.5, 0)),
])
crown = crown + Pos(0, 0, z) * revolve(Plane.XZ * sp, Axis.Z)
crown_top_solid = z

# chimney cavity (to band2) + skirt void
cav = Pos(0, 0, crown_base - crown_skirt_h - 0.1) * Cylinder(
    37.6 + COUPON_TBD_SLIDE, crown_skirt_h + 0.1,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
zc = crown_base
for i in range(min(3, n_roofs)):
    seg_top = zc + rhs[i] + lip + (bhs[i] if i < len(bhs) else 0)
    r_in = (bands[i] if i < len(bands) else 8.0) - wall
    cav = cav + Pos(0, 0, zc - 0.05) * Cylinder(
        max(r_in, 6.0), seg_top - zc + 0.05,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    zc = seg_top
crown = largest_solid(crown - cav)
crown = back_cut(crown, -back_y)
# back wall trimmed to the crown's stepped SILHOUETTE (billboard lesson:
# a full-width slab reads as a rectangle behind the diminishing roofs)
back_wall = Pos(0, -back_y, crown_base) * Box(
    100, wall, crown_top_solid - crown_base,
    align=(Align.CENTER, Align.MIN, Align.MIN))
env = Pos(0, 0, crown_base - crown_skirt_h) * Cylinder(
    37.6 + wall + COUPON_TBD_SLIDE, crown_skirt_h,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
ze = crown_base
for i in range(n_roofs):
    env = env + Pos(0, 0, ze) * Cylinder(
        eaves[i], rhs[i] + lip, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ze += rhs[i] + lip
    if i < len(bands):
        env = env + Pos(0, 0, ze) * Cylinder(
            bands[i], bhs[i], align=(Align.CENTER, Align.CENTER, Align.MIN))
        ze += bhs[i]
env = env + Pos(0, 0, ze) * Cylinder(
    6.5, sp_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
back_wall = largest_solid(back_wall & env)
crown = crown + back_wall

for (br, bz, bh_) in pierce_jobs:
    s = max(min(bh_ * 0.42, 2.4), 1.5)
    for az in (60, 90, 120):
        for f in clover(0, bz, s):
            crown = largest_solid(crown - radial_cutter(f, az, br + 2, wall + 5))

for sx in (-1, 1):
    th = Pos(sx * 24.0, -back_inner + 3.0, crown_base - 20) * Cylinder(
        1.7, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    crown = largest_solid(crown - th)

# ============================================================
# CAP
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

# L-slots in body cap seat
for k in range(n_lugs):
    entry = Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 6.2) * Box(
        3.4, 9.0, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    turn = Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 3.4) * Box(
        3.4, 22.0, 3.2, align=(Align.CENTER, Align.MIN, Align.MIN)))
    body = largest_solid(largest_solid(body - entry) - turn)

# ============================================================
# INTERFERENCE CHECKS
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
ok &= check("module vs crown", hm_module, crown)
ok &= check("perfboard+parts vs body", perfboard + perf_env, body)
ok &= check("perfboard+parts vs module", perfboard + perf_env, hm_module)
ok &= check("crown vs body (assembled)", crown, body, limit=0.6)
print("ALL OK" if ok else "INTERFERENCE FAILURES — fix before trusting STLs")

# ============================================================
# EXPORTS (incl. print-oriented body: inverted, z-min at 0)
# ============================================================
cap_placed = Pos(0, 0, floor_z - wall - 6.0 - 1.6) * cap
assembly = Compound([body, crown, cap_placed, hm_module, perfboard])
half = Box(300, 300, 400, align=(Align.MAX, Align.CENTER, Align.MIN))
cutaway = Compound([largest_solid(body - half),
                    largest_solid(crown - half),
                    hm_module, perfboard])

body_print = Rot(180, 0, 0) * body
bbp = body_print.bounding_box()
body_print = Pos(0, 0, -bbp.min.Z) * body_print

crown_print = Pos(0, 0, -(crown_base - crown_skirt_h)) * crown

REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)
for name, part, outdir in [
        ("plus_body", body, OUT), ("plus_body_print", body_print, OUT),
        ("plus_crown", crown_print, OUT), ("plus_cap", cap, OUT),
        ("plus_assembly", assembly, REVIEW),   # review-only: interpenetrating
        ("plus_cutaway", cutaway, REVIEW)]:    # dummies, exempt from strict
    export_stl(part, os.path.join(outdir, f"{name}.stl"))
    if name in ("plus_body", "plus_crown", "plus_cap"):
        export_step(part, os.path.join(outdir, f"{name}.step"))
    bb = part.bounding_box()
    print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
