#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Genera tráfico contra la app para que los gráficos tengan datos.
#
# Uso:
#   ./generar-trafico.sh            → tráfico normal, 60 segundos
#   ./generar-trafico.sh errores    → mete muchos errores (para ver el panel rojo)
#   ./generar-trafico.sh lento      → mete requests lentas (para ver el p95 subir)
# ─────────────────────────────────────────────────────────────
set -u

URL="http://localhost:8000"
MODO="${1:-normal}"
DURACION="${2:-60}"

echo "Generando tráfico en modo '$MODO' durante ${DURACION}s contra $URL"
echo "Cortá con Ctrl+C cuando quieras."

FIN=$(( $(date +%s) + DURACION ))

while [ "$(date +%s)" -lt "$FIN" ]; do
  case "$MODO" in
    errores)
      # 1 de cada 3 requests falla
      curl -s -o /dev/null "$URL/" &
      curl -s -o /dev/null "$URL/error" &
      curl -s -o /dev/null "$URL/" &
      ;;
    lento)
      curl -s -o /dev/null "$URL/" &
      curl -s -o /dev/null "$URL/lento" &
      ;;
    *)
      # tráfico sano: casi todo OK, algún error ocasional
      curl -s -o /dev/null "$URL/" &
      curl -s -o /dev/null "$URL/" &
      if [ $(( RANDOM % 20 )) -eq 0 ]; then
        curl -s -o /dev/null "$URL/error" &
      fi
      ;;
  esac
  wait
  sleep 0.3
done

echo "Listo. Mirá el dashboard en http://localhost:3000"
