import os, glob, shutil
pattern = r'D:\AeroTwin_Datasets\**\Vibration dataset*'
files = glob.glob(pattern, recursive=True)
if files:
    for f in files:
        sz = os.path.getsize(f) // 1024 // 1024
        print(f"Deleting: {f} ({sz} MB)")
        os.remove(f)
        print("  Done.")
else:
    print("File not found - may already be deleted.")
print(f"D: Free: {shutil.disk_usage('D:').free/1024**3:.1f} GB")
