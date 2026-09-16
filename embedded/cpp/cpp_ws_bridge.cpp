/**
 * @file cpp_ws_bridge.cpp
 * @brief C++ Embedded Physics Engine → WebSocket Bridge → React GCS Dashboard
 *        Zero External Libraries. WinSock2 only. Air-Gapped Defense Architecture.
 *        Stack: C/C++ (Physics + Safety-Critical Comms) + React.js (Display)
 *
 *        Port 9001 → ws://localhost:9001 (React connects here for real C++ data)
 */

#include "aero_twin_engine.hpp"
#include "ws_server.hpp"

#include <iostream>
#include <sstream>
#include <thread>
#include <chrono>
#include <iomanip>
#include <atomic>
#include <cstring>

using namespace AeroTwin;

// ─── JSON Builder — no external JSON library needed ───────────────────────────
static std::string escJson(double v, int prec = 2) {
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(prec) << v;
    return ss.str();
}

static std::string buildTelemetryJson(
    const AeroEngineState& s,
    const FlightCondition& fc,
    double accumulated_hours,
    const std::string& active_fault,
    int tick)
{
    std::ostringstream j;
    j << "{"
      // Source identifier
      << "\"source\":\"CPP_EMBEDDED\","
      << "\"tick\":" << tick << ","

      // Flight envelope
      << "\"flight\":{"
        << "\"altitude_m\":"        << escJson(fc.altitude_m, 0)        << ","
        << "\"ambient_temp_c\":"    << escJson(fc.ambient_temp_c, 1)    << ","
        << "\"airspeed_kts\":"      << escJson(fc.true_airspeed_kts, 1) << ","
        << "\"throttle_pct\":"      << escJson(fc.throttle_pct, 1)      << ","
        << "\"mission_name\":\"CPP_LIVE_STREAM\""
      << "},"

      // Core engine state
      << "\"state\":{"
        << "\"rpm\":"                        << escJson(s.rpm, 0)                       << ","
        << "\"manifold_pressure_hpa\":"      << escJson(s.manifold_pressure_hpa, 1)     << ","
        << "\"power_output_kw\":"            << escJson(s.power_output_kw, 2)           << ","
        << "\"torque_nm\":"                  << escJson(s.torque_nm, 2)                 << ","
        << "\"fuel_flow_lph\":"              << escJson(s.fuel_flow_lph, 2)             << ","
        << "\"fuel_pressure_bar\":"          << escJson(s.fuel_pressure_bar, 2)         << ","

        // CHT per cylinder
        << "\"cht_c\":["
          << escJson(s.cht_c[0],1) << ","
          << escJson(s.cht_c[1],1) << ","
          << escJson(s.cht_c[2],1) << ","
          << escJson(s.cht_c[3],1)
        << "],"

        // EGT per cylinder
        << "\"egt_c\":["
          << escJson(s.egt_c[0],1) << ","
          << escJson(s.egt_c[1],1) << ","
          << escJson(s.egt_c[2],1) << ","
          << escJson(s.egt_c[3],1)
        << "],"

        // Lubrication
        << "\"oil_temperature_c\":"   << escJson(s.oil_temperature_c, 1)  << ","
        << "\"oil_pressure_bar\":"    << escJson(s.oil_pressure_bar, 2)   << ","
        << "\"coolant_temp_c\":"      << escJson(s.coolant_temperature_c, 1) << ","

        // Turbocharger
        << "\"turbo_rpm\":"              << escJson(s.turbo_rpm, 0)              << ","
        << "\"wastegate_position_pct\":" << escJson(s.wastegate_position_pct, 1) << ","
        << "\"intercooler_temp_c\":"     << escJson(s.intercooler_temp_c, 1)     << ","

        // Electrical
        << "\"bus_voltage_v\":"       << escJson(s.bus_voltage_v, 2)       << ","
        << "\"alternator_current_a\":" << escJson(s.alternator_current_a, 2) << ","

        // FADEC / Combustion
        << "\"ignition_timing_btdc\":"       << escJson(s.ignition_timing_deg_btdc, 1)  << ","
        << "\"injection_pulse_width_ms\":"   << escJson(s.injection_pulse_width_ms, 3)  << ","
        << "\"lambda_afr\":"                 << escJson(s.lambda_afr, 4)                << ","
        << "\"combustion_efficiency_pct\":"  << escJson(s.combustion_efficiency_pct, 2) << ","

        // Vibration
        << "\"overall_vibration_g\":" << escJson(s.overall_vibration_g, 3) << ","
        << "\"fft_spectrum\":["
          << escJson(s.fft_peaks[0],3) << ","
          << escJson(s.fft_peaks[1],3) << ","
          << escJson(s.fft_peaks[2],3) << ","
          << escJson(s.fft_peaks[3],3)
        << "],"

        // Health
        << "\"health_index\":"           << escJson(s.health_index, 4)             << ","
        << "\"remaining_useful_life_hrs\":" << escJson(s.remaining_useful_life_hrs, 1) << ","
        << "\"accumulated_hours\":"      << escJson(accumulated_hours, 2)          << ","
        << "\"active_fault\":\""         << active_fault                            << "\""
      << "}"
    << "}";

    return j.str();
}

// ─── Fault injection state ─────────────────────────────────────────────────────
static std::atomic<bool> injectFault{false};
static std::atomic<int>  faultType{0};
// 0=none, 1=Injector_Clogging, 2=Turbo_Degradation, 3=Oil_Starvation,
// 4=Coolant_Loss, 5=Cylinder_Misfire, 6=Combustion_Knock

static std::string faultName(int ft) {
    switch(ft) {
        case 1: return "Injector_Clogging";
        case 2: return "Turbo_Degradation";
        case 3: return "Oil_Starvation";
        case 4: return "Coolant_Loss";
        case 5: return "Cylinder_Misfire";
        case 6: return "Combustion_Knock";
        default: return "NONE";
    }
}

// ─── Main ─────────────────────────────────────────────────────────────────────
int main() {
    std::cout << "=============================================================\n";
    std::cout << "  AEROTWIN — C++ EMBEDDED PHYSICS ENGINE (SIH 2026)\n";
    std::cout << "  Engine  : Rotax 914F Turbocharged Boxer (115HP / 84.5kW)\n";
    std::cout << "  Stack   : C/C++ Physics Core + React.js GCS Dashboard\n";
    std::cout << "  Comms   : WinSock2 WebSocket (ws://127.0.0.1:9001)\n";
    std::cout << "  API Key : NONE — 100% Air-Gapped Architecture\n";
    std::cout << "=============================================================\n\n";

    // ─── Init Physics Engine ──────────────────────────────────────────────────
    AeroPistonTwinCore engine;

    FlightCondition nominal;
    nominal.altitude_m         = 5000.0;
    nominal.ambient_temp_c     = -11.0;
    nominal.ambient_press_hpa  = 540.0;
    nominal.true_airspeed_kts  = 110.0;
    nominal.throttle_pct       = 82.0;
    engine.setFlightConditions(nominal);

    std::cout << "[AeroTwin C++] Physics engine initialized — Rotax 914F nominal state.\n";

    // ─── Init WebSocket Server ────────────────────────────────────────────────
    AeroTwinWsServer wsServer(9001);
    if (!wsServer.start()) {
        std::cerr << "[ERROR] Failed to start WebSocket server on port 9001.\n";
        return 1;
    }

    // Accept loop in background thread
    std::thread acceptThread([&]() { wsServer.acceptLoop(); });
    acceptThread.detach();

    std::cout << "[AeroTwin C++] Streaming telemetry at 20Hz to React Dashboard...\n";
    std::cout << "[AeroTwin C++] Open browser: http://localhost:5173  (React GCS)\n\n";

    // ─── Main Telemetry Loop — 20Hz (50ms per tick) ───────────────────────────
    double accHours = 0.0;
    const double dt       = 0.05;   // 50ms per step = 20Hz
    const double dt_hours = dt / 3600.0;
    int tick = 0;

    while (true) {
        engine.step(dt);
        accHours += dt_hours;
        tick++;

        // Apply / clear fault
        if (injectFault.load() && faultType.load() > 0) {
            engine.injectFault(faultName(faultType.load()), 0.85);
        } else {
            engine.clearFault();
        }

        auto state = engine.getState();
        std::string fault = (injectFault && faultType > 0) ? faultName(faultType.load()) : "NONE";

        // Build and send JSON
        std::string json = buildTelemetryJson(state, nominal, accHours, fault, tick);
        wsServer.sendJson(json);

        // Console heartbeat every 5 seconds (100 ticks)
        if (tick % 100 == 0) {
            std::cout << "[T+" << std::fixed << std::setprecision(1)
                      << (tick * dt) << "s]"
                      << " RPM:" << std::setprecision(0) << state.rpm
                      << " | CHT_avg:" << std::setprecision(1)
                      << ((state.cht_c[0]+state.cht_c[1]+state.cht_c[2]+state.cht_c[3])/4.0)
                      << "°C | Health:" << std::setprecision(1)
                      << (state.health_index * 100.0) << "%"
                      << " | Clients:" << (wsServer.clientConnected ? 1 : 0)
                      << "\n";
        }

        // 20Hz sleep
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    wsServer.stop();
    return 0;
}
