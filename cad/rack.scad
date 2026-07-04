// Crémaillère (rack) avec profil évasé - La Boîte à Coucou
//
// Construction 100% sans rotation :
//   X = longueur (0 -> rack_length)
//   Y = largeur  (centré sur 0 : -head_w/2 -> +head_w/2)
//   Z = hauteur  (0 = bas)
//
// Le corps est construit par hull() de sphères/cylindres directement
// dans le bon repère. Les dents idem.

gear_module  = 2;
rack_length  = 110;

head_w  =  6.3;
head_h  =  2.0;
head_r  =  0.8;
taper_h =  1.5;
stem_w  =  3.4;
stem_h  =  1.5;

tooth_pitch = gear_module * PI;
num_teeth   = floor(rack_length / tooth_pitch);
tooth_h     = gear_module * 1.2 + 1;  // +1mm par rapport au calcul théorique

total_body_h = head_h + taper_h + stem_h;

// =====================================================
// Corps - construit par hull de sphères
// 4 coins de la base arrondie × 2 extrémités X = 8 sphères
// + trapèze via hull entre base large et tige
// =====================================================
module rack_body() {
    union() {
        // Base arrondie + trapèze en un seul hull :
        // coins arrondis en bas + arêtes de la tige en haut
        hull() {
            // 8 sphères pour les coins arrondis de la base
            for (xe = [head_r, rack_length - head_r])
            for (ye = [-(head_w/2 - head_r), (head_w/2 - head_r)])
            for (ze = [head_r, head_h - head_r])
                translate([xe, ye, ze])
                sphere(r = head_r, $fn = 16);

            // 4 coins de la tige en haut (petit cube mince)
            translate([0, -stem_w/2, head_h + taper_h])
            cube([rack_length, stem_w, 0.01]);
        }

        // Tige
        translate([0, -stem_w/2, head_h + taper_h - 0.1])
        cube([rack_length, stem_w, stem_h + 0.1]);
    }
}

// =====================================================
// Une dent - trapèze dans le plan XZ, extrudé en Y
// =====================================================
module rack_tooth() {
    top_w  = tooth_pitch * 0.05;  // sommet quasi-pointu
    base_w = tooth_pitch * 0.88;  // base large - les dents se touchent presque

    // hull de 4 arêtes (segments) pour un trapèze propre en 3D
    hull() {
        // base de la dent
        translate([-base_w/2, -stem_w/2, 0]) cube([base_w, stem_w, 0.01]);
        // sommet de la dent
        translate([-top_w/2,  -stem_w/2, tooth_h]) cube([top_w,  stem_w, 0.01]);
    }
}

// =====================================================
// Assemblage
// =====================================================
union() {
    rack_body();

    for (i = [0 : num_teeth - 2]) {
        translate([
            tooth_pitch / 2 + i * tooth_pitch,
            0,
            total_body_h
        ])
        rack_tooth();
    }
}
