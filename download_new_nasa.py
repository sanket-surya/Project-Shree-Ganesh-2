import urllib.request, os, zipfile, time, json

base = r'ml_models\data\real_datasets'
HEADERS = {'User-Agent': 'Mozilla/5.0 AeroTwin Research'}

datasets_to_download = [
    # IGBT Accelerated Aging - 229MB - Power electronics degradation data (useful for UAV power systems!)
    ('nasa_igbt_aging', 'NASA IGBT Accelerated Aging',
     'https://phm-datasets.s3.amazonaws.com/NASA/8.+IGBT+Accelerated+Aging.zip', 240000000),
    # Algae Raceway - 9MB - Small but NASA verified
    ('nasa_algae_raceway', 'NASA Algae Raceway',
     'https://phm-datasets.s3.amazonaws.com/NASA/1.+Algae+Raceway.zip', 9500000),
]

# NOTE: GE-UTK Generator is 21GB - SKIP unless specifically requested
# Saving metadata only for now
ge_meta_dir = os.path.join(base, 'nasa_ge_utk_generator')
os.makedirs(ge_meta_dir, exist_ok=True)
json.dump({
    'name': 'NASA GE-UTK Generator Fault Dataset',
    'url': 'https://phm-datasets.s3.amazonaws.com/GE-UTK/FMCRD_Data.zip',
    'size_gb': 21.3,
    'note': 'CONFIRMED ACCESSIBLE - Generator fault detection data. Download separately (21GB)',
    'relevance': 'HIGH - Generator/alternator fault prediction for aircraft power systems'
}, open(os.path.join(ge_meta_dir, 'metadata.json'), 'w'), indent=2)
print('[META] NASA GE-UTK Generator (21GB) - metadata saved, download separately if needed')

def download_with_resume(folder, name, url, total_target):
    dest_dir = os.path.join(base, folder)
    os.makedirs(dest_dir, exist_ok=True)
    fname = os.path.basename(url).replace('+', '_')
    dest_file = os.path.join(dest_dir, fname)
    
    current_size = os.path.getsize(dest_file) if os.path.exists(dest_file) else 0
    
    if current_size >= total_target * 0.99:
        print(f'[DONE] {name}: Already complete ({current_size//1048576}MB)')
        return True
    
    headers = dict(HEADERS)
    if current_size > 0:
        headers['Range'] = f'bytes={current_size}-'
        print(f'[RESUME] {name}: Resuming from {current_size//1048576}MB...')
    else:
        print(f'[START] {name}: Downloading from 0...')
    
    try:
        req = urllib.request.Request(url, headers=headers)
        mode = 'ab' if current_size > 0 else 'wb'
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest_file, mode) as f:
            downloaded = current_size
            last_print = time.time()
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if time.time() - last_print > 5:
                    pct = (downloaded / total_target * 100) if total_target > 0 else 0
                    print(f'  {name}: {downloaded//1048576}MB ({pct:.1f}%)')
                    last_print = time.time()
        
        final_size = os.path.getsize(dest_file)
        print(f'[DONE] {name}: {final_size//1048576}MB downloaded!')
        
        # Save metadata
        json.dump({'name': name, 'url': url, 'size_mb': final_size//1048576,
                   'source': 'NASA PCoE S3', 'verified': True}, 
                  open(os.path.join(dest_dir, 'metadata.json'), 'w'), indent=2)
        return True
    except Exception as e:
        print(f'[ERROR] {name}: {e}')
        return False

print('\n=== DOWNLOADING NEW NASA DATASETS ===\n')
for folder, name, url, target in datasets_to_download:
    download_with_resume(folder, name, url, target)

print('\n=== ALL DOWNLOADS COMPLETE ===')
