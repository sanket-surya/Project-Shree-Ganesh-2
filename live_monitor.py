# -*- coding: utf-8 -*-
"""
AeroTwin LIVE Monitor — Press Ctrl+C to stop
Run: python live_monitor.py
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os, time, shutil

BASE = 'D:/AeroTwin_Datasets'

TARGETS = [
    ('SNU Gearbox',       'snu_planetary_gearbox',  15776),
    ('N-CMAPSS',          'nasa_ncmapss',            15030),
    ('RflyMAD Real',      'rflymad',                 19183),
    ('RflyMAD-HIL',       'rflymad_hil',             23987),
    ('RflyMAD-SIL',       'rflymad_sil',             22676),
    ('RflyMAD+ROS',       'rflymad_withros',         15630),
    ('UAV-FD',            'uavfd_actuator_fault_zenodo', 838),
    ('IMS Bearing',       'ims_nasa',                6000),
]

DONE = [
    ('FEMTO Bearing',     'femto_bearing_vibration'),
    ('XJTU-SY',          'xjtu_sy_bearing_full'),
    ('ALFA UAV',          'alfa_uav_engine_failure'),
    ('Paderborn',         'pedrobearing'),
    ('PHM 2024',          'phm_2024'),
    ('MFPT',              'mfpt_bearing'),
    ('C-MAPSS',           'nasa_cmapss'),
    ('Marine Engine',     'marine_engine_fault'),
    ('NASA IGBT',         'nasa_igbt_aging'),
    ('UAV-FD',            'uavfd_actuator_fault_zenodo'),
]

prev = {}

def get_mb(folder):
    fp = os.path.join(BASE, folder)
    if not os.path.exists(fp): return 0
    return sum(os.path.getsize(os.path.join(r,f))
               for r,d,files in os.walk(fp) for f in files) / 1048576

def bar(pct, w=20):
    f = int(pct/100*w)
    return '█'*f + '░'*(w-f)

while True:
    os.system('cls')
    now = time.strftime('%H:%M:%S')

    print('╔══════════════════════════════════════════════════════╗')
    print('║   🔥 AeroTwin Download Monitor  |  ' + now + '         ║')
    print('╠══════════════════════════════════════════════════════╣')
    print('║  ⬇️  DOWNLOADING                                      ║')
    print('╠══════════════════════════════════════════════════════╣')

    total_down = 0
    total_tgt = 0
    for name, folder, target_mb in TARGETS:
        mb = get_mb(folder)
        pct = min(mb/target_mb*100, 100)
        spd = (mb - prev.get(folder, mb)) / 10
        prev[folder] = mb
        eta_s = (target_mb-mb)/max(spd,0.05)
        eta = f'{int(eta_s//3600)}h{int((eta_s%3600)//60)}m' if spd > 0.05 else '--'
        if pct >= 99:
            status = '✅ DONE'
        else:
            status = f'{spd:.1f}MB/s ETA:{eta}'
        b = bar(pct)
        line = f'║ {name[:14]:<14} {b} {pct:5.1f}% {status[:14]}'
        print(line.ljust(54) + '║')
        total_down += mb
        total_tgt += target_mb

    print('╠══════════════════════════════════════════════════════╣')
    print('║  ✅ ALREADY DONE                                      ║')
    print('╠══════════════════════════════════════════════════════╣')

    done_total = 0
    for name, folder in DONE:
        mb = get_mb(folder)
        done_total += mb
        if mb > 1:
            print(f'║  ✅ {name:<18} {mb:>7.0f} MB'.ljust(54) + '║')

    total_all = done_total + total_down
    free = shutil.disk_usage('D:/').free / 1e9
    print('╠══════════════════════════════════════════════════════╣')
    print(f'║  💾 TOTAL on D:   {total_all/1024:>6.1f} GB  |  Free: {free:.0f} GB'.ljust(54) + '║')
    print(f'║  📦 Active Queue: {total_down/1024:>6.1f}/{total_tgt/1024:.0f} GB'.ljust(54) + '║')
    print('╚══════════════════════════════════════════════════════╝')
    print('  Refreshing every 10s... Ctrl+C to stop')

    time.sleep(10)
