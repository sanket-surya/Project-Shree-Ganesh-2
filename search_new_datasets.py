import subprocess
import sys
import os

queries = [
    'uav telemetry',
    'flight telemetry',
    'piston engine',
    'engine fault',
    'engine vibration',
    'aircraft telemetry',
    'engine predictive maintenance',
    'uav flight',
    'bearing fault',
    'rotax'
]

print("=== SEARCHING KAGGLE FOR IN-DOMAIN DATASETS ===")
already = set(os.listdir(r'D:/AeroTwin_Datasets'))

found_candidates = []

for q in queries:
    cmd = [sys.executable, '-m', 'kaggle', 'datasets', 'list', '-s', q]
    res = subprocess.run(cmd, capture_output=True, text=True)
    lines = res.stdout.strip().split('\n')
    print(f"\n[QUERY]: '{q}' ({len(lines)-2} results):")
    for line in lines[2:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3:
            ref = parts[0]
            # check if ref or folder already exists
            short_name = ref.split('/')[-1]
            size = parts[-5] if len(parts) >= 6 else 'N/A'
            # Let's get title
            title_chunk = line[len(ref):].strip()
            print(f"  * {ref:<45} | {title_chunk[:60]}")
            found_candidates.append((ref, title_chunk[:50]))
