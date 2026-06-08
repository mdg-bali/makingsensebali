#!/usr/bin/env python3
"""Disposable concept form studies — Making Sense Bali enclosure.

Three banana-flower (jantung pisang) massing variants per frozen decisions:
DEC-01 banana flower, DEC-02 <=140mm tall, flat back / 270deg wrap,
clean parametric bract shells, USB-C-at-tip gesture.

These are FORM STUDIES: no internals, no joints, no fit geometry.
They exist to be judged and thrown away (handover lesson: cheap concepts
before full builds).

  concept_A_closed_bud.stl    tight imbrication, small reveals, quiet
  concept_B_opening_bud.stl   lower ring flared, deep shadow gaps
  concept_C_spiral.stl        bracts descend in a phyllotaxis-like spiral
"""
import os
import math
from build123d import *  # noqa: F403

OUT = os.path.join(os.path.dirname(__file__), "..", "concepts")
os.makedirs(OUT, exist_ok=True)

# ============================================================
# PARAMETERS (mm) — shared envelope
# ============================================================
total_h = 138.0          # < 140 cap (DEC-02)
tip_h = 14.0             # tip cone zone, USB-C stem gesture
body_h = total_h - tip_h
r_max = 44.0             # widest body radius -> ~O88 + bract standoff
r_top = 26.0             # shoulder radius at top
bulge_z = 0.42           # fraction of body height where r_max sits
back_y = 16.0            # flat back plane at y = -16 (270-ish wrap)
bract_t = 2.5            # bract shell thickness (ICD wall rule)
n_az = 5                 # bracts per ring (azimuthal), rings of 5/4/3 etc.


def teardrop_body():
    """Revolved teardrop, tip down at z=0, cut flat at the back."""
    zs = [tip_h, tip_h + body_h * bulge_z, tip_h + body_h * 0.78, total_h]
    rs = [7.0, r_max, r_max * 0.82, r_top]
    pts = [(rs[i], zs[i]) for i in range(len(zs))]
    ln = Spline(*pts)
    closed = make_face(
        [ln,
         Line(ln @ 1, (0, total_h)),
         Line((0, total_h), (0, tip_h)),
         Line((0, tip_h), ln @ 0)]
    )
    body = revolve(Plane.XZ * closed, Axis.Z)
    # tip cone + usb stem gesture
    tip = Pos(0, 0, 0) * Cone(7.0, 2.5, tip_h,
                              align=(Align.CENTER, Align.CENTER, Align.MIN))
    tip = Rot(180, 0, 0) * tip          # point down
    tip = Pos(0, 0, tip_h) * tip
    stem = Pos(0, 0, -6) * Cylinder(4.0, 8.0,
                                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid = body + tip + stem
    # flat back: remove everything behind y = -back_y
    # (MAX-aligned: box occupies y in [-back_y-400, -back_y])
    cutter = Pos(0, -back_y, total_h / 2 - 4) * Box(
        400, 400, total_h + 60,
        align=(Align.CENTER, Align.MAX, Align.CENTER))
    return largest_solid(solid - cutter)


def largest_solid(x):
    """Collapse Solid/Compound/ShapeList to its single largest solid."""
    try:
        solids = list(x.solids())
    except (AttributeError, TypeError):
        solids = [s for item in x for s in item.solids()]
    if not solids:
        raise ValueError("boolean produced no solids")
    return max(solids, key=lambda s: s.volume)


# cache of scaled teardrop shells, keyed by round(scale_f, 3)
_shell_cache = {}


def teardrop_shell(scale_f):
    """A thin shell that follows the body surface, scaled outward in XY.

    bract = sector of THIS (not of a sphere): bracts must hug the teardrop
    or they read as loose petals (lesson from concept render v1).
    """
    key = round(scale_f, 3)
    if key not in _shell_cache:
        zs = [tip_h, tip_h + body_h * bulge_z, tip_h + body_h * 0.78, total_h]
        rs = [7.0, r_max, r_max * 0.82, r_top]

        def rev(f):
            pts = [(rs[i] * f, zs[i]) for i in range(len(zs))]
            ln = Spline(*pts)
            face = make_face(
                [ln,
                 Line(ln @ 1, (0, total_h)),
                 Line((0, total_h), (0, tip_h)),
                 Line((0, tip_h), ln @ 0)])
            return revolve(Plane.XZ * face, Axis.Z)

        outer = rev(scale_f)
        inner = rev(scale_f - bract_t / (r_max * 0.8))  # ~2.5mm radial at flank
        _shell_cache[key] = outer - inner
    return _shell_cache[key]


def bract(scale_f, z_lo, z_hi, az_deg, width_deg, droop=0.0):
    """One imbricated bract: a tall sector of the scaled body surface.

    z_lo/z_hi bound the bract band (z_lo is the drip tip end), width_deg its
    azimuthal width. The leaf prism extrudes ONE direction (-Y), cutting the
    shell once; the bract faces azimuth -90° before final rotation. droop
    tilts the whole bract slightly outward-down for peeling tips.
    """
    shell = teardrop_shell(scale_f)
    h = z_hi - z_lo
    zc = (z_lo + z_hi) / 2
    w = 2 * (r_max * scale_f + 6) * math.sin(math.radians(width_deg / 2))
    tip_pt = (0.0, z_lo)
    left = (-w / 2, zc + h * 0.05)
    right = (w / 2, zc + h * 0.05)
    top = (0.0, z_hi)
    leaf = make_face([
        ThreePointArc(tip_pt, (-w * 0.40, z_lo + h * 0.22), left),
        ThreePointArc(left, (-w * 0.34, z_hi - h * 0.16), top),
        ThreePointArc(top, (w * 0.34, z_hi - h * 0.16), right),
        ThreePointArc(right, (w * 0.40, z_lo + h * 0.22), tip_pt),
    ])
    prism = extrude(Plane.XZ * leaf, amount=r_max * scale_f + 40)
    piece = largest_solid(shell & prism)
    if droop:
        # hinge outward around the bract's top edge (it faces -Y here)
        piece = Pos(0, 0, z_hi) * Rot(droop, 0, 0) * Pos(0, 0, -z_hi) * piece
    return Rot(0, 0, az_deg + 90.0) * piece


def back_clip(shape):
    # MAX-aligned: cutter occupies y in [-back_y-400, -back_y]
    cutter = Pos(0, -back_y, 0) * Box(
        500, 400, 500, align=(Align.CENTER, Align.MAX, Align.CENTER))
    clipped = shape - cutter
    return largest_solid(clipped)


def ring_azimuths(n, offset=0.0, span=252.0):
    """n azimuths centred on +Y (front = 90deg), inside the wrap span."""
    if n == 1:
        return [90.0 + offset]
    step = span / n
    start = 90.0 - span / 2 + step / 2 + offset
    return [start + i * step for i in range(n)]


def build_concept(name, tiers, spiral=False):
    """tiers: list of dicts(scale, z_lo, z_hi, width_deg, droop, n, offset).

    Imbrication logic: each lower tier has a LARGER scale and its z_hi
    tucks under the tier above (roof-tile lap, rain runs outward).
    """
    body = teardrop_body()
    parts = [body]
    failed = 0
    if not spiral:
        for ti, t in enumerate(tiers):
            for az in ring_azimuths(t["n"], offset=t.get("offset", 0)):
                try:
                    b = bract(t["scale"], t["z_lo"], t["z_hi"], az,
                              t["width_deg"], t.get("droop", 0))
                    parts.append(back_clip(b))
                except Exception as e:
                    failed += 1
                    print(f"  bract fail tier{ti} az{az:.0f}: {e}")
    else:
        n = 10
        step = 97.0     # pseudo golden angle inside the wrap
        for i in range(n):
            t = i / (n - 1)
            az = 90.0 - 126.0 + ((i * step) % 252.0)
            z_hi = min(total_h * (0.99 - 0.48 * t), total_h * 0.98)
            z_lo = max(z_hi - total_h * 0.46, tip_h * 0.9)
            try:
                b = bract(scale_f=1.05 + 0.24 * t,
                          z_lo=z_lo, z_hi=z_hi,
                          az_deg=az, width_deg=66 - 12 * t,
                          droop=3 + 13 * t)
                parts.append(back_clip(b))
            except Exception as e:
                failed += 1
                print(f"  bract fail i{i}: {e}")
    comp = Compound(parts)
    stl = os.path.join(OUT, f"{name}.stl")
    export_stl(comp, stl)
    bb = comp.bounding_box()
    print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm, "
          f"{len(parts)-1} bracts, {failed} failed -> {stl}")


# Tall imbricated tiers. z-bands overlap (roof-tile lap); scale grows
# downward so lower bracts shingle OVER the zone below the upper tier.
# Gen1: bracts floated off the body (sphere sectors). Gen2: hugged
# invisibly (scale steps too small). Gen3: legible tiers, top still mute.
# Gen4 (Tomas, 2026-06-08): hybrid — A's calm crown LIFTED to visible
# standoff + B's peeling bottom tier. This is the Phase-1 base form
# candidate.
build_concept("concept_D_hybrid", [
    dict(n=4, scale=1.11, z_lo=total_h * 0.42, z_hi=total_h * 0.96,
         width_deg=88, droop=3),
    dict(n=4, scale=1.20, z_lo=total_h * 0.16, z_hi=total_h * 0.62,
         width_deg=80, droop=6, offset=45),
    dict(n=3, scale=1.31, z_lo=tip_h * 0.8, z_hi=total_h * 0.38,
         width_deg=68, droop=20, offset=15),
])

# Earlier generations (disposable, kept for the record — re-enable to rerun):
# build_concept("concept_A_closed_bud", [...])   # gen3 calm
# build_concept("concept_B_opening_bud", [...])  # gen3 peeling
# build_concept("concept_C_spiral", [], spiral=True)
