#!/usr/bin/env python3
"""
Génération de clips synthétiques "ah que coucou" avec Coqui XTTS v2.

Usage dans le conteneur :
  python3 generate_tts.py --n 5000 --output /data/positive

Le script génère N clips WAV 16kHz mono en faisant varier :
- La vitesse de parole (speed)
- La voix de référence : à chaque clip, un sous-ensemble aléatoire de 1 à N
  fichiers WAV est tiré parmi tous les fichiers de référence disponibles dans
  --references-dir. XTTS v2 accepte une liste de speaker_wav et moyenne les
  embeddings, ce qui maximise la diversité acoustique.

Pour ajouter une nouvelle voix de référence, il suffit de déposer un fichier
WAV (≥ 6 s recommandées, 16 kHz ou 22 kHz mono) dans le dossier --references-dir.
"""

import argparse
import random
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5000, help="Nombre de clips à générer")
    parser.add_argument("--output", type=str, default="/data/positive", help="Dossier de sortie")
    parser.add_argument(
        "--references-dir",
        type=str,
        default="/data/references",
        help="Dossier contenant les fichiers WAV de référence pour le clonage de voix",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Import TTS ici pour avoir un message d'erreur clair si absent
    try:
        from TTS.api import TTS
    except ImportError:
        print("ERREUR: Coqui TTS non installé. Lancer dans le conteneur approprié.")
        sys.exit(1)

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Utilisation du device : {device}")

    # Collecte des fichiers de référence
    references_dir = Path(args.references_dir)
    reference_wavs = sorted(references_dir.glob("*.wav")) if references_dir.is_dir() else []
    if reference_wavs:
        print(f"Voix de référence trouvées ({len(reference_wavs)}) :")
        for r in reference_wavs:
            print(f"  - {r.name}")
    else:
        print("Avertissement : aucun fichier WAV de référence trouvé, utilisation de la voix par défaut XTTS")

    print("Chargement du modèle XTTS v2...")
    # agree_to_tos=True : accepte la licence CPML non-commerciale de Coqui
    # nécessaire pour éviter le prompt interactif en mode non-TTY (conteneur, CI)
    # La licence CPML est acceptée via COQUI_TOS_AGREED=1 dans l'environnement du conteneur
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # Phrases variantes - légères variations orthographiques pour diversifier
    # la prosodie générée par le TTS
    phrases = [
        "ah que coucou",
        "ah, que coucou",
        "à que coucou",
        "ah que coucou !",
    ]

    # Paramètres de variation
    speeds = [0.85, 0.90, 0.95, 1.0, 1.05, 1.10, 1.15]

    print(f"Génération de {args.n} clips dans {output_dir}...")

    for i in range(args.n):
        phrase = random.choice(phrases)
        speed = random.choice(speeds)
        output_path = str(output_dir / f"ah_que_coucou_{i:05d}.wav")

        # Sous-ensemble aléatoire de références : entre 1 et len(reference_wavs)
        # XTTS v2 accepte une liste et moyenne les embeddings de voix
        if reference_wavs:
            k = random.randint(1, len(reference_wavs))
            selected_refs = [str(r) for r in random.sample(reference_wavs, k)]
        else:
            selected_refs = None

        try:
            if selected_refs:
                tts.tts_to_file(
                    text=phrase,
                    language="fr",
                    speaker_wav=selected_refs,
                    speed=speed,
                    file_path=output_path,
                )
            else:
                tts.tts_to_file(
                    text=phrase,
                    language="fr",
                    speed=speed,
                    file_path=output_path,
                )

            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{args.n} clips générés...")

        except Exception as e:
            print(f"  Erreur clip {i}: {e}")
            continue

    print(f"\nTerminé. {args.n} clips dans {output_dir}")


if __name__ == "__main__":
    main()
