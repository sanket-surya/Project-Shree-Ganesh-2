import urllib.request, os, json

BASE = r"D:\AeroTwin_Datasets"

records = {
    "lenze_motor_bearing": "10543968",
    "ball_bearing_metrics": "8202676",
    "drone_sound_2023": "7779574",
    "polito_rolling_bearing": "3900270",
    "dgen380_turbofan": "10951459",
}

download_urls = []

for name, rec_id in records.items():
    url = f"https://zenodo.org/api/records/{rec_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            files = data.get("files", [])
            print(f"\n[{rec_id}] {name}:")
            for f in files[:3]:
                sz = f.get("size", 0) / (1024*1024)
                link = f["links"]["self"]
                key = f["key"]
                print(f"  {key} ({sz:.1f} MB)")
                download_urls.append((name, key, link, sz))
    except Exception as e:
        print(f"[{rec_id}] FAIL: {e}")

print("\n\n=== NOW DOWNLOADING VALID FILES ===")
for name, key, link, sz_mb in download_urls:
    if sz_mb > 2000:
        print(f"SKIP (too large {sz_mb:.0f} MB): {key}")
        continue
    dest_dir = os.path.join(BASE, f"zenodo_{name}")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, key)
    if os.path.exists(dest):
        print(f"SKIP (exists): {key}")
        continue
    try:
        print(f"DL: {key} ({sz_mb:.1f} MB)...")
        urllib.request.urlretrieve(link, dest)
        print(f"  OK: {key}")
    except Exception as e:
        print(f"  FAIL: {e}")

total = sum(
    os.path.getsize(os.path.join(r, f))
    for r, d, fs in os.walk(BASE) for f in fs
)
print(f"\nTOTAL: {total/(1024**3):.2f} GB")
