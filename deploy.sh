#!/usr/bin/env bash
# Déploiement sur le Raspberry Pi.
#
# Usage: ./deploy.sh user@host
# Exemple: ./deploy.sh pi@raspberrypi.local

set -e

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    echo "Usage: $0 user@host"
    exit 1
fi

REMOTE_DIR="~/aquecoucou"

echo "==> Transfert vers $TARGET..."
ssh "$TARGET" "mkdir -p $REMOTE_DIR"
tar -czf - \
    aquecoucou.py \
    wakeword.py \
    wakeword/output/ah_que_coucou.onnx \
    $([ -f wakeword/output/ah_que_coucou.onnx.data ] && echo wakeword/output/ah_que_coucou.onnx.data) \
    sounds/ \
    tests/ \
    deploy/aquecoucou.service \
    setup.sh \
| ssh "$TARGET" "cd $REMOTE_DIR && tar -xzf -"

echo "==> Mise à jour du service systemd..."
ssh "$TARGET" "sudo cp $REMOTE_DIR/deploy/aquecoucou.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl stop aquecoucou && sleep 3 && sudo systemctl start aquecoucou"

echo ""
echo "Déployé sur $TARGET:$REMOTE_DIR"
echo "Service redémarré."
echo ""
echo "Premier déploiement ? Lancer le setup d'abord :"
echo "   ssh $TARGET 'cd $REMOTE_DIR && ./setup.sh'"
