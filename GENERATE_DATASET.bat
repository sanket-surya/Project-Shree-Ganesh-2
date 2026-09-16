@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AeroTwin Physics Dataset Generator - SIH 2026
echo =======================================================================
echo   AeroTwin Physics-Verified Per-Engine Dataset Generator
echo   SIH 2026 / DRDO Tapas-BH-201 Digital Twin
echo =======================================================================
echo Working Directory: %CD%
echo.
echo Select Dataset Size to Generate:
echo   [1] 1 Million rows per engine  (~150 MB each, takes ~45 seconds total)
echo   [2] 5 Million rows per engine  (~750 MB each, takes ~3 minutes total)
echo   [3] 10 Million rows per engine (~1.5 GB each, takes ~6 minutes total)
echo   [4] 40 Million rows per engine (~6.0 GB each, takes ~25 minutes total)
echo.
set /p choice="Enter choice [1, 2, 3 or 4] (Default is 1): "

if "%choice%"=="2" (
    set ROWS=5000000
) else if "%choice%"=="3" (
    set ROWS=10000000
) else if "%choice%"=="4" (
    set ROWS=40000000
) else (
    set ROWS=1000000
)

echo.
echo [STARTING] Generating %ROWS% rows per engine for ALL 3 engines...
"C:\Users\Asus\AppData\Local\Programs\Python\Python312\python.exe" -u ml_models\dataset_generator_per_engine.py --engine ALL --rows %ROWS%
echo.
echo =======================================================================
echo   Generation Complete! Telemetry saved to ml_models\data\
echo =======================================================================
pause
