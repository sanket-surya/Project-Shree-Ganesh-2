import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

BASE = r'C:\Users\Asus\Desktop\Project Shree Ganesh 2'

def sz(path):
    try:
        total = 0
        if os.path.isfile(path): return os.path.getsize(path)
        for r,d,fs in os.walk(path):
            for f in fs:
                try: total += os.path.getsize(os.path.join(r,f))
                except: pass
        return total
    except: return 0

def fmt(b):
    if b >= 1024**3: return f"{b/1024**3:.1f}GB"
    if b >= 1024**2: return f"{b/1024**2:.0f}MB"
    if b >= 1024: return f"{b/1024:.0f}KB"
    return f"{b}B"

def count_files(path):
    try:
        return sum(len(fs) for _,_,fs in os.walk(path))
    except: return 0

print("=" * 70)
print("  AEROTWIN PROJECT — COMPLETE SCAN")
print("=" * 70)

# Top-level structure
print("\n[1] TOP-LEVEL FOLDERS:")
entries = []
for name in sorted(os.listdir(BASE)):
    fp = os.path.join(BASE, name)
    if os.path.isdir(fp) and not name.startswith('.'):
        s = sz(fp)
        fc = count_files(fp)
        entries.append((name, s, fc))

for name, s, fc in sorted(entries, key=lambda x:-x[1]):
    print(f"  {name:<40} {fmt(s):>8}  ({fc:,} files)")

print(f"\n[2] ML MODELS STATUS:")
ml = os.path.join(BASE, 'ml_models')
for name in sorted(os.listdir(ml)):
    fp = os.path.join(ml, name)
    if os.path.isfile(fp):
        print(f"  [FILE] {name:<45} {fmt(sz(fp)):>8}")
    elif os.path.isdir(fp):
        fc = count_files(fp)
        print(f"  [DIR]  {name:<45} {fmt(sz(fp)):>8}  ({fc:,} files)")

print(f"\n[3] ML WEIGHTS CHECK:")
weights = os.path.join(ml, 'weights')
if os.path.exists(weights):
    for f in sorted(os.listdir(weights)):
        fp = os.path.join(weights, f)
        print(f"  {f:<50} {fmt(sz(fp)):>8}")
else:
    print("  [MISSING] ml_models/weights/ folder!")

print(f"\n[4] EXPERT DATASETS CHECK:")
experts = os.path.join(ml, 'data', 'experts')
if os.path.exists(experts):
    for f in sorted(os.listdir(experts)):
        fp = os.path.join(experts, f)
        if f.endswith('.parquet'):
            import pandas as pd
            try:
                df = pd.read_parquet(fp)
                print(f"  {f:<40} {fmt(sz(fp)):>8}  rows:{len(df):,}  cols:{len(df.columns)}")
            except:
                print(f"  {f:<40} {fmt(sz(fp)):>8}  [READ ERROR]")
        else:
            print(f"  {f:<40} {fmt(sz(fp)):>8}")
else:
    print("  [MISSING] ml_models/data/experts/")

print(f"\n[5] BACKEND STATUS:")
backend = os.path.join(BASE, 'backend')
for f in sorted(os.listdir(backend)):
    fp = os.path.join(backend, f)
    if f.endswith('.py'):
        lines = open(fp, encoding='utf-8', errors='replace').readlines()
        print(f"  {f:<40} {len(lines):>5} lines  {fmt(sz(fp)):>8}")

print(f"\n[6] FRONTEND STATUS:")
fe = os.path.join(BASE, 'frontend', 'src')
if os.path.exists(fe):
    comps = os.path.join(fe, 'components')
    jsx_files = [f for f in os.listdir(comps) if f.endswith('.jsx')]
    print(f"  Components: {len(jsx_files)} JSX files")
    for f in sorted(jsx_files):
        fp = os.path.join(comps, f)
        lines = open(fp, encoding='utf-8', errors='replace').readlines()
        print(f"    {f:<45} {len(lines):>4} lines")

print(f"\n[7] KEY PYTHON SCRIPTS (root):")
for f in sorted(os.listdir(BASE)):
    fp = os.path.join(BASE, f)
    if f.endswith('.py') and os.path.isfile(fp):
        lines = open(fp, encoding='utf-8', errors='replace').readlines()
        print(f"  {f:<50} {len(lines):>5} lines")

print(f"\n[8] EMBEDDED/CPP:")
cpp = os.path.join(BASE, 'embedded', 'cpp')
if os.path.exists(cpp):
    cpp_files = [f for f in os.listdir(cpp) if f.endswith(('.cpp','.hpp','.h'))]
    print(f"  {len(cpp_files)} C++ files")
    for f in sorted(cpp_files):
        fp = os.path.join(cpp, f)
        lines = open(fp, encoding='utf-8', errors='replace').readlines()
        print(f"    {f:<45} {len(lines):>4} lines")

print("\n" + "=" * 70)
print("  SCAN COMPLETE")
print("=" * 70)
