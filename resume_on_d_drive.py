import urllib.request, os, time, json

# NEW BASE = D Drive!
base = r'D:\AeroTwin_Datasets'
H = {'User-Agent': 'Mozilla/5.0 AeroTwin Research', 'Referer': 'https://figshare.com/articles/dataset/SNU_Planetary_Gearbox_Dataset/32025606'}

def download_resume(folder, fname, url, total_target, name):
    dest_dir = os.path.join(base, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest_file = os.path.join(dest_dir, fname)
    current_size = os.path.getsize(dest_file) if os.path.exists(dest_file) else 0
    
    if current_size >= total_target * 0.99:
        print(f'[DONE] {name}: Already complete ({current_size//1048576}MB)')
        return True
    
    headers = dict(H)
    if current_size > 0:
        headers['Range'] = f'bytes={current_size}-'
        print(f'[RESUME] {name}: from {current_size//1048576}MB / {total_target//1048576}MB ...')
    else:
        print(f'[START] {name}: 0 -> {total_target//1048576}MB ...')
    
    try:
        req = urllib.request.Request(url, headers=headers)
        mode = 'ab' if current_size > 0 else 'wb'
        with urllib.request.urlopen(req, timeout=300) as resp, open(dest_file, mode) as f:
            downloaded = current_size
            last_print = time.time()
            while True:
                chunk = resp.read(2 * 1024 * 1024)
                if not chunk: break
                f.write(chunk)
                downloaded += len(chunk)
                if time.time() - last_print > 5:
                    pct = (downloaded / total_target * 100)
                    mb_done = downloaded // 1048576
                    mb_total = total_target // 1048576
                    print('  ' + name + ': ' + str(mb_done) + 'MB / ' + str(mb_total) + 'MB (' + str(round(pct,1)) + '%)')
                    last_print = time.time()
        final = os.path.getsize(dest_file)
        print('[DONE] ' + name + ': ' + str(final//1048576) + 'MB complete!')
        return True
    except Exception as e:
        print('[ERROR] ' + name + ': ' + str(e))
        return False

print(f'Downloading to D:\\AeroTwin_Datasets')
print()

# XJTU-SY - already DONE, will skip
download_resume('xjtu_sy_bearing_full', 'XJTU-SY_Bearing_Datasets.zip',
    'https://ndownloader.figshare.com/files/59487086', 4478000000, 'XJTU-SY Full (4.27GB)')

# SNU Gearbox Code - already DONE, will skip
download_resume('snu_planetary_gearbox', 'SNU_Gearbox_code.zip',
    'https://ndownloader.figshare.com/files/68833543', 1259000000, 'SNU Gearbox Code (1.2GB)')

# SNU Gearbox Full (15.7GB) - Resume from 4824MB
# Fixed: Added correct Referer header to avoid 403 Forbidden
download_resume('snu_planetary_gearbox', 'SNU Planetary Gearbox Dataset.zip',
    'https://ndownloader.figshare.com/files/68834563', 16543309134, 'SNU Gearbox Full (15.4GB)')

print('\n=== ALL DONE ===')
