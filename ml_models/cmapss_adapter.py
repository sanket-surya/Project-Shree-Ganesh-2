"""
NASA CMAPSS Real Data Adapter for Rotax 914F Piston Engine Digital Twin
==========================================================================
Maps NASA CMAPSS turbofan engine sensor channels to equivalent Rotax 914F
piston engine parameters using physics-based scaling and domain adaptation.

CMAPSS Dataset: NASA Ames Prognostics Center of Excellence
Reference: Saxena et al., "Damage Propagation Modeling for Aircraft Engine
           Run-to-Failure Simulation" (ICSMA 2008)

Sensor Mapping Strategy:
  CMAPSS Turbofan → Rotax 914F Piston (Domain Analogy)
  -------------------------------------------------------
  Nf  (Fan Speed, RPM)          → rpm (scaled 0-5800)
  Nc  (Core Speed, RPM)         → turbo_rpm (scaled 0-145000)
  P30 (HPC Outlet Pressure)     → manifold_pressure_hpa (turbo boost)
  T30 (HPC Outlet Temperature)  → cht_c (cylinder head temperature proxy)
  T50 (LPT Outlet Temperature)  → egt_c (exhaust gas temperature proxy)
  phi (Fuel Flow / P30 ratio)   → lambda_afr (air-fuel ratio proxy)
  BPR (Bypass Ratio)            → combustion_efficiency_pct
  htBleed (Bleed Enthalpy)      → oil_temperature_c proxy
  epr (Engine Pressure Ratio)   → oil_pressure_bar proxy
  Ps30 (Static HPC Pressure)    → fuel_pressure_bar
"""

import numpy as np
import pandas as pd
import os

# CMAPSS column names
CMAPSS_COLS = [
    "unit_id", "cycle",
    "op_set_1", "op_set_2", "op_set_3",
    "s1",  "s2",  "s3",  "s4",  "s5",
    "s6",  "s7",  "s8",  "s9",  "s10",
    "s11", "s12", "s13", "s14", "s15",
    "s16", "s17", "s18", "s19", "s20", "s21"
]

# CMAPSS sensor index → physical quantity mapping
# Based on CMAPSS documentation (Saxena 2008)
# s2=T24, s3=T30, s4=T50, s7=P30, s8=Nf, s9=Nc, s11=Ps30,
# s12=phi, s13=NRf, s14=NRc, s15=BPR, s17=htBleed, s21=W32
SENSOR_MAP = {
    "fan_speed_pct":       "s8",   # Nf normalized
    "core_speed_pct":      "s9",   # Nc normalized
    "hpc_pressure":        "s7",   # P30 (psia)
    "hpc_temp":            "s3",   # T30 (°R)
    "exhaust_temp":        "s4",   # T50 (°R)
    "fuel_air_ratio":      "s12",  # phi
    "bypass_ratio":        "s15",  # BPR
    "bleed_enthalpy":      "s17",  # htBleed
    "static_pressure":     "s11",  # Ps30
    "lpc_temp":            "s2",   # T24 (°R) → ambient proxy
}


def rankine_to_celsius(rankine_val):
    """Convert Rankine to Celsius."""
    return (rankine_val - 491.67) * 5.0 / 9.0


def normalize_minmax(series, new_min, new_max):
    s_min, s_max = series.min(), series.max()
    if s_max == s_min:
        return pd.Series(np.full(len(series), (new_min + new_max) / 2))
    return ((series - s_min) / (s_max - s_min)) * (new_max - new_min) + new_min


def load_cmapss(data_dir="ml_models/data/cmapss", subsets=("FD001", "FD002")):
    """Load and concatenate CMAPSS train subsets."""
    dfs = []
    for subset in subsets:
        fpath = os.path.join(data_dir, f"train_{subset}.txt")
        if not os.path.exists(fpath):
            print(f"[CMAPSS] WARNING: {fpath} not found, skipping.")
            continue
        df = pd.read_csv(fpath, sep=r"\s+", header=None, names=CMAPSS_COLS)
        df["subset"] = subset
        # Compute RUL per unit (max cycle - current cycle)
        max_cycles = df.groupby("unit_id")["cycle"].max()
        df["rul_hours"] = df.apply(
            lambda row: float(max_cycles[row["unit_id"]] - row["cycle"]), axis=1
        )
        # Scale RUL from cycles → hours (CMAPSS cycles ≈ 1 flight hour each)
        # Cap at 1000 to match Rotax TBO
        df["rul_hours"] = df["rul_hours"].clip(0, 1000)
        dfs.append(df)
        print(f"[CMAPSS] Loaded {subset}: {len(df)} records, {df['unit_id'].nunique()} engines")
    return pd.concat(dfs, ignore_index=True)


def adapt_cmapss_to_rotax(df_cmapss):
    """
    Domain-adapt CMAPSS turbofan sensor channels to Rotax 914F piston engine
    feature space used by our ML pipeline.
    """
    out = pd.DataFrame()

    # ── RPM: Fan Speed → Engine RPM (Rotax range: 1400–5800 RPM) ──────────
    out["rpm"] = normalize_minmax(df_cmapss["s8"], 1400.0, 5800.0)

    # ── Manifold Pressure: P30 (HPC Pressure) → MAP hPa (850–1400 hPa) ───
    out["manifold_pressure_hpa"] = normalize_minmax(df_cmapss["s7"], 850.0, 1400.0)

    # ── Power Output: RPM * MAP proxy ─────────────────────────────────────
    out["power_output_kw"] = (out["manifold_pressure_hpa"] / 1013.25) * (out["rpm"] / 5800.0) * 84.5

    # ── Torque ─────────────────────────────────────────────────────────────
    out["torque_nm"] = out["power_output_kw"] * 9548.8 / out["rpm"].clip(lower=100)

    # ── Fuel Flow: derived from power + BSFC ──────────────────────────────
    out["fuel_flow_lph"] = out["power_output_kw"] * 0.285 / 0.72

    # ── Fuel Pressure: Static pressure proxy ──────────────────────────────
    out["fuel_pressure_bar"] = normalize_minmax(df_cmapss["s11"], 2.5, 3.5)

    # ── CHT per cylinder: T30 (HPC outlet °R → °C) proxy ─────────────────
    # CMAPSS T30 typically 1300–1600°R → scale to CHT 70–170°C
    cht_base = normalize_minmax(df_cmapss["s3"], 70.0, 165.0)
    noise = np.random.normal(0, 1.5, len(cht_base))
    out["cht_cyl_1"] = (cht_base * 0.98 + noise).clip(40, 170)
    out["cht_cyl_2"] = (cht_base * 0.99 + noise).clip(40, 170)
    out["cht_cyl_3"] = (cht_base * 1.03 + noise).clip(40, 170)
    out["cht_cyl_4"] = (cht_base * 1.02 + noise).clip(40, 170)

    # ── EGT per cylinder: T50 (LPT outlet °R → °C) proxy ─────────────────
    # CMAPSS T50 ~700–800°R → scale to EGT 700–950°C
    egt_base = normalize_minmax(df_cmapss["s4"], 700.0, 940.0)
    out["egt_cyl_1"] = (egt_base + np.random.normal(0, 5, len(egt_base))).clip(600, 950)
    out["egt_cyl_2"] = (egt_base + 5 + np.random.normal(0, 5, len(egt_base))).clip(600, 950)
    out["egt_cyl_3"] = (egt_base - 3 + np.random.normal(0, 5, len(egt_base))).clip(600, 950)
    out["egt_cyl_4"] = (egt_base + 2 + np.random.normal(0, 5, len(egt_base))).clip(600, 950)

    # ── Oil Temperature: bleed enthalpy proxy ────────────────────────────
    out["oil_temperature_c"] = normalize_minmax(df_cmapss["s17"], 70.0, 125.0)

    # ── Oil Pressure: EPR (Engine Pressure Ratio) proxy ──────────────────
    out["oil_pressure_bar"] = normalize_minmax(
        df_cmapss["s9"], 2.0, 5.0  # Core speed correlates with oil pump speed
    )

    # ── Coolant Temperature ───────────────────────────────────────────────
    out["coolant_temperature_c"] = out["oil_temperature_c"] * 0.92

    # ── Turbo RPM: Core speed → turbo RPM (0–145k) ───────────────────────
    out["turbo_rpm"] = normalize_minmax(df_cmapss["s9"], 80000.0, 145000.0)

    # ── Vibration: derived from degradation — increases as engine ages ────
    # Use (max_cycle - current_cycle) inverse as health proxy
    age_factor = 1.0 - (df_cmapss["rul_hours"] / df_cmapss["rul_hours"].max()).clip(0, 1)
    out["vibration_g"] = 0.8 + age_factor * 1.2 + np.random.normal(0, 0.05, len(age_factor))
    out["vibration_g"] = out["vibration_g"].clip(0.5, 3.5)

    # ── Bus Voltage: stays relatively stable ─────────────────────────────
    out["bus_voltage_v"] = 28.1 + np.random.normal(0, 0.1, len(df_cmapss))

    # ── Flight Parameters ─────────────────────────────────────────────────
    out["altitude_m"]     = normalize_minmax(df_cmapss["op_set_1"].abs(), 500, 7500)
    out["ambient_temp_c"] = 15.0 - (out["altitude_m"] * 0.0065)
    out["throttle_pct"]   = normalize_minmax(df_cmapss["op_set_2"].abs(), 40.0, 100.0)

    # ── Physics Residual Features ─────────────────────────────────────────
    out["res_cht_spread"]       = out[["cht_cyl_1","cht_cyl_2","cht_cyl_3","cht_cyl_4"]].max(axis=1) - \
                                   out[["cht_cyl_1","cht_cyl_2","cht_cyl_3","cht_cyl_4"]].min(axis=1)
    out["res_egt_spread"]       = out[["egt_cyl_1","egt_cyl_2","egt_cyl_3","egt_cyl_4"]].max(axis=1) - \
                                   out[["egt_cyl_1","egt_cyl_2","egt_cyl_3","egt_cyl_4"]].min(axis=1)
    expected_map                = 850 + (out["throttle_pct"] / 100.0) * 550
    out["res_map_residual"]     = out["manifold_pressure_hpa"] - expected_map
    expected_oil_press          = (out["rpm"] / 5000.0) * 4.0 * (1.0 - (out["oil_temperature_c"] - 80.0) * 0.003)
    out["res_oil_press_residual"] = out["oil_pressure_bar"] - expected_oil_press

    # ── RUL Label from CMAPSS ─────────────────────────────────────────────
    out["rul_hours"] = df_cmapss["rul_hours"].values

    # ── Fault Labels: CMAPSS has no fault type, mark as degradation-only ──
    # All CMAPSS data is "Nominal" class for fault classifier (engine degrading, not specific fault)
    # Use only for RUL and anomaly training
    out["fault_class"] = "Nominal"
    out["fault_code"]  = 0
    out["is_anomaly"]  = (df_cmapss["rul_hours"] < 50).astype(int)  # Near-EOL = anomaly

    out = out.round(3)
    return out


def build_hybrid_dataset(data_dir="ml_models/data"):
    """
    Build hybrid training dataset:
    - NASA CMAPSS real data → for RUL regressor + anomaly detector
    - Physics Twin synthetic data → for fault classifier (has fault labels)
    """
    print("=" * 60)
    print("  NASA CMAPSS HYBRID DATASET BUILDER")
    print("=" * 60)

    # 1. Load real CMAPSS data
    print("\n[STEP 1] Loading NASA CMAPSS real engine data...")
    df_cmapss_raw = load_cmapss(
        data_dir=os.path.join(data_dir, "cmapss"),
        subsets=("FD001", "FD002")
    )
    print(f"[CMAPSS] Total raw records: {len(df_cmapss_raw)}")

    # 2. Adapt to Rotax 914F feature space
    print("\n[STEP 2] Domain-adapting CMAPSS → Rotax 914F feature space...")
    df_cmapss_adapted = adapt_cmapss_to_rotax(df_cmapss_raw)
    print(f"[ADAPTED] Records: {len(df_cmapss_adapted)}, Features: {len(df_cmapss_adapted.columns)}")

    # 3. Load physics twin synthetic fault data
    print("\n[STEP 3] Loading physics-twin synthetic fault dataset...")
    synth_path = os.path.join(data_dir, "aero_engine_telemetry.csv")
    if os.path.exists(synth_path):
        df_synth = pd.read_csv(synth_path)
        print(f"[SYNTH] Records: {len(df_synth)}, Fault classes: {df_synth['fault_class'].nunique()}")
    else:
        print("[SYNTH] Not found — generating now...")
        import sys; sys.path.append(".")
        from ml_models.dataset_generator import generate_telemetry_dataset
        df_synth = generate_telemetry_dataset(num_samples_per_mode=2000)

    # 4. Merge: CMAPSS Nominal rows + Synth fault rows
    print("\n[STEP 4] Merging: CMAPSS (real degradation) + Physics (fault signatures)...")
    # Sample CMAPSS to balance with synthetic nominal count
    n_synth_nominal = (df_synth["fault_class"] == "Nominal").sum()
    df_cmapss_sampled = df_cmapss_adapted.sample(
        min(len(df_cmapss_adapted), n_synth_nominal * 2),
        random_state=42
    )
    df_hybrid = pd.concat([df_cmapss_sampled, df_synth], ignore_index=True)
    print(f"[HYBRID] Total records: {len(df_hybrid)}")
    print(f"[HYBRID] Fault distribution:\n{df_hybrid['fault_class'].value_counts()}")

    # Save hybrid dataset
    hybrid_path = os.path.join(data_dir, "hybrid_training_data.csv")
    df_hybrid.to_csv(hybrid_path, index=False)
    print(f"\n[SAVED] Hybrid dataset → {hybrid_path}")
    return df_hybrid, df_cmapss_adapted


if __name__ == "__main__":
    df_hybrid, df_cmapss = build_hybrid_dataset()
    print("\n✅ NASA CMAPSS + Physics Twin hybrid dataset ready!")
