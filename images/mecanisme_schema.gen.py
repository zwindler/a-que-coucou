#!/usr/bin/env python3
"""Schéma de principe pignon-crémaillère : rotation du servo -> translation verticale."""
W, H = 720, 540
BLUE="#1971c2"; BLUEF="#d0eb77".replace("77","eb"); ORANGE="#e8590c"; ORANGEF="#ffe8cc"
BLUEF="#d0ebfb"
s=[]
def add(x): s.append(x)
def txt(x,y,t,sz=13,w="400",f="#111",a="start"):
    add(f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{f}" text-anchor="{a}">{t}</text>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')
add('<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto">'
    '<path d="M0,0 L7,3 L0,6 Z" fill="#111"/></marker></defs>')
txt(24,34,"Du mouvement circulaire au mouvement linéaire",20,"700","#111")
txt(24,56,"le système pignon-crémaillère",13,"400","#868e96")

# --- haut de la boîte : simple ligne (boîte ouverte, 4 murs sans plafond) ---
lidy=210
add(f'<line x1="70" y1="{lidy}" x2="650" y2="{lidy}" stroke="#adb5bd" stroke-width="2" stroke-dasharray="7 5"/>')
txt(74,lidy-8,"haut de la boîte",12,"500","#868e96")

# --- crémaillère (rack) : barre verticale, dents à gauche ---
rx, rw = 306, 30
rtop, rbot = 150, 440
add(f'<rect x="{rx}" y="{rtop}" width="{rw}" height="{rbot-rtop}" rx="4" fill="{ORANGEF}" stroke="{ORANGE}" stroke-width="2"/>')
for j in range(9):
    y=rtop+12+j*30
    add(f'<path d="M{rx},{y} L{rx},{y+18} L{rx-15},{y+9} Z" fill="{ORANGEF}" stroke="{ORANGE}" stroke-width="2"/>')
txt(rx+rw+18, 250, "crémaillère", 14, "700", ORANGE)
txt(rx+rw+18, 268, "(tige dentée)", 11, "400", "#868e96")

# --- œuf sur le dessus (plus gros) ---
add(f'<ellipse cx="{rx+rw/2}" cy="112" rx="38" ry="48" fill="#fff9db" stroke="#f59f00" stroke-width="2"/>')
txt(rx+rw/2, 118, "œuf", 15, "700", "#b8860b", "middle")

# --- pignon : cercle + dents + moyeu ---
cx, cy, r = 210, 330, 74
for i in range(14):
    ang=i*(360/14)
    # dent triangulaire : base sur le cercle, pointe vers l'extérieur (comme la crémaillère)
    add(f'<polygon points="{cx-9},{cy-r+1} {cx+9},{cy-r+1} {cx},{cy-r-15}" fill="{BLUEF}" stroke="{BLUE}" stroke-width="2" stroke-linejoin="round" transform="rotate({ang} {cx} {cy})"/>')
add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BLUEF}" stroke="{BLUE}" stroke-width="2.5"/>')
add(f'<circle cx="{cx}" cy="{cy}" r="16" fill="#fff" stroke="{BLUE}" stroke-width="2"/>')
add(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{BLUE}"/>')
txt(cx, cy+r+34, "pignon", 14, "700", BLUE, "middle")
txt(cx, cy+r+52, "(fixé sur l'axe du SG90)", 11, "400", "#868e96", "middle")

# --- flèche rotation autour du pignon (anti-horaire : le flanc droit monte) ---
add(f'<path d="M{cx+78},{cy-72} A 106 106 0 0 0 {cx-78},{cy-72}" fill="none" stroke="#111" stroke-width="2.6" marker-end="url(#ah)"/>')
txt(cx-118, cy+8, "rotation", 12, "600", "#111", "end")
txt(cx-118, cy+24, "du servo", 12, "600", "#111", "end")

# --- flèche translation verticale (montée de l'œuf), pointe crimson propre ---
ax=470
atop, abot = 172, 380
add(f'<line x1="{ax}" y1="{abot}" x2="{ax}" y2="{atop}" stroke="#c2255c" stroke-width="3"/>')
add(f'<polygon points="{ax-9},{atop} {ax+9},{atop} {ax},{atop-16}" fill="#c2255c"/>')
txt(ax+14, 250, "l'œuf monte", 13, "700", "#c2255c")
txt(ax+14, 268, "tout droit", 13, "700", "#c2255c")

# --- légende engrènement ---
txt(24, H-24, "Le pignon (sur l'axe du servo) tourne ; ses dents engrènent la crémaillère, qui ne peut que coulisser verticalement.", 12, "400", "#495057")

add('</svg>')
open("meca.svg","w").write("\n".join(s))
print("OK")
