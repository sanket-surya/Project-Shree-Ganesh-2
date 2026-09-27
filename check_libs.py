import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
try:
    import scipy
    print(f"scipy: {scipy.__version__} OK")
except: print("scipy: NOT installed")
try:
    import h5py
    print(f"h5py:  {h5py.__version__} OK")
except: print("h5py:  NOT installed")
try:
    import pyarrow
    print(f"pyarrow: {pyarrow.__version__} OK")
except: print("pyarrow: NOT installed")
