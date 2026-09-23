import urllib.request, os, subprocess, sys

BASE = r"D:\AeroTwin_Datasets"

# Resume drone_B and drone_C
for fname in ["drone_B.tar", "drone_C.tar"]:
    dest = os.path.join(BASE, "drone_sound_fault_2023", fname)
    url = f"https://zenodo.org/records/7779574/files/{fname}"
    existing = os.path.getsize(dest) if os.path.exists(dest) else 0
    req = urllib.request.Request(url)
    if existing:
        req.add_header("Range", f"bytes={existing}-")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            total = int(r.headers.get("Content-Length", 0)) + existing
            print(f"DL {fname}: resume {existing/(1024**2):.0f}MB -> total {total/(1024**3):.2f}GB")
            with open(dest, "ab" if existing else "wb") as f:
                while True:
                    d = r.read(1024 * 1024)
                    if not d:
                        break
                    f.write(d)
        print(f"OK {fname}: {os.path.getsize(dest)/(1024**3):.3f}GB")
    except Exception as e:
        print(f"FAIL {fname}: {e}")

# Kaggle — targeted domain hits
targets = [
    ("mohammedbellosani/rotax-914-uav-engine-fault-dataset", "rotax914_fault"),
    ("venkataramananarukulla/aircraft-engine-failure-prediction", "aircraft_engine_fail"),
    ("srinivasanr/aero-engine-predictive-maintenance", "aero_engine_pm"),
    ("ahuyng/bearingfault-dataset", "acoustic_bearing_kaggle"),
]
for ref, folder in targets:
    d = os.path.join(BASE, folder)
    os.makedirs(d, exist_ok=True)
    if any(f.endswith(".zip") for f in os.listdir(d)):
        print(f"SKIP {folder}")
        continue
    r = subprocess.run(
        [sys.executable, "-m", "kaggle", "datasets", "download", "-d", ref, "-p", d],
        capture_output=True, text=True, timeout=120
    )
    zips = [f for f in os.listdir(d) if f.endswith(".zip")]
    if zips:
        sz = os.path.getsize(os.path.join(d, zips[0])) / (1024*1024)
        print(f"OK {folder}: {zips[0]} ({sz:.1f}MB)")
    else:
        print(f"FAIL {folder}: {r.stderr.strip()[-80:]}")

total = sum(os.path.getsize(os.path.join(r, f)) for r, d, fs in os.walk(BASE) for f in fs)
print(f"\nTOTAL: {total/(1024**3):.2f} GB")
