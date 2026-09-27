import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

BASE     = r'D:\AeroTwin_Datasets'
UNPACKED = os.path.join(BASE, 'unpacked')
SKIP     = {'paderborn-db.zip', 'XJTU-SY_Bearing_Datasets.zip'}

free = shutil.disk_usage('D:').free / 1024**3
print(f"D: Drive Free: {free:.1f} GB\n")

pending = []
already_done = []

for root, dirs, files in os.walk(BASE):
    if root.startswith(UNPACKED): continue
    for f in files:
        if not f.endswith(('.zip', '.tar', '.tar.gz', '.7z', '.rar')): continue
        fp  = os.path.join(root, f)
        sz  = os.path.getsize(fp) / 1024**3
        skip_reason = ''
        if f in SKIP:
            skip_reason = 'TOO LARGE (no space)'
        # Check if already extracted
        dest_name = os.path.splitext(f)[0]
        dest_dir  = os.path.join(UNPACKED, dest_name)
        is_done   = False
        if os.path.exists(dest_dir):
            fc = sum(len(fs) for _, _, fs in os.walk(dest_dir))
            if fc > 0:
                is_done = True
        if is_done:
            already_done.append((f, sz))
        elif skip_reason:
            print(f"  [SKIP ] {f[:55]:55} {sz:.2f} GB  <- {skip_reason}")
        else:
            pending.append((sz, f, fp))

pending.sort(key=lambda x: -x[0])
total_compressed = sum(x[0] for x in pending)

print(f"\n--- PENDING (not yet extracted) ---")
for sz, fname, fp in pending:
    sz_str = f"{sz:.2f} GB" if sz >= 1 else f"{sz*1024:.0f} MB"
    print(f"  {fname[:55]:55} {sz_str}")

print(f"\nTotal pending compressed: {total_compressed:.2f} GB")
print(f"Already extracted:        {len(already_done)} archives")
print(f"D: Free:                  {free:.1f} GB")
print(f"\nEstimate extracted size (3x avg): ~{total_compressed*3:.1f} GB needed")
print(f"Safe to proceed: {'YES' if (free - total_compressed*3) > 5 else 'RISKY - will stop if low'}")
