#!/usr/bin/env python3
"""
Test de lecture audio via aplay.

Joue le son "coucou" sur le haut-parleur I2S (MAX98357A).

Prérequis :
    dtoverlay=googlevoicehat-soundcard dans /boot/firmware/config.txt
    aplay -l  ->  doit afficher card 0: sndrpigooglevoi

Usage :
    python3 tests/test_audio.py
    python3 tests/test_audio.py --device plughw:1,0
    python3 tests/test_audio.py --sound sounds/boite_a_coucou.wav
"""

import argparse
import subprocess
import sys
from pathlib import Path

SOUNDS_DIR = Path(__file__).parent.parent / "sounds"
DEFAULT_SOUND = SOUNDS_DIR / "boite_a_coucou.wav"
DEFAULT_DEVICE = "plughw:0,0"

parser = argparse.ArgumentParser()
parser.add_argument("--sound",  default=str(DEFAULT_SOUND), help="Fichier WAV à jouer")
parser.add_argument("--device", default=DEFAULT_DEVICE,     help="Device ALSA (ex: plughw:0,0)")
args = parser.parse_args()

sound = Path(args.sound)
if not sound.exists():
    print(f"Fichier introuvable : {sound}")
    sys.exit(1)

print(f"Lecture de {sound.name} sur {args.device}...")
result = subprocess.run(
    ["/usr/bin/aplay", "-D", args.device, str(sound)],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print(f"Erreur aplay :\n{result.stderr}")
    sys.exit(1)

print("Lecture terminée.")
