# Deploy Guide

## Backend auf Render
1. https://render.com → New Web Service
2. Repository auswählen
3. Build: pip install -r backend/requirements.txt
4. Start: cd backend && gunicorn main:app --bind 0.0.0.0:$PORT
5. Environment Variables eintragen (API Keys)

## Frontend auf Vercel
1. https://vercel.com → Import Git Repository
2. Deploy klicken
3. Environment Variable: VITE_API_URL = https://vitalcoach-api.onrender.com
