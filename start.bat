@echo off
title ScreenIt Launcher
echo ===================================================
echo   ScreenIt ^| AI Resume Screening Platform
echo ===================================================
echo.

:: Detect venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .\venv\
    echo         Run: python -m venv venv ^&^& venv\Scripts\pip install -r backend\requirements.txt
    pause
    exit /b 1
)

:: Start Backend FastAPI
echo [1/2] Starting FastAPI backend   ^>  http://localhost:8000
start "ScreenIt Backend" cmd /k "venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Give the backend a moment to bind
timeout /t 3 >nul

:: Start Frontend Vite dev server
echo [2/2] Starting React dev server  ^>  http://localhost:5173
cd apps\web
start "ScreenIt Client" cmd /k "npm run dev"
cd ..\..

echo.
echo ===================================================
echo   Both services are running.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo ===================================================
echo.
pause
