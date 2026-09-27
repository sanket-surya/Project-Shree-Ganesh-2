import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

BASE     = r'D:\AeroTwin_Datasets'
UNPACKED = os.path.join(BASE, 'unpacked')

# Find XJTU zip
import glob
xjtu_zips = glob.glob(r'D:\AeroTwin_Datasets\**\XJTU*.zip', recursive=True)
pader_zips = glob.glob(r'D:\AeroTwin_Datasets\**\paderborn*.zip', recursive=True)
print(f"XJTU zips found:     {xjtu_zips}")
print(f"Paderborn zips found: {pader_zips}")

# Check paderborn in unpacked
pader_dirs = [d for d in os.listdir(UNPACKED) if 'pader' in d.lower() or 'pedro' in d.lower()]
print(f"\nPaderborn unpacked: {pader_dirs}")
for d in pader_dirs:
    fp = os.path.join(UNPACKED, d)
    fc = sum(len(fs) for _, _, fs in os.walk(fp))
    sz = sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(fp) for f in fs) / 1024**3
    print(f"  {d}: {fc} files, {sz:.2f} GB")

print(f"\nD: Free: {shutil.disk_usage('D:').free/1024**3:.1f} GB")
print(f"C: Free: {shutil.disk_usage('C:').free/1024**3:.1f} GB")
