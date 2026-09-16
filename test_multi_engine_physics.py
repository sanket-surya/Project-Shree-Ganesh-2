import pandas as pd
from backend.physics_twin import AeroPistonTwinPhysics
from ml_models.inference_engine import AeroEngineInferenceEngine

for eng_id, f_cht, off_egt in [
    ('ROTAX_914F', [0.98, 0.99, 1.03, 1.02], [0.0, 5.0, -3.0, 2.0]),
    ('AUSTRO_AE300', [1.00, 1.01, 1.01, 1.02], [0.0, 2.0, 2.0, 4.0]),
    ('LYCOMING_IO360', [0.97, 0.99, 1.04, 1.06], [0.0, 8.0, -5.0, 10.0])
]:
    pt = AeroPistonTwinPhysics()
    pt.set_engine_profile(eng_id)
    ai = AeroEngineInferenceEngine(f'ml_models/weights/{eng_id.lower()}')
    s = pt.get_state_dict()
    f = pt.get_flight_dict()
    
    is_diesel = 'Diesel' in pt.engine_name
    has_turbo = pt.max_boost_map_hpa > 1050.0
    amb = f['ambient_press_hpa']
    thr = f['throttle_pct']
    
    map_hpa = amb + (thr / 100.0) * (pt.max_boost_map_hpa - amb) if has_turbo else amb * (thr / 100.0) * 0.95
    pwr = min(pt.engine_power_kw * 1.02, (map_hpa / 1013.25) * (pt.rpm / pt.rated_rpm) * pt.engine_power_kw)
    ram = (f['airspeed_kts'] / 100.0) * (8.0 if is_diesel else 15.0)
    
    cht_base = (70.0 + (pwr / pt.engine_power_kw) * 35.0 + f['ambient_temp_c'] * 0.15) if is_diesel else (pt.nominal_cht_c - 40.0 + (pwr / pt.engine_power_kw) * 60.0 - ram + f['ambient_temp_c'] * 0.28)
    egt_base = (pt.nominal_egt_c - 100.0 + (map_hpa / pt.max_boost_map_hpa) * 150.0) if is_diesel else (pt.nominal_egt_c - 150.0 + (map_hpa / 1300.0) * 180.0)
    
    s['manifold_pressure_hpa'] = map_hpa
    s['power_output_kw'] = pwr
    s['torque_nm'] = pwr * 9548.8 / pt.rpm
    fuel_sfc = 0.210 if is_diesel else (0.310 if not has_turbo else 0.285)
    fuel_density = 0.84 if is_diesel else 0.72
    s['fuel_flow_lph'] = pwr * fuel_sfc / fuel_density
    s['fuel_pressure_bar'] = 1.8 if is_diesel else 3.0
    s['turbo_rpm'] = ((map_hpa / pt.max_boost_map_hpa) * (180000.0 if is_diesel else 145000.0)) if has_turbo else 0.0
    s['cht_c'] = [round(cht_base * fc, 1) for fc in f_cht]
    s['egt_c'] = [round(egt_base + eo, 1) for eo in off_egt]
    s['oil_temperature_c'] = pt.nominal_oil_c - 5.0
    s['oil_pressure_bar'] = (pt.rpm / pt.rated_rpm) * pt.nominal_oil_bar * (1.0 - (s['oil_temperature_c'] - pt.nominal_oil_c) * 0.004)
    s['coolant_temperature_c'] = s['oil_temperature_c'] * (0.85 if is_diesel else 0.90)
    s['overall_vibration_g'] = 0.7 + (pt.rpm / pt.rated_rpm) * 0.8
    s['ignition_timing_btdc'] = 0.0 if is_diesel else (18.0 + (pt.rpm / pt.rated_rpm) * 14.0 - (map_hpa / pt.max_boost_map_hpa) * 6.0)
    s['injection_timing_btdc'] = 5.0 + (pt.rpm / pt.rated_rpm) * 15.0 if is_diesel else (4.0 + (thr / 100.0) * 8.0)
    s['injection_pulse_width_ms'] = 1.5 + (s['fuel_flow_lph'] / (pt.engine_power_kw * 0.4)) * 4.0
    s['lambda_afr'] = pt.nominal_lambda - (thr / 100.0) * (0.3 if is_diesel else 0.08)
    s['combustion_efficiency_pct'] = 96.0 - abs(s['lambda_afr'] - pt.nominal_lambda) * 12.0
    
    diag = ai.predict(s, f)
    primary = diag['primary_fault']
    conf = diag['fault_confidence'] * 100
    rul = diag['predicted_rul_hours']
    anom = diag['is_anomaly']
    print(f"{eng_id:15s} -> Top: {primary:18s} ({conf:5.1f}%) | RUL: {rul:6.1f}h | Anomaly: {anom}")
