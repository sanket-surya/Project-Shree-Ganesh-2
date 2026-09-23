"""
AeroTwin — RESUME ALL INCOMPLETE DOWNLOADS
1. Drone Sound Fault (Zenodo 7779574) — 3 tar files ~7.2 GB (got only 13-16 MB each)
2. Kaggle — remaining datasets from DOWNLOAD_PATCH_MANUAL.bat
3. Cleanup tiny/junk files from bad downloads
"""
import os, sys, subprocess, urllib.request, shutil

BASE = r"D:\AeroTwin_Datasets"

def dl_resume(url, dest, name):
    """Download with resume support using Range header"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    existing = os.path.getsize(dest) if os.path.exists(dest) else 0
    try:
        req = urllib.request.Request(url)
        if existing > 0:
            req.add_header("Range", f"bytes={existing}-")
        with urllib.request.urlopen(req, timeout=60) as r:
            total = int(r.headers.get("Content-Length", 0)) + existing
            print(f"  DL: {name} | Resume from {existing/(1024**2):.1f}MB | Total ~{total/(1024**3):.2f}GB")
            with open(dest, "ab" if existing > 0 else "wb") as f:
                chunk = 1024 * 1024  # 1MB chunks
                downloaded = existing
                while True:
                    data = r.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    downloaded += len(data)
                    pct = (downloaded / total * 100) if total > 0 else 0
                    print(f"\r    {downloaded/(1024**2):.1f}MB / {total/(1024**2):.1f}MB ({pct:.1f}%)", end="", flush=True)
        print(f"\n  OK: {os.path.getsize(dest)/(1024**3):.3f} GB")
        return True
    except Exception as e:
        print(f"\n  FAIL: {e}")
        return False

def kaggle_dl(ref, folder, timeout=600):
    dest = os.path.join(BASE, folder)
    os.makedirs(dest, exist_ok=True)
    zips = [f for f in os.listdir(dest) if f.endswith(".zip") and os.path.getsize(os.path.join(dest,f)) > 1024*500]
    if zips:
        print(f"  SKIP (exists): {folder}")
        return True
    print(f"  Kaggle: {ref}")
    cmd = [sys.executable, "-m", "kaggle", "datasets", "download", "-d", ref, "-p", dest]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode == 0:
        zips = [f for f in os.listdir(dest) if f.endswith(".zip")]
        if zips:
            sz = os.path.getsize(os.path.join(dest, zips[0]))/(1024*1024)
            print(f"  OK: {zips[0]} ({sz:.1f} MB)")
            return True
    print(f"  FAIL: {r.stderr.strip()[:100]}")
    return False

print("=" * 65)
print("  AEROTWIN — RESUME ALL DOWNLOADS")
print("=" * 65)

results = []

# ── SECTION 1: Drone Sound Fault — RESUME TAR FILES ──────────────
print("\n[DRONE SOUND] Zenodo 7779574 — Resuming 3 tar files (~7.2 GB)")
drone_dir = os.path.join(BASE, "drone_sound_fault_2023")
for fname in ["drone_A.tar", "drone_B.tar", "drone_C.tar"]:
    dest = os.path.join(drone_dir, fname)
    url = f"https://zenodo.org/records/7779574/files/{fname}"
    ok = dl_resume(url, dest, fname)
    results.append((f"Drone Sound {fname}", ok))

# ── SECTION 2: Kaggle — remaining datasets ────────────────────────
print("\n[KAGGLE] Remaining datasets")
kaggle_todo = [
    ("sumairaziz/subf-v2-0-dataset-bearing-faults-sound-data", "subf_v2_bearing_sound"),
    ("bishals098/nasa-cmapss-2-engine-degradation",             "nasa_cmapss2_degradation"),
    ("ahuyng/bearingfault-dataset",                             "acoustic_bearing_fault_kaggle"),
    ("aneelahmad/helicopter-engines-dataset",                   "helicopter_engine_alt"),
    ("jishnukoliyath/rotax-912-engine-data",                    "rotax_912_engine_data"),
    ("datasets/phm-data-challenge-2010",                        "phm_2010_challenge"),
]
for ref, folder in kaggle_todo:
    try:
        ok = kaggle_dl(ref, folder, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {ref} — try CMD manually")
        ok = False
    results.append((folder, ok))

# ── SECTION 3: Cleanup junk tiny files ───────────────────────────
print("\n[CLEANUP] Removing junk downloads (<100KB non-CSV)")
junk_dirs = [
    "zenodo_lenze_motor_bearing",     # only treatment.html
    "zenodo_polito_rolling_bearing",  # only PDF
    "zenodo_dgen380_turbofan",        # steam CSV (not aero)
]
for d in junk_dirs:
    path = os.path.join(BASE, d)
    if os.path.exists(path):
        sz = sum(os.path.getsize(os.path.join(r,f)) for r,ds,fs in os.walk(path) for f in fs)
        if sz < 1024*1024:  # < 1MB
            shutil.rmtree(path)
            print(f"  DELETED: {d}")

# ── Summary ───────────────────────────────────────────────────────
print("\n" + "="*65)
for name, ok in results:
    print(f"  {'OK  ' if ok else 'FAIL'} | {name}")

total = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(BASE) for f in fs)
print(f"\n  TOTAL: {total/(1024**3):.2f} GB")
print("="*65)
