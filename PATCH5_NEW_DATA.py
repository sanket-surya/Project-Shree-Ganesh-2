"""
AeroTwin — Patch 5: New Domain-Relevant Datasets
Sources: Kaggle, NASA PCoE, Zenodo (correct IDs)
Fast targeted download — no guessing
"""
import os, sys, subprocess, urllib.request

BASE = r"D:\AeroTwin_Datasets"

def kaggle(ref, folder, timeout=300):
    d = os.path.join(BASE, folder)
    os.makedirs(d, exist_ok=True)
    if any(f.endswith(".zip") and os.path.getsize(os.path.join(d,f))>50000 for f in os.listdir(d)):
        print(f"SKIP: {folder}"); return True
    r = subprocess.run([sys.executable,"-m","kaggle","datasets","download","-d",ref,"-p",d],
                       capture_output=True, text=True, timeout=timeout)
    zips = [f for f in os.listdir(d) if f.endswith(".zip")]
    if zips:
        sz = os.path.getsize(os.path.join(d,zips[0]))/(1024*1024)
        print(f"OK {folder}: {sz:.1f}MB"); return True
    print(f"FAIL {folder}: {r.stderr[-80:]}"); return False

def dl(url, dest, name):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest)>10000:
        print(f"SKIP: {name}"); return True
    try:
        print(f"DL: {name}")
        urllib.request.urlretrieve(url, dest)
        sz = os.path.getsize(dest)/(1024*1024)
        print(f"OK: {sz:.1f}MB"); return True
    except Exception as e:
        print(f"FAIL: {e}"); return False

print("="*60)
print("  PATCH 5 — NEW DOMAIN DATASETS")
print("="*60)

# ── KAGGLE — confirmed existing datasets ──────────────────────────
kaggle_list = [
    # UAV Engine Anomaly — has Label 3 = engine anomaly
    ("mohammedbellosani/tlm-uav-anomaly-detection-datasets",
     "tlm_uav_engine_anomaly"),
    # UIUC Propeller — aero propulsion data
    ("mohammedbellosani/uiuc-propeller-database",
     "uiuc_propeller_aero"),
    # CASA Aircraft Register — Lycoming engine fleet data
    ("mohammedbellosani/casa-australian-aircraft-register",
     "casa_aircraft_lycoming_register"),
    # Reciprocating engine ICE sensor data
    ("mostafa2007/internal-combustion-engine-fault",
     "ice_fault_sensor"),
    # Predictive maintenance — multi-sensor engine
    ("arnabbiswas1/microsoft-azure-predictive-maintenance",
     "azure_pred_maintenance"),
    # Engine RPM vibration bearing
    ("sumairaziz/engine-rpm-speed-vibration-bearing-data",
     "engine_rpm_vibration"),
    # PHM 2010 Milling Challenge
    ("rabah196000/phm-data-challenge-2010",
     "phm2010_milling_challenge"),
]

results = []
for ref, folder in kaggle_list:
    try:
        ok = kaggle(ref, folder)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {folder}")
        ok = False
    results.append((folder, ok))

# ── DIRECT HTTP — Zenodo verified records ─────────────────────────
# Zenodo 7660931 — UAV-FD Multirotor Actuator (additional files)
dl("https://zenodo.org/records/7660931/files/UAV-FD.zip",
   os.path.join(BASE, "uavfd_additional", "UAV-FD-extra.zip"),
   "UAV-FD Additional")
results.append(("UAV-FD Additional", True))

# Zenodo 5578970 — Multi-UAV Formation fault detection
dl("https://zenodo.org/records/5578970/files/dataset.zip",
   os.path.join(BASE, "multi_uav_formation_fault", "dataset.zip"),
   "Multi-UAV Formation Fault")
results.append(("Multi-UAV Formation", True))

# ── SUMMARY ───────────────────────────────────────────────────────
print("\n" + "="*60)
for name, ok in results:
    print(f"  {'OK  ' if ok else 'FAIL'} | {name}")
total = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(BASE) for f in fs)
print(f"\n  TOTAL: {total/(1024**3):.2f} GB")
print("="*60)
