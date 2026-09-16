"""
train_from_cpp.py — Hybrid C++ → Python ML Training Pipeline (SIH 2026)
==========================================================================
Reads physics simulation data streamed from C++ aero_twin_engine via stdin pipe
and trains 3 XGBoost models (Anomaly + Fault Classifier + RUL Regressor).

KEY INNOVATION: C++ runs physics at ~50,000 rows/sec (hardware speed).
Python ML trains on that real-time stream — no intermediate CSV needed.

Usage:
  # Option A: Pipe directly (fastest - no disk I/O)
  cd embedded/cpp
  ./cpp_data_exporter 10000 | python ../../ml_models/train_from_cpp.py

  # Option B: Save C++ output first, then train
  ./cpp_data_exporter 10000 > ../../ml_models/data/cpp_engine_data.csv
  python train_from_cpp.py --from-file ml_models/data/cpp_engine_data.csv

  # Option C: Full pipeline via retrain batch (Windows)
  retrain_ai.bat
"""

import sys
import os
import json
import time
import argparse
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

# ── Feature columns (matches C++ CSV header) ─────────────────────────────────
FEATURE_COLS = [
    "engine_code",                                              # NEW: engine identity
    "rpm", "manifold_pressure_hpa", "power_output_kw", "torque_nm",
    "fuel_flow_lph", "fuel_pressure_bar",
    "cht_cyl_1", "cht_cyl_2", "cht_cyl_3", "cht_cyl_4",
    "egt_cyl_1", "egt_cyl_2", "egt_cyl_3", "egt_cyl_4",
    "oil_temperature_c", "oil_pressure_bar", "coolant_temperature_c",
    "turbo_rpm", "vibration_g", "bus_voltage_v",
    "altitude_m", "ambient_temp_c", "throttle_pct",
    "ignition_timing_btdc", "injection_timing_btdc", "injection_pulse_width_ms",
    "lambda_afr", "combustion_efficiency_pct",
    # Physics-informed residual features (engine-agnostic deltas)
    "res_cht_spread", "res_egt_spread", "res_map_residual", "res_oil_press_residual",
]
RUL_FEATURE_COLS = FEATURE_COLS + ["engine_hours_used"]

FAULT_CLASSES = [
    "Nominal", "Cylinder_Misfire", "Turbo_Degradation", "Injector_Clogging",
    "Coolant_Loss", "Oil_Starvation", "Sensor_Drift", "Combustion_Knock", "Valve_Leakage"
]

ENGINE_NAMES = {0: "Rotax 914F3 Turbo", 1: "Austro AE300 Diesel", 2: "Lycoming IO-360"}

def load_data(source: str) -> pd.DataFrame:
    """Load data from stdin pipe or file."""
    t0 = time.time()
    if source == "stdin":
        print("[PIPE] Reading C++ physics stream from stdin...", flush=True)
        df = pd.read_csv(sys.stdin)
    else:
        print(f"[FILE] Loading from {source}...", flush=True)
        df = pd.read_csv(source)

    elapsed = time.time() - t0
    print(f"[DATA] Loaded {len(df):,} rows × {len(df.columns)} cols in {elapsed:.2f}s", flush=True)

    # Per-engine breakdown
    if "engine_code" in df.columns:
        for code, name in ENGINE_NAMES.items():
            n = len(df[df["engine_code"] == code])
            print(f"  → Engine {code} ({name}): {n:,} rows", flush=True)

    return df

def train_pipeline(df: pd.DataFrame):
    os.makedirs("ml_models/weights", exist_ok=True)
    os.makedirs("ml_models/data",    exist_ok=True)

    # Build label columns
    # Map fault_name string → integer code
    fault_map = {name: i for i, name in enumerate(FAULT_CLASSES)}
    if "fault_name" in df.columns:
        df["fault_code_int"] = df["fault_name"].map(fault_map).fillna(0).astype(int)
    else:
        df["fault_code_int"] = df["fault_code"].astype(int)

    X         = df[FEATURE_COLS]
    y_fault   = df["fault_code_int"]
    y_anomaly = df["is_anomaly"].astype(int)
    y_rul     = df["rul_hours"].clip(lower=0)

    # ── 1. Anomaly Detector (Isolation Forest on Nominal baseline) ────────────
    print("\n[AI-TRAIN 1/3] Training Anomaly Detector (Isolation Forest)...", flush=True)
    X_nominal = X[y_anomaly == 0]
    sample_n  = min(50000, len(X_nominal))
    X_sample  = X_nominal.sample(sample_n, random_state=42)
    anomaly_det = IsolationForest(n_estimators=120, contamination=0.01,
                                  random_state=42, n_jobs=-1)
    anomaly_det.fit(X_sample)
    joblib.dump(anomaly_det, "ml_models/weights/anomaly_detector.joblib")
    print(f"[✓] Anomaly Detector trained on {sample_n:,} nominal rows.", flush=True)

    # ── 2. Multi-Class Fault Classifier (XGBoost GPU) ─────────────────────────
    print("\n[AI-TRAIN 2/3] Training Multi-Class Fault Classifier (XGBoost)...", flush=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y_fault, test_size=0.2,
                                               random_state=42, stratify=y_fault)
    gpu_params = dict(n_estimators=200, max_depth=8, learning_rate=0.08,
                      tree_method="hist", device="cuda",
                      random_state=42, subsample=0.85, eval_metric="mlogloss")
    cpu_params = {**gpu_params, "device": "cpu", "n_jobs": -1}
    del cpu_params["device"]

    try:
        clf = xgb.XGBClassifier(**gpu_params)
        clf.fit(X_tr, y_tr)
        print("[GPU] Fault Classifier trained on CUDA GPU.", flush=True)
    except Exception as e:
        print(f"[CPU] GPU failed ({e}), falling back to CPU...", flush=True)
        clf = xgb.XGBClassifier(**cpu_params)
        clf.fit(X_tr, y_tr)

    acc = accuracy_score(y_te, clf.predict(X_te))
    print(f"[✓] Fault Classifier Accuracy: {acc*100:.2f}% on {len(X_te):,} test rows.", flush=True)
    joblib.dump(clf, "ml_models/weights/fault_classifier.joblib")

    # Per-engine accuracy breakdown
    print("[XAI] Per-Engine Classification Accuracy:", flush=True)
    for code, name in ENGINE_NAMES.items():
        mask = X_te["engine_code"] == code
        if mask.sum() > 0:
            acc_e = accuracy_score(y_te[mask], clf.predict(X_te[mask]))
            print(f"  → {name}: {acc_e*100:.2f}%", flush=True)

    # Top feature importances
    fi = dict(zip(FEATURE_COLS, clf.feature_importances_))
    top5 = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:5]
    print("[XAI] Top 5 features:", [f"{k}:{v:.3f}" for k, v in top5], flush=True)

    # ── 3. RUL Regressor (XGBoost GPU) ────────────────────────────────────────
    print("\n[AI-TRAIN 3/3] Training RUL Regressor (XGBoost)...", flush=True)
    rul_cols = [c for c in RUL_FEATURE_COLS if c in df.columns]
    X_rul = df[rul_cols]
    X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(X_rul, y_rul,
                                                        test_size=0.2, random_state=42)
    rul_gpu = dict(n_estimators=250, max_depth=6, learning_rate=0.06,
                   tree_method="hist", device="cuda", random_state=42, subsample=0.85)
    rul_cpu = {**rul_gpu, "n_jobs": -1}
    del rul_cpu["device"]

    try:
        reg = xgb.XGBRegressor(**rul_gpu)
        reg.fit(X_tr_r, y_tr_r)
        print("[GPU] RUL Regressor trained on CUDA GPU.", flush=True)
    except Exception as e:
        print(f"[CPU] GPU failed ({e}), falling back to CPU...", flush=True)
        reg = xgb.XGBRegressor(**rul_cpu)
        reg.fit(X_tr_r, y_tr_r)

    y_pred_r = reg.predict(X_te_r)
    rmse = np.sqrt(mean_squared_error(y_te_r, y_pred_r))
    r2   = r2_score(y_te_r, y_pred_r)
    print(f"[✓] RUL Regressor: RMSE={rmse:.2f} hrs | R²={r2:.4f}", flush=True)
    joblib.dump(reg, "ml_models/weights/rul_regressor.joblib")

    # ── 4. Save Metadata ───────────────────────────────────────────────────────
    metadata = {
        "model_version":        "4.0-CPP-Python-Hybrid-MultiEngine",
        "pipeline":             "C++ Physics Engine → stdout pipe → Python XGBoost",
        "engines_covered":      list(ENGINE_NAMES.values()),
        "feature_names":        FEATURE_COLS,
        "rul_feature_names":    rul_cols,
        "fault_classes":        FAULT_CLASSES,
        "training_samples":     len(df),
        "classification_accuracy": float(acc),
        "rul_rmse_hours":       float(rmse),
        "rul_r2_score":         float(r2),
        "hardware":             "C++ O3 Physics + XGBoost CUDA GPU",
        "feature_importances":  {k: float(v) for k, v in fi.items()},
    }
    with open("ml_models/weights/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "="*70, flush=True)
    print("[COMPLETE] All 3 models saved to ml_models/weights/", flush=True)
    print(f"  → Covers: Rotax 914F + Austro AE300 + Lycoming IO-360", flush=True)
    print(f"  → Fault accuracy: {acc*100:.2f}% | RUL RMSE: {rmse:.2f} hrs", flush=True)
    print("="*70, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroTwin C++→Python ML Trainer")
    parser.add_argument("--from-file", type=str, default=None,
                        help="Load CSV from file instead of stdin pipe")
    args = parser.parse_args()

    source = args.from_file if args.from_file else "stdin"
    df = load_data(source)
    train_pipeline(df)
