#!/usr/bin/env python3
"""Schéma de câblage vectoriel (SVG) - La Boîte à Coucou. Layout par lignes alignées."""

W, H = 1010, 790
C = {"5v":"#e03131","3v3":"#f76707","gnd":"#212529","bclk":"#1971c2",
     "lrck":"#2f9e44","dout":"#9c36b5","din":"#c2255c","pwm":"#f2b705"}

s=[]
def add(x): s.append(x)
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')
add(f'<text x="24" y="36" font-size="22" font-weight="700" fill="#111">La Boîte à Coucou &#8212; câblage (Raspberry Pi 5)</text>')

def txt(x,y,t,sz=13,w="400",f="#111",a="start"):
    add(f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{f}" text-anchor="{a}">{t}</text>')
def rrect(x,y,w,h,fill,st,rx=12):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{st}" stroke-width="1.6"/>')
def dot(x,y,c): add(f'<circle cx="{x}" cy="{y}" r="5" fill="{c}"/>')

RPI_X, RPI_W = 30, 250
RDOT = RPI_X+RPI_W          # 280, bord droit du RPi
CDOT = 600                  # bord gauche des composants
CBOX_W = 380

# lanes : (titre, sous-titre, [(net, label_rpi, label_comp)])
lanes = [
 ("Micro INMP441","I2S &#8212; entrée audio",[
   ("3v3","pin 1 &#183; 3V3","VDD"),
   ("gnd","GND","GND"),
   ("bclk","pin 12 &#183; GPIO18  (breadboard)","SCK / BCLK"),
   ("lrck","pin 35 &#183; GPIO19  (breadboard)","WS / LRCLK"),
   ("dout","pin 38 &#183; GPIO20","SD (DOUT)"),
 ]),
 ("Ampli MAX98357A","I2S &#8212; sortie audio (+ HP 4&#937; 3W)",[
   ("5v","pin 4 &#183; 5V","Vin"),
   ("gnd","GND","GND"),
   ("bclk","pin 12 &#183; GPIO18  (breadboard)","BCLK"),
   ("lrck","pin 35 &#183; GPIO19  (breadboard)","LRC"),
   ("din","pin 40 &#183; GPIO21","DIN"),
   ("3v3","pin 17 &#183; 3V3","SD (enable)"),
 ]),
 ("Servo SG90","PWM matériel",[
   ("5v","pin 2 &#183; 5V","VCC"),
   ("gnd","GND","GND"),
   ("pwm","pin 33 &#183; GPIO13","Signal"),
 ]),
]

TOP=90
row_h=30
lane_gap=34
lane_head=34

# calcul des y
y=TOP
lane_layout=[]
for title,sub,rows in lanes:
    y0=y
    ry=y0+lane_head+6
    ys=[ry+i*row_h for i in range(len(rows))]
    y=ry+len(rows)*row_h+lane_gap
    lane_layout.append((y0, ys, rows, title, sub))
band_bottom=lane_layout[-1][1][-1]+18

# bande RPi (une seule, couvre toutes les lanes)
rrect(RPI_X, TOP-4, RPI_W, band_bottom-(TOP-4)+8, "#f8f9fa", "#495057", 14)
txt(RPI_X+RPI_W/2, TOP+18, "Raspberry Pi 5", 15, "700", "#111", "middle")
txt(RPI_X+RPI_W/2, TOP+34, "header GPIO 40 broches", 10, "400", "#868e96", "middle")

# lanes
for y0, ys, rows, title, sub in lane_layout:
    # boîte composant
    cbox_y=ys[0]-24
    cbox_h=(ys[-1]-ys[0])+48
    rrect(CDOT, cbox_y, CBOX_W, cbox_h, "#e7f5ff", "#1971c2", 12)
    txt(CDOT+150, cbox_y+20, title, 14, "700", "#111", "start")
    txt(CDOT+150, cbox_y+35, sub, 10, "400", "#868e96", "start")
    for (net,lr,lc),yy in zip(rows,ys):
        col=C[net]
        # fil horizontal
        add(f'<line x1="{RDOT}" y1="{yy}" x2="{CDOT}" y2="{yy}" stroke="{col}" stroke-width="3.2" stroke-linecap="round"/>')
        dot(RDOT,yy,col); dot(CDOT,yy,col)
        txt(RPI_X+16, yy+4, lr, 12, "600", col)                      # étiquette côté RPi
        txt(CDOT+16, yy+4, lc, 12.5, "600", "#111")                  # étiquette côté composant

# note breadboard
ny=band_bottom+28
txt(24, ny, "Astuce : GPIO18 (BCLK) et GPIO19 (LRCLK) alimentent À LA FOIS le micro et l'ampli.", 12, "600", "#111")
txt(24, ny+18, "Un fil Dupont ne se dédoublant pas, la breadboard répartit chaque horloge vers les deux composants.", 12, "400", "#495057")

# légende
lx, ly = 24, H-26
items=[("5V","5v"),("3V3","3v3"),("GND","gnd"),("BCLK","bclk"),("LRCLK","lrck"),("data micro","dout"),("data ampli","din"),("PWM","pwm")]
for i,(lbl,net) in enumerate(items):
    x=lx+i*112
    add(f'<line x1="{x}" y1="{ly}" x2="{x+22}" y2="{ly}" stroke="{C[net]}" stroke-width="4"/>')
    txt(x+28, ly+4, lbl, 11, "500", "#495057")

add('</svg>')
open("cablage.svg","w").write("\n".join(s))
print("SVG écrit", W, "x", H)
