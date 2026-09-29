"""
Train Domain-Specific AI/ML Models for MALE UAV Aero Piston Digital Twin
1. Physics-Informed Anomaly Detector (Residuals + Isolation Forest)
2. Multi-Class Fault Diagnostic Classifier (NVIDIA GPU-Accelerated XGBoost)
3. Remaining Useful Life (RUL) Prognostics Regressor (NVIDIA GPU-Accelerated XGBoost)

Trained on 1,000,008 Rotax 914F Physics-Informed Aero Propulsion Telemetry Records
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

# Add directory to path
sys.path.append(os.path.dirname(__file__))
from dataset_generator import FAULT_CLASSES

FEATURE_COLS = [
    "rpm", "manifold_pressure_hpa", "power_output_kw", "torque_nm", 
    "fuel_flow_lph", "fuel_pressure_bar",
    "cht_cyl_1", "cht_cyl_2", "cht_cyl_3", "cht_cyl_4",
    "egt_cyl_1", "egt_cyl_2", "egt_cyl_3", "egt_cyl_4",
    "oil_temperature_c", "oil_pressure_bar", "coolant_temperature_c",
    "turbo_rpm", "vibration_g", "bus_voltage_v",
    "altitude_m", "ambient_temp_c", "throttle_pct",
    # FADEC Injection & Combustion parameters
    "ignition_timing_btdc", "injection_timing_btdc", "injection_pulse_width_ms",
    "lambda_afr", "combustion_efficiency_pct",
    # Physics-informed residual features
    "res_cht_spread", "res_egt_spread", "res_map_residual", "res_oil_press_residual"
]

# RUL training uses all features + engine age (most predictive for remaining life)
RUL_FEATURE_COLS = FEATURE_COLS + ["engine_hours_used"]

def train_all_models():
    os.makedirs("ml_models/weights", exist_ok=True)
    os.makedirs("ml_models/data", exist_ok=True)

    csv_path = "ml_models/data/aero_engine_telemetry.csv"
    print(f"[DATA] Loading 1,000,000+ telemetry dataset from {csv_path}...", flush=True)
    df = pd.read_csv(csv_path)
    print(f"[DATA] Successfully loaded {len(df):,} records with {len(df.columns)} columns.", flush=True)

    X = df[FEATURE_COLS]
    y_fault = df["fault_code"]
    y_anomaly = df["is_anomaly"]
    y_rul = df["rul_hours"]

    # 1. Train Anomaly Detection Model on Nominal (Healthy) Baseline
    print("[AI-TRAIN] Training Physics-Informed Anomaly Detector (Isolation Forest)...", flush=True)
    X_nominal = X[y_anomaly == 0]
    # Sample 35,000 nominal records for fast, robust envelope fitting
    if len(X_nominal) > 35000:
        X_nominal_sample = X_nominal.sample(35000, random_state=42)
    else:
        X_nominal_sample = X_nominal
    anomaly_detector = IsolationForest(
        n_estimators=100, 
        contamination=0.01, 
        random_state=42,
        n_jobs=-1
    )
    anomaly_detector.fit(X_nominal_sample)
    joblib.dump(anomaly_detector, "ml_models/weights/anomaly_detector.joblib")
    print("[AI-TRAIN] Anomaly Detector trained and saved.", flush=True)

    # 2. Train Multi-Class Fault Diagnostic Classifier using NVIDIA GPU (XGBoost)
    print("[AI-TRAIN] Training Multi-Class Fault Diagnostic Classifier (NVIDIA RTX GPU XGBoost)...", flush=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_fault, test_size=0.2, random_state=42, stratify=y_fault
    )
    
    # Check if GPU device is available
    try:
        fault_classifier = xgb.XGBClassifier(
            n_estimators=180,
            max_depth=8,
            learning_rate=0.08,
            tree_method="hist",
            device="cuda",
            random_state=42,
            subsample=0.85,
            eval_metric="mlogloss"
        )
        fault_classifier.fit(X_train, y_train)
        print("[GPU] Fitted Fault Classifier on NVIDIA RTX GPU (CUDA).", flush=True)
    except Exception as e:
        print(f"[GPU FALLBACK] CUDA fit failed ({e}), training on CPU...", flush=True)
        fault_classifier = xgb.XGBClassifier(
            n_estimators=180,
            max_depth=8,
            learning_rate=0.08,
            tree_method="hist",
            random_state=42,
            subsample=0.85,
            n_jobs=-1,
            eval_metric="mlogloss"
        )
        fault_classifier.fit(X_train, y_train)

    y_pred = fault_classifier.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[METRICS] Fault Diagnostic Classification Accuracy on 200,000 Test Records: {acc * 100:.2f}%", flush=True)
    joblib.dump(fault_classifier, "ml_models/weights/fault_classifier.joblib")

    # Feature importances for XAI
    feature_importances = dict(zip(FEATURE_COLS, fault_classifier.feature_importances_))
    sorted_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)
    print("[XAI] Top 5 Diagnostic Feature Attributions:", flush=True)
    for feat, imp in sorted_features[:5]:
        print(f"  - {feat}: {imp:.4f}", flush=True)

    # 3. Train Remaining Useful Life (RUL) Regressor using NVIDIA GPU (XGBoost)
    print("[AI-TRAIN] Training Remaining Useful Life (RUL) Regressor (NVIDIA RTX GPU XGBoost)...", flush=True)
    rul_cols = [c for c in RUL_FEATURE_COLS if c in df.columns]
    X_rul = df[rul_cols]
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X_rul, y_rul, test_size=0.2, random_state=42
    )

    try:
        rul_regressor = xgb.XGBRegressor(
            n_estimators=220,
            max_depth=6,
            learning_rate=0.06,
            tree_method="hist",
            device="cuda",
            random_state=42,
            subsample=0.85
        )
        rul_regressor.fit(X_train_r, y_train_r)
        print("[GPU] Fitted RUL Regressor on NVIDIA RTX GPU (CUDA).", flush=True)
    except Exception as e:
        print(f"[GPU FALLBACK] CUDA fit failed ({e}), training on CPU...", flush=True)
        rul_regressor = xgb.XGBRegressor(
            n_estimators=220,
            max_depth=6,
            learning_rate=0.06,
            tree_method="hist",
            random_state=42,
            subsample=0.85,
            n_jobs=-1
        )
        rul_regressor.fit(X_train_r, y_train_r)

    y_pred_r = rul_regressor.predict(X_test_r)
    rmse = np.sqrt(mean_squared_error(y_test_r, y_pred_r))
    r2 = r2_score(y_test_r, y_pred_r)
    print(f"[METRICS] RUL Predictor RMSE: {rmse:.2f} hrs | R^2 Score: {r2:.4f}", flush=True)
    joblib.dump(rul_regressor, "ml_models/weights/rul_regressor.joblib")

    # Save Metadata & Feature Schema
    metadata = {
        "model_version": "3.0-GPU-MillionRecord-Physics",
        "feature_names": FEATURE_COLS,
        "rul_feature_names": rul_cols,
        "fault_classes": FAULT_CLASSES,
        "training_samples": len(df),
        "samples_per_mode": len(df) // len(FAULT_CLASSES),
        "classification_accuracy": float(acc),
        "rul_rmse_hours": float(rmse),
        "rul_r2_score": float(r2),
        "hardware_accelerator": "NVIDIA GeForce RTX 5050 Laptop GPU (CUDA)",
        "feature_importances": {k: float(v) for k, v in feature_importances.items()}
    }
    with open("ml_models/weights/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("[COMPLETE] All AI/ML models trained on 1,000,000 records and saved to ml_models/weights/ successfully.", flush=True)

if __name__ == "__main__":
    train_all_models()
