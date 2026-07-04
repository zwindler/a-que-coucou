#!/usr/bin/env python3
"""
Test d'enregistrement micro et de détection du wake word "ah que coucou".

Affiche le score de détection en temps réel. Utile pour valider
le câblage du micro INMP441 et ajuster le seuil de détection.

Prérequis :
    dtoverlay=googlevoicehat-soundcard dans /boot/firmware/config.txt
    arecord -l  ->  doit afficher card 0: sndrpigooglevoi

Usage :
    python3 tests/test_wakeword.py
    python3 tests/test_wakeword.py --device 0 --threshold 0.7
"""

import argparse
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy import signal as scipy_signal

os.environ.setdefault("ORT_LOGGING_LEVEL", "3")
warnings.filterwarnings("ignore", message=".*CUDAExecutionProvider.*")

from openwakeword.model import Model

MODEL_PATH = Path(__file__).parent.parent / "wakeword" / "output" / "ah_que_coucou.onnx"
SAMPLE_RATE = 16000
CHUNK = 1280  # 80ms @ 16kHz

parser = argparse.ArgumentParser()
parser.add_argument("--device",    default="0",          help="Index ou nom du device audio")
parser.add_argument("--threshold", type=float, default=0.5)
parser.add_argument("--model",     default=str(MODEL_PATH))
args = parser.parse_args()

if not Path(args.model).exists():
    print(f"Modèle introuvable : {args.model}")
    sys.exit(1)

device_id = int(args.device) if args.device is not None and args.device.isdigit() else args.device
device_info = sd.query_devices(device_id if device_id is not None else sd.default.device)
native_rate = int(device_info["default_samplerate"])
capture_chunk = int(CHUNK * native_rate / SAMPLE_RATE) if native_rate != SAMPLE_RATE else CHUNK

print(f"Micro : {device_info['name']} @ {native_rate} Hz")
if native_rate != SAMPLE_RATE:
    print(f"Resampling {native_rate} -> {SAMPLE_RATE} Hz")

model = Model(wakeword_model_paths=[args.model])
print(f"Seuil de détection : {args.threshold}")
print("Dites 'ah que coucou'... (Ctrl+C pour quitter)\n")


def callback(indata, frames, time_info, status):
    mono = indata[:, 0]
    if native_rate != SAMPLE_RATE:
        mono = scipy_signal.resample_poly(mono, SAMPLE_RATE, native_rate)

    audio = (mono * 32768).astype(np.int16)
    score = model.predict(audio).get("ah_que_coucou", 0)

    if score >= args.threshold:
        print(f"[{time.strftime('%H:%M:%S')}]  DÉTECTÉ !  score={score:.4f}  ***")
    elif score > 0.05:
        print(f"[{time.strftime('%H:%M:%S')}]  score={score:.4f}")


with sd.InputStream(
    samplerate=native_rate,
    channels=1,
    dtype="float32",
    blocksize=capture_chunk,
    device=device_id,
    callback=callback,
):
    try:
        while True:
            sd.sleep(100)
    except KeyboardInterrupt:
        print("\nArrêt.")
