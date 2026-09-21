"""
AeroTwin MASTER DOWNLOAD — सगळं एकत्र
Run: python master_download.py
"""
import urllib.request, os, ssl, time, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
BASE = r'D:\AeroTwin_Datasets'

def dl(folder, fname, url, headers=None):
    d = os.path.join(BASE, folder); os.makedirs(d, exist_ok=True)
    dest = os.path.join(d, fname)
    h = {'User-Agent':'Mozilla/5.0 AeroTwin','Referer':'https://figshare.com/'}
    if headers: h.update(headers)
    cur = os.path.getsize(dest) if os.path.exists(dest) else 0
    if cur > 0: h['Range'] = 'bytes='+str(cur)+'-'
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=300, context=ctx) as r, open(dest,'ab' if cur else 'wb') as f:
            done = cur; t0 = time.time()
            while True:
                chunk = r.read(2*1024*1024)
                if not chunk: break
                f.write(chunk); done += len(chunk)
                if time.time()-t0 > 15:
                    print(f'  {fname[:30]}: {done//1048576}MB @ {(done-cur)/(time.time()-t0+1)/1048576:.1f}MB/s', flush=True)
                    t0=time.time(); cur=done
        sz = os.path.getsize(dest)
        print(f'[DONE] {fname}: {sz//1048576}MB', flush=True); return True
    except Exception as e:
        print(f'[ERR] {fname}: {str(e)[:60]}', flush=True); return False

def dl_zenodo_all(record_id, folder):
    """Download ALL files from a Zenodo record"""
    H = {'User-Agent':'Mozilla/5.0 AeroTwin'}
    try:
        req = urllib.request.Request(f'https://zenodo.org/api/records/{record_id}', headers=H)
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            data = json.loads(r.read())
        files = data.get('files', [])
        print(f'Zenodo {record_id}: {len(files)} files, {sum(f.get("size",0) for f in files)/1048576:.0f}MB total')
        for f in files:
            fname = f.get('key',''); fsize = f.get('size',0)
            furl = f.get('links',{}).get('self','')
            if not furl or fsize < 1024: continue
            dest = os.path.join(BASE, folder, fname)
            if os.path.exists(dest) and os.path.getsize(dest) >= fsize*0.99:
                print(f'[SKIP] {fname}'); continue
            print(f'[GET] {fname} ({fsize//1048576}MB)', flush=True)
            dl(folder, fname, furl, H)
    except Exception as e:
        print(f'Zenodo {record_id} error: {e}')

print('='*55)
print('  AeroTwin MASTER DOWNLOAD')
print('='*55)

# ── 1. UAV-FD Complete (838MB) ──────────────────────────
print('\n[1] UAV-FD Actuator Fault (838MB)...')
dl_zenodo_all(7648996, 'uavfd_actuator_fault_zenodo')

# ── 2. SNU Gearbox Full (15.7GB) ────────────────────────
print('\n[2] SNU Planetary Gearbox (15.7GB)...')
dl('snu_planetary_gearbox','SNU Planetary Gearbox Dataset.zip',
   'https://ndownloader.figshare.com/files/68834563',
   {'Referer':'https://figshare.com/articles/dataset/SNU_Planetary_Gearbox_Dataset/32025606'})

# ── 3. Paderborn via pip ─────────────────────────────────
print('\n[3] Paderborn: run separately → pip install paderborn-bearing')

# ── 4. Ottawa Bearing (Mendeley) ─────────────────────────
print('\n[4] Ottawa Bearing (variable speed)...')
ottawa_files = [
    ('Ottawa_Bearing.zip','https://data.mendeley.com/public-files/datasets/v43hmbwxpm/files/0e63e773-d6ce-4aba-9f7d-b36d67ea3ecd/file_downloaded'),
]
for fname, url in ottawa_files:
    dl('ottawa_bearing_variable_speed', fname, url)

# ── 5. Marine Engine (Mendeley) ──────────────────────────
print('\n[5] Marine Engine Fault...')
dl('marine_engine_fault','marine_data.zip',
   'https://data.mendeley.com/public-files/datasets/kp4pctpjhb/files/e3a6e7ac-2c8a-42f6-9fba-7a0059bedc95/file_downloaded')

# ── 6. HUST Bearing (Mendeley) ───────────────────────────
print('\n[6] HUST Bearing...')
dl('hust_bearing','HUST_bearing.zip',
   'https://data.mendeley.com/public-files/datasets/cbv7jyx4p9/files/4df88bc8-3cca-44de-b3e1-ea64a5a3ddd8/file_downloaded')

# ── 7. Gearbox PHM 2009 (alternate) ─────────────────────
print('\n[7] PHM Gearbox (alternate)...')
dl('phm_2009_gearbox','phm09.zip',
   'https://ndownloader.figshare.com/files/12912893')

# ── 8. VBL Vibration (Figshare) ──────────────────────────
print('\n[8] VBL Vibration Bearing...')
dl('vbl_vibration_fault','VBL_dataset.zip',
   'https://ndownloader.figshare.com/files/26379895')

print('\n'+'='*55)
print('  ALL DOWNLOADS COMPLETE!')
print('='*55)

import shutil
total = sum(os.path.getsize(os.path.join(r2,f))
            for fld in os.listdir(BASE)
            for r2,d,files in os.walk(os.path.join(BASE,fld))
            for f in files if os.path.isdir(os.path.join(BASE,fld)))
print(f'TOTAL on D: {total/1073741824:.2f} GB')
print(f'D: Free: {shutil.disk_usage("D:").free/1e9:.1f} GB')
