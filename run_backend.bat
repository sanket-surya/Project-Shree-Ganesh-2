@echo off
title UAV Digital Twin - FastAPI Backend (Port 8000)
color 0A
cd /d "%~dp0"
echo ======================================================================
echo   AERO PISTON ENGINE DIGITAL TWIN - FASTAPI & AI TELEMETRY BACKEND
echo ======================================================================
echo Starting FastAPI server on http://127.0.0.1:8000 ...
echo Telemetry WebSocket: ws://127.0.0.1:8000/ws/telemetry
echo REST API Docs:      http://127.0.0.1:8000/docs
echo ======================================================================
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
