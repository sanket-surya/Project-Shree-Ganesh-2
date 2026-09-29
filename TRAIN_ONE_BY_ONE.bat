@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AeroTwin - Sequential GPU Training (No OOM)
echo =======================================================================
echo   AeroTwin Sequential Training Pipeline (NVIDIA RTX 5050 GPU)
echo   SIH 2026 / DRDO Tapas-BH-201 Digital Twin
echo   Running Models One-by-One to Avoid Out-Of-Memory (OOM) Errors
echo =======================================================================
echo Working Directory: %CD%
echo.

echo [1/8] Training Gating Router...
python -X utf8 ml_models/train_moe.py --expert router
if errorlevel 1 echo [WARN] Router training warning

echo.
echo [2/8] Training E1 (Performance & Thermodynamics)...
python -X utf8 ml_models/train_moe.py --expert E1
if errorlevel 1 echo [WARN] E1 training warning

echo.
echo [3/8] Training E2 (High-Frequency Fault Classifier)...
python -X utf8 ml_models/train_moe.py --expert E2
if errorlevel 1 echo [WARN] E2 training warning

echo.
echo [4/8] Training E3 (Lubrication & Thermal Health Index)...
python -X utf8 ml_models/train_moe.py --expert E3
if errorlevel 1 echo [WARN] E3 training warning

echo.
echo [5/8] Training E4 (Remaining Useful Life - RUL Prognostics)...
python -X utf8 ml_models/train_moe.py --expert E4
if errorlevel 1 echo [WARN] E4 training warning

echo.
echo [6/8] Training E5 (Operating Regime & Flight Envelope)...
python -X utf8 ml_models/train_moe.py --expert E5
if errorlevel 1 echo [WARN] E5 training warning

echo.
echo [7/8] Training E6 (Cross-Engine Domain Invariants)...
python -X utf8 ml_models/train_moe.py --expert E6
if errorlevel 1 echo [WARN] E6 training warning

echo.
echo [8/8] Training E7 (First-Principles Physics Residuals)...
python -X utf8 ml_models/train_moe.py --expert E7
if errorlevel 1 echo [WARN] E7 training warning

echo.
echo =======================================================================
echo   All Experts Successfully Trained One-by-One on GPU!
echo   Weights saved to: ml_models\weights\moe\
echo =======================================================================
pause
