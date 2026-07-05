#!/usr/bin/env python3
"""Vue physique du header GPIO 40 broches - broches utilisées en couleur."""

W, H = 820, 760
C = {"5v":"#e03131","3v3":"#f76707","gnd":"#212529","bclk":"#1971c2",
     "lrck":"#2f9e44","dout":"#9c36b5","din":"#c2255c","pwm":"#f2b705"}

# layout physique standard RPi : (pin_impair_gauche_fonction, pin_pair_droite_fonction)
# on ne renseigne que ce qui nous intéresse ; le reste = libre
HDR = {
 1:("3V3",None), 2:("5V",None),
 3:("GPIO2",None), 4:("5V",None),
 5:("GPIO3",None), 6:("GND",None),
 7:("GPIO4",None), 8:("GPIO14",None),
 9:("GND",None), 10:("GPIO15",None),
 11:("GPIO17",None), 12:("GPIO18",None),
 13:("GPIO27",None), 14:("GND",None),
 15:("GPIO22",None), 16:("GPIO23",None),
 17:("3V3",None), 18:("GPIO24",None),
 19:("GPIO10",None), 20:("GND",None),
 21:("GPIO9",None), 22:("GPIO25",None),
 23:("GPIO11",None), 24:("GPIO8",None),
 25:("GND",None), 26:("GPIO7",None),
 27:("GPIO0",None), 28:("GPIO1",None),
 29:("GPIO5",None), 30:("GND",None),
 31:("GPIO6",None), 32:("GPIO12",None),
 33:("GPIO13",None), 34:("GND",None),
 35:("GPIO19",None), 36:("GPIO16",None),
 37:("GPIO26",None), 38:("GPIO20",None),
 39:("GND",None), 40:("GPIO21",None),
}
# broches utilisées : pin -> (net, libellé)
USED = {
 1:("3v3","micro VDD"),
 2:("5v","servo VCC"),
 4:("5v","ampli Vin"),
 6:("gnd","GND (ampli)"),
 9:("gnd","GND (micro)"),
 12:("bclk","BCLK -> micro+ampli"),
 14:("gnd","GND (servo)"),
 17:("3v3","ampli SD"),
 33:("pwm","servo Signal"),
 35:("lrck","LRCLK -> micro+ampli"),
 38:("dout","micro SD/DOUT"),
 40:("din","ampli DIN"),
}

s=[]
def add(x): s.append(x)
def txt(x,y,t,sz=12,w="400",f="#111",a="start"):
    add(f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{f}" text-anchor="{a}">{t}</text>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')
txt(24,34,"Header GPIO 40 broches - vue physique",20,"700","#111")
txt(24,56,"Broches utilisées en couleur. Pin 1 = coin repéré (pad carré) sur la carte.",12,"400","#868e96")

top=92; rh=31
cxL=372; cxR=448; padw=58; padh=22
for row in range(20):
    pinL=row*2+1; pinR=row*2+2
    y=top+row*rh
    for pin,cx,side in ((pinL,cxL,"L"),(pinR,cxR,"R")):
        used=pin in USED
        col=C[USED[pin][0]] if used else "#dee2e6"
        tcol="#fff" if used else "#adb5bd"
        # pin 1 = carré, sinon arrondi
        rx=2 if pin==1 else 10
        add(f'<rect x="{cx-padw/2}" y="{y-padh/2}" width="{padw}" height="{padh}" rx="{rx}" fill="{col}" stroke="#adb5bd" stroke-width="1"/>')
        txt(cx, y+4, str(pin), 11, "700", tcol, "middle")
        # nom de broche (gris) collé au pad, + libellé fonction si utilisée
        name=HDR[pin][0]
        if side=="L":
            txt(cx-padw/2-8, y+4, name, 10, "500", "#868e96", "end")
            if used:
                lab=USED[pin][1]
                txt(cx-padw/2-70, y+4, lab, 12, "700", C[USED[pin][0]], "end")
        else:
            txt(cx+padw/2+8, y+4, name, 10, "500", "#868e96", "start")
            if used:
                lab=USED[pin][1]
                txt(cx+padw/2+70, y+4, lab, 12, "700", C[USED[pin][0]], "start")

# légende
lx=24; ly=H-24
items=[("5V","5v"),("3V3","3v3"),("GND","gnd"),("BCLK","bclk"),("LRCLK","lrck"),("data micro","dout"),("data ampli","din"),("PWM","pwm")]
for i,(lbl,net) in enumerate(items):
    x=lx+i*98
    add(f'<rect x="{x}" y="{ly-10}" width="16" height="12" rx="3" fill="{C[net]}"/>')
    txt(x+22, ly, lbl, 10.5, "500", "#495057")

add('</svg>')
open("cablage_header.svg","w").write("\n".join(s))
print("OK")
