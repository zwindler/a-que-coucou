#!/usr/bin/env python3
"""
Test de détection du wake word 'ah que coucou' avec le modèle custom.
Usage: python3 test_wakeword.py
Parlez dans le micro et dites "ah que coucou" pour tester.
Ctrl+C pour quitter.
"""
from pathlib import Path
import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model
import time

# Charger le modèle custom
MODEL_PATH = Path(__file__).parent / "output" / "ah_que_coucou.onnx"
model = Model(
    wakeword_model_paths=[str(MODEL_PATH)],
)

print("Modèle chargé. Micro actif - dites 'ah que coucou'...")
print("Ctrl+C pour quitter.\n")

SAMPLE_RATE = 16000
CHUNK = 1280  # 80ms @ 16kHz (recommandé par oww)

def callback(indata, frames, time_info, status):
    audio = (indata[:, 0] * 32768).astype(np.int16)
    rms = int(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
    prediction = model.predict(audio)
    score = prediction.get("ah_que_coucou", 0)
    if score > 0.5:
        print(f"[{time.strftime('%H:%M:%S')}] DÉTECTÉ ! score={score:.4f}  rms={rms:5d} ***")
    elif score > 0.01:
        print(f"[{time.strftime('%H:%M:%S')}] score={score:.4f}  rms={rms:5d}")

with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                     blocksize=CHUNK, callback=callback):
    while True:
        sd.sleep(100)
