// ============================================================
// Making Sense Bali — DIY Node enclosure v4  "column"
// ============================================================
// Compact vertical-stack outdoor enclosure for the XIAO ESP32-S3
// + BME680 (+ Grove HM3301) Smart Citizen DIY node.
//
// v4 (from the v3 review: "bulky — set the PM sensor vertical"):
//  * The 80×40 Grove module stands VERTICAL in front rails, can
//    facing forward through a louvered grille in the hood's nose.
//    Datasheet allows sideways ports; four shade rings + a 45°
//    sill + the cone brim kill every rain sight line into the
//    grille. The wide v3 foot is gone: one Ø66 column.
//  * Printed INDICATIONS: XIAO top / BME680 bottom on the spine,
//    PM SOCKET UP on the floor, USB at the exit, LIPO at the bay.
//  * Optional LiPo (≤ 803040, 8×30×40, ~1000 mAh), zero height
//    cost: Basic stands it in a floor frame in the front bay;
//    Plus foam-tapes it to the carrier back — it rides in with
//    the module, a floor lip stops it sliding. Wire to the XIAO
//    BAT pads before mounting. LiPo in a tropical outdoor box is
//    a considered choice: USB stays the recommended supply.
//
// Two printed parts, support-free:
//   core — floor + cup + rails + spine. Prints standing.
//   hood — collar + body + grille + shade rings + cone spire.
//          Prints inverted, spire cap down (10 mm brim!).
//
//   variant = "basic" | "plus"
//   part    = "core" | "hood" | "assembly" | "plate"
//
// White PETG. PLA softens on Bali rooftops — don't.
// Older versions: archive/ (read the disclaimer).
// License: MIT (parent repo).
// ============================================================

// ---------- what to render ----------
variant = "plus";      // ["basic", "plus"]
part    = "assembly";  // ["core", "hood", "assembly", "plate"]
show_dummies = true;
with_battery = true;   // LiPo provisions (no height cost)

// ---------- components ----------
pb_w = 40;  pb_h = 60;  pb_t = 1.6;   // 4×6 cm perfboard
crr_l = 80; crr_w = 40; crr_t = 1.6;  // Grove HM3301 carrier
can_l = 40; can_w = 38; can_h = 15;   // bare can on the carrier
can_cx = -5;     // can centre offset on carrier (socket end = -40)
bat_l = 40; bat_w = 30; bat_t = 8;    // 803040 LiPo, ~1000 mAh

// ---------- shells / fit ----------
shell = 1.6;  floor_t = 2.0;  spine_t = 2.4;  cup_t = 1.8;
skirt_t = 1.3;
fit  = 0.5;      // joint radial clearance (v2 jammed at 0.2)
drop = 0.8;

// ---------- plan ----------
R_up = 31.5;  cy = 12;          // body D-section, inner
spine_hw = 26;                  // spine half-width (52)
skirt_p  = 6;  cone_tip = 8;

// ---------- fasteners ----------
keyhole_head = 8;  keyhole_slot = 4.2;
pilot_d = 2.5;  thru_d = 3.4;

// ---------- derived: depth stack (y, from spine front face) ----------
gy_pb  = 4.5;                   // perfboard back face
gy_crr = 18.8;                  // carrier back face
y_canface = gy_crr + crr_t + can_h;   // 35.4, faces the nose

// ---------- derived: vertical stack (z) ----------
is_plus = (variant=="plus");
z_pb0  = 14;   z_pb1 = z_pb0 + pb_h;        // board 14..74
z_crr0 = 14;   z_crr1 = z_crr0 + crr_l;     // carrier 14..94
spine_top = (is_plus ? z_crr1 : z_pb1) + 2;
cup_top = 10;  step_z = 7;  boss_z = 5.5;
col_bot = step_z + 0.3;
g_lo0 = 18;  g_lo1 = 26;                    // intake vent ring
g_hi0 = spine_top - 9;  g_hi1 = spine_top - 1;
// grille over the can face (plus)
can_cz = z_crr0 + crr_l/2 - can_cx;
win_w2 = 17;
win_z0 = can_cz - can_l/2 + 2;  win_z1 = can_cz + can_l/2 - 2;
R_out   = R_up + shell;
r_brim  = R_out + skirt_p + 1;
cone_z0 = g_hi1 - (r_brim - R_out) - 1.5;
cone_h  = r_brim - cone_tip;
z_tip   = cone_z0 + cone_h + 1.7;
R_cup_in = R_up - 2;

eps = 0.01;
$fa = 3; $fs = 0.5;
FONT = "Liberation Sans:style=Bold";

// ============================================================
// 2D + helpers
// ============================================================
module Dprof(r, c=cy) {
    intersection() {
        translate([0,c]) circle(r);
        translate([-r-60,0]) square([2*r+120, r+c+60]);
    }
}
function chw(r,c=cy) = sqrt(r*r - c*c);
module Dring(r_in, t, z0, z1) {
    translate([0,0,z0]) linear_extrude(z1-z0)
        difference() { Dprof(r_in+t); Dprof(r_in); }
}
module half_y(y0=0) { translate([-250,y0,-60]) cube([500,500,500]); }
module label(txt, h=0.6, size=4.2) {
    linear_extrude(h) text(txt, size=size, font=FONT,
                           halign="center", valign="center");
}

// ============================================================
// CORE — prints standing
// ============================================================
module keyhole() {
    translate([0,-eps,0]) rotate([-90,0,0]) {
        cylinder(d=keyhole_head, h=spine_t+2*eps);
        translate([-keyhole_slot/2,-10,0])
            cube([keyhole_slot, 10, spine_t+2*eps]);
        translate([0,-10,0]) cylinder(d=keyhole_slot, h=spine_t+2*eps);
    }
}

// side plates + fin pairs forming vertical grooves:
// rear pair = perfboard, front pair = HM3301 carrier (plus).
module rails(side) {
    fin_d = 9;
    fins = is_plus
        ? [[gy_pb-2, z_pb0], [gy_pb+pb_t+0.6, z_pb0],
           [gy_crr-2, z_crr0], [gy_crr+crr_t+0.6, z_crr0]]
        : [[gy_pb-2, z_pb0], [gy_pb+pb_t+0.6, z_pb0]];
    mirror([side<0?1:0,0,0]) {
        translate([24, 0, floor_t])     // side plate, on the floor
            cube([2, is_plus ? 23.2 : 9.2, spine_top-2-floor_t]);
        for (f=fins) {
            fz = f[1] - 3;
            translate([26-fin_d, f[0], fz]) {
                cube([fin_d, 2, spine_top-2-fz]);
                // 45° wedge below, tip merging into the side plate
                rotate([90,0,0]) translate([0,0,-2]) linear_extrude(2)
                    polygon([[fin_d,0],[0,0],[fin_d,-fin_d]]);
            }
        }
        translate([17, gy_pb-0.5, z_pb0-3])          // board stop
            cube([9, pb_t+1.6, 3]);
        if (is_plus) translate([17, gy_crr-0.5, z_crr0-3])
            cube([9, crr_t+1.6, 3]);
    }
}

module core() {
    difference() {
        union() {
            // floor
            linear_extrude(floor_t) union() {
                Dprof(R_cup_in+cup_t);
                translate([-spine_hw,-spine_t]) square([2*spine_hw, spine_t+1]);
            }
            // cup wall, shoulder step, lead-in chamfer
            linear_extrude(step_z) difference()
                { Dprof(R_cup_in+cup_t); Dprof(R_cup_in); }
            linear_extrude(cup_top) difference()
                { Dprof(R_cup_in+cup_t-1.2); Dprof(R_cup_in); }
            translate([0,0,cup_top-1]) linear_extrude(1) difference()
                { Dprof(R_cup_in+cup_t-1.2);
                  offset(delta=-1) Dprof(R_cup_in+cup_t-1.2); }
            // joint screw bosses inside the cup wall
            for (sx=[-1,1]) mirror([sx<0?1:0,0,0])
                translate([chw(R_cup_in)-4, cy-5, floor_t])
                    cube([5, 10, cup_top-floor_t]);
            // spine + gussets
            translate([-spine_hw, -spine_t, 0])
                cube([2*spine_hw, spine_t, spine_top]);
            for (sx=[-1,1]) mirror([sx<0?1:0,0,0])
                translate([8, 0, floor_t]) rotate([90,0,90])
                    linear_extrude(2) polygon([[0,0],[8,0],[0,8]]);
            rails(1); rails(-1);
            // zip post (USB strain relief)
            translate([4, 0, floor_t]) difference() {
                cube([8, 4, 8]);
                translate([4,-eps,4]) rotate([-90,0,0]) cylinder(d=4, h=5);
            }
            // ---- LiPo provisions (no height cost) ----
            if (with_battery) {
                if (is_plus)
                    // catch lip: battery is foam-taped to the carrier
                    // back and rides in with the module; this stops
                    // it sliding down. (battery y ≈ 9.5..17.5)
                    translate([-15, 8.6, floor_t]) cube([30, 1.6, 6]);
                else {
                    // basic: stand the cell in a frame, front bay
                    difference() {
                        translate([-bat_l/2-1.6, 15.4, floor_t])
                            cube([bat_l+3.2, bat_t+3.2, 7]);
                        translate([-bat_l/2, 17, floor_t-eps])
                            cube([bat_l, bat_t, 7+2*eps]);
                        // zip slots through the frame walls
                        for (xx=[-12,12]) translate([xx-1.6, 14, floor_t+1.5])
                            cube([3.2, 8, 3]);
                    }
                }
            }
            // ---- raised indications on the floor ----
            translate([-12, cy+19, floor_t-eps]) label("USB", h=0.5, size=4);
            if (is_plus) translate([2, cy+26, floor_t-eps])
                label("PM SOCKET UP", h=0.5, size=3.4);
        }
        // ---- debossed indications on the spine front ----
        // mirror+R90: cut engages 0.55 deep, reads correctly from +y
        // (verified empirically — OpenSCAD text orientation is a trap)
        translate([0, 0.05, 9]) mirror([1,0,0]) rotate([90,0,0])
            label("BME680 v    XIAO ^", h=0.6, size=4);
        if (with_battery)
            translate([0, 0.05, is_plus ? 62 : 38])
                mirror([1,0,0]) rotate([90,0,0])
                    label(is_plus ? "LIPO ON CARRIER BACK" : "LIPO 803040",
                          h=0.6, size=3.4);
        // version stamp on the spine back (reads from the back)
        translate([0, -spine_t+0.55, spine_top-7]) rotate([90,0,0])
            label(str("MSB v4 ", variant), h=0.6, size=3.6);
        // keyholes — behind the boards: hang the core on pre-driven
        // screws FIRST, then slide the boards in.
        for (p=[[-15, 64],[15, 64],[-12, 20],[12, 20]])
            translate([p[0], -spine_t, p[1]]) keyhole();
        // joint screw pilots
        for (sx=[-1,1])
            translate([sx*(chw(R_cup_in)+cup_t+eps), cy, boss_z])
                rotate([0, sx>0?-90:90, 0]) cylinder(d=pilot_d, h=9);
        // cable arch, right side of the cup
        translate([24, 16, -eps]) cube([10, 8, floor_t+2*eps]);
        translate([24, 16, floor_t-eps]) cube([10, 8, 6]);
        // weeps
        for (xx=[-10,10]) translate([xx, 2.4, -eps])
            cylinder(d=3, h=floor_t+2*eps);
    }
}

// ============================================================
// HOOD — prints inverted
// ============================================================
// 45° conical shade ring; root welds through the wall thickness.
module shade_ring(z_root, proj=skirt_p, clip_y=-99) {
    dropv = proj + 1 + shell;
    translate([0,0,z_root-dropv]) intersection() {
        translate([0,cy,0]) rotate_extrude()
            polygon([[R_up, dropv], [R_out+proj+1, 0],
                     [R_out+proj+1, -skirt_t], [R_up, dropv-skirt_t]]);
        half_y(clip_y > -90 ? clip_y : 0);
    }
}
module cone_shell() {
    translate([0,0,cone_z0]) intersection() {
        translate([0,cy,0]) rotate_extrude()
            polygon([[r_brim, 1.7], [cone_tip, cone_h+1.7], [0, cone_h+1.7],
                     [0, cone_h], [cone_tip, cone_h], [r_brim, 0]]);
        half_y();
    }
}
module above_cone() {
    translate([0,0,cone_z0]) translate([0,cy,0]) rotate_extrude()
        polygon([[r_brim, 0], [cone_tip, cone_h],
                 [cone_tip, cone_h+99], [r_brim+99, cone_h+99], [r_brim+99, 0]]);
}
module vent_ribs(z0, z1) {
    for (az=[0,45,90,135,180]) translate([0,cy,0]) rotate([0,0,az])
        translate([R_up-0.3, -0.8, z0]) cube([shell+0.6, 1.6, z1-z0]);
}
module col_in_prof()  { offset(r=fit)     Dprof(R_cup_in+cup_t-1.2); }
module col_out_prof() { offset(r=fit+1.8) Dprof(R_cup_in+cup_t-1.2); }

module hood() {
    union() {
        difference() {
            union() {
                // collar over the cup step (hard shoulder stop)
                translate([0,0,col_bot]) linear_extrude(cup_top+1-col_bot)
                    difference() { col_out_prof(); col_in_prof(); }
                hull() { translate([0,0,cup_top+0.9]) linear_extrude(0.02)
                             col_out_prof();
                         translate([0,0,cup_top+5]) linear_extrude(0.02)
                             Dprof(R_out); }
                // body bands with a real vent gap between them
                Dring(R_up, shell, cup_top+5-eps, g_lo0);
                Dring(R_up, shell, g_lo1, g_hi0);
                shade_ring(g_lo1+1.5);            // intake skirt
                vent_ribs(g_lo0-eps, g_lo1+eps);
                vent_ribs(g_hi0-eps, g_hi1+4);
                // back wall above the spine + slit cover
                translate([-chw(R_up), 0.5, spine_top+0.5])
                    cube([2*chw(R_up), 1.6, z_tip-spine_top-1]);
                translate([-chw(R_up), -1.7, spine_top+0.5])
                    cube([2*chw(R_up), 2.2+1.6, 2]);
                // spine guide towers, start above the cup
                for (sx=[-1,1]) mirror([sx<0?1:0,0,0]) {
                    translate([spine_hw+0.5, -2.1, cup_top+6])
                        cube([1.8, 6.3, spine_top+1-(cup_top+6)]);
                    translate([spine_hw-2.3, 0.5, cup_top+6])
                        cube([4.6, 1.6, spine_top+1-(cup_top+6)]);
                }
            }
            above_cone();
            // PM grille aperture through the nose (plus)
            if (is_plus)
                translate([-win_w2, y_canface+1, win_z0])
                    cube([2*win_w2, 20, win_z1-win_z0]);
            // joint screw holes through the collar
            for (sx=[-1,1])
                translate([sx*(chw(R_cup_in)+cup_t+fit+1.8+eps), cy, boss_z])
                    rotate([0, sx>0?-90:90, 0]) {
                        cylinder(d=thru_d, h=6);
                        cylinder(d=6.4, h=1.4);
                    }
        }
        cone_shell();
        if (is_plus) {
            // grille louvers: 4 shade rings over the window, front
            // arc only; the cone brim covers the top band at 45°
            for (zr=[win_z0+11.5, win_z0+21.5, win_z0+31.5, win_z0+41.5])
                shade_ring(zr, 5, cy+6);
            // vertical gecko bars in the aperture
            intersection() {
                union() for (bx=[-14:3.5:14])
                    translate([bx-0.6, y_canface, win_z0-1])
                        cube([1.2, 12, win_z1-win_z0+2]);
                Dring(R_up-0.4, shell+2.5, win_z0-1, win_z1+1);
            }
            // 45° shedding sill at the aperture's bottom lip
            intersection() {
                translate([0,0,win_z0+eps]) translate([0,cy,0]) rotate_extrude()
                    polygon([[R_up-1, 0], [R_out+3.5, -(R_out+3.5-(R_up-1))],
                             [R_up-1, -(R_out+3.5-(R_up-1))]]);
                half_y(cy+6);
            }
        }
    }
}

// ============================================================
// preview dummies
// ============================================================
module dummies() {
    color("ForestGreen") translate([-pb_w/2, gy_pb, z_pb0])
        cube([pb_w, pb_t, pb_h]);
    color("DimGray") translate([-10.5, gy_pb+pb_t, z_pb1-20])
        cube([21, 8, 17.8]);                          // XIAO top
    color("MediumPurple") translate([4, gy_pb+pb_t, z_pb0+4])
        cube([15, 10, 13]);                           // BME680 bottom
    if (is_plus) {
        color("DarkGreen") translate([-crr_w/2, gy_crr, z_crr0])
            cube([crr_w, crr_t, crr_l]);
        color("Silver") translate([-can_w/2, gy_crr+crr_t, can_cz-can_l/2])
            cube([can_w, can_h, can_l]);
        color("White") translate([-5, gy_crr+crr_t, z_crr1-8])
            cube([10, 6, 8]);                         // socket end, up
        if (with_battery) color("Gold")
            translate([-bat_l/2, gy_crr-bat_t-0.5, 20])
                cube([bat_l, bat_t, bat_w]);          // taped to carrier
    } else if (with_battery) color("Gold")
        translate([-bat_l/2, 17, floor_t+1])
            cube([bat_l, bat_t, bat_w]);              // floor frame
}

// ============================================================
// output, print-oriented
// ============================================================
module hood_printed() { translate([0,0,z_tip]) rotate([180,0,0]) hood(); }

if (part=="core") core();
else if (part=="hood") hood_printed();
else if (part=="plate") {
    translate([-44, 0, 0]) core();
    translate([ 46, 0, 0]) hood_printed();
}
else { core(); hood(); if (show_dummies) dummies(); }

echo(str("== ", variant, " v4 ==  body Ø", 2*R_out, "  brim Ø", 2*r_brim,
     "  H=", z_tip, "  board z ", z_pb0, "→", z_pb1,
     is_plus ? str("  carrier ", z_crr0, "→", z_crr1,
                   "  grille z ", win_z0, "→", win_z1) : "",
     "  battery=", with_battery ? "yes" : "no"));
