#!/usr/bin/env python3
"""
Test du servo SG90 via PWM sysfs (GPIO13 = pwmchip0/pwm1).

Prérequis :
    sudo pinctrl set 13 a0   (ou ExecStartPre dans le service systemd)

Enchaîne : position basse -> position haute -> position basse.
"""

import os
import sys
import time

PWM_CHIP    = "/sys/class/pwm/pwmchip0"
PWM_CHANNEL = "pwm1"
PWM_PATH    = f"{PWM_CHIP}/{PWM_CHANNEL}"
PWM_PERIOD  = 20_000_000  # 20ms = 50Hz

# Duty cycles validés sur SG90 clone TowerPro
SERVO_LOW  = 0.130  # repos (œuf rentré)
SERVO_HIGH = 0.025  # œuf sorti


def write(path, value):
    with open(path, "w") as f:
        f.write(str(value))


def set_duty(duty_cycle):
    write(f"{PWM_PATH}/duty_cycle", int(duty_cycle * PWM_PERIOD))


def setup():
    if not os.path.exists(PWM_PATH):
        write(f"{PWM_CHIP}/export", 1)
        time.sleep(0.1)
    write(f"{PWM_PATH}/period", PWM_PERIOD)
    set_duty(SERVO_LOW)
    write(f"{PWM_PATH}/enable", 1)


def teardown():
    set_duty(SERVO_LOW)
    write(f"{PWM_PATH}/enable", 0)


if os.geteuid() != 0 and not os.access(f"{PWM_CHIP}/export", os.W_OK):
    print("Erreur : accès PWM refusé. Lancer avec sudo ou configurer les permissions.")
    sys.exit(1)

print("Setup PWM...")
setup()

print(f"Position basse (duty={SERVO_LOW})...")
set_duty(SERVO_LOW)
time.sleep(1)

print(f"Position haute (duty={SERVO_HIGH})...")
set_duty(SERVO_HIGH)
time.sleep(1)

print(f"Retour position basse (duty={SERVO_LOW})...")
set_duty(SERVO_LOW)
time.sleep(0.5)

teardown()
print("Test terminé.")
