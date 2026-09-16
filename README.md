# 🛰️ AI-Enabled Real-Time Digital Twin System for Aero Piston Engines in MALE UAVs
**Smart India Hackathon (SIH 2026) — Defense Propulsion Digital Twin & Predictive Health Monitoring Framework**

---

## 📌 Executive Summary
This project delivers an indigenous, defense-grade Digital Twin (DT) framework engineered specifically for aero piston engines (modeled on the **Rotax 914F/912 Turbocharged 4-Cylinder Boxer Platform** deployed on MALE UAVs such as **Tapas-BH-201, Heron, Hermes 900, and Predator-A**).

By fusing **first-principles thermodynamics, high-frequency SocketCAN / FADEC telemetry ingestion, embedded C++/C# edge engines, and real domain-specific AI/ML predictive analytics**, the system transitions UAV engine management from reactive threshold alarms to **proactive prognostic health monitoring, real-time 3D twin thermal visualization, and autonomous contingency planning**.

---

## 🏛️ System Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                      SYSTEM ARCHITECTURE                                           |
+----------------------------------------------------------------------------------------------------+
|  1. EMBEDDED / EDGE LAYER (C++ & C#)                                                               |
|     • SocketCAN / FADEC 2.0 CAN-Bus Telemetry Frame Encoders / Decoders (PGN 0xFEE0, 0xFEEE)       |
|     • First-Principles Thermodynamic & Mechanical Physics Engine (Otto-Turbo Cycle, Heat Exchange) |
|     • Embedded Signal Filtering & Physics Residual Generator                                       |
+----------------------------------------------------------------------------------------------------+
|  2. FASTAPI & WEBSOCKET BACKEND (Edge Telemetry & AI Inference Hub)                                 |
|     • High-frequency Telemetry Streamer (20 Hz - 50 Hz) with bidirectional control                 |
|     • Telemetry Black Box Logger & Mission Flight Dataset Replayer                                |
|     • Physics Residuals & Model Inference Pipeline                                                 |
+----------------------------------------------------------------------------------------------------+
|  3. DOMAIN-SPECIFIC AI/ML ENGINE (Python / Scikit-Learn / SciPy / ONNX)                            |
|     • Physics-Informed Autoencoder / Isolation Forest for Anomaly Detection                        |
|     • Multi-Fault Diagnostic Classifier (8+ distinct failure modes)                                |
|     • Temporal Degradation Regressor for Remaining Useful Life (RUL)                               |
|     • Explainable AI (XAI) Feature Attribution & Diagnostic Reasoning Engine                       |
+----------------------------------------------------------------------------------------------------+
|  4. TACTICAL DEFENSE GCS DASHBOARD (React.js + Three.js + Canvas Gauges)                           |
|     • Interactive 3D Digital Twin: Real-time CHT 1-4 & EGT 1-4 heatmaps, Piston/Turbo animation     |
|     • Real-time Telemetry HMI: RPM, MAP, CHT, EGT, Oil P/T, Fuel Flow, Battery/Alternator, FFT    |
|     • Fault Injection & Mission Scenario Studio: Simulate mid-air failures in real time            |
|     • Mission Replay & Blackbox Scrubbing: Time-travel analysis of past flights                     |
|     • Contingency Planning & Autonomous Maintenance Advisory: Safe Return to Base calculations     |
|     • Automated Mission Health & Maintenance Work-Order PDF/CSV Exporter                           |
+----------------------------------------------------------------------------------------------------+
```

---

## 🚀 Key Features & Deliverables

### 1. Interactive 3D Digital Twin (Three.js / WebGL)
- Dynamic 3D model of a 4-cylinder turbocharged boxer engine.
- **Live Thermal Heatmaps**: Cylinder heads (CHT 1–4) and exhaust headers (EGT 1–4) dynamically change color based on incoming telemetry.
- **Dynamic Physics Animation**: Reciprocating pistons synchronized with engine RPM, rotating propeller hub, and spinning turbocharger compressor spool.
- **Exploded View / Inspection Mode**: Smoothly separates component assemblies to inspect internal pistons, combustion chambers, and oil sump.

### 2. Domain-Specific AI/ML Intelligence
- **Physics-Informed Anomaly Detection**: Evaluates deviations between observed sensor values and first-principles thermodynamic models using an Isolation Forest baseline.
- **Multi-Class Fault Diagnostic Classifier**: 99.93% test accuracy across 8+ failure modes:
  1. `Cylinder_Misfire` (Coil / Spark loss on Cyl 3)
  2. `Turbo_Degradation` (Wastegate jam & boost pressure loss)
  3. `Injector_Clogging` (Lean combustion & critical EGT spike)
  4. `Coolant_Loss` (Radiator puncture & thermal runaway)
  5. `Oil_Starvation` (Pressure drop & bearing friction)
  6. `Sensor_Drift` (Thermocouple offset without mechanical change)
  7. `Combustion_Knock` (Detonation in hot-and-high ambient)
  8. `Valve_Leakage` (Exhaust valve blowby)
- **Remaining Useful Life (RUL) Estimation**: Predicts operational flight hours remaining before mandatory teardown/overhaul.
- **Explainable AI (XAI)**: Feature attribution breakdown providing pilot/ground crew with direct root-cause explanations (e.g. `res_egt_spread: +3.435`, `vibration_g: +0.206`).

### 3. Mission Scenarios & Real-Time Fault Injection Studio
- **Operational Flight Profiles**: Nominal ISR Loiter, High Altitude (25,000 ft turbo boost), Hot Desert (46°C thermal stress), and Rapid Throttle Climbs.
- **Mid-Air Failure Injection**: Inject any failure in real-time with variable severity (20% to 100%) to demonstrate AI detection and contingency reactions live.

### 4. Autonomous Contingency Advisory & Decision Support
- Calculates **Power De-Rate Recommendations** (e.g., `-25% MAX` on misfire to prevent crankshaft fatigue).
- Computes **Safe Return to Base (RTB) Glide Range** in Nautical Miles (NM).
- Step-by-step pilot/autopilot contingency checklist.

### 5. Embedded C++ & C# Telemetry Layer
- **C++17 Engine Core**: Located in `embedded/cpp/` (`aero_twin_engine.hpp`, `aero_twin_engine.cpp`, `main_sim.cpp`, `CMakeLists.txt`).
- **C# .NET Core**: Located in `embedded/csharp/` (`AeroEngineTwinCore.cs`, `CanBusFadecProtocol.cs`, `Program.cs`, `AeroDigitalTwin.csproj`).
- **SocketCAN / ARINC Framing**: Encodes raw CAN IDs (`0x18FEE000`, `0x18FEEE00`) and live hex stream.

### 6. Defense Airworthiness Debrief & Work-Order Exporter
- Generates defense-standard engine health certificates with subsystem health breakdowns and scheduled maintenance work orders with one-click print/PDF support.

---

### 🚀 One-Click Start (Recommended)
Simply double-click **`run.bat`** (or run `run_all.bat`) or run:
```bash
python run_all.py
```
This automatically:
1. Validates Python and Node.js environments
2. Starts the **FastAPI AI Telemetry Backend** on `http://127.0.0.1:8000`
3. Starts the **React.js Tactical GCS Visualizer** on `http://localhost:5173`
4. Automatically opens the browser to **`http://localhost:5173/`**

---

### 🛠️ Manual Step-by-Step Start

#### Prerequisites
```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

#### Step 1: Start the Backend Server (FastAPI + WebSockets)
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
# Or run: run_backend.bat
```

#### Step 2: Start the React.js Ground Control Station Dashboard
```bash
cd frontend
npm run dev
# Or run: run_frontend.bat
```
Open **`http://localhost:5173/`** in your browser!

### Step 3: Run Embedded C++ or C# Simulator (Optional)
**C++:**
```bash
cd embedded/cpp
g++ -std=c++17 main_sim.cpp aero_twin_engine.cpp -o aero_twin_sim
./aero_twin_sim
```

**C# (.NET):**
```bash
cd embedded/csharp
dotnet run
```

---

## 📂 Project Structure

```
Project Shree Ganesh 1/
├── backend/
│   ├── main.py                     # FastAPI WebSocket & REST Server
│   └── physics_twin.py             # First-Principles Otto-Turbo Thermodynamic Model
├── ml_models/
│   ├── dataset_generator.py        # MALE UAV Flight Telemetry Dataset Generator
│   ├── train_models.py             # ML Model Training & Evaluation Pipeline
│   ├── inference_engine.py         # Real-Time AI Diagnostics, XAI & RUL Engine
│   ├── data/                       # Generated Telemetry Datasets
│   └── weights/                    # Pre-trained ML weights (RF, Isolation Forest, GBR)
├── embedded/
│   ├── cpp/                        # Embedded C++17 Twin Engine & SocketCAN Framer
│   │   ├── aero_twin_engine.hpp
│   │   ├── aero_twin_engine.cpp
│   │   ├── main_sim.cpp
│   │   └── CMakeLists.txt
│   └── csharp/                     # Embedded C# .NET Twin Engine & FADEC Protocol
│       ├── AeroEngineTwinCore.cs
│       ├── CanBusFadecProtocol.cs
│       ├── Program.cs
│       └── AeroDigitalTwin.csproj
├── frontend/                       # Tactical Defense React.js GCS Visualizer
│   ├── src/
│   │   ├── components/
│   │   │   ├── ThreeEngineTwin.jsx         # 3D WebGL Engine Twin with Thermal Gradients
│   │   │   ├── TelemetryGauges.jsx         # Avionics Analog & Digital Dials
│   │   │   ├── CylinderThermalMatrix.jsx   # CHT & EGT Balance Matrix
│   │   │   ├── VibrationWaterfall.jsx      # Dynamic FFT Waterfall & Harmonics
│   │   │   ├── AIPredictivePanel.jsx       # AI Fault Diagnostics & XAI Attributions
│   │   │   ├── RULDegradationGauge.jsx     # RUL & Subsystem Health Indicators
│   │   │   ├── MissionStudio.jsx           # Flight Profiles & Fault Injector
│   │   │   ├── ContingencyAdvisory.jsx     # Autonomous Decision Support
│   │   │   ├── CanBusTerminal.jsx          # Live SocketCAN Hex Frame Stream
│   │   │   ├── MissionReplayBar.jsx        # Black Box Timeline Scrubber
│   │   │   └── ReportModal.jsx             # Airworthiness Report & Work Orders
│   │   ├── App.jsx
│   │   ├── index.css                       # Military GCS Design Tokens & Tailwind v4
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 🏆 SIH 2026 Evaluation Criteria Fulfillment
| Evaluation Criterion | Implementation Details |
| :--- | :--- |
| **Real-time Digital Twin Framework** | Three.js 3D dynamic virtual twin synchronized at 20Hz with live physics engine & thermal shaders. |
| **Domain-Specific AI/ML (Not API Wrapper)** | Real trained Isolation Forest, Random Forest Classifier (99.93% acc), and GBR RUL regressor on aero engine physics telemetry. |
| **Embedded C++ / C# Integration** | Native C++17 and C# .NET embedded engines with SocketCAN PGN 0xFEE0 / 0xFEEE frame packing. |
| **Explainable AI (XAI)** | Real-time feature attribution indicating exact thermodynamic deviation causes. |
| **Simulation & Replay** | Mission profiles (High-Alt 25k ft, Hot Desert 46°C, Climbs) + Live Fault Injector + Black Box Scrubbing. |
| **Operational GCS Dashboard** | Defense-grade dark-mode tactical UI with analog/digital avionics gauges and automated PDF/work-order export. |
