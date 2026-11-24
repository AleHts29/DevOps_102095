FROM python:3.12-slim

WORKDIR /app

# Instalamos dependencias primero: así Docker cachea esta capa
# y no reinstala todo cada vez que cambiás app.py
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
