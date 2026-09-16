import requests

def test_api():
    base_url = "http://localhost:8000"
    print("Testing REST endpoints...")

    endpoints = [
        "/api/health-report",
        "/api/degradation-trend",
        "/api/fleet-status",
        "/api/maintenance-schedule",
        "/api/mission/profiles"
    ]

    for ep in endpoints:
        try:
            r = requests.get(base_url + ep)
            print(f"GET {ep:<30} -> Status {r.status_code} | OK: {r.ok}")
        except Exception as e:
            print(f"GET {ep:<30} -> Failed: {e}")

    # Test Hardware Ingest POST
    try:
        sample_hardware_payload = {
            "source": "ESP32_HARDWARE_NODE",
            "rpm": 5200.0,
            "vibration_g": 1.62,
            "cht_c": [112.0, 114.0, 115.5, 113.0],
            "egt_c": [815.0, 820.0, 810.0, 818.0],
            "oil_temperature_c": 93.5,
            "oil_pressure_bar": 3.9,
            "manifold_pressure_hpa": 1180.0,
            "bus_voltage_v": 28.2,
            "ignition_timing_btdc": 26.5,
            "injection_timing_btdc": 8.8,
            "injection_pulse_ms": 4.1,
            "lambda_afr": 1.015,
            "combustion_eff_pct": 93.2,
            "health_index": 0.98,
            "rul_hours": 870.0
        }
        r_post = requests.post(base_url + "/api/telemetry/hardware-ingest", json=sample_hardware_payload)
        print(f"POST /api/telemetry/hardware-ingest -> Status {r_post.status_code} | OK: {r_post.ok}")
    except Exception as e:
        print(f"POST hardware-ingest -> Failed: {e}")

if __name__ == '__main__':
    test_api()
