#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# generar-carga.sh — Hace subir la CPU para ver escalar el HPA.
#
# Uso:
#   bash generar-carga.sh          # arranca la carga
#   Ctrl+C                         # la corta
#
# En OTRA terminal, mirá:  kubectl get hpa --watch
# El HPA tarda entre 1 y 2 minutos en reaccionar.
# ─────────────────────────────────────────────────────────────
set -u
echo "Generando carga contra web-svc. Cortá con Ctrl+C."
echo "En otra terminal mirá:  kubectl get hpa --watch"
echo ""

kubectl run carga-$RANDOM \
  --rm -it \
  --restart=Never \
  --image=busybox:1.36 \
  -- /bin/sh -c 'while true; do wget -q -O- http://web-svc >/dev/null; done'
