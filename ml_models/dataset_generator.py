"""
Aero Piston Engine Telemetry Dataset Generator for MALE UAV Digital Twin
Generates physically consistent telemetry based on Rotax 914F Turbocharged Aero Piston Engine.
Vectorized NumPy generator supporting 1,000,000+ defense-grade telemetry records.
Includes 8+ failure modes across diverse flight envelopes with complete FADEC features.
"""

import numpy as np
import pandas as pd
import os

FAULT_CLASSES = [
    "Nominal",
    "Cylinder_Misfire",
    "Turbo_Degradation",
    "Injector_Clogging",
    "Coolant_Loss",
    "Oil_Starvation",
    "Sensor_Drift",
    "Combustion_Knock",
    "Valve_Leakage"
]

def generate_telemetry_dataset(num_samples_per_mode=111112, random_seed=42):
    """
    High-speed vectorized generator for Rotax 914F Aero Engine Telemetry.
    Generates ~1,000,000 records across 9 distinct operational and failure regimes.
    """
    np.random.seed(random_seed)
    dfs = []
    total_target = num_samples_per_mode * len(FAULT_CLASSES)
    print(f"[DATASET] Generating {total_target:,} physics-informed records across {len(FAULT_CLASSES)} regimes...", flush=True)

    for fault_idx, fault_name in enumerate(FAULT_CLASSES):
        n = num_samples_per_mode

        # 1. Flight Envelope Sampling
        altitude_m = np.random.uniform(500, 7500, n)
        ambient_temp_c = 15.0 - (altitude_m * 0.0065) + np.random.uniform(-5, 10, n)
        ambient_press_hpa = 1013.25 * (1.0 - (0.0065 * altitude_m / 288.15)) ** 5.255
        airspeed_kts = np.random.uniform(70, 130, n)
        throttle_pct = np.random.uniform(40, 100, n)

        # 2. First-Principles Otto-Turbo Dynamics
        rpm = 1400.0 + (throttle_pct / 100.0) * (5800.0 - 1400.0) + np.random.normal(0, 15, n)
        boost_target = 1013.25 + (throttle_pct / 100.0) * (1400.0 - 1013.25)
        map_hpa = boost_target + np.random.normal(0, 10, n)
        power_kw = (map_hpa / 1013.25) * (rpm / 5800.0) * 84.5 + np.random.normal(0, 0.5, n)
        torque_nm = power_kw * 9548.8 / np.maximum(rpm, 100.0)
        fuel_flow_lph = (power_kw * 0.285 / 0.72) + np.random.normal(0, 0.3, n)
        fuel_press_bar = 3.0 + np.random.normal(0, 0.05, n)

        # 3. Thermal Simulation (Rotax 914F Boxer Cylinders)
        ram_cooling = (airspeed_kts / 100.0) * 12.0
        cht_base = 75.0 + (power_kw * 0.48) - ram_cooling + (ambient_temp_c * 0.25)
        cht_1 = cht_base * 0.98 + np.random.normal(0, 1.5, n)
        cht_2 = cht_base * 0.99 + np.random.normal(0, 1.5, n)
        cht_3 = cht_base * 1.03 + np.random.normal(0, 1.8, n)  # Rear cylinder
        cht_4 = cht_base * 1.02 + np.random.normal(0, 1.8, n)

        egt_base = 730.0 + (map_hpa * 0.10)
        egt_1 = egt_base + np.random.normal(0, 6, n)
        egt_2 = egt_base + 5.0 + np.random.normal(0, 6, n)
        egt_3 = egt_base - 3.0 + np.random.normal(0, 6, n)
        egt_4 = egt_base + 2.0 + np.random.normal(0, 6, n)

        oil_temp_c = 78.0 + (power_kw * 0.35) - (ram_cooling * 0.4) + np.random.normal(0, 1.2, n)
        oil_press_bar = (rpm / 5000.0) * 4.0 * (1.0 - (oil_temp_c - 80.0) * 0.003) + np.random.normal(0, 0.08, n)
        coolant_temp_c = oil_temp_c * 0.93 + np.random.normal(0, 1.0, n)
        turbo_rpm = (map_hpa / 1400.0) * 140000.0 + np.random.normal(0, 1000, n)
        vibration_g = 0.8 + (rpm / 5800.0) * 0.9 + np.random.normal(0, 0.05, n)
        bus_voltage_v = 28.1 + np.random.normal(0, 0.1, n)

        # 4. FADEC Telemetry Parameters (Physics-Based)
        optimal_timing = 18.0 + (rpm / 5800.0) * 14.0 - (map_hpa / 1400.0) * 6.0
        ignition_timing_btdc = optimal_timing + np.random.normal(0, 0.2, n)
        injection_timing_btdc = 4.0 + (throttle_pct / 100.0) * 8.0 + np.random.normal(0, 0.1, n)
        injection_pulse_width_ms = 1.5 + (fuel_flow_lph / 25.0) * 4.0 + np.random.normal(0, 0.05, n)
        lambda_afr = 1.08 - (throttle_pct / 100.0) * 0.10 + np.random.normal(0, 0.005, n)
        combustion_efficiency_pct = 96.0 - np.abs(lambda_afr - 1.0) * 15.0 - np.maximum(0.0, (vibration_g - 1.5) * 3.0)

        # 5. RUL Simulation — Physics-based Weibull degradation curve
        sim_hours_used = np.random.uniform(5, 950, n)
        tbo_hours = 1000.0
        rul_linear = np.maximum(5.0, tbo_hours - sim_hours_used)
        degradation_factor = 1.0 + 0.3 * (sim_hours_used / tbo_hours) ** 2
        rul_hours = np.maximum(5.0, rul_linear / degradation_factor + np.random.normal(0, 8, n))
        rul_hours = np.minimum(rul_hours, rul_linear)

        # 6. Apply Distinct Physics Fault Signatures
        severity = np.random.uniform(0.4, 1.0, n) if fault_idx > 0 else np.zeros(n)

        if fault_name == "Cylinder_Misfire":
            cht_3 -= 45.0 * severity
            egt_3 -= 180.0 * severity
            vibration_g += 2.2 * severity
            power_kw *= (1.0 - 0.22 * severity)
            rul_hours *= 0.4

        elif fault_name == "Turbo_Degradation":
            map_hpa -= 250.0 * severity
            turbo_rpm -= 35000.0 * severity
            egt_1 += 60.0 * severity
            egt_2 += 60.0 * severity
            egt_3 += 60.0 * severity
            egt_4 += 60.0 * severity
            rul_hours *= 0.5

        elif fault_name == "Injector_Clogging":
            egt_1 += 130.0 * severity
            cht_1 += 28.0 * severity
            injection_pulse_width_ms += 1.8 * severity
            lambda_afr = np.minimum(1.3, lambda_afr + 0.15 * severity)
            combustion_efficiency_pct -= 14.0 * severity
            rul_hours *= 0.6

        elif fault_name == "Coolant_Loss":
            cht_1 += 55.0 * severity
            cht_2 += 55.0 * severity
            cht_3 += 55.0 * severity
            cht_4 += 55.0 * severity
            coolant_temp_c += 38.0 * severity
            rul_hours *= 0.15

        elif fault_name == "Oil_Starvation":
            oil_press_bar = np.maximum(0.4, 0.5 + (1.0 - severity) * 1.0)
            oil_temp_c += 38.0 * severity
            vibration_g += 2.1 * severity
            rul_hours *= 0.1

        elif fault_name == "Sensor_Drift":
            cht_4 += 55.0 * severity

        elif fault_name == "Combustion_Knock":
            vibration_g += 1.8 * severity
            cht_1 += 22.0 * severity
            cht_2 += 22.0 * severity
            cht_3 += 22.0 * severity
            cht_4 += 22.0 * severity
            ignition_timing_btdc -= 8.0 * severity  # FADEC knock retard
            combustion_efficiency_pct -= 18.0 * severity
            rul_hours *= 0.35

        elif fault_name == "Valve_Leakage":
            egt_2 += 115.0 * severity
            power_kw *= (1.0 - 0.14 * severity)
            combustion_efficiency_pct -= 12.0 * severity
            rul_hours *= 0.45

        # 7. Compute Physics Residuals
        all_cht = np.stack([cht_1, cht_2, cht_3, cht_4], axis=0)
        all_egt = np.stack([egt_1, egt_2, egt_3, egt_4], axis=0)
        res_cht_spread = np.max(all_cht, axis=0) - np.min(all_cht, axis=0)
        res_egt_spread = np.max(all_egt, axis=0) - np.min(all_egt, axis=0)
        res_map_residual = map_hpa - boost_target
        expected_oil = (rpm / 5000.0) * 4.0 * (1.0 - (oil_temp_c - 80.0) * 0.003)
        res_oil_press_residual = oil_press_bar - expected_oil

        batch_df = pd.DataFrame({
            "rpm": np.round(rpm, 1),
            "manifold_pressure_hpa": np.round(map_hpa, 1),
            "power_output_kw": np.round(power_kw, 2),
            "torque_nm": np.round(torque_nm, 1),
            "fuel_flow_lph": np.round(fuel_flow_lph, 2),
            "fuel_pressure_bar": np.round(fuel_press_bar, 2),
            "cht_cyl_1": np.round(cht_1, 1),
            "cht_cyl_2": np.round(cht_2, 1),
            "cht_cyl_3": np.round(cht_3, 1),
            "cht_cyl_4": np.round(cht_4, 1),
            "egt_cyl_1": np.round(egt_1, 1),
            "egt_cyl_2": np.round(egt_2, 1),
            "egt_cyl_3": np.round(egt_3, 1),
            "egt_cyl_4": np.round(egt_4, 1),
            "oil_temperature_c": np.round(oil_temp_c, 1),
            "oil_pressure_bar": np.round(oil_press_bar, 2),
            "coolant_temperature_c": np.round(coolant_temp_c, 1),
            "turbo_rpm": np.round(turbo_rpm, 0),
            "vibration_g": np.round(vibration_g, 2),
            "bus_voltage_v": np.round(bus_voltage_v, 2),
            "altitude_m": np.round(altitude_m, 0),
            "ambient_temp_c": np.round(ambient_temp_c, 1),
            "throttle_pct": np.round(throttle_pct, 1),
            
            # FADEC Injection & Combustion parameters
            "ignition_timing_btdc": np.round(ignition_timing_btdc, 1),
            "injection_timing_btdc": np.round(injection_timing_btdc, 2),
            "injection_pulse_width_ms": np.round(injection_pulse_width_ms, 2),
            "lambda_afr": np.round(lambda_afr, 3),
            "combustion_efficiency_pct": np.round(combustion_efficiency_pct, 1),
            
            # Physics-informed residual features
            "res_cht_spread": np.round(res_cht_spread, 2),
            "res_egt_spread": np.round(res_egt_spread, 2),
            "res_map_residual": np.round(res_map_residual, 2),
            "res_oil_press_residual": np.round(res_oil_press_residual, 2),

            # Engine age — critical for RUL prediction
            "engine_hours_used": np.round(sim_hours_used, 1),
            
            # Target Labels
            "fault_class": fault_name,
            "fault_code": fault_idx,
            "is_anomaly": 1 if fault_idx > 0 else 0,
            "rul_hours": np.round(rul_hours, 1)
        })
        dfs.append(batch_df)

    df = pd.concat(dfs, ignore_index=True)
    os.makedirs("ml_models/data", exist_ok=True)
    csv_path = "ml_models/data/aero_engine_telemetry.csv"
    df.to_csv(csv_path, index=False)
    print(f"[SUCCESS] Generated {len(df):,} telemetry samples across {len(FAULT_CLASSES)} classes saved to {csv_path}", flush=True)
    return df

if __name__ == "__main__":
    generate_telemetry_dataset()
