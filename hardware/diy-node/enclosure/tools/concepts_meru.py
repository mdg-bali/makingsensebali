#!/usr/bin/env python3
"""Meru-batik concept form studies — DEC-01 v1.1.

Self-similar stacked tiers (meru/pagoda logic): each curved roof sheds rain
and shadows the recessed band beneath it; those bands are where pierced
batik-derived (kawung-class) pattern ventilation lives in Phase 2. Organic
curved profiles, not hard cones. Flat back (270° wrap), <=140mm, carry-over
engineering per ICD.

MASSING ONLY — no internals, no fits, bands are plain recessed cylinders.

  concept_M1_classic.stl   5 tiers, strong taper, steep roofs, deep eaves
  concept_M2_soft.stl      5 tiers, gentle taper, droopy ogee roofs
  concept_M3_slender.stl   7 tiers, tight rhythm, slimmer body
"""
import os
import math
from build123d import *  # noqa: F403

OUT = os.path.join(os.path.dirname(__file__), "..", "concepts")
os.makedirs(OUT, exist_ok=True)

back_y = 16.0          # flat back plane (carry-over)
z_budget = 138.0       # DEC-02


def largest_solid(x):
    try:
        solids = list(x.solids())
    except (AttributeError, TypeError):
        solids = [s for item in x for s in item.solids()]
    if not solids:
        raise ValueError("boolean produced no solids")
    return max(solids, key=lambda s: s.volume)


def back_clip(shape):
    cutter = Pos(0, -back_y, 0) * Box(
        500, 400, 500, align=(Align.CENTER, Align.MAX, Align.CENTER))
    return largest_solid(shape - cutter)


def roof(r_apex, r_eave, h, z_base, sag_out=0.48, sag_down=0.58, lip=2.5):
    """One curved tier roof, solid, sitting on z_base.

    Profile: apex plateau at r_apex (the band above emerges from it),
    ogee spline out to the eave, small vertical eave lip. sag_out/sag_down
    place the spline midpoint: larger = droopier, more organic.
    """
    zt = z_base + h + lip
    mid = (r_apex + (r_eave - r_apex) * sag_out, zt - h * sag_down)
    face = make_face([
        Line((0, zt), (r_apex, zt)),
        Spline((r_apex, zt), mid, (r_eave, z_base + lip)),
        Line((r_eave, z_base + lip), (r_eave, z_base)),
        Line((r_eave, z_base), (0, z_base)),
        Line((0, z_base), (0, zt)),
    ])
    return revolve(Plane.XZ * face, Axis.Z)


def dome(r, h):
    """Rounded underside, apex at z=0."""
    face = make_face([
        Spline((0, 0), (r * 0.82, h * 0.5), (r, h)),
        Line((r, h), (0, h)),
        Line((0, h), (0, 0)),
    ])
    return revolve(Plane.XZ * face, Axis.Z)


def finial(r, z_base):
    """Meru crown (murda): clean concave spire to a point."""
    h = r * 2.3
    face = make_face([
        Spline((r, 0), (r * 0.38, h * 0.42), (0.01, h)),
        Line((0.01, h), (0, h)),
        Line((0, h), (0, 0)),
        Line((0, 0), (r, 0)),
    ])
    return Pos(0, 0, z_base) * revolve(Plane.XZ * face, Axis.Z)


def build_meru(name, n_roofs, ratio, body_r, body_h, body_eave_r,
               h0, band_h0, band_recess=0.62,
               sag_out=0.40, sag_down=0.45, lip=3.0,
               dome_h=7.0, finial_r=None):
    """Gen2 composition: BODY (cylinder, the PM/board bay and the largest
    pattern band) wearing one generous body roof, then (n_roofs-1)
    diminishing roof+band pairs above. Total roof count should be ODD
    (meru convention: 3/5/7…).

    Gen1 lesson: taper from the ground reads as a pine tree; roofs sagging
    past horizontal read as ruffles. Tiers must sit on a body, eaves must
    stay crisp, bands must be SEEN (they carry the pierced batik later).
    """
    eaves = [body_eave_r * ratio**i for i in range(n_roofs)]
    bands = [e * band_recess for e in eaves[1:]]          # bands above body
    rh = [h0 * ratio**i for i in range(n_roofs)]
    bh = [band_h0 * ratio**i for i in range(n_roofs - 1)]
    fin_r = finial_r if finial_r else eaves[-1] * 0.42

    total = (dome_h + body_h + sum(rh) + n_roofs * lip + sum(bh)
             + fin_r * 2.3)
    f = z_budget / total
    dome_h *= f
    body_h *= f
    rh = [r * f for r in rh]
    bh = [b * f for b in bh]

    parts = []
    z = 0.0
    parts.append(dome(body_r, dome_h))
    z += dome_h
    parts.append(Pos(0, 0, z) * Cylinder(
        body_r, body_h, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    z += body_h
    for i in range(n_roofs):
        r_apex = bands[i] if i < len(bands) else fin_r * 0.8
        parts.append(roof(r_apex, eaves[i], rh[i], z,
                          sag_out=sag_out, sag_down=sag_down, lip=lip))
        z += rh[i] + lip
        if i < len(bands):
            parts.append(Pos(0, 0, z) * Cylinder(
                bands[i], bh[i],
                align=(Align.CENTER, Align.CENTER, Align.MIN)))
            z += bh[i]
    parts.append(finial(fin_r, z))

    solid = parts[0]
    for p in parts[1:]:
        solid = solid + p          # stacked, touching: stays a single solid
    solid = back_clip(solid)

    stl = os.path.join(OUT, f"{name}.stl")
    export_stl(solid, stl)
    export_step(solid, os.path.join(OUT, f"{name}.step"))
    bb = solid.bounding_box()
    print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm, "
          f"{n_roofs} roofs, ratio {ratio} -> {stl}")


# Roof counts follow the meru odd-number convention: 3 / 5 / 7.
# Gen3 retune (Tomas): crisper flatter roofs (h0 down ~35%, concave
# thatch profile, sharp eave) + murda spire finial instead of onion knob.
# ---- N1 tumpang lima: body + 5 roofs, the balanced tower -------------------
build_meru("concept_N1_lima", n_roofs=5, ratio=0.84,
           body_r=38.0, body_h=42.0, body_eave_r=47.0,
           h0=7.5, band_h0=10.5, band_recess=0.64,
           sag_out=0.45, sag_down=0.60, lip=2.2)

# ---- N2 tumpang telu: body + 3 broad roofs, calm and practical -------------
build_meru("concept_N2_telu", n_roofs=3, ratio=0.80,
           body_r=40.0, body_h=48.0, body_eave_r=48.0,
           h0=9.0, band_h0=14.0, band_recess=0.60,
           sag_out=0.48, sag_down=0.62, lip=2.5)

# ---- N3 tumpang pitu: body + 7 roofs, vertical rhythm ----------------------
build_meru("concept_N3_pitu", n_roofs=7, ratio=0.875,
           body_r=34.0, body_h=36.0, body_eave_r=42.0,
           h0=5.8, band_h0=8.0, band_recess=0.66,
           sag_out=0.44, sag_down=0.58, lip=1.8)
