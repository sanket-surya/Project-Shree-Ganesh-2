# 🔌 Raspberry Pi to Laptop Connection & Setup Guide (Semi-Hardware)

---

## 🎯 What We Are Doing:
The **Raspberry Pi** acts as the **Onboard UAV Health Monitoring Computer (HUMS)**.
It reads real physical sensors (**Vibration from MPU6050**, **BLDC Motor RPM**, **Thermocouple Temperature**) and transmits the data over **Wi-Fi / Hotspot** directly into our **React 3D Digital Twin Dashboard** running on the Laptop!

---

## 🛠️ Step 1: Physical Sensor Wiring to Raspberry Pi (Jumper Wires)

| Sensor | Sensor Pin | Raspberry Pi Pin | Description |
| :--- | :--- | :--- | :--- |
| **MPU-6050 (Vibration)** | **VCC** | **Pin 1 (3.3V)** | Power Supply |
| | **GND** | **Pin 6 (GND)** | Ground |
| | **SDA** | **Pin 3 (GPIO 2 - SDA)** | I2C Data |
| | **SCL** | **Pin 5 (GPIO 3 - SCL)** | I2C Clock |
| **Optical / Hall RPM Sensor** | **OUT / D0** | **Pin 11 (GPIO 17)** | Pulse Counter |
| | **VCC / GND** | **3.3V / GND** | Power Supply |

---

## 🌐 Step 2: Connect Raspberry Pi to Laptop via Wi-Fi / Hotspot

1. Turn on your **Mobile Hotspot**.
2. Connect both your **Laptop** and your **Raspberry Pi** to the **same Mobile Hotspot**.
3. Find your Laptop's IP address:
   - On Windows Laptop, open Command Prompt (`cmd`) and type:
     ```cmd
     ipconfig
     ```
   - Look for **IPv4 Address** (e.g., `192.168.1.15` or `192.168.43.100`).

---

## 🚀 Step 3: Run the Ingestion Script on Raspberry Pi

1. Copy the script [`hardware/rpi_sensor_node.py`](file:///c:/Users/Asus/Desktop/Project%20Shree%20Ganesh%201/hardware/rpi_sensor_node.py) to your Raspberry Pi.
2. Open `rpi_sensor_node.py` on the Raspberry Pi and set your Laptop's IP address:
   ```python
   LAPTOP_BACKEND_URL = "http://192.168.43.100:8000/api/telemetry/hardware-ingest"
   ```
3. Run the script on the Raspberry Pi:
   ```bash
   python rpi_sensor_node.py
   ```

---

## 🌟 Step 4: Watch Live Physical Data on Laptop!
1. Open your browser on the Laptop at **`http://localhost:5173/`**.
2. Spin the BLDC motor or shake/tap the MPU6050 sensor on the Raspberry Pi.
3. You will immediately see:
   - **Real vibration peaks** moving in the **FFT Waterfall**.
   - **Real RPM changes** moving the 3D propeller and cockpit gauge dials.
   - **AI Anomaly Detector** flagging live physical motor anomalies in real time!
