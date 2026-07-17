FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Frontend bauen
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*
COPY frontend/package.json frontend/package-lock.json* frontend/
RUN cd frontend && npm install && npm run build

# Frontend in static Ordner kopieren
RUN mkdir -p /app/static && cp -r frontend/dist/* /app/static/

COPY backend/ .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
