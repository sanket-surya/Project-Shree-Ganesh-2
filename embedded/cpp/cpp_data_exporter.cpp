/**
 * @file cpp_data_exporter.cpp
 * @brief High-Speed C++ Physics Data Exporter for ML Training Pipeline (SIH 2026)
 *
 * Runs AeroTwin physics engine for ALL engine profiles (Rotax, Austro, Lycoming)
 * across ALL fault modes and streams CSV rows to stdout for Python XGBoost trainer.
 *
 * Build:  g++ -O3 -std=c++17 cpp_data_exporter.cpp aero_twin_engine.cpp -o cpp_data_exporter
 * Run:    ./cpp_data_exporter 5000 | python ../../ml_models/train_from_cpp.py
 *
 * Output: ~135,000 rows (3 engines × 9 faults × 5000 steps)
 * Speed:  ~50,000 rows/sec (C++ physics advantage)
 */

#include "aero_twin_engine.hpp"
#include <cstdio>
#include <cmath>
#include <algorithm>
#include <cstdlib>

using namespace AeroTwin;

// ── Engine Profiles ───────────────────────────────────────────────────────────
struct EngineProfile {
    const char* id;
    const char* name;
    float rated_rpm;
    float power_kw;
    float nominal_cht_c;
    float nominal_egt_c;
    float compression_ratio;
    float tbo_hours;
    int   engine_code;
};

static const EngineProfile ENGINE_PROFILES[] = {
    { "ROTAX_914F",    "Rotax 914F3 Turbo",             5800.0f,  84.5f, 112.0f, 810.0f,  9.0f, 2000.0f, 0 },
    { "AUSTRO_AE300",  "Austro AE300 Heavy Fuel Diesel", 3880.0f, 123.5f,  96.0f, 720.0f, 18.0f, 1800.0f, 1 },
    { "LYCOMING_IO360","Lycoming IO-360-M1A Flat-4",     2700.0f, 134.0f, 165.0f, 760.0f,  8.5f, 2000.0f, 2 },
};
static const int N_ENGINES = 3;

// ── Fault Modes ───────────────────────────────────────────────────────────────
struct FaultSpec { const char* name; int code; float severity; };

static const FaultSpec FAULT_MODES[] = {
    { "Nominal",           0, 0.0f },
    { "Cylinder_Misfire",  1, 0.7f },
    { "Turbo_Degradation", 2, 0.6f },
    { "Injector_Clogging", 3, 0.8f },
    { "Coolant_Loss",      4, 0.7f },
    { "Oil_Starvation",    5, 0.9f },
    { "Sensor_Drift",      6, 0.5f },
    { "Combustion_Knock",  7, 0.8f },
    { "Valve_Leakage",     8, 0.6f },
};
static const int N_FAULTS = 9;

// ── Apply fault physics ───────────────────────────────────────────────────────
static void applyFault(AeroEngineState& s, const FaultSpec& f) {
    float sv = f.severity;
    switch (f.code) {
        case 1: s.cht_c[0]+=28.0f*sv; s.egt_c[0]-=95.0f*sv; s.overall_vibration_g+=0.85f*sv; s.combustion_efficiency_pct-=15.0f*sv; break;
        case 2: s.manifold_pressure_hpa-=200.0f*sv; s.overall_vibration_g+=0.6f*sv; for(int i=0;i<4;i++) s.cht_c[i]+=18.0f*sv; break;
        case 3: s.fuel_flow_lph-=3.5f*sv; s.egt_c[2]+=85.0f*sv; s.combustion_efficiency_pct-=12.0f*sv; break;
        case 4: s.coolant_temperature_c+=45.0f*sv; for(int i=0;i<4;i++) s.cht_c[i]+=30.0f*sv; break;
        case 5: s.oil_pressure_bar=std::max(0.45f,s.oil_pressure_bar-2.1f*sv); s.oil_temperature_c+=35.0f*sv; s.overall_vibration_g+=2.1f*sv; break;
        case 6: s.cht_c[3]+=58.0f*sv; break;
        case 7: s.overall_vibration_g+=1.8f*sv; s.combustion_efficiency_pct-=18.0f*sv; for(int i=0;i<4;i++) s.cht_c[i]+=22.0f*sv; break;
        case 8: s.egt_c[1]+=115.0f*sv; s.combustion_efficiency_pct-=12.0f*sv; break;
        default: break;
    }
}

int main(int argc, char** argv) {
    int steps_per_combo = (argc > 1) ? std::atoi(argv[1]) : 5000;
    int total = N_ENGINES * N_FAULTS * steps_per_combo;

    std::fprintf(stderr,
        "[CPP-EXPORTER] Engines:%d | Faults:%d | Steps/combo:%d | Total rows:%d\n",
        N_ENGINES, N_FAULTS, steps_per_combo, total);

    // CSV Header
    std::printf(
        "engine_code,engine_name,rpm,manifold_pressure_hpa,power_output_kw,torque_nm,"
        "fuel_flow_lph,fuel_pressure_bar,"
        "cht_cyl_1,cht_cyl_2,cht_cyl_3,cht_cyl_4,"
        "egt_cyl_1,egt_cyl_2,egt_cyl_3,egt_cyl_4,"
        "oil_temperature_c,oil_pressure_bar,coolant_temperature_c,"
        "turbo_rpm,vibration_g,bus_voltage_v,"
        "altitude_m,ambient_temp_c,throttle_pct,"
        "ignition_timing_btdc,injection_timing_btdc,injection_pulse_width_ms,"
        "lambda_afr,combustion_efficiency_pct,"
        "res_cht_spread,res_egt_spread,res_map_residual,res_oil_press_residual,"
        "engine_hours_used,health_index,"
        "fault_code,fault_name,is_anomaly,rul_hours\n"
    );

    // 4 flight profiles: [altitude_m, ambient_temp_c, throttle_pct]
    float fp[4][3] = {
        {1500.0f, 15.0f, 75.0f},   // ISR Loiter
        {7500.0f,-33.5f, 88.0f},   // High-Alt Recon
        { 800.0f, 46.0f, 80.0f},   // Desert Patrol
        {4000.0f,  5.0f,100.0f},   // Combat Climb
    };

    for (int ei = 0; ei < N_ENGINES; ei++) {
        const EngineProfile& eng = ENGINE_PROFILES[ei];
        for (int fi = 0; fi < N_FAULTS; fi++) {
            const FaultSpec& fault = FAULT_MODES[fi];

            AeroPistonTwinCore engine;
            float acc_hours = 0.0f;
            int steps_each = steps_per_combo / 4;

            for (int pi = 0; pi < 4; pi++) {
                FlightCondition fc;
                fc.altitude_m        = fp[pi][0];
                fc.ambient_temp_c    = fp[pi][1];
                fc.throttle_pct      = fp[pi][2];
                fc.true_airspeed_kts = 95.0f;
                fc.ambient_press_hpa = 1013.25f * std::pow(
                    1.0f - 0.0065f * fc.altitude_m / 288.15f, 5.255f);
                engine.setFlightConditions(fc);

                for (int step = 0; step < steps_each; step++) {
                    engine.step(0.05);
                    acc_hours += 0.05f / 3600.0f;

                    AeroEngineState s = engine.getState();

                    // Engine-agnostic scaling: shift CHT/EGT baseline per profile
                    float cht_delta_factor = eng.nominal_cht_c / 112.0f;
                    float egt_delta_factor = eng.nominal_egt_c / 810.0f;
                    for (int k = 0; k < 4; k++) {
                        s.cht_c[k] = (s.cht_c[k] - 112.0f) * cht_delta_factor + eng.nominal_cht_c;
                        s.egt_c[k] = (s.egt_c[k] - 810.0f) * egt_delta_factor + eng.nominal_egt_c;
                    }
                    s.rpm *= (eng.rated_rpm / 5800.0f);

                    // Inject fault
                    applyFault(s, fault);

                    // Compute residuals (engine-agnostic delta features for AI)
                    float cht_max = *std::max_element(s.cht_c, s.cht_c+4);
                    float cht_mean= (s.cht_c[0]+s.cht_c[1]+s.cht_c[2]+s.cht_c[3])/4.0f;
                    float egt_max = *std::max_element(s.egt_c, s.egt_c+4);
                    float egt_mean= (s.egt_c[0]+s.egt_c[1]+s.egt_c[2]+s.egt_c[3])/4.0f;

                    float res_cht_spread = cht_max - cht_mean;
                    float res_egt_spread = egt_max - egt_mean;
                    float res_map_res    = s.manifold_pressure_hpa - 1200.0f;
                    float res_oil_res    = s.oil_pressure_bar - 4.0f;

                    float rul = std::max(0.0f, eng.tbo_hours - acc_hours
                                         - (fault.code>0 ? fault.severity*200.0f : 0.0f));
                    int is_anom = (fault.code != 0 && fault.severity > 0.4f) ? 1 : 0;

                    std::printf(
                        "%d,%s,"
                        "%.2f,%.2f,%.2f,%.2f,%.3f,%.3f,"
                        "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,"
                        "%.2f,%.3f,%.2f,%.0f,%.3f,%.2f,"
                        "%.1f,%.2f,%.1f,"
                        "%.2f,%.2f,%.3f,%.4f,%.2f,"
                        "%.3f,%.3f,%.3f,%.3f,"
                        "%.4f,%.4f,"
                        "%d,%s,%d,%.2f\n",
                        eng.engine_code, eng.name,
                        s.rpm, s.manifold_pressure_hpa, s.power_output_kw, s.torque_nm,
                        s.fuel_flow_lph, s.fuel_pressure_bar,
                        s.cht_c[0],s.cht_c[1],s.cht_c[2],s.cht_c[3],
                        s.egt_c[0],s.egt_c[1],s.egt_c[2],s.egt_c[3],
                        s.oil_temperature_c, s.oil_pressure_bar, s.coolant_temperature_c,
                        (float)s.turbo_rpm, s.overall_vibration_g, s.bus_voltage_v,
                        fc.altitude_m, fc.ambient_temp_c, fc.throttle_pct,
                        s.ignition_timing_deg_btdc, 8.0f, s.injection_pulse_width_ms,
                        s.lambda_afr, s.combustion_efficiency_pct,
                        res_cht_spread, res_egt_spread, res_map_res, res_oil_res,
                        acc_hours, s.health_index,
                        fault.code, fault.name, is_anom, rul
                    );
                }
            }
            std::fprintf(stderr, "[CPP] Engine:%-32s | Fault:%-22s | Done\n",
                eng.name, fault.name);
        }
    }
    return 0;
}
