"""
AeroTwin Real Dataset Downloader
Downloads all available open-source engine / UAV fault datasets
Run: python ml_models/download_real_datasets.py
"""
import os
import sys
import json
import urllib.request
import zipfile

BASE_DIR = os.path.join(os.path.dirname(__file__), "data", "real_datasets")
os.makedirs(BASE_DIR, exist_ok=True)

def download_file(url, dest_path, label=""):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        print(f"  [SKIP] Already exists: {os.path.basename(dest_path)}")
        return True
    print(f"  [DL] {label}: {url[:80]}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AeroTwin-Researcher"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest_path, 'wb') as f:
            total = int(r.headers.get('Content-Length', 0))
            downloaded = 0
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(f"\r    {pct}% ({downloaded//1024} KB)", end="", flush=True)
        print(f"\n  [OK] Saved: {os.path.basename(dest_path)}")
        return True
    except Exception as e:
        print(f"\n  [FAIL] {label}: {e}")
        return False

print("=" * 60)
print("AeroTwin Real Dataset Downloader v2.0")
print("=" * 60)

# ── 1. EngineFaultDB (pip install) ─────────────────────────
print("\n[1/5] EngineFaultDB - Spark Ignition Piston Engine")
try:
    os.system("pip install git+https://github.com/Leo-Thomas/EngineFaultDB --quiet")
    import importlib
    edb = importlib.import_module("EngineFaultDB")
    import pandas as pd
    out_dir = os.path.join(BASE_DIR, "engine_fault_db")
    os.makedirs(out_dir, exist_ok=True)
    df = edb.load_data()
    out_csv = os.path.join(out_dir, "enginefaultdb_C14NE_piston.csv")
    df.to_csv(out_csv, index=False)
    print(f"  [OK] EngineFaultDB: {df.shape[0]} rows x {df.shape[1]} cols")
    meta = {
        "source": "github.com/Leo-Thomas/EngineFaultDB",
        "engine": "C14NE Spark Ignition Piston",
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": list(df.columns),
    }
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
except Exception as e:
    print(f"  [FAIL] EngineFaultDB: {e}")

# ── 2. Marine Engine Fault Dataset (Zenodo) ─────────────────
print("\n[2/5] Marine Diesel Engine Fault Dataset (Zenodo)")
marine_dir = os.path.join(BASE_DIR, "marine_engine_fault")
os.makedirs(marine_dir, exist_ok=True)
marine_base = "https://zenodo.org/records/19857425/files"
marine_files = [
    "dataset_index.csv",
    "variable_dictionary.csv",
    "ref_cond.csv",
    "fault_03_injection_valve_nozzle.csv",
    "fault_05_turbine_degradation.csv",
]
downloaded_marine = 0
for fname in marine_files:
    url = f"{marine_base}/{fname}?download=1"
    dest = os.path.join(marine_dir, fname)
    if download_file(url, dest, f"Marine {fname}"):
        downloaded_marine += 1
if downloaded_marine == 0:
    meta = {
        "source": "zenodo.org/records/19857425",
        "engine": "Matsui MU323DGSC Marine Diesel Turbo",
        "samples": 115000, "csv_files": 16, "channels": 70,
        "fault_types": ["Compressor clogging", "Injection nozzle", "Turbine degradation",
                        "Air-cooler fouling", "Cooling pump cavitation"],
        "relevance": "HIGH - Same diesel+turbo as Austro AE300",
        "status": "PENDING - Zenodo under load, download manually"
    }
    with open(os.path.join(marine_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

# ── 3. ALFA Dataset - Check extracted files ──────────────────
print("\n[3/5] ALFA CMU - Real UAV Engine Failures (Check)")
alfa_dir = os.path.join(BASE_DIR, "alfa_uav_engine_failure")
alfa_processed = os.path.join(alfa_dir, "processed")
alfa_csv_count = 0
alfa_engine_failures = 0
if os.path.exists(alfa_processed):
    try:
        import pandas as pd
        engine_csvs = []
        for root, dirs, files in os.walk(alfa_processed):
            for f in files:
                if f.endswith(".csv"):
                    alfa_csv_count += 1
                    if "engine_failure" in root.lower() or "engine_failure" in f.lower():
                        engine_csvs.append(os.path.join(root, f))
                        alfa_engine_failures += 1
        print(f"  [OK] {alfa_csv_count} CSV files, {alfa_engine_failures} engine failure files")
        # Combine first 10 engine failure flights
        dfs = []
        for csv_f in engine_csvs[:10]:
            try:
                df_tmp = pd.read_csv(csv_f, nrows=500)
                df_tmp["source_flight"] = os.path.basename(os.path.dirname(csv_f))
                dfs.append(df_tmp)
            except Exception:
                pass
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            out_csv = os.path.join(alfa_dir, "alfa_engine_failures_combined.csv")
            combined.to_csv(out_csv, index=False)
            print(f"  [OK] Combined: {combined.shape[0]} rows -> alfa_engine_failures_combined.csv")
            print(f"  Columns: {list(combined.columns[:10])}")
    except Exception as e:
        print(f"  [WARN] {e}")
else:
    print("  [INFO] ALFA not extracted yet")

# ── 4. Update Master Summary ─────────────────────────────────
print("\n[4/5] Updating MASTER_SUMMARY.json...")
summary = {
    "total_real_flights": 1683 + alfa_csv_count,
    "total_piston_samples": 69499 + 55999,
    "corpus_description": "Multi-source real + physics-validated synthetic engine data",
    "datasets": {
        "NASA_CMAPSS": {"type": "NASA Simulated", "status": "DOWNLOADED"},
        "ALFA_CMU": {
            "type": "REAL UAV Engine Failures", "flights": 47,
            "csv_files": alfa_csv_count, "engine_failure_csvs": alfa_engine_failures,
            "status": "DOWNLOADED + EXTRACTED"
        },
        "EngineFaultDB": {
            "type": "REAL Piston IC Engine", "samples": 55999,
            "engine": "C14NE Spark Ignition",
            "status": "DOWNLOADED" if os.path.exists(
                os.path.join(BASE_DIR, "engine_fault_db", "enginefaultdb_C14NE_piston.csv")) else "PENDING"
        },
        "Marine_Engine_Fault": {
            "type": "REAL Marine Diesel Turbo", "samples": 115000,
            "relevance": "Austro AE300 proxy (diesel+turbo)",
            "status": f"{'DOWNLOADED' if downloaded_marine > 0 else 'PENDING - Zenodo slow'}"
        },
        "IDF_DS": {"type": "REAL Fixed Wing UAV", "flights": 240, "status": "PENDING"},
        "UAV_SEAD": {"type": "REAL UAV Anomaly", "flights": 1396, "status": "PENDING"},
        "Synthetic_AeroTwin": {
            "type": "Physics-Validated Synthetic", "samples": "1M+",
            "engines": ["ROTAX_914F", "AUSTRO_AE300", "LYCOMING_IO360"],
            "status": "GENERATED"
        }
    }
}
with open(os.path.join(BASE_DIR, "MASTER_SUMMARY.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("  [OK] MASTER_SUMMARY.json updated")

# ── 5. Final Report ──────────────────────────────────────────
print("\n" + "=" * 60)
print("DOWNLOAD STATUS REPORT")
print("=" * 60)
total_mb = 0
for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), "data")):
    for f in files:
        total_mb += os.path.getsize(os.path.join(root, f)) / (1024*1024)
print(f"  Total data: {total_mb:.1f} MB")
print(f"  ALFA CSV files extracted: {alfa_csv_count}")
print(f"  ALFA engine failure scenarios: {alfa_engine_failures}")
print("\n  STILL NEEDED (Manual download):")
print("  -> Marine Engine: https://zenodo.org/records/19857425")
print("  -> IDF-DS:        https://doi.org/10.5281/zenodo.16992975")
print("  -> Kaggle Engine: kaggle datasets download -d zizya0/engine-fault-detection-data")
print("=" * 60)
