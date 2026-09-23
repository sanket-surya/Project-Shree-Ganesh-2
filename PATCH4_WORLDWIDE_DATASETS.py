"""
AeroTwin — WORLD-WIDE Dataset Hunter Patch 4
Sources: Zenodo (DOI), Mendeley Data, Figshare, NASA, Harvard Dataverse, GitHub
All direct HTTP downloads — no Kaggle timeout issues
"""
import os, sys, urllib.request, zipfile, shutil, time

BASE = r"D:\AeroTwin_Datasets"
os.makedirs(BASE, exist_ok=True)

def dl(url, dest, name, chunk_mb=50):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        print(f"  SKIP (exists): {name}")
        return True
    try:
        print(f"  DL: {name}")
        print(f"      {url[:80]}")
        urllib.request.urlretrieve(url, dest)
        sz = os.path.getsize(dest)/(1024*1024)
        print(f"  OK: {sz:.1f} MB -> {os.path.basename(dest)}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False

results = []

print("="*65)
print("  AEROTWIN — WORLD-WIDE DATASET HUNTER (Patch 4)")
print("  Sources: Zenodo · Mendeley · Figshare · NASA · Harvard")
print("="*65)

# ── 1. Mendeley: ICE Journal Bearing Vibration 2024 ───────────────
# DOI: 10.17632/3fcrrdjjvk.5  — piston engine bearing under diverse conditions
print("\n[1] Mendeley: ICE Journal Bearing Vibration (DOI: 3fcrrdjjvk)")
ok = dl(
    "https://data.mendeley.com/public-files/datasets/3fcrrdjjvk/files/download",
    os.path.join(BASE, "mendeley_ice_journal_bearing", "ice_journal_bearing.zip"),
    "ICE Journal Bearing Vibration 2024"
)
results.append(("Mendeley ICE Journal Bearing", ok))

# ── 2. Zenodo: DGEN 380 Turbofan Vibroacoustic ────────────────────
print("\n[2] Zenodo: DGEN 380 Turbofan Vibroacoustic (2024)")
ok = dl(
    "https://zenodo.org/records/10951459/files/DGEN380_vibroacoustic.zip",
    os.path.join(BASE, "dgen380_turbofan_vibroacoustic", "DGEN380.zip"),
    "DGEN 380 Turbofan Vibroacoustic"
)
results.append(("DGEN 380 Turbofan", ok))

# ── 3. Zenodo: Lenze Motor Bearing Fault (2025) ───────────────────
print("\n[3] Zenodo: Lenze Motor Bearing Fault Dataset")
ok = dl(
    "https://zenodo.org/records/10543968/files/Lenze-MB.zip",
    os.path.join(BASE, "lenze_motor_bearing_fault", "Lenze-MB.zip"),
    "Lenze Motor Bearing Fault"
)
results.append(("Lenze Motor Bearing", ok))

# ── 4. Zenodo: Ball Bearing Vibration Metrics 2023 ────────────────
print("\n[4] Zenodo: Ball Bearing Vibration Metrics 2023")
ok = dl(
    "https://zenodo.org/records/8202676/files/vibration_bearing_metrics.zip",
    os.path.join(BASE, "ball_bearing_vibration_metrics", "vibration_metrics.zip"),
    "Ball Bearing Vibration Metrics 2023"
)
results.append(("Ball Bearing Metrics 2023", ok))

# ── 5. Zenodo: Drone Sound Fault Classification 2023 ─────────────
print("\n[5] Zenodo: Drone Sound Fault Classification 2023")
ok = dl(
    "https://zenodo.org/records/7779574/files/Drone_Sound_Dataset.zip",
    os.path.join(BASE, "drone_sound_fault_2023", "drone_sound.zip"),
    "Drone Sound Fault Classification 2023"
)
results.append(("Drone Sound Fault", ok))

# ── 6. Zenodo: Politecnico Torino Rolling Bearing ─────────────────
print("\n[6] Zenodo: Politecnico di Torino Rolling Bearing")
ok = dl(
    "https://zenodo.org/records/3900270/files/Data.zip",
    os.path.join(BASE, "polito_rolling_bearing", "polito_data.zip"),
    "Politecnico Torino Rolling Bearing"
)
results.append(("PoliTo Rolling Bearing", ok))

# ── 7. NASA Open Data: Aviation Safety data ───────────────────────
print("\n[7] NASA: ASRS Aviation Safety Reporting (CSV)")
ok = dl(
    "https://data.nasa.gov/api/views/q2a6-tr5b/rows.csv?accessType=DOWNLOAD",
    os.path.join(BASE, "nasa_asrs_aviation_safety", "asrs_reports.csv"),
    "NASA ASRS Aviation Safety Reports"
)
results.append(("NASA ASRS Aviation Safety", ok))

# ── 8. GitHub: ALPHA UAV dataset (direct CSV) ─────────────────────
print("\n[8] ALPHA UAV Engine Failure (GitHub CMU)")
ok = dl(
    "https://raw.githubusercontent.com/amirabbasasadi/ALPHA-dataset/main/data/engine_failure_metadata.csv",
    os.path.join(BASE, "alpha_uav_github", "engine_failure_metadata.csv"),
    "ALPHA UAV Engine Failure Metadata"
)
results.append(("ALPHA UAV GitHub", ok))

# ── 9. Figshare: Helicopter gearbox dataset ───────────────────────
print("\n[9] Figshare: Helicopter Gearbox Vibration")
ok = dl(
    "https://figshare.com/ndownloader/articles/5765383/versions/1",
    os.path.join(BASE, "figshare_helicopter_gearbox", "helicopter_gearbox.zip"),
    "Figshare Helicopter Gearbox"
)
results.append(("Figshare Helicopter Gearbox", ok))

# ── 10. Harvard Dataverse: UAV telemetry ─────────────────────────
print("\n[10] Harvard Dataverse: UAV Flight Telemetry")
ok = dl(
    "https://dataverse.harvard.edu/api/access/datafile/6714890",
    os.path.join(BASE, "harvard_uav_telemetry", "uav_telemetry.tab"),
    "Harvard Dataverse UAV Telemetry"
)
results.append(("Harvard UAV Telemetry", ok))

# ── Summary ───────────────────────────────────────────────────────
print("\n" + "="*65)
print("  DOWNLOAD SUMMARY")
print("="*65)
ok_count = sum(1 for _, s in results if s)
for name, status in results:
    print(f"  {'OK ' if status else 'FAIL'} | {name}")

total = sum(
    os.path.getsize(os.path.join(r,f))
    for r,d,fs in os.walk(BASE) for f in fs
)
print(f"\n  TOTAL: {total/(1024**3):.2f} GB ({ok_count}/{len(results)} new sources)")
print("="*65)
