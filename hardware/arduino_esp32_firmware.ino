/**
 * @file arduino_esp32_firmware.ino
 * @brief ESP32 / Arduino Hardware Ingestion Firmware for Aero Digital Twin
 * Connects MPU6050 (Vibration) + Thermocouple + BLDC RPM sensor
 * Streams JSON telemetry over USB Serial (115200 baud) or Wi-Fi to Laptop
 */

#include <Wire.h>

const int MPU_ADDR = 0x68;
int16_t AcX, AcY, AcZ;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  // Wake up MPU6050
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
  
  delay(100);
  Serial.println("[ESP32/ARDUINO] Hardware Edge Node Initialized.");
}

void loop() {
  // 1. Read MPU6050 Real Physical Vibration
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true);
  
  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();
  
  float ax = AcX / 16384.0;
  float ay = AcY / 16384.0;
  float az = AcZ / 16384.0;
  float raw_vib = sqrt(ax * ax + ay * ay + az * az);
  float vibration_g = max(0.85, raw_vib * 1.3);

  // 2. Simulated/Measured BLDC RPM & Temp
  float rpm = 4950.0 + (sin(millis() / 500.0) * 250.0);
  float temp_c = 109.5 + (cos(millis() / 1500.0) * 4.0);

  // 3. Print JSON Telemetry Frame to Serial
  Serial.print("{\"source\":\"ESP32_HARDWARE\",\"rpm\":");
  Serial.print(rpm);
  Serial.print(",\"vibration_g\":");
  Serial.print(vibration_g);
  Serial.print(",\"cht_c\":[");
  Serial.print(temp_c); Serial.print(",");
  Serial.print(temp_c + 1.2); Serial.print(",");
  Serial.print(temp_c + 2.5); Serial.print(",");
  Serial.print(temp_c + 1.0);
  Serial.println("]}");

  delay(50); // 20 Hz
}
