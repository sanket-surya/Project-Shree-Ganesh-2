/**
 * @file main_sim.cpp
 * @brief Standalone Embedded C++ Simulator for Aero Piston Digital Twin (SIH 2026)
 *        Demonstrates: Nominal Operation, Multi-Fault Injection, Injection Timing,
 *        Combustion Efficiency, Degradation Trend Buffer, CAN PGN Streaming,
 *        and JSON Payload generation for FastAPI backend ingestion.
 */

#include "aero_twin_engine.hpp"
#include <iomanip>
#include <thread>
#include <chrono>
#include <cstdio>

using namespace AeroTwin;

// Helper: Print CAN frame as SocketCAN hex string
static void printCanFrame(const CanTelemetryFrame& f, const char* label) {
    std::printf("[CAN] %-24s | ID: 0x%08X | ", label, f.can_id);
    for (int i = 0; i < 8; ++i) std::printf("%02X ", f.data[i]);
    std::printf("| T:%llu us\n", (unsigned long long)f.timestamp_us);
}

// Helper: Print injection/combustion summary
static void printInjectionStats(const AeroEngineState& s) {
    std::printf("  [FADEC INJECTION] IGN: %.1f°BTDC | INJ: %.1f°BTDC | PW: %.2f ms | λ=%.3f | EFF: %.1f%%\n",
        s.ignition_timing_deg_btdc, s.injection_timing_btdc,
        s.injection_pulse_width_ms, s.lambda_afr,
        s.combustion_efficiency_pct);
}

int main(int argc, char** argv) {
    std::printf("=============================================================================\n");
    std::printf("  MALE UAV AERO PISTON ENGINE — EMBEDDED C++ DIGITAL TWIN (SIH 2026)\n");
    std::printf("  Engine : Rotax 914F Turbocharged 4-Cylinder Boxer (115 HP / 84.5 kW)\n");
    std::printf("  Layers : C++17 Physics Core  →  FADEC CAN Bus  →  FastAPI JSON Ingest\n");
    std::printf("=============================================================================\n\n");

    AeroPistonTwinCore engine;

    // ─── PHASE 1: High-Altitude ISR Loiter ──────────────────────────────────
    FlightCondition mission_ha;
    mission_ha.altitude_m        = 7500.0;   // ~25,000 ft
    mission_ha.ambient_temp_c    = -33.5;
    mission_ha.ambient_press_hpa = 382.0;    // ISA at 7500m
    mission_ha.true_airspeed_kts = 115.0;
    mission_ha.throttle_pct      = 88.0;
    engine.setFlightConditions(mission_ha);

    std::printf("► PHASE 1: HIGH-ALTITUDE ISR LOITER  (7500m / 88%% THR)\n");
    std::printf("─────────────────────────────────────────────────────────────────────────────\n");
    for (int step = 0; step < 10; ++step) {
        engine.step(0.1);
        auto s = engine.getState();
        std::printf("[T+%4.1fs] RPM:%5.0f | MAP:%6.1fhPa | CHT:[%.0f,%.0f,%.0f,%.0f]°C"
                    " | Oil:%.1fb/%.0f°C | Vib:%.2fg | Health:%.1f%%\n",
            step * 0.1, s.rpm, s.manifold_pressure_hpa,
            s.cht_c[0], s.cht_c[1], s.cht_c[2], s.cht_c[3],
            s.oil_pressure_bar, s.oil_temperature_c,
            s.overall_vibration_g, s.health_index * 100.0);
    }
    printInjectionStats(engine.getState());

    // CAN PGN Pack & display for Phase 1
    auto can_spd  = engine.packCanFrame(0xFEE0);
    auto can_temp = engine.packCanFrame(0xFEEE);
    auto can_inj  = engine.packCanFrame(0xFF10);
    std::printf("\n  [SocketCAN FRAMES]\n");
    printCanFrame(can_spd,  "PGN-0xFEE0 RPM/MAP   ");
    printCanFrame(can_temp, "PGN-0xFEEE CHT/OIL   ");
    printCanFrame(can_inj,  "PGN-0xFF10 INJECTION  ");

    // ─── PHASE 2: Hot Desert Ops ─────────────────────────────────────────────
    FlightCondition mission_hd;
    mission_hd.altitude_m        = 800.0;
    mission_hd.ambient_temp_c    = 46.0;     // Severe desert heat
    mission_hd.ambient_press_hpa = 932.0;
    mission_hd.true_airspeed_kts = 90.0;
    mission_hd.throttle_pct      = 80.0;
    engine.setFlightConditions(mission_hd);
    engine.clearFault();

    std::printf("\n\n► PHASE 2: HOT DESERT OPS  (800m / 46°C AMB)\n");
    std::printf("─────────────────────────────────────────────────────────────────────────────\n");
    for (int step = 0; step < 8; ++step) {
        engine.step(0.1);
        auto s = engine.getState();
        std::printf("[T+%4.1fs] RPM:%5.0f | EGT:[%.0f,%.0f,%.0f,%.0f]°C | Oil:%.0f°C | Eff:%.1f%%\n",
            step * 0.1, s.rpm,
            s.egt_c[0], s.egt_c[1], s.egt_c[2], s.egt_c[3],
            s.oil_temperature_c, s.combustion_efficiency_pct);
    }
    printInjectionStats(engine.getState());

    // ─── PHASE 3: Mid-Air Fault Injection ───────────────────────────────────
    std::printf("\n\n[!] INJECTING FAULT: CYLINDER_MISFIRE on Cyl-3 (Severity: 0.90)\n");
    engine.injectFault(FaultType::CYLINDER_MISFIRE, 0.90);

    std::printf("► PHASE 3: MISFIRE FAULT — MONITORING DEGRADATION TREND\n");
    std::printf("─────────────────────────────────────────────────────────────────────────────\n");
    for (int step = 0; step < 12; ++step) {
        engine.step(0.1);
        auto s = engine.getState();
        std::printf("[T+%5.1fs] RPM:%5.0f | CHT-3:%5.1f°C(COLD!) | EGT-3:%5.1f°C"
                    " | Vib:%.2fg | Health:%.1f%% | RUL:%.0fh\n",
            (8 + step) * 0.1, s.rpm,
            s.cht_c[2], s.egt_c[2],
            s.overall_vibration_g, s.health_index * 100.0,
            s.remaining_useful_life_hrs);
    }
    printInjectionStats(engine.getState());

    // ─── PHASE 4: Degradation Trend Buffer Summary ───────────────────────────
    const auto& trend = engine.getTrendBuffer();
    int n = trend.count;
    std::printf("\n\n► PHASE 4: DEGRADATION TREND BUFFER  (%d / 60 data points)\n", n);
    std::printf("─────────────────────────────────────────────────────────────────────────────\n");
    if (n > 0) {
        // Find min/max for each channel
        double cht_min=9999, cht_max=-9999;
        double eff_min=9999, eff_max=-9999;
        for (int i = 0; i < n; ++i) {
            int idx = (trend.head - n + i + DegradationTrendBuffer::MAX_POINTS) % DegradationTrendBuffer::MAX_POINTS;
            if (trend.cht_max[idx] < cht_min) cht_min = trend.cht_max[idx];
            if (trend.cht_max[idx] > cht_max) cht_max = trend.cht_max[idx];
            if (trend.efficiency[idx] < eff_min) eff_min = trend.efficiency[idx];
            if (trend.efficiency[idx] > eff_max) eff_max = trend.efficiency[idx];
        }
        std::printf("  CHT max range : %.1f → %.1f °C  (rise: %.1f °C)\n",
            cht_min, cht_max, cht_max - cht_min);
        std::printf("  Combustion Eff: %.1f → %.1f %%  (drop: %.1f %%)\n",
            eff_max, eff_min, eff_max - eff_min);
        // Trend direction
        int last_idx = (trend.head - 1 + DegradationTrendBuffer::MAX_POINTS) % DegradationTrendBuffer::MAX_POINTS;
        int first_idx = (trend.head - std::min(n, 10) + DegradationTrendBuffer::MAX_POINTS) % DegradationTrendBuffer::MAX_POINTS;
        double trend_slope = trend.cht_max[last_idx] - trend.cht_max[first_idx];
        std::printf("  CHT trend slope (last 10 pts): %+.2f °C  → %s\n",
            trend_slope,
            trend_slope > 3.0 ? "RISING CRITICAL ⚠" : trend_slope < -1.0 ? "COOLING ✓" : "STABLE ✓");
    }

    // ─── PHASE 5: JSON Payload for FastAPI HTTP Ingest ───────────────────────
    std::printf("\n\n► PHASE 5: JSON PAYLOAD (for POST to FastAPI /api/telemetry/hardware-ingest)\n");
    std::printf("─────────────────────────────────────────────────────────────────────────────\n");
    std::string json = engine.buildJsonPayload();
    std::printf("%s\n", json.c_str());

    std::printf("\n=============================================================================\n");
    std::printf("  C++ Embedded Twin Simulation COMPLETE. All 3 layers demonstrated:\n");
    std::printf("  [C++ Physics Core] → [CAN PGN Framing] → [JSON → FastAPI Backend]\n");
    std::printf("=============================================================================\n");
    return 0;
}
