@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AeroTwin NVIDIA RTX 5050 GPU Training Pipeline
echo =======================================================================
echo   AeroTwin NVIDIA RTX 5050 GPU Training Pipeline (CUDA)
echo   SIH 2026 / DRDO Tapas-BH-201 Digital Twin
echo =======================================================================
echo Working Directory: %CD%
echo.
echo Target Hardware: NVIDIA GeForce RTX 5050 Laptop GPU
echo.
echo Select Training Mode:
echo   [1] Fast GPU Training (1,000,000 Sample - takes ~15 seconds per engine)
echo   [2] Deep GPU Training (5,000,000 Sample - takes ~1.5 minutes per engine)
echo   [3] Full Dataset GPU Training (Uses all rows in CSV)
echo.
set /p choice="Enter choice [1, 2 or 3] (Default is 1): "

if "%choice%"=="2" (
    set SAMPLE=5000000
) else if "%choice%"=="3" (
    set SAMPLE=0
) else (
    set SAMPLE=1000000
)

echo.
echo [STARTING] Training ML models on RTX 5050 GPU for ALL 3 engines...
"C:\Users\Asus\AppData\Local\Programs\Python\Python312\python.exe" -u ml_models\train_per_engine.py --engine ALL --sample %SAMPLE%
echo.
echo =======================================================================
echo   GPU Training Complete! Weights saved to ml_models\weights\
echo =======================================================================
pause
