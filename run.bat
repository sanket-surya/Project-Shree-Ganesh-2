@echo off
title UAV Aero Digital Twin - Launcher
color 0E
cd /d "%~dp0"

echo ==============================================================================
echo    AERO PISTON ENGINE DIGITAL TWIN - MALE UAV (SIH 2026)
echo ==============================================================================
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [2/4] Checking Node.js / npm environment...
cmd /c npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [3/4] Launching FastAPI Backend (Port 8000)...
start "UAV Backend (Port 8000)" cmd /k "color 0A && cd /d "%~dp0" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [4/4] Launching React GCS Frontend (Port 5173)...
start "UAV Frontend (Port 5173)" cmd /k "color 0B && cd /d "%~dp0frontend" && cmd /c npm run dev"

echo.
echo Waiting 4 seconds for servers to initialize...
timeout /t 4 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo ==============================================================================
echo  SYSTEM RUNNING SUCCESSFULLY!
echo  - Frontend Dashboard : http://localhost:5173
echo  - Backend API & Docs : http://127.0.0.1:8000/docs
echo  - WebSocket Stream   : ws://127.0.0.1:8000/ws/telemetry
echo ==============================================================================
echo Both Backend and Frontend terminals have been started in separate windows.
echo To stop the system, close those terminal windows.
echo.
pause
