#!/usr/bin/env python3
"""
Diagnostic du microphone INMP441.

Enregistre quelques secondes audio et analyse le signal pour détecter
les problèmes courants :

  - Static noise  : RMS élevé et constant (câblage MAX98357A SD pin sur GPIO18 au lieu de 3.3V)
  - Silence total : RMS quasi nul (micro non alimenté, mauvais device)
  - Signal normal : RMS variable, pics sur la parole

Prérequis :
    dtoverlay=googlevoicehat-soundcard dans /boot/firmware/config.txt
    arecord -l  ->  doit afficher card 0: sndrpigooglevoi

Usage :
    python3 tests/test_mic.py
    python3 tests/test_mic.py --device 0 --duration 5
"""

import argparse
import sys
import time

import numpy as np
import sounddevice as sd
from scipy import signal as scipy_signal

SAMPLE_RATE = 16000
CHUNK = 1280  # 80ms @ 16kHz

parser = argparse.ArgumentParser()
parser.add_argument("--device",   default="0",      help="Index ou nom du device audio")
parser.add_argument("--duration", type=float, default=5.0, help="Durée d'analyse en secondes")
args = parser.parse_args()

device_id = int(args.device) if args.device is not None and args.device.isdigit() else args.device
try:
    device_info = sd.query_devices(device_id if device_id is not None else sd.default.device)
except Exception as e:
    print(f"Erreur device audio : {e}")
    print("Devices disponibles :")
    print(sd.query_devices())
    sys.exit(1)

native_rate = int(device_info["default_samplerate"])
capture_chunk = int(CHUNK * native_rate / SAMPLE_RATE) if native_rate != SAMPLE_RATE else CHUNK

print(f"Micro : {device_info['name']} @ {native_rate} Hz")
print(f"Analyse pendant {args.duration}s - parlez dans le micro...\n")

rms_values = []
start = time.monotonic()


def callback(indata, frames, time_info, status):
    mono = indata[:, 0]
    if native_rate != SAMPLE_RATE:
        mono = scipy_signal.resample_poly(mono, SAMPLE_RATE, native_rate)

    audio = (mono * 32768).astype(np.int16)
    rms = int(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
    rms_values.append(rms)

    bar = "#" * min(40, rms // 50)
    print(f"  RMS {rms:5d}  |{bar:<40}|", end="\r")


with sd.InputStream(
    samplerate=native_rate,
    channels=1,
    dtype="float32",
    blocksize=capture_chunk,
    device=device_id,
    callback=callback,
):
    try:
        while time.monotonic() - start < args.duration:
            sd.sleep(100)
    except KeyboardInterrupt:
        pass

print("\n")

if not rms_values:
    print("Aucune donnée reçue.")
    sys.exit(1)

rms_mean = np.mean(rms_values)
rms_std  = np.std(rms_values)
rms_max  = np.max(rms_values)

print(f"Résultats sur {len(rms_values)} chunks :")
print(f"  RMS moyen : {rms_mean:.0f}")
print(f"  RMS écart-type : {rms_std:.0f}  (faible = signal constant -> suspect)")
print(f"  RMS max   : {rms_max:.0f}")
print()

# Diagnostic
if rms_mean < 50:
    print("PROBLÈME : signal quasi nul.")
    print("  -> Vérifier l'alimentation du micro (VDD sur 3.3V, GND sur GND)")
    print("  -> Vérifier le device audio (arecord -l)")
elif rms_mean > 800 and rms_std < rms_mean * 0.15:
    print("PROBLÈME : static noise détecté (RMS élevé et constant).")
    print("  -> Vérifier que MAX98357A SD est sur Pin 17 (3.3V) et NON sur Pin 12 (GPIO18)")
    print("  -> Vérifier que les deux composants INMP441 et MAX98357A sont connectés simultanément")
elif rms_std < rms_mean * 0.1 and rms_mean > 200:
    print("AVERTISSEMENT : signal peu variable (possible static faible).")
    print("  -> Tester en parlant près du micro pour confirmer que le RMS monte")
else:
    print("OK : signal audio normal.")
    print("  -> RMS variable, réactif à la voix")
