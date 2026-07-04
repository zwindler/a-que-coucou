// Murs de la boîte - La Boîte à Coucou
//
// Tube carré monobloc (4 murs solidaires), ouvert en haut et en bas.
// Tenon 2x2mm en bas qui s'insère dans la rainure périphérique de base.scad.
//
// PoC : hauteur 20mm, pas de trou, pas de grille.
// Version finale : ajuster wall_h, ajouter trou câble Ø10mm côté Y-.
// ===================================================================

base_x   = 120;
base_y   = 120;
wall_t   = 3;    // épaisseur des murs
wall_h   = 180;  // hauteur finale 18cm

// Tenon correspondant à la rainure de base.scad
// groove_w=2, groove_d=2, collée au bord extérieur
tenon_w  = 2;
tenon_h  = 2;
cl       = 0;  // pas de jeu - filament bien calibré

// Dimensions réelles avec jeu
box_x    = base_x - 2*cl;
box_y    = base_y - 2*cl;

// Trou câble USB-C - mur Y- (côté Pi), centré en X
// Connecteur RPi5 USB-C : 7x12mm -> trou 8x13mm (1mm jeu)
usbc_w   = 13;   // largeur trou (axe X)
usbc_h   = 8;    // hauteur trou (axe Z)
usbc_z   = 2;    // distance du bas

// Trous haut-parleur - mur X+ (mur droit vu de la face USB-C), centrés en Y
spk_d    = 2.5;  // Ø M2.5
spk_z    = wall_h - 25;  // à 25mm du haut
spk_entraxe = 36;

// Trou micro - mur X- (mur gauche vu de la face USB-C), centré en Y, même hauteur que speaker
mic_d    = 2.5;  // Ø M2.5

// groove_w=2mm de chaque côté -> ouverture rainure = 120 - 2*2 = 116mm
// Le tenon doit faire < 116mm en extérieur -> 116 - 2*cl
groove_w = 2;
tenon_ext = base_x - 2*groove_w - 2*cl;  // extérieur du tenon = 115.6mm avec cl=0.20

// -------------------------------------------------------------------
// Murs : tube carré = cube plein - intérieur
// -------------------------------------------------------------------
difference() {
    // Tube plein - exactement 120x120mm
    cube([base_x, base_y, wall_h]);

    // Évidement intérieur
    translate([wall_t, wall_t, -0.1])
    cube([base_x - 2*wall_t, base_y - 2*wall_t, wall_h + 0.2]);

    // Évidement tenon : retire le bas pour que le tenon fasse tenon_ext en extérieur
    // offset de chaque côté = (base_x - tenon_ext) / 2 = groove_w + cl
    translate([groove_w + cl, groove_w + cl, -0.1])
    cube([tenon_ext, tenon_ext, tenon_h + 0.1]);

    // Trou câble USB-C - mur Y- (face avant), décalé 30mm à gauche du centre
    translate([base_x/2 - usbc_w/2 - 30, -0.1, usbc_z])
    cube([usbc_w, wall_t + 0.2, usbc_h]);

    // Trous fixation haut-parleur - mur X+, entraxe 36mm, centrés en Y
    for (dy = [-spk_entraxe/2, spk_entraxe/2])
    translate([base_x - wall_t - 0.1, base_y/2 + dy, spk_z])
    rotate([0, 90, 0])
    cylinder(d=spk_d, h=wall_t + 0.2, $fn=16);

    // Trou fixation micro - mur X-, centré en Y, même hauteur que speaker
    translate([-0.1, base_y/2, spk_z])
    rotate([0, 90, 0])
    cylinder(d=mic_d, h=wall_t + 0.2, $fn=16);
}
