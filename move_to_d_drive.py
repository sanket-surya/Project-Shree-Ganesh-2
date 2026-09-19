import os, shutil, json

src = r'C:\Users\Asus\Desktop\Project Shree Ganesh 2\ml_models\data\real_datasets'
dst = r'D:\AeroTwin_Datasets'

os.makedirs(dst, exist_ok=True)
print('Moving datasets to D:\\AeroTwin_Datasets ...')
print()

moved = 0
failed = 0
for folder in os.listdir(src):
    src_folder = os.path.join(src, folder)
    dst_folder = os.path.join(dst, folder)
    if not os.path.isdir(src_folder):
        continue
    
    # Calculate size
    total = 0
    for r, d, files in os.walk(src_folder):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(r, f))
            except:
                pass
    
    print(f'  Moving: {folder} ({total/1048576:.1f} MB) ...', end=' ', flush=True)
    try:
        shutil.move(src_folder, dst_folder)
        print('OK')
        moved += 1
    except Exception as e:
        print(f'FAILED: {e}')
        failed += 1

print()
print(f'Done! {moved} folders moved, {failed} failed')
print()
print('D:\\AeroTwin_Datasets contents:')

total_all = 0
for folder in sorted(os.listdir(dst)):
    fp = os.path.join(dst, folder)
    if not os.path.isdir(fp): continue
    total = sum(os.path.getsize(os.path.join(r, f)) for r, d, files in os.walk(fp) for f in files if os.path.exists(os.path.join(r, f)))
    total_all += total
    print(f'  {folder}: {total/1048576:.1f} MB')

print(f'\nTOTAL: {total_all/1073741824:.2f} GB')
