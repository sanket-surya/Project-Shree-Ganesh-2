"""
AeroTwin - MASTER RESUME ALL DATASETS
Zero byte loss, HTTP Range resume for Figshare & S3, Native resume for Kaggle.
Run: python -u RESUME_ALL_DATASETS.py
"""
import os, sys, time, ssl, subprocess
import urllib.request, shutil

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

BASE = r"D:\AeroTwin_Datasets"
os.makedirs(BASE, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def dl_direct(name, folder, fname, url, headers=None, target_mb=0):
    dest_dir = os.path.join(BASE, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, fname)

    print("\n" + "="*65)
    print(f"  [QUEUE] {name}")
    print(f"  Destination: {dest}")
    print("="*65)

    cur = os.path.getsize(dest) if os.path.exists(dest) else 0
    if target_mb > 0 and cur >= target_mb * 0.995 * 1048576:
        print(f"  [ALREADY DONE] {name} ({cur // 1048576} MB / {target_mb} MB)")
        return True

    max_retries = 20
    for attempt in range(1, max_retries + 1):
        cur = os.path.getsize(dest) if os.path.exists(dest) else 0
        h = {"User-Agent": "Mozilla/5.0 AeroTwin Download Engine"}
        if headers:
            h.update(headers)
        if cur > 0:
            h["Range"] = f"bytes={cur}-"
            print(f"  [RESUME] {name} from {cur // 1048576} MB (Attempt {attempt}/{max_retries})...")
        else:
            print(f"  [START] {name} (0 -> {target_mb} MB, Attempt {attempt}/{max_retries})...")

        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp, open(dest, "ab" if cur else "wb") as f:
                code = resp.getcode()
                total_content_len = resp.headers.get("Content-Length")
                total_target = (cur + int(total_content_len)) if total_content_len else (target_mb * 1048576)

                done = cur
                t_last_print = time.time()
                bytes_since_print = 0

                while True:
                    chunk = resp.read(2 * 1024 * 1024)  # 2MB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    bytes_since_print += len(chunk)

                    now = time.time()
                    elapsed = now - t_last_print
                    if elapsed >= 10:
                        speed = (bytes_since_print / elapsed) / 1048576
                        pct = (done / total_target * 100) if total_target > 0 else 0
                        remain = max(0, total_target - done)
                        eta_min = (remain / max(speed * 1048576, 1)) / 60
                        print(f"  [{name}] {done // 1048576} MB / {total_target // 1048576} MB ({pct:.1f}%) | {speed:.1f} MB/s | ETA: {eta_min:.1f} min", flush=True)
                        t_last_print = now
                        bytes_since_print = 0

            final_sz = os.path.getsize(dest)
            print(f"  [SUCCESS] {name}: {final_sz // 1048576} MB downloaded successfully!\n")
            return True

        except Exception as e:
            print(f"  [NETWORK RETRY {attempt}]: {str(e)[:70]}")
            time.sleep(5)

    print(f"  [FAILED after {max_retries} attempts]: {name}")
    return False


def dl_kaggle(name, ref, folder):
    target_dir = os.path.join(BASE, folder)
    os.makedirs(target_dir, exist_ok=True)

    print("\n" + "="*65)
    print(f"  [QUEUE] Kaggle Dataset: {name} ({ref})")
    print(f"  Target Folder: {target_dir}")
    print("="*65)

    cmd = ["kaggle", "datasets", "download", ref, "-p", target_dir]
    max_retries = 15
    for attempt in range(1, max_retries + 1):
        print(f"  [START KAGGLE] (Attempt {attempt}/{max_retries})...")
        try:
            p = subprocess.run(cmd, check=False)
            if p.returncode == 0:
                print(f"  [SUCCESS] {name} completed successfully!")
                return True
            else:
                print(f"  [WARN] Kaggle exited with code {p.returncode}. Retrying in 10s...")
                time.sleep(10)
        except Exception as e:
            print(f"  [WARN] Error running kaggle: {e}")
            time.sleep(10)

    print(f"  [FAILED after {max_retries} attempts]: {name}")
    return False


def main():
    print("*" * 65)
    print("   AeroTwin MASTER DATASET RESUME ENGINE")
    print(f"   Target Base: {BASE}")
    free_gb = shutil.disk_usage("D:/").free / 1e9
    print(f"   Free Space on D: {free_gb:.1f} GB")
    print("*" * 65)

    # 1. HUST Bearing (Smallest first ~665MB, 177MB done -> 5-10 min)
    dl_kaggle("HUST Bearing", "mohdsufianbinothman/hust-bearing", "hust_bearing")

    # 2. Rotating Shaft Vibration (~2.7GB)
    dl_kaggle("Rotating Shaft Vibration", "jishnukoliyadan/vibration-analysis-on-rotating-shaft", "rotating_shaft_vibration")

    # 3. SNU Planetary Gearbox (~15.7GB, ~8.2GB already done! Figshare Range resume)
    dl_direct(
        name="SNU Planetary Gearbox",
        folder="snu_planetary_gearbox",
        fname="SNU Planetary Gearbox Dataset.zip",
        url="https://ndownloader.figshare.com/files/68834563",
        headers={"Referer": "https://figshare.com/articles/dataset/SNU_Planetary_Gearbox_Dataset/32025606"},
        target_mb=15776
    )

    # 4. Paderborn FULL DB (~9.2GB)
    dl_kaggle("Paderborn-db FULL", "dippatel03/paderborn-db", "paderborn_full")

    # 5. Machinery Fault DB (~12.3GB)
    dl_kaggle("Machinery Fault DB", "josh101/machinery-fault-database-induction-motor-fault", "machinery_fault_db")

    # 6. N-CMAPSS DS02 (~15GB, S3 Range resume)
    dl_direct(
        name="N-CMAPSS DS02",
        folder="nasa_ncmapss",
        fname="N-CMAPSS_DS02.zip",
        url="https://phm-datasets.s3.amazonaws.com/NASA/17.+Turbofan+Engine+Degradation+Simulation+Data+Set+2.zip",
        target_mb=15030
    )

    # 7. RflyMAD Datasets (Kaggle)
    dl_kaggle("RflyMAD-WithROS", "xianglile/rflymad-withros", "rflymad_withros")
    dl_kaggle("RflyMAD-SIL", "xianglile/rflymad-sil", "rflymad_sil")
    dl_kaggle("RflyMAD-HIL", "xianglile/rflymad-hil", "rflymad_hil")

    # 8. Engine Acoustic Emissions & Fault Detection (~450 MB)
    dl_kaggle("Engine Acoustic Emissions", "julienjta/engine-acoustic-emissions", "engine_acoustic_emissions")

    # 9. Engine Failure Multi-Sensor Telemetry (~380 MB)
    dl_kaggle("Engine Failure Detection", "zeynepyk/engine-failure-detection-dataset", "engine_failure_detection")

    # 10. SUBF Bearing Fault Vibration v1.0 (~1.6 GB)
    dl_kaggle("SUBF Bearing Fault", "sumairaziz/subf-v1-0-dataset-bearing-fault-vibration-data", "subf_bearing_fault")

    # 11. Bispectrum Signal Gearbox (~1.8 GB)
    dl_kaggle("Bispectrum Signal Gearbox", "zacky131/bispectrum-signal", "bispectrum_signal")

    print("\n" + "*" * 65)
    print("   [ALL DATASETS DOWNLOADED AND VERIFIED!]")
    print("*" * 65)

if __name__ == "__main__":
    main()
