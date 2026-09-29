@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AeroTwin - Complete Step-by-Step Training for ALL 7 Experts
echo =======================================================================
echo   AeroTwin Step-by-Step Progressive Training Pipeline
echo   Hardware Target: NVIDIA RTX 5050 Laptop GPU (CUDA)
echo   Independent Expert-by-Expert Execution (100%% Safe from OOM)
echo =======================================================================
echo.
echo Select Expert to Train:
echo   [1] E1 - Performance & Thermodynamics (NASA CMAPSS + Lycoming C172)
echo   [2] E2 - Fault Classification (CWRU, MFPT, XJTU, Paderborn Vibration)
echo   [3] E3 - Thermal & Lubrication Health (FEMTO, CWRU Wear Telemetry)
echo   [4] E4 - Remaining Useful Life RUL (NASA N-CMAPSS, FEMTO Degradation)
echo   [5] E5 - Flight Operating Regime & Envelope (Real Drone Telemetry)
echo   [6] E6 - Cross-Engine Transfer Invariants (Rotax, Austro, Lycoming)
echo   [7] E7 - First-Principles Physics Residuals (Thermodynamic Invariants)
echo   [8] Router - Update Gating Router (Connects all 7 to Main Brain)
echo   [9] Fine-Tune - Run GPU Hyperparameter Grid Search (Maximize Accuracy)
echo   [A] Train ALL 7 Experts Sequentially One-by-One (Automated Pipeline)
echo.
set /p choice="Enter choice [1 to 9, or A]: "

if "%choice%"=="1" (
    echo.
    echo [E1] Processing NASA CMAPSS + Lycoming data and training E1...
    python -X utf8 ml_models\prepare_expert_datasets.py --expert E1
    python -X utf8 ml_models\train_moe.py --expert E1
) else if "%choice%"=="2" (
    echo.
    echo [E2] Processing CWRU, MFPT, Paderborn vibration and training E2...
    python -X utf8 ml_models\prepare_expert_datasets.py --expert E2
    python -X utf8 ml_models\train_moe.py --expert E2
) else if "%choice%"=="3" (
    echo.
    echo [E3] Processing lubrication and wear telemetry and training E3...
    python -X utf8 ml_models\prepare_expert_datasets.py --expert E3
    python -X utf8 ml_models\train_moe.py --expert E3
) else if "%choice%"=="4" (
    echo.
    echo [E4] Processing NASA + FEMTO run-to-failure sequences and training E4...
    python -X utf8 ml_models\prepare_expert_datasets.py --expert E4
    python -X utf8 ml_models\train_moe.py --expert E4
) else if "%choice%"=="5" (
    echo.
    echo [E5] Processing Drone flight telemetry and training E5...
    python -X utf8 ml_models\prepare_expert_datasets.py --expert E5
    python -X utf8 ml_models\train_moe.py --expert E5
) else if "%choice%"=="6" (
    echo.
    echo [E6] Processing multi-propulsion cross-engine data and training E6...
    python -X utf8 ml_models\prepare_expert_datasets.py --expert E6
    python -X utf8 ml_models\train_moe.py --expert E6
) else if "%choice%"=="7" (
    echo.
    echo [E7] Processing physics residuals and training E7...
    python -X utf8 ml_models\prepare_expert_datasets.py --expert E7
    python -X utf8 ml_models\train_moe.py --expert E7
) else if "%choice%"=="8" (
    echo.
    echo [ROUTER] Training Softmax Gating Attention Router for Main Brain...
    python -X utf8 ml_models\train_moe.py --expert router
) else if "%choice%"=="9" (
    echo.
    echo [FINE-TUNE] Running 3-Fold Cross-Validation on RTX 5050 GPU...
    python -X utf8 ml_models\tune_hyperparameters.py --engine ROTAX_914F --sample 150000 --cv 3
) else if /i "%choice%"=="A" (
    echo.
    echo [ALL] Training all 7 Experts sequentially with memory cleanup between each...
    python -X utf8 ml_models\train_moe.py --expert E1
    python -X utf8 ml_models\train_moe.py --expert E2
    python -X utf8 ml_models\train_moe.py --expert E3
    python -X utf8 ml_models\train_moe.py --expert E4
    python -X utf8 ml_models\train_moe.py --expert E5
    python -X utf8 ml_models\train_moe.py --expert E6
    python -X utf8 ml_models\train_moe.py --expert E7
    python -X utf8 ml_models\train_moe.py --expert router
) else (
    echo Invalid selection.
)

echo.
echo =======================================================================
echo   Process Finished! All updated weights saved in ml_models\weights\moe\
echo =======================================================================
pause
