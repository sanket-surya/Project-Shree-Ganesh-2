"""
Extract all remaining archives from D:\AeroTwin_Datasets
Skip: paderborn-db.zip, XJTU-SY_Bearing_Datasets.zip (too large)
After successful extraction -> delete original archive
Auto-stop if free space < 8 GB
"""
import os, subprocess, shutil, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

BASE      = r'D:\AeroTwin_Datasets'
UNPACKED  = os.path.join(BASE, 'unpacked')
SEVEN_Z   = r'C:\Program Files\7-Zip\7z.exe'
MIN_FREE  = 8.0  # GB

SKIP = {
    'paderborn-db.zip',
    'XJTU-SY_Bearing_Datasets.zip',
}

def free_gb():
    return shutil.disk_usage('D:\\').free / 1024**3

# Collect all archives
all_archives = []
for root, dirs, files in os.walk(BASE):
    if root.startswith(UNPACKED): continue
    for f in files:
        if not f.endswith(('.zip', '.tar', '.tar.gz', '.7z', '.rar')): continue
        if f in SKIP: continue
        fp = os.path.join(root, f)
        sz = os.path.getsize(fp) / 1024**2  # MB
        all_archives.append((sz, f, fp, root))

all_archives.sort(key=lambda x: x[0])  # smallest first

print("=" * 65)
print(f"  Extract All Remaining — {len(all_archives)} archives")
print(f"  Total compressed: {sum(x[0] for x in all_archives)/1024:.2f} GB")
print(f"  D: Free: {free_gb():.1f} GB | Safety: {MIN_FREE} GB")
print(f"  Skipping: Paderborn ({9.02} GB) + XJTU ({4.17} GB)")
print("=" * 65 + "\n")

extracted, deleted, failed, stopped = [], [], [], []

for sz_mb, fname, src, src_dir in all_archives:
    fg = free_gb()
    if fg < MIN_FREE:
        print(f"\n[STOP] Low space: {fg:.1f} GB. Stopping safely.")
        stopped.append(fname)
        break

    # Destination = unpacked\<filename_without_ext>
    base = fname
    for ext in ('.tar.gz', '.zip', '.7z', '.rar', '.tar'):
        if base.endswith(ext):
            base = base[:-len(ext)]; break
    # Make unique dest if same name exists
    dest = os.path.join(UNPACKED, base)
    if os.path.exists(dest):
        fc = sum(len(fs) for _, _, fs in os.walk(dest))
        if fc > 0:
            # Already extracted — just delete the zip
            sz_str = f"{sz_mb/1024:.2f} GB" if sz_mb >= 1024 else f"{sz_mb:.0f} MB"
            print(f"[ALREADY] {fname} ({sz_str}) — deleting zip only")
            try:
                os.remove(src)
                print(f"  🗑  Deleted zip. Freed {sz_mb/1024:.2f} GB")
                deleted.append(fname)
            except Exception as e:
                print(f"  ⚠  Could not delete: {e}")
            continue
        # dest exists but empty — use it
    else:
        # Try appending _2, _3 etc if name conflicts
        i = 2
        orig_dest = dest
        while os.path.exists(dest):
            dest = f"{orig_dest}_{i}"; i += 1

    sz_str = f"{sz_mb/1024:.2f} GB" if sz_mb >= 1024 else f"{sz_mb:.0f} MB"
    print(f"[EXTRACT] {fname:<52} ({sz_str})  Free: {fg:.1f} GB")

    os.makedirs(dest, exist_ok=True)
    result = subprocess.run(
        [SEVEN_Z, 'x', src, f'-o{dest}', '-y'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600
    )

    fc = sum(len(fs) for _, _, fs in os.walk(dest))
    if fc > 0:
        print(f"  ✅ {fc:,} files → unpacked\\{os.path.basename(dest)}")
        extracted.append(fname)
        try:
            os.remove(src)
            print(f"  🗑  Deleted zip. Freed {sz_mb/1024:.2f} GB")
            deleted.append(fname)
        except Exception as e:
            print(f"  ⚠  Delete failed: {e}")
    else:
        print(f"  ❌ FAILED — 0 files extracted")
        # Remove empty dest dir
        try: os.rmdir(dest)
        except: pass
        failed.append(fname)

print(f"\n{'=' * 65}")
print(f"  FINAL SUMMARY")
print(f"  Extracted:  {len(extracted)}")
print(f"  Deleted:    {len(deleted)} original zips")
print(f"  Failed:     {len(failed)}")
print(f"  Stopped early (space): {len(stopped)}")
print(f"  D: Free now: {free_gb():.1f} GB")
print(f"{'=' * 65}")
if failed:    print(f"\nFailed: {failed}")
if stopped:   print(f"Stopped: {stopped}")
