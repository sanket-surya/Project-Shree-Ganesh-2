"""
AeroTwin - DOWNLOAD REMAINING DATASETS PATCH
Downloads only the 4 pending high-value datasets:
1. Engine Acoustic Emissions (~450 MB)
2. Engine Failure Detection (~380 MB)
3. SUBF Bearing Fault Vibration v1.0 (~1.6 GB)
4. Bispectrum Signal Gearbox FFT (~1.8 GB)

Usage in CMD:
    python DOWNLOAD_REMAINING_PATCH.py
"""
import os, sys, time, subprocess, shutil

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

BASE = r"D:\AeroTwin_Datasets"
os.makedirs(BASE, exist_ok=True)

DATASETS = [
    {
        "name": "1. Engine Acoustic Emissions & Noise",
        "ref": "julienjta/engine-acoustic-emissions",
        "folder": "engine_acoustic_emissions",
        "size": "~450 MB"
    },
    {
        "name": "2. Engine Failure Multi-Sensor Telemetry",
        "ref": "zeynepyk/engine-failure-detection-dataset",
        "folder": "engine_failure_detection",
        "size": "~380 MB"
    },
    {
        "name": "3. SUBF Bearing Fault Vibration v1.0",
        "ref": "sumairaziz/subf-v1-0-dataset-bearing-fault-vibration-data",
        "folder": "subf_bearing_fault",
        "size": "~1.6 GB"
    },
    {
        "name": "4. Bispectrum Signal Gearbox FFT",
        "ref": "zacky131/bispectrum-signal",
        "folder": "bispectrum_signal",
        "size": "~1.8 GB"
    }
]

def main():
    print("*" * 65)
    print("   AeroTwin - FINAL REMAINING DATASETS DOWNLOADER")
    print(f"   Target Directory: {BASE}")
    free_gb = shutil.disk_usage(BASE).free / (1024**3)
    print(f"   Free Space on D: {free_gb:.1f} GB")
    print("*" * 65 + "\n")

    for i, ds in enumerate(DATASETS, 1):
        target_dir = os.path.join(BASE, ds["folder"])
        os.makedirs(target_dir, exist_ok=True)

        print("=" * 65)
        print(f"  [{i}/4] QUEUE: {ds['name']} ({ds['size']})")
        print(f"  Kaggle Ref: {ds['ref']}")
        print(f"  Destination: {target_dir}")
        print("=" * 65)

        existing = [f for f in os.listdir(target_dir) if f.endswith(('.zip', '.csv', '.mat', '.txt'))]
        if existing:
            sz = sum(os.path.getsize(os.path.join(target_dir, f)) for f in existing)
            if sz > 10 * 1024 * 1024:
                print(f"  [ALREADY DOWNLOADED] Size: {sz / (1024**2):.1f} MB. Skipping!\n")
                continue

        cmd = ["kaggle", "datasets", "download", ds["ref"], "-p", target_dir]
        success = False
        for attempt in range(1, 10):
            print(f"  Starting download (Attempt {attempt}/10)...", flush=True)
            p = subprocess.run(cmd, check=False)
            if p.returncode == 0:
                print(f"  [SUCCESS] {ds['name']} downloaded successfully!\n", flush=True)
                success = True
                break
            else:
                print(f"  [WARN] Download returned code {p.returncode}. Retrying in 5 seconds...", flush=True)
                time.sleep(5)

        if not success:
            print(f"  [ERROR] Failed to download {ds['name']} after 10 attempts.\n", flush=True)

    print("*" * 65)
    print("   ALL REMAINING DATASETS DOWNLOAD PROCESS COMPLETED!")
    print("*" * 65)

if __name__ == "__main__":
    main()
