#!/usr/bin/env python3
"""
Script d'entraînement du modèle openWakeWord custom "ah que coucou".

Ce script est un wrapper autour de openwakeword/train.py qui :
1. Télécharge les données nécessaires (si absent du cache)
2. Génère le fichier de config YAML
3. Lance l'augmentation des clips positifs
4. Lance l'entraînement du modèle
5. Indique où trouver le .onnx exporté

Usage (dans le conteneur aquecoucou-train) :
  python3 /app/train_wakeword.py \
    --positive_clips /data/positive \
    --cache_dir     /cache \
    --output_dir    /output

Prérequis :
  - /data/positive/ : dossier contenant les 5 000 clips WAV générés par generate_tts.py
  - /cache/         : dossier persistant pour les téléchargements volumineux
                      (ACAV100M ~17 Go, téléchargé une seule fois)
  - /output/        : dossier de sortie pour le modèle .onnx entraîné
"""

import argparse
import os
import sys
import yaml
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Téléchargement des données
# ---------------------------------------------------------------------------

def download_if_missing(url: str, dest: Path, desc: str) -> None:
    """Télécharge `url` vers `dest` si le fichier n'existe pas déjà."""
    if dest.exists():
        log.info(f"Cache hit : {dest.name} ({desc})")
        return
    log.info(f"Téléchargement : {desc} -> {dest}")
    import urllib.request
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    log.info(f"Terminé : {dest.name}")


def download_hf_dataset_to_wav(hf_dataset_name: str, dest_dir: Path,
                                split: str = "train",
                                streaming: bool = True,
                                max_hours: float = None) -> None:
    """Télécharge un dataset HuggingFace audio et le convertit en WAV 16kHz."""
    if dest_dir.exists() and any(dest_dir.glob("*.wav")):
        log.info(f"Cache hit : {dest_dir.name} (dataset HuggingFace)")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    import datasets as hf_datasets
    import scipy.io.wavfile
    import numpy as np
    from tqdm import tqdm

    log.info(f"Téléchargement dataset HuggingFace : {hf_dataset_name} -> {dest_dir}")
    ds = hf_datasets.load_dataset(hf_dataset_name, split=split, streaming=streaming)
    ds = iter(ds.cast_column("audio", hf_datasets.Audio(sampling_rate=16000)))

    max_clips = int(max_hours * 3600 / 30) if max_hours else None  # clips de ~30s
    for i, row in enumerate(tqdm(ds)):
        if max_clips and i >= max_clips:
            break
        name = row['audio']['path'].split('/')[-1]
        name = name.replace(".mp3", ".wav").replace(".flac", ".wav")
        scipy.io.wavfile.write(
            str(dest_dir / name), 16000,
            (row['audio']['array'] * 32767).astype(np.int16)
        )


def download_mit_rirs(dest_dir: Path) -> None:
    """Télécharge les Room Impulse Responses MIT (petit dataset ~50 Mo)."""
    if dest_dir.exists() and any(dest_dir.glob("*.wav")):
        log.info(f"Cache hit : {dest_dir.name} (MIT RIRs)")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    import datasets as hf_datasets
    import scipy.io.wavfile
    import numpy as np
    from tqdm import tqdm

    log.info("Téléchargement MIT RIRs...")
    ds = hf_datasets.load_dataset(
        "davidscripka/MIT_environmental_impulse_responses",
        split="train", streaming=True
    )
    for row in tqdm(ds):
        name = row['audio']['path'].split('/')[-1]
        scipy.io.wavfile.write(
            str(dest_dir / name), 16000,
            (row['audio']['array'] * 32767).astype(np.int16)
        )


def download_audioset(dest_dir: Path, max_hours: float = 1.0) -> None:
    """Télécharge AudioSet via l'API HuggingFace datasets (streaming, pas de tar).

    Note : l'URL tar directe (bal_train09.tar) retourne 404 depuis HuggingFace.
    On utilise le streaming datasets pour contourner le problème.
    max_hours : durée approximative de clips à télécharger (clips de ~10s).
    """
    if dest_dir.exists() and any(dest_dir.glob("*.wav")):
        log.info(f"Cache hit : {dest_dir.name} (AudioSet)")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    import datasets as hf_datasets
    import scipy.io.wavfile
    import numpy as np
    from tqdm import tqdm

    log.info(f"Téléchargement AudioSet (streaming HuggingFace, ~{max_hours}h)...")
    ds = hf_datasets.load_dataset(
        "agkphysics/AudioSet", "balanced",
        split="train", streaming=True
    )
    ds = iter(ds.cast_column("audio", hf_datasets.Audio(sampling_rate=16000)))

    # ~10s par clip AudioSet -> max_hours * 3600 / 10 clips
    max_clips = int(max_hours * 3600 / 10)
    for i, row in enumerate(tqdm(ds, total=max_clips)):
        if i >= max_clips:
            break
        name = f"audioset_{i:06d}.wav"
        scipy.io.wavfile.write(
            str(dest_dir / name), 16000,
            (row['audio']['array'] * 32767).astype(np.int16)
        )


# ---------------------------------------------------------------------------
# Configuration YAML
# ---------------------------------------------------------------------------

def make_config(positive_clips_dir: Path, cache_dir: Path,
                output_dir: Path) -> dict:
    """Génère le dictionnaire de configuration pour openwakeword/train.py."""
    return {
        "model_name": "ah_que_coucou",
        "target_phrase": [
            "ah que coucou",
            "ah, que coucou",
            "à que coucou",
            "ah que coucou !",
        ],
        "custom_negative_phrases": [],

        # On pointe directement vers nos clips déjà générés.
        # train.py attend un dossier "positive" sous output_dir/clips/train/
        # On le crée comme lien symbolique vers nos clips.
        "n_samples": 5000,
        "n_samples_val": 500,
        "tts_batch_size": 50,
        "augmentation_batch_size": 16,

        # piper_sample_generator_path pointe vers notre stub generate_samples.py
        # (train.py fait toujours cet import, même sans --generate_clips)
        "piper_sample_generator_path": "/app",

        "output_dir": str(output_dir),

        "rir_paths": [str(cache_dir / "mit_rirs")],
        # background_paths vide : AudioSet/FMA incompatibles avec datasets 2.14.6
        # (parquet format trop récent -> TypeError). Le mixing background est désactivé ;
        # augment_clips() gère bien le cas background_clip_paths=[].
        "background_paths": [],
        "background_paths_duplication_rate": [],

        "false_positive_validation_data_path": str(
            cache_dir / "validation_set_features.npy"
        ),
        "augmentation_rounds": 1,

        "feature_data_files": {
            "ACAV100M_sample": str(
                cache_dir / "openwakeword_features_ACAV100M_2000_hrs_16bit.npy"
            )
        },
        "batch_n_per_class": {
            "ACAV100M_sample": 1024,
            "adversarial_negative": 50,
            "positive": 50,
        },

        "model_type": "dnn",
        "layer_size": 32,
        "steps": 50000,
        "max_negative_weight": 1500,
        "target_false_positives_per_hour": 0.2,

        # Paramètres ajoutés pour target_accuracy et target_recall
        # (utilisés pour l'early stopping)
        "target_accuracy": 0.7,
        "target_recall": 0.5,
    }


def generate_adversarial_clips_espeak(dest_dir: Path, n_clips: int = 5000) -> None:
    """Génère des clips adversariaux (phonétiquement proches mais incorrects)
    avec espeak-ng en français. Rapide (~100 clips/s).

    Ces clips permettent au modèle d'apprendre à NE PAS déclencher sur des
    phrases similaires à "ah que coucou".
    """
    if dest_dir.exists() and len(list(dest_dir.glob("*.wav"))) >= n_clips:
        log.info(f"Cache hit : {dest_dir.name} ({n_clips} clips adversariaux)")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)

    import subprocess
    import uuid
    import scipy.io.wavfile
    import numpy as np

    # Phrases phonétiquement similaires mais pas le wake word
    phrases = [
        "coucou",
        "que coucou",
        "ah coucou",
        "oh que coucou",
        "eh que coucou",
        "ah le coucou",
        "à le coucou",
        "ah que",
        "ah que cou",
        "voilà le coucou",
        "c'est le coucou",
        "bonjour coucou",
        "un que coucou",
        "ah des coucous",
        "ah quelque chose",
        "ah quel coucou",
        "ah quoi coucou",
        "là que coucou",
        "ha que coucou",
        "ah que coucous",
        "il crie coucou",
        "entends le coucou",
        "ah que côté",
    ]

    clips_per_phrase = max(1, n_clips // len(phrases))
    total = 0
    log.info(f"Génération de {n_clips} clips adversariaux avec espeak-ng...")

    for phrase in phrases:
        for _ in range(clips_per_phrase):
            if total >= n_clips:
                break
            fname = dest_dir / f"{uuid.uuid4().hex}.wav"
            # espeak-ng : fr, 16kHz, WAV, légèrement variable (rate aléatoire)
            rate = np.random.randint(140, 200)
            result = subprocess.run(
                ["espeak-ng", "-v", "fr", "-s", str(rate), "-w", str(fname), phrase],
                capture_output=True
            )
            if result.returncode == 0 and fname.exists():
                # Resampler à 16kHz (espeak-ng génère du 22050 Hz par défaut)
                import scipy.io.wavfile
                import scipy.signal
                import numpy as np
                sr, data = scipy.io.wavfile.read(str(fname))
                if sr != 16000:
                    data_f = data.astype(np.float32)
                    n_samples = int(len(data_f) * 16000 / sr)
                    data_f = scipy.signal.resample(data_f, n_samples)
                    data = np.clip(data_f, -32768, 32767).astype(np.int16)
                    scipy.io.wavfile.write(str(fname), 16000, data)
                total += 1

    log.info(f"  {total} clips adversariaux générés dans {dest_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Entraîne un modèle openWakeWord custom 'ah que coucou'"
    )
    parser.add_argument(
        "--positive_clips", required=True,
        help="Dossier contenant les clips WAV positifs générés par generate_tts.py"
    )
    parser.add_argument(
        "--cache_dir", required=True,
        help="Dossier pour les téléchargements volumineux (ACAV100M, etc.)"
    )
    parser.add_argument(
        "--output_dir", required=True,
        help="Dossier de sortie pour le modèle entraîné"
    )
    parser.add_argument(
        "--skip_download", action="store_true",
        help="Sauter les téléchargements (utile si le cache est déjà rempli)"
    )
    parser.add_argument(
        "--skip_augment", action="store_true",
        help="Sauter l'étape d'augmentation (si déjà faite)"
    )
    args = parser.parse_args()

    positive_clips = Path(args.positive_clips)
    cache_dir = Path(args.cache_dir)
    output_dir = Path(args.output_dir)

    if not positive_clips.exists() or not any(positive_clips.glob("*.wav")):
        log.error(f"Dossier de clips positifs vide ou introuvable : {positive_clips}")
        sys.exit(1)

    n_clips = len(list(positive_clips.glob("*.wav")))
    log.info(f"{n_clips} clips positifs trouvés dans {positive_clips}")

    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Téléchargements
    # ------------------------------------------------------------------
    if not args.skip_download:
        log.info("=== Étape 1/4 : Téléchargements ===")

        download_if_missing(
            "https://huggingface.co/datasets/davidscripka/openwakeword_features"
            "/resolve/main/openwakeword_features_ACAV100M_2000_hrs_16bit.npy",
            cache_dir / "openwakeword_features_ACAV100M_2000_hrs_16bit.npy",
            "features ACAV100M (~17 Go, négatifs entraînement)"
        )
        download_if_missing(
            "https://huggingface.co/datasets/davidscripka/openwakeword_features"
            "/resolve/main/validation_set_features.npy",
            cache_dir / "validation_set_features.npy",
            "features validation (~185 Mo)"
        )
        download_mit_rirs(cache_dir / "mit_rirs")
        # Note : AudioSet et FMA sont incompatibles avec datasets 2.14.6
        # (format parquet trop récent). On utilise uniquement MIT RIRs pour
        # la réverbération. Le background mixing est désactivé (background_paths=[]).
    else:
        log.info("Téléchargements ignorés (--skip_download)")

    # ------------------------------------------------------------------
    # 2. Copier les clips positifs là où train.py les attend
    #    Structure attendue par train.py :
    #      output_dir/ah_que_coucou/positive_train/*.wav  (~4500 clips)
    #      output_dir/ah_que_coucou/positive_test/*.wav   (~500 clips)
    #      output_dir/ah_que_coucou/negative_train/*.wav  (adversariaux)
    #      output_dir/ah_que_coucou/negative_test/*.wav   (adversariaux)
    # ------------------------------------------------------------------
    log.info("=== Étape 2/4 : Préparation des clips ===")
    model_dir = output_dir / "ah_que_coucou"
    model_dir.mkdir(parents=True, exist_ok=True)

    pos_train_dir = model_dir / "positive_train"
    pos_test_dir  = model_dir / "positive_test"
    neg_train_dir = model_dir / "negative_train"
    neg_test_dir  = model_dir / "negative_test"

    import shutil

    # Clips positifs : 90% train / 10% test
    all_clips = sorted(positive_clips.glob("*.wav"))
    n_test = max(100, len(all_clips) // 10)
    clips_train = all_clips[:-n_test]
    clips_test  = all_clips[-n_test:]

    for dest, clips in [(pos_train_dir, clips_train), (pos_test_dir, clips_test)]:
        dest.mkdir(parents=True, exist_ok=True)
        existing = list(dest.glob("*.wav"))
        if existing:
            log.info(f"  {len(existing)} clips déjà présents dans {dest.name}, skip.")
        else:
            import scipy.io.wavfile
            import scipy.signal
            import numpy as np
            TARGET_SR = 16000
            log.info(f"  Copie + resampling {len(clips)} clips vers {dest.name} ({TARGET_SR} Hz)...")
            for clip in clips:
                sr, data = scipy.io.wavfile.read(str(clip))
                if sr != TARGET_SR:
                    # Resample float32 pour éviter les overflows
                    data_f = data.astype(np.float32)
                    n_samples = int(len(data_f) * TARGET_SR / sr)
                    data_f = scipy.signal.resample(data_f, n_samples)
                    data = np.clip(data_f, -32768, 32767).astype(np.int16)
                scipy.io.wavfile.write(str(dest / clip.name), TARGET_SR, data)

    # Clips adversariaux avec espeak-ng
    n_adv = max(500, len(clips_train) // 10)
    n_adv_test = max(100, n_adv // 10)
    generate_adversarial_clips_espeak(neg_train_dir, n_clips=n_adv)
    generate_adversarial_clips_espeak(neg_test_dir,  n_clips=n_adv_test)

    # ------------------------------------------------------------------
    # 3. Générer le fichier de config YAML
    # ------------------------------------------------------------------
    log.info("=== Étape 3/4 : Génération de la config YAML ===")
    config = make_config(positive_clips, cache_dir, output_dir)
    config_path = output_dir / "ah_que_coucou.yml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    log.info(f"  Config écrite : {config_path}")

    # ------------------------------------------------------------------
    # 4. Lancer train.py
    # ------------------------------------------------------------------
    train_script = "/opt/openwakeword/openwakeword/train.py"

    # train.py importe generate_samples au toplevel (import inconditionnel).
    # On copie notre stub dans le même dossier que train.py pour satisfaire cet import.
    stub_src = Path(__file__).parent / "generate_samples_stub.py"
    stub_dst = Path(train_script).parent / "generate_samples.py"
    if stub_src.exists() and not stub_dst.exists():
        shutil.copy(stub_src, stub_dst)
        log.info(f"  Stub generate_samples.py copié dans {stub_dst.parent}")

    if not args.skip_augment:
        log.info("=== Étape 4a/4 : Augmentation des clips ===")
        ret = os.system(
            f"{sys.executable} {train_script} "
            f"--training_config {config_path} --augment_clips"
        )
        if ret != 0:
            log.error("Augmentation échouée (code %d)", ret)
            sys.exit(ret)
    else:
        log.info("Augmentation ignorée (--skip_augment)")

    log.info("=== Étape 4b/4 : Entraînement du modèle ===")
    ret = os.system(
        f"{sys.executable} {train_script} "
        f"--training_config {config_path} --train_model"
    )
    if ret != 0:
        # Vérifier si le .onnx est quand même présent (crash post-export, ex. conversion tflite)
        onnx_path = output_dir / "ah_que_coucou.onnx"
        if onnx_path.exists():
            log.warning(
                "train.py a retourné un code d'erreur (%d) mais le fichier .onnx "
                "est présent - le crash est probablement post-export (ex. conversion "
                "tflite). On continue.", ret
            )
        else:
            log.error("Entraînement échoué (code %d)", ret)
            sys.exit(ret)

    # ------------------------------------------------------------------
    # 5. Résumé
    # ------------------------------------------------------------------
    onnx_candidates = list(output_dir.glob("**/*.onnx"))
    log.info("=== Entraînement terminé ===")
    if onnx_candidates:
        for f in onnx_candidates:
            log.info(f"  Modèle exporté : {f}")
        log.info("")
        log.info("Pour copier sur le RPi :")
        log.info(f"  scp {onnx_candidates[0]} pi@raspberrypi.local:~/")
    else:
        log.warning("Aucun fichier .onnx trouvé dans le dossier de sortie.")


if __name__ == "__main__":
    main()
