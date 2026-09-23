"""Download Zenodo Drone Sound Fault Dataset (7779574) - 3 tar files ~7.2 GB total"""
import urllib.request, os, json

BASE = r"D:\AeroTwin_Datasets"
dest_dir = os.path.join(BASE, "drone_sound_fault_2023")
os.makedirs(dest_dir, exist_ok=True)

files = [
    ("drone_A.tar", "https://zenodo.org/records/7779574/files/drone_A.tar"),
    ("drone_B.tar", "https://zenodo.org/records/7779574/files/drone_B.tar"),
    ("drone_C.tar", "https://zenodo.org/records/7779574/files/drone_C.tar"),
]

for fname, url in files:
    dest = os.path.join(dest_dir, fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 1024*1024:
        sz = os.path.getsize(dest)/(1024**3)
        print(f"SKIP (exists {sz:.2f} GB): {fname}")
        continue
    print(f"DL: {fname} (~2.4 GB)...")
    try:
        urllib.request.urlretrieve(url, dest)
        sz = os.path.getsize(dest)/(1024**3)
        print(f"  OK: {sz:.2f} GB -> {fname}")
    except Exception as e:
        print(f"  FAIL: {e}")

total = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(BASE) for f in fs)
print(f"\nD:/AeroTwin_Datasets TOTAL: {total/(1024**3):.2f} GB")
