// Rail + Bracket assemblés - La Boîte à Coucou
//
// Le rail est vertical (Z). Le bracket est fixé sur la face gauche
// du rail (X=0), bras montant en Z, servo s'insérant par le haut.

// ===================================================================
// Paramètres rail (identiques à rail.scad)
// ===================================================================
rb_head_w    = 6.3;
rb_head_h    = 2.0;
rb_taper_h   = 1.5;
rb_stem_w    = 3.4;
rb_stem_h    = 1.5;
rb_cl        = 0.20;

rb_ihead_w   = rb_head_w + 2*rb_cl;
rb_istem_w   = rb_stem_w + 2*rb_cl;
rb_ihead_h   = rb_head_h + rb_cl;
rb_itaper_h  = rb_taper_h;
rb_istem_h   = rb_stem_h + rb_cl;

rb_wall      = 2.5;
rb_rail_h    = 120;

rb_inner_d   = rb_istem_h + rb_itaper_h + rb_ihead_h;
rb_rail_w    = rb_ihead_w + 2*rb_wall;   // ~11.7mm  (axe X)
rb_rail_d    = rb_inner_d + rb_wall;     // ~7.7mm   (axe Y)

// ===================================================================
// Paramètres bracket (identiques à bracket.scad)
// ===================================================================
br_servo_w   = 22.5;
br_body_cl   = 0.3;
br_thick     = 3.9;
br_extra     = 3.0;
br_ext       = 9.0;
br_ear_z     = 16.4;
br_ear_d     = 2.6;

br_inner_w   = br_servo_w + 2*br_body_cl;
br_total_w   = br_inner_w + 2*br_thick + 2*br_extra;  // ~36.9mm

br_fond_z    = br_ext + br_thick;
br_arm_h     = br_ear_z + br_thick + 3.0;
br_total_h   = br_fond_z + br_arm_h;

br_hole_z    = br_fond_z + br_ear_z;

br_lx        = br_extra + br_thick/2;
br_rx        = br_total_w - br_extra - br_thick/2;

// ===================================================================
// Module rail
// ===================================================================
module rail() {
    difference() {
        cube([rb_rail_w, rb_rail_d, rb_rail_h]);
        translate([rb_rail_w/2, 0, -0.1])
        linear_extrude(height = rb_rail_h + 0.2)
        polygon([
            [-rb_istem_w/2, 0],
            [ rb_istem_w/2, 0],
            [ rb_istem_w/2, rb_istem_h],
            [ rb_ihead_w/2, rb_istem_h + rb_itaper_h],
            [ rb_ihead_w/2, rb_istem_h + rb_itaper_h + rb_ihead_h],
            [-rb_ihead_w/2, rb_istem_h + rb_itaper_h + rb_ihead_h],
            [-rb_ihead_w/2, rb_istem_h + rb_itaper_h],
            [-rb_istem_w/2, rb_istem_h],
        ]);
    }
}

// ===================================================================
// Module bracket
// Repère natif : X=largeur (br_total_w), Y=épaisseur fond (br_thick), Z=hauteur
// Face Y=0 = fond (à coller contre le rail)
// Bras montent en Z, fins en X et Y
// ===================================================================
module bracket() {
    difference() {
        union() {
            // Fond : pleine largeur X, fin en Y, hauteur fond_z+thick
            cube([br_total_w, br_thick, br_fond_z + br_thick]);
            // Bras gauche
            translate([br_extra, 0, 0])
            cube([br_thick, br_thick, br_total_h]);
            // Bras droit
            translate([br_total_w - br_extra - br_thick, 0, 0])
            cube([br_thick, br_thick, br_total_h]);
        }
        // Trou oreille gauche (traverse en Y)
        translate([br_lx, -0.1, br_hole_z])
        rotate([-90, 0, 0])
        cylinder(d=br_ear_d, h=br_thick + 0.2, $fn=24);
        // Trou oreille droit
        translate([br_rx, -0.1, br_hole_z])
        rotate([-90, 0, 0])
        cylinder(d=br_ear_d, h=br_thick + 0.2, $fn=24);
    }
}

// ===================================================================
// Assemblage
//
// On veut :
//   - fond du bracket (face Y_nat=0) collé contre X=0 du rail (face gauche)
//   - bras montent en Z (inchangé)
//   - largeur du bracket centrée sur rb_rail_d/2 (profondeur du rail)
//
// rotate([0,0,-90]) : X_nat->-Y_new, Y_nat->X_new, Z_nat->Z_new
//   -> fond (Y_nat=0) -> X_new=0 ✓  (flush contre X=0 du rail)
//   -> largeur (X_nat=0..br_total_w) -> Y_new=0..-br_total_w (vers Y-)
//   -> bras restent en Z ✓
//
// translate Y : ramener de Y- vers Y+ et centrer sur rb_rail_d/2
//   offset_y = rb_rail_d/2 + br_total_w/2
// ===================================================================
union() {
    rail();
    rotate([0, 0, -90])
    rotate([0, 90, 0])
    translate([-br_total_h - 0.7, -br_thick, -rb_rail_d+1])
    bracket();
}
