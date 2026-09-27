"""
Scan all remaining archives in D:\AeroTwin_Datasets
Test each with 7-Zip. If corrupt and can't be repaired -> delete.
"""
import os, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

BASE     = r'D:\AeroTwin_Datasets'
UNPACKED = os.path.join(BASE, 'unpacked')
SEVEN_Z  = r'C:\Program Files\7-Zip\7z.exe'

# Find all archives (including in unpacked subfolders too - check everything)
archives = []
for root, dirs, files in os.walk(BASE):
    for f in files:
        if f.endswith(('.zip', '.tar', '.tar.gz', '.7z', '.rar')):
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            archives.append((fp, f, sz))

archives.sort(key=lambda x: x[2], reverse=True)

print(f"{'='*65}")
print(f"  AeroTwin — Archive Integrity Check + Auto-Delete Corrupt")
print(f"  Total archives found: {len(archives)}")
print(f"{'='*65}\n")

ok_count      = 0
corrupt_count = 0
deleted_count = 0
empty_count   = 0

for fp, fname, sz in archives:
    sz_mb = sz / (1024**2)
    sz_str = f"{sz_mb/1024:.2f} GB" if sz_mb >= 1024 else f"{sz_mb:.1f} MB"

    # Empty file check
    if sz == 0:
        print(f"[EMPTY ] {fname} ({sz_str}) — deleting...")
        try:
            os.remove(fp)
            print(f"  🗑  Deleted empty file.")
            deleted_count += 1
            empty_count += 1
        except Exception as e:
            print(f"  ⚠  Could not delete: {e}")
        continue

    # Test archive with 7-Zip
    result = subprocess.run(
        [SEVEN_Z, 't', fp],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120
    )

    is_ok = result.returncode == 0

    if is_ok:
        print(f"[OK    ] {fname} ({sz_str})")
        ok_count += 1
    else:
        # Try to check if it's a multi-part or partial - look for specific 7zip error
        err_out = (result.stdout + result.stderr).lower()
        is_partial = 'unexpected end' in err_out or 'headers error' in err_out or 'data error' in err_out

        print(f"[CORRUPT] {fname} ({sz_str})")
        print(f"   Reason: {result.stdout.strip()[-200:] if result.stdout.strip() else 'Unknown error'}")

        # Cannot repair zip/rar/7z corruption without original source - delete
        print(f"  Cannot repair — deleting...")
        try:
            os.remove(fp)
            print(f"  🗑  Deleted corrupt archive. Freed: {sz_mb/1024:.2f} GB")
            deleted_count += 1
            corrupt_count += 1
        except Exception as e:
            print(f"  ⚠  Could not delete: {e}")

print(f"\n{'='*65}")
print(f"  INTEGRITY CHECK COMPLETE")
print(f"  ✅ OK / Good:      {ok_count}")
print(f"  ❌ Corrupt/Empty:  {corrupt_count + empty_count}")
print(f"  🗑  Deleted:        {deleted_count}")
print(f"{'='*65}")
