"""
AeroTwin Simple Download Monitor
Run: python -u monitor.py
Press Ctrl+C to stop
"""
import os, time, shutil, sys
sys.stdout.reconfigure(line_buffering=True)

BASE = 'D:/AeroTwin_Datasets'

ACTIVE = [
    # Already running
    ('SNU Gearbox',   'snu_planetary_gearbox/SNU Planetary Gearbox Dataset.zip', 15776),
    ('N-CMAPSS',      'nasa_ncmapss/N-CMAPSS_DS02.zip',                          15030),
    ('RflyMAD-HIL',   'rflymad_hil',                                             23987),
    ('RflyMAD-SIL',   'rflymad_sil',                                             22676),
    ('RflyMAD+ROS',   'rflymad_withros',                                         15630),
    # New datasets
    ('HUST Bearing',  'hust_bearing',                                              665),
    ('Machinery FDB', 'machinery_fault_db',                                      12569),
    ('Paderborn FULL','paderborn_full',                                           9239),
    ('Rotating Shaft','rotating_shaft_vibration',                                 2686),
]

def get_mb(rel):
    p = os.path.join(BASE, rel)
    if os.path.isfile(p):
        return os.path.getsize(p) / 1048576
    elif os.path.isdir(p):
        return sum(os.path.getsize(os.path.join(r,f))
                   for r,d,fs in os.walk(p) for f in fs) / 1048576
    return 0.0

def bar(pct, w=20):
    f = int(pct/100*w)
    return '#'*f + '-'*(w-f)

prev = {}
print('AeroTwin Download Monitor — refresh every 30s\n' + '='*55)

while True:
    now = time.strftime('%H:%M:%S')
    total_disk = sum(
        get_mb(d) for d in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, d))
    )
    free = shutil.disk_usage('D:/').free / 1e9
    
    print(f'\n[{now}] Total: {total_disk/1024:.1f}GB on D:  |  Free: {free:.0f}GB')
    print('-'*55)
    
    baki_total = 0
    for name, rel, target in ACTIVE:
        mb = get_mb(rel)
        pct = min(mb/target*100, 100)
        spd = (mb - prev.get(name, mb)) / 30
        prev[name] = mb
        baki = max(0, target - mb)
        baki_total += baki
        
        if pct >= 99:
            print(f'  {name:<14} [{bar(100)}] DONE!  ')
        else:
            eta = int(baki / max(spd, 0.05) / 60) if spd > 0.05 else 999
            eta_str = f'{eta}min' if eta < 999 else '...'
            sp_str = f'{spd:.1f}MB/s' if spd > 0.05 else 'idle'
            print(f'  {name:<14} [{bar(pct)}] {pct:5.1f}%  {mb:.0f}/{target}MB  {sp_str}  ETA:{eta_str}')
    
    print(f'\n  Still coming: {baki_total/1024:.1f} GB more')
    print('='*55)
    
    time.sleep(30)
