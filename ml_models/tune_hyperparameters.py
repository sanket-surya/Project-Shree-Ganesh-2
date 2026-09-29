"""
tune_hyperparameters.py
=============================================================================
AeroTwin - NVIDIA RTX 5050 GPU Hyperparameter Tuning Pipeline
Project: MALE UAV Aero Engine Digital Twin (SIH 2026 / DRDO)

Performs Systematic Grid & Randomized Search on CUDA GPU:
  - Multi-Class Fault Classifier (Stratified K-Fold CV)
  - Remaining Useful Life (RUL) Regressor (K-Fold CV)

Hardware Target:
  - NVIDIA GeForce RTX 5050 Laptop GPU (CUDA acceleration)
  - PowerShell / CMD Execution
=============================================================================
"""

import os
import sys
import json
import time
import argparse
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, KFold, train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

FEATURE_COLS = [
    "rpm", "manifold_pressure_hpa", "power_output_kw", "torque_nm", 
    "fuel_flow_lph", "fuel_pressure_bar",
    "cht_cyl_1", "cht_cyl_2", "cht_cyl_3", "cht_cyl_4",
    "egt_cyl_1", "egt_cyl_2", "egt_cyl_3", "egt_cyl_4",
    "oil_temperature_c", "oil_pressure_bar", "coolant_temperature_c",
    "turbo_rpm", "vibration_g", "bus_voltage_v",
    "altitude_m", "ambient_temp_c", "throttle_pct",
    "ignition_timing_btdc", "injection_timing_btdc", "injection_pulse_width_ms",
    "lambda_afr", "combustion_efficiency_pct",
    "res_cht_spread", "res_egt_spread", "res_map_residual", "res_oil_press_residual"
]

RUL_FEATURE_COLS = FEATURE_COLS + ["engine_hours_used"]

ENGINE_DIRS = {
    "ROTAX_914F":    {"name": "Rotax 914F3 Turbo Boxer",         "folder": "rotax_914f"},
    "AUSTRO_AE300":  {"name": "Austro Engine AE300 Heavy Fuel",  "folder": "austro_ae300"},
    "LYCOMING_IO360":{"name": "Lycoming IO-360-M1A Flat-4",      "folder": "lycoming_io360"},
}

FAULT_CLASSES = [
    "Nominal", "Cylinder_Misfire", "Turbo_Degradation", "Injector_Clogging",
    "Coolant_Loss", "Oil_Starvation", "Sensor_Drift", "Combustion_Knock", "Valve_Leakage"
]

# Hyperparameter search grid
CLASSIFIER_GRID = [
    {"max_depth": 6, "learning_rate": 0.10, "n_estimators": 150, "subsample": 0.85, "colsample_bytree": 0.9},
    {"max_depth": 8, "learning_rate": 0.08, "n_estimators": 200, "subsample": 0.85, "colsample_bytree": 0.9},
    {"max_depth": 8, "learning_rate": 0.05, "n_estimators": 250, "subsample": 0.90, "colsample_bytree": 0.85},
    {"max_depth": 10, "learning_rate": 0.04, "n_estimators": 220, "subsample": 0.90, "colsample_bytree": 0.80},
    {"max_depth": 10, "learning_rate": 0.06, "n_estimators": 280, "subsample": 0.95, "colsample_bytree": 0.90},
]

REGRESSOR_GRID = [
    {"max_depth": 5, "learning_rate": 0.08, "n_estimators": 180, "subsample": 0.85},
    {"max_depth": 6, "learning_rate": 0.06, "n_estimators": 220, "subsample": 0.85},
    {"max_depth": 7, "learning_rate": 0.05, "n_estimators": 260, "subsample": 0.90},
    {"max_depth": 8, "learning_rate": 0.04, "n_estimators": 300, "subsample": 0.90},
]


def tune_engine(engine_id: str, sample_size: int = 200_000, cv_folds: int = 3):
    info = ENGINE_DIRS[engine_id]
    data_path = f"ml_models/data/{info['folder']}/telemetry.csv"
    weights_dir = f"ml_models/weights/{info['folder']}"
    os.makedirs(weights_dir, exist_ok=True)

    print("\n" + "="*75, flush=True)
    print(f"  GPU HYPERPARAMETER TUNING: {info['name']}", flush=True)
    print(f"  Target Engine : {engine_id}", flush=True)
    print(f"  Data Source   : {data_path}", flush=True)
    print(f"  CV Folds      : {cv_folds}-Fold Cross-Validation", flush=True)
    print(f"  Hardware      : NVIDIA GeForce RTX 5050 (device='cuda')", flush=True)
    print("="*75 + "\n", flush=True)

    if not os.path.exists(data_path):
        fallback = "ml_models/data/aero_engine_telemetry.csv"
        if os.path.exists(fallback):
            data_path = fallback
        else:
            print(f"[ERROR] Data not found at {data_path}", flush=True)
            return

    t0 = time.time()
    file_size_mb = os.path.getsize(data_path) / (1024 * 1024)
    target_sample = sample_size if (sample_size and sample_size > 0) else None

    if target_sample and file_size_mb > 400:
        print(f"   [STREAMING] Large dataset detected ({file_size_mb:.1f} MB). Streaming balanced sample of {target_sample:,} rows...", flush=True)
        per_class_target = max(500, target_sample // 9)
        class_counts = {i: 0 for i in range(9)}
        collected = []
        for chunk in pd.read_csv(data_path, chunksize=200_000):
            for code in range(9):
                needed = per_class_target - class_counts[code]
                if needed > 0:
                    matching = chunk[chunk["fault_code"] == code]
                    if len(matching) > 0:
                        take = matching.head(needed)
                        collected.append(take)
                        class_counts[code] += len(take)
            if all(c >= per_class_target for c in class_counts.values()):
                break
        df = pd.concat(collected, ignore_index=True)
    else:
        df = pd.read_csv(data_path)
        if target_sample and target_sample < len(df):
            _, df = train_test_split(df, test_size=target_sample, stratify=df["fault_code"], random_state=42)
            df = df.reset_index(drop=True)

    print(f"[OK] Loaded {len(df):,} records in {time.time()-t0:.2f}s ({df['fault_code'].nunique()} fault classes).", flush=True)

    avail_features = [c for c in FEATURE_COLS if c in df.columns]
    X = df[avail_features]
    y_fault = df["fault_code"]
    y_rul = df["rul_hours"]

    # ── PART 1: TUNE FAULT CLASSIFIER ──────────────────────────────────────────
    print(f"\n[PART 1/2] Tuning 9-Class Fault Diagnostic Classifier ({len(CLASSIFIER_GRID)} Candidate Architectures)...", flush=True)
    print("-" * 75, flush=True)
    print(f"  {'Trial':<7} {'Depth':<7} {'LR':<7} {'Trees':<7} {'Subsample':<11} {'Colsample':<11} {'Val Acc':<10} {'Time':<6}", flush=True)
    print("-" * 75, flush=True)

    best_clf_score = -1.0
    best_clf_params = None
    best_clf_model = None

    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)

    for idx, params in enumerate(CLASSIFIER_GRID, 1):
        t_start = time.time()
        fold_scores = []

        for train_idx, val_idx in skf.split(X, y_fault):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y_fault.iloc[train_idx], y_fault.iloc[val_idx]

            model = xgb.XGBClassifier(
                max_depth=params["max_depth"],
                learning_rate=params["learning_rate"],
                n_estimators=params["n_estimators"],
                subsample=params["subsample"],
                colsample_bytree=params["colsample_bytree"],
                tree_method="hist",
                device="cuda",
                random_state=42,
                eval_metric="mlogloss"
            )
            model.fit(X_tr, y_tr)
            preds = model.predict(X_val)
            fold_scores.append(accuracy_score(y_val, preds))

        mean_acc = np.mean(fold_scores)
        t_elapsed = time.time() - t_start

        star = " *" if mean_acc > best_clf_score else ""
        print(f"  #{idx:<5} {params['max_depth']:<7} {params['learning_rate']:<7} {params['n_estimators']:<7} {params['subsample']:<11} {params['colsample_bytree']:<11} {mean_acc*100:6.4f}%{star:<3} {t_elapsed:4.1f}s", flush=True)

        if mean_acc > best_clf_score:
            best_clf_score = mean_acc
            best_clf_params = params
            best_clf_model = model

    print("-" * 75, flush=True)
    print(f"  [BEST CLASSIFIER] Accuracy: {best_clf_score*100:.4f}% | Config: {best_clf_params}", flush=True)

    # ── PART 2: TUNE RUL PROGNOSTICS REGRESSOR ─────────────────────────────────
    print(f"\n[PART 2/2] Tuning Remaining Useful Life (RUL) Regressor ({len(REGRESSOR_GRID)} Candidate Architectures)...", flush=True)
    print("-" * 75, flush=True)
    print(f"  {'Trial':<7} {'Depth':<7} {'LR':<7} {'Trees':<7} {'Subsample':<11} {'R2 Score':<10} {'RMSE (hrs)':<12} {'Time':<6}", flush=True)
    print("-" * 75, flush=True)

    rul_cols = [c for c in RUL_FEATURE_COLS if c in df.columns]
    X_rul = df[rul_cols]

    best_rul_r2 = -999.0
    best_rul_rmse = 9999.0
    best_rul_params = None
    best_rul_model = None

    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)

    for idx, params in enumerate(REGRESSOR_GRID, 1):
        t_start = time.time()
        r2_scores = []
        rmse_scores = []

        for train_idx, val_idx in kf.split(X_rul):
            X_tr, X_val = X_rul.iloc[train_idx], X_rul.iloc[val_idx]
            y_tr, y_val = y_rul.iloc[train_idx], y_rul.iloc[val_idx]

            reg = xgb.XGBRegressor(
                max_depth=params["max_depth"],
                learning_rate=params["learning_rate"],
                n_estimators=params["n_estimators"],
                subsample=params["subsample"],
                tree_method="hist",
                device="cuda",
                random_state=42
            )
            reg.fit(X_tr, y_tr)
            preds = reg.predict(X_val)
            r2_scores.append(r2_score(y_val, preds))
            rmse_scores.append(np.sqrt(mean_squared_error(y_val, preds)))

        mean_r2 = np.mean(r2_scores)
        mean_rmse = np.mean(rmse_scores)
        t_elapsed = time.time() - t_start

        star = " *" if mean_r2 > best_rul_r2 else ""
        print(f"  #{idx:<5} {params['max_depth']:<7} {params['learning_rate']:<7} {params['n_estimators']:<7} {params['subsample']:<11} {mean_r2:7.5f}{star:<3} {mean_rmse:8.2f} hrs  {t_elapsed:4.1f}s", flush=True)

        if mean_r2 > best_rul_r2:
            best_rul_r2 = mean_r2
            best_rul_rmse = mean_rmse
            best_rul_params = params
            best_rul_model = reg

    print("-" * 75, flush=True)
    print(f"  [BEST RUL REGRESSOR] R2 Score: {best_rul_r2:.5f} | RMSE: {best_rul_rmse:.2f} hrs | Config: {best_rul_params}", flush=True)

    # ── PART 3: RETRAIN ON FULL SAMPLE WITH OPTIMAL HYPERPARAMETERS ───────────
    print("\n[OPTIMAL FIT] Retraining Final Models with Discovered Best Hyperparameters on NVIDIA RTX 5050...", flush=True)
    
    # 1. Final Classifier
    final_clf = xgb.XGBClassifier(
        **best_clf_params,
        tree_method="hist",
        device="cuda",
        random_state=42,
        eval_metric="mlogloss"
    )
    final_clf.fit(X, y_fault)
    clf_path = f"{weights_dir}/fault_classifier.joblib"
    joblib.dump(final_clf, clf_path)
    print(f"  [OK] Saved Optimal Fault Classifier -> {clf_path}", flush=True)

    # 2. Final RUL Regressor
    final_rul = xgb.XGBRegressor(
        **best_rul_params,
        tree_method="hist",
        device="cuda",
        random_state=42
    )
    final_rul.fit(X_rul, y_rul)
    rul_path = f"{weights_dir}/rul_regressor.joblib"
    joblib.dump(final_rul, rul_path)
    print(f"  [OK] Saved Optimal RUL Regressor -> {rul_path}", flush=True)

    # 3. Save Tuned Hyperparameters & Performance Card
    tuning_card = {
        "engine_id": engine_id,
        "engine_name": info["name"],
        "tuning_date": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hardware": "NVIDIA GeForce RTX 5050 (CUDA Hist)",
        "cv_folds": cv_folds,
        "samples_evaluated": len(df),
        "fault_classifier": {
            "best_accuracy": float(best_clf_score),
            "optimal_hyperparameters": best_clf_params,
            "feature_attributions": {
                feat: float(imp) for feat, imp in zip(avail_features, final_clf.feature_importances_)
            }
        },
        "rul_regressor": {
            "best_r2_score": float(best_rul_r2),
            "best_rmse_hours": float(best_rul_rmse),
            "optimal_hyperparameters": best_rul_params
        }
    }

    card_path = f"{weights_dir}/tuned_hyperparameters.json"
    with open(card_path, "w") as f:
        json.dump(tuning_card, f, indent=2)
    print(f"  [OK] Hyperparameter Tuning Report Saved -> {card_path}", flush=True)

    # Sync to default weights if primary engine
    if engine_id == "ROTAX_914F":
        joblib.dump(final_clf, "ml_models/weights/fault_classifier.joblib")
        joblib.dump(final_rul, "ml_models/weights/rul_regressor.joblib")
        with open("ml_models/weights/tuned_hyperparameters.json", "w") as f:
            json.dump(tuning_card, f, indent=2)

    total_tuning_time = time.time() - t0
    print("\n" + "="*75, flush=True)
    print(f"  TUNING FINISHED for {info['name']} in {total_tuning_time:.1f}s!", flush=True)
    print(f"  Final Validated Accuracy : {best_clf_score*100:.4f}%", flush=True)
    print(f"  Final Validated R2 Score : {best_rul_r2:.5f} (RMSE: {best_rul_rmse:.2f} hrs)", flush=True)
    print("="*75 + "\n", flush=True)

    return tuning_card


def main():
    parser = argparse.ArgumentParser(description="AeroTwin GPU Hyperparameter Tuning")
    parser.add_argument("--engine", type=str, default="ROTAX_914F",
                        choices=["ALL", "ROTAX_914F", "AUSTRO_AE300", "LYCOMING_IO360"])
    parser.add_argument("--sample", type=int, default=100_000,
                        help="Sample rows for hyperparameter search (default: 100,000 for rapid GPU search)")
    parser.add_argument("--cv", type=int, default=3, help="Cross-validation folds (default: 3)")
    args = parser.parse_args()

    print("\n" + "#"*75, flush=True)
    print("  AEROTWIN GPU HYPERPARAMETER TUNING - NVIDIA RTX 5050", flush=True)
    print(f"  Target Engine : {args.engine}", flush=True)
    print(f"  Sample Size   : {args.sample:,}", flush=True)
    print(f"  CV Folds      : {args.cv}", flush=True)
    print("#"*75, flush=True)

    engines = [args.engine] if args.engine != "ALL" else list(ENGINE_DIRS.keys())
    for eid in engines:
        tune_engine(eid, sample_size=args.sample, cv_folds=args.cv)


if __name__ == "__main__":
    main()
