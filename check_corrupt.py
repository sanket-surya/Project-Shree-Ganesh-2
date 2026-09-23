"""AeroTwin - Corrupt File Checker"""
import os, zipfile, tarfile, csv

BASE = r"D:\AeroTwin_Datasets"
corrupt = []
ok = []

for root, dirs, files in os.walk(BASE):
    for fname in files:
        fpath = os.path.join(root, fname)
        sz = os.path.getsize(fpath)
        rel = fpath.replace(BASE, "").lstrip("\\")
        sz_mb = sz / (1024*1024)

        # ── ZIP check ──
        if fname.endswith(".zip"):
            if sz < 1024 * 50:  # < 50KB = definitely partial
                corrupt.append((rel, f"ZIP too small ({sz_mb:.2f} MB) — partial download"))
                continue
            try:
                with zipfile.ZipFile(fpath) as z:
                    bad = z.testzip()
                    if bad:
                        corrupt.append((rel, f"ZIP corrupt: bad file inside = {bad}"))
                    else:
                        ok.append((rel, f"ZIP OK ({sz_mb:.1f} MB)"))
            except zipfile.BadZipFile:
                corrupt.append((rel, f"ZIP BadZipFile ({sz_mb:.2f} MB)"))
            except Exception as e:
                corrupt.append((rel, f"ZIP error: {e}"))

        # ── TAR check ──
        elif fname.endswith((".tar", ".tar.gz", ".tgz")):
            if sz < 1024 * 100:  # < 100KB
                corrupt.append((rel, f"TAR too small ({sz_mb:.2f} MB) — partial"))
                continue
            try:
                with tarfile.open(fpath) as t:
                    members = t.getmembers()
                    ok.append((rel, f"TAR OK ({sz_mb:.1f} MB, {len(members)} files)"))
            except tarfile.TarError as e:
                corrupt.append((rel, f"TAR corrupt: {e}"))
            except Exception as e:
                corrupt.append((rel, f"TAR error: {e}"))

        # ── CSV check ──
        elif fname.endswith(".csv"):
            if sz < 100:
                corrupt.append((rel, f"CSV empty ({sz} bytes)"))
            else:
                try:
                    with open(fpath, "r", errors="ignore") as f:
                        reader = csv.reader(f)
                        rows = sum(1 for _ in reader)
                    if rows < 2:
                        corrupt.append((rel, f"CSV only {rows} rows ({sz_mb:.2f} MB)"))
                    else:
                        ok.append((rel, f"CSV OK ({rows} rows, {sz_mb:.1f} MB)"))
                except Exception as e:
                    corrupt.append((rel, f"CSV error: {e}"))

        # ── HTML/PDF junk ──
        elif fname.endswith((".html", ".pdf")) and sz < 1024*10:
            corrupt.append((rel, f"JUNK file ({fname}, {sz} bytes)"))

print("=" * 70)
print(f"  CORRUPT / PARTIAL / JUNK FILES ({len(corrupt)} found)")
print("=" * 70)
for rel, reason in corrupt:
    print(f"  ❌ {reason}")
    print(f"     {rel}")

print()
print(f"  CLEAN FILES: {len(ok)}")
print("=" * 70)

total = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(BASE) for f in fs)
print(f"  TOTAL: {total/(1024**3):.2f} GB")
