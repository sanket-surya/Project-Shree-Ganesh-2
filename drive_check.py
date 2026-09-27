import shutil, os

for drive in ['C:', 'D:']:
    try:
        total, used, free = shutil.disk_usage(drive + '\\')
        print(f"{drive}  Free: {free/1024**3:.1f} GB  |  Used: {used/1024**3:.1f} GB  |  Total: {total/1024**3:.1f} GB")
    except:
        print(f"{drive}  Not found")

print()
# Check remaining large archives on D
BASE = r'D:\AeroTwin_Datasets'
UNPACKED = os.path.join(BASE, 'unpacked')
archives = []
for root, dirs, files in os.walk(BASE):
    if root.startswith(UNPACKED): continue
    for f in files:
        if f.endswith(('.zip','.tar','.tar.gz','.7z','.rar')):
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)/1024**3
            archives.append((f, sz, fp))

archives.sort(key=lambda x: -x[1])
print(f"Remaining archives on D: ({len(archives)} files):")
total_zip = 0
for fname, sz, fp in archives:
    print(f"  {fname:50} {sz:.2f} GB")
    total_zip += sz
print(f"  Total compressed: {total_zip:.2f} GB")
print(f"  Est. extracted (~4x): ~{total_zip*4:.1f} GB")
