// ============================================================
// Making Sense Bali — DIY Node enclosure v5  "pine cone"
// ============================================================
// Biomimetic outdoor enclosure for the XIAO ESP32-S3 + BME680
// (+ Grove HM3301) Smart Citizen DIY node.
//
// v5 = v4's column architecture wearing a pine cone's skin:
//  * Overlapping scale rows — nature's rain shingles — replace
//    the smooth rings. Scales grow with height, so the envelope
//    reads as a hanging (inverted) cone. Seeded jitter on angle,
//    size and azimuth makes it organic but reproducible: change
//    scale_seed for a different individual of the same species.
//  * The skin breathes: small wall slots hide in the rain shadow
//    of scale rows — intake low (BME680 zone), exhaust high.
//    No separate vent rings; the ornament IS the ventilation.
//  * NO text labels. Components locate by printed FOOTPRINTS:
//    XIAO outline + USB-C notch and BME680 outline + lid circle
//    embossed on the spine (sight them through the perfboard
//    holes when soldering), LiPo outline at its bay, a USB
//    pictogram at the cable arch, and two registration pegs that
//    click into the Grove carrier's own Ø3.2 mounting holes.
//  * PM module vertical as v4: can faces a barred grille, shaded
//    by three scale-line rings + a 45° sill + the scales above.
//
// Two printed parts, support-free:
//   core — floor + cup + rails + spine + footprints. Standing.
//   hood — scaled skin + grille + cap. Inverted (10 mm brim!);
//          scales print as rising ~40° fins.
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
with_battery = true;
scale_seed   = 42;     // reroll for a different pine cone

// ---------- components ----------
pb_w = 40;  pb_h = 60;  pb_t = 1.6;
crr_l = 80; crr_w = 40; crr_t = 1.6;
can_l = 40; can_w = 38; can_h = 15;
can_cx = -5;
bat_l = 40; bat_w = 30; bat_t = 8;     // 803040 LiPo

// ---------- shells / fit ----------
shell = 1.6;  floor_t = 2.0;  spine_t = 2.4;  cup_t = 1.8;
skirt_t = 1.3;  fit = 0.5;  drop = 0.8;

// ---------- plan ----------
R_up = 31.5;  cy = 12;
spine_hw = 26;
cone_tip = 14;

// ---------- fasteners ----------
keyhole_head = 8;  keyhole_slot = 4.2;
pilot_d = 2.5;  thru_d = 3.4;

// ---------- derived: depth stack ----------
gy_pb  = 4.5;
gy_crr = 18.8;
y_canface = gy_crr + crr_t + can_h;

// ---------- derived: vertical stack ----------
is_plus = (variant=="plus");
z_pb0  = 14;   z_pb1 = z_pb0 + pb_h;
z_crr0 = 14;   z_crr1 = z_crr0 + crr_l;
spine_top = (is_plus ? z_crr1 : z_pb1) + 2;
cup_top = 10;  step_z = 7;  boss_z = 5.5;
col_bot = step_z + 0.3;
can_cz = z_crr0 + crr_l/2 - can_cx;
win_w2 = 17;
win_z0 = can_cz - can_l/2 + 2;  win_z1 = can_cz + can_l/2 - 2;
R_out  = R_up + shell;
cap_z0 = spine_top - 3;
cap_r  = R_out + 5;
cone_h = cap_r - cone_tip;
z_tip  = cap_z0 + cone_h + 1.7;

R_cup_in = R_up - 2;

// scales — top row roots fuse into the cap, like a cone's stem
sc_z0 = 20;  sc_pitch = 9;
sc_rows = floor((cap_z0 - 1 - sc_z0)/sc_pitch) + 2;

eps = 0.01;
$fa = 4; $fs = 0.6;
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

module rails(side) {
    fin_d = 9;
    fins = is_plus
        ? [[gy_pb-2, z_pb0], [gy_pb+pb_t+0.6, z_pb0],
           [gy_crr-2, z_crr0], [gy_crr+crr_t+0.6, z_crr0]]
        : [[gy_pb-2, z_pb0], [gy_pb+pb_t+0.6, z_pb0]];
    mirror([side<0?1:0,0,0]) {
        translate([24, 0, floor_t])
            cube([2, is_plus ? 23.2 : 9.2, spine_top-2-floor_t]);
        for (f=fins) {
            fz = f[1] - 3;
            translate([26-fin_d, f[0], fz]) {
                cube([fin_d, 2, spine_top-2-fz]);
                rotate([90,0,0]) translate([0,0,-2]) linear_extrude(2)
                    polygon([[fin_d,0],[0,0],[fin_d,-fin_d]]);
            }
        }
        translate([17, gy_pb-0.5, z_pb0-3])
            cube([9, pb_t+1.6, 3]);
        if (is_plus) translate([17, gy_crr-0.5, z_crr0-3])
            cube([9, crr_t+1.6, 3]);
    }
}

// raised footprint ring on the spine front (proud 0.6)
module fp_ring(w, h, r, z, t=1.2) {
    translate([0, 0, z]) rotate([-90,0,0]) linear_extrude(0.6)
        difference() {
            offset(r=r)   square([w-2*r, h-2*r], center=true);
            offset(r=r-t) square([w-2*r, h-2*r], center=true);
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
            // cup wall, shoulder step, lead-in
            linear_extrude(step_z) difference()
                { Dprof(R_cup_in+cup_t); Dprof(R_cup_in); }
            linear_extrude(cup_top) difference()
                { Dprof(R_cup_in+cup_t-1.2); Dprof(R_cup_in); }
            translate([0,0,cup_top-1]) linear_extrude(1) difference()
                { Dprof(R_cup_in+cup_t-1.2);
                  offset(delta=-1) Dprof(R_cup_in+cup_t-1.2); }
            // joint screw bosses
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
            // zip post
            translate([4, 0, floor_t]) difference() {
                cube([8, 4, 8]);
                translate([4,-eps,4]) rotate([-90,0,0]) cylinder(d=4, h=5);
            }
            // ---- FOOTPRINT GUIDES (no text) ----
            // XIAO shadow at the board top + its USB-C notch
            fp_ring(21.6, 18.4, 3, z_pb1-9.2);
            fp_ring(9.4, 3.8, 1.7, z_pb1+0.4);
            // BME680 shadow low + sensor-lid circle
            fp_ring(15.6, 12.6, 1.6, z_pb0+10);
            translate([0,0,z_pb0+10]) rotate([-90,0,0]) linear_extrude(0.6)
                difference() { circle(d=5); circle(d=3); }
            // LiPo shadow (plus: cell tapes to the carrier back here)
            if (with_battery && is_plus) fp_ring(40.6, 30.6, 2, 38);
            if (with_battery && is_plus)
                translate([-15, 8.6, floor_t]) cube([30, 1.6, 6]); // lip
            if (with_battery && !is_plus) difference() {
                translate([-bat_l/2-1.6, 15.4, floor_t])
                    cube([bat_l+3.2, bat_t+3.2, 7]);
                translate([-bat_l/2, 17, floor_t-eps])
                    cube([bat_l, bat_t, 7+2*eps]);
                for (xx=[-12,12]) translate([xx-1.6, 14, floor_t+1.5])
                    cube([3.2, 8, 3]);
            }
            // USB pictogram (oval ring) beside the cable arch
            translate([16, 22, floor_t-eps]) linear_extrude(0.6)
                difference() {
                    offset(r=2)   square([6, 0.5], center=true);
                    offset(r=1)   square([6, 0.5], center=true);
                }
            // PM registration pegs: click into the carrier's own
            // Ø3.2 mounting holes (bottom pair sits 4 mm up)
            if (is_plus) for (px=[-16,16])
                translate([px, gy_crr+0.8, z_crr0-1])
                    cylinder(d=2.6, h=5);
        }
        // version stamp, spine back (reads from the back)
        translate([0, -spine_t+0.55, spine_top-7]) rotate([90,0,0])
            linear_extrude(0.6) text(str("MSB v5 ", variant), size=3.6,
                font=FONT, halign="center", valign="center");
        // keyholes — behind the boards: hang first, boards after
        for (p=[[-15, 64],[15, 64],[-12, 20],[12, 20]])
            translate([p[0], -spine_t, p[1]]) keyhole();
        // joint screw pilots
        for (sx=[-1,1])
            translate([sx*(chw(R_cup_in)+cup_t+eps), cy, boss_z])
                rotate([0, sx>0?-90:90, 0]) cylinder(d=pilot_d, h=9);
        // cable arch
        translate([24, 16, -eps]) cube([10, 8, floor_t+2*eps]);
        translate([24, 16, floor_t-eps]) cube([10, 8, 6]);
        // weeps
        for (xx=[-10,10]) translate([xx, 2.4, -eps])
            cylinder(d=3, h=floor_t+2*eps);
    }
}

// ============================================================
// HOOD — prints inverted; scales become rising ~40° fins
// ============================================================
module shade_ring(z_root, proj, clip_y) {   // grille shading
    dropv = proj + 1 + shell;
    translate([0,0,z_root-dropv]) intersection() {
        translate([0,cy,0]) rotate_extrude()
            polygon([[R_up, dropv], [R_out+proj+1, 0],
                     [R_out+proj+1, -skirt_t], [R_up, dropv-skirt_t]]);
        half_y(clip_y);
    }
}
module cone_shell() {
    translate([0,0,cap_z0]) intersection() {
        translate([0,cy,0]) rotate_extrude()
            polygon([[cap_r, 1.7], [cone_tip, cone_h+1.7], [0, cone_h+1.7],
                     [0, cone_h], [cone_tip, cone_h], [cap_r, 0]]);
        half_y();
    }
}
module above_cone() {
    translate([0,0,cap_z0]) translate([0,cy,0]) rotate_extrude()
        polygon([[cap_r, 0], [cone_tip, cone_h],
                 [cone_tip, cone_h+99], [cap_r+99, cone_h+99], [cap_r+99, 0]]);
}

// one scale: shield-shaped fin, tilted down-out (use) / up-out (print)
module pine_scale(az, z, len, tilt) {
    w2 = len*0.42;
    translate([0,cy,0]) rotate([0,0,az])
        translate([R_out-1.2, 0, z]) rotate([0,tilt,0])
            linear_extrude(1.35)
                polygon([[-2.5, -w2*0.7], [len*0.5, -w2],
                         [len, 0], [len*0.5, w2], [-2.5, w2*0.7]]);
}

// the skin: jittered rows, scales grow with height (inverted-cone
// envelope), bald patch over the grille sector (plus)
module scales() {
    for (row=[0:sc_rows-1]) {
        z = sc_z0 + row*sc_pitch;
        n = 15;
        rnd = rands(0, 1, n*4, scale_seed + row);
        for (i=[0:n-1]) {
            az = -15 + i*15 + (row%2==0 ? 0 : 7.5)
                 + (rnd[4*i]-0.5)*5;
            grow = min(1, (z - sc_z0)/(cap_z0 - sc_z0));
            len  = (8 + 8.5*grow) * (0.88 + 0.24*rnd[4*i+1]);
            tilt = 50 + (rnd[4*i+2]-0.5)*8;   // 46–54°: ≤44° print overhang
            zj   = min(z + (rnd[4*i+3]-0.5)*2.4, cap_z0+2);
            in_grille = is_plus && az > 52 && az < 128
                        && zj > win_z0-4 && zj < win_z1+5;
            if (az > -18 && az < 198 && !in_grille)
                pine_scale(az, zj, len, tilt);
        }
    }
}

module col_in_prof()  { offset(r=fit)     Dprof(R_cup_in+cup_t-1.2); }
module col_out_prof() { offset(r=fit+1.8) Dprof(R_cup_in+cup_t-1.2); }

module hood() {
    union() {
        difference() {
            union() {
                // collar + blend + one continuous wall to the cap
                translate([0,0,col_bot]) linear_extrude(cup_top+1-col_bot)
                    difference() { col_out_prof(); col_in_prof(); }
                hull() { translate([0,0,cup_top+0.9]) linear_extrude(0.02)
                             col_out_prof();
                         translate([0,0,cup_top+5]) linear_extrude(0.02)
                             Dprof(R_out); }
                Dring(R_up, shell, cup_top+5-eps, cap_z0+2);
                // back wall above the spine + slit cover
                translate([-chw(R_up), 0.5, spine_top+0.5])
                    cube([2*chw(R_up), 1.6, z_tip-spine_top-1]);
                translate([-chw(R_up), -1.7, spine_top+0.5])
                    cube([2*chw(R_up), 2.2+1.6, 2]);
                // spine guide towers
                for (sx=[-1,1]) mirror([sx<0?1:0,0,0]) {
                    translate([spine_hw+0.5, -2.1, cup_top+6])
                        cube([1.8, 6.3, spine_top+1-(cup_top+6)]);
                    translate([spine_hw-2.3, 0.5, cup_top+6])
                        cube([4.6, 1.6, spine_top+1-(cup_top+6)]);
                }
            }
            above_cone();
            // breathing slots, hidden under scale rows:
            // intake low (BME680 zone) — full arc
            for (zs=[19, 28]) for (az=[0:30:180])
                translate([0,cy,0]) rotate([0,0,az])
                    translate([R_up-1, -3.5, zs]) cube([shell+2, 7, 3]);
            // exhaust high — rear + side sectors, under the cap
            for (zs=[spine_top-10, spine_top-19]) for (az=[-10,20,160,190])
                translate([0,cy,0]) rotate([0,0,az])
                    translate([R_up-1, -3.5, zs]) cube([shell+2, 7, 3]);
            // PM grille aperture (plus)
            if (is_plus)
                translate([-win_w2, y_canface+1, win_z0])
                    cube([2*win_w2, 20, win_z1-win_z0]);
            // joint screw holes
            for (sx=[-1,1])
                translate([sx*(chw(R_cup_in)+cup_t+fit+1.8+eps), cy, boss_z])
                    rotate([0, sx>0?-90:90, 0]) {
                        cylinder(d=thru_d, h=6);
                        cylinder(d=6.4, h=1.4);
                    }
        }
        cone_shell();
        scales();
        if (is_plus) {
            // grille shading: three scale-line rings, front sector
            for (zr=[win_z0+11, win_z0+23, win_z0+35])
                shade_ring(zr, 5, cy+6);
            // gecko bars
            intersection() {
                union() for (bx=[-14:3.5:14])
                    translate([bx-0.6, y_canface, win_z0-1])
                        cube([1.2, 12, win_z1-win_z0+2]);
                Dring(R_up-0.4, shell+2.5, win_z0-1, win_z1+1);
            }
            // 45° shedding sill
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
        cube([21, 8, 17.8]);
    color("MediumPurple") translate([4, gy_pb+pb_t, z_pb0+4])
        cube([15, 10, 13]);
    if (is_plus) {
        color("DarkGreen") translate([-crr_w/2, gy_crr, z_crr0])
            cube([crr_w, crr_t, crr_l]);
        color("Silver") translate([-can_w/2, gy_crr+crr_t, can_cz-can_l/2])
            cube([can_w, can_h, can_l]);
        color("White") translate([-5, gy_crr+crr_t, z_crr1-8])
            cube([10, 6, 8]);
        if (with_battery) color("Gold")
            translate([-bat_l/2, gy_crr-bat_t-0.5, 20])
                cube([bat_l, bat_t, bat_w]);
    } else if (with_battery) color("Gold")
        translate([-bat_l/2, 17, floor_t+1])
            cube([bat_l, bat_t, bat_w]);
}

// ============================================================
// output, print-oriented
// ============================================================
module hood_printed() { translate([0,0,z_tip]) rotate([180,0,0]) hood(); }

if (part=="core") core();
else if (part=="hood") hood_printed();
else if (part=="plate") {
    translate([-46, 0, 0]) core();
    translate([ 50, 0, 0]) hood_printed();
}
else { core(); hood(); if (show_dummies) dummies(); }

echo(str("== ", variant, " v5 ==  body Ø", 2*R_out,
     "  scale envelope ~Ø", round(2*(R_out+12)),
     "  H=", z_tip, "  rows=", sc_rows,
     is_plus ? str("  grille z ", win_z0, "→", win_z1) : "",
     "  battery=", with_battery ? "yes" : "no",
     "  seed=", scale_seed));
