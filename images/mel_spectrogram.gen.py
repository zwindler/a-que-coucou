#!/usr/bin/env python3
"""Génère un mel-spectrogramme (numpy/scipy/matplotlib, sans librosa).

Usage : python3 mel_spectrogram.gen.py <fichier.wav> [sortie.png]
Défaut : reference_johnny_a_que_coucou.wav -> mel_spectrogram.png
Dépendances : numpy, scipy, matplotlib.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WAV = sys.argv[1] if len(sys.argv) > 1 else "reference_johnny_a_que_coucou.wav"
OUT = sys.argv[2] if len(sys.argv) > 2 else "mel_spectrogram.png"

sr, x = wavfile.read(WAV)
if x.ndim > 1:                       # stéréo -> mono
    x = x.mean(axis=1)
x = x.astype(np.float32)
x /= (np.abs(x).max() + 1e-9)

# --- STFT (spectrogramme de puissance) ---
n_fft, hop = 1024, 256
f, t, Z = stft(x, fs=sr, window="hann", nperseg=n_fft, noverlap=n_fft - hop, boundary=None)
power = np.abs(Z) ** 2

# --- banc de filtres mel, construit à la main ---
def hz2mel(hz): return 2595.0 * np.log10(1 + hz / 700.0)
def mel2hz(m):  return 700.0 * (10 ** (m / 2595.0) - 1)

n_mels, fmin, fmax = 64, 0.0, sr / 2
m_pts = np.linspace(hz2mel(fmin), hz2mel(fmax), n_mels + 2)
bins = np.floor((n_fft + 1) * mel2hz(m_pts) / sr).astype(int)
fb = np.zeros((n_mels, power.shape[0]))
for i in range(1, n_mels + 1):
    l, c, r = bins[i - 1], bins[i], bins[i + 1]
    for k in range(l, c):
        if c > l: fb[i - 1, k] = (k - l) / (c - l)
    for k in range(c, r):
        if r > c: fb[i - 1, k] = (r - k) / (r - c)

mel_db = 10 * np.log10(fb @ power + 1e-10)   # projection mel puis passage en dB

# --- tracé ---
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
im = ax.imshow(mel_db, origin="lower", aspect="auto", cmap="magma",
               extent=[0, len(x) / sr, 0, n_mels],
               vmin=mel_db.max() - 70, vmax=mel_db.max())
yt = np.linspace(0, n_mels, 6)
ax.set_yticks(yt)
ax.set_yticklabels([f"{int(mel2hz(hz2mel(fmax) * (v / n_mels)))}" for v in yt])
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Fréquence (Hz, échelle mel)")
ax.set_title("Mel-spectrogramme de « ah que coucou » (extrait du sketch)")
cb = fig.colorbar(im, ax=ax, pad=0.01)
cb.set_label("Puissance (dB)")
fig.tight_layout()
fig.savefig(OUT)
print("écrit :", OUT, "| sr =", sr, "| durée = %.2fs" % (len(x) / sr))
