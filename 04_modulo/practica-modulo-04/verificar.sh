#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# verificar.sh — Chequea que el entorno esté listo ANTES de la clase.
# Uso:  bash verificar.sh
# ─────────────────────────────────────────────────────────────
ok=0; fail=0
check() {
  if eval "$2" >/dev/null 2>&1; then
    echo "  [OK]    $1"; ok=$((ok+1))
  else
    echo "  [FALTA] $1"; echo "          -> $3"; fail=$((fail+1))
  fi
}

echo ""
echo "Verificando el entorno para la clase de Kubernetes"
echo "---------------------------------------------------"

check "kubectl instalado"        "kubectl version --client"        "Instalar kubectl: kubernetes.io/docs/tasks/tools"
check "Un cluster alcanzable"    "kubectl get nodes"               "Arrancar el cluster: minikube start"
check "El nodo está Ready"       "kubectl get nodes | grep -q Ready" "Esperar un minuto y reintentar"
check "Addon ingress activo"     "kubectl get ns ingress-nginx"    "minikube addons enable ingress"
check "metrics-server activo"    "kubectl top nodes"               "minikube addons enable metrics-server (tarda 1-2 min)"

echo "---------------------------------------------------"
if [ "$fail" -eq 0 ]; then
  echo "  Todo listo. $ok de $((ok+fail)) verificaciones pasaron."
else
  echo "  $fail cosa(s) por resolver antes de la clase."
  echo "  Si no llegás, avisá: igual podés trabajar en grupo."
fi
echo ""
