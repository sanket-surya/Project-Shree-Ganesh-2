@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AeroTwin NVIDIA RTX 5050 GPU Hyperparameter Tuning
echo =======================================================================
echo   AeroTwin GPU Hyperparameter Tuning Pipeline
echo   Hardware Target: NVIDIA GeForce RTX 5050 Laptop GPU (CUDA)
echo =======================================================================
echo Working Directory: %CD%
echo.
echo Select Engine to Tune:
echo   [1] Rotax 914F3 Turbo Boxer (Primary Tapas UAV Engine)
echo   [2] Austro Engine AE300 Heavy Fuel Diesel
echo   [3] Lycoming IO-360-M1A Flat-4
echo   [4] ALL Engines Sequentially
echo.
set /p choice="Enter choice [1, 2, 3 or 4] (Default is 1): "

if "%choice%"=="2" (
    set ENG=AUSTRO_AE300
) else if "%choice%"=="3" (
    set ENG=LYCOMING_IO360
) else if "%choice%"=="4" (
    set ENG=ALL
) else (
    set ENG=ROTAX_914F
)

echo.
echo [STARTING] Tuning Hyperparameters on RTX 5050 GPU for: %ENG%...
"C:\Users\Asus\AppData\Local\Programs\Python\Python312\python.exe" -u ml_models\tune_hyperparameters.py --engine %ENG% --sample 100000 --cv 3
echo.
echo =======================================================================
echo   Tuning Complete! Best hyperparameters saved to ml_models\weights\
echo =======================================================================
pause
