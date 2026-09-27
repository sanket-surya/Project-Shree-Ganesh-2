r"""
Batch extractor with real-time disk space monitoring.
Extracts remaining datasets into D:\AeroTwin_Datasets\unpacked\<dataset_name>
Safety: Stops if D: drive free space drops below 25 GB.
"""
import os, sys, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'D:\AeroTwin_Datasets'
UNPACKED = os.path.join(BASE, 'unpacked')
os.makedirs(UNPACKED, exist_ok=True)

SEVEN_ZIP = r'C:\Program Files\7-Zip\7z.exe'
MIN_FREE_GB = 25.0

def get_free_space_gb():
    total, used, free = shutil.disk_usage('D:\\')
    return free / (1024**3)

# Find all zip archives outside unpacked
candidates = []
for root, dirs, files in os.walk(BASE):
    if root.startswith(UNPACKED):
        continue
    for f in files:
        if f.endswith('.zip') or f.endswith('.tar.gz') or f.endswith('.7z'):
            fp = os.path.join(root, f)
            sz_mb = os.path.getsize(fp) / (1024**2)
            rel = os.path.relpath(fp, BASE)
            
            # Skip archives that are already unpacked or partially corrupted master archives
            if f in ['rflymad.zip', 'N-CMAPSS_DS02.zip']:
                continue
            
            # Determine suitable subfolder name in unpacked
            parent_dir = os.path.basename(os.path.dirname(fp))
            if parent_dir == 'AeroTwin_Datasets':
                dest_name = os.path.splitext(f)[0]
            else:
                dest_name = parent_dir
                
            dest_dir = os.path.join(UNPACKED, dest_name)
            candidates.append((f, fp, dest_dir, sz_mb, dest_name))

# Sort by size ascending (smallest first)
candidates.sort(key=lambda x: x[3])

print(f"Total archives to extract: {len(candidates)}")
print(f"Current D: free space: {get_free_space_gb():.2f} GB (Safety limit: {MIN_FREE_GB} GB)\n")

success_count = 0
skipped_count = 0
stopped_early = False

for fname, src_path, dest_dir, sz_mb, dest_name in candidates:
    free_gb = get_free_space_gb()
    if free_gb < MIN_FREE_GB:
        print(f"\n[ALERT] Free space reached safety threshold: {free_gb:.2f} GB < {MIN_FREE_GB} GB. Stopping extraction.")
        stopped_early = True
        break
        
    # Check if dest_dir already has substantial extracted data
    if os.path.exists(dest_dir):
        existing_files = sum(len(fs) for _, _, fs in os.walk(dest_dir))
        if existing_files > 5:
            print(f"Skipping already extracted: {dest_name} ({existing_files} files present)")
            skipped_count += 1
            continue

    print(f"Extracting [{sz_mb:.1f} MB]: {fname} -> unpacked\\{dest_name} (Free: {free_gb:.1f} GB)...")
    os.makedirs(dest_dir, exist_ok=True)
    
    cmd = [SEVEN_ZIP, 'x', src_path, f'-o{dest_dir}', '-y']
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    extracted_files = sum(len(fs) for _, _, fs in os.walk(dest_dir))
    if extracted_files > 0:
        success_count += 1
        print(f"  OK: {dest_name} ({extracted_files} files)")
    else:
        print(f"  Warning: No files extracted from {fname}")

final_free = get_free_space_gb()
print("\n" + "="*50)
print(f"EXTRACTION BATCH SUMMARY:")
print(f"  Extracted: {success_count}")
print(f"  Skipped (already done): {skipped_count}")
print(f"  Stopped early due to space: {stopped_early}")
print(f"  Remaining D: Free Space: {final_free:.2f} GB")
print("="*50)
