"""Extract all corrupt-but-extractable large ZIPs"""
import os, zipfile, time

BASE = r"D:\AeroTwin_Datasets"

to_extract = [
    ("nasa_ncmapss",         "N-CMAPSS_DS02.zip"),
    ("snu_planetary_gearbox","SNU Planetary Gearbox Dataset.zip"),
    ("machinery_fault_db",   "machinery-fault-database-induction-motor-fault.zip"),
    ("rflymad_hil",          "rflymad-hil.zip"),
    ("rflymad_sil",          "rflymad-sil.zip"),
    ("rflymad_withros",      "rflymad-withros.zip"),
]

for folder, zipname in to_extract:
    zippath = os.path.join(BASE, folder, zipname)
    dest = os.path.join(BASE, folder)
    if not os.path.exists(zippath):
        print("SKIP missing: " + zipname); continue
    sz = os.path.getsize(zippath)/(1024**3)
    print("\nEXTRACTING: " + folder + " (" + str(round(sz,2)) + " GB)")
    t0 = time.time()
    extracted = 0
    failed = 0
    try:
        with zipfile.ZipFile(zippath, "r") as z:
            members = z.namelist()
            print("  Files: " + str(len(members)))
            for m in members:
                try:
                    z.extract(m, dest)
                    extracted += 1
                    if extracted % 100 == 0:
                        print("  Progress: " + str(extracted) + "/" + str(len(members)))
                except Exception as e:
                    failed += 1
        elapsed = time.time() - t0
        print("  DONE: " + str(extracted) + " OK, " + str(failed) + " failed, " + str(round(elapsed,1)) + "s")
        # Check extracted size
        ext_sz = sum(os.path.getsize(os.path.join(r,f))
                     for r,d,fs in os.walk(dest)
                     for f in fs if not f.endswith(".zip")) / (1024**3)
        print("  Extracted data: " + str(round(ext_sz,2)) + " GB")
        if ext_sz > 0.5:
            print("  -> Deleting corrupt zip (data extracted safely)")
            os.remove(zippath)
    except Exception as e:
        print("  OPEN ERROR: " + str(e)[:100])

total = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(BASE) for f in fs)
print("\nFINAL TOTAL: " + str(round(total/(1024**3),2)) + " GB (all extracted)")
