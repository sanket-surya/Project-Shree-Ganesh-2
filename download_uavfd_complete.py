"""
UAV-FD Complete Download + Paderborn + More
Runs in background - all 30 UAV-FD files
"""
import urllib.request, os, ssl, time, json, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
H = {'User-Agent': 'Mozilla/5.0 AeroTwin'}

dest_dir = r'D:\AeroTwin_Datasets\uavfd_actuator_fault_zenodo'
os.makedirs(dest_dir, exist_ok=True)

def download_file(name, url, dest):
    cur = os.path.getsize(dest) if os.path.exists(dest) else 0
    h = dict(H)
    if cur > 0:
        h['Range'] = 'bytes=' + str(cur) + '-'
    try:
        req = urllib.request.Request(url, headers=h)
        mode = 'ab' if cur > 0 else 'wb'
        with urllib.request.urlopen(req, timeout=300, context=ctx) as r, open(dest, mode) as f:
            done = cur
            t0 = time.time()
            while True:
                chunk = r.read(2*1024*1024)
                if not chunk: break
                f.write(chunk)
                done += len(chunk)
                if time.time()-t0 > 10:
                    sp = (done-cur)/(time.time()-t0+1)/1048576
                    print('  ' + name[:30] + ': ' + str(done//1048576) + 'MB @ ' + str(round(sp,1)) + 'MB/s', flush=True)
                    t0 = time.time(); cur = done
        final = os.path.getsize(dest)
        print('[DONE] ' + name + ': ' + str(final//1048576) + 'MB', flush=True)
        return True
    except Exception as e:
        print('[ERR] ' + name + ': ' + str(e)[:50], flush=True)
        return False

# All UAV-FD files from Zenodo
print('=== FETCHING UAV-FD FILE LIST ===', flush=True)
try:
    req = urllib.request.Request('https://zenodo.org/api/records/7648996', headers=H)
    with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
        data = json.loads(r.read())
    files = data.get('files', [])
    print(f'Total files: {len(files)}, Size: {sum(f.get("size",0) for f in files)/1048576:.1f} MB', flush=True)
    
    for f in files:
        fname = f.get('key','')
        fsize = f.get('size',0)
        furl = f.get('links',{}).get('self','')
        if not furl or fsize < 1024: continue  # skip tiny
        dest = os.path.join(dest_dir, fname)
        cur = os.path.getsize(dest) if os.path.exists(dest) else 0
        if cur >= fsize * 0.99:
            print('[SKIP] ' + fname + ' already done', flush=True)
            continue
        print('[GET] ' + fname + ' (' + str(fsize//1048576) + 'MB)...', flush=True)
        download_file(fname, furl, dest)
except Exception as e:
    print('Failed to get file list: ' + str(e))

print()
print('=== UAV-FD COMPLETE! ===', flush=True)

# Print final total
total = sum(os.path.getsize(os.path.join(dest_dir,f)) for f in os.listdir(dest_dir) if os.path.isfile(os.path.join(dest_dir,f)))
print('UAV-FD Total: ' + str(round(total/1048576,1)) + 'MB')
