#!/usr/bin/env python3
"""
Cross-Platform Master Launcher for Aero Piston Digital Twin System
Runs FastAPI Backend and Vite React Frontend concurrently,
monitors their lifecycle, opens the browser, and handles graceful shutdown.
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
from threading import Thread

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

def print_banner():
    print("=" * 78)
    print("   DEFENSE PROPULSION DIGITAL TWIN - MALE UAV (SIH 2026)")
    print("=" * 78)
    print(" [1/3] Initializing FastAPI Telemetry Hub & AI Inference Engine...")
    print(" [2/3] Initializing Vite React Tactical Ground Control Station...")
    print(" [3/3] Launching Web Visualizer at http://localhost:5173 ...")
    print("=" * 78)
    print(" Press Ctrl+C at any time to cleanly stop all services.")
    print("=" * 78)

def stream_logs(process, prefix):
    try:
        for line in iter(process.stdout.readline, b''):
            decoded = line.decode('utf-8', errors='replace').rstrip()
            if decoded:
                print(f"[{prefix}] {decoded}")
    except Exception:
        pass

def main():
    print_banner()

    is_windows = sys.platform.startswith("win")
    
    # 1. Start Backend process
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]
    print(f"[*] Starting Backend: {' '.join(backend_cmd)}")
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # 2. Start Frontend process
    npm_exec = "npm.cmd" if is_windows else "npm"
    frontend_cmd = f"{npm_exec} run dev"
    print(f"[*] Starting Frontend: {frontend_cmd}")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=FRONTEND_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # Stream logs asynchronously
    Thread(target=stream_logs, args=(backend_proc, "BACKEND"), daemon=True).start()
    Thread(target=stream_logs, args=(frontend_proc, "FRONTEND"), daemon=True).start()

    # Wait 3 seconds and open browser
    time.sleep(3)
    print("\n[+] System is ONLINE!")
    print("    - Web GCS Dashboard : http://localhost:5173")
    print("    - API Documentation : http://127.0.0.1:8000/docs")
    print("    - WebSocket Telemetry: ws://127.0.0.1:8000/ws/telemetry\n")
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        print("[!] Note: Please open http://localhost:5173 manually in your browser.")

    def cleanup(*args):
        print("\n\n[*] Shutting down Digital Twin services...")
        try:
            if is_windows:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(backend_proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                backend_proc.terminate()
                frontend_proc.terminate()
        except Exception:
            pass
        print("[+] All services stopped cleanly. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            if backend_proc.poll() is not None:
                print(f"[!] Backend process exited with code {backend_proc.returncode}")
                cleanup()
                break
            if frontend_proc.poll() is not None:
                print(f"[!] Frontend process exited with code {frontend_proc.returncode}")
                cleanup()
                break
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
