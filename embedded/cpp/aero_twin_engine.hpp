/**
 * @file aero_twin_engine.hpp
 * @brief High-Performance Physics-Informed Digital Twin & Telemetry Core for Aero Piston Engines
 *        Targeted for MALE UAV Propulsion Monitoring (Rotax 914F/912 Architecture)
 * @author SIH 2026 Defense Propulsion Digital Twin Team
 */

#ifndef AERO_TWIN_ENGINE_HPP
#define AERO_TWIN_ENGINE_HPP

#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <chrono>
#include <cstdint>
#include <array>

namespace AeroTwin {

    // CAN Bus Telemetry Frame (SocketCAN / ARINC-429 compatible)
    struct CanTelemetryFrame {
        uint32_t can_id;         // Extended CAN ID (e.g. 0x18FEE000 for Engine Speed)
        uint8_t dlc;             // Data length (8 bytes)
        std::array<uint8_t, 8> data;
        uint64_t timestamp_us;   // Microsecond timestamp
    };

    // Engine Environmental & Operational Flight Profile
    struct FlightCondition {
        double altitude_m;       // Flight altitude (0 to 9000 m / 30,000 ft)
        double ambient_temp_c;   // Ambient temperature (-50 to +50 °C)
        double ambient_press_hpa;// Ambient atmospheric pressure
        double true_airspeed_kts;// True Airspeed (0 to 150 kts)
        double throttle_pct;     // Throttle lever angle (0.0 to 100.0 %)
    };

    // Comprehensive Aero Engine State (Rotax 914 4-Cylinder Turbocharged)
    struct AeroEngineState {
        // Operational Dynamics
        double rpm;                      // Engine RPM (idle: 1400, cruise: 5000, max: 5800)
        double manifold_pressure_hpa;    // MAP (ambient to 1400 hPa turbo boost)
        double power_output_kw;          // Mechanical power (0 to 85 kW / 115 HP)
        double torque_nm;                // Engine torque (0 to 145 Nm)
        double fuel_flow_lph;            // Fuel consumption rate (5 to 33 L/h)
        double fuel_pressure_bar;        // Fuel rail pressure (2.8 to 3.2 bar)
        
        // Per-Cylinder Temperatures (°C)
        std::array<double, 4> cht_c;     // Cylinder Head Temperatures (normal: 90 - 135 °C)
        std::array<double, 4> egt_c;     // Exhaust Gas Temperatures (normal: 750 - 880 °C)
        
        // Lubrication & Cooling
        double oil_temperature_c;        // Oil temp (normal: 80 - 110 °C, max 130 °C)
        double oil_pressure_bar;         // Oil pressure (normal: 2.0 - 5.0 bar)
        double coolant_temperature_c;    // Coolant temp (normal: 80 - 105 °C)
        
        // Turbocharger System
        double turbo_rpm;                // Turbocharger shaft speed (0 to 160,000 RPM)
        double wastegate_position_pct;   // Electronic wastegate duty cycle (0 to 100%)
        double intercooler_temp_c;       // Charge air temp after intercooler
        
        // Electrical & Ignition
        double bus_voltage_v;            // FADEC 28V DC bus voltage (27.5 - 28.5 V)
        double alternator_current_a;     // Alternator load (10 - 40 A)
        double ignition_timing_deg_btdc; // Ignition advance (22° to 34° BTDC) — MBT curve

        // Injection & Combustion Parameters (FADEC-Controlled)
        double injection_timing_btdc;    // Injection pulse lead angle before TDC (2° - 12°)
        double injection_pulse_width_ms; // Injector on-time per combustion event (ms)
        double lambda_afr;               // Air-Fuel Ratio lambda (0.9=rich, 1.0=stoich, 1.1=lean)
        double combustion_efficiency_pct;// Thermodynamic combustion efficiency % (85 - 96%)

        // Vibration & Health
        double overall_vibration_g;      // Overall RMS vibration (0.5 to 4.5 G)
        std::array<double, 8> fft_peaks; // Top frequency bin amplitudes (1X, 2X, 3X, Combustion)

        // Health Indicators & Prognostics
        double health_index;             // Composite Engine Health Index (0.0 to 1.0)
        double remaining_useful_life_hrs;// Predicted RUL (hours until maintenance required)

        uint64_t timestamp_ms;
    };

    // Degradation Trend History Buffer
    struct DegradationTrendBuffer {
        static const int MAX_POINTS = 60;
        double cht_max[MAX_POINTS]   = {};
        double egt_max[MAX_POINTS]   = {};
        double oil_temp[MAX_POINTS]  = {};
        double vibration[MAX_POINTS] = {};
        double efficiency[MAX_POINTS]= {};
        int count = 0;
        int head  = 0;  // circular buffer index
    };

    // Active Simulated Fault Modes
    enum class FaultType {
        NONE = 0,
        CYLINDER_MISFIRE = 1,            // Spark plug or coil failure on Cylinder 2/3
        TURBO_DEGRADATION = 2,           // Wastegate sticking / boost leak
        INJECTOR_CLOGGING = 3,           // Fuel starvation / lean combustion
        COOLANT_LOSS = 4,                // Radiator puncture / thermal runaway
        OIL_STARVATION = 5,              // Lubrication pressure drop / bearing friction
        SENSOR_DRIFT = 6,                // CHT/EGT thermocouple calibration drift
        COMBUSTION_KNOCK = 7,            // Detonation due to hot-high ambient or poor octane
        VALVE_LEAKAGE = 8                // Compression loss on cylinder
    };

    class AeroPistonTwinCore {
    private:
        AeroEngineState current_state;
        FlightCondition current_flight;
        FaultType active_fault;
        double fault_severity;           // 0.0 (benign) to 1.0 (critical)
        double accumulated_run_hours;
        DegradationTrendBuffer trend_buf;

        // Internal first-principles thermodynamic constants (Rotax 914F)
        const double DISPLACEMENT_L       = 1.211; // 1211 cc total displacement
        const double COMPRESSION_RATIO    = 9.0;
        const double AIR_FUEL_RATIO_STOICH= 14.7;
        const double SPECIFIC_HEAT_RATIO  = 1.33; // Combustion gases (gamma)
        const double MAX_BOOST_HPA        = 1400.0;
        const double RATED_POWER_KW       = 84.5;
        const double RATED_RPM            = 5800.0;

        void calculateThermodynamics(double dt_sec);
        void calculateMechanicalDynamics(double dt_sec);
        void calculateInjectionAndCombustion();
        void calculateVibrations();
        void applyFaultDynamics(double dt_sec);
        void updateTrendBuffer();

    public:
        AeroPistonTwinCore();
        void setFlightConditions(const FlightCondition& fc);
        void injectFault(FaultType fault, double severity = 1.0);
        void clearFault();
        void step(double dt_sec);

        AeroEngineState getState() const { return current_state; }
        const DegradationTrendBuffer& getTrendBuffer() const { return trend_buf; }
        CanTelemetryFrame packCanFrame(uint16_t pgn) const;
        std::string buildJsonPayload() const; // Serialize state to JSON for HTTP POST to FastAPI
    };

} // namespace AeroTwin

#endif // AERO_TWIN_ENGINE_HPP
