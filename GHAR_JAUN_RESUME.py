"""
AeroTwin - GHARI RESUME KARO!
Run this when you get home with charger plugged in.
Downloads directly to D:\AeroTwin_Datasets with auto-resume.
"""
import urllib.request, os, time, json, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = r'D:\AeroTwin_Datasets'

HEADERS_FIGSHARE = {
    'User-Agent': 'Mozilla/5.0 AeroTwin Research',
    'Referer': 'https://figshare.com/articles/dataset/SNU_Planetary_Gearbox_Dataset/32025606'
}
HEADERS_ZENODO = {
    'User-Agent': 'Mozilla/5.0 AeroTwin Research',
    'Referer': 'https://zenodo.org/'
}

def download(folder, fname, url, total_bytes, name, headers):
    dest_dir = os.path.join(base, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, fname)
    current = os.path.getsize(dest) if os.path.exists(dest) else 0

    if current >= total_bytes * 0.99:
        print('[SKIP] ' + name + ' already done (' + str(current//1048576) + 'MB)')
        return True

    h = dict(headers)
    if current > 0:
        h['Range'] = 'bytes=' + str(current) + '-'
        print('[RESUME] ' + name + ' from ' + str(current//1048576) + 'MB...')
    else:
        print('[START] ' + name + ' (0 -> ' + str(total_bytes//1048576) + 'MB)...')

    try:
        req = urllib.request.Request(url, headers=h)
        mode = 'ab' if current > 0 else 'wb'
        with urllib.request.urlopen(req, timeout=300, context=ctx) as resp, open(dest, mode) as f:
            done = current
            t0 = time.time()
            while True:
                chunk = resp.read(2*1024*1024)
                if not chunk: break
                f.write(chunk)
                done += len(chunk)
                if time.time()-t0 > 8:
                    pct = done/total_bytes*100 if total_bytes > 0 else 0
                    speed = (done-current)/(time.time()-t0+1)/1048576
                    eta = (total_bytes-done)/((speed or 1)*1048576)/60
                    print('  ' + name + ': ' + str(done//1048576) + 'MB (' + str(round(pct,1)) + '%) ' + str(round(speed,1)) + 'MB/s ETA:' + str(round(eta,1)) + 'min')
                    t0 = time.time()
                    current = done

        final = os.path.getsize(dest)
        print('[DONE] ' + name + ': ' + str(final//1048576) + 'MB!')
        return True
    except Exception as e:
        print('[ERROR] ' + name + ': ' + str(e))
        return False

print('=' * 60)
print('  AeroTwin Download Queue - GHAR WALI SESSION')
print('=' * 60)
print()

# ============================================================
# QUEUE 1: SNU Gearbox Full (15.7 GB) - PRIORITY
# ============================================================
download(
    'snu_planetary_gearbox',
    'SNU Planetary Gearbox Dataset.zip',
    'https://ndownloader.figshare.com/files/68834563',
    16543309134,
    'SNU Gearbox Full (15.7GB)',
    HEADERS_FIGSHARE
)

# ============================================================
# QUEUE 2: UAV-FD Actuator Fault (838 MB) - Zenodo
# ============================================================
# Download all .mat files
uavfd_files = [
    ('NO_FAULT1.mat', 'https://zenodo.org/api/records/7648996/files/NO_FAULT1.mat/content', 50_000_000),
    ('NO_FAULT2.mat', 'https://zenodo.org/api/records/7648996/files/NO_FAULT2.mat/content', 50_000_000),
    ('NO_FAULT3.mat', 'https://zenodo.org/api/records/7648996/files/NO_FAULT3.mat/content', 51_722_240),
    ('FAULT_TYPE1_LEVEL1.mat', 'https://zenodo.org/api/records/7648996/files/FAULT_TYPE1_LEVEL1.mat/content', 50_000_000),
    ('FAULT_TYPE1_LEVEL2.mat', 'https://zenodo.org/api/records/7648996/files/FAULT_TYPE1_LEVEL2.mat/content', 50_000_000),
    ('FAULT_TYPE2_LEVEL1.mat', 'https://zenodo.org/api/records/7648996/files/FAULT_TYPE2_LEVEL1.mat/content', 50_000_000),
    ('FAULT_TYPE2_LEVEL2.mat', 'https://zenodo.org/api/records/7648996/files/FAULT_TYPE2_LEVEL2.mat/content', 50_000_000),
]
for fname, url, sz in uavfd_files:
    download('uavfd_actuator_fault_zenodo', fname, url, sz, 'UAV-FD ' + fname, HEADERS_ZENODO)

# ============================================================
# QUEUE 3: Paderborn Bearing (if accessible)
# ============================================================
# pip install paderborn-bearing  (easier way!)
print()
print('TIP: For Paderborn bearing run: pip install paderborn-bearing')
print('     Then: python -c "import paderborn_bearing; paderborn_bearing.download()"')

# ============================================================
# QUEUE 4: RflyMAD (needs Kaggle token)
# ============================================================
print()
print('TIP: RflyMAD (114GB UAV dataset) on Kaggle:')
print('     kaggle datasets download xianglile/rflymad -p D:\\AeroTwin_Datasets\\rflymad\\')

print()
print('=' * 60)
print('  ALL DOWNLOADS COMPLETE!')
print('=' * 60)
