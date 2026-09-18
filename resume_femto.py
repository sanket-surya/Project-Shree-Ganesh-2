import urllib.request, os, zipfile, sys, time

femto_path = r'ml_models\data\real_datasets\femto_bearing_vibration\femto_bearing.zip'
url = 'https://phm-datasets.s3.amazonaws.com/NASA/10.+FEMTO+Bearing.zip'
total_target = 1157035288

current_size = os.path.getsize(femto_path) if os.path.exists(femto_path) else 0
print(f'Starting from offset: {current_size} bytes ({current_size/1048576:.2f} MB / {total_target/1048576:.2f} MB)')

if current_size >= total_target:
    print('Already complete!')
else:
    headers = {'User-Agent': 'Mozilla/5.0 AeroTwin'}
    if current_size > 0:
        headers['Range'] = f'bytes={current_size}-'
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp, open(femto_path, 'ab' if current_size > 0 else 'wb') as f:
        downloaded = current_size
        last_print = time.time()
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if time.time() - last_print > 3:
                pct = (downloaded / total_target) * 100
                print(f'Progress: {downloaded/1048576:.1f} MB / {total_target/1048576:.1f} MB ({pct:.1f}%)')
                last_print = time.time()

print(f'Download complete! Total size: {os.path.getsize(femto_path)/1048576:.2f} MB')

try:
    with zipfile.ZipFile(femto_path, 'r') as zf:
        print(f'ZIP integrity verified! Total files inside: {len(zf.namelist())}')
except Exception as e:
    print(f'ZIP integrity check failed: {e}')
