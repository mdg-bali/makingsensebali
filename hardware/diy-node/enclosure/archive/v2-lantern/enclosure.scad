// ============================================================
// Making Sense Bali — DIY Node enclosure v2  "lantern"
// ============================================================
// FDM-native outdoor enclosure for the XIAO ESP32-S3 + BME680
// (+ HM3301) Smart Citizen DIY node. Two printed parts, no
// supports, no glue, snap-fit — geometry a laser cutter can't do:
//
//   core — floor + PM cradle + mounting spine. Prints standing
//          on its floor. Rail blocks carry 45° underside chamfers
//          so nothing overhangs.
//   hood — D-section shell with two continuous skirt vents and a
//          45° cone spire. Prints inverted (spire cap on the bed);
//          every skirt becomes a rising 45° surface. Thin walls:
//          curvature does the stiffening, not material.
//
//   variant = "basic" | "plus"
//   part    = "core" | "hood" | "assembly" | "plate"
//             ("plate" = both parts print-oriented on one bed)
//
// Material: white PETG. PLA softens on Bali rooftops — don't.
// Rationale + assembly: README.md. License: MIT (parent repo).
// ============================================================

// ---------- what to render ----------
variant = "plus";      // ["basic", "plus"]
part    = "assembly";  // ["core", "hood", "assembly", "plate"]
show_dummies = true;

// ---------- components (datasheet / measured) ----------
pb_w = 50;  pb_h = 70;  pb_t = 1.6;   // 5×7 cm perfboard
hm_l = 40;  hm_w = 38;  hm_h = 15;    // HM3301 (40 × 38 × 15)
hm_top_extra = 7;                     // Grove adapter + plug room

// ---------- shells / fit ----------
shell    = 1.6;    // hood wall (curved → stiff at 4 perimeters)
skirt_t  = 1.3;    // skirt + cone thickness
floor_t  = 2.0;
spine_t  = 2.4;
cup_t    = 1.8;
drop_fit = 0.8;

// ---------- plan geometry (D-section) ----------
cy        = 17.1;            // circle centre, forward of spine face
R_cup_in  = 33.9;            // cup inner radius
R_hood_in = 36.0;            // hood inner radius
skirt_p   = 8;               // skirt projection beyond hood wall
cone_tip  = 10;              // spire truncation radius

// ---------- fasteners ----------
keyhole_head = 8;  keyhole_slot = 4.2;
pilot_d = 2.5;               // optional M3 backup screws
use_screws = false;          // snap-fit is the default

// ---------- derived: vertical stack (z=0 under floor) ----------
is_plus  = (variant=="plus");
pm_bay_h = hm_h + hm_top_extra + 4;                  // 26
z_stop   = floor_t + (is_plus ? pm_bay_h + 3 : 5);   // board bottom
z_board_top = z_stop + pb_h;
spine_top   = z_board_top + 2;   // 1+ mm under the cone inner face
cup_top  = floor_t + (is_plus ? pm_bay_h : 8);
rim_z    = cup_top - 5.7;                            // hood rim seat
g_lo0 = z_stop + 4;        g_lo1 = g_lo0 + 8;        // intake vent
g_hi0 = z_board_top - 7;   g_hi1 = z_board_top + 1;  // exhaust vent

// ---------- derived: plan ----------
function chw(r) = sqrt(r*r - cy*cy);   // chord half-width at y=0
R_cup_out  = R_cup_in + cup_t;         // 35.7
flange_r   = 35.8;                     // cup top flange (hood seat)
R_hood_out = R_hood_in + shell;        // 37.6
r_brim     = R_hood_out + skirt_p;     // 45.6 skirt/cone reach
spine_hw   = chw(R_cup_out);           // ~31.3
hood_chw   = chw(R_hood_in);           // ~31.7
cone_z0    = g_hi1 - (r_brim - R_hood_out) - 1.5;  // brim tip below vent
cone_h     = r_brim - cone_tip;        // 45° spire
z_tip      = cone_z0 + cone_h + 1.7;   // overall top

// PM bay (plus)
fence_l = hm_l + drop_fit;  fence_w = hm_w + drop_fit;
fence_t = 2.0;  fence_h = 8;  hm_cy = 22;
win_w = 13;  win_l = 30;  mesh_x = 36;  mesh_y = 34;

// rails
groove_y0 = 4.5;  rail_x0 = 22;  rail_d = 12;
screw_z = [z_stop+8, z_stop+55];

rib_az  = [0, 45, 90, 135, 180];   // vent webs, azimuth about C
nub_az  = [35, 145];               // snap nubs

eps = 0.01;
$fa = 3; $fs = 0.5;

// ============================================================
// 2D helpers — the D profile (flat at y=0, arc forward)
// ============================================================
module Dprof(r) {
    intersection() {
        translate([0,cy]) circle(r);
        translate([-r-50, 0]) square([2*r+100, r+cy+50]);
    }
}
module Dring(r_in, t, z0, z1) {
    translate([0,0,z0]) linear_extrude(z1-z0)
        difference() { Dprof(r_in+t); Dprof(r_in); }
}
module half_y() {  // y ≥ 0 halfspace
    translate([-250,0,-50]) cube([500,500,500]);
}

// ============================================================
// CORE — floor + cup + PM cradle + spine. Prints standing.
// ============================================================
module keyhole() {
    translate([0,-eps,0]) rotate([-90,0,0]) {
        cylinder(d=keyhole_head, h=spine_t+2*eps);
        translate([-keyhole_slot/2,-10,0])
            cube([keyhole_slot, 10, spine_t+2*eps]);
        translate([0,-10,0]) cylinder(d=keyhole_slot, h=spine_t+2*eps);
    }
}

module rail_block(side) {
    bz0 = max(z_stop-3, floor_t);            // block bottom
    ch  = min(rail_d, bz0-floor_t);          // chamfer drop available
    mirror([side<0?1:0,0,0]) difference() {
        union() {                       // block + 45° print chamfer:
            translate([rail_x0, 0, bz0])     // tip on the spine, grows
                cube([spine_hw-rail_x0-2, rail_d, spine_top-2-bz0]);
            if (ch > 0.5)                    // out/up at 45° — standing
                translate([rail_x0, 0, bz0]) // print stays support-free
                    rotate([0,90,0]) linear_extrude(spine_hw-rail_x0-2)
                        polygon([[0,0],[0,ch],[ch,0]]);
        }
        translate([rail_x0-eps, groove_y0, z_stop])     // board groove
            cube([3.6, pb_t+0.6, spine_top]);
        for (zz=screw_z)                                // M3 pilots
            translate([rail_x0-eps, groove_y0+pb_t+3, zz])
                rotate([0,90,0]) cylinder(d=pilot_d, h=spine_hw-rail_x0);
    }
}

module core() {
    difference() {
        union() {
            // floor: D slab + band back to the wall plane
            linear_extrude(floor_t) union() {
                Dprof(R_cup_out);
                translate([-spine_hw, -spine_t]) square([2*spine_hw, spine_t+1]);
            }
            // cup wall
            Dring(R_cup_in, cup_t, floor_t, cup_top);
            // top flange: hood seat + snap groove lives here
            Dring(R_cup_in, flange_r-R_cup_in, cup_top-6, cup_top);
            // spine (also the cup's flat back wall), full height
            translate([-spine_hw, -spine_t, 0])
                cube([2*spine_hw, spine_t, spine_top]);
            // gussets: spine ↔ floor, 45°, outside the fence
            for (sx=[-1,1]) mirror([sx<0?1:0,0,0])
                translate([26, 0, floor_t]) rotate([90,0,90])
                    linear_extrude(2) polygon([[0,0],[12,0],[0,12]]);
            // perfboard rails
            rail_block(1); rail_block(-1);
            // zip post, cable side +x. Basic: sits on the floor.
            // Plus: hangs off the spine with a 45° chamfer below.
            translate([10, 0, is_plus ? pm_bay_h-4 : floor_t]) {
                difference() {
                    cube([10, groove_y0-0.5, 8]);
                    translate([5,-eps,4]) rotate([-90,0,0])
                        cylinder(d=4, h=groove_y0+2*eps);
                }
                if (is_plus) rotate([0,90,0]) linear_extrude(10)
                    polygon([[0,0],[0,groove_y0-0.5],[groove_y0-0.5,0]]);
            }
            if (is_plus) {
                // HM3301 fence
                difference() {
                    translate([-fence_l/2-fence_t, hm_cy-fence_w/2-fence_t, floor_t])
                        cube([fence_l+2*fence_t, fence_w+2*fence_t, fence_h]);
                    translate([-fence_l/2, hm_cy-fence_w/2, floor_t-eps])
                        cube([fence_l, fence_w, fence_h+2*eps]);
                }
                // snap fingers over the can, both 40 mm sides
                for (sx=[-1,1]) mirror([sx<0?1:0,0,0])
                    translate([fence_l/2+1.6, hm_cy-4, floor_t]) {
                        cube([2, 8, hm_h+4.5]);
                        translate([-1.5, 0, hm_h-0.1]) {
                            cube([1.5, 8, 1.6]);
                            translate([0,0,1.6]) rotate([0,45,0])
                                cube([1.5, 8, 1.5]);
                        }
                    }
            }
        }
        // snap groove ring in the flange outer face
        translate([0,0,cup_top-4.9]) linear_extrude(2)
            difference() { Dprof(flange_r+1); Dprof(flange_r-0.55); }
        // keyholes (hang on pre-driven screws, pan head ≤ Ø8)
        for (p=[[-19, spine_top-16],[19, spine_top-16],
                [-14, z_stop+14],  [14, z_stop+14]])
            translate([p[0], -spine_t, p[1]]) keyhole();
        if (is_plus) {
            // mesh windows: inlet | 8 mm isolation band | outlet
            for (sx=[-1,1])
                translate([sx*(4+win_w/2)-win_w/2, hm_cy-win_l/2, -eps])
                    cube([win_w, win_l, floor_t+2*eps]);
            // mesh pocket (sheet drops in, sensor face clamps it)
            translate([-mesh_x/2, hm_cy-mesh_y/2, floor_t-0.6])
                cube([mesh_x, mesh_y, 0.6+eps]);
        } else {
            // basic: chimney intake slots in the floor
            for (xx=[-21:7:21])
                translate([xx-1.5, 8, -eps]) cube([3, 26, floor_t+2*eps]);
        }
        // condensation weeps
        for (xx=[-15,15]) translate([xx, 2.2, -eps])
            cylinder(d=3, h=floor_t+2*eps);
        // cable exit: arch through cup wall + floor, right side
        translate([24, 18, -eps]) cube([R_cup_out+13-24, 8, floor_t+2*eps]);
        translate([24, 18, floor_t-eps]) cube([R_cup_out+13-24, 8, 6]);
    }
}

// ============================================================
// HOOD — skirted D shell + cone spire. PRINT INVERTED.
// ============================================================
// 45° skirt: root crosses the wall thickness (volumetric weld),
// tip drops past the vent's bottom edge — no horizontal sight line.
sk_drop = r_brim - R_hood_in;    // 9.6
module skirt(z_root) {
    translate([0,0,z_root-sk_drop]) intersection() {
        translate([0,cy,0]) rotate_extrude()
            polygon([[R_hood_in, sk_drop], [r_brim, 0],
                     [r_brim, -skirt_t], [R_hood_in, sk_drop-skirt_t]]);
        half_y();
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

module above_cone_underside() {  // trims ribs/towers/backwall to the cone
    translate([0,0,cone_z0]) translate([0,cy,0]) rotate_extrude()
        polygon([[r_brim, 0], [cone_tip, cone_h],
                 [cone_tip, cone_h+99], [r_brim+99, cone_h+99], [r_brim+99, 0]]);
}

module vent_ribs(z0, z1) {
    for (az=rib_az) translate([0,cy,0]) rotate([0,0,az])
        translate([R_hood_in-0.3, -0.8, z0]) cube([shell+0.6, 1.6, z1-z0]);
}

module hood() {
    union() {
        difference() {
            union() {
                // body bands
                Dring(R_hood_in, shell, rim_z, g_lo0);        // lower
                Dring(R_hood_in, shell, g_lo1, g_hi0);        // upper
                // skirt over the intake vent (root welds 1.5 into band)
                skirt(g_lo1+1.5);
                // vent webs
                vent_ribs(g_lo0, g_lo1);
                vent_ribs(g_hi0, g_hi1+4);
                // back wall above the spine (cone zone), 0.4 off spine face
                translate([-hood_chw, 0.4, spine_top+0.4])
                    cube([2*hood_chw, 1.6, z_tip-spine_top]);
                // its foot: covers the slit over the spine top
                translate([-hood_chw, -1.8, spine_top+0.4])
                    cube([2*hood_chw, 2.2+1.6, 2]);
                // chord-edge towers: C-channels riding the spine edges
                for (sx=[-1,1]) mirror([sx<0?1:0,0,0]) {
                    translate([spine_hw+0.4, -2.1, rim_z])
                        cube([1.8, 6.1, spine_top+2-rim_z]);     // cheek
                    translate([spine_hw-2.1, 0.4, rim_z])
                        cube([4.3, 1.6, spine_top+2-rim_z]);     // lip
                }
                // snap nubs near the rim, engage the cup flange groove
                for (az=nub_az) translate([0,cy,0]) rotate([0,0,az])
                    translate([R_hood_in, 0, rim_z+1.55])
                        rotate([0,-90,0]) cylinder(d1=4, d2=2.2, h=0.55);
            }
            above_cone_underside();
            if (use_screws)
                for (sx=[-1,1]) for (zz=screw_z)
                    translate([sx>0 ? R_hood_out+eps : -R_hood_out-eps,
                               groove_y0+pb_t+3, zz])
                        rotate([0, sx>0?-90:90, 0]) cylinder(d=3.4, h=12);
        }
        cone_shell();
    }
}

// ============================================================
// preview dummies
// ============================================================
module dummies() {
    color("ForestGreen") translate([-pb_w/2, groove_y0, z_stop])
        cube([pb_w, pb_t, pb_h]);
    color("DimGray") translate([-10.5, groove_y0+pb_t, z_board_top-22])
        cube([21, 9, 17.8]);                       // XIAO, top of board
    color("MediumPurple") translate([6, groove_y0+pb_t, z_stop+6])
        cube([15, 11, 13]);                        // BME680, bottom
    if (is_plus) color("Silver")
        translate([-hm_l/2, hm_cy-hm_w/2, floor_t])
            cube([hm_l, hm_w, hm_h]);              // HM3301, face down
}

// ============================================================
// output, print-oriented
// ============================================================
module hood_printed() { translate([0,0,z_tip]) rotate([180,0,0]) hood(); }

if (part=="core") core();
else if (part=="hood") hood_printed();
else if (part=="plate") {
    translate([-48, 0, 0]) core();
    translate([ 50, 0, 0]) hood_printed();
}
else { core(); hood(); if (show_dummies) dummies(); }

echo(str("== ", variant, " ==  body Ø", 2*R_hood_out,
     "  max Ø", 2*r_brim, "  H=", z_tip,
     "  board z ", z_stop, "→", z_board_top,
     "  vents z ", g_lo0, "-", g_lo1, " / ", g_hi0, "-", g_hi1,
     "  cone z0 ", cone_z0));
