import os, time, sys

sys.stdout.reconfigure(encoding='utf-8')

base = r'D:\AeroTwin_Datasets'

checks = [
    ('xjtu_sy_bearing_full', 'XJTU-SY_Bearing_Datasets.zip', 4271),
    ('snu_planetary_gearbox', 'SNU_Gearbox_full.zip', 15776),
    ('snu_planetary_gearbox', 'SNU_Gearbox_code.zip', 1201),
]

os.system('cls')

print('=' * 65)
print('  AeroTwin - Live Download Monitor  (Ctrl+C to stop)')
print('=' * 65)

while True:
    print('\033[4;0H', end='')  # Move cursor to row 4
    
    total_done = 0
    total_target = 0
    
    for folder, fname, target_mb in checks:
        fp = os.path.join(base, folder, fname)
        if os.path.exists(fp):
            sz = os.path.getsize(fp) / 1048576
            pct = min(sz / target_mb * 100, 100)
            filled = int(pct / 5)
            bar = '#' * filled + '-' * (20 - filled)
            status = 'DONE!' if pct >= 99.5 else 'downloading...'
            line = f'  {fname[:28]:<28} {sz:>7.1f}/{target_mb} MB [{bar}] {pct:5.1f}% {status}'
            total_done += sz
            total_target += target_mb
        else:
            line = f'  {fname[:28]:<28}    0.0/{target_mb} MB [--------------------]   0.0% not started'
        
        print(line)
    
    # Also show completed ones
    completed = [
        ('femto_bearing_vibration', 'femto_bearing.zip', 1103),
        ('nasa_igbt_aging', '8._IGBT_Accelerated_Aging.zip', 229),
        ('pronostia_ieee_phm2012', 'IEEE_PHM_2012_Bearing.7z', 186),
        ('nasa_battery', 'battery.zip', 200),
    ]
    print()
    print('  --- Completed ---')
    for folder, fname, target_mb in completed:
        fp = os.path.join(base, folder, fname)
        if os.path.exists(fp):
            sz = os.path.getsize(fp) / 1048576
            print(f'  {fname[:28]:<28} {sz:>7.1f} MB  [####################] DONE!')
    
    # Grand total
    total_all = 0
    for folder in os.listdir(base):
        fp = os.path.join(base, folder)
        if os.path.isdir(fp):
            for r, d, files in os.walk(fp):
                for f in files:
                    try:
                        total_all += os.path.getsize(os.path.join(r, f))
                    except:
                        pass
    
    print()
    print(f'  GRAND TOTAL ON DISK: {total_all/1073741824:.2f} GB')
    print(f'  Last refresh: {time.strftime("%H:%M:%S")}  (refreshing every 5s)')
    print('=' * 65)
    
    time.sleep(5)
