import os, subprocess, shutil, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

SEVEN_Z  = r'C:\Program Files\7-Zip\7z.exe'
XJTU_ZIP = r'D:\AeroTwin_Datasets\xjtu_sy_bearing_full\XJTU-SY_Bearing_Datasets.zip'
XJTU_DST = r'D:\AeroTwin_Datasets\unpacked\XJTU-SY_Bearing_Datasets'
PADR_ZIP = r'D:\AeroTwin_Datasets\paderborn_full\paderborn-db.zip'
PADR_DST = r'C:\AeroTwin_Paderborn'

def free_gb(drive):
    return shutil.disk_usage(drive+'\\').free / 1024**3

print("=" * 65)
print("  Final Extraction: XJTU (D:) + Paderborn (C:)")
print(f"  D: Free: {free_gb('D:'):.1f} GB | C: Free: {free_gb('C:'):.1f} GB")
print("=" * 65)

tasks = [
    ("XJTU-SY Bearing", XJTU_ZIP, XJTU_DST, "D:"),
    ("Paderborn Full DB", PADR_ZIP, PADR_DST, "C:"),
]

for name, src, dst, drive in tasks:
    if not os.path.exists(src):
        print(f"\n[SKIP] {name} zip not found: {src}")
        continue

    sz_gb = os.path.getsize(src) / 1024**3
    fg = free_gb(drive)
    print(f"\n[EXTRACT] {name} ({sz_gb:.2f} GB zip)")
    print(f"  Dest: {dst}")
    print(f"  {drive} Free: {fg:.1f} GB")

    # Check already extracted
    if os.path.exists(dst):
        fc = sum(len(fs) for _, _, fs in os.walk(dst))
        if fc > 10:
            print(f"  Already extracted ({fc:,} files). Deleting zip only...")
            os.remove(src)
            print(f"  Deleted zip. +{sz_gb:.2f} GB freed")
            continue

    os.makedirs(dst, exist_ok=True)
    result = subprocess.run(
        [SEVEN_Z, 'x', src, f'-o{dst}', '-y'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    fc = sum(len(fs) for _, _, fs in os.walk(dst))
    if fc > 0:
        print(f"  OK — {fc:,} files extracted!")
        os.remove(src)
        print(f"  Deleted zip. Freed {sz_gb:.2f} GB on D:")
    else:
        print(f"  FAILED: {result.stderr[-200:]}")

print(f"\n{'='*65}")
print(f"  DONE | D: Free: {free_gb('D:'):.1f} GB | C: Free: {free_gb('C:'):.1f} GB")
print(f"{'='*65}")
