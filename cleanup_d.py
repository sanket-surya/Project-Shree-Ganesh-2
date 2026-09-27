import shutil, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

# 1. Delete friend share
folder = r'D:\friend share'
print(f"Deleting: {folder}")
if os.path.exists(folder):
    sz = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(folder) for f in fs) / 1024**3
    shutil.rmtree(folder)
    print(f"  Deleted! Freed: {sz:.2f} GB")
else:
    print("  Not found.")

# 2. Empty Recycle Bin
print("\nEmptying Recycle Bin...")
try:
    subprocess.run(['powershell', '-Command', 'Clear-RecycleBin -Force -ErrorAction SilentlyContinue'], capture_output=True)
    print("  Recycle Bin emptied!")
except:
    print("  Could not empty Recycle Bin.")

# 3. Final free space
import shutil as sh
free = sh.disk_usage('D:').free / 1024**3
print(f"\nD: Free now: {free:.1f} GB")
