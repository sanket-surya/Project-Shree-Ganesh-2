import urllib.request
import os

urls = {
    "train_FD001.txt": "https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMAPSSData/train_FD001.txt",
    "train_FD002.txt": "https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMAPSSData/train_FD002.txt",
    "RUL_FD001.txt":   "https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMAPSSData/RUL_FD001.txt",
    "RUL_FD002.txt":   "https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMAPSSData/RUL_FD002.txt",
    "test_FD001.txt":  "https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMAPSSData/test_FD001.txt",
    "test_FD002.txt":  "https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMAPSSData/test_FD002.txt",
}

os.makedirs("ml_models/data/cmapss", exist_ok=True)

for fname, url in urls.items():
    dest = f"ml_models/data/cmapss/{fname}"
    print(f"Downloading {fname}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, dest)
        size_kb = os.path.getsize(dest) / 1024
        print(f"OK ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"FAILED: {e}")

print("\nDone!")
