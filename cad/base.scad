// Base de la boîte - La Boîte à Coucou
//
// Vue de dessus (schéma utilisateur) :
//   Y+ = côté rail (haut du schéma)
//   Y- = côté Pi (bas du schéma) -> trou câble alimentation
//   X  = centré
//
// Assemblage :
//   - base plate avec rainure périphérique pour les murs (box.scad)
//   - languette mâle en T côté Y+, centrée en X :
//     profil identique à la crémaillère (rack.scad), jeu tight 0.1mm
//     s'insère dans le canal du rail_bracket par le bas
//
// PROTO validé à 50% (01/05/2026). Version finale : 120x120mm, languette 12mm
// ===================================================================

// -------------------------------------------------------------------
// Profil T intérieur du rail (identique à rail_bracket.scad)
// On reproduit le profil avec jeu tight pour que la languette s'emboîte
// -------------------------------------------------------------------
rb_head_w  = 6.3;
rb_head_h  = 2.0;
rb_taper_h = 1.5;
rb_stem_w  = 3.4;
rb_stem_h  = 1.5;
rb_cl      = 0.20;   // jeu glissant interne du rail

// Dimensions intérieures du canal (ce dans quoi on doit rentrer)
canal_head_w = rb_head_w + 2*rb_cl;
canal_stem_w = rb_stem_w + 2*rb_cl;
canal_head_h = rb_head_h + rb_cl;
canal_taper  = rb_taper_h;
canal_stem_h = rb_stem_h + rb_cl;

cl_tight     = 0.05;   // jeu tight languette dans canal

// Languette mâle : légèrement plus petite que le canal
tongue_head_w = canal_head_w - 2*cl_tight;
tongue_stem_w = canal_stem_w - 2*cl_tight;
tongue_head_h = canal_head_h - cl_tight;
tongue_taper  = canal_taper;
tongue_stem_h = canal_stem_h - cl_tight;
tongue_h      = 12;   // hauteur de la languette réduite (évite contact avec bas du rail)

// -------------------------------------------------------------------
// Dimensions base (proto 50%)
// -------------------------------------------------------------------
proto    = 1.0;

base_x   = 120 * proto;   // 120mm
base_y   = 120 * proto;   // 120mm
base_z   = 3;

groove_w = 2;  // pas de jeu - filament bien calibré
groove_d = 2;
wall_t   = 3;

cable_d  = 10;
cable_x  = base_x / 2;

// -------------------------------------------------------------------
// Module languette mâle en T (section 2D, profil crémaillère)
// -------------------------------------------------------------------
module tongue_2d() {
    polygon([
        // tige (partie fine, face avant Y=0)
        [-tongue_stem_w/2, 0                                        ],
        [ tongue_stem_w/2, 0                                        ],
        // trapèze
        [ tongue_stem_w/2, tongue_stem_h                            ],
        [ tongue_head_w/2, tongue_stem_h + tongue_taper             ],
        // base large
        [ tongue_head_w/2, tongue_stem_h + tongue_taper + tongue_head_h ],
        [-tongue_head_w/2, tongue_stem_h + tongue_taper + tongue_head_h ],
        [-tongue_head_w/2, tongue_stem_h + tongue_taper             ],
        [-tongue_stem_w/2, tongue_stem_h                            ],
    ]);
}

// -------------------------------------------------------------------
// Base
// -------------------------------------------------------------------
difference() {
    union() {
        // Dalle principale
        cube([base_x, base_y, base_z]);

        // Languette mâle - centrée en X, côté Y+, décalée de wall_t du bord
        // S'insère vers le haut dans le canal du rail_bracket
        // Miroir Y : tête large côté Y-, tige fine côté Y+ (câbles dégagés du côté pignon/crémaillère)
        translate([base_x/2, base_y - wall_t - 46, base_z])
        mirror([0,1,0])
        linear_extrude(height = tongue_h)
        tongue_2d();
    }

    // Rainure périphérique collée au bord extérieur
    translate([0, 0, base_z - groove_d])
    difference() {
        cube([base_x, base_y, groove_d + 0.1]);
        translate([groove_w, groove_w, -0.1])
        cube([base_x - 2*groove_w, base_y - 2*groove_w, groove_d + 0.3]);
    }
}
