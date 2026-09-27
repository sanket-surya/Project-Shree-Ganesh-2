import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = r'D:\AeroTwin_Datasets\unpacked'

check_dirs = [
    'nasa_cmapss',
    'nasa_cmapss2',
    'cwru-mat-full-dataset',
    'cwru_bearing_full',
    'MFPT',
    'mfpt_bearing',
    'hust-bearing',
    'hust_bearing',
    'bispectrum-signal',
    'bispectrum_signal',
    '10. FEMTO Bearing',
    'FEMTOBearingDataSet',
    'pronostia_ieee_phm2012',
]

print(f"{'Folder':<45} {'Files':>7} {'Size':>10} {'Extensions'}")
print("-" * 80)

for d in check_dirs:
    fp = os.path.join(BASE, d)
    if not os.path.exists(fp):
        print(f"{'[MISSING] ' + d:<45} {'N/A':>7}")
        continue

    files = []
    for root, dirs, fs in os.walk(fp):
        for f in fs:
            files.append(os.path.join(root, f))

    if not files:
        print(f"{d:<45} {'0':>7} {'0 MB':>10} EMPTY")
        continue

    total_sz = sum(os.path.getsize(f) for f in files) / 1024**2
    exts = list(set(os.path.splitext(f)[1].lower() for f in files))[:5]
    print(f"{d:<45} {len(files):>7,} {total_sz:>9.1f}MB  {', '.join(exts)}")
