"""
AeroTwin - PATCH 1: NASA IMS Bearing Run-to-Failure Dataset (~1.06 GB)
Features:
- Complete run-to-failure vibration signals & pre-computed features
- features_good.csv, features_fault.csv, train_final.csv, test_final.csv
- Pre-trained edge AI VAE model (.tflite) for bearing anomaly detection

Usage:
  python PATCH_1_NASA_IMS_BEARING.py
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
TARGET_DIR = os.path.join(BASE, "nasa_ims_bearing")
os.makedirs(TARGET_DIR, exist_ok=True)
REF = "jawadulkarim117/nasa-bearing-dataset"

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
    print("   AeroTwin - PATCH 1: NASA IMS BEARING DATASET (~1.06 GB)")
    print(f"   Target Directory: {TARGET_DIR}")
    print(f"   Free Space on D: : {shutil.disk_usage(BASE).free / (1024**3):.1f} GB")
    print("=" * 68 + "\n")

    # Clean any old corrupted or partial files
    for f in os.listdir(TARGET_DIR):
        if f.endswith('.kaggle-partial'):
            try:
                os.remove(os.path.join(TARGET_DIR, f))
            except Exception:
                pass

    existing = [f for f in os.listdir(TARGET_DIR) if f.endswith(('.zip', '.csv'))]
    if existing:
        total_sz = sum(os.path.getsize(os.path.join(TARGET_DIR, f)) for f in existing)
        if total_sz > 500 * 1024 * 1024:
            print(f"  [ALREADY DOWNLOADED] Total size: {total_sz / (1024**2):.1f} MB. Skipping!\n")
            return

    cmd = [sys.executable, "-m", "kaggle", "datasets", "download", REF, "-p", TARGET_DIR]
    for attempt in range(1, 6):
        print(f"  Starting download (Attempt {attempt}/5)...", flush=True)
        t0 = time.time()
        p = subprocess.run(cmd, check=False)
        t_el = time.time() - t0
        if p.returncode == 0:
            zips = [f for f in os.listdir(TARGET_DIR) if f.endswith('.zip')]
            for z in zips:
                ok, msg = verify_zip(os.path.join(TARGET_DIR, z))
                print(f"  [VERIFICATION] {z}: {msg}")
            print(f"  [SUCCESS] NASA IMS Bearing downloaded in {t_el:.1f}s!\n")
            break
        else:
            print(f"  [WARN] Download failed. Retrying in 5s...", flush=True)
            time.sleep(5)

    print("=" * 68)
    print("   PATCH 1 DOWNLOAD COMPLETE!")
    print("=" * 68)

if __name__ == "__main__":
    main()
