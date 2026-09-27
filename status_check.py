import os, shutil

BASE     = r'D:\AeroTwin_Datasets'
UNPACKED = os.path.join(BASE, 'unpacked')

# Free space
free = shutil.disk_usage('D:').free / 1024**3
print(f"D: Free: {free:.1f} GB")

# Count remaining archives (pending)
pending = []
for root, dirs, files in os.walk(BASE):
    if root.startswith(UNPACKED): continue
    for f in files:
        if f.endswith(('.zip','.tar','.tar.gz','.7z','.rar')):
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp) / 1024**3
            pending.append((f, sz, fp))

pending.sort(key=lambda x: -x[1])
print(f"\nRemaining Archives: {len(pending)}")
for fname, sz, fp in pending:
    print(f"  {fname[:60]:60} {sz:.2f} GB")

# Count extracted
total_files = sum(len(fs) for _, _, fs in os.walk(UNPACKED))
total_dirs  = sum(len(d) for _, d, _ in os.walk(UNPACKED) if _ == [])
folders = [d for d in os.listdir(UNPACKED) if os.path.isdir(os.path.join(UNPACKED, d))]
print(f"\nUnpacked Datasets: {len(folders)} folders | {total_files:,} files")

# Empty folders to clean
empty = [d for d in folders if sum(len(fs) for _, _, fs in os.walk(os.path.join(UNPACKED, d))) == 0]
if empty:
    print(f"\nEmpty folders to clean: {len(empty)}")
    for e in empty:
        fp = os.path.join(UNPACKED, e)
        shutil.rmtree(fp)
        print(f"  Deleted empty: {e}")
else:
    print("\nNo empty folders.")

print("\nDone.")
