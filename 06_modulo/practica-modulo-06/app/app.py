"""
App de ejemplo para la práctica del Módulo 6.

Expone cuatro rutas:
  GET /          → responde rápido (tráfico normal)
  GET /lento     → tarda entre 1 y 3 segundos (latencia alta)
  GET /error     → devuelve HTTP 500 (fallos)
  GET /metrics   → el endpoint que lee Prometheus

Lo importante para la clase está en las tres métricas de abajo:
un counter, un histogram y un gauge.
"""
import random
import time

from flask import Flask, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# MÉTRICA 1 — COUNTER: solo sube, nunca baja.
# Cuenta cuántas requests entraron, separadas por ruta y código.
# Se consulta siempre con rate(), nunca en crudo.
# ─────────────────────────────────────────────────────────────
REQUESTS = Counter(
    "http_requests_total",
    "Cantidad total de requests HTTP",
    ["ruta", "metodo", "codigo"],
)

# ─────────────────────────────────────────────────────────────
# MÉTRICA 2 — HISTOGRAM: reparte los valores en buckets.
# Permite calcular percentiles (p50, p95, p99) con PromQL.
# ─────────────────────────────────────────────────────────────
DURACION = Histogram(
    "http_duration_seconds",
    "Duración de las requests HTTP en segundos",
    ["ruta"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# ─────────────────────────────────────────────────────────────
# MÉTRICA 3 — GAUGE: sube y baja. El valor actual es lo que importa.
# Cuántas requests se están procesando en este instante.
# ─────────────────────────────────────────────────────────────
EN_CURSO = Gauge(
    "http_requests_en_curso",
    "Requests que se están procesando ahora mismo",
)


def registrar(ruta, metodo, codigo, inicio):
    """Actualiza el counter y el histogram al terminar una request."""
    REQUESTS.labels(ruta=ruta, metodo=metodo, codigo=str(codigo)).inc()
    DURACION.labels(ruta=ruta).observe(time.time() - inicio)


@app.route("/")
def home():
    inicio = time.time()
    EN_CURSO.inc()
    try:
        time.sleep(random.uniform(0.01, 0.15))
        registrar("/", "GET", 200, inicio)
        return {"mensaje": "todo bien", "servicio": "app-demo"}
    finally:
        EN_CURSO.dec()


@app.route("/lento")
def lento():
    """Simula una operación pesada: sirve para ver el p95 dispararse."""
    inicio = time.time()
    EN_CURSO.inc()
    try:
        time.sleep(random.uniform(1.0, 3.0))
        registrar("/lento", "GET", 200, inicio)
        return {"mensaje": "tarde bastante"}
    finally:
        EN_CURSO.dec()


@app.route("/error")
def error():
    """Simula una falla: sirve para ver la tasa de error subir."""
    inicio = time.time()
    EN_CURSO.inc()
    try:
        time.sleep(random.uniform(0.01, 0.1))
        registrar("/error", "GET", 500, inicio)
        return {"error": "algo salio mal"}, 500
    finally:
        EN_CURSO.dec()


@app.route("/metrics")
def metrics():
    """El endpoint que Prometheus va a buscar cada 15 segundos."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
