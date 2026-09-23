"""
AeroTwin - Multi-Source Domain Data Fetcher
Sources: Zenodo, NASA, PHM Society, GitHub, IEEE DataPort
Targets critical GAPS: Real piston engine sensors, aero RUL, UAV mission data
"""
import os, sys, subprocess, urllib.request, shutil, zipfile, time

BASE = r"D:\AeroTwin_Datasets"
os.makedirs(BASE, exist_ok=True)

def dl(url, dest_path, name):
    try:
        print(f"  Downloading {name}...")
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        urllib.request.urlretrieve(url, dest_path)
        sz = os.path.getsize(dest_path) / (1024*1024)
        print(f"  OK: {sz:.2f} MB -> {os.path.basename(dest_path)}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False

def kaggle_dl(ref, folder):
    dest = os.path.join(BASE, folder)
    os.makedirs(dest, exist_ok=True)
    cmd = [sys.executable, "-m", "kaggle", "datasets", "download", "-d", ref, "-p", dest]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode == 0:
        zips = [f for f in os.listdir(dest) if f.endswith('.zip')]
        if zips:
            sz = os.path.getsize(os.path.join(dest, zips[0])) / (1024*1024)
            print(f"  OK (Kaggle): {zips[0]} ({sz:.1f} MB)")
            return True
    print(f"  FAIL (Kaggle): {r.stderr.strip()[:80]}")
    return False

print("=" * 65)
print("  AEROTWIN MULTI-SOURCE GAP-FILLER DOWNLOADER")
print("  Sources: Zenodo + Kaggle + NASA + GitHub + UCI")
print("=" * 65)

results = []

# ─── GAP 1: Real piston aero engine fault data ──────────────────
# PHM 2024 Helicopter (already have zip in root, extract it)
phm_zip = r"c:\Users\Asus\Desktop\Project Shree Ganesh 2\PHM 2024 Helicopter.zip"
if os.path.exists(phm_zip):
    dest = os.path.join(BASE, "phm2024_helicopter")
    os.makedirs(dest, exist_ok=True)
    if not os.listdir(dest):
        try:
            with zipfile.ZipFile(phm_zip, 'r') as z:
                z.extractall(dest)
            sz = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(dest) for f in fs) / (1024*1024)
            print(f"[1] EXTRACTED PHM 2024 Helicopter -> {sz:.1f} MB ({dest})")
            results.append(("PHM 2024 Helicopter", "SUCCESS", f"{sz:.1f} MB"))
        except Exception as e:
            print(f"[1] PHM 2024 Helicopter FAIL: {e}")
            results.append(("PHM 2024 Helicopter", "FAIL", str(e)))
    else:
        print("[1] PHM 2024 Helicopter already extracted.")
        results.append(("PHM 2024 Helicopter", "ALREADY_DONE", ""))

# ─── GAP 2: PRONOSTIA/IEEE PHM 2012 - extract if zip exists ─────
pro_zip = os.path.join(BASE, "pronostia_ieee_phm2012", "IEEE_PHM_2012_Bearing.7z")
print(f"\n[2] PRONOSTIA: {pro_zip}")
if os.path.exists(pro_zip):
    print("  .7z file present — use 7zip manually if needed.")
    results.append(("PRONOSTIA PHM2012", "PRESENT_7Z", "186 MB"))

# ─── GAP 3: Zenodo - UAV engine failure dataset ──────────────────
print("\n[3] ZENODO: UAV Propulsion & Piston Engine datasets")
zenodo_datasets = [
    {
        "name": "UAV Motor Vibration Fault (Zenodo 7790205)",
        "url": "https://zenodo.org/records/7790205/files/UAV_motor_vibration.zip",
        "dest": os.path.join(BASE, "uav_motor_vibration_zenodo", "UAV_motor_vibration.zip"),
        "folder": "uav_motor_vibration_zenodo"
    },
    {
        "name": "PHM Society 2023 Accelerometer (Zenodo 7761861)",
        "url": "https://zenodo.org/records/7761861/files/dataset.zip",
        "dest": os.path.join(BASE, "phm2023_accelerometer_zenodo", "dataset.zip"),
        "folder": "phm2023_accelerometer_zenodo"
    },
]
for zds in zenodo_datasets:
    os.makedirs(os.path.dirname(zds["dest"]), exist_ok=True)
    ok = dl(zds["url"], zds["dest"], zds["name"])
    results.append((zds["name"], "SUCCESS" if ok else "FAIL", ""))

# ─── GAP 4: Kaggle - more domain-specific ────────────────────────
print("\n[4] KAGGLE: Additional engine & aviation datasets")
kaggle_datasets = [
    ("mohammedbellosani/boeing-787-ignition-digital-twin-and-phm-dataset", "boeing787_ignition_phm"),
    ("palbha/cmapss-jet-engine-simulated-data", "cmapss_extra"),
    ("ziya07/helicopter-engine-degradation-dataset", "helicopter_engine_degradation"),
    ("bishals098/nasa-cmapss-2-engine-degradation", "nasa_cmapss2"),
    ("sumairaziz/subf-v2-0-dataset-bearing-faults-sound-data", "subf_bearing_sound"),
]
for ref, folder in kaggle_datasets:
    dest = os.path.join(BASE, folder)
    if os.path.exists(dest) and os.listdir(dest):
        print(f"  SKIP (exists): {folder}")
        results.append((folder, "ALREADY_EXISTS", ""))
        continue
    print(f"  Kaggle: {ref}")
    ok = kaggle_dl(ref, folder)
    results.append((folder, "SUCCESS" if ok else "FAIL", ""))

# ─── Summary ─────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  DOWNLOAD SUMMARY")
print("=" * 65)
for name, status, note in results:
    icon = "OK" if "SUCCESS" in status or "DONE" in status or "EXISTS" in status else "FAIL"
    print(f"  [{icon}] {name:<50} | {status} {note}")

total = sum(
    os.path.getsize(os.path.join(r,f))
    for r,d,fs in os.walk(BASE) for f in fs
)
print(f"\n  D:/AeroTwin_Datasets TOTAL: {total/(1024**3):.2f} GB")
print("=" * 65)
