import urllib.request, os, time, json

base = r'ml_models\data\real_datasets'
H = {'User-Agent': 'Mozilla/5.0 AeroTwin Research', 'Referer': 'https://figshare.com/'}

# Priority downloads - small ones first, then queue big
downloads = [
    # SMALL - Download immediately (sync)
    ('synchronized_vibration_fault', 'LOAD_5KG_vibration.zip',
     'https://ndownloader.figshare.com/files/62827030', 27000000, 'SMALL'),
    ('synchronized_vibration_fault', 'NO_LOAD_vibration.zip', 
     'https://ndownloader.figshare.com/files/62827033', 26000000, 'SMALL'),
    # MEDIUM - SNU Code 1.2GB
    ('snu_planetary_gearbox', 'SNU_Gearbox_code.zip',
     'https://ndownloader.figshare.com/files/68833543', 1259000000, 'MEDIUM'),
    # LARGE - SNU Full 15.7GB (will take hours - background only)
    ('snu_planetary_gearbox', 'SNU_Gearbox_full.zip',
     'https://ndownloader.figshare.com/files/68834563', 16541000000, 'LARGE'),
]

def download_resume(folder, fname, url, total_target, priority):
    dest_dir = os.path.join(base, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest_file = os.path.join(dest_dir, fname)
    
    current_size = os.path.getsize(dest_file) if os.path.exists(dest_file) else 0
    
    if current_size >= total_target * 0.99:
        print('[DONE] ' + fname + ': Already complete (' + str(current_size//1048576) + 'MB)')
        return True
    
    headers = dict(H)
    if current_size > 0:
        headers['Range'] = 'bytes=' + str(current_size) + '-'
        print('[RESUME] ' + fname + ' from ' + str(current_size//1048576) + 'MB...')
    else:
        print('[START] ' + fname + ' (' + str(total_target//1048576) + 'MB expected)...')
    
    try:
        req = urllib.request.Request(url, headers=headers)
        mode = 'ab' if current_size > 0 else 'wb'
        with urllib.request.urlopen(req, timeout=300) as resp, open(dest_file, mode) as f:
            downloaded = current_size
            last_print = time.time()
            while True:
                chunk = resp.read(2 * 1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if time.time() - last_print > 5:
                    pct = (downloaded / total_target * 100) if total_target > 0 else 0
                    print('  ' + fname + ': ' + str(round(downloaded/1048576,1)) + 'MB (' + str(round(pct,1)) + '%)')
                    last_print = time.time()
        
        final = os.path.getsize(dest_file)
        print('[DONE] ' + fname + ': ' + str(final//1048576) + 'MB')
        return True
    except Exception as e:
        print('[ERROR] ' + fname + ': ' + str(e))
        return False

# Save metadata for SNU Gearbox
snu_meta = {
    'name': 'SNU Planetary Gearbox Dataset',
    'institution': 'Seoul National University',
    'figshare_id': 32025606,
    'total_size_gb': 16.6,
    'description': '16-channel vibration from planetary gearbox under multiple fault conditions',
    'relevance': 'HIGH - Gearbox fault diagnosis directly applicable to aero piston engine reduction gearbox',
    'files': {
        'code': 'SNU_Gearbox_code.zip (1.2GB)',
        'data': 'SNU_Gearbox_full.zip (15.7GB)'
    }
}
snu_dir = os.path.join(base, 'snu_planetary_gearbox')
os.makedirs(snu_dir, exist_ok=True)
json.dump(snu_meta, open(os.path.join(snu_dir, 'metadata.json'), 'w'), indent=2)
print('[META] SNU Gearbox metadata saved')

# Download small ones first
for folder, fname, url, target, priority in downloads:
    if priority in ('SMALL', 'MEDIUM'):
        download_resume(folder, fname, url, target, priority)

# LARGE one - just start it (will run as background task)
print('\n[QUEUING] SNU Full 15.7GB - starting...')
download_resume('snu_planetary_gearbox', 'SNU_Gearbox_full.zip',
                'https://ndownloader.figshare.com/files/68834563', 16541000000, 'LARGE')

print('\n=== DOWNLOADS COMPLETE ===')
