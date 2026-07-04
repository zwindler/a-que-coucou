#!/usr/bin/env python3
"""
Détection du mot-clé "ah que coucou" via openWakeWord.

Écoute le microphone en continu. Quand le mot-clé est détecté,
appelle le callback fourni avec le score de confiance.

Usage autonome (test) :
    python3 wakeword.py
    python3 wakeword.py --threshold 0.7 --device 0
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

MODEL_PATH = Path(__file__).parent / "wakeword" / "output" / "ah_que_coucou.onnx"
SAMPLE_RATE = 16000
CHUNK = 1280  # 80ms @ 16kHz, taille requise par openWakeWord


def listen(callback, model_path=MODEL_PATH, threshold=0.5, cooldown=3.0, device=None):
    device_id = int(device) if device is not None and str(device).isdigit() else device
    try:
        device_info = sd.query_devices(device_id if device_id is not None else sd.default.device)
    except Exception as e:
        print(f"Erreur device audio : {e}", file=sys.stderr)
        sys.exit(1)

    native_rate = int(device_info["default_samplerate"])
    capture_chunk = int(CHUNK * native_rate / SAMPLE_RATE) if native_rate != SAMPLE_RATE else CHUNK

    print(f"Micro : {device_info['name']} @ {native_rate} Hz", file=sys.stderr)
    if native_rate != SAMPLE_RATE:
        print(f"Resampling {native_rate} -> {SAMPLE_RATE} Hz", file=sys.stderr)

    if not Path(model_path).exists():
        print(f"Modèle introuvable : {model_path}", file=sys.stderr)
        sys.exit(1)

    model = Model(wakeword_model_paths=[str(model_path)])
    print("Écoute en cours...", file=sys.stderr)

    last_detection = 0.0

    def audio_callback(indata, frames, time_info, status):
        nonlocal last_detection
        if status:
            print(f"Audio status : {status}", file=sys.stderr)

        mono = indata[:, 0]
        if native_rate != SAMPLE_RATE:
            mono = scipy_signal.resample_poly(mono, SAMPLE_RATE, native_rate)

        audio = (mono * 32768).astype(np.int16)
        score = model.predict(audio).get("ah_que_coucou", 0)

        now = time.monotonic()
        if score >= threshold and (now - last_detection) >= cooldown:
            last_detection = now
            callback(score)

    with sd.InputStream(
        samplerate=native_rate,
        channels=1,
        dtype="float32",
        blocksize=capture_chunk,
        device=device_id,
        callback=audio_callback,
    ):
        try:
            while True:
                sd.sleep(100)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=str(MODEL_PATH))
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--cooldown", type=float, default=3.0)
    parser.add_argument("--device", default="0")
    args = parser.parse_args()

    def on_detection(score):
        print(f"Détecté ! score={score:.4f}")

    listen(on_detection, args.model, args.threshold, args.cooldown, args.device)
