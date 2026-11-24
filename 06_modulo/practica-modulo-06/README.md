# Práctica — Módulo 6: Observabilidad y Monitoreo

**Tiempo estimado:** 60 a 75 minutos
**Se entrega:** capturas del dashboard + una métrica propia + el diseño de un SLO
**Necesitás:** Docker Desktop corriendo. Nada más.

---

## Qué vas a construir

Un stack de observabilidad completo, corriendo en tu máquina:

```
   ┌──────────────┐  expone      ┌──────────────┐  consulta   ┌──────────────┐
   │     app      │  /metrics    │  prometheus  │             │   grafana    │
   │   :8000      │ ◀─ scrape ── │    :9090     │ ◀────────── │    :3000     │
   │  Flask +     │   cada 15s   │ guarda series│             │  dibuja los  │
   │  3 métricas  │              │ evalúa alertas│            │  dashboards  │
   └──────────────┘              └──────────────┘             └──────────────┘
```

Son tres contenedores que levanta un solo comando. El datasource de Grafana y el dashboard ya vienen preconfigurados: no vas a tener que conectar nada a mano.

---

# Ejercicio 1 — Levantar el stack

**Tiempo:** 15 minutos

## Paso 1 — Verificar que Docker está corriendo

```bash
docker --version
docker compose version
```

Si el segundo comando falla, probá `docker-compose version` (con guion). Docker Desktop moderno usa `docker compose`; instalaciones viejas usan `docker-compose`. Ajustá los comandos de abajo según cuál te funcione.

Si te dice `Cannot connect to the Docker daemon`, abrí Docker Desktop y esperá a que el ícono deje de moverse.

## Paso 2 — Descargar las imágenes

Este paso es opcional pero conviene hacerlo antes, porque descarga unos 400 MB:

```bash
cd practica-modulo-06
docker compose pull
```

## Paso 3 — Levantar todo

```bash
docker compose up -d
```

El flag `-d` (*detached*) hace que corra en segundo plano y te devuelva la terminal. La primera vez tarda un par de minutos porque construye la imagen de la app.

Verificá que los tres están arriba:

```bash
docker compose ps
```

Tenés que ver:

```
NAME             IMAGE                      STATUS         PORTS
obs-app          practica-modulo-06-app     Up 30 seconds  0.0.0.0:8000->8000/tcp
obs-prometheus   prom/prometheus:v2.53.0    Up 29 seconds  0.0.0.0:9090->9090/tcp
obs-grafana      grafana/grafana:11.1.0     Up 28 seconds  0.0.0.0:3000->3000/tcp
```

## Paso 4 — Ver las métricas crudas

Antes de mirar gráficos lindos, mirá el dato en bruto. Esto es lo que Prometheus lee:

```bash
curl localhost:8000/metrics
```

Vas a ver mucho texto. Buscá estas líneas:

```
# HELP http_requests_total Cantidad total de requests HTTP
# TYPE http_requests_total counter
http_requests_total{codigo="200",metodo="GET",ruta="/"} 3.0
```

**Eso es todo lo que tu aplicación tiene que hacer para ser observable:** publicar texto plano en un endpoint. Prometheus se encarga del resto.

## Paso 5 — Confirmar que Prometheus la está viendo

Abrí en el navegador: **http://localhost:9090/targets**

Tenés que ver el job `app-demo` con estado **UP** en verde. Si dice DOWN, mirá la sección de problemas al final.

## ✅ Cómo saber que salió bien

- `docker compose ps` muestra tres contenedores `Up`
- `curl localhost:8000/metrics` devuelve texto con métricas
- En `localhost:9090/targets`, `app-demo` está en **UP**

---

# Ejercicio 2 — Generar tráfico y leer el dashboard

**Tiempo:** 20 minutos

Un dashboard sin datos no enseña nada. Vamos a generar tráfico real.

## Paso 1 — Abrir Grafana

Andá a **http://localhost:3000**

- Usuario: `admin`
- Contraseña: `admin`

Te va a pedir cambiar la contraseña: podés saltear con "Skip".

En el menú lateral, entrá a **Dashboards** y abrí **"App — RED (Rate, Errors, Duration)"**. Está vacío, porque todavía nadie usó la app.

## Paso 2 — Generar tráfico normal

En la terminal, **dejá esto corriendo** y poné la ventana de Grafana al lado:

```bash
./generar-trafico.sh
```

> **En Windows:** si el `.sh` no corre, usá Git Bash. O generá tráfico a mano abriendo `http://localhost:8000` en el navegador y refrescando varias veces.

Esperá entre 30 y 60 segundos y mirá el dashboard. Los cuatro paneles empiezan a llenarse.

## Paso 3 — Entender qué muestra cada panel

Tomate el tiempo de leerlos, porque este es el contenido real del ejercicio:

| Panel | Qué mide | Qué mirar |
|---|---|---|
| **RATE** | Requests por segundo, separadas por ruta | Debería estabilizarse en un valor parejo |
| **ERRORS** | Qué porcentaje de las requests falla | Con tráfico normal ronda el 5 % o menos |
| **DURATION** | Latencia p50 y p95 | El p95 siempre está por encima del p50. **Esa distancia es la que el promedio te oculta** |
| **En curso** | Gauge de requests procesándose ahora | Sube y baja. No usa `rate()` |

## Paso 4 — Romper la app a propósito

Ahora viene lo interesante. Cortá el script (Ctrl+C) y corré:

```bash
./generar-trafico.sh errores 60
```

**Mirá el panel ERRORS mientras corre.** En unos 15 segundos empieza a subir hasta superar el 30 %.

Fijate en el retraso: el gráfico no reacciona instantáneamente. Prometheus hace scrape cada 15 segundos, así que siempre vas a ver el mundo con esa demora. **Es un detalle importante para cuando estés en un incidente real:** el gráfico te muestra el pasado reciente, no el instante exacto.

## Paso 5 — Hacerla lenta

```bash
./generar-trafico.sh lento 60
```

Ahora mirá el panel **DURATION**. El p95 se dispara por encima de 1 segundo, mientras el p50 se mantiene bajo.

**Ese es exactamente el punto de usar percentiles:** la mayoría de los usuarios sigue teniendo una buena experiencia (p50 bajo), pero hay un grupo que la está pasando mal (p95 alto). Un promedio habría mezclado las dos cosas y no te habría mostrado ninguna.

## Paso 6 — Ver las alertas

Andá a **http://localhost:9090/alerts**

Vas a ver las tres alertas definidas. Mientras corre el modo `errores`, la alerta `TasaDeErrorAlta` pasa de verde (*Inactive*) a amarillo (*Pending*) y, después de 2 minutos sostenidos, a rojo (*Firing*).

**Ese estado "Pending" es el campo `for: 2m` en acción.** Sin él, cualquier pico de un segundo dispararía la alerta y despertaría a alguien para nada.

Abrí el archivo `prometheus/alertas.yml` y leé las tres reglas. Fijate que todas alertan sobre **síntomas que nota el usuario**, nunca sobre CPU o memoria.

## Paso 7 — Capturas para la entrega

Sacá dos capturas del dashboard:

1. Con tráfico normal (todo tranquilo)
2. Durante el modo `errores` (el panel ERRORS arriba del 30 %)

## ✅ Cómo saber que salió bien

- Los cuatro paneles tienen datos
- Viste el panel ERRORS subir al generar errores
- Viste el p95 separarse del p50 en modo lento
- Encontraste una alerta en estado Pending o Firing

---

# Ejercicio 3 — Agregar tu propia métrica

**Tiempo:** 20 minutos

Hasta acá usaste métricas que ya estaban. Ahora vas a crear una.

## Paso 1 — Elegir qué medir

Vamos a agregar un **counter** que cuente cuántas veces se visitó cada ruta desde que arrancó la app, pero separado por si el usuario llegó a una ruta lenta o rápida. O el que vos quieras: lo importante es el proceso.

Un ejemplo simple y útil: **contar visitas a una ruta nueva**.

## Paso 2 — Editar la app

Abrí `app/app.py`. Después de las tres métricas que ya existen, agregá la tuya:

```python
# ── MI MÉTRICA ──
SALUDOS = Counter(
    "saludos_total",
    "Cantidad de saludos enviados",
    ["idioma"],
)
```

Y abajo, antes de `@app.route("/metrics")`, agregá una ruta que la use:

```python
@app.route("/saludo")
def saludo():
    inicio = time.time()
    idioma = random.choice(["es", "en", "pt"])
    SALUDOS.labels(idioma=idioma).inc()
    registrar("/saludo", "GET", 200, inicio)
    return {"saludo": {"es": "hola", "en": "hello", "pt": "olá"}[idioma]}
```

> **Fijate en la etiqueta `idioma`:** tiene solo tres valores posibles. Eso es cardinalidad baja y está perfecto. Si en vez de eso etiquetaras por ID de usuario, crearías una serie temporal por cada usuario y tumbarías Prometheus. Es el error número uno de quien recién empieza.

## Paso 3 — Reconstruir y reiniciar

Como cambiaste el código, hay que reconstruir la imagen:

```bash
docker compose up -d --build app
```

Verificá que la métrica aparece:

```bash
curl localhost:8000/saludo
curl localhost:8000/saludo
curl localhost:8000/metrics | grep saludos
```

Tenés que ver algo como:

```
saludos_total{idioma="es"} 1.0
saludos_total{idioma="en"} 1.0
```

## Paso 4 — Graficarla en Grafana

1. En el dashboard, arriba a la derecha, clic en **Edit** y después en **Add** → **Visualization**
2. Elegí el datasource **Prometheus**
3. En el campo de query, pegá:
   ```
   sum by (idioma) (rate(saludos_total[1m]))
   ```
4. En **Legend** poné `{{idioma}}`
5. Ponele un título al panel: "Saludos por idioma"
6. Clic en **Save dashboard** arriba a la derecha

Generá algunas visitas más a `/saludo` y mirá cómo se dibuja.

**Sacá una captura de tu panel nuevo con datos.**

## ✅ Cómo saber que salió bien

- `curl localhost:8000/metrics | grep saludos` muestra tu métrica
- Tenés un panel nuevo en el dashboard con datos

---

# Ejercicio 4 — Diseñar un SLO (en papel)

**Tiempo:** 15 minutos

Este ejercicio no tiene código. Es el más importante de los cuatro, porque es el que te obliga a pensar en el usuario y no en la máquina.

## La consigna

Elegí **un servicio real que conozcas**: el de tu trabajo, una app que uses, o la app de esta práctica. Y completá:

**1. El SLI** — la métrica concreta que mide la experiencia del usuario.

> Mal: "uso de CPU del servidor"
> Bien: "porcentaje de requests al checkout que responden con éxito en menos de 500 ms"

**2. El SLO** — el objetivo que el equipo se compromete a cumplir.

> "El 99,5 % de las requests al checkout responde con éxito en menos de 500 ms, medido sobre 30 días."

**3. El error budget** — cuánto te podés permitir fallar.

> Con un SLO de 99,5 % mensual: 0,5 % de 30 días son **3 horas y 36 minutos** de degradación permitida al mes.

Para calcularlo: `(100 - SLO) / 100 × 43.200 minutos`  (un mes de 30 días)

Ejemplo con 99,9 %:  `0,001 × 43.200 = 43,2 minutos`

| SLO | Error budget mensual |
|---|---|
| 99 % | 7 h 12 min |
| 99,5 % | 3 h 36 min |
| 99,9 % | 43 min |
| 99,99 % | 4 min 19 s |

**4. Una alerta sobre un síntoma.** Escribila en pseudocódigo o en PromQL:

> "Alertar si menos del 99 % de las requests del checkout responde bien durante 10 minutos seguidos."

**5. La justificación**, en tres líneas: ¿por qué ese umbral y no otro? ¿Qué pasaría si lo subieras a 99,99 %?

> **Pista para la número 5:** cada nueve extra cuesta muchísimo más que el anterior. Pasar de 99 % a 99,9 % puede significar duplicar la infraestructura. La pregunta correcta no es "¿cuánta disponibilidad podemos lograr?" sino "¿cuánta necesita realmente el negocio?".

---

# Apagar todo

Cuando termines:

```bash
docker compose down
```

Si además querés borrar los datos guardados:

```bash
docker compose down -v
```

---

# Entrega

En tu repositorio, creá una carpeta `modulo-06/` con:

```
modulo-06/
├── app.py                     ← con tu métrica agregada
├── slo.md                     ← el ejercicio 4 completo
└── evidencias/
    ├── 01-dashboard-normal.png
    ├── 02-dashboard-errores.png
    ├── 03-panel-propio.png
    └── 04-alerta-firing.png    (opcional)
```

Y en `NOTAS.md`, una sección "Módulo 6" respondiendo:

1. ¿Por qué un counter siempre se consulta con `rate()` y nunca en crudo?
2. ¿Qué problema tendría etiquetar una métrica con el ID de usuario?
3. ¿Por qué el p95 dice más que el promedio?
4. ¿Por qué el campo `for` de una alerta es importante?
5. Una métrica te dice que el 3 % de los pagos falla. ¿Qué mirás después y por qué?

## Cómo se evalúa

| Criterio | Peso |
|---|---|
| Ejercicio 1 y 2: stack levantado, capturas con datos reales | 30 % |
| Ejercicio 3: métrica propia instrumentada y graficada | 25 % |
| Ejercicio 4: SLI, SLO, error budget y alerta bien planteados | 30 % |
| Las 5 preguntas de `NOTAS.md` | 15 % |

---

# ⚠️ Si algo no funciona

### `docker compose up` falla al construir la app

Mirá el error completo. Si dice algo de red o de `pip`, probá de nuevo: suele ser una descarga que se cortó.

### En `localhost:9090/targets`, `app-demo` aparece **DOWN**

1. Verificá que la app esté viva: `docker compose logs app`
2. El error `connection refused` acá casi siempre significa que la app crasheó al arrancar. Los logs te dicen por qué.
3. **No uses `localhost` en `prometheus.yml`:** adentro de la red de Docker, `localhost` es el propio contenedor de Prometheus. Por eso el target dice `app:8000`, usando el nombre del servicio.

### Grafana muestra "No data" en todos los paneles

1. ¿Generaste tráfico? Sin requests no hay métricas.
2. Verificá el rango de tiempo arriba a la derecha: tiene que ser "Last 15 minutes" o similar.
3. Verificá el datasource: **Connections → Data sources → Prometheus → Save & test**. Tiene que decir "Successfully queried".

### El puerto 3000 u 8000 está ocupado

Editá `docker-compose.yml` y cambiá el número de la izquierda:

```yaml
ports:
  - "3001:3000"     # ahora Grafana está en localhost:3001
```

### `./generar-trafico.sh: Permission denied`

```bash
chmod +x generar-trafico.sh
```

### Cambié `app.py` y no veo la métrica nueva

Hay que reconstruir la imagen, no solo reiniciar:

```bash
docker compose up -d --build app
```

### Cambié `prometheus.yml` y no toma los cambios

Ese sí solo necesita reinicio:

```bash
docker compose restart prometheus
```

---

## Si querés ir más lejos

- **Agregá node-exporter** al `docker-compose.yml` y armá un dashboard USE con las métricas del sistema operativo.
- **Probá Loki** (de los mismos creadores de Grafana) para sumar el pilar de logs al stack.
- **Probá Jaeger o Tempo** para sumar trazas y ver el pilar que falta.
- **Escribí tu propia alerta** en `alertas.yml` y hacela disparar a propósito.
- **Explorá PromQL** en `localhost:9090/graph`: probá `topk(3, rate(http_requests_total[5m]))` para ver las tres rutas más usadas.
