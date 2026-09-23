"""
AeroTwin - PATCH 2: UAV Flight Telemetry & Tampering Datasets (~700 MB)
Includes:
1. Drone Telemetry Tampering Dataset v2 (~694 MB)
2. TLM UAV Anomaly Detection (~4.7 MB)
3. Autonomous Drone Flight Telemetry 2026 (~250 KB)

Usage:
  python PATCH_2_UAV_TELEMETRY.py
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
        "name": "1. Drone Telemetry Tampering Dataset v2",
        "ref": "rasikaekanayakadevlk/drone-telemetry-tampering-dataset-v2",
        "folder": "drone_telemetry_tampering",
        "size": "~694 MB"
    },
    {
        "name": "2. TLM UAV Anomaly Detection Datasets",
        "ref": "luyucwnu/tlmuav-anomaly-detection-datasets",
        "folder": "tlm_uav_anomaly",
        "size": "~4.7 MB"
    },
    {
        "name": "3. Autonomous Drone Flight Telemetry 2026",
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
            return True, f"Valid ({len(zf.namelist())} files)"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 68)
    print("   AeroTwin - PATCH 2: UAV TELEMETRY & TAMPERING DATASETS")
    print(f"   Target Directory: {BASE}")
    print(f"   Free Space on D: : {shutil.disk_usage(BASE).free / (1024**3):.1f} GB")
    print(f"   Queue Size      : {len(DATASETS)} datasets (~700 MB)")
    print("=" * 68 + "\n")

    for i, ds in enumerate(DATASETS, 1):
        target_dir = os.path.join(BASE, ds["folder"])
        os.makedirs(target_dir, exist_ok=True)

        print("-" * 68)
        print(f"  [{i}/3] QUEUE: {ds['name']} ({ds['size']})")
        print(f"  Kaggle Ref: {ds['ref']}")
        print(f"  Destination: {target_dir}")
        print("-" * 68)

        # Check existing
        existing = [f for f in os.listdir(target_dir) if f.endswith(('.zip', '.csv', '.mat'))]
        if existing:
            sz = sum(os.path.getsize(os.path.join(target_dir, f)) for f in existing)
            if sz > 100 * 1024:
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
    print("   PATCH 2 DOWNLOAD COMPLETE!")
    print("=" * 68)

if __name__ == "__main__":
    main()
