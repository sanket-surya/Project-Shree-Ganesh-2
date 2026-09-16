import sys
import os

print("="*60)
print("AEROTWIN SYSTEM-WIDE AUDIT & VERIFICATION")
print("="*60)

try:
    from backend.physics_twin import AeroPistonTwinPhysics, ENGINE_PROFILES
    from ml_models.inference_engine import AeroEngineInferenceEngine
    import backend.main as main_app
    print("[PASS] Core backend modules imported cleanly.")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# 1. Test all engine profiles
pt = AeroPistonTwinPhysics()
ai = AeroEngineInferenceEngine()

for eng_id in ENGINE_PROFILES.keys():
    pt.set_engine_profile(eng_id)
    swapped = ai.switch_engine(eng_id)
    for _ in range(25):
        pt.step(0.05)
    telem = pt.get_state_dict()
    flight = pt.get_flight_dict()
    diag = ai.predict(telem, flight)
    print(f"[ENGINE {eng_id}] RPM={telem['rpm']:.1f} | Top: {diag['primary_fault']} ({diag['fault_confidence']*100:.1f}%) | RUL: {diag['predicted_rul_hours']:.1f}h")

# 2. Test Fault Injections
print("\n--- Testing Fault Injections on Rotax 914F ---")
pt.set_engine_profile("ROTAX_914F")
ai.switch_engine("ROTAX_914F")
test_faults = ["Cylinder_Misfire", "Injector_Clogging", "Turbo_Degradation", "Coolant_Loss", "Oil_Starvation"]
for f in test_faults:
    pt.inject_fault(f, severity=0.8)
    for _ in range(20):
        pt.step(0.05)
    telem = pt.get_state_dict()
    flight = pt.get_flight_dict()
    diag = ai.predict(telem, flight)
    print(f"Fault [{f:18s}] -> Detected: {diag['primary_fault']:18s} (Conf: {diag['fault_confidence']*100:5.1f}%) | Anomaly Score: {diag['anomaly_score']:.2f}")
    pt.clear_fault()

# 3. Test Cascade Failure Demo logic in main.py
print("\n--- Testing Cascade Sequence Data ---")
for stage in main_app.CASCADE_STAGES:
    print(f"Stage {stage['stage']}: {stage['label']} | Fault: {stage['fault']}")

print("\n[SUCCESS] All Python backend tests completed without error!")
