@echo off
echo ========================================
echo    VitalCoach - Health & Fitness App
echo ========================================
echo.

:: Start Backend
echo [1/2] Starting Backend Server...
cd backend
start "VitalCoach Backend" cmd /k "pip install -r requirements.txt && python main.py"
cd ..

:: Start Frontend
echo [2/2] Starting Frontend...
cd frontend
start "VitalCoach Frontend" cmd /k "npm install && npm run dev"
cd ..

echo.
echo ========================================
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo ========================================
echo.
pause
