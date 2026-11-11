# Práctica — Módulo 4: Kubernetes

**Formato:** dos actividades en grupo durante la sesión en vivo, más la tarea individual
**Necesitás:** un cluster de Kubernetes y `kubectl`. Nada más.

---

## ⚠️ Antes de la clase — hacé esto hoy, no mañana

Levantar un cluster puede llevar un rato la primera vez. Si llegás sin entorno, perdés las dos actividades.

### 1 · Instalar y arrancar

```bash
minikube start
```

Si no tenés Minikube: [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start)

> **Alternativas válidas:** `kind`, o el Kubernetes que trae Docker Desktop (Settings → Kubernetes → Enable). Cualquiera sirve.

### 2 · Habilitar los dos addons

**Esto tarda entre 1 y 2 minutos cada uno.** Hacelo antes, no durante la clase:

```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

### 3 · Verificar que todo esté listo

```bash
bash verificar.sh
```

Tenés que ver cinco `[OK]`. Si falta alguno, el script te dice qué hacer.

### 🆘 Si no lográs levantar nada

No te quedes afuera: **[Killercoda](https://killercoda.com/playgrounds/scenario/kubernetes)** te da un cluster real en el navegador, sin instalar nada y sin registrarte. Avisá en el chat así te ubicamos en un grupo que tenga entorno.

---

# Actividad 1 — Pod y Service

**20 minutos · En grupos de 3 o 4**

## Objetivo

Desplegar una aplicación con 3 réplicas y poder abrirla en el navegador.

## Dinámica

Una persona comparte pantalla y escribe; las demás dictan y buscan. **A los 10 minutos rotan.**

## Los pasos

### 1 · Completar los archivos

En `actividad-1/` hay dos archivos con huecos marcados `___`. Son cuatro en total, y **tres de ellos tienen que ser coherentes entre sí**.

```bash
cd actividad-1
```

Abrí `deployment.yaml` y `service.yaml` y completá los huecos. Los comentarios de cada archivo te dicen qué va en cada uno.

> **Pista:** las labels son el pegamento de Kubernetes. El selector del Deployment, las labels del template y el selector del Service tienen que apuntar todos a lo mismo. Si no coinciden, **no hay error**: simplemente no funciona.

### 2 · Aplicar

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### 3 · Verificar

```bash
kubectl get pods
```

Tenés que ver **3 pods en Running**:

```
NAME                   READY   STATUS    RESTARTS   AGE
web-7d9f8b6c5-x4k2m    1/1     Running   0          20s
web-7d9f8b6c5-t8m1q    1/1     Running   0          20s
web-7d9f8b6c5-p9j3n    1/1     Running   0          20s
```

```bash
kubectl get svc
```

El Service tiene que mostrar un puerto en el rango 30000-32767.

### 4 · Abrir la aplicación

```bash
minikube service web-svc
```

Se abre el navegador solo. **Ese es el objetivo de la actividad.**

### 5 · Romperla a propósito

Dejá esto corriendo en una terminal:

```bash
kubectl get pods --watch
```

Y en **otra terminal**, borrá un pod:

```bash
kubectl delete pod <nombre-de-un-pod>
```

Mirá la primera terminal. **Aparece un pod nuevo en pocos segundos.** Nadie se lo pidió: Kubernetes contó dos, vio que faltaba uno, y lo creó.

Eso es el estado deseado funcionando.

## ✅ Terminaste cuando

- [ ] `kubectl get pods` muestra 3 pods en Running
- [ ] `minikube service web-svc` abre la página en el navegador
- [ ] Al borrar un pod, aparece otro solo

## 🎁 Si te sobra tiempo

Agregá el ConfigMap de `actividad-2/configmap.yaml`, inyectalo como variables de entorno en el Deployment y verificalo:

```bash
kubectl apply -f ../actividad-2/configmap.yaml
# agregar al container del deployment:
#   envFrom:
#     - configMapRef: { name: web-config }
kubectl exec <un-pod> -- env | grep AMBIENTE
```

---

# Actividad 2 — Ingress y auto-escalado

**20 minutos · Mismos grupos · Sobre el despliegue de la actividad 1**

## ⚠️ Dos cosas sin las cuales esto no funciona

Las dos **fallan en silencio**, sin dar ningún error:

```bash
# 1. Los addons
minikube addons enable ingress
minikube addons enable metrics-server

# 2. El Deployment tiene que tener requests de CPU
#    (el deployment.yaml de la actividad 1 ya los trae)
kubectl get deploy web -o yaml | grep -A3 requests
```

## Parte A — Ingress

### 1 · Aplicar

```bash
cd ../actividad-2
kubectl apply -f ingress.yaml
```

### 2 · Verificar que tenga dirección

```bash
kubectl get ingress
```

```
NAME          CLASS   HOSTS          ADDRESS        PORTS   AGE
web-ingress   nginx   mi-app.local   192.168.49.2   80      30s
```

**La columna ADDRESS no puede estar vacía.** Si lo está, falta el Ingress Controller: volvé a habilitar el addon y esperá un minuto.

### 3 · Probarlo

El dominio `mi-app.local` no existe de verdad. En vez de editar tu archivo `hosts`, mandalo como cabecera:

```bash
curl -H "Host: mi-app.local" http://$(minikube ip)
```

Tiene que responder el HTML de nginx.

> **En Windows con PowerShell:**
> ```powershell
> curl.exe -H "Host: mi-app.local" http://$(minikube ip)
> ```

## Parte B — Auto-escalado

### 1 · Aplicar

```bash
kubectl apply -f hpa.yaml
```

### 2 · Verificar que lea métricas

```bash
kubectl get hpa
```

```
NAME      REFERENCE        TARGETS   MINPODS   MAXPODS   REPLICAS
web-hpa   Deployment/web   2%/50%    2         10        3
```

**La columna TARGETS tiene que mostrar un porcentaje.** Si dice `<unknown>`, hay dos causas posibles:

| Causa | Cómo verificar | Solución |
|---|---|---|
| Falta metrics-server | `kubectl top nodes` da error | `minikube addons enable metrics-server` y esperar 1-2 min |
| Faltan los requests | `kubectl get deploy web -o yaml \| grep requests` no devuelve nada | Agregar `resources.requests.cpu` al Deployment |

### 3 · Generar carga y ver escalar

En una terminal:

```bash
cd ..
bash generar-carga.sh
```

En **otra terminal**:

```bash
kubectl get hpa --watch
```

**Tené paciencia: el HPA tarda entre 1 y 2 minutos en reaccionar.** Vas a ver la columna REPLICAS subir de 3 a 4, a 5...

```
NAME      REFERENCE        TARGETS    REPLICAS
web-hpa   Deployment/web   2%/50%     3
web-hpa   Deployment/web   87%/50%    3
web-hpa   Deployment/web   87%/50%    6     ← escaló
```

Cuando cortes la carga con `Ctrl+C`, las réplicas **van a tardar varios minutos en bajar**. Es a propósito: subir es rápido, bajar es conservador, para no prender y apagar todo el tiempo.

## ✅ Terminaste cuando

- [ ] `kubectl get ingress` muestra una ADDRESS
- [ ] El `curl` con la cabecera Host responde
- [ ] `kubectl get hpa` muestra un porcentaje, no `<unknown>`
- [ ] Viste las réplicas subir con carga

---

# Tarea — Para la próxima clase

## Consigna 1 · Desplegar tu propia aplicación

Sobre el repositorio que venís armando:

- Usar **la imagen que construiste en el módulo 3**, no nginx
- Deployment con 3 réplicas, Service, Ingress y HPA
- Agregar **readiness y liveness probes** que funcionen de verdad
- Capturar el HPA escalando con carga real

> **Para que Minikube vea tu imagen local:**
> ```bash
> minikube image load mi-app:v1
> ```
> Y en el Deployment, agregá `imagePullPolicy: Never`.

### Las probes

```yaml
readinessProbe:
  httpGet:
    path: /          # o el endpoint de salud de tu app
    port: 8000
  initialDelaySeconds: 3
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /
    port: 8000
  initialDelaySeconds: 15   # margen generoso: si es muy corto, entra en bucle de reinicios
  periodSeconds: 10
```

## Consigna 2 · Probar la resiliencia

Esta es la más formativa de las dos.

### Con 3 réplicas

Dejá corriendo un bucle de tráfico:

```bash
while true; do curl -s -o /dev/null -w "%{http_code} " $URL; sleep 0.2; done
```

Y **mientras corre**, hacé un rolling update:

```bash
kubectl set image deploy/web web=mi-app:v2
```

Observá la salida del bucle. Anotá: **¿hubo alguna request fallida?**

### Con 1 réplica

Bajá a una sola réplica y repetí exactamente lo mismo:

```bash
kubectl scale deploy/web --replicas=1
# volvé a lanzar el bucle de curl
kubectl set image deploy/web web=mi-app:v1
```

**Comparalo con el caso anterior.** Esa diferencia es toda la lección del módulo.

---

# Entrega

```
modulo-04/
├── k8s/
│   ├── deployment.yaml      ← con probes y requests
│   ├── service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
├── NOTAS.md
└── evidencias/
    ├── 01-pods-running.png
    ├── 02-pod-reponiendose.png
    ├── 03-hpa-escalando.png
    └── 04-rolling-update.png
```

En `NOTAS.md`, sección "Módulo 4":

1. ¿Por qué un Deployment y no un Pod suelto?
2. ¿Cómo se conectan un Service y un Deployment, si en el YAML no se nombran entre sí?
3. ¿Qué pasó al hacer el rolling update con 3 réplicas? ¿Y con 1? **Pegá la salida del bucle de curl en los dos casos.**
4. ¿Qué diferencia hay entre readiness y liveness? ¿Qué pasa si la liveness es muy agresiva?
5. ¿Por qué el HPA necesita `requests` para funcionar?

## Cómo se evalúa

| Criterio | Peso |
|---|---|
| Deployment, Service, Ingress y HPA funcionando con tu propia imagen | 30 % |
| Probes configuradas y justificadas | 20 % |
| Consigna 2: la comparación 3 réplicas vs 1, con la evidencia pegada | 30 % |
| Las 5 preguntas de `NOTAS.md` | 20 % |

---

# Si algo no funciona

El comando que resuelve el 80 % de los problemas:

```bash
kubectl describe pod <nombre>
```

**Leé la sección `Events`, al final de la salida.** Ahí está la respuesta casi siempre.

| Síntoma | Qué significa | Solución |
|---|---|---|
| `Pending` eterno | Ningún nodo tiene recursos libres | `minikube stop && minikube start --memory=4096` |
| `ImagePullBackOff` | No encuentra la imagen | Revisá nombre y tag. Si es local: `minikube image load mi-app:v1` + `imagePullPolicy: Never` |
| `CrashLoopBackOff` | La app arranca y se muere sola | `kubectl logs <pod>` te dice por qué |
| `OOMKilled` en describe | Se pasó del límite de memoria | Subí `resources.limits.memory` |
| No hay ningún pod | El selector no coincide con las labels del template | Compará los dos campos del Deployment |
| El Service no responde | Las labels del Service no coinciden con las de los pods | `kubectl get endpoints web-svc` — si está vacío, es esto |
| Ingress sin ADDRESS | Falta el controller | `minikube addons enable ingress` |
| HPA en `<unknown>` | Falta metrics-server o faltan requests | Ver la tabla de la actividad 2 |
| `error validating data` | Indentación con tabs | YAML **solo** acepta espacios |

---

# Si querés ir más lejos

- **Rolling update al detalle:** probá `kubectl rollout status deploy/web`, `kubectl rollout history deploy/web` y `kubectl rollout undo deploy/web` para volver atrás un despliegue.
- **Jugá con las estrategias:** configurá `maxSurge` y `maxUnavailable` en el Deployment y observá cómo cambia el comportamiento del rolling update.
- **Probá un PodDisruptionBudget** y después hacé `kubectl drain` del nodo para ver cómo protege el servicio.
- **Escalá por otra métrica:** el HPA puede escalar por memoria o por métricas personalizadas, no solo por CPU.
- **Explorá los Secrets:** creá uno, inyectalo como variable de entorno y después hacé `kubectl get secret <nombre> -o yaml` para ver que está en base64 y no cifrado.
