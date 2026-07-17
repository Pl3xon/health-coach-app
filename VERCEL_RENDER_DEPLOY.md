# Vercel + Render Deploy Guide

## Voraussetzungen
- GitHub Konto (für einfachen Deploy)
- Oder direkt per Drag & Drop

---

## Schritt 1: Code auf GitHub hochladen

```bash
cd "C:\Users\Kevin\Documents\Default Project\health-coach-app"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/DEINUSERNAME/health-coach-app.git
git push -u origin main
```

---

## Schritt 2: Backend auf Render deployen

1. Öffne https://render.com
2. Mit GitHub einloggen
3. **New** → **Web Service**
4. Dein Repository auswählen
5. Einstellungen:
   - **Name:** vitalcoach-api
   - **Region:** Frankfurt (eu-central)
   - **Branch:** main
   - **Runtime:** Python
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && gunicorn main:app --bind 0.0.0.0:$PORT`
6. **Environment Variables** hinzufügen:

| Key | Value |
|-----|-------|
| `GOOGLE_CLIENT_ID` | `679517015378-755hdb8b3o8suaomc62eh1hd59f1griq.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | `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` |
| `GEMINI_API_KEY` | `AQ.Ab8RN6JW1HBsWGbfvdEUsNG5wUThPkiucEhreUvsGvL312DX7w` |
| `RENPHO_EMAIL` | `saynofairplay@gmx.de` |
| `RENPHO_PASSWORD` | `Pokemon190696!` |

7. **Create Web Service** klicken
8. Warten bis Deploy fertig ist (2-3 Min)
9. **URL kopieren** (z.B. `https://vitalcoach-api.onrender.com`)

---

## Schritt 3: Frontend auf Vercel deployen

1. Öffne https://vercel.com
2. Mit GitHub einloggen
3. **Add New...** → **Project**
4. Dein Repository auswählen
5. Einstellungen:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
6. **Environment Variables** hinzufügen:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://vitalcoach-api.onrender.com` |

7. **Deploy** klicken
8. Warten bis Deploy fertig ist (1-2 Min)
9. **URL kopieren** (z.B. `https://health-coach-app.vercel.app`)

---

## Schritt 4: App auf dem Handy nutzen

1. Öffne die Vercel-URL im Handy-Browser
2. **Zum Home-Bildschirm hinzufügen:**
   - **iOS:** Teilen-Button → "Zum Home-Bildschirm"
   - **Android:** Drei Punkte → "Zum Startbildschirm hinzufügen"
3. Fertig! Die App läuft unabhängig vom PC

---

## Kosten

| Service | Free Tier | Geschätzt |
|---------|-----------|-----------|
| Vercel | 100 GB Bandbreite/Monat | Kostenlos |
| Render | 750 Stunden/Monat | Kostenlos |
| **Gesamt** | | **Kostenlos** |

---

## Achtung

- Render spinnt nach 15 Min Inaktivitätrunter (Free Tier)
- Beim ersten Aufruf dauert es ~30 Sekunden
- Danach läuft es normal
