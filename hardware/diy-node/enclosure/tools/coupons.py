#!/usr/bin/env python3
"""Calibration coupon set for the Making Sense Bali enclosure (ICD §5.1).

Two plates, printed in PETG on the actual machine before any fit is modeled:

  coupon_A_fits.stl   — clearance ladder: 7 holes Ø5.0+c and 7 edge slots
                        3.0+c wide, c = 0.0…0.6 in 0.1 steps, embossed labels
                        0–6; plus 3 loose Ø5.00 pins and 2 loose 3.00 tabs.
  coupon_B_print.stl  — overhang fins at 35/40/45/50/55° from vertical,
                        horizontal-hole wall Ø3.2/Ø5/Ø10 (keyhole + peg
                        proxies), snap-flex stick (PETG spring behavior for
                        the bayonet detent).

Measure per ICD §5.1: first hole the pin slides into without force = sliding
fit; first it drops freely into = free fit; calipers on holes/pins for shrink;
fin undersides judged for max clean overhang; plate edge for elephant foot.

Print: PETG @COREONE HF0.4, 0.15mm SPEED, no supports, as printed (no
deburring before measuring).
"""
from build123d import *  # noqa: F403

OUT = __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "coupons")
__import__("os").makedirs(OUT, exist_ok=True)

# ============================================================
# PARAMETERS (mm)
# ============================================================
plate_l, plate_w, plate_t = 124.0, 62.0, 3.0
hole_d_nom = 5.0            # nominal pin diameter
slot_w_nom = 3.0            # nominal tab thickness
steps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
hole_pitch = 16.0
label_h = 0.6               # emboss height
label_size = 5.0

pin_d, pin_len = 5.0, 12.0
pin_flange_d, pin_flange_t = 9.0, 2.0

tab_t, tab_w, tab_len = 3.0, 10.0, 22.0
slot_depth = 12.0           # how far the slot notch goes into the plate

fin_angles = [35, 40, 45, 50, 55]   # degrees from vertical (overhang)
fin_t, fin_w, fin_h = 1.6, 12.0, 18.0

hw_wall_l, hw_wall_t, hw_wall_h = 46.0, 5.0, 22.0
hw_holes = [3.2, 5.0, 10.0]

snap_beam_l, snap_beam_w, snap_beam_t = 42.0, 8.0, 1.8
snap_hook_h = 3.5

# ============================================================
# COUPON A — fits plate + loose gauges
# ============================================================
plate = Box(plate_l, plate_w, plate_t,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

x0 = -plate_l / 2 + 14.0
for i, c in enumerate(steps):
    x = x0 + i * hole_pitch
    # hole row (top half of plate)
    plate -= Pos(x, 12, 0) * Cylinder(
        (hole_d_nom + c) / 2, plate_t * 3,
        align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # slot notch row (front edge)
    plate -= Pos(x, -plate_w / 2 + slot_depth / 2 - 0.01, 0) * Box(
        slot_w_nom + c, slot_depth, plate_t * 3,
        align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # embossed label between rows
    lbl = Plane.XY.offset(plate_t) * Pos(x, -1.5, 0) * Text(
        str(i), font_size=label_size)
    plate += extrude(lbl, label_h)

# loose pins (3×) — printed vertical like the holes
pins = []
for k in range(3):
    pin = Cylinder(pin_flange_d / 2, pin_flange_t,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    pin += Cylinder(pin_d / 2, pin_len,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    pins.append(Pos(-20 + k * 14, plate_w / 2 + 12, 0) * pin)

# loose tabs (2×) — printed flat, 3.0 thickness in Z (20 layers @0.15)
tabs = []
for k in range(2):
    tab = Box(tab_len, tab_w, tab_t,
              align=(Align.CENTER, Align.CENTER, Align.MIN))
    tab += Pos(tab_len / 2 - 4, 0, 0) * Box(
        8, tab_w, tab_t + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN))  # grip step
    tabs.append(Pos(18 + k * 4, plate_w / 2 + 12 + (k * 16), 0) *
                Rot(0, 0, 90 * k) * tab)

# NOTE: Solid + Solid on disjoint bodies returns ShapeList in build123d 0.10;
# aggregate islands explicitly as a Compound for export.
coupon_a = Compound([plate] + pins + tabs)

# ============================================================
# COUPON B — overhang fins + horizontal holes + snap stick
# ============================================================
# overhang fins on a shared base bar
fin_base = Box(len(fin_angles) * 14.0 + 8, 16, 3.0,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
fins = fin_base
fx0 = -(len(fin_angles) - 1) * 14.0 / 2
for i, ang in enumerate(fin_angles):
    fin = Box(fin_t, fin_w, fin_h,
              align=(Align.CENTER, Align.CENTER, Align.MIN))
    fin = Rot(0, ang, 0) * fin          # lean in +X by `ang` from vertical
    fins += Pos(fx0 + i * 14.0, 0, 3.0) * fin
    lbl = Plane.XY.offset(3.0) * Pos(fx0 + i * 14.0 - 4, -6.5, 0) * Text(
        str(ang), font_size=3.5)
    fins += extrude(lbl, label_h)

# horizontal-hole wall
hw = Box(hw_wall_l, hw_wall_t, hw_wall_h,
         align=(Align.CENTER, Align.CENTER, Align.MIN))
hw_x = [-15.0, 0.0, 15.0]
for d, x in zip(hw_holes, hw_x):
    hw -= Pos(x, 0, 11.0) * Rot(90, 0, 0) * Cylinder(
        d / 2, hw_wall_t * 3,
        align=(Align.CENTER, Align.CENTER, Align.CENTER))
hw = Pos(0, 26, 0) * hw

# snap-flex stick: anchored beam with hook, flex by hand after printing
snap = Box(12, snap_beam_w, 6,
           align=(Align.MIN, Align.CENTER, Align.MIN))      # anchor block
snap += Pos(12, 0, 0) * Box(snap_beam_l, snap_beam_w, snap_beam_t,
                            align=(Align.MIN, Align.CENTER, Align.MIN))
snap += Pos(12 + snap_beam_l - 3, 0, snap_beam_t) * Box(
    3, snap_beam_w, snap_hook_h,
    align=(Align.MIN, Align.CENTER, Align.MIN))
snap = Pos(-32, -26, 0) * snap

coupon_b = Compound([fins, hw, snap])

# ============================================================
# EXPORT + report
# ============================================================
import os
for name, part in [("coupon_A_fits", coupon_a), ("coupon_B_print", coupon_b)]:
    stl = os.path.join(OUT, f"{name}.stl")
    step = os.path.join(OUT, f"{name}.step")
    export_stl(part, stl)
    export_step(part, step)
    bb = part.bounding_box()
    print(f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
          f"volume {part.volume/1000:.1f} cm3 -> {stl}")
