---
name: aerotwin-ml-train
description: >-
  AeroTwin SIH 2026 project साठी ML models train करण्याची complete procedure.
  Dataset generation, training pipeline, GPU acceleration, आणि weights save करण्याचे steps.
---

# AeroTwin ML Training Guide

## Project Location
```
C:\Users\Asus\Desktop\Project Shree Ganesh 2\
```

## ML Folder Structure
```
ml_models/
├── data/                    ← Training CSV (generate करावा लागतो)
│   └── aero_engine_telemetry.csv
├── weights/                 ← Trained model files (joblib)
│   ├── anomaly_detector.joblib
│   ├── fault_classifier.joblib
│   ├── rul_regressor.joblib
│   ├── model_metadata.json
│   └── tuned_hyperparameters.json
├── weights_backup/          ← Backup of previous weights
├── dataset_generator.py     ← Synthetic physics-based data generator
├── dataset_generator_per_engine.py ← Per-engine dataset generator
├── train_models.py          ← Main training script (XGBoost)
├── train_per_engine.py      ← Per-engine training
├── train_moe.py             ← MoE training (future)
├── tune_hyperparameters.py  ← Hyperparameter tuning
├── inference_engine.py      ← Real-time inference
└── streaming_loader.py      ← 110 GB real data loader
```

## Step 1: Generate Training Dataset
```bash
cd "C:\Users\Asus\Desktop\Project Shree Ganesh 2"
python ml_models/dataset_generator.py
```
- Generates `ml_models/data/aero_engine_telemetry.csv`
- ~1,000,000 records with 32 features + fault labels + RUL
- Physics-informed: 7 fault classes + Nominal

## Step 2: Train Models (Main)
```bash
cd "C:\Users\Asus\Desktop\Project Shree Ganesh 2"
python ml_models/train_models.py
```
- Trains 3 models: IsolationForest + XGBoost Classifier + XGBoost Regressor
- GPU (CUDA) → auto fallback to CPU if GPU unavailable
- Saves weights to `ml_models/weights/`
- Shows accuracy metrics at end

## Step 3: Per-Engine Training (Optional — Better accuracy)
```bash
python ml_models/train_per_engine.py
```
- Trains separate weights for: ROTAX_914F, AUSTRO_AE300, LYCOMING_IO360
- Saves to `ml_models/weights/rotax_914f/`, `austro_ae300/`, `lycoming_io360/`

## Step 4: Hyperparameter Tuning (Optional — Max accuracy)
```bash
python ml_models/tune_hyperparameters.py
```
- Uses Optuna for automatic hyperparameter search
- Saves best params to `ml_models/weights/tuned_hyperparameters.json`

## Step 5: Restart Backend (after training)
```bash
cd "C:\Users\Asus\Desktop\Project Shree Ganesh 2"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Fault Classes (7 + Nominal)
```python
FAULT_CLASSES = [
    "Nominal",
    "Cylinder_Misfire",
    "Oil_Starvation",
    "Coolant_Loss",
    "Turbo_Degradation",
    "Valve_Leakage",
    "Combustion_Knock",
    "Fuel_Contamination",
]
```

## 27 Features (MoE Architecture)
```
Performance (E1): rpm, power_output_kw, torque_nm, manifold_pressure_hpa, throttle_pct, combustion_efficiency_pct
Fault (E2):       cht_max, egt_max, res_cht_spread, res_egt_spread, vibration_g, lambda_afr
Health (E3):      oil_temperature_c, oil_pressure_bar, coolant_temperature_c, fuel_flow_lph
RUL (E4):         engine_hours_used, res_map_residual, res_oil_press_residual
Operating (E5):   altitude_m, ambient_temp_c, fuel_pressure_bar, bus_voltage_v
Cross-Engine (E6):turbo_rpm, injection_pulse_width_ms
Physics (E7):     ignition_timing_btdc, injection_timing_btdc
```

## Real Datasets Available
```
D:\AeroTwin_Datasets\unpacked\   ← 70+ folders, 386,000+ files
C:\AeroTwin_Paderborn\           ← 2,624 Paderborn .mat files
Key datasets:
- cwru-mat-full-dataset          ← CWRU Bearing (fault classification)
- nasa-bearing-dataset           ← NASA Bearing (RUL)
- MFPT                          ← MFPT Bearing
- hust-bearing                  ← HUST Bearing
- subf-v1, subf-v2              ← Sound-based fault data
- bispectrum-signal              ← 102,400 files (vibration)
- gearbox-fault-detection-dataset-phm-2009-nasa ← PHM Gearbox
- nasa-cmaps + cmapss-jet-engine ← CMAPSS (RUL prediction)
- drone-telemetry-tampering-dataset-v2 ← UAV telemetry
- SNU_Gearbox_code              ← SNU Gearbox
- XJTU-SY_Bearing_Datasets      ← XJTU Bearing
```

## Streaming Loader (110 GB Real Data)
```python
from ml_models.streaming_loader import AeroTwinStreamingLoader
loader = AeroTwinStreamingLoader()

# Load data for specific expert
df_e2 = loader.load_expert_dataset("E2_fault", max_rows=200000)

# Stream all datasets for expert
for chunk in loader.stream_all_for_expert("E1_performance"):
    # process chunk...
```

## MoE Architecture (7 Experts + Gating Router)
```
Created files:
- ml_models/moe_architecture.py  ← Router + 7 Experts definition
- ml_models/train_moe.py         ← MoE training on real 110 GB data (2.1M rows)
- ml_models/moe_inference.py     ← MoE real-time inference (<5ms latency)
```

### MoE Training Command:
```bash
python -X utf8 ml_models/train_moe.py
```
- Trains Gating Router (Softmax dynamic attention)
- Trains 7 GPU-accelerated domain experts (E1 to E7)
- Saves weights to `ml_models/weights/moe/`

## Current Model Performance (after training)
- Check `ml_models/weights/model_metadata.json` for latest metrics
- Expected: Classification Accuracy ~87-95%

## Important Notes
- Always run from project root: `C:\Users\Asus\Desktop\Project Shree Ganesh 2`
- Dataset generation takes ~5-10 min for 1M records
- Training takes ~15-30 min on CPU, ~5 min on GPU (RTX 5050)
- After training → restart backend to load new weights
- Backend runs on port 8000, Frontend on port 5173
