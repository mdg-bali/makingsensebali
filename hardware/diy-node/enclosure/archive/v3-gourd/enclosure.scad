// ============================================================
// Making Sense Bali — DIY Node enclosure v3  "gourd"
// ============================================================
// FDM-native outdoor enclosure for the XIAO ESP32-S3 + BME680
// (+ Grove HM3301 module) Smart Citizen DIY node.
//
// v3 fixes (from a real v2 print):
//  * PM bay now fits the FULL Grove module — the bare HM3301 can
//    (40×38×15) sits on an 80×40 carrier PCB. Dimensions taken
//    from Seeed's Eagle .brd: outline 80×40, Ø3.2 mounting holes
//    at (±36,±16), Grove socket left end, pigtail header right.
//    Module mounts inverted: can face-down over mesh windows.
//  * The hood↔core joint actually closes: hard shoulder stop on
//    the foot, 0.5 mm radial clearances, chamfered lead-ins, and
//    two M3 screws into foot bosses. No more wishful snap nubs.
//  * Downsized: perfboard spec drops to 4×6 cm (a XIAO + BME680
//    barely fills a 5×7). Slim body Ø~60; only the foot is wide,
//    because the module is 80 mm long and physics doesn't care.
//
// Two printed parts, support-free:
//   core — foot + module cradle + floor + mounting spine.
//          Prints standing on its floor.
//   hood — collar + loft + body + skirt vents + cone spire.
//          Prints inverted, spire cap on the bed (use a brim).
//
//   variant = "basic" | "plus"
//   part    = "core" | "hood" | "assembly" | "plate"
//
// Material: white PETG. PLA softens on Bali rooftops — don't.
// License: MIT (parent repo).
// ============================================================

// ---------- what to render ----------
variant = "plus";      // ["basic", "plus"]
part    = "assembly";  // ["core", "hood", "assembly", "plate"]
show_dummies = true;

// ---------- components ----------
pb_w = 40;  pb_h = 60;  pb_t = 1.6;   // 4×6 cm perfboard
crr_l = 80; crr_w = 40; crr_t = 1.6;  // HM3301 Grove carrier (Eagle)
hole_dx = 36; hole_dy = 16;           // carrier holes ±36, ±16, Ø3.2
can_l = 40; can_w = 38; can_h = 15;   // bare sensor can on carrier
can_cx = -5;   // can centre offset along carrier (measure yours;
               // socket end = -40, pigtail end = +40)

// ---------- shells / fit ----------
shell   = 1.6;   floor_t = 2.0;   spine_t = 2.4;   foot_t = 1.8;
skirt_t = 1.3;
fit     = 0.5;   // radial joint clearance (printed v2 jammed at 0.2)
drop    = 0.8;   // drop-in clearance

// ---------- plan geometry ----------
// upper body: D-section for the 40-wide board
R_up = 28;  cy = 10;                  // inner radius, centre offset
// foot: rounded rectangle for the 80×40 module (plus only)
foot_ix = 84;  foot_iy = 44;  foot_r = 9;   // interior, corner r
// basic cup: small D
R_cupb = 25.5;

skirt_p  = 6;       // skirt projection
cone_tip = 8;
spine_hw = 23;      // spine half-width (46 wide)

// ---------- fasteners ----------
keyhole_head = 8;  keyhole_slot = 4.2;
pilot_d = 2.5;  thru_d = 3.4;         // M3 joint screws ×2

// ---------- derived: vertical stack ----------
is_plus  = (variant=="plus");
bay_h    = can_h + crr_t + 4.5;               // 21: can+pcb+fingers
cup_top  = floor_t + (is_plus ? bay_h + 2 : 8);   // 25 / 10
loft_h   = 16;     // plus: foot → body; keeps the flare ≤45° in print
z_stop   = is_plus ? cup_top + loft_h - 3 : cup_top + 4;  // board btm
z_board_top = z_stop + pb_h;
spine_top   = z_board_top + 2;
g_lo0 = z_stop + 4;        g_lo1 = g_lo0 + 8;  // intake vent
g_hi0 = z_board_top - 7;   g_hi1 = z_board_top + 1;
R_up_out = R_up + shell;
r_brim   = R_up_out + skirt_p + 1;             // 36.6
cone_z0  = g_hi1 - (r_brim - R_up_out) - 1.5;
cone_h   = r_brim - cone_tip;
z_tip    = cone_z0 + cone_h + 1.7;
sk_drop  = r_brim - R_up;

// joint
step_z   = cup_top - 3;        // shoulder height on the foot/cup
col_bot  = step_z + 0.3;       // hood collar bottom edge (hard stop)
hm_cy    = foot_iy/2;          // module centre, y = 22
boss_z   = cup_top - 5;        // joint screw axis height

eps = 0.01;
$fa = 3; $fs = 0.5;

// ============================================================
// 2D profiles
// ============================================================
module Dprof(r, c=cy) {        // D: flat at y=0, arc forward
    intersection() {
        translate([0,c]) circle(r);
        translate([-r-60,0]) square([2*r+120, r+c+60]);
    }
}
module rrect(ix, iy) {         // rounded rect, back edge at y=0
    translate([0, iy/2]) offset(r=foot_r)
        square([ix-2*foot_r, iy-2*foot_r], center=true);
}
function chwD(r,c) = sqrt(r*r - c*c);

// thin slice of a 2D profile at height z (for hull lofts)
module slice(z) { translate([0,0,z]) linear_extrude(0.02) children(); }

module half_y() { translate([-250,0.0,-60]) cube([500,500,500]); }

// ============================================================
// CORE — prints standing on its floor
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
    bz0 = max(z_stop-3, cup_top+1);
    rail_d = 11;
    mirror([side<0?1:0,0,0]) difference() {
        union() {
            translate([16.5, 0, bz0])
                cube([spine_hw-16.5-1, rail_d, spine_top-2-bz0]);
            // 45° chamfer below: tip on the spine, no overhang
            translate([16.5, 0, bz0]) rotate([0,90,0])
                linear_extrude(spine_hw-16.5-1)
                    polygon([[0,0],[0,rail_d],[rail_d,0]]);
        }
        translate([16.5-eps, 4.5, z_stop])     // board groove
            cube([3.1, pb_t+0.6, spine_top]);
    }
}

// foot outline (outer). Basic uses the small D cup instead.
module foot_out_prof()  { offset(r=foot_t) rrect(foot_ix, foot_iy); }
module foot_step_prof() { offset(r=foot_t-1.2) rrect(foot_ix, foot_iy); }

module core() {
    difference() {
        union() {
            // ---- floor ----
            linear_extrude(floor_t) union() {
                if (is_plus) foot_out_prof(); else Dprof(R_cupb+foot_t, cy);
                translate([-spine_hw, -spine_t]) square([2*spine_hw, spine_t+1]);
            }
            // ---- cup / foot wall, with shoulder step + chamfer ----
            if (is_plus) {
                linear_extrude(step_z) difference()
                    { foot_out_prof(); rrect(foot_ix, foot_iy); }
                linear_extrude(cup_top) difference()
                    { foot_step_prof(); rrect(foot_ix, foot_iy); }
                // 45° lead-in on the step top edge
                translate([0,0,cup_top-1]) linear_extrude(1) difference()
                    { foot_step_prof(); offset(delta=-1) foot_step_prof(); }
            } else {
                linear_extrude(step_z) difference()
                    { Dprof(R_cupb+foot_t, cy); Dprof(R_cupb, cy); }
                linear_extrude(cup_top) difference()
                    { Dprof(R_cupb+foot_t-1.2, cy); Dprof(R_cupb, cy); }
            }
            // ---- joint screw bosses, fused INSIDE the wall ----
            for (sx=[-1,1]) mirror([sx<0?1:0,0,0])
                translate([is_plus ? foot_ix/2-5 : chwD(R_cupb,cy)-5,
                           (is_plus ? hm_cy : cy)-5, boss_z-5])
                    cube([5.5, 10, 10]);
            // ---- spine ----
            translate([-spine_hw, -spine_t, 0])
                cube([2*spine_hw, spine_t, spine_top]);
            // gussets, clear of the can (can spans x -25..15)
            for (sx=[-1,1]) mirror([sx<0?1:0,0,0])
                translate([20, 0, floor_t]) rotate([90,0,90])
                    linear_extrude(2) polygon([[0,0],[10,0],[0,10]]);
            // rails
            rail_block(1); rail_block(-1);
            // zip post
            translate([8, 0, is_plus ? cup_top+1 : floor_t]) {
                difference() {
                    cube([8, 4, 8]);
                    translate([4,-eps,4]) rotate([-90,0,0])
                        cylinder(d=4, h=5);
                }
                if (is_plus) rotate([0,90,0]) linear_extrude(8)
                    polygon([[0,0],[0,4],[4,0]]);
            }
            if (is_plus) {
                // ---- module cradle: 4 posts + pegs (Eagle: ±36,±16) ----
                for (px=[-hole_dx,hole_dx]) for (py=[-hole_dy,hole_dy])
                    translate([px, hm_cy+py, 0]) {
                        cylinder(d=7, h=floor_t+can_h);
                        cylinder(d=2.8, h=floor_t+can_h+crr_t+1.8);
                    }
                // two fingers over the carrier's long edges
                for (fy=[0.2, foot_iy-1.8])
                    translate([can_cx-4, fy, floor_t]) {
                        cube([8, 1.6, can_h+crr_t+3]);
                        translate([0, fy<2 ? 1.6 : -1.2, can_h+crr_t-0.1]) {
                            cube([8, 1.2, 1.4]);
                            translate([0, fy<2 ? 0 : 1.2, 1.4])
                                rotate([fy<2 ? -45 : 225, 0, 0])
                                    cube([8, 1.2, 1.4]);   // lead-in
                        }
                    }
            }
        }
        // keyholes
        for (p=[[-15, spine_top-14],[15, spine_top-14],
                [-12, z_stop+12],  [12, z_stop+12]])
            translate([p[0], -spine_t, p[1]]) keyhole();
        // joint screw pilots (axis x)
        for (sx=[-1,1])
            translate([sx*(is_plus ? foot_ix/2+foot_t+eps
                                   : chwD(R_cupb,cy)+foot_t+eps),
                       hm_cy*(is_plus?1:0) + (is_plus?0:cy), boss_z])
                rotate([0, sx>0?-90:90, 0]) cylinder(d=pilot_d, h=9);
        if (is_plus) {
            // mesh windows under the can (inlet | 8 mm band | outlet)
            for (sx=[-1,1])
                translate([can_cx+sx*(4+13/2)-13/2, hm_cy-14, -eps])
                    cube([13, 28, floor_t+2*eps]);
            // mesh pocket
            translate([can_cx-18, hm_cy-17, floor_t-0.6])
                cube([36, 34, 0.6+eps]);
            // cable arch, right end wall
            translate([foot_ix/2-2, hm_cy-4, -eps])
                cube([foot_t+4, 8, floor_t+2*eps]);
            translate([foot_ix/2-2, hm_cy-4, floor_t-eps])
                cube([foot_t+4, 8, 6]);
        } else {
            for (xx=[-15:6:15])
                translate([xx-1.5, 6, -eps]) cube([3, 22, floor_t+2*eps]);
            translate([chwD(R_cupb,cy)-2, cy+6, -eps])
                { cube([foot_t+4, 8, floor_t+2*eps]); }
            translate([chwD(R_cupb,cy)-2, cy+6, floor_t-eps])
                cube([foot_t+4, 8, 6]);
        }
        // condensation weeps
        for (xx=[-12,12]) translate([xx, 2.2, -eps])
            cylinder(d=3, h=floor_t+2*eps);
    }
}

// ============================================================
// HOOD — prints inverted (spire cap on the bed)
// ============================================================
module Dring(r_in, t, z0, z1, c=cy) {
    translate([0,0,z0]) linear_extrude(z1-z0)
        difference() { Dprof(r_in+t, c); Dprof(r_in, c); }
}
module skirt(z_root) {
    translate([0,0,z_root-sk_drop]) intersection() {
        translate([0,cy,0]) rotate_extrude()
            polygon([[R_up, sk_drop], [r_brim, 0],
                     [r_brim, -skirt_t], [R_up, sk_drop-skirt_t]]);
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
module above_cone() {
    translate([0,0,cone_z0]) translate([0,cy,0]) rotate_extrude()
        polygon([[r_brim, 0], [cone_tip, cone_h],
                 [cone_tip, cone_h+99], [r_brim+99, cone_h+99], [r_brim+99, 0]]);
}
module vent_ribs(z0, z1) {
    for (az=[0,45,90,135,180]) translate([0,cy,0]) rotate([0,0,az])
        translate([R_up-0.3, -0.8, z0]) cube([shell+0.6, 1.6, z1-z0]);
}

// collar + loft profiles (hood side, with joint clearance)
module col_in_prof()  {
    if (is_plus) offset(r=fit) foot_step_prof();
    else offset(r=fit) Dprof(R_cupb+foot_t-1.2, cy);
}
module col_out_prof() { offset(r=fit+1.8) {
    if (is_plus) foot_step_prof(); else Dprof(R_cupb+foot_t-1.2, cy); } }

module hood() {
    body_z0 = is_plus ? cup_top + loft_h : cup_top;
    union() {
        difference() {
            union() {
                // collar: slides over the step, lands on the shoulder
                translate([0,0,col_bot]) linear_extrude(cup_top+1-col_bot)
                    difference() { col_out_prof(); col_in_prof(); }
                // loft: collar profile → upper body (hull of slices)
                if (is_plus) difference() {
                    hull() { slice(cup_top+0.9) col_out_prof();
                             slice(body_z0) Dprof(R_up_out, cy); }
                    hull() { slice(cup_top-eps) col_in_prof();
                             slice(body_z0+eps) Dprof(R_up, cy); }
                }
                // body bands
                Dring(R_up, shell, body_z0, g_lo0);
                Dring(R_up, shell, g_lo1, g_hi0);
                skirt(g_lo1+1.5);
                vent_ribs(g_lo0-eps, g_lo1+eps);
                vent_ribs(g_hi0-eps, g_hi1+4);
                // back wall above the spine + slit cover foot
                translate([-chwD(R_up,cy), 0.5, spine_top+0.5])
                    cube([2*chwD(R_up,cy), 1.6, z_tip-spine_top-1]);
                translate([-chwD(R_up,cy), -1.7, spine_top+0.5])
                    cube([2*chwD(R_up,cy), 2.2+1.6, 2]);
                // spine guide towers — START ABOVE THE CUP (v2 bug)
                for (sx=[-1,1]) mirror([sx<0?1:0,0,0]) {
                    translate([spine_hw+0.5, -2.1, body_z0+1])
                        cube([1.8, 6.3, spine_top+1-(body_z0+1)]); // cheek
                    translate([spine_hw-2.3, 0.5, body_z0+1])
                        cube([4.6, 1.6, spine_top+1-(body_z0+1)]); // lip
                }
            }
            above_cone();
            // joint screw holes through the collar, counterbored
            for (sx=[-1,1]) {
                bx = is_plus ? foot_ix/2+foot_t : chwD(R_cupb,cy)+foot_t;
                by = is_plus ? hm_cy : cy;
                translate([sx*(bx+fit+1.8+eps), by, boss_z])
                    rotate([0, sx>0?-90:90, 0]) {
                        cylinder(d=thru_d, h=6);
                        cylinder(d=6.4, h=1.4);
                    }
            }
        }
        cone_shell();
    }
}

// ============================================================
// preview dummies
// ============================================================
module dummies() {
    color("ForestGreen") translate([-pb_w/2, 4.5, z_stop])
        cube([pb_w, pb_t, pb_h]);
    color("DimGray") translate([-10.5, 4.5+pb_t, z_board_top-20])
        cube([21, 8, 17.8]);
    color("MediumPurple") translate([4, 4.5+pb_t, z_stop+5])
        cube([15, 10, 13]);
    if (is_plus) {
        color("Silver") translate([can_cx-can_l/2, hm_cy-can_w/2, floor_t])
            cube([can_l, can_w, can_h]);                  // can, face down
        color("DarkGreen") translate([-crr_l/2, hm_cy-crr_w/2, floor_t+can_h])
            cube([crr_l, crr_w, crr_t]);                  // carrier above
        color("White") translate([-crr_l/2, hm_cy-5, floor_t+can_h-6])
            cube([10, 10, 6]);                            // grove socket
    }
}

// ============================================================
// output, print-oriented
// ============================================================
module hood_printed() { translate([0,0,z_tip]) rotate([180,0,0]) hood(); }

if (part=="core") core();
else if (part=="hood") hood_printed();
else if (part=="plate") {
    translate([is_plus ? -52 : -42, 0, 0]) core();
    translate([ 42, 0, 0]) hood_printed();
}
else { core(); hood(); if (show_dummies) dummies(); }

echo(str("== ", variant, " v3 ==  body Ø", 2*R_up_out,
     "  brim Ø", 2*r_brim,
     is_plus ? str("  foot ", foot_ix+2*foot_t, "×", foot_iy+2*foot_t) : "",
     "  H=", z_tip, "  board z ", z_stop, "→", z_board_top,
     "  vents ", g_lo0, "-", g_lo1, " / ", g_hi0, "-", g_hi1));
