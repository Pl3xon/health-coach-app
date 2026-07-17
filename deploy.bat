@echo off
echo ========================================
echo    VitalCoach - Vercel + Render Deploy
echo ========================================
echo.
echo 1. Frontend (Vercel):
echo    - Oeffne https://vercel.com
echo    - Login mit GitHub/Google
echo    - "Add New Project"
echo    - Ordner: health-coach-app/frontend
echo    - Deploy
echo.
echo 2. Backend (Render):
echo    - Oeffne https://render.com
echo    - Login mit GitHub/Google
echo    - "New Web Service"
echo    - Ordner: health-coach-app/backend
echo    - Build: pip install -r requirements.txt
echo    - Start: gunicorn main:app
echo    - Deploy
echo.
echo 3. Backend URL in Frontend eintragen:
echo    - Vercel Dashboard -> Settings -> Environment Variables
echo    - VITE_API_URL = https://dein-backend.onrender.com
echo    - Neu deployen
echo.
echo 4. Handy: Frontend-URL oeffnen -> zum Homescreen hinzufuegen
echo.
pause
