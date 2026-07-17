FROM python:3.12-slim

WORKDIR /app

# Python Dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Node.js installieren für Frontend Build
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Frontend bauen
COPY frontend/ frontend/
RUN cd frontend && npm install && npm run build

# Frontend in static verschieben
RUN mkdir -p static && cp -r frontend/dist/* static/

# Backend Code kopieren
COPY backend/ .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
