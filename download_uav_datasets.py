import urllib.request, ssl, os, json, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
H = {'User-Agent': 'Mozilla/5.0 AeroTwin', 'Referer': 'https://zenodo.org/'}

base = r'D:\AeroTwin_Datasets'

# ===== 1. UAV-FD: Actuator Fault (Zenodo 7648996) - 838 MB =====
print('=== Testing UAV-FD (838MB) ===')
uavfd_url = 'https://zenodo.org/api/records/7648996/files/NO_FAULT3.mat/content'
try:
    req = urllib.request.Request(uavfd_url, method='HEAD', headers=H)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
        sz = int(r.headers.get('Content-Length', 0))
        print('  HEAD OK! Size: ' + str(sz//1048576) + 'MB')
except Exception as e:
    print('  HEAD failed: ' + str(e))

# Get all files for UAV-FD
print('  Fetching all files...')
try:
    req = urllib.request.Request('https://zenodo.org/api/records/7648996', headers=H)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        data = json.loads(r.read())
    files = data.get('files', [])
    total_mb = sum(f.get('size', 0) for f in files)/1048576
    print('  Total files: ' + str(len(files)) + ' | Total: ' + str(round(total_mb, 1)) + 'MB')
    
    uavfd_dir = os.path.join(base, 'uavfd_actuator_fault_zenodo')
    os.makedirs(uavfd_dir, exist_ok=True)
    
    # Save metadata
    meta = {
        'name': 'UAV-FD Actuator Fault Detection Dataset',
        'source': 'Zenodo 7648996',
        'url': 'https://zenodo.org/records/7648996',
        'total_mb': round(total_mb, 1),
        'files_count': len(files),
        'description': 'Real multirotor drone actuator fault data - blade damage, motor faults',
        'relevance': 'HIGH - Real UAV propulsion fault data, directly relevant to MALE UAV engine health',
        'files': [{'name': f.get('key',''), 'size_mb': round(f.get('size',0)/1048576,1), 
                   'url': f.get('links',{}).get('self','')} for f in files]
    }
    json.dump(meta, open(os.path.join(uavfd_dir, 'metadata.json'), 'w'), indent=2)
    print('  Metadata saved!')
    
    # Download small files first (< 100MB each)
    for fi in files[:5]:
        fname = fi.get('key', '?')
        fsize = fi.get('size', 0)/1048576
        furl = fi.get('links', {}).get('self', '')
        dest = os.path.join(uavfd_dir, fname)
        
        if os.path.exists(dest) and os.path.getsize(dest) >= fi.get('size', 0) * 0.99:
            print('  [SKIP] ' + fname + ' already downloaded')
            continue
        
        print('  [DOWN] ' + fname + ' (' + str(round(fsize,1)) + 'MB)...')
        try:
            req = urllib.request.Request(furl, headers=H)
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp, open(dest, 'wb') as f:
                downloaded = 0
                last_p = time.time()
                while True:
                    chunk = resp.read(1024*1024)
                    if not chunk: break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if time.time() - last_p > 5:
                        print('    ' + str(downloaded//1048576) + 'MB...')
                        last_p = time.time()
            print('  [DONE] ' + fname + ': ' + str(os.path.getsize(dest)//1048576) + 'MB')
        except Exception as e:
            print('  [ERR] ' + fname + ': ' + str(e))

except Exception as e:
    print('  Error: ' + str(e))

# ===== 2. UAV Ground Telemetry CSV (Zenodo 19086193) - 5.7 MB =====
print('\n=== Downloading UAV Ground Telemetry CSV (5.7MB) ===')
tel_url = 'https://zenodo.org/api/records/19086193/files/uav_ground_telemetry.csv/content'
tel_dir = os.path.join(base, 'uav_ground_telemetry_zenodo')
os.makedirs(tel_dir, exist_ok=True)
try:
    req = urllib.request.Request(tel_url, headers=H)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp, open(os.path.join(tel_dir, 'uav_ground_telemetry.csv'), 'wb') as f:
        f.write(resp.read())
    sz = os.path.getsize(os.path.join(tel_dir, 'uav_ground_telemetry.csv'))/1048576
    print('  DONE! ' + str(round(sz,2)) + 'MB')
except Exception as e:
    print('  Error: ' + str(e))

# ===== 3. Save metadata for UAV Digital Model (9.2GB) =====
print('\n=== Saving metadata for UAV Digital Model (9.2GB) ===')
uav_dm_dir = os.path.join(base, 'uav_digital_model_zenodo')
os.makedirs(uav_dm_dir, exist_ok=True)
json.dump({
    'name': 'UAV Digital Model and Experimental Tests',
    'source': 'Zenodo 17457069',
    'url': 'https://zenodo.org/records/17457069',
    'total_gb': 9.0,
    'note': '9.2GB - digital model sim files + experimental data. Download manually if needed.',
    'relevance': 'MEDIUM - Digital twin model validation data for multirotor UAV'
}, open(os.path.join(uav_dm_dir, 'metadata.json'), 'w'), indent=2)
print('  Metadata saved!')

print('\n=== ALL DONE ===')
