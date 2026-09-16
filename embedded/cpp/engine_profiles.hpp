/**
 * @file engine_profiles.hpp
 * @brief Multi-Engine Propulsion Architecture Configuration (Engine-Agnostic Core)
 * @project AeroTwin — MALE UAV Aero Engine Digital Twin (SIH 2026 / DRDO)
 * 
 * Demonstrates that the C++ Digital Twin Core is completely decoupled from any single
 * engine platform. Supports dynamic re-parameterization across:
 *   1. Rotax 914F3 (115 HP Turbo Boxer — Tapas-BH-201 / Heron)
 *   2. Austro Engine AE300 (168 HP Heavy Fuel Turbo Diesel — Camcopter S-100)
 *   3. Lycoming IO-360-M1A (180 HP Naturally Aspirated Flat-4 — Tactical UAV)
 */

#pragma once

#include <string>
#include <vector>

namespace AeroTwin {

struct EngineThermodynamicProfile {
    std::string id;
    std::string name;
    std::string architecture;
    std::string fuel_type;
    std::string target_airframes;
    std::string certification_standard;

    // Displacement and Geometry
    double displacement_cc;
    double bore_mm;
    double stroke_mm;
    double compression_ratio;

    // Thermodynamic Limits
    double rated_power_kw;       // Peak continuous output
    double rated_power_hp;       // Horsepower equivalent
    double rated_rpm;            // Redline operating speed
    double max_boost_map_hpa;    // Max manifold absolute pressure (hPa)
    double tbo_hours;            // Time Between Overhaul

    // Nominal Thermal Baseline
    double nominal_cht_c;        // Baseline Cylinder Head Temp (°C)
    double nominal_egt_c;        // Baseline Exhaust Gas Temp (°C)
    double nominal_oil_temp_c;   // Baseline Oil Temp (°C)
    double nominal_oil_press_bar;// Baseline Oil Pressure (bar)
};

class EngineCatalog {
public:
    static inline EngineThermodynamicProfile getRotax914F() {
        return EngineThermodynamicProfile{
            "ROTAX_914F",
            "Rotax 914F3 Turbocharged Boxer",
            "4-Cylinder Horizontally Opposed 4-Stroke Turbo",
            "MOGAS 95 / AVGAS 100LL",
            "DRDO Tapas-BH-201, IAI Heron Mk I, Hermes 900",
            "EASA.E.122 / FAA FAR-33 Certified",
            1211.2, 79.5, 61.0, 9.0,
            84.5, 115.0, 5800.0, 1400.0, 2000.0,
            112.0, 810.0, 92.0, 3.85
        };
    }

    static inline EngineThermodynamicProfile getAustroAE300() {
        return EngineThermodynamicProfile{
            "AUSTRO_AE300",
            "Austro Engine AE300 Heavy Fuel",
            "Inline-4 Common-Rail Turbocharged Diesel",
            "Jet-A1 / Military Diesel F-54 (Single Fuel Concept)",
            "Schiebel Camcopter S-100, Diamond DA42 MPP",
            "EASA.E.118 / JAR-E Certified",
            1991.0, 83.0, 92.0, 18.0,
            123.5, 168.0, 3880.0, 2300.0, 1800.0,
            96.0, 720.0, 88.0, 4.50
        };
    }

    static inline EngineThermodynamicProfile getLycomingIO360() {
        return EngineThermodynamicProfile{
            "LYCOMING_IO360",
            "Lycoming IO-360-M1A Flat-4",
            "4-Cylinder Direct-Drive Fuel Injected Air-Cooled",
            "100LL Aviation Gasoline",
            "Tactical Target Drones, Border Decoy Airframes",
            "FAA TCDS 1E10 Certified",
            5916.0, 130.2, 111.1, 8.5,
            134.0, 180.0, 2700.0, 1013.25, 2000.0,
            165.0, 760.0, 85.0, 4.80
        };
    }

    static inline std::vector<EngineThermodynamicProfile> getAllProfiles() {
        return { getRotax914F(), getAustroAE300(), getLycomingIO360() };
    }
};

} // namespace AeroTwin
