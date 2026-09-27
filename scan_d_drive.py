import os, shutil

D = 'D:\\'
print(f"D: Free: {shutil.disk_usage(D).free/1024**3:.1f} GB\n")

# Top-level folders on D with size
print("=== TOP LEVEL FOLDERS ON D: ===")
entries = []
try:
    for name in os.listdir(D):
        fp = os.path.join(D, name)
        try:
            if os.path.isdir(fp):
                total = sum(
                    os.path.getsize(os.path.join(r, f))
                    for r, d, fs in os.walk(fp)
                    for f in fs
                    if not os.path.islink(os.path.join(r, f))
                )
                entries.append((name, total, 'DIR', fp))
            else:
                sz = os.path.getsize(fp)
                entries.append((name, sz, 'FILE', fp))
        except Exception as e:
            entries.append((name, 0, 'ERR', fp))
except Exception as e:
    print(f"Error listing D: {e}")

entries.sort(key=lambda x: -x[1])
for name, sz, typ, fp in entries:
    sz_str = f"{sz/1024**3:.2f} GB" if sz >= 1024**3 else f"{sz/1024**2:.0f} MB" if sz >= 1024**2 else f"{sz/1024:.0f} KB"
    print(f"  [{typ}] {name:45} {sz_str}")

print(f"\nTotal shown: {sum(x[1] for x in entries)/1024**3:.1f} GB")
