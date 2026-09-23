"""
AeroTwin - PATCH 3: Aero Engine Sensors & Turbine Fault Datasets (~9 MB)
Includes:
1. Aircraft Sensor and Engine Performance (~6.6 MB)
2. Aircraft Engine Predictive Maintenance (~1.3 MB)
3. Engine Fault Detection Data Multi-Sensor (~1.0 MB)
4. Gas Turbine Engine Fault Detection Dataset (~115 KB)

Usage:
  python PATCH_3_ENGINE_SENSORS.py
"""
import os
import sys
import time
import shutil
import zipfile
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

BASE = r"D:\AeroTwin_Datasets"
os.makedirs(BASE, exist_ok=True)

DATASETS = [
    {
        "name": "1. Aircraft Sensor & Engine Performance",
        "ref": "aadharshviswanath/aircraft-sensor-and-engine-performance",
        "folder": "aircraft_sensor_performance",
        "size": "~6.6 MB"
    },
    {
        "name": "2. Aircraft Engine Predictive Maintenance",
        "ref": "mhadani/predictive-maintenance-aircraft-engine",
        "folder": "aircraft_engine_pred_maint",
        "size": "~1.3 MB"
    },
    {
        "name": "3. Engine Fault Detection Data Multi-Sensor",
        "ref": "ziya07/engine-fault-detection-data",
        "folder": "engine_fault_detection",
        "size": "~1.0 MB"
    },
    {
        "name": "4. Gas Turbine Engine Fault Detection",
        "ref": "ziya07/gas-turbine-engine-fault-detection-dataset",
        "folder": "gas_turbine_fault",
        "size": "~115 KB"
    }
]

def verify_zip(filepath):
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            bad = zf.testzip()
            if bad:
                return False, f"Corrupted at {bad}"
            return True, f"Valid ({len(zf.namelist())} files)"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 68)
    print("   AeroTwin - PATCH 3: AERO ENGINE SENSORS & TURBINE DATASETS")
    print(f"   Target Directory: {BASE}")
    print(f"   Free Space on D: : {shutil.disk_usage(BASE).free / (1024**3):.1f} GB")
    print(f"   Queue Size      : {len(DATASETS)} datasets (~9 MB)")
    print("=" * 68 + "\n")

    for i, ds in enumerate(DATASETS, 1):
        target_dir = os.path.join(BASE, ds["folder"])
        os.makedirs(target_dir, exist_ok=True)

        print("-" * 68)
        print(f"  [{i}/4] QUEUE: {ds['name']} ({ds['size']})")
        print(f"  Kaggle Ref: {ds['ref']}")
        print(f"  Destination: {target_dir}")
        print("-" * 68)

        existing = [f for f in os.listdir(target_dir) if f.endswith(('.zip', '.csv', '.mat'))]
        if existing:
            sz = sum(os.path.getsize(os.path.join(target_dir, f)) for f in existing)
            if sz > 50 * 1024:
                print(f"  [ALREADY DOWNLOADED] Size: {sz / (1024**2):.2f} MB. Skipping!\n")
                continue

        cmd = [sys.executable, "-m", "kaggle", "datasets", "download", ds["ref"], "-p", target_dir]
        success = False
        for attempt in range(1, 6):
            print(f"  Starting download (Attempt {attempt}/5)...", flush=True)
            p = subprocess.run(cmd, check=False)
            if p.returncode == 0:
                zips = [f for f in os.listdir(target_dir) if f.endswith('.zip')]
                if zips:
                    for z in zips:
                        ok, msg = verify_zip(os.path.join(target_dir, z))
                        print(f"  [VERIFICATION] {z}: {msg}")
                print(f"  [SUCCESS] {ds['name']} downloaded successfully!\n", flush=True)
                success = True
                break
            else:
                print(f"  [WARN] Attempt {attempt} failed. Retrying in 5 seconds...", flush=True)
                time.sleep(5)

        if not success:
            print(f"  [ERROR] Failed to download {ds['name']} after 5 attempts.\n", flush=True)

    print("=" * 68)
    print("   PATCH 3 DOWNLOAD COMPLETE!")
    print("=" * 68)

if __name__ == "__main__":
    main()
