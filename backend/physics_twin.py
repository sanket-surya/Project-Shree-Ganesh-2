"""
Real-Time Physics-Informed Digital Twin Simulation Engine
Continuous thermodynamic & mechanical model of Rotax 914F Turbocharged Aero Piston Engine.
"""

import time
import math
from datetime import datetime, timedelta
import numpy as np

ENGINE_PROFILES = {
    "ROTAX_914F": {
        "id": "ROTAX_914F",
        "name": "Rotax 914F3 Turbocharged Boxer",
        "type": "4-Cylinder Horizontally Opposed Turbo",
        "power_hp": 115.0,
        "power_kw": 84.5,
        "rated_rpm": 5800.0,
        "max_boost_map_hpa": 1400.0,
        "displacement_cc": 1211.2,
        "bore_mm": 79.5,
        "stroke_mm": 61.0,
        "compression_ratio": 9.0,
        "fuel_type": "MOGAS 95 / AVGAS 100LL",
        "tbo_hours": 2000.0,
        "nominal_cht_c": 112.0,
        "nominal_egt_c": 810.0,
        "nominal_oil_bar": 3.8,
        "nominal_oil_c": 95.0,
        "nominal_lambda": 1.02,
        "cht_factors": [0.98, 0.99, 1.03, 1.02],
        "egt_offsets": [0.0, 5.0, -3.0, 2.0],
        "airframes": "DRDO Tapas-BH-201, IAI Heron Mk I, Hermes 900",
        "certification": "EASA.E.122 / FAR-33"
    },
    "AUSTRO_AE300": {
        "id": "AUSTRO_AE300",
        "name": "Austro Engine AE300 Heavy Fuel",
        "type": "Inline-4 Turbocharged Common-Rail Diesel",
        "power_hp": 168.0,
        "power_kw": 123.5,
        "rated_rpm": 3880.0,
        "max_boost_map_hpa": 2300.0,
        "displacement_cc": 1991.0,
        "bore_mm": 83.0,
        "stroke_mm": 92.0,
        "compression_ratio": 18.0,
        "fuel_type": "Jet-A1 / Military Diesel F-54",
        "tbo_hours": 1800.0,
        "nominal_cht_c": 96.0,
        "nominal_egt_c": 720.0,
        "nominal_oil_bar": 4.2,
        "nominal_oil_c": 82.0,
        "nominal_lambda": 1.6,
        "cht_factors": [1.00, 1.01, 1.01, 1.02],
        "egt_offsets": [0.0, 2.0, 2.0, 4.0],
        "airframes": "Schiebel Camcopter S-100, Diamond DA42 MPP",
        "certification": "EASA.E.118 / JAR-E"
    },
    "LYCOMING_IO360": {
        "id": "LYCOMING_IO360",
        "name": "Lycoming IO-360-M1A Flat-4",
        "type": "4-Cylinder Direct-Drive Fuel Injected",
        "power_hp": 180.0,
        "power_kw": 134.0,
        "rated_rpm": 2700.0,
        "max_boost_map_hpa": 1013.25,
        "displacement_cc": 5916.0,
        "bore_mm": 130.2,
        "stroke_mm": 111.1,
        "compression_ratio": 8.5,
        "fuel_type": "100LL Aviation Gasoline",
        "tbo_hours": 2000.0,
        "nominal_cht_c": 165.0,
        "nominal_egt_c": 760.0,
        "nominal_oil_bar": 3.5,
        "nominal_oil_c": 100.0,
        "nominal_lambda": 1.0,
        "cht_factors": [0.97, 0.99, 1.04, 1.06],
        "egt_offsets": [0.0, 8.0, -5.0, 10.0],
        "airframes": "MALE Recon Drones, Target Decoy Platforms",
        "certification": "FAA TCDS 1E10"
    }
}


# ============================================================
# ISA STANDARD ATMOSPHERE MODEL (DO-278A / ICAO Doc 7488)
# Used for altitude-corrected engine performance predictions
# ============================================================
class ISAAtmosphereModel:
    """
    International Standard Atmosphere (ISA) model for MALE UAV altitude corrections.
    Troposphere model (0–11,000m) per ICAO Doc 7488/3.
    Covers Rotax 914F operational envelope up to 20,000 ft.
    """
    T0  = 288.15    # Sea level temperature (K)
    P0  = 101325.0  # Sea level pressure (Pa)
    L   = 0.0065    # Lapse rate (K/m)
    R   = 287.05    # Gas constant for dry air (J/kg·K)
    g   = 9.80665   # Gravity (m/s²)
    rho0 = 1.2250   # Sea level density (kg/m³)

    # Rotax 914F turbocharger critical altitude (maintains 100% power below)
    ROTAX_914F_CRITICAL_ALT_M = 3810.0  # ~12,500 ft

    @classmethod
    def conditions(cls, altitude_m: float) -> dict:
        """Returns ISA temperature, pressure, density at given altitude."""
        alt = max(0.0, min(altitude_m, 11000.0))  # Clamp to troposphere
        T   = cls.T0 - cls.L * alt
        P   = cls.P0 * ((1.0 - cls.L * alt / cls.T0) ** (cls.g / (cls.L * cls.R)))
        rho = P / (cls.R * T)
        sigma = rho / cls.rho0
        return {
            "temperature_k": T,
            "temperature_c": T - 273.15,
            "pressure_pa": P,
            "pressure_hpa": P / 100.0,
            "density_kgm3": rho,
            "density_ratio": sigma,
            "altitude_m": alt,
            "altitude_ft": alt * 3.28084,
        }

    @classmethod
    def power_fraction(cls, altitude_m: float, turbocharged: bool = True,
                       critical_alt_m: float = None) -> float:
        """
        Returns power fraction (0–1.0) at altitude vs sea level.
        Turbocharged engine maintains 1.0 up to critical_alt_m,
        then falls off per density ratio^0.5.
        """
        crit = critical_alt_m if critical_alt_m else cls.ROTAX_914F_CRITICAL_ALT_M
        isa = cls.conditions(altitude_m)
        sigma = isa["density_ratio"]
        if turbocharged and altitude_m <= crit:
            return 1.0
        return sigma ** 0.5

    @classmethod
    def bsfc_altitude_correction(cls, bsfc_sl: float, altitude_m: float) -> float:
        """
        BSFC correction for altitude using GA piston empirical constants.
        From SAE J1349 / BSFC_alt = BSFC_SL × ((σ - E)/(1 - E))^F
        Constants E=0.065, F=1.117 (GA piston engine standard).
        """
        isa = cls.conditions(altitude_m)
        sigma = max(0.1, isa["density_ratio"])
        E, F = 0.065, 1.117
        return bsfc_sl * ((sigma - E) / (1.0 - E)) ** F


# ============================================================
# MISSION RELIABILITY INDEX (MRI) CALCULATOR
# Implements: Weibull failure model + AHP multi-parameter fusion
# Directly satisfies PS SIH26054: "Mission Reliability Enhancement"
# ============================================================
class MissionReliabilityIndex:
    """
    Pre-flight and real-time Mission Reliability Index calculator.
    Uses Weibull distribution for failure probability estimation
    and AHP (Analytic Hierarchy Process) for multi-parameter fusion.

    Output: MRI score 0.0–1.0
      ≥ 0.85 → GO  (green)
      0.70–0.85 → CAUTION (amber)
      < 0.70  → NO-GO (red)
    """

    # AHP weights (tuned for safety-critical UAV context)
    W_HI         = 0.35   # Overall Health Index (AHP priority 1)
    W_FAIL_PROB  = 0.30   # 1 - P(failure during mission) (AHP priority 2)
    W_RUL_RATIO  = 0.25   # RUL / mission_duration (AHP priority 3)
    W_OIL_MARGIN = 0.10   # Oil pressure margin ratio (AHP priority 4)

    # Weibull parameters for piston aircraft engines
    WEIBULL_BETA  = 3.5    # Shape: wear-out failure mode (β > 1)
    WEIBULL_ETA   = 3200.0 # Scale: characteristic life ≈ MTTF (flight hours)

    # Decision thresholds
    GO_THRESHOLD      = 0.85
    CAUTION_THRESHOLD = 0.70

    @classmethod
    def weibull_failure_prob(cls, hours_accumulated: float,
                              mission_duration_hrs: float) -> float:
        """
        P(failure during mission) using Weibull reliability:
          R(t) = e^(-(t/η)^β)
          P_fail = R(t_start) - R(t_end)  (conditional probability)
        """
        import math
        t_start = max(0.0, hours_accumulated)
        t_end   = t_start + max(0.1, mission_duration_hrs)
        try:
            R_start = math.exp(-((t_start / cls.WEIBULL_ETA) ** cls.WEIBULL_BETA))
            R_end   = math.exp(-((t_end   / cls.WEIBULL_ETA) ** cls.WEIBULL_BETA))
            return max(0.0, min(1.0, R_start - R_end))
        except Exception:
            return 0.05  # Default conservative estimate

    @classmethod
    def compute(cls,
                health_index: float,
                rul_hours: float,
                mission_duration_hrs: float,
                hours_accumulated: float,
                oil_press_bar: float,
                oil_press_nominal: float = 3.8) -> dict:
        """
        Compute Mission Reliability Index.

        Args:
            health_index:         Overall HI (0–1.0)
            rul_hours:            Remaining Useful Life in hours
            mission_duration_hrs: Planned mission duration in hours
            hours_accumulated:    Engine hours flown so far
            oil_press_bar:        Current oil pressure reading
            oil_press_nominal:    Engine nominal oil pressure

        Returns dict with MRI score, decision, and sub-indices.
        """
        # Sub-index 1: Health Index (already 0-1)
        hi_norm = max(0.0, min(1.0, health_index))

        # Sub-index 2: 1 - P(failure during mission)
        p_fail  = cls.weibull_failure_prob(hours_accumulated, mission_duration_hrs)
        fail_si = max(0.0, 1.0 - p_fail * 20.0)  # Scale: 5% fail → ~0 SI

        # Sub-index 3: RUL vs mission duration (margin ratio, capped at 1.0)
        rul_ratio = min(1.0, rul_hours / max(1.0, mission_duration_hrs * 5.0))

        # Sub-index 4: Oil pressure margin
        oil_margin = max(0.0, min(1.0, oil_press_bar / max(0.1, oil_press_nominal)))

        # AHP weighted sum
        mri = (cls.W_HI         * hi_norm  +
               cls.W_FAIL_PROB  * fail_si  +
               cls.W_RUL_RATIO  * rul_ratio +
               cls.W_OIL_MARGIN * oil_margin)
        mri = max(0.0, min(1.0, mri))

        # Decision
        if mri >= cls.GO_THRESHOLD:
            decision = "GO"
            decision_color = "green"
        elif mri >= cls.CAUTION_THRESHOLD:
            decision = "CAUTION"
            decision_color = "amber"
        else:
            decision = "NO-GO"
            decision_color = "red"

        return {
            "mri_score":          round(mri, 4),
            "mri_pct":            round(mri * 100, 1),
            "decision":           decision,
            "decision_color":     decision_color,
            "sub_health_index":   round(hi_norm, 4),
            "sub_fail_prob_si":   round(fail_si, 4),
            "p_fail_mission":     round(p_fail * 100, 3),
            "sub_rul_ratio":      round(rul_ratio, 4),
            "sub_oil_margin":     round(oil_margin, 4),
            "rul_hours":          round(rul_hours, 1),
            "mission_duration_hrs": round(mission_duration_hrs, 2),
            "hours_accumulated":  round(hours_accumulated, 1),
            "weibull_beta":       cls.WEIBULL_BETA,
            "weibull_eta":        cls.WEIBULL_ETA,
            "go_threshold":       cls.GO_THRESHOLD,
            "caution_threshold":  cls.CAUTION_THRESHOLD,
        }


class AeroPistonTwinPhysics:

    def __init__(self):
        # Engine Architecture (Modular Engine-Agnostic Core)
        self.active_engine_id = "ROTAX_914F"
        prof = ENGINE_PROFILES[self.active_engine_id]
        self.engine_name = prof["name"]
        self.engine_type = prof["type"]
        self.engine_power_hp = prof["power_hp"]
        self.engine_power_kw = prof["power_kw"]
        self.rated_rpm = prof["rated_rpm"]
        self.max_boost_map_hpa = prof["max_boost_map_hpa"]
        self.displacement_cc = prof["displacement_cc"]
        self.fuel_type = prof["fuel_type"]
        self.tbo_hours = prof["tbo_hours"]
        self.airframes = prof["airframes"]
        self.certification = prof["certification"]
        self.nominal_cht_c = prof.get("nominal_cht_c", 112.0)
        self.nominal_egt_c = prof.get("nominal_egt_c", 810.0)
        self.nominal_oil_bar = prof.get("nominal_oil_bar", 3.8)
        self.nominal_oil_c = prof.get("nominal_oil_c", 95.0)
        self.nominal_lambda = prof.get("nominal_lambda", 1.02)
        self.cht_factors = prof.get("cht_factors", [0.98, 0.99, 1.03, 1.02])
        self.egt_offsets = prof.get("egt_offsets", [0.0, 5.0, -3.0, 2.0])

        # Flight Envelope Parameters
        self.altitude_m = 1500.0 # 5000 ft
        self.ambient_temp_c = 15.0 - (self.altitude_m * 0.0065)
        self.ambient_press_hpa = 1013.25 * ((1.0 - (0.0065 * self.altitude_m / 288.15)) ** 5.255)
        self.airspeed_kts = 95.0
        self.throttle_pct = 75.0
        self.mission_name = "Nominal ISR Loiter"

        # Engine Dynamic States
        self.rpm = 5000.0
        self.fuel_press_bar = 3.0
        
        # Initialize in thermodynamic equilibrium
        target_map = self.ambient_press_hpa + (self.throttle_pct / 100.0) * (self.max_boost_map_hpa - self.ambient_press_hpa)
        self.manifold_pressure_hpa = target_map
        self.power_kw = (self.manifold_pressure_hpa / 1013.25) * (self.rpm / self.rated_rpm) * self.engine_power_kw
        self.torque_nm = (self.power_kw * 9548.8 / max(self.rpm, 100.0))
        self.fuel_flow_lph = (self.power_kw * 0.285 / 0.72)
        
        # Per-Cylinder Temperatures
        self.cht_c = [110.0, 111.5, 113.0, 112.0]
        self.egt_c = [810.0, 815.0, 808.0, 812.0]
        
        # Oil & Cooling
        self.oil_temp_c = 92.0
        self.oil_press_bar = 3.85
        self.coolant_temp_c = 88.0
        
        # Turbocharger
        self.turbo_rpm = 112000.0
        self.wastegate_pct = 42.0
        self.intercooler_temp_c = 38.0
        
        # Electrical & Vibration
        self.bus_voltage_v = 28.1
        self.alternator_current_a = 22.4
        self.ignition_timing_btdc = 26.0
        self.overall_vibration_g = 1.45
        self.fft_spectrum = [0.4, 0.9, 0.25, 0.55, 0.12, 0.08, 0.05, 0.03]

        # Combustion & Injection
        self.injection_timing_btdc = 8.5   # Injection pulse lead angle before TDC (deg)
        self.injection_pulse_width_ms = 4.2 # Injector on-time per cycle (ms)
        self.combustion_efficiency_pct = 92.5  # Thermodynamic combustion efficiency %
        self.lambda_afr = 1.02  # Air-Fuel Ratio lambda (1.0 = stoichiometric)

        # Health & Faults (Supports Multiple Concurrent Compound Faults)
        self.active_faults = {} # Dict[str, float] of fault_type -> severity
        self.accumulated_hours = 124.5
        self.last_update = time.time()
        self.is_mitigated = False
        self.engine_seized = False

        # Rolling Degradation Trend History Buffer (last 60 steps ~ 3 seconds at 20Hz)
        self._trend_max = 60
        self.trend_cht_max = []
        self.trend_egt_max = []
        self.trend_oil_temp = []
        self.trend_vibration = []
        self.trend_health_score = []
        self.trend_efficiency = []
        self.trend_timestamps = []

    @property
    def active_fault(self) -> str:
        if not self.active_faults:
            return "NONE"
        return " + ".join(self.active_faults.keys())

    @property
    def fault_severity(self) -> float:
        if not self.active_faults:
            return 0.0
        return max(self.active_faults.values())

    def set_mission_profile(self, profile_name: str, altitude: float = None, ambient_temp: float = None, throttle: float = None):
        self.mission_name = profile_name
        if profile_name == "High_Altitude_Loiter":
            self.altitude_m = 7500.0 # ~25,000 ft
            self.ambient_temp_c = -33.5
            self.throttle_pct = 88.0
            self.airspeed_kts = 115.0
        elif profile_name == "Hot_Desert_Ops":
            self.altitude_m = 800.0
            self.ambient_temp_c = 46.0 # Severe desert heat
            self.throttle_pct = 80.0
            self.airspeed_kts = 90.0
        elif profile_name == "Rapid_Climb":
            self.altitude_m = 2500.0
            self.ambient_temp_c = -1.0
            self.throttle_pct = 100.0 # Full takeoff power
            self.airspeed_kts = 85.0
        elif profile_name == "Night_Maritime_ISR":
            self.altitude_m = 1200.0
            self.ambient_temp_c = 18.0
            self.throttle_pct = 68.0
            self.airspeed_kts = 95.0
        else: # Nominal
            self.altitude_m = 1500.0
            self.ambient_temp_c = 5.2
            self.throttle_pct = 75.0
            self.airspeed_kts = 95.0

        if altitude is not None: self.altitude_m = altitude
        if ambient_temp is not None: self.ambient_temp_c = ambient_temp
        if throttle is not None: self.throttle_pct = throttle

        self.ambient_press_hpa = 1013.25 * ((1.0 - (0.0065 * self.altitude_m / 288.15)) ** 5.255)

    def inject_fault(self, fault_type: str, severity: float = 1.0):
        if fault_type == "NONE":
            self.clear_fault()
            return
        self.active_faults[fault_type] = max(0.0, min(1.0, severity))

    def toggle_fault(self, fault_type: str, severity: float = 1.0):
        if fault_type in self.active_faults:
            del self.active_faults[fault_type]
        else:
            self.active_faults[fault_type] = max(0.0, min(1.0, severity))

    def remove_fault(self, fault_type: str):
        if fault_type in self.active_faults:
            del self.active_faults[fault_type]

    def clear_fault(self):
        self.active_faults.clear()
        self.is_mitigated = False
        self.engine_seized = False

    def apply_ai_mitigation(self):
        """Engages autonomous AI FADEC emergency countermeasure:
        - Auto-derates throttle to 50%
        - Enriches fuel mixture to cool cylinder heads (lambda 0.92)
        - Halts cascade degradation and restores thermal equilibrium
        - Re-stabilizes engine at 3300 RPM safe loiter / RTB glide mode
        """
        self.is_mitigated = True
        self.engine_seized = False
        self.throttle_pct = 50.0
        self.active_faults.clear()
        self.oil_press_bar = 3.3
        self.lambda_afr = 0.92
        self.combustion_efficiency_pct = 88.5

    def trigger_engine_seizure(self):
        """Called at catastrophic Stage 4 without mitigation:
        Engine physically seizes due to thermal expansion and bearing friction.
        RPM drops to 0, electrical charging stops, bus on battery power.
        """
        self.engine_seized = True
        self.is_mitigated = False
        self.rpm = 0.0
        self.power_kw = 0.0
        self.torque_nm = 0.0
        self.turbo_rpm = 0.0
        self.fuel_flow_lph = 0.0
        self.oil_press_bar = 0.05
        self.alternator_current_a = 0.0
        self.bus_voltage_v = 23.8
        self.overall_vibration_g = 0.02
        self.fft_spectrum = [0.01] * 8

    def step(self, dt_sec: float = 0.05):
        now = time.time()

        if self.engine_seized:
            self.rpm = 0.0
            self.power_kw = 0.0
            self.torque_nm = 0.0
            self.turbo_rpm = 0.0
            self.fuel_flow_lph = 0.0
            self.oil_press_bar = 0.05
            self.alternator_current_a = 0.0
            self.bus_voltage_v = 23.8
            self.overall_vibration_g = 0.02
            self.fft_spectrum = [0.01] * 8
            self.manifold_pressure_hpa = self.ambient_press_hpa
            for k in range(4):
                self.cht_c[k] = max(self.ambient_temp_c, self.cht_c[k] - dt_sec * 0.8)
                self.egt_c[k] = max(self.ambient_temp_c + 20.0, self.egt_c[k] - dt_sec * 12.0)
            self.accumulated_hours += (dt_sec / 3600.0)
            self.last_update = now
            return

        # Base target RPM and boost from throttle (dynamic per engine architecture)
        idle_rpm = self.rated_rpm * 0.25
        target_rpm = idle_rpm + (self.throttle_pct / 100.0) * (self.rated_rpm - idle_rpm)
        max_boost = self.max_boost_map_hpa
        has_turbo = max_boost > 1050.0
        if has_turbo:
            target_map = self.ambient_press_hpa + (self.throttle_pct / 100.0) * (max_boost - self.ambient_press_hpa)
        else:
            target_map = self.ambient_press_hpa * (self.throttle_pct / 100.0) * 0.95

        if self.is_mitigated:
            target_rpm = self.rated_rpm * 0.55
            target_map = self.ambient_press_hpa * 0.50 if not has_turbo else (self.ambient_press_hpa + 0.45 * (max_boost - self.ambient_press_hpa))

        # Couple physical fault degradation directly to RPM and Manifold Pressure
        if "Turbo_Degradation" in self.active_faults and max_boost > 1050.0:
            sev = self.active_faults["Turbo_Degradation"]
            target_map -= 280.0 * sev              # Wastegate stuck / boost collapse
            target_rpm -= 240.0 * sev              # Power loss drops propeller speed

        if "Cylinder_Misfire" in self.active_faults:
            sev = self.active_faults["Cylinder_Misfire"]
            target_rpm -= 410.0 * sev              # Dead cylinder drops torque immediately
            target_rpm += float(np.random.normal(0, 22.0 * sev)) # Cyclic roughness hunting
            target_map += float(np.random.normal(0, 14.0 * sev)) # Intake runner pulsation

        if "Oil_Starvation" in self.active_faults:
            sev = self.active_faults["Oil_Starvation"]
            target_rpm -= 480.0 * sev              # Severe journal bearing boundary friction drag

        if "Combustion_Knock" in self.active_faults:
            sev = self.active_faults["Combustion_Knock"]
            target_rpm -= 180.0 * sev              # Detonation shockwave counter-torque
            target_rpm += float(np.random.normal(0, 20.0 * sev)) # Knock hunting oscillation

        if "Valve_Leakage" in self.active_faults:
            sev = self.active_faults["Valve_Leakage"]
            target_rpm -= 220.0 * sev              # Compression loss
            target_map += 42.0 * sev               # Valve blowby backpressure into intake

        if "Injector_Clogging" in self.active_faults:
            sev = self.active_faults["Injector_Clogging"]
            target_rpm -= 150.0 * sev              # Partial lean cylinder power shortfall

        target_rpm = max(idle_rpm * 0.75, target_rpm)
        min_map = (self.ambient_press_hpa - 120.0) if has_turbo else 250.0
        target_map = max(min_map, target_map)

        self.rpm += (target_rpm - self.rpm) * min(1.0, dt_sec * 3.5)
        self.manifold_pressure_hpa += (target_map - self.manifold_pressure_hpa) * min(1.0, dt_sec * 4.0)

        # Power & Fuel Flow (clipped to engine envelope)
        is_diesel = self.fuel_type.startswith("Jet") or "Diesel" in self.engine_name
        has_turbo = max_boost > 1050.0

        pwr_raw = (self.manifold_pressure_hpa / 1013.25) * (self.rpm / self.rated_rpm) * self.engine_power_kw
        self.power_kw = min(self.engine_power_kw * 1.02, max(0.0, pwr_raw))
        self.torque_nm = (self.power_kw * 9548.8 / max(self.rpm, 100.0))

        fuel_sfc = 0.210 if is_diesel else (0.310 if not has_turbo else 0.285)
        fuel_density = 0.84 if is_diesel else 0.72
        self.fuel_flow_lph = (self.power_kw * fuel_sfc / fuel_density)
        self.fuel_press_bar = 1.8 if is_diesel else 3.0

        # Turbocharger (Naturally aspirated Lycoming has no turbo spool)
        if has_turbo:
            target_turbo_rpm = (self.manifold_pressure_hpa / max_boost) * (180000.0 if is_diesel else 145000.0)
            self.turbo_rpm += (target_turbo_rpm - self.turbo_rpm) * min(1.0, dt_sec * 2.0)
            self.wastegate_pct = max(0.0, min(100.0, ((self.manifold_pressure_hpa - (max_boost - 220.0)) / 220.0) * 100.0))
        else:
            self.turbo_rpm = 0.0
            self.wastegate_pct = 0.0

        # Thermal heat transfer (aligned with physics dataset)
        ram_cooling = (self.airspeed_kts / 100.0) * (8.0 if is_diesel else 15.0)
        if is_diesel:
            cht_base = 70.0 + (self.power_kw / self.engine_power_kw) * 35.0 + (self.ambient_temp_c * 0.15)
            egt_base = self.nominal_egt_c - 100.0 + (self.manifold_pressure_hpa / max_boost) * 150.0
        else:
            cht_base = self.nominal_cht_c - 40.0 + (self.power_kw / self.engine_power_kw) * 60.0 - ram_cooling + (self.ambient_temp_c * 0.28)
            egt_base = self.nominal_egt_c - 150.0 + (self.manifold_pressure_hpa / 1300.0) * 180.0

        for i in range(4):
            target_cht = cht_base * self.cht_factors[i]
            self.cht_c[i] += (target_cht - self.cht_c[i]) * min(1.0, dt_sec * 0.2)

            target_egt = egt_base + self.egt_offsets[i]
            self.egt_c[i] += (target_egt - self.egt_c[i]) * min(1.0, dt_sec * 0.6)

        # Oil & Cooling
        target_oil_temp = (self.nominal_oil_c - 15.0) + (self.power_kw * 0.36) - (ram_cooling * 0.4) + (self.ambient_temp_c * 0.15)
        self.oil_temp_c += (target_oil_temp - self.oil_temp_c) * min(1.0, dt_sec * 0.1)
        if "Oil_Starvation" not in self.active_faults:
            exp_oil = (self.rpm / self.rated_rpm) * self.nominal_oil_bar * (1.0 - (self.oil_temp_c - self.nominal_oil_c) * 0.004)
            self.oil_press_bar += (exp_oil - self.oil_press_bar) * min(1.0, dt_sec * 2.0)
        if "Coolant_Loss" not in self.active_faults:
            self.coolant_temp_c = self.oil_temp_c * (0.85 if is_diesel else 0.90)

        # Vibrations (Base)
        base_vib = 0.85 + (self.rpm / self.rated_rpm) * 0.8
        self.fft_spectrum = [
            round(base_vib * 0.38 + np.random.normal(0, 0.01), 3),
            round(base_vib * 0.88 + np.random.normal(0, 0.02), 3),
            round(base_vib * 0.24 + np.random.normal(0, 0.01), 3),
            round(base_vib * 0.58 + np.random.normal(0, 0.02), 3),
            0.12, 0.07, 0.04, 0.02
        ]
        self.overall_vibration_g = base_vib

        # Injection Timing & Combustion Efficiency (Physics-Based per Engine Cycle)
        if is_diesel:
            self.ignition_timing_btdc = 0.0  # Compression ignition (no spark plugs)
            self.injection_timing_btdc = 5.0 + (self.rpm / self.rated_rpm) * 15.0
            self.lambda_afr = round(self.nominal_lambda - (self.throttle_pct / 100.0) * 0.3 + float(np.random.normal(0, 0.005)), 3)
        else:
            self.ignition_timing_btdc = 18.0 + (self.rpm / self.rated_rpm) * 14.0 - (self.manifold_pressure_hpa / self.max_boost_map_hpa) * 6.0
            self.injection_timing_btdc = 4.0 + (self.throttle_pct / 100.0) * 8.0
            self.lambda_afr = round(self.nominal_lambda - (self.throttle_pct / 100.0) * 0.08 + float(np.random.normal(0, 0.003)), 3)

        self.injection_pulse_width_ms = round(1.5 + (self.fuel_flow_lph / max(10.0, self.engine_power_kw * 0.4)) * 4.0, 2)
        # Combustion efficiency from MAP utilization, AFR deviation, and vibration
        afr_penalty = abs(self.lambda_afr - self.nominal_lambda) * 12.0
        vib_penalty = max(0, (self.overall_vibration_g - 1.5) * 3.0)
        self.combustion_efficiency_pct = round(max(50.0, 96.0 - afr_penalty - vib_penalty), 2)

        # Apply Injected Fault Dynamics
        self._apply_fault(dt_sec)

        # Clamp temperatures to physical boundaries (cannot drop below ambient air)
        for k in range(4):
            self.cht_c[k] = max(self.ambient_temp_c, self.cht_c[k])
            self.egt_c[k] = max(self.ambient_temp_c + 20.0, self.egt_c[k])
        self.oil_temp_c = max(self.ambient_temp_c, self.oil_temp_c)
        self.coolant_temp_c = max(self.ambient_temp_c, self.coolant_temp_c)

        self.accumulated_hours += (dt_sec / 3600.0)
        self.last_update = now

        # Update Rolling Degradation Trend Buffer
        ts = round(time.time(), 2)
        self.trend_timestamps.append(ts)
        self.trend_cht_max.append(round(max(self.cht_c), 1))
        self.trend_egt_max.append(round(max(self.egt_c), 1))
        self.trend_oil_temp.append(round(self.oil_temp_c, 1))
        self.trend_vibration.append(round(self.overall_vibration_g, 3))
        self.trend_efficiency.append(round(self.combustion_efficiency_pct, 1))
        # Trim to buffer max
        for buf in [self.trend_timestamps, self.trend_cht_max, self.trend_egt_max,
                     self.trend_oil_temp, self.trend_vibration, self.trend_efficiency]:
            if len(buf) > self._trend_max:
                buf.pop(0)

    def _apply_fault(self, dt_sec: float):
        if not self.active_faults:
            return

        for fault_name, sev in self.active_faults.items():
            if fault_name == "Cylinder_Misfire":
                # Cyl 3 cold, unburned exhaust drop, half-order vibration
                self.cht_c[2] -= 48.0 * sev * dt_sec
                self.egt_c[2] -= 190.0 * sev * dt_sec
                self.overall_vibration_g += 2.6 * sev
                self.fft_spectrum[0] += 1.9 * sev
                self.power_kw *= (1.0 - 0.22 * sev)

            elif fault_name == "Turbo_Degradation":
                self.manifold_pressure_hpa -= 290.0 * sev * dt_sec
                self.turbo_rpm -= 40000.0 * sev * dt_sec
                for k in range(4): self.egt_c[k] += 70.0 * sev * dt_sec

            elif fault_name == "Injector_Clogging":
                # Lean condition on Cyl 1: EGT spike, CHT rise, injector degradation
                self.egt_c[0] += 130.0 * sev * dt_sec
                self.cht_c[0] += 28.0 * sev * dt_sec
                self.fft_spectrum[4] += 0.9 * sev
                self.injection_pulse_width_ms += 1.8 * sev    # partial clog increases PW
                self.lambda_afr = min(1.3, self.lambda_afr + 0.15 * sev)  # goes lean
                self.combustion_efficiency_pct -= 14.0 * sev

            elif fault_name == "Coolant_Loss":
                # Radiator leak → rapid CHT thermal runaway and coolant boiling
                for k in range(4): self.cht_c[k] += 45.0 * sev * dt_sec * 2.5
                self.coolant_temp_c += 35.0 * sev * dt_sec * 2.5

            elif fault_name == "Oil_Starvation":
                # Oil line rupture → severe pressure collapse, friction → vibration & heat
                target_oil_press = max(0.45, 0.5 + (1.0 - sev) * 1.0)
                self.oil_press_bar = target_oil_press
                self.oil_temp_c += 35.0 * sev * dt_sec
                self.overall_vibration_g += 2.1 * sev

            elif fault_name == "Sensor_Drift":
                # Thermocouple calibration drift on Cyl 4 (false high reading, smooth offset)
                target_drift = self.cht_c[0] + 58.0 * sev
                self.cht_c[3] += (target_drift - self.cht_c[3]) * min(1.0, dt_sec * 3.0)

            elif fault_name == "Combustion_Knock":
                # Detonation: severe acoustic vibration, high-freq FFT spike, IGN knock retard, CHT rise, efficiency loss
                self.overall_vibration_g += 1.8 * sev
                self.fft_spectrum[4] += 1.8 * sev
                self.fft_spectrum[5] += 1.4 * sev
                for k in range(4): self.cht_c[k] += 22.0 * sev * dt_sec
                self.ignition_timing_btdc -= 8.0 * sev  # FADEC knock retard
                self.combustion_efficiency_pct -= 18.0 * sev

            elif fault_name == "Valve_Leakage":
                # Exhaust valve blowby on Cyl 2: continuous EGT spike, power loss, eff drop
                self.egt_c[1] += 115.0 * sev * dt_sec
                self.power_kw *= (1.0 - 0.14 * sev)
                self.combustion_efficiency_pct -= 12.0 * sev


    def set_engine_profile(self, profile_id: str):
        """Switches the propulsion twin architecture to any supported aero engine."""
        if profile_id not in ENGINE_PROFILES:
            return False
        self.active_engine_id = profile_id
        prof = ENGINE_PROFILES[profile_id]
        self.engine_name = prof["name"]
        self.engine_type = prof["type"]
        self.engine_power_hp = prof["power_hp"]
        self.engine_power_kw = prof["power_kw"]
        self.rated_rpm = prof["rated_rpm"]
        self.max_boost_map_hpa = prof["max_boost_map_hpa"]
        self.displacement_cc = prof["displacement_cc"]
        self.fuel_type = prof["fuel_type"]
        self.tbo_hours = prof["tbo_hours"]
        self.airframes = prof["airframes"]
        self.certification = prof["certification"]
        self.nominal_cht_c = prof.get("nominal_cht_c", 112.0)
        self.nominal_egt_c = prof.get("nominal_egt_c", 810.0)
        self.nominal_oil_bar = prof.get("nominal_oil_bar", 3.8)
        self.nominal_oil_c = prof.get("nominal_oil_c", 95.0)
        self.nominal_lambda = prof.get("nominal_lambda", 1.02)
        self.cht_factors = prof.get("cht_factors", [0.98, 0.99, 1.03, 1.02])
        self.egt_offsets = prof.get("egt_offsets", [0.0, 5.0, -3.0, 2.0])
        self.oil_temp_c = self.nominal_oil_c
        self.oil_press_bar = self.nominal_oil_bar

        # Re-initialize engine operating states to match selected engine physics
        idle_rpm = self.rated_rpm * 0.25
        self.rpm = idle_rpm + (self.throttle_pct / 100.0) * (self.rated_rpm - idle_rpm)
        is_diesel = self.fuel_type.startswith("Jet") or "Diesel" in self.engine_name
        has_turbo = self.max_boost_map_hpa > 1050.0

        if has_turbo:
            self.manifold_pressure_hpa = self.ambient_press_hpa + (self.throttle_pct / 100.0) * (self.max_boost_map_hpa - self.ambient_press_hpa)
            self.turbo_rpm = (self.manifold_pressure_hpa / self.max_boost_map_hpa) * (180000.0 if is_diesel else 145000.0)
            self.wastegate_pct = max(0.0, min(100.0, ((self.manifold_pressure_hpa - (self.max_boost_map_hpa - 220.0)) / 220.0) * 100.0))
        else:
            self.manifold_pressure_hpa = self.ambient_press_hpa * (self.throttle_pct / 100.0) * 0.95
            self.turbo_rpm = 0.0
            self.wastegate_pct = 0.0

        pwr_raw = (self.manifold_pressure_hpa / 1013.25) * (self.rpm / self.rated_rpm) * self.engine_power_kw
        self.power_kw = min(self.engine_power_kw * 1.02, max(0.0, pwr_raw))
        self.torque_nm = (self.power_kw * 9548.8 / max(self.rpm, 100.0))
        fuel_sfc = 0.210 if is_diesel else (0.310 if not has_turbo else 0.285)
        fuel_density = 0.84 if is_diesel else 0.72
        self.fuel_flow_lph = (self.power_kw * fuel_sfc / fuel_density)
        self.fuel_press_bar = 1.8 if is_diesel else 3.0

        ram_cooling = (self.airspeed_kts / 100.0) * (8.0 if is_diesel else 15.0)
        if is_diesel:
            cht_base = 70.0 + (self.power_kw / self.engine_power_kw) * 35.0 + (self.ambient_temp_c * 0.15)
            egt_base = self.nominal_egt_c - 100.0 + (self.manifold_pressure_hpa / self.max_boost_map_hpa) * 150.0
        else:
            cht_base = self.nominal_cht_c - 40.0 + (self.power_kw / self.engine_power_kw) * 60.0 - ram_cooling + (self.ambient_temp_c * 0.28)
            egt_base = self.nominal_egt_c - 150.0 + (self.manifold_pressure_hpa / 1300.0) * 180.0

        self.cht_c = [round(cht_base * f + float(np.random.normal(0, 0.3)), 1) for f in self.cht_factors]
        self.egt_c = [round(egt_base + off + float(np.random.normal(0, 0.8)), 1) for off in self.egt_offsets]
        return True

    def get_components_health(self) -> dict:
        """
        Calculates defense-grade Component-Level Predictive Health Monitoring (PHM)
        and Dynamic Parts Replacement Schedule for 8 mission-critical aero engine parts.
        Integrates Arrhenius thermal wear, mechanical vibration/RPM stress, cumulative flight hours,
        and active compound fault penalties.
        """
        now = datetime.now()
        tempo_daily_hrs = 6.0  # Standard MALE UAV operational tempo (6.0 flight hrs/day)

        is_diesel = (self.active_engine_id == "AUSTRO_AE300")
        is_lycoming = (self.active_engine_id == "LYCOMING_IO360")

        faults = self.active_faults
        def get_fault_sev(name: str) -> float:
            return float(faults.get(name, 0.0))

        inj_sev = get_fault_sev("Injector_Clogging")
        tc_sev = get_fault_sev("Turbo_Degradation")
        oil_sev = get_fault_sev("Oil_Starvation")
        cool_sev = get_fault_sev("Coolant_Loss")
        knock_sev = get_fault_sev("Combustion_Knock")
        valve_sev = get_fault_sev("Valve_Leakage")
        misfire_sev = get_fault_sev("Cylinder_Misfire")
        fric_sev = get_fault_sev("Piston_Friction")

        max_cht = max(self.cht_c)
        max_egt = max(self.egt_c)

        # 1. Turbocharger Spool & Bearings
        tc_tbo = 2000.0 if is_lycoming else (1200.0 if is_diesel else 1000.0)
        tc_part = "LYC-NA-AIRBOX" if is_lycoming else ("AUS-AE300-TC-02" if is_diesel else "ROT-914-TC-01")
        tc_wear = (self.accumulated_hours % tc_tbo) / tc_tbo * 100.0
        if is_lycoming:
            tc_health = max(10.0, 98.0 - tc_wear)
            tc_action = "Naturally aspirated airbox nominal. Clean induction filter element at 50-hr service."
        else:
            tc_stress = max(0.0, (self.turbo_rpm - 110000.0) / 20000.0 * 8.0)
            tc_penalty = tc_sev * 78.0 + oil_sev * 35.0 + knock_sev * 15.0
            tc_health = max(5.0, min(100.0, 100.0 - tc_wear - tc_stress - tc_penalty))
            if tc_health < 25.0:
                tc_action = "CRITICAL: Turbo impeller bearing degradation / oil starvation. Ground aircraft and replace cartridge immediately."
            elif tc_health < 50.0:
                tc_action = "Inspect turbocharger wastegate servo linkage, shaft end-play tolerance, and compressor wheel for FOD."
            else:
                tc_action = "Nominal boost envelope. Inspect wastegate electronic linkage at upcoming 100-hr service."

        # 2. Fuel Injector Nozzles & Valve
        inj_tbo = 600.0
        inj_part = "BENDIX-RSA-02" if is_lycoming else ("BOS-CRD-INJ-04" if is_diesel else "BOS-EFI-INJ-01")
        inj_wear = (self.accumulated_hours % inj_tbo) / inj_tbo * 100.0
        inj_stress = max(0.0, (self.lambda_afr - 1.12) * 25.0) if not is_diesel else max(0.0, (self.lambda_afr - 1.7) * 20.0)
        inj_penalty = inj_sev * 80.0 + knock_sev * 18.0 + misfire_sev * 12.0
        inj_health = max(5.0, min(100.0, 100.0 - inj_wear - inj_stress - inj_penalty))
        if inj_health < 25.0:
            inj_action = "CRITICAL: Fuel injector spray orifice clogged / flow restriction detected. Ground UAV and replace injector rail assembly."
        elif inj_health < 50.0:
            inj_action = "Perform ultrasonic injector cleaning, pulse duty cycle diagnostic test, and fuel rail pressure balance check."
        else:
            inj_action = "Uniform atomization pattern verified across all cylinders. Flow bench calibration nominal."

        # 3. Piston Rings, Crown & Liners
        pst_tbo = 1200.0
        pst_part = "LYC-PST-7834" if is_lycoming else ("AUS-PST-AE44" if is_diesel else "ROT-PST-RNG-02")
        pst_wear = (self.accumulated_hours % pst_tbo) / pst_tbo * 100.0
        pst_therm = max(0.0, (max_cht - (self.nominal_cht_c + 6.0)) * 0.75)
        pst_penalty = fric_sev * 75.0 + knock_sev * 40.0 + oil_sev * 32.0 + cool_sev * 28.0
        pst_health = max(5.0, min(100.0, 100.0 - pst_wear - pst_therm - pst_penalty))
        if pst_health < 25.0:
            pst_action = "CRITICAL: Severe ring blowby / cylinder liner scoring. Teardown cylinder jug and replace pistons & rings immediately."
        elif pst_health < 50.0:
            pst_action = "Perform differential compression check (must exceed 75/80 psi) and borescope cylinder walls for micro-scoring."
        else:
            pst_action = "Compression seal nominal. Cylinder cross-hatch hone pattern verified intact."

        # 4. Inconel Exhaust & Intake Valves
        vlv_tbo = 800.0
        vlv_part = "LYC-VLV-EX71" if is_lycoming else ("AUS-VLV-CR02" if is_diesel else "VAL-INC-08")
        vlv_wear = (self.accumulated_hours % vlv_tbo) / vlv_tbo * 100.0
        vlv_therm = max(0.0, (max_egt - (self.nominal_egt_c + 15.0)) * 0.38)
        vlv_penalty = valve_sev * 80.0 + knock_sev * 26.0 + misfire_sev * 15.0
        vlv_health = max(5.0, min(100.0, 100.0 - vlv_wear - vlv_therm - vlv_penalty))
        if vlv_health < 25.0:
            vlv_action = "CRITICAL: Exhaust valve seat erosion / gas leakage detected. Remove cylinder head and replace valve train immediately."
        elif vlv_health < 50.0:
            vlv_action = "Check lash clearance, inspect valve stem guides for wobble, and perform leakdown test on exhaust ports."
        else:
            vlv_action = "Valve seating faces clean. Thermal color gradient nominal per maintenance manual."

        # 5. Crankshaft Main Journal Bearings
        crk_tbo = 2000.0
        crk_part = "LYC-BRG-MN36" if is_lycoming else ("AUS-BRG-AE90" if is_diesel else "BRG-MAIN-01")
        crk_wear = (self.accumulated_hours % crk_tbo) / crk_tbo * 100.0
        crk_vib = max(0.0, (self.overall_vibration_g - 1.4) * 12.0) + max(0.0, (self.rpm - self.rated_rpm) / 200.0 * 6.0)
        crk_penalty = oil_sev * 82.0 + fric_sev * 28.0 + knock_sev * 22.0
        crk_health = max(5.0, min(100.0, 100.0 - crk_wear - crk_vib - crk_penalty))
        if crk_health < 25.0:
            crk_action = "CRITICAL: Main bearing hydrodynamic wedge collapse / babbitt wiping risk. Ground engine for bottom-end overhaul."
        elif crk_health < 50.0:
            crk_action = "Inspect magnetic chip detector plug for ferrous metal debris, check oil filter pleats, and verify journal clearance."
        else:
            crk_action = "Hydrodynamic oil film thickness nominal. Vibration signature well below DO-160G threshold."

        # 6. Oil Scavenge Pump & Filter Unit
        oil_tbo = 1500.0
        oil_part = "LYC-OIL-PM22" if is_lycoming else ("AUS-OIL-PMP01" if is_diesel else "LUB-PMP-03")
        oil_wear = (self.accumulated_hours % oil_tbo) / oil_tbo * 100.0
        oil_therm = max(0.0, (self.oil_temp_c - (self.nominal_oil_c + 6.0)) * 0.75)
        oil_penalty = oil_sev * 85.0 + fric_sev * 20.0
        oil_health = max(5.0, min(100.0, 100.0 - oil_wear - oil_therm - oil_penalty))
        if oil_health < 25.0:
            oil_action = "CRITICAL: Lube oil pressure collapsed / scavenge pump cavitating. Immediate replacement of pump & filter pack."
        elif oil_health < 50.0:
            oil_action = "Replace 10-micron oil filter cartridge, calibrate oil pressure regulator relief valve, and take SOAP oil sample."
        else:
            oil_action = "Circulation pressure and flow rate within nominal certified operating range."

        # 7. Spark Plugs / Glow Plugs
        ign_tbo = 300.0 if is_diesel else 100.0
        ign_part = "REM38E-AV" if is_lycoming else ("GLW-BOSCH-D04" if is_diesel else "PLG-AV-09")
        ign_wear = (self.accumulated_hours % ign_tbo) / ign_tbo * 100.0
        ign_penalty = misfire_sev * 82.0 + knock_sev * 25.0 + inj_sev * 16.0
        ign_health = max(5.0, min(100.0, 100.0 - ign_wear - ign_penalty))
        if ign_health < 25.0:
            ign_action = "CRITICAL: Electrode fouling / coil dielectric breakdown. Replace all plugs and test ignition harness."
        elif ign_health < 50.0:
            ign_action = "Check spark plug electrode gap (0.6 - 0.7 mm), clean lead carbon deposits, and test ignition lead resistance."
        else:
            ign_action = "Clean dual ignition spark delivery. Magneto / ECU timing synchronization locked."

        # 8. Radiator Heat Exchanger & Water Pump
        cool_tbo = 1200.0
        cool_part = "OIL-CLR-12A" if is_lycoming else ("AUS-RAD-HEX02" if is_diesel else "RAD-HEX-05")
        cool_wear = (self.accumulated_hours % cool_tbo) / cool_tbo * 100.0
        cool_penalty = cool_sev * 88.0 + (max(0.0, (self.coolant_temp_c - 105.0) * 1.5) if not is_lycoming else 0.0)
        cool_health = max(5.0, min(100.0, 100.0 - cool_wear - cool_penalty))
        if cool_health < 25.0:
            cool_action = "CRITICAL: Coolant circulation loss / radiator thermal core blockage. Ground aircraft to prevent head warping."
        elif cool_health < 50.0:
            cool_action = "Pressure test cooling circuit to 1.2 bar, inspect water pump mechanical seal weep hole, and clean radiator fins."
        else:
            cool_action = "Heat rejection rate nominal. Thermostat expansion valve and mechanical pump operating smoothly."

        raw_parts = [
            {
                "id": "turbocharger",
                "name": "Turbocharger Spool & Dynamic Bearings",
                "part_number": tc_part,
                "subsystem": "Induction & Boost System",
                "health_pct": round(tc_health, 1),
                "base_tbo_hours": tc_tbo,
                "action_required": tc_action,
                "mil_standard": "MIL-STD-810H / EASA.E.122",
                "wear_factor_label": "High-RPM Centrifugal & Thermal Stress"
            },
            {
                "id": "fuel_injectors",
                "name": "Fuel Injector Nozzles & High-Pressure Valve",
                "part_number": inj_part,
                "subsystem": "Fuel Delivery & Atomization",
                "health_pct": round(inj_health, 1),
                "base_tbo_hours": inj_tbo,
                "action_required": inj_action,
                "mil_standard": "DO-160G Section 14 / RTCA",
                "wear_factor_label": "Pulse Cavitation & Lean Atomization Wear"
            },
            {
                "id": "piston_rings",
                "name": "Piston Rings, Crown & Cylinder Liners",
                "part_number": pst_part,
                "subsystem": "Reciprocating Power Assembly",
                "health_pct": round(pst_health, 1),
                "base_tbo_hours": pst_tbo,
                "action_required": pst_action,
                "mil_standard": "FAA FAR-33.19 / EASA CS-E",
                "wear_factor_label": "Combustion Pressure & Cylinder Bore Friction"
            },
            {
                "id": "valves_train",
                "name": "Inconel Exhaust & Intake Valves (Nimonic 80A)",
                "part_number": vlv_part,
                "subsystem": "Cylinder Head & Valvetrain",
                "health_pct": round(vlv_health, 1),
                "base_tbo_hours": vlv_tbo,
                "action_required": vlv_action,
                "mil_standard": "MIL-HDBK-5J High-Temp Superalloys",
                "wear_factor_label": "Thermal Creep & Dynamic Seat Pounding"
            },
            {
                "id": "crankshaft_bearings",
                "name": "Crankshaft Main Journal Bearings & Inserts",
                "part_number": crk_part,
                "subsystem": "Crankcase & Bottom End Assembly",
                "health_pct": round(crk_health, 1),
                "base_tbo_hours": crk_tbo,
                "action_required": crk_action,
                "mil_standard": "SAE AS8879 / DEF-STAN 00-970",
                "wear_factor_label": "Hydrodynamic Film Shear & RPM Fatigue"
            },
            {
                "id": "oil_pump",
                "name": "Oil Scavenge Pump, Relief Valve & Filter Unit",
                "part_number": oil_part,
                "subsystem": "Lubrication & Scavenge Circuit",
                "health_pct": round(oil_health, 1),
                "base_tbo_hours": oil_tbo,
                "action_required": oil_action,
                "mil_standard": "ISO 4406 / EASA.E.118",
                "wear_factor_label": "Fluid Shear Viscosity & Particulate Abrasion"
            },
            {
                "id": "ignition_system",
                "name": "Common-Rail Glow Plugs & Module" if is_diesel else "Aviation Spark Plugs & Shielded Harness",
                "part_number": ign_part,
                "subsystem": "Ignition & Combustion Pre-Heat",
                "health_pct": round(ign_health, 1),
                "base_tbo_hours": ign_tbo,
                "action_required": ign_action,
                "mil_standard": "MIL-P-21743 / EASA CS-E 640",
                "wear_factor_label": "High-Voltage Arc Erosion & Spark Depletion"
            },
            {
                "id": "cooling_system",
                "name": "Air-Cooled Cylinder Baffles & Oil Cooler" if is_lycoming else "Radiator Heat Exchanger & Water Pump",
                "part_number": cool_part,
                "subsystem": "Thermal Heat Exchanger Circuit",
                "health_pct": round(cool_health, 1),
                "base_tbo_hours": cool_tbo,
                "action_required": cool_action,
                "mil_standard": "DEF-STAN 05-91 / NATO STANAG 4671",
                "wear_factor_label": "Coolant Cavitation & Thermal Cycling"
            }
        ]

        components = []
        for p in raw_parts:
            hp = p["health_pct"]
            tbo = p["base_tbo_hours"]
            hrs_rem = round(max(0.5, (hp / 100.0) * tbo), 1)
            days_rem = round(hrs_rem / tempo_daily_hrs, 1)

            if hp < 25.0 or hrs_rem < 20.0:
                urg = "CRITICAL"
                urg_lbl = "REPLACE IMMEDIATELY (AOG)"
                col = "red"
                rep_date = "IMMEDIATE (AOG - GROUNDED)"
                rep_date_disp = "IMMEDIATE (AOG - GROUNDED)"
            elif hp < 50.0 or hrs_rem < 75.0:
                urg = "DUE_SOON"
                urg_lbl = "REPLACEMENT DUE SOON"
                col = "amber"
                target_dt = now + timedelta(days=days_rem)
                rep_date = target_dt.strftime("%d-%b-%Y")
                rep_date_disp = f"{rep_date} (~{days_rem:.0f} days)"
            elif hp < 75.0 or hrs_rem < 200.0:
                urg = "MONITOR"
                urg_lbl = "PREDICTIVE MONITORING"
                col = "cyan"
                target_dt = now + timedelta(days=days_rem)
                rep_date = target_dt.strftime("%d-%b-%Y")
                rep_date_disp = f"{rep_date} (~{days_rem:.0f} days)"
            else:
                urg = "OPTIMAL"
                urg_lbl = "AIRWORTHY (OPTIMAL)"
                col = "emerald"
                target_dt = now + timedelta(days=days_rem)
                rep_date = target_dt.strftime("%d-%b-%Y")
                rep_date_disp = f"{rep_date} (~{days_rem:.0f} days)"

            p["hours_remaining"] = hrs_rem
            p["days_remaining"] = days_rem
            p["replacement_date"] = rep_date
            p["replacement_date_display"] = rep_date_disp
            p["urgency"] = urg
            p["urgency_label"] = urg_lbl
            p["status_color"] = col
            components.append(p)

        crit_count = sum(1 for c in components if c["urgency"] == "CRITICAL")
        due_count = sum(1 for c in components if c["urgency"] == "DUE_SOON")
        monitor_count = sum(1 for c in components if c["urgency"] == "MONITOR")
        optimal_count = sum(1 for c in components if c["urgency"] == "OPTIMAL")
        avg_comp_health = round(sum(c["health_pct"] for c in components) / len(components), 1)

        return {
            "engine_id": self.active_engine_id,
            "engine_name": self.engine_name,
            "accumulated_hours": round(self.accumulated_hours, 1),
            "tempo_daily_hours": tempo_daily_hrs,
            "average_component_health": avg_comp_health,
            "counts": {
                "critical": crit_count,
                "due_soon": due_count,
                "monitor": monitor_count,
                "optimal": optimal_count,
                "total": len(components)
            },
            "components": components,
            "timestamp": time.time()
        }

    def get_state_dict(self) -> dict:
        return {
            "engine_profile_id": self.active_engine_id,
            "engine_name": self.engine_name,
            "engine_type": self.engine_type,
            "engine_power_hp": self.engine_power_hp,
            "engine_power_kw": self.engine_power_kw,
            "rated_rpm": self.rated_rpm,
            "max_boost_map_hpa": self.max_boost_map_hpa,
            "nominal_oil_bar": self.nominal_oil_bar,
            "nominal_oil_c": self.nominal_oil_c,
            "nominal_lambda": self.nominal_lambda,
            "fuel_type": self.fuel_type,
            "displacement_cc": self.displacement_cc,
            "airframes": self.airframes,
            "certification": self.certification,
            "tbo_hours": self.tbo_hours,
            "rpm": round(self.rpm, 1),
            "manifold_pressure_hpa": round(self.manifold_pressure_hpa, 1),
            "power_output_kw": round(self.power_kw, 2),
            "torque_nm": round(self.torque_nm, 1),
            "fuel_flow_lph": round(self.fuel_flow_lph, 2),
            "fuel_pressure_bar": round(self.fuel_press_bar, 2),
            "cht_c": [round(c, 1) for c in self.cht_c],
            "egt_c": [round(e, 1) for e in self.egt_c],
            "oil_temperature_c": round(self.oil_temp_c, 1),
            "oil_pressure_bar": round(self.oil_press_bar, 2),
            "coolant_temperature_c": round(self.coolant_temp_c, 1),
            "turbo_rpm": round(self.turbo_rpm, 0),
            "wastegate_pct": round(self.wastegate_pct, 1),
            "intercooler_temp_c": round(self.intercooler_temp_c, 1),
            "bus_voltage_v": round(self.bus_voltage_v, 2),
            "alternator_current_a": round(self.alternator_current_a, 1),
            "ignition_timing_btdc": round(self.ignition_timing_btdc, 1),
            "injection_timing_btdc": round(self.injection_timing_btdc, 2),
            "injection_pulse_width_ms": round(self.injection_pulse_width_ms, 2),
            "lambda_afr": round(self.lambda_afr, 3),
            "combustion_efficiency_pct": round(self.combustion_efficiency_pct, 1),
            "overall_vibration_g": round(self.overall_vibration_g, 2),
            "fft_spectrum": self.fft_spectrum,
            "accumulated_hours": round(self.accumulated_hours, 2),
            "active_fault": self.active_fault,
            "active_faults": list(self.active_faults.keys()),
            "fault_severity": self.fault_severity,
            "is_mitigated": self.is_mitigated,
            "engine_seized": self.engine_seized,
            "components_health": self.get_components_health()
        }

    def get_trend_dict(self) -> dict:
        """Returns rolling degradation trend history for dashboard charts."""
        return {
            "timestamps": list(self.trend_timestamps),
            "cht_max": list(self.trend_cht_max),
            "egt_max": list(self.trend_egt_max),
            "oil_temp": list(self.trend_oil_temp),
            "vibration": list(self.trend_vibration),
            "efficiency": list(self.trend_efficiency),
            "count": len(self.trend_timestamps)
        }

    def get_flight_dict(self) -> dict:
        return {
            "mission_name": self.mission_name,
            "altitude_m": round(self.altitude_m, 1),
            "ambient_temp_c": round(self.ambient_temp_c, 1),
            "ambient_press_hpa": round(self.ambient_press_hpa, 1),
            "airspeed_kts": round(self.airspeed_kts, 1),
            "throttle_pct": round(self.throttle_pct, 1)
        }

    def get_raw_can_frame_hex(self) -> str:
        # Generate representative SocketCAN raw frame string
        raw_rpm = int(self.rpm * 8.0) & 0xFFFF
        raw_map = int(self.manifold_pressure_hpa * 10.0) & 0xFFFF
        b0 = raw_rpm & 0xFF
        b1 = (raw_rpm >> 8) & 0xFF
        b2 = raw_map & 0xFF
        b3 = (raw_map >> 8) & 0xFF
        b4 = int(self.fuel_flow_lph * 2.0) & 0xFF
        b5 = int(self.power_kw) & 0xFF
        b6 = int(self.oil_temp_c) & 0xFF
        b7 = int(self.oil_press_bar * 10.0) & 0xFF
        return f"CAN0 18FEE000# {b0:02X} {b1:02X} {b2:02X} {b3:02X} {b4:02X} {b5:02X} {b6:02X} {b7:02X}"
