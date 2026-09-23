@echo off
echo ============================================================
echo   AEROTWIN — MANUAL DOWNLOAD PATCH
echo   D:\AeroTwin_Datasets target
echo ============================================================

echo.
echo [1/5] SUBF v2 Bearing Sound...
kaggle datasets download -d sumairaziz/subf-v2-0-dataset-bearing-faults-sound-data -p D:\AeroTwin_Datasets\subf_v2_bearing_sound
echo DONE: subf_v2_bearing_sound

echo.
echo [2/5] C172X Lycoming JSBSim Telemetry...
kaggle datasets download -d mohammedbellosani/phi-spike-c172x-jsbsim-aircraft-telemetry-dataset -p D:\AeroTwin_Datasets\c172x_lycoming_jsbsim
echo DONE: c172x_lycoming_jsbsim

echo.
echo [3/5] NASA CMAPSS-2 Engine Degradation...
kaggle datasets download -d bishals098/nasa-cmapss-2-engine-degradation -p D:\AeroTwin_Datasets\nasa_cmapss2_degradation
echo DONE: nasa_cmapss2_degradation

echo.
echo [4/5] Acoustic Bearing Fault...
kaggle datasets download -d ahuyng/bearingfault-dataset -p D:\AeroTwin_Datasets\acoustic_bearing_fault
echo DONE: acoustic_bearing_fault

echo.
echo [5/5] Helicopter Engine Degradation (alt source)...
kaggle datasets download -d aneelahmad/helicopter-engines-dataset -p D:\AeroTwin_Datasets\helicopter_engine_alt
echo DONE: helicopter_engine_alt

echo.
echo ============================================================
echo   ALL DOWNLOADS COMPLETE
echo ============================================================
python -c "import os; total=sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(r'D:\AeroTwin_Datasets') for f in fs); print(f'  TOTAL: {total/(1024**3):.2f} GB')"
pause
