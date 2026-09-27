import sys, subprocess, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Python Libraries Check ─────────────────────────────────────────────────────
REQUIRED = {
    'fastapi':       '0.115.0',
    'uvicorn':       '0.30.0',
    'xgboost':       '2.1.0',
    'scikit-learn':  '1.5.0',
    'numpy':         '1.26.0',
    'pandas':        '2.2.0',
    'scipy':         '1.13.0',
    'joblib':        '1.4.0',
    'pyarrow':       '16.0.0',
    'h5py':          '3.11.0',
    'pydantic':      '2.7.0',
    'optuna':        '3.6.0',
    'python-multipart': '0.0.9',
    'aiofiles':      '23.2.1',
}

print("=" * 65)
print("  PYTHON LIBRARY AUDIT")
print("=" * 65)
print(f"{'Library':<22} {'Installed':>12} {'Min Required':>14} {'Status':>8}")
print("-" * 65)

to_upgrade = []
to_install = []

for lib, min_ver in REQUIRED.items():
    try:
        result = subprocess.run(
            [sys.executable, '-c', f'import importlib.metadata; print(importlib.metadata.version("{lib}"))'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            installed = result.stdout.strip()
            inst_parts = [int(x) for x in installed.split('.')[:3] if x.isdigit()]
            min_parts  = [int(x) for x in min_ver.split('.')[:3]   if x.isdigit()]
            # Pad to same length
            while len(inst_parts) < 3: inst_parts.append(0)
            while len(min_parts)  < 3: min_parts.append(0)
            ok = inst_parts >= min_parts
            status = 'OK' if ok else 'OLD'
            print(f"  {lib:<22} {installed:>12} {min_ver:>14}  {'✅' if ok else '⚠️ '}")
            if not ok:
                to_upgrade.append(lib)
        else:
            print(f"  {lib:<22} {'NOT FOUND':>12} {min_ver:>14}  ❌")
            to_install.append(lib)
    except Exception as e:
        print(f"  {lib:<22} {'ERROR':>12} {min_ver:>14}  ❌ {e}")
        to_install.append(lib)

print()
if to_upgrade:
    print(f"  ⚠️  Upgrade needed: {', '.join(to_upgrade)}")
if to_install:
    print(f"  ❌ Install needed:  {', '.join(to_install)}")
if not to_upgrade and not to_install:
    print("  ✅ All libraries up to date!")

# ── NPM Package Check ──────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  NPM PACKAGE AUDIT")
print("=" * 65)
try:
    result = subprocess.run(
        ['npm', 'outdated', '--json'],
        capture_output=True, text=True, cwd=r'C:\Users\Asus\Desktop\Project Shree Ganesh 2\frontend',
        timeout=30
    )
    if result.stdout.strip():
        outdated = json.loads(result.stdout)
        if outdated:
            print(f"  {'Package':<30} {'Current':>10} {'Latest':>10}")
            print("-" * 55)
            for pkg, info in outdated.items():
                print(f"  {pkg:<30} {info.get('current','?'):>10} {info.get('latest','?'):>10}  ⚠️")
        else:
            print("  ✅ All npm packages up to date!")
    else:
        print("  ✅ All npm packages up to date!")
except Exception as e:
    print(f"  Error checking npm: {e}")

print("\n" + "=" * 65)
print(f"  UPGRADE COMMAND:")
if to_upgrade:
    print(f"  pip install --upgrade {' '.join(to_upgrade)}")
if to_install:
    print(f"  pip install {' '.join(to_install)}")
print("=" * 65)
