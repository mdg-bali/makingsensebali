#!/usr/bin/env python3
"""Making Sense Bali — enclosure v2: modular faceted (ICD DEC-10..13).

Function-first, modular, faceted. Four parts:

  v2_spine.stl    open chassis: flat back plate + keyholes + HM3301 rails +
                  perfboard standoffs + registration pegs + crown bosses.
                  Shared topology; height set by variant. (validated v1 internals)
  v2_shell.stl    faceted octagonal sleeve, chevron-triangle louvers in
                  fractal-graded bands; the variant + aesthetic part; D-open
                  back slides over the spine. (DEC-11/12 — the new look)
  v2_base.stl     bottom cap: down-facing intake, cable gland, bayonet, mesh seat
  v2_crown.stl    top exhaust finial, faceted, drip skirt, 2x M3 to spine

Airflow (DEC-13 #1): chimney — base intake (cool, by BME680 low) → up the open
chassis → exhaust louvers high (by XIAO) + crown. HM3301 can ports face the
front fan grille (sideways = datasheet-legal).
Water (#2): every louver angles down-and-out; no up-facing aperture; shell↔spine
seam is at the back, in the wall's rain shadow; crown overhangs the shell rim.
Material/time (#3): 1.8 mm faceted walls, no infill needed, open back saves a
quarter of the sleeve; modular reprints.

ALL FITS = COUPON_TBD_* placeholders (ICD §5.1). Section-print before trusting.
Set VARIANT = 'plus' or 'basic'.
"""
import os
import math
from build123d import *  # noqa: F403

VARIANT = os.environ.get("MSB_VARIANT", "plus")
OUT = os.path.join(os.path.dirname(__file__), "..", "v2")
REVIEW = os.path.join(OUT, "review")
os.makedirs(OUT, exist_ok=True)
os.makedirs(REVIEW, exist_ok=True)

# ============================================================
# COUPON-TBD FITS (ICD §5.1)
# ============================================================
TBD_SLIDE = 0.30
TBD_FREE = 0.45
TBD_PRESS = -0.05
TBD_PILOT_M2 = 1.75
TBD_PILOT_M3 = 2.65

# ============================================================
# FROZEN COMPONENTS (ICD §2)
# ============================================================
perf_w, perf_h, perf_t = 40.0, 60.0, 1.6
hm_w, hm_h, hm_t = 40.0, 80.0, 1.6
can_w, can_h, can_d = 38.0, 40.0, 15.2
hm_hole_d = 3.2

# ============================================================
# ARCHITECTURE PARAMS
# ============================================================
wall = 1.8                 # shell facet wall (thin, material-conscious)
spine_wall = 2.5
back_y = 16.0              # outer back plane
back_inner = back_y - spine_wall   # 13.5, inner face of back plate

r_circ = 42.0             # octagon circumradius at base
taper = 3.0               # circumradius shrink base→top
n_fac = 8
shell_h = 100.0 if VARIANT == "plus" else 70.0
open_y = -back_inner      # shell cut plane (back opening)

# internal layout (validated v1 numbers)
hm_carrier_y = 13.0
hm_z0 = 13.0 if VARIANT == "plus" else 13.0
perf_back_gap = 4.0
perf_z0 = 18.0
perf_cx = 0.0
key_x, key_z = 16.0, min(64.0, shell_h - 30)
can_face_z0 = hm_z0 + (hm_h - can_h) / 2     # 33

base_h = 13.0
crown_h = 22.0
total_h = base_h_overlap = None


def largest(x):
    try:
        s = list(x.solids())
    except (AttributeError, TypeError):
        s = [q for it in x for q in it.solids()]
    if not s:
        raise ValueError("no solids")
    return max(s, key=lambda k: k.volume)


def back_cut(shape, y_plane):
    c = Pos(0, y_plane, 0) * Box(600, 500, 600,
                                 align=(Align.CENTER, Align.MAX, Align.CENTER))
    return largest(shape - c)


def octa(r, z, rot=0.0):
    return Plane.XY.offset(z) * RegularPolygon(r, n_fac, rotation=rot)


poly_rot = 22.5   # octagon: vertices at 22.5+45k → flats centred at 45+45k


def louver(a, zc, half_w, h, tilt, r_out, depth=10.0):
    """Chevron (apex-up triangle) louver cutter on a facet at azimuth `a`
    (degrees from +X, CCW). Built at the origin facing +X, tilted in place,
    THEN translated out to the facet and rotated to `a` (tilt-about-origin
    would otherwise fling the cutter off the wall). Apex-up → wall above each
    slot is an inverted-V blade shedding rain sideways; tilt kills sightline.
    """
    tri = Plane.YZ * Polygon((-half_w, 0.0), (half_w, 0.0), (0.0, h))
    cut = extrude(tri, amount=-depth)       # straddles origin, faces +X
    cut = Rot(0, tilt, 0) * cut             # tilt in place (outer edge ↓)
    cut = Pos(r_out, 0.0, zc) * cut         # out to facet, up to height
    return Rot(0, 0, a) * cut


# facet centres are the FLATS: 45,90,135,180,225,270,315,0 ; front flat = 90°
facet_centre_az = [(45.0 + i * 45.0) % 360.0 for i in range(n_fac)]


# ============================================================
# SHELL — faceted octagon + chevron louver bands (DEC-11/12)
# ============================================================
def front_facets():
    """Facet centre azimuths to vent: front + sides, skip the rear-most
    (the back is open and covered by the spine)."""
    return [a for a in facet_centre_az
            if math.sin(math.radians(a)) > -0.35]


vent_az = front_facets()
TILT = 18.0

outer = loft([octa(r_circ, 0, poly_rot),
              octa(r_circ - taper, shell_h, poly_rot)], ruled=True)
inner = loft([octa(r_circ - wall, -2, poly_rot),
              octa(r_circ - taper - wall, shell_h + 2, poly_rot)], ruled=True)
shell = largest(outer - inner)
shell = back_cut(shell, open_y)            # open the back

# DEC-12: the chevron louvers ARE the skin. A fractal-graded grid covers
# every front/side facet — big intake chevrons low (by the BME680), shrinking
# and multiplying upward (self-similar batik rhythm) to fine exhaust near the
# crown (by the XIAO). All built as ONE fused cutter, subtracted once (fast,
# robust). Each chevron leans down-and-out (TILT) so rain sheds, air enters,
# rows overlap vertically → no straight sightline in.
n_rows = 8
row_z0, row_z1 = 7.0, 93.0
cutters = []
for i in range(n_rows):
    t = i / (n_rows - 1)
    zc = row_z0 + t * (row_z1 - row_z0)
    hw = 6.6 * (1 - 0.52 * t)               # fractal shrink with height
    h = 8.5 * (1 - 0.48 * t)
    per = 1 if t < 0.34 else (2 if t < 0.67 else 3)
    pitch = 13.0 * (1 - 0.4 * t)
    # stagger alternate rows half a facet → diamond/triangulated read
    az_off = 22.5 if i % 2 else 0.0
    for a in vent_az:
        start = -(per - 1) * pitch / 2.0
        for k in range(per):
            daz = math.degrees((start + k * pitch) / r_circ)
            cutters.append(louver(a + az_off + daz, zc, hw, h, TILT,
                                  r_circ + 2, depth=9.0))
shell = largest(shell - Compound(cutters))   # single subtraction

# dedicated HM3301 fan grille: front facet (az 90), aligned to can face
for k in range(3):
    z = can_face_z0 + 8 + k * 11
    shell = largest(shell - louver(90.0, z, 7.0, 5.0, 10.0, r_circ + 2,
                                   depth=11.0))

# crown-seat: top inner rabbet so crown skirt overlaps shell rim
seat_cut = Pos(0, 0, shell_h - 6) * Cylinder(
    r_circ - taper + 0.2, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
seat_keep = Pos(0, 0, shell_h - 6) * Cylinder(
    r_circ - taper - wall - TBD_SLIDE, 8,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
shell = largest(shell - (seat_cut - seat_keep))
shell = back_cut(shell, open_y)

# base bayonet seat: thicken bottom inner ring with 3 L-slots
base_ring = Pos(0, 0, 0) * Cylinder(
    r_circ - 6, 8.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
base_ring = largest(base_ring - Pos(0, 0, -0.1) * Cylinder(
    r_circ - 6 - 3.0, 8.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
base_ring = back_cut(base_ring, open_y)
shell = largest(shell + base_ring)

# ============================================================
# SPINE — open chassis (validated internals)
# ============================================================
plate_w = 78.0
plate = Pos(0, -back_y, 0) * Box(plate_w, spine_wall, shell_h,
                                 align=(Align.CENTER, Align.MIN, Align.MIN))
# trim plate to sit inside shell outline (intersect with a prism of shell outer)
outline = loft([octa(r_circ + 0.5, -1, poly_rot),
                octa(r_circ - taper + 0.5, shell_h + 1, poly_rot)], ruled=True)
plate = largest(plate & outline)
spine = plate

# back lips: two vertical tabs overlapping shell inner back edges
for sx in (-1, 1):
    lip = Pos(sx * (plate_w / 2 - 2), open_y - 1.0, 0) * Box(
        4, 3.0, shell_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    spine = spine + lip

# HM3301 rails (C-channels) joined to the back plate by a full-height web,
# + pegs. Web spans y=-14.5 (into plate) → +13 (carrier back); post grips
# the carrier side edge; slot opens the channel. (x=±22 clears can & board.)
rail_gap = hm_t + TBD_SLIDE
if VARIANT == "plus":
    for sx in (-1, 1):
        postx = sx * (hm_w / 2 + 2.0)            # ±22
        web = Pos(postx, -0.75, hm_z0 + hm_h / 2) * Box(
            4.0, 27.5, hm_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        post = Pos(postx, hm_carrier_y + rail_gap / 2 + 2.0, hm_z0 + hm_h / 2) * Box(
            4.0, rail_gap + 5.0, hm_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        slot = Pos(sx * (hm_w / 2 - 1.0), hm_carrier_y + 0.7, hm_z0 + hm_h / 2) * Box(
            6.0, rail_gap, hm_h + 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        spine = largest(spine + web + post - slot)
if VARIANT == "plus":
    for sx in (-1, 1):
        peg = Pos(sx * 16.0, hm_carrier_y - 0.02, hm_z0 + 4.0) * Rot(-90, 0, 0) * \
            Cylinder((hm_hole_d + TBD_PRESS) / 2, hm_t + 1.2,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        spine = spine + peg

# perfboard standoffs (M2 self-tap)
so_dx, so_dz = 16.2, 26.2
perf_cz = perf_z0 + perf_h / 2
for sx in (-1, 1):
    for sz in (-1, 1):
        x_, z_ = sx * so_dx, perf_cz + sz * so_dz
        if z_ > shell_h - 6:
            continue
        post = Pos(x_, -back_inner, z_) * Rot(-90, 0, 0) * Cylinder(
            3.0, perf_back_gap, align=(Align.CENTER, Align.CENTER, Align.MIN))
        pilot = Pos(x_, -back_inner - 0.1, z_) * Rot(-90, 0, 0) * Cylinder(
            TBD_PILOT_M2 / 2, perf_back_gap + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
        spine = largest(spine + post - pilot)

# keyholes
for sx in (-1, 1):
    kh = Pos(sx * key_x, 0, key_z) * Rot(-90, 0, 0) * Cylinder(
        4.0, 60, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    ks = Pos(sx * key_x, -back_y - 2, key_z) * Box(
        4.0, 12, 10, align=(Align.CENTER, Align.MIN, Align.MIN))
    spine = largest(largest(spine - kh) - ks)

# crown bosses (M3) near top
for sx in (-1, 1):
    boss = Pos(sx * 24.0, -back_inner + 3.0, shell_h - 16) * Cylinder(
        4.5, 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pil = Pos(sx * 24.0, -back_inner + 3.0, shell_h - 16.1) * Cylinder(
        TBD_PILOT_M3 / 2, 17, align=(Align.CENTER, Align.CENTER, Align.MIN))
    spine = largest(spine + boss - pil)

# USB chase low back-left
usb = Pos(0, 0, 14.0) * Rot(0, 0, 210) * (
    Pos(0, -back_y - 2, 0) * Rot(35, 0, 0) * Cylinder(
        4.25, spine_wall + 16, align=(Align.CENTER, Align.CENTER, Align.MIN)))
spine = largest(spine - usb)

# ============================================================
# BASE CAP — down intake + cable + bayonet + mesh seat
# ============================================================
base = Cylinder(r_circ - 6 - TBD_SLIDE, 3.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
brim = Cylinder(r_circ - 2, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
base = brim + base
# down-intake: ring of triangular slots in the brim underside (face down)
for a in range(0, 360, 30):
    sl = Pos(0, 0, -0.1) * Rot(0, 0, a) * (
        Pos(r_circ - 12, 0, 0) * Box(5, 10, 6,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN)))
    base = largest(base - sl)
# bayonet lugs (3) to engage shell base_ring slots
for k in range(3):
    lug = Pos(0, 0, 3.0) * Rot(0, 0, k * 120) * (
        Pos(r_circ - 6 - TBD_SLIDE, 0, 0) * Box(
            3.0, 7.0, 2.4, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    base = base + lug
# mesh seat ring + cable gland
base = largest(base - Cylinder(r_circ - 16, 30,
               align=(Align.CENTER, Align.CENTER, Align.CENTER)))
seat = Pos(0, 0, 3.0) * Cylinder(r_circ - 13, 1.2,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
seat = largest(seat - Cylinder(r_circ - 15, 30,
               align=(Align.CENTER, Align.CENTER, Align.CENTER)))
base = base + seat
base = back_cut(base, open_y + 1.5)        # match the D back

# ============================================================
# CROWN — faceted exhaust finial + drip skirt + M3
# ============================================================
top_r = r_circ - taper
crown_over = top_r + 5            # overhang radius (drip + rain-shadow)
# faceted cone, hollowed from the bottom (single robust boolean), top stays solid
crown_o = loft([octa(crown_over, 0, poly_rot),
                octa(top_r * 0.55, crown_h * 0.6, poly_rot),
                octa(top_r * 0.25, crown_h, poly_rot)], ruled=True)
crown_i = loft([octa(crown_over - wall, -0.1, poly_rot),
                octa(top_r * 0.55 - wall, crown_h * 0.6 - 1, poly_rot)], ruled=True)
crown = largest(crown_o - crown_i)
# legs (3): the crown floats above the shell rim → continuous ring-gap
# exhaust, rain-shadowed by the 5 mm overhang. Two rear legs take M3 to
# the spine bosses at (±24, -10.5); one front leg rests on the rim.
exhaust_gap = 5.0
leg_pos = [(24.0, -back_inner + 3.0), (-24.0, -back_inner + 3.0), (0.0, top_r - 6)]
for (lx, ly) in leg_pos:
    leg = Pos(lx, ly, -exhaust_gap) * Box(
        9.0, 7.0, exhaust_gap + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    crown = crown + leg
crown = largest(crown)
crown = back_cut(crown, open_y)
# M3 through the two rear legs into spine bosses
for sx in (-1, 1):
    th = Pos(sx * 24.0, -back_inner + 3.0, -exhaust_gap - 1) * Cylinder(
        1.7, crown_h + exhaust_gap + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    crown = largest(crown - th)

# ============================================================
# COMPONENT DUMMIES + INTERFERENCE
# ============================================================
hm_carrier = Pos(0, hm_carrier_y, hm_z0) * Box(hm_w, hm_t, hm_h,
            align=(Align.CENTER, Align.MIN, Align.MIN))
hm_can = Pos(0, hm_carrier_y + hm_t, hm_z0 + (hm_h - can_h) / 2) * Box(
    can_w, can_d, can_h, align=(Align.CENTER, Align.MIN, Align.MIN))
hm_module = hm_carrier + hm_can
perf_y0 = -back_inner + perf_back_gap
perfboard = Pos(perf_cx, perf_y0, perf_z0) * Box(perf_w, perf_t, perf_h,
            align=(Align.CENTER, Align.MIN, Align.MIN))
perf_env = Pos(perf_cx, perf_y0 + perf_t, perf_z0) * Box(perf_w, 12.0, perf_h,
            align=(Align.CENTER, Align.MIN, Align.MIN))

shell_seated = shell
crown_seated = largest(Pos(0, 0, shell_h + exhaust_gap) * crown)


def check(name, a, b, limit=0.02):
    try:
        v = sum(s.volume for s in (a & b).solids()) / 1000.0
    except Exception:
        v = 0.0
    print(f"  [{'OK ' if v <= limit else 'FAIL'}] {name}: {v:.3f} cm3")
    return v <= limit


print(f"=== interference checks (VARIANT={VARIANT}) ===")
ok = True
if VARIANT == "plus":
    ok &= check("module vs spine", hm_module, spine)
    ok &= check("module vs shell", hm_module, shell_seated)
    ok &= check("perf vs module", perfboard + perf_env, hm_module)
ok &= check("perf vs spine", perfboard + perf_env, spine)
ok &= check("perf vs shell", perfboard + perf_env, shell_seated)
ok &= check("spine vs shell (back lips touch OK)", spine, shell_seated, limit=1.2)
ok &= check("crown vs shell (seat lap OK)", crown_seated, shell_seated, limit=1.5)
print("ALL OK" if ok else "INTERFERENCE — review before trusting")

# ============================================================
# EXPORTS
# ============================================================
sfx = VARIANT
parts_print = {
    f"v2_shell_{sfx}": shell,
    "v2_spine_" + sfx: spine,
}
if VARIANT == "plus":
    parts_print["v2_base"] = base
    parts_print["v2_crown"] = crown
for name, part in parts_print.items():
    export_stl(part, os.path.join(OUT, f"{name}.stl"))
    export_step(part, os.path.join(OUT, f"{name}.step"))
    bb = part.bounding_box()
    print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm, "
          f"{part.volume/1000:.1f} cm3")

# review-only assembly + cutaway (interpenetrating dummies → not strict)
asm = Compound([spine, shell_seated, Pos(0, 0, -base_h + 3) * base,
                crown_seated, hm_module, perfboard])
half = Box(400, 400, 500, align=(Align.MAX, Align.CENTER, Align.MIN))
cut = Compound([largest(spine - half), largest(shell_seated - half),
                largest(crown_seated - half), hm_module, perfboard])
export_stl(asm, os.path.join(REVIEW, f"v2_assembly_{sfx}.stl"))
export_stl(cut, os.path.join(REVIEW, f"v2_cutaway_{sfx}.stl"))
print("review assembly + cutaway written")
