// ============================================================
// Making Sense Bali — DIY Node enclosure v1 "box" (ARCHIVED)
// ============================================================
// Status: superseded, see ../../README.md and ../README.md.
// Never printed. Rejected in design review: flat panels and
// slot louvers are laser-cutter thinking — it under-uses FDM
// (see v2 onward). Also sized for the BARE HM3301 can, not the
// 80×40 Grove carrier the kit actually buys (the v3 lesson).
// Kept for the design lineage and as workshop teaching material.
//
// Louvered Stevenson-screen box, three flat-printable PETG parts:
//   part = "chassis" | "floor" | "hood" | "assembly"
//   variant = "basic" | "plus"
// ============================================================

variant = "plus";      // ["basic", "plus"]
part    = "assembly";  // ["chassis", "floor", "hood", "assembly"]
show_dummies = true;

// ---------- components (datasheet / measured) ----------
pb_w = 50;  pb_h = 70;  pb_t = 1.6;   // 5×7 perfboard (v1-era spec)
hm_l = 40;  hm_w = 38;  hm_h = 15;    // bare HM3301 can — WRONG part,
hm_top_extra = 7;                     // the Grove module is 80×40!

// ---------- print / fit ----------
wall = 2.4;  plate_t = 2.4;  floor_t = 2.4;
slide_fit = 0.3;  drop_fit = 0.8;

// ---------- interior ----------
in_w = 58;  in_d = 44;

// ---------- louvers ----------
lv_pitch = 6;  lv_slot = 3.8;  lv_proj = 8.6;  lv_blade_t = 1.2;
lv_rows_lo = 5;  lv_rows_hi = 3;

// ---------- mounting ----------
keyhole_head = 8;  keyhole_slot = 4.2;
pilot_d = 2.5;  thru_d = 3.4;

// ---------- derived ----------
is_plus  = (variant == "plus");
pm_bay_h = hm_h + hm_top_extra + 4;
z_stop   = floor_t + (is_plus ? pm_bay_h + 3 : 5);
z_board_top = z_stop + pb_h;
z_roof_in   = z_board_top + 6;
z_plate_top = z_roof_in - 1;
roof_t = 3;  roof_oh = 10;
hx = in_w/2;
hood_in_x = hx + 0.4;  hood_out_x = hood_in_x + wall;
front_in = in_d;  front_out = in_d + wall;
hood_back = -plate_t + 0.2;
side_len  = front_in - hood_back;
groove_y0 = 4.5;  rail_x0 = 22;  rail_d = 12;
screw_z = [z_stop+8, z_stop+63];
fence_l = hm_l + drop_fit;  fence_w = hm_w + drop_fit;
fence_t = 2.0;  fence_h = 8;  hm_cy = in_d/2;
win_w = 13;  win_l = 30;  mesh_x = 36;  mesh_y = 34;
z_band_lo = z_stop + 4;
z_band_hi = z_roof_in - lv_rows_hi*lv_pitch - 4;
floor_x = hood_in_x - 0.2;
floor_y0 = hood_back;  floor_y1 = front_in - 0.2;
eps = 0.01;  $fn = 40;

module keyhole() {
    translate([0,-eps,0]) rotate([-90,0,0]) {
        cylinder(d=keyhole_head, h=plate_t+2*eps);
        translate([-keyhole_slot/2,-10,0])
            cube([keyhole_slot, 10, plate_t+2*eps]);
        translate([0,-10,0]) cylinder(d=keyhole_slot, h=plate_t+2*eps);
    }
}
module blade(len) {
    rotate([90,0,90]) linear_extrude(len)
        polygon([[-0.6, lv_slot+1.4], [-0.6, lv_slot+2.6],
                 [lv_proj, lv_slot+2.6-(lv_proj+0.6)],
                 [lv_proj, lv_slot+1.4-(lv_proj+0.6)]]);
}
module rail_block(side) {
    mirror([side<0?1:0, 0, 0]) difference() {
        translate([rail_x0, 0, z_stop-3])
            cube([hx-rail_x0, rail_d, (z_plate_top-4)-(z_stop-3)]);
        translate([rail_x0-eps, groove_y0, z_stop])
            cube([3.6, pb_t+0.6, z_plate_top]);
        for (zz=screw_z)
            translate([rail_x0-eps, groove_y0+pb_t+3, zz])
                rotate([0,90,0]) cylinder(d=pilot_d, h=hx-rail_x0+2*eps);
    }
}
module chassis() {
    difference() {
        union() {
            translate([-hx, -plate_t, floor_t])
                cube([in_w, plate_t, z_plate_top-floor_t]);
            rail_block(1); rail_block(-1);
            translate([10, 0, is_plus ? pm_bay_h-4 : floor_t]) {
                difference() {
                    cube([10, groove_y0-0.5, 8]);
                    translate([5,-eps,4]) rotate([-90,0,0])
                        cylinder(d=4, h=groove_y0+2*eps);
                }
                if (is_plus) rotate([0,90,0]) linear_extrude(10)
                    polygon([[0,0],[0,groove_y0-0.5],[groove_y0-0.5,0]]);
            }
            for (xx=[-14,14]) translate([xx-3, -plate_t, 0]) {
                cube([6, plate_t, floor_t+eps]);
                translate([0,-eps,-2]) cube([6, plate_t, 2+eps]);
                translate([0, plate_t-eps, -2]) cube([6, 2.5, 2]);
            }
        }
        for (p=[[-19, z_plate_top-16],[19, z_plate_top-16],
                [-14, z_stop+14],    [14, z_stop+14]])
            translate([p[0], -plate_t, p[1]]) keyhole();
    }
}
module floor_plate() {
    difference() {
        union() {
            translate([-floor_x, floor_y0, 0])
                cube([2*floor_x, floor_y1-floor_y0, floor_t]);
            lip = 2;
            difference() {
                translate([-floor_x+1, floor_y0+1, floor_t])
                    cube([2*floor_x-2, floor_y1-floor_y0-2, 4]);
                translate([-floor_x+1+lip, floor_y0+1+lip, floor_t-eps])
                    cube([2*floor_x-2-2*lip, floor_y1-floor_y0-2-2*lip, 4+2*eps]);
            }
            if (is_plus) {
                difference() {
                    translate([-fence_l/2-fence_t, hm_cy-fence_w/2-fence_t, floor_t])
                        cube([fence_l+2*fence_t, fence_w+2*fence_t, fence_h]);
                    translate([-fence_l/2, hm_cy-fence_w/2, floor_t-eps])
                        cube([fence_l, fence_w, fence_h+2*eps]);
                }
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
        if (is_plus) {
            for (sx=[-1,1])
                translate([sx*(4+win_w/2)-win_w/2, hm_cy-win_l/2, -eps])
                    cube([win_w, win_l, floor_t+2*eps]);
            translate([-mesh_x/2, hm_cy-mesh_y/2, floor_t-0.6])
                cube([mesh_x, mesh_y, 0.6+eps]);
        } else {
            for (xx=[-21:7:21])
                translate([xx-1.5, 8, -eps]) cube([3, in_d-20, floor_t+2*eps]);
        }
        for (xx=[-10,10])
            translate([xx-3, floor_y0+1.2, -eps]) cube([6, 2, floor_t+2*eps]);
        for (xx=[-14,14])
            translate([xx-3.3, -plate_t-0.3, -eps])
                cube([6.6, plate_t+0.4, floor_t+2*eps]);
        translate([24, 18, -eps]) cube([floor_x-24+eps, 8, floor_t+2*eps]);
    }
}
module hood() {
    difference() {
        union() {
            translate([-hood_out_x, front_in, 1])
                cube([2*hood_out_x, wall, z_roof_in-1]);
            for (sx=[-1,1])
                translate([sx>0 ? hood_in_x : -hood_out_x, hood_back, 1])
                    cube([wall, side_len, z_roof_in-1]);
            translate([-hood_out_x-roof_oh, hood_back, z_roof_in])
                cube([2*(hood_out_x+roof_oh),
                      front_out+roof_oh-hood_back, roof_t]);
        }
        difference() {
            translate([-hood_out_x-roof_oh+4, hood_back+4, z_roof_in-eps])
                cube([2*(hood_out_x+roof_oh)-8,
                      front_out+roof_oh-hood_back-8, 1]);
            translate([-hood_out_x-roof_oh+6, hood_back+6, z_roof_in-2*eps])
                cube([2*(hood_out_x+roof_oh)-12,
                      front_out+roof_oh-hood_back-12, 1+4*eps]);
        }
        for (zb=[z_band_lo, z_band_hi]) {
            rows = (zb==z_band_lo) ? lv_rows_lo : lv_rows_hi;
            for (i=[0:rows-1]) {
                translate([-hood_in_x+6, front_in-eps, zb+i*lv_pitch])
                    cube([2*hood_in_x-12, wall+2*eps, lv_slot]);
                for (sx=[-1,1])
                    translate([sx>0 ? hood_in_x-eps : -hood_out_x-eps,
                               hood_back+6, zb+i*lv_pitch])
                        cube([wall+2*eps, side_len-12, lv_slot]);
            }
        }
        for (sx=[-1,1]) for (zz=screw_z)
            translate([sx*(hood_out_x+eps), groove_y0+pb_t+3, zz])
                rotate([0, sx>0?-90:90, 0]) {
                    cylinder(d=thru_d, h=wall+2*eps);
                    cylinder(d=6.2, h=1.2);
                }
        translate([hood_in_x-eps, 17.5, 1-eps])
            cube([wall+2*eps, 9, 6]);
    }
    for (zb=[z_band_lo, z_band_hi]) {
        rows = (zb==z_band_lo) ? lv_rows_lo : lv_rows_hi;
        for (i=[0:rows-1]) {
            translate([-hood_in_x+6, front_out, zb+i*lv_pitch])
                blade(2*hood_in_x-12);
            translate([hood_out_x, front_in-6, zb+i*lv_pitch])
                rotate([0,0,-90]) blade(side_len-12);
            translate([-hood_out_x, hood_back+6, zb+i*lv_pitch])
                rotate([0,0,90]) blade(side_len-12);
        }
    }
}
module dummies() {
    color("ForestGreen") translate([-pb_w/2, groove_y0, z_stop])
        cube([pb_w, pb_t, pb_h]);
    color("DimGray") translate([-10.5, groove_y0+pb_t, z_board_top-22])
        cube([21, 9, 17.8]);
    color("MediumPurple") translate([6, groove_y0+pb_t, z_stop+6])
        cube([15, 11, 13]);
    if (is_plus) color("Silver")
        translate([-hm_l/2, hm_cy-hm_w/2, floor_t])
            cube([hm_l, hm_w, hm_h]);
}
if (part=="chassis")
    rotate([90,0,0]) translate([0, plate_t, 0]) chassis();
else if (part=="floor") floor_plate();
else if (part=="hood")
    translate([0,0,z_roof_in+roof_t]) rotate([180,0,0]) hood();
else { chassis(); floor_plate(); hood(); if (show_dummies) dummies(); }

echo(str("== v1 ", variant, " ==  body W=", 2*hood_out_x,
     "  roof W=", 2*(hood_out_x+roof_oh),
     "  D=", front_out+roof_oh-hood_back, "  H=", z_roof_in+roof_t));
