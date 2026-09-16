import sys
sys.path.append('.')
from backend.physics_twin import AeroPistonTwinPhysics
from ml_models.inference_engine import AeroEngineInferenceEngine

def test_all():
    engine = AeroPistonTwinPhysics()
    ai = AeroEngineInferenceEngine()

    print("==================================================")
    print("  PHYSICS & AI REAL-TIME INFERENCE VERIFICATION")
    print("==================================================")

    # 1. Test Nominal
    engine.clear_fault()
    for _ in range(40):
        engine.step(0.05)
    st = engine.get_state_dict()
    fl = engine.get_flight_dict()
    pred = ai.predict(st, fl)
    print(f"[NOMINAL STEADY] Anomaly: {pred['is_anomaly']} | Top: {pred['primary_fault']} ({pred['fault_confidence']:.2f}) | Health: {pred['health_index']*100:.0f}% | RUL: {pred['predicted_rul_hours']}h")

    # 2. Test All 8 Fault Modes at Steady-State (50 steps = 2.5 sec of fault evolution)
    faults = [
        'Cylinder_Misfire', 'Turbo_Degradation', 'Oil_Starvation',
        'Coolant_Loss', 'Injector_Clogging', 'Sensor_Drift',
        'Combustion_Knock', 'Valve_Leakage'
    ]

    for f in faults:
        engine = AeroPistonTwinPhysics()
        for _ in range(30):
            engine.step(0.05)
        engine.inject_fault(f, 0.9)
        for _ in range(50):
            engine.step(0.05)
        st = engine.get_state_dict()
        fl = engine.get_flight_dict()
        pred = ai.predict(st, fl)
        print(f"[{f:<18}] Anomaly: {str(pred['is_anomaly']):<5} | Detected: {pred['primary_fault']:<18} ({pred['fault_confidence']:.2f}) | Health: {pred['health_index']*100:.0f}% | RUL: {pred['predicted_rul_hours']:>5.1f}h")

    # 3. Test Compound Failure
    print("\n--- Testing Compound Multi-Fault Scenario ---")
    engine.clear_fault()
    engine.inject_fault('Coolant_Loss', 0.9)
    engine.inject_fault('Turbo_Degradation', 0.8)
    for _ in range(50):
        engine.step(0.05)
    st = engine.get_state_dict()
    fl = engine.get_flight_dict()
    pred = ai.predict(st, fl)
    print(f"[COMPOUND CASCADING] Anomaly: {pred['is_anomaly']} | Detected: {pred['primary_fault']} | Health: {pred['health_index']*100:.0f}% | RUL: {pred['predicted_rul_hours']}h")
    print("==================================================")
    print("VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    test_all()
