import urllib.request, os, json, zipfile

base = r'ml_models\data\real_datasets'
HEADERS = {'User-Agent': 'Mozilla/5.0 AeroTwin Research'}

# ALL confirmed/known NASA PCoE S3 dataset URLs - testing which ones work
nasa_datasets = [
    # Already downloaded (skip if exists)
    ('nasa_cmapss', 'NASA C-MAPSS Turbofan', 
     'https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip', 12),
    ('nasa_battery', 'NASA Battery',
     'https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip', 200),
    ('femto_bearing_vibration', 'NASA FEMTO Bearing',
     'https://phm-datasets.s3.amazonaws.com/NASA/10.+FEMTO+Bearing.zip', 1100),
    # NEW ones to try
    ('nasa_ims_bearing', 'NASA IMS Bearing (New)',
     'https://phm-datasets.s3.amazonaws.com/NASA/3.+IMS+Bearing.zip', 300),
    ('nasa_milling', 'NASA Milling',
     'https://phm-datasets.s3.amazonaws.com/NASA/2.+Milling.zip', 50),
    ('nasa_igbt_aging', 'NASA IGBT Accelerated Aging',
     'https://phm-datasets.s3.amazonaws.com/NASA/8.+IGBT+Accelerated+Aging.zip', 50),
    ('nasa_hirf_generator', 'NASA Generator (GE-UTK)',
     'https://phm-datasets.s3.amazonaws.com/GE-UTK/FMCRD_Data.zip', 50),
    ('nasa_turbofan_v2', 'NASA Turbofan V2 (N-CMAPSS)',
     'https://phm-datasets.s3.amazonaws.com/NASA/N-CMAPSS_DS01-005.zip', 1000),
    ('nasa_run_to_fail', 'NASA Run-to-Failure (HIRF)',
     'https://phm-datasets.s3.amazonaws.com/NASA/7.+HIRF+Susceptibility.zip', 100),
    ('nasa_small_sat', 'NASA Small Satellite Power',
     'https://phm-datasets.s3.amazonaws.com/NASA/9.+Small+Satellite+Power+Faults.zip', 50),
    ('nasa_algae', 'NASA Algae Raceway (Biofuel engine)',
     'https://phm-datasets.s3.amazonaws.com/NASA/1.+Algae+Raceway.zip', 50),
]

print('=== TESTING NASA S3 URLS ===\n')
accessible = []

for folder, name, url, est_mb in nasa_datasets:
    dest = os.path.join(base, folder)
    
    # Check if already downloaded
    main_zip = os.path.join(dest, os.path.basename(url).replace('+', ' '))
    existing_zips = []
    if os.path.exists(dest):
        existing_zips = [f for f in os.listdir(dest) if f.endswith('.zip')]
    
    if existing_zips:
        sz = os.path.getsize(os.path.join(dest, existing_zips[0]))
        print(f'[SKIP] {name}: Already downloaded ({sz//1048576}MB)')
        continue
    
    # Test URL
    try:
        req = urllib.request.Request(url, method='HEAD', headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            size = int(resp.headers.get('Content-Length', 0))
            print(f'[OK]   {name}: {size//1048576}MB accessible -> {url}')
            accessible.append((folder, name, url, size))
    except urllib.error.HTTPError as e:
        print(f'[FAIL] {name}: HTTP {e.code} -> {url}')
    except Exception as e:
        print(f'[ERR]  {name}: {e}')

# Save accessible list for download
with open('nasa_accessible.json', 'w') as f:
    json.dump(accessible, f, indent=2)

print(f'\n=== FOUND {len(accessible)} NEW ACCESSIBLE DATASETS ===')
for folder, name, url, size in accessible:
    print(f'  {name}: {size//1048576}MB')
