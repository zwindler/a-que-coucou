#!/usr/bin/env bash
# Installation sur le Raspberry Pi.
# À lancer une seule fois depuis le dossier ~/aquecoucou.
#
# Usage: ./setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
CONFIG="/boot/firmware/config.txt"

echo "==> Paquets système..."
sudo apt-get update -qq
sudo apt-get install -y python3-venv python3-dev portaudio19-dev

echo "==> Environnement Python..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install numpy sounddevice scipy openwakeword

echo "==> Configuration /boot/firmware/config.txt..."

# Désactiver l'audio BCM (conflit avec I2S)
if grep -q "^dtparam=audio=on" "$CONFIG"; then
    sudo sed -i 's/^dtparam=audio=on/#dtparam=audio=on/' "$CONFIG"
    echo "   dtparam=audio=on commenté"
fi

# PWM hardware sur GPIO13
if ! grep -q "pwm-2chan" "$CONFIG"; then
    echo "dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4" | sudo tee -a "$CONFIG" > /dev/null
    echo "   dtoverlay=pwm-2chan ajouté"
fi

# I2S micro + ampli
if ! grep -q "googlevoicehat-soundcard" "$CONFIG"; then
    echo "dtoverlay=googlevoicehat-soundcard" | sudo tee -a "$CONFIG" > /dev/null
    echo "   dtoverlay=googlevoicehat-soundcard ajouté"
fi

echo "==> Installation du service systemd..."
sudo cp "$SCRIPT_DIR/deploy/aquecoucou.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aquecoucou.service
echo "   Service installé et activé (démarrera au prochain boot)"

echo ""
echo "Installation terminée. Redémarrer le RPi pour appliquer les overlays :"
echo "   sudo reboot"
echo ""
echo "Vérification après reboot :"
echo "   pinctrl get 13    # doit afficher a0 (PWM)"
echo "   pinctrl get 18    # doit afficher a2 (I2S)"
echo "   arecord -l        # doit afficher sndrpigooglevoi"
echo "   aplay -l          # doit afficher sndrpigooglevoi"
