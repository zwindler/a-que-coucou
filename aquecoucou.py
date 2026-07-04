#!/usr/bin/env python3
"""
La Boîte à Coucou - orchestrateur principal.

Détecte "ah que coucou" via le micro, monte l'œuf avec le servo,
joue le son, puis redescend l'œuf.

Usage :
    python3 aquecoucou.py
    python3 aquecoucou.py --device 0 --threshold 0.6

Variables d'environnement (optionnelles) :
    SERVO_HIGH   duty cycle position haute / œuf sorti  (défaut: 0.025)
    SERVO_LOW    duty cycle position basse / repos       (défaut: 0.130)
    APLAY_ARGS   arguments aplay                        (défaut: -D plughw:0,0)
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

SOUNDS_DIR = Path(__file__).parent / "sounds"
SERVO_HIGH = float(os.environ.get("SERVO_HIGH", "0.025"))
SERVO_LOW  = float(os.environ.get("SERVO_LOW",  "0.130"))
APLAY_ARGS = os.environ.get("APLAY_ARGS", "-D plughw:0,0").split()

PWM_CHIP    = "/sys/class/pwm/pwmchip0"
PWM_CHANNEL = "pwm1"  # GPIO13 = pwmchip0/pwm1
PWM_PERIOD  = 20_000_000  # 20ms = 50Hz


def servo_write(path, value):
    with open(path, "w") as f:
        f.write(str(value))


def servo_duty(duty_cycle):
    path = f"{PWM_CHIP}/{PWM_CHANNEL}/duty_cycle"
    servo_write(path, int(duty_cycle * PWM_PERIOD))


def servo_setup():
    pwm_path = f"{PWM_CHIP}/{PWM_CHANNEL}"
    if not os.path.exists(pwm_path):
        servo_write(f"{PWM_CHIP}/export", 1)
        time.sleep(0.1)
    servo_write(f"{pwm_path}/period", PWM_PERIOD)
    servo_duty(SERVO_LOW)
    servo_write(f"{pwm_path}/enable", 1)


def servo_teardown():
    servo_duty(SERVO_LOW)
    servo_write(f"{PWM_CHIP}/{PWM_CHANNEL}/enable", 0)


def play_sound():
    sound = SOUNDS_DIR / "boite_a_coucou.wav"
    subprocess.run(["/usr/bin/aplay"] + APLAY_ARGS + [str(sound)], check=True)


def trigger(score):
    print(f"Déclenché ! score={score:.4f}")

    servo_duty(SERVO_HIGH)
    time.sleep(0.25)   # laisse le servo atteindre la position haute

    try:
        play_sound()   # bloquant - redescend seulement quand le son est fini
    except Exception as e:
        print(f"Erreur son : {e}")
    finally:
        time.sleep(0.35)
        servo_duty(SERVO_LOW)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device",    default="0")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--cooldown",  type=float, default=3.0)
    parser.add_argument("--model",     default=None)
    args = parser.parse_args()

    servo_setup()

    def shutdown(sig, frame):
        print("\nArrêt...")
        servo_teardown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT,  shutdown)

    from wakeword import listen
    kwargs = dict(threshold=args.threshold, cooldown=args.cooldown, device=args.device)
    if args.model:
        kwargs["model_path"] = args.model
    listen(trigger, **kwargs)


if __name__ == "__main__":
    main()
