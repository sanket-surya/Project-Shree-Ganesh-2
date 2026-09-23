"""
AeroTwin - Automated Downloader for All Verified New Datasets
Downloads:
1. NASA IMS Bearing Dataset (~1.67 GB)
2. Drone Telemetry Tampering Dataset v2 (~694 MB)
3. TLM UAV Anomaly Detection Datasets (~4.7 MB)
4. Gas Turbine Engine Fault Detection Dataset (~115 KB)
5. Engine Fault Detection Data (~1.0 MB)
6. Aircraft Sensor & Engine Performance (~6.6 MB)
7. Aircraft Engine Predictive Maintenance (~1.3 MB)
8. Autonomous Drone Flight Telemetry 2026 (~250 KB)
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

NEW_DATASETS = [
    {
        "name": "1. NASA IMS Bearing Run-to-Failure (~1.67 GB)",
        "ref": "vinayak123tyagi/bearing-dataset",
        "folder": "nasa_ims_bearing",
        "size": "~1.67 GB"
    },
    {
        "name": "2. Drone Telemetry Tampering Dataset v2 (~694 MB)",
        "ref": "rasikaekanayakadevlk/drone-telemetry-tampering-dataset-v2",
        "folder": "drone_telemetry_tampering",
        "size": "~694 MB"
    },
    {
        "name": "3. TLM UAV Anomaly Detection (~4.7 MB)",
        "ref": "luyucwnu/tlmuav-anomaly-detection-datasets",
        "folder": "tlm_uav_anomaly",
        "size": "~4.7 MB"
    },
    {
        "name": "4. Gas Turbine Engine Fault Detection (~115 KB)",
        "ref": "ziya07/gas-turbine-engine-fault-detection-dataset",
        "folder": "gas_turbine_fault",
        "size": "~115 KB"
    },
    {
        "name": "5. Engine Fault Detection Multi-Sensor (~1.0 MB)",
        "ref": "ziya07/engine-fault-detection-data",
        "folder": "engine_fault_detection",
        "size": "~1.0 MB"
    },
    {
        "name": "6. Aircraft Sensor & Engine Performance (~6.6 MB)",
        "ref": "aadharshviswanath/aircraft-sensor-and-engine-performance",
        "folder": "aircraft_sensor_performance",
        "size": "~6.6 MB"
    },
    {
        "name": "7. Aircraft Engine Predictive Maintenance (~1.3 MB)",
        "ref": "mhadani/predictive-maintenance-aircraft-engine",
        "folder": "aircraft_engine_pred_maint",
        "size": "~1.3 MB"
    },
    {
        "name": "8. Autonomous Drone Flight Telemetry 2026 (~250 KB)",
        "ref": "beraterolelk/autonomous-drone-and-uav-flight-telemetry-2026",
        "folder": "autonomous_drone_telemetry_2026",
        "size": "~250 KB"
    }
]

def verify_zip(filepath):
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            bad = zf.testzip()
            if bad:
                return False, f"Corrupted at {bad}"
            return True, f"Valid ({len(zf.namelist())} files inside)"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("   AeroTwin - ALL VERIFIED NEW DATASETS DOWNLOADER")
    print(f"   Target Directory : {BASE}")
    free_gb = shutil.disk_usage(BASE).free / (1024**3)
    print(f"   Free Space on D: : {free_gb:.1f} GB")
    print(f"   Total in Queue   : {len(NEW_DATASETS)} datasets")
    print("=" * 70 + "\n")

    summary = []

    for idx, ds in enumerate(NEW_DATASETS, 1):
        target_dir = os.path.join(BASE, ds["folder"])
        os.makedirs(target_dir, exist_ok=True)

        print("-" * 70)
        print(f"[{idx}/{len(NEW_DATASETS)}] QUEUE: {ds['name']}")
        print(f"  Kaggle Ref : {ds['ref']}")
        print(f"  Target Dir : {target_dir}")
        print("-" * 70)

        # Check if valid zip or file already exists with substantial size (>100KB for small or >10MB for large)
        existing_zips = [f for f in os.listdir(target_dir) if f.endswith(('.zip', '.csv', '.mat', '.parquet', '.npy'))]
        total_sz = sum(os.path.getsize(os.path.join(target_dir, f)) for f in existing_zips)
        
        already_valid = False
        if existing_zips and total_sz > 50 * 1024:
            for f in existing_zips:
                if f.endswith('.zip'):
                    ok, msg = verify_zip(os.path.join(target_dir, f))
                    if ok:
                        print(f"  [ALREADY DOWNLOADED & VERIFIED] {f} ({total_sz/(1024*1024):.2f} MB, {msg})")
                        already_valid = True
                        break
                elif f.endswith(('.csv', '.mat')):
                    print(f"  [ALREADY DOWNLOADED] {f} ({total_sz/(1024*1024):.2f} MB)")
                    already_valid = True
                    break

        if already_valid:
            summary.append((ds["name"], "ALREADY OK", total_sz))
            print()
            continue

        cmd = [sys.executable, "-m", "kaggle", "datasets", "download", ds["ref"], "-p", target_dir]
        success = False
        for attempt in range(1, 6):
            print(f"  Starting download (Attempt {attempt}/5)...", flush=True)
            t0 = time.time()
            p = subprocess.run(cmd, check=False)
            t_elapsed = time.time() - t0

            if p.returncode == 0:
                # Check downloaded files
                zips = [f for f in os.listdir(target_dir) if f.endswith('.zip')]
                if zips:
                    for z in zips:
                        z_path = os.path.join(target_dir, z)
                        ok, msg = verify_zip(z_path)
                        sz_mb = os.path.getsize(z_path) / (1024*1024)
                        if ok:
                            print(f"  [SUCCESS] {z} ({sz_mb:.2f} MB in {t_elapsed:.1f}s) - {msg}")
                            success = True
                            summary.append((ds["name"], "SUCCESS", os.path.getsize(z_path)))
                        else:
                            print(f"  [WARNING] Zip test failed: {msg}. Retrying...")
                else:
                    sz_mb = sum(os.path.getsize(os.path.join(target_dir, f)) for f in os.listdir(target_dir)) / (1024*1024)
                    print(f"  [SUCCESS] Downloaded {sz_mb:.2f} MB in {t_elapsed:.1f}s")
                    success = True
                    summary.append((ds["name"], "SUCCESS", int(sz_mb * 1024 * 1024)))
                
                if success:
                    break
            else:
                print(f"  [WARN] Attempt {attempt} failed with exit code {p.returncode}. Retrying in 5 seconds...", flush=True)
                time.sleep(5)

        if not success:
            print(f"  [ERROR] Could not download {ds['name']} after 5 attempts.")
            summary.append((ds["name"], "FAILED", 0))

        print()

    print("=" * 70)
    print("   DOWNLOAD PROCESS SUMMARY")
    print("=" * 70)
    total_downloaded = 0
    for name, status, sz in summary:
        print(f"  {status:12} : {name:50} ({sz/(1024*1024):.1f} MB)")
        total_downloaded += sz
    print("-" * 70)
    print(f"  Total Data Processed: {total_downloaded/(1024*1024):.1f} MB ({total_downloaded/(1024**3):.2f} GB)")
    print(f"  Remaining Free Space on D: {shutil.disk_usage(BASE).free / (1024**3):.1f} GB")
    print("=" * 70)

if __name__ == "__main__":
    main()
