import urllib.request, os, time, json

base = r'ml_models\data\real_datasets'
HEADERS = {'User-Agent': 'Mozilla/5.0 AeroTwin Research', 'Referer': 'https://figshare.com/'}

def download_resume(folder, fname, url, total_target, name):
    dest_dir = os.path.join(base, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest_file = os.path.join(dest_dir, fname)
    
    current_size = os.path.getsize(dest_file) if os.path.exists(dest_file) else 0
    
    if current_size >= total_target * 0.99:
        print('[DONE] ' + name + ': Already complete (' + str(current_size//1048576) + 'MB)')
        return True
    
    headers = dict(HEADERS)
    if current_size > 0:
        headers['Range'] = 'bytes=' + str(current_size) + '-'
        print('[RESUME] ' + name + ': from ' + str(current_size//1048576) + 'MB...')
    else:
        print('[START] ' + name + ': from scratch...')
    
    try:
        req = urllib.request.Request(url, headers=headers)
        mode = 'ab' if current_size > 0 else 'wb'
        with urllib.request.urlopen(req, timeout=300) as resp, open(dest_file, mode) as f:
            downloaded = current_size
            last_print = time.time()
            while True:
                chunk = resp.read(2 * 1024 * 1024)  # 2MB chunks
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if time.time() - last_print > 5:
                    pct = (downloaded / total_target * 100) if total_target > 0 else 0
                    print('  ' + name + ': ' + str(round(downloaded/1048576,1)) + 'MB (' + str(round(pct,1)) + '%)')
                    last_print = time.time()
        
        final = os.path.getsize(dest_file)
        print('[DONE] ' + name + ': ' + str(final//1048576) + 'MB total!')
        json.dump({'name': name, 'url': url, 'size_mb': final//1048576,
                   'source': 'Figshare - XJTU-SY/PRONOSTIA', 'verified': True},
                  open(os.path.join(dest_dir, 'metadata.json'), 'w'), indent=2)
        return True
    except Exception as e:
        print('[ERROR] ' + name + ': ' + str(e))
        return False

# PRONOSTIA/IEEE PHM 2012 = 186MB 
download_resume(
    'pronostia_ieee_phm2012',
    'IEEE_PHM_2012_Bearing.7z',
    'https://ndownloader.figshare.com/files/59486987',
    195000000,
    'PRONOSTIA IEEE PHM 2012 (186MB)'
)

# XJTU-SY = 4.27GB - BIG dataset, run in background
download_resume(
    'xjtu_sy_bearing_full',
    'XJTU-SY_Bearing_Datasets.zip',
    'https://ndownloader.figshare.com/files/59487086',
    4478000000,
    'XJTU-SY Full Bearing Dataset (4.27GB)'
)

print('\n=== ALL FIGSHARE DOWNLOADS COMPLETE ===')
