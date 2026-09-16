/**
 * @file aero_twin_engine.cpp
 * @brief High-Performance Physics-Informed Digital Twin Implementation for Aero Piston Engines
 *        Includes: Injection Timing, Combustion Efficiency, Degradation Trend Buffer, JSON Serialization
 */

#include "aero_twin_engine.hpp"
#include <random>
#include <algorithm>
#include <cmath>
#include <sstream>
#include <iomanip>

namespace AeroTwin {

    AeroPistonTwinCore::AeroPistonTwinCore() 
        : active_fault(FaultType::NONE), fault_severity(0.0), accumulated_run_hours(124.5) {
        
        // Initialize Default Flight Condition (ISA Sea Level Cruise)
        current_flight.altitude_m = 1500.0; // 5000 ft
        current_flight.ambient_temp_c = 15.0 - (current_flight.altitude_m * 0.0065); // Standard lapse rate
        current_flight.ambient_press_hpa = 1013.25 * std::pow(1.0 - (0.0065 * current_flight.altitude_m / 288.15), 5.255);
        current_flight.true_airspeed_kts = 95.0;
        current_flight.throttle_pct = 75.0;

        // Initialize Engine Nominal Baseline State
        current_state.rpm = 5000.0;
        current_state.manifold_pressure_hpa = 1150.0;
        current_state.power_output_kw = 65.0;
        current_state.torque_nm = 124.0;
        current_state.fuel_flow_lph = 18.5;
        current_state.fuel_pressure_bar = 3.0;

        for (int i = 0; i < 4; ++i) {
            current_state.cht_c[i] = 110.0 + (i * 1.5);
            current_state.egt_c[i] = 810.0 + ((i % 2 == 0) ? 5.0 : -4.0);
        }

        current_state.oil_temperature_c = 92.0;
        current_state.oil_pressure_bar = 3.8;
        current_state.coolant_temperature_c = 88.0;
        current_state.turbo_rpm = 110000.0;
        current_state.wastegate_position_pct = 45.0;
        current_state.intercooler_temp_c = 38.0;
        current_state.bus_voltage_v = 28.1;
        current_state.alternator_current_a = 22.4;
        current_state.ignition_timing_deg_btdc = 26.0;
        // Injection & Combustion defaults
        current_state.injection_timing_btdc    = 8.5;
        current_state.injection_pulse_width_ms = 4.2;
        current_state.lambda_afr               = 1.02;
        current_state.combustion_efficiency_pct= 92.5;
        current_state.overall_vibration_g = 1.45;
        current_state.health_index = 0.98;
        current_state.remaining_useful_life_hrs = 875.5;
        current_state.timestamp_ms = 0;
    }

    void AeroPistonTwinCore::setFlightConditions(const FlightCondition& fc) {
        current_flight = fc;
    }

    void AeroPistonTwinCore::injectFault(FaultType fault, double severity) {
        active_fault = fault;
        fault_severity = std::clamp(severity, 0.0, 1.0);
    }

    void AeroPistonTwinCore::clearFault() {
        active_fault = FaultType::NONE;
        fault_severity = 0.0;
    }

    void AeroPistonTwinCore::calculateThermodynamics(double dt_sec) {
        // Target RPM based on throttle and propeller governor
        double target_rpm = 1400.0 + (current_flight.throttle_pct / 100.0) * (5800.0 - 1400.0);
        current_state.rpm += (target_rpm - current_state.rpm) * std::min(1.0, dt_sec * 3.5);

        // Manifold Absolute Pressure (MAP) with Turbocharger compensation
        // Rotax 914 Turbo controller maintains up to 1350-1400 hPa at full throttle even at altitude
        double base_ambient = current_flight.ambient_press_hpa;
        double max_boost_hpa = 1400.0;
        double target_map = base_ambient + (current_flight.throttle_pct / 100.0) * (max_boost_hpa - base_ambient);
        current_state.manifold_pressure_hpa += (target_map - current_state.manifold_pressure_hpa) * std::min(1.0, dt_sec * 4.0);

        // Turbocharger dynamics
        double target_turbo_rpm = (current_state.manifold_pressure_hpa / max_boost_hpa) * 145000.0;
        current_state.turbo_rpm += (target_turbo_rpm - current_state.turbo_rpm) * std::min(1.0, dt_sec * 2.0);
        current_state.wastegate_position_pct = (current_state.manifold_pressure_hpa > 1200.0) ? 
            ((current_state.manifold_pressure_hpa - 1200.0) / 200.0) * 100.0 : 0.0;

        // Mechanical power output (kW) = Torque * RPM / 9548.8
        current_state.power_output_kw = (current_state.manifold_pressure_hpa / 1013.25) * (current_state.rpm / 5800.0) * 84.5;
        current_state.torque_nm = (current_state.rpm > 100.0) ? (current_state.power_output_kw * 9548.8 / current_state.rpm) : 0.0;

        // Specific Fuel Consumption (BSFC approx 280 g/kWh for turbo aero piston)
        double fuel_kg_hr = (current_state.power_output_kw * 0.285);
        current_state.fuel_flow_lph = fuel_kg_hr / 0.72; // AVGAS 100LL density approx 0.72 kg/L

        // Thermal dynamics (First-principles cylinder heat transfer)
        double combustion_heat = current_state.power_output_kw * 1.8;
        double ram_air_cooling = (current_flight.true_airspeed_kts / 100.0) * 15.0;
        
        for (int i = 0; i < 4; ++i) {
            double cyl_load_factor = (i == 2 || i == 3) ? 1.03 : 0.98; // Rear cylinders run slightly hotter
            double target_cht = 70.0 + (combustion_heat * 0.45 * cyl_load_factor) - ram_air_cooling + (current_flight.ambient_temp_c * 0.3);
            current_state.cht_c[i] += (target_cht - current_state.cht_c[i]) * std::min(1.0, dt_sec * 0.15);

            double target_egt = 720.0 + (current_state.manifold_pressure_hpa * 0.11) + (cyl_load_factor * 12.0);
            current_state.egt_c[i] += (target_egt - current_state.egt_c[i]) * std::min(1.0, dt_sec * 0.5);
        }

        // Oil and Coolant loops
        double target_oil_temp = 75.0 + (current_state.power_output_kw * 0.38) - (ram_air_cooling * 0.5);
        current_state.oil_temperature_c += (target_oil_temp - current_state.oil_temperature_c) * std::min(1.0, dt_sec * 0.1);
        
        // Oil pressure is inversely proportional to oil temp and directly proportional to RPM
        current_state.oil_pressure_bar = (current_state.rpm / 5000.0) * 4.2 * (1.0 - (current_state.oil_temperature_c - 80.0) * 0.003);
        current_state.coolant_temperature_c = current_state.oil_temperature_c * 0.92;
    }

    void AeroPistonTwinCore::calculateVibrations() {
        // Base mechanical vibration RMS
        double base_g = 0.8 + (current_state.rpm / 5800.0) * 1.2;
        
        // Frequency domain peaks: 1X (propeller order), 2X (engine crankshaft firing order), 4X (piston strokes)
        current_state.fft_peaks[0] = base_g * 0.4;  // 1X Subharmonic
        current_state.fft_peaks[1] = base_g * 0.85; // 2X Engine order (fundamental)
        current_state.fft_peaks[2] = base_g * 0.25; // 3X
        current_state.fft_peaks[3] = base_g * 0.55; // 4X Combustion peak
        current_state.fft_peaks[4] = 0.12;          // High freq noise
        current_state.fft_peaks[5] = 0.08;
        current_state.fft_peaks[6] = 0.05;
        current_state.fft_peaks[7] = 0.03;

        current_state.overall_vibration_g = base_g;
    }

    void AeroPistonTwinCore::applyFaultDynamics(double dt_sec) {
        if (active_fault == FaultType::NONE) {
            current_state.health_index = 0.98;
            return;
        }

        switch (active_fault) {
            case FaultType::CYLINDER_MISFIRE:
                // Cylinder 3 misfire: CHT drops, unburned fuel causes EGT drop/surge, severe 1X & 0.5X vibration
                current_state.cht_c[2] -= 45.0 * fault_severity * dt_sec;
                current_state.egt_c[2] -= 180.0 * fault_severity * dt_sec;
                current_state.overall_vibration_g += 2.4 * fault_severity;
                current_state.fft_peaks[0] += 1.8 * fault_severity; // Strong half-order vibration
                current_state.power_output_kw *= (1.0 - (0.24 * fault_severity));
                current_state.health_index = std::max(0.2, 0.98 - (0.45 * fault_severity));
                break;

            case FaultType::TURBO_DEGRADATION:
                // Wastegate sticking / boost leak: MAP drops at altitude, high EGT, turbo RPM hunts
                current_state.manifold_pressure_hpa -= 280.0 * fault_severity * dt_sec;
                current_state.turbo_rpm -= 35000.0 * fault_severity * dt_sec;
                for (auto& egt : current_state.egt_c) egt += 65.0 * fault_severity * dt_sec;
                current_state.health_index = std::max(0.3, 0.98 - (0.35 * fault_severity));
                break;

            case FaultType::INJECTOR_CLOGGING:
                // Cylinder 1 lean condition: EGT spikes critically, mild knock
                current_state.egt_c[0] += 95.0 * fault_severity * dt_sec;
                current_state.cht_c[0] += 25.0 * fault_severity * dt_sec;
                current_state.fft_peaks[4] += 0.8 * fault_severity; // Knock frequency
                current_state.health_index = std::max(0.4, 0.98 - (0.30 * fault_severity));
                break;

            case FaultType::COOLANT_LOSS:
                // Radiator leak: CHT runaway across all cylinders, coolant boiling
                for (auto& cht : current_state.cht_c) cht += 55.0 * fault_severity * dt_sec;
                current_state.coolant_temperature_c += 35.0 * fault_severity * dt_sec;
                current_state.health_index = std::max(0.1, 0.98 - (0.70 * fault_severity));
                break;

            case FaultType::OIL_STARVATION:
                // Oil pressure drops rapidly, oil temp surges, mechanical friction increases vibration
                current_state.oil_pressure_bar = std::max(0.6, current_state.oil_pressure_bar - (2.5 * fault_severity * dt_sec));
                current_state.oil_temperature_c += 38.0 * fault_severity * dt_sec;
                current_state.overall_vibration_g += 1.8 * fault_severity;
                current_state.health_index = std::max(0.05, 0.98 - (0.85 * fault_severity));
                break;

            case FaultType::SENSOR_DRIFT:
                // Thermocouple drift on Cylinder 4 (+60°C false reading)
                current_state.cht_c[3] += 60.0 * fault_severity;
                current_state.health_index = 0.82;
                break;

            case FaultType::COMBUSTION_KNOCK:
                // Detonation: High-frequency acoustic spike in FFT, elevated CHT
                current_state.fft_peaks[4] += 1.6 * fault_severity;
                current_state.fft_peaks[5] += 1.2 * fault_severity;
                for (auto& cht : current_state.cht_c) cht += 20.0 * fault_severity * dt_sec;
                current_state.health_index = std::max(0.35, 0.98 - (0.40 * fault_severity));
                break;

            case FaultType::VALVE_LEAKAGE:
                // Exhaust valve leak on Cylinder 2: continuous high EGT, blowby
                current_state.egt_c[1] += 110.0 * fault_severity * dt_sec;
                current_state.power_output_kw *= (1.0 - (0.15 * fault_severity));
                current_state.health_index = std::max(0.45, 0.98 - (0.35 * fault_severity));
                break;

            default:
                break;
        }
    }

    void AeroPistonTwinCore::calculateInjectionAndCombustion() {
        // --- Ignition Timing: MBT advance curve (Rotax 914F FADEC schedule) ---
        // Advance increases with RPM (centrifugal), retards at high MAP (knock prevention)
        double rpm_adv   = (current_state.rpm / RATED_RPM) * 14.0;
        double map_retard= (current_state.manifold_pressure_hpa / MAX_BOOST_HPA) * 6.0;
        current_state.ignition_timing_deg_btdc = 18.0 + rpm_adv - map_retard;

        // --- Injection Timing & Pulse Width ---
        // Injection advances slightly with RPM to maintain homogeneous mixture
        current_state.injection_timing_btdc = 4.0 +
            (current_flight.throttle_pct / 100.0) * 8.0;
        // Injector pulse width: derived from fuel flow requirement
        //   PW(ms) = (fuel_flow_L/hr) / (N/2 * 60) * 1000 * 3600 + deadtime
        double firing_freq = (current_state.rpm / 2.0) / 60.0; // events/sec (4-stroke)
        current_state.injection_pulse_width_ms =
            (firing_freq > 0.1) ?
            (current_state.fuel_flow_lph / (firing_freq * 3600.0)) * 1000.0 + 0.8 : 4.2;

        // --- Lambda (Air-Fuel Ratio) ---
        // Lean at cruise, slightly rich at full power (Rotax FADEC map)
        static std::default_random_engine rng(42);
        static std::normal_distribution<double> noise(0.0, 0.003);
        current_state.lambda_afr = 1.08 -
            (current_flight.throttle_pct / 100.0) * 0.10 + noise(rng);

        // --- Combustion Efficiency ---
        // Penalized by AFR deviation from stoichiometric and excess vibration
        double afr_penalty = std::abs(current_state.lambda_afr - 1.0) * 15.0;
        double vib_penalty = std::max(0.0, (current_state.overall_vibration_g - 1.5) * 3.0);
        current_state.combustion_efficiency_pct =
            std::max(50.0, 96.0 - afr_penalty - vib_penalty);
    }

    void AeroPistonTwinCore::updateTrendBuffer() {
        // Circular ring buffer — overwrites oldest entry when full
        int idx = trend_buf.head;
        double cht_max = *std::max_element(current_state.cht_c.begin(), current_state.cht_c.end());
        double egt_max = *std::max_element(current_state.egt_c.begin(), current_state.egt_c.end());

        trend_buf.cht_max[idx]    = cht_max;
        trend_buf.egt_max[idx]    = egt_max;
        trend_buf.oil_temp[idx]   = current_state.oil_temperature_c;
        trend_buf.vibration[idx]  = current_state.overall_vibration_g;
        trend_buf.efficiency[idx] = current_state.combustion_efficiency_pct;

        trend_buf.head = (idx + 1) % DegradationTrendBuffer::MAX_POINTS;
        if (trend_buf.count < DegradationTrendBuffer::MAX_POINTS)
            ++trend_buf.count;
    }

    void AeroPistonTwinCore::step(double dt_sec) {
        calculateThermodynamics(dt_sec);
        calculateVibrations();
        calculateInjectionAndCombustion();
        applyFaultDynamics(dt_sec);
        updateTrendBuffer();

        accumulated_run_hours += (dt_sec / 3600.0);
        current_state.remaining_useful_life_hrs =
            std::max(0.0, (1000.0 - accumulated_run_hours) * current_state.health_index);
        current_state.timestamp_ms += static_cast<uint64_t>(dt_sec * 1000.0);
    }

    CanTelemetryFrame AeroPistonTwinCore::packCanFrame(uint16_t pgn) const {
        CanTelemetryFrame frame;
        frame.dlc = 8;
        frame.timestamp_us = current_state.timestamp_ms * 1000;

        switch (pgn) {
            case 0xFEE0: // Engine Speed & MAP (PGN 65248)
                frame.can_id = 0x18FEE000;
                {
                    uint16_t raw_rpm = static_cast<uint16_t>(current_state.rpm * 8.0); // 0.125 rpm/bit
                    uint16_t raw_map = static_cast<uint16_t>(current_state.manifold_pressure_hpa * 10.0);
                    frame.data[0] = raw_rpm & 0xFF;
                    frame.data[1] = (raw_rpm >> 8) & 0xFF;
                    frame.data[2] = raw_map & 0xFF;
                    frame.data[3] = (raw_map >> 8) & 0xFF;
                    frame.data[4] = static_cast<uint8_t>(current_state.fuel_flow_lph * 2.0);
                    frame.data[5] = static_cast<uint8_t>(current_state.power_output_kw);
                    frame.data[6] = static_cast<uint8_t>(current_state.health_index * 100.0);
                    frame.data[7] = static_cast<uint8_t>(active_fault);
                }
                break;
            case 0xFEEE: // Temperatures (CHT & Oil Temp)
                frame.can_id = 0x18FEEE00;
                frame.data[0] = static_cast<uint8_t>(current_state.cht_c[0]);
                frame.data[1] = static_cast<uint8_t>(current_state.cht_c[1]);
                frame.data[2] = static_cast<uint8_t>(current_state.cht_c[2]);
                frame.data[3] = static_cast<uint8_t>(current_state.cht_c[3]);
                frame.data[4] = static_cast<uint8_t>(current_state.oil_temperature_c);
                frame.data[5] = static_cast<uint8_t>(current_state.oil_pressure_bar * 10.0);
                frame.data[6] = static_cast<uint8_t>(current_state.coolant_temperature_c);
                frame.data[7] = 0x00;
                break;
            case 0xFF10: // Injection & Combustion PGN (new — FADEC injection data)
                frame.can_id = 0x18FF1000;
                {
                    // Byte 0: Ignition timing (1 deg/bit, offset -128)
                    frame.data[0] = static_cast<uint8_t>(
                        std::clamp(current_state.ignition_timing_deg_btdc + 0.5, 0.0, 255.0));
                    // Byte 1: Injection timing BTDC (0.1 deg/bit)
                    frame.data[1] = static_cast<uint8_t>(
                        std::clamp(current_state.injection_timing_btdc * 10.0, 0.0, 255.0));
                    // Bytes 2-3: Injection pulse width (0.01 ms/bit)
                    uint16_t raw_pw = static_cast<uint16_t>(current_state.injection_pulse_width_ms * 100.0);
                    frame.data[2] = raw_pw & 0xFF;
                    frame.data[3] = (raw_pw >> 8) & 0xFF;
                    // Byte 4: Lambda AFR (0.01/bit, offset 0.5)
                    frame.data[4] = static_cast<uint8_t>(
                        std::clamp((current_state.lambda_afr - 0.5) * 100.0, 0.0, 255.0));
                    // Byte 5: Combustion efficiency (1%/bit)
                    frame.data[5] = static_cast<uint8_t>(
                        std::clamp(current_state.combustion_efficiency_pct, 0.0, 255.0));
                    frame.data[6] = 0x00;
                    frame.data[7] = 0x00;
                }
                break;
            default:
                frame.can_id = 0x18FF0000;
                frame.data.fill(0);
                break;
        }
        return frame;
    }

    std::string AeroPistonTwinCore::buildJsonPayload() const {
        // Serialize current engine state to JSON string for HTTP POST to FastAPI /api/telemetry/hardware-ingest
        // Uses only std:: — zero external dependencies
        std::ostringstream j;
        j << std::fixed << std::setprecision(2);
        j << "{";
        j << "\"source\":\"CPP_EMBEDDED_SIM\",";
        j << "\"rpm\":"       << current_state.rpm << ",";
        j << "\"vibration_g\":" << current_state.overall_vibration_g << ",";
        j << "\"cht_c\":[";
        for (int i = 0; i < 4; ++i) {
            j << current_state.cht_c[i];
            if (i < 3) j << ",";
        }
        j << "],";
        j << "\"egt_c\":[";
        for (int i = 0; i < 4; ++i) {
            j << current_state.egt_c[i];
            if (i < 3) j << ",";
        }
        j << "],";
        j << "\"oil_temperature_c\":"    << current_state.oil_temperature_c << ",";
        j << "\"oil_pressure_bar\":"     << current_state.oil_pressure_bar << ",";
        j << "\"manifold_pressure_hpa\":"<< current_state.manifold_pressure_hpa << ",";
        j << "\"bus_voltage_v\":"         << current_state.bus_voltage_v << ",";
        j << "\"ignition_timing_btdc\":" << current_state.ignition_timing_deg_btdc << ",";
        j << "\"injection_timing_btdc\":"<< current_state.injection_timing_btdc << ",";
        j << "\"injection_pulse_ms\":"   << current_state.injection_pulse_width_ms << ",";
        j << "\"lambda_afr\":"           << current_state.lambda_afr << ",";
        j << "\"combustion_eff_pct\":"   << current_state.combustion_efficiency_pct << ",";
        j << "\"health_index\":"         << current_state.health_index << ",";
        j << "\"rul_hours\":"            << current_state.remaining_useful_life_hrs;
        j << "}";
        return j.str();
    }

} // namespace AeroTwin
