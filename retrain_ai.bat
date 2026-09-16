@echo off
title UAV Digital Twin - AI Model Retraining Pipeline
color 0E
cd /d "%~dp0"

echo ==============================================================================
echo   RE-GENERATING TELEMETRY DATASET & TRAINING DEFENSE AI/ML MODELS
echo ==============================================================================
echo [1/2] Generating physics telemetry dataset (Nominal + 8 Failure Modes)...
python ml_models/dataset_generator.py

echo.
echo [2/2] Training Isolation Forest, Random Forest Classifier, and RUL Regressor...
python ml_models/train_models.py

echo.
echo ==============================================================================
echo  AI/ML TRAINING COMPLETED SUCCESSFULLY! Weights saved to ml_models/weights/
echo ==============================================================================
pause
