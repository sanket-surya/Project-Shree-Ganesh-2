"""
AeroTwin - High-Value In-Domain Aero Engine & UAV Telemetry Downloader
Target: D:\\AeroTwin_Datasets
Datasets:
1. Cessna 172X (Lycoming IO-360 Aero Piston) JSBSim Flight Telemetry
2. NASA PHM 2009 Gearbox Fault Detection Benchmark
3. Drone Flight Telemetry with GPS, ESC & RPM
4. Automotive Multi-Sensor Engine Health
5. Aero Turboshaft Engine Fault Detection
6. Vibration Faults for Rotating Machines (Crankshaft / Bearing)
7. ICAO Aircraft Engine Emissions Database
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
        "name": "1. Cessna 172X (Lycoming IO-360) Telemetry (~2.6 MB)",
        "ref": "mohammedbellosani/phi-spike-c172x-jsbsim-aircraft-telemetry-dataset",
        "folder": "c172x_lycoming_telemetry"
    },
    {
        "name": "2. NASA PHM 2009 Gearbox Fault Detection (~90 MB)",
        "ref": "hetarthchopra/gearbox-fault-detection-dataset-phm-2009-nasa",
        "folder": "nasa_phm_2009_gearbox"
    },
    {
        "name": "3. Drone Flight Telemetry with GPS & ESC (~15 MB)",
        "ref": "kunalkarnik95/drone-flight-video-with-telemetry-gps-esc",
        "folder": "drone_flight_telemetry_esc"
    },
    {
        "name": "4. Vehicle Multi-Sensor Engine Health (~609 KB)",
        "ref": "parvmodi/automotive-vehicles-engine-health-dataset",
        "folder": "automotive_engine_health"
    },
    {
        "name": "5. Aero Turboshaft Engine Fault Detection (~1.2 MB)",
        "ref": "ziya07/helicopter-turboshaft-detection-dataset",
        "folder": "helicopter_turboshaft_fault"
    },
    {
        "name": "6. Vibration Faults for Rotating Machines (~19.5 MB)",
        "ref": "sumairaziz/vibration-faults-dataset-for-rotating-machines",
        "folder": "vibration_faults_rotating_machines"
    },
    {
        "name": "7. ICAO Aero Engine Emissions Database (~200 KB)",
        "ref": "ahmedeltom/icao-aircraft-engine-emissions",
        "folder": "icao_aero_engine_emissions"
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
    print("=" * 70)
    print("   AEROTWIN - HIGH-VALUE IN-DOMAIN DATASETS DOWNLOADER")
    print(f"   Target Directory : {BASE}")
    free_gb = shutil.disk_usage(BASE).free / (1024**3)
    print(f"   Free Space on D: : {free_gb:.1f} GB")
    print(f"   Queue Size       : {len(DATASETS)} in-domain datasets")
    print("=" * 70 + "\n")

    summary = []

    for idx, ds in enumerate(DATASETS, 1):
        name = ds["name"]
        ref = ds["ref"]
        folder_name = ds["folder"]
        dest_dir = os.path.join(BASE, folder_name)
        os.makedirs(dest_dir, exist_ok=True)

        print(f"[{idx}/{len(DATASETS)}] Downloading {name}...")
        print(f"       Ref: {ref}")
        print(f"       Dest: {dest_dir}")

        cmd = [sys.executable, "-m", "kaggle", "datasets", "download", "-d", ref, "-p", dest_dir]
        
        success = False
        error_msg = ""
        for attempt in range(1, 4):
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                if res.returncode == 0:
                    success = True
                    break
                else:
                    error_msg = res.stderr or res.stdout
                    print(f"       Attempt {attempt} failed: {error_msg.strip()[:100]}")
                    time.sleep(2)
            except Exception as e:
                error_msg = str(e)
                print(f"       Attempt {attempt} exception: {e}")
                time.sleep(2)

        if success:
            # Check downloaded files
            zips = [f for f in os.listdir(dest_dir) if f.endswith('.zip')]
            if zips:
                zip_path = os.path.join(dest_dir, zips[0])
                v_ok, v_msg = verify_zip(zip_path)
                size_mb = os.path.getsize(zip_path) / (1024 * 1024)
                print(f"       ✅ Downloaded & Verified: {zips[0]} ({size_mb:.2f} MB) -> {v_msg}")
                summary.append((name, "SUCCESS", f"{size_mb:.2f} MB", v_msg))
            else:
                files = os.listdir(dest_dir)
                total_mb = sum(os.path.getsize(os.path.join(dest_dir, f)) for f in files) / (1024 * 1024)
                print(f"       ✅ Downloaded ({len(files)} files, {total_mb:.2f} MB)")
                summary.append((name, "SUCCESS", f"{total_mb:.2f} MB", "Downloaded"))
        else:
            print(f"       ❌ FAILED after 3 attempts: {error_msg.strip()[:100]}")
            summary.append((name, "FAILED", "0 MB", error_msg.strip()[:50]))

        print()

    print("=" * 70)
    print("   DOWNLOAD SUMMARY")
    print("=" * 70)
    for name, status, size, note in summary:
        icon = "✅" if status == "SUCCESS" else "❌"
        print(f"  {icon} {name:<50} | {status} | {size} | {note}")
    print("=" * 70)

if __name__ == "__main__":
    main()
