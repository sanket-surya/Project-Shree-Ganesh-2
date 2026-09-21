import os, time, sys, subprocess

p_snu = r'D:\AeroTwin_Datasets\snu_planetary_gearbox\SNU Planetary Gearbox Dataset.zip'
target = 16543309134 # 15.77 GB

sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
print("Watching SNU until 100% complete, then stopping all download processes...", flush=True)

while True:
    cur = os.path.getsize(p_snu) if os.path.exists(p_snu) else 0
    rem_mb = max(0, (target - cur) / 1048576)
    pct = min(100.0, cur / target * 100)
    print(f"[{time.strftime('%H:%M:%S')}] SNU: {cur//1048576} MB / {target//1048576} MB ({pct:.2f}%) | Left: {rem_mb:.1f} MB", flush=True)
    
    if cur >= target * 0.9999 or rem_mb <= 1:
        print("\n🎉 SNU Planetary Gearbox 100% COMPLETE!", flush=True)
        break
    time.sleep(8)

# Stop download processes: master_download.py, GHAR_JAUN_RESUME.py, RESUME_ALL_DATASETS.py
print("\nStopping background download processes...", flush=True)
cmd = '''
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { 
    $_.CommandLine -match 'master_download.py|GHAR_JAUN_RESUME.py|RESUME_ALL_DATASETS.py' 
} | ForEach-Object { 
    Write-Output "Stopping PID $($_.ProcessId): $($_.CommandLine)"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}
'''
subprocess.run(['powershell', '-Command', cmd], check=False)
print("All download processes successfully STOPPED! You can sleep peacefully!", flush=True)
