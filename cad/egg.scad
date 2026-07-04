// Oeuf - La Boîte à Coucou
//
// Deux demi-ellipsoïdes joints à Z=0, même rayon équatorial -> jointure invisible.
//   - haut : élancé   (h_top=30mm)
//   - bas  : écrasé   (h_bot=22mm), tronqué à flat_cut=3mm du bas
//
// Base : encoche en creux au profil de la tige de la crémaillère (stem)
// pour emboîter l'œuf sur l'extrémité haute du rack.

eq_r     = 22.5;
h_top    = 30;
h_bot    = 22;
flat_cut = 3;

big = 200;

// Profil complet crémaillère (T inversé) - identique à rack.scad
head_w   = 6.3;
head_h   = 2.0;
taper_h  = 1.5;
stem_w   = 3.4;
stem_h   = 1.5;
rack_total_h = head_h + taper_h + stem_h;  // 5.0mm

// Encoche : profil T + jeu 0.3mm partout + profondeur = rack_total_h + 1mm marge
slot_cl  = 0.3;
slot_depth = rack_total_h + 1.0;  // 6mm

z_bottom = -(h_bot - flat_cut);  // Z du bas de l'œuf = -19mm

difference() {
    union() {
        // Moitié haute (Z >= 0)
        intersection() {
            scale([eq_r, eq_r, h_top]) sphere(r=1, $fn=128);
            translate([0, 0, big/2]) cube(big, center=true);
        }
        // Moitié basse tronquée
        intersection() {
            scale([eq_r, eq_r, h_bot]) sphere(r=1, $fn=128);
            translate([0, 0, -(h_bot - flat_cut)/2])
            cube([big, big, h_bot - flat_cut], center=true);
        }
    }

    // Encoche profil T inversé - ouverte vers le bas, centrée XY
    translate([0, 0, z_bottom - 0.1])
    linear_extrude(height = slot_depth + 0.1)
    polygon([
        // tige (haut du T)
        [-(stem_w/2 + slot_cl),  0],
        [ (stem_w/2 + slot_cl),  0],
        [ (stem_w/2 + slot_cl),  stem_h + slot_cl],
        // trapèze
        [ (head_w/2 + slot_cl),  stem_h + taper_h + slot_cl],
        // base large (bas du T)
        [ (head_w/2 + slot_cl),  stem_h + taper_h + head_h + slot_cl],
        [-(head_w/2 + slot_cl),  stem_h + taper_h + head_h + slot_cl],
        [-(head_w/2 + slot_cl),  stem_h + taper_h + slot_cl],
        [-(stem_w/2 + slot_cl),  stem_h + slot_cl],
    ]);
}
