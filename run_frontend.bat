@echo off
title UAV Digital Twin - React GCS Frontend (Port 5173)
color 0B
cd /d "%~dp0frontend"
echo ======================================================================
echo   AERO PISTON ENGINE DIGITAL TWIN - REACT GCS TACTICAL DASHBOARD
echo ======================================================================
echo Starting Vite Dev Server on http://localhost:5173 ...
echo ======================================================================
cmd /c npm run dev
pause
