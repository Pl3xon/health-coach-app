# VitalCoach - Gesundheits-Cockpit

Eine moderne Health & Fitness App mit KI-Coach, Renpho-Integration und Google Fit Sync.

## Features

- **Dashboard** - Übersicht aller Vitaldaten mit animated Charts
- **AI Coach** - Gemini-powered Chat mit Bild/Video-Empfehlungen  
- **Ernährungsplan** - Personalisiert basierend auf BMR & Zielen
- **Home Workouts** - Übungen mit Bildern & YouTube-Links
- **Vitaldaten** - Renpho & Google Fit Integration
- **Profil** - Persönliche Daten & Fitnessziele verwalten

## Quick Start

### Windows
```batch
start.bat
```

### Manuell

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Frontend:** React + Vite + TailwindCSS + Framer Motion
- **Backend:** Python FastAPI
- **AI:** Google Gemini API
- **Daten:** Renpho Health API + Google Fit REST API

## API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/profile` | GET/POST | Profil verwalten |
| `/api/chat` | POST | AI Coach Chat |
| `/api/renpho/status` | GET | Renpho Verbindung |
| `/api/renpho/measurements` | GET | Renpho Messdaten |
| `/api/google-fit/data` | GET | Google Fit Daten |
| `/api/nutrition/plan` | POST | Ernährungsplan erstellen |
| `/api/workout/plan` | POST | Workout-Plan erstellen |
| `/api/dashboard` | GET | Dashboard-Daten |

## Konfiguration

API Keys und Zugangsdaten werden in `backend/.env` gespeichert.

## Sicherheit

- Alle Zugangsdaten werden lokal gespeichert
- Keine Daten werden an Dritte weitergegeben
- Renpho API nutzt AES-Verschlüsselung
