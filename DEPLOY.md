# VitalCoach - Google Cloud Deploy Guide

## Voraussetzungen
1. Google Cloud CLI installieren: https://cloud.google.com/sdk/docs/install
2. Firebase CLI installieren: `npm install -g firebase-tools`
3. Google Cloud Projekt erstellen in der Console

## Schritt 1: Google Cloud Projekt erstellen

```bash
# Login bei Google Cloud
gcloud auth login

# Projekt erstellen (oder bestehendes verwenden)
gcloud config set project DEIN_PROJEKT_NAME

# APIs aktivieren
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## Schritt 2: Firestore erstellen

```bash
# Firestore in Native Mode erstellen
gcloud firestore databases create --location=europe-west1
```

Oder in der Google Cloud Console:
1. Firestore Database erstellen
2. Native Mode wählen
3. Region: europe-west1 (Frankfurt)

## Schritt 3: Backend deployen (Cloud Run)

```bash
cd backend

# Docker Image bauen und pushen
gcloud builds submit --tag gcr.io/DEIN_PROJEKT/vitalcoach-api

# Cloud Run Service erstellen
gcloud run deploy vitalcoach-api \
  --image gcr.io/DEIN_PROJEKT/vitalcoach-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLIENT_ID=679517015378-755hdb8b3o8suaomc62eh1hd59f1griq.apps.googleusercontent.com" \
  --set-env-vars="GOOGLE_CLIENT_SECRET=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" \
  --set-env-vars="GEMINI_API_KEY=AQ.Ab8RN6JW1HBsWGbfvdEUsNG5wUThPkiucEhreUvsGvL312DX7w" \
  --set-env-vars="RENPHO_EMAIL=saynofairplay@gmx.de" \
  --set-env-vars="RENPHO_PASSWORD=Pokemon190696!"
```

## Schritt 4: Frontend builden und deployen

```bash
cd frontend

# Dependencies installieren
npm install

# Build erstellen (mit korrekter API URL)
VITE_API_URL=https://vitalcoach-api-XXXXXX-ew.a.run.app npm run build

# Firebase inicialisieren und deployen
firebase login
firebase init  # Hosting auswählen, projectId auswählen
firebase deploy
```

## Schritt 5: App auf dem Handy nutzen

Nach dem Deploy:
1. Öffne `https://DEIN_PROJEKT.web.app` im Handy-Browser
2. App zum Home-Screen hinzufügen (iOS: Teilen → Zum Home-Bildschirm)
3. Fertig! Die App läuft unabhängig vom PC

## Kosten (Free Tier)

| Service | Free Tier | Geschätzt für dich |
|---------|-----------|-------------------|
| Cloud Run | 180K Sek/Monat | ~5€/Monat (10Mio) |
| Firestore | 1 GiB + 50K Reads/Tag | Kostenlos |
| Firebase Hosting | 10 GB + 360 MB/Tag | Kostenlos |
| **Gesamt** | | **Kostenlos bis ~5€/Monat** |

## Automatisches Update (Optional)

Für Renpho-Sync alle 6 Stunden:
```bash
gcloud scheduler jobs create http vitalcoach-renpho-sync \
  --schedule="0 */6 * * *" \
  --uri="https://vitalcoach-api-XXXXXX-ew.a.run.app/api/renpho/measurements" \
  --http-method=GET
```
