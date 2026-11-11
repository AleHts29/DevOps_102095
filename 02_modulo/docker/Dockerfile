# ─────────────────────────────────────────────────────────────
# Dockerfile — Módulo 1, práctica de Docker
#
# Un Dockerfile es la RECETA para construir una imagen.
# Cada instrucción de abajo crea una capa nueva sobre la anterior.
# ─────────────────────────────────────────────────────────────

# FROM: la imagen base sobre la que construimos.
# nginx es un servidor web; "alpine" es una variante mínima (~10 MB).
FROM nginx:alpine

# LABEL: metadatos de la imagen. No es obligatorio, pero es buena práctica.
LABEL autor="TU NOMBRE"
LABEL descripcion="Landing estática de la práctica del Módulo 1"

# COPY: copia archivos de tu máquina hacia adentro de la imagen.
# /usr/share/nginx/html es la carpeta que nginx publica por defecto.
COPY index.html /usr/share/nginx/html/
COPY style.css  /usr/share/nginx/html/

# EXPOSE: documenta qué puerto usa la aplicación adentro del contenedor.
# Es informativo: la publicación real se hace con -p en docker run.
EXPOSE 80

# CMD: el comando que se ejecuta cuando el contenedor arranca.
# "daemon off" mantiene nginx en primer plano; si el proceso principal
# termina, el contenedor se apaga.
CMD ["nginx", "-g", "daemon off;"]
