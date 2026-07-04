"""
Stub de generate_samples pour satisfaire l'import de train.py.
On n'utilise pas piper-sample-generator (génération TTS déjà faite
avec Coqui XTTS v2). Ce stub lève une erreur claire si la fonction
est appelée à tort.
"""


def generate_samples(*args, **kwargs):
    raise RuntimeError(
        "generate_samples() ne doit pas être appelée : "
        "les clips positifs sont déjà générés par generate_tts.py (Coqui XTTS v2)."
    )
