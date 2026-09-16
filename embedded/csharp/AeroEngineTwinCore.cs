using System;

namespace AeroTwin.Embedded.CSharp
{
    public enum FaultMode
    {
        None = 0,
        CylinderMisfire   = 1,
        TurboDegradation  = 2,
        InjectorClogging  = 3,
        CoolantLoss       = 4,
        OilStarvation     = 5,
        SensorDrift       = 6,
        CombustionKnock   = 7,
        ValveLeakage      = 8
    }

    public class FlightEnvelope
    {
        public double AltitudeMeters       { get; set; } = 1500.0;
        public double AmbientTempCelsius   { get; set; } = 15.0;
        public double AmbientPressureHpa   { get; set; } = 1013.25;
        public double AirspeedKnots        { get; set; } = 95.0;
        public double ThrottlePercent      { get; set; } = 75.0;
    }

    public class AeroEngineTelemetry
    {
        public double   Rpm                    { get; set; }
        public double   ManifoldPressureHpa    { get; set; }
        public double   PowerOutputKw          { get; set; }
        public double   TorqueNm               { get; set; }
        public double   FuelFlowLph            { get; set; }
        public double   FuelPressureBar        { get; set; }
        public double[] ChtCelsius             { get; set; } = new double[4];
        public double[] EgtCelsius             { get; set; } = new double[4];
        public double   OilTempCelsius         { get; set; }
        public double   OilPressureBar         { get; set; }
        public double   CoolantTempCelsius     { get; set; }
        public double   TurboRpm               { get; set; }
        public double   WastegatePct           { get; set; }
        public double   BusVoltageV            { get; set; }
        public double   AlternatorCurrentA     { get; set; }
        public double   OverallVibrationG      { get; set; }

        // ── Injection & Combustion (FADEC-Controlled) ──────────────────────
        public double   IgnitionTimingBtdc     { get; set; }   // degrees BTDC (MBT curve)
        public double   InjectionTimingBtdc    { get; set; }   // injection lead angle
        public double   InjectionPulseWidthMs  { get; set; }   // injector on-time per event
        public double   LambdaAfr              { get; set; }   // 1.0 = stoichiometric
        public double   CombustionEfficiencyPct{ get; set; }   // thermodynamic efficiency %

        // ── Health & Prognostics ────────────────────────────────────────────
        public double   HealthIndex            { get; set; } = 1.0;
        public double   RulHours               { get; set; } = 1000.0;
        public long     TimestampMs            { get; set; }
    }

    // Circular degradation trend buffer (60 samples)
    public class DegradationTrendBuffer
    {
        public const int MaxPoints = 60;
        public double[] ChtMax    = new double[MaxPoints];
        public double[] EgtMax    = new double[MaxPoints];
        public double[] OilTemp   = new double[MaxPoints];
        public double[] Vibration = new double[MaxPoints];
        public double[] Efficiency= new double[MaxPoints];
        public int Count = 0;
        public int Head  = 0;

        public void Push(double chtMax, double egtMax, double oilTemp, double vib, double eff)
        {
            ChtMax[Head]    = chtMax;
            EgtMax[Head]    = egtMax;
            OilTemp[Head]   = oilTemp;
            Vibration[Head] = vib;
            Efficiency[Head]= eff;
            Head = (Head + 1) % MaxPoints;
            if (Count < MaxPoints) Count++;
        }

        public (double min, double max) Range(double[] arr)
        {
            if (Count == 0) return (0, 0);
            double mn = double.MaxValue, mx = double.MinValue;
            for (int i = 0; i < Count; i++)
            {
                int idx = (Head - Count + i + MaxPoints) % MaxPoints;
                if (arr[idx] < mn) mn = arr[idx];
                if (arr[idx] > mx) mx = arr[idx];
            }
            return (mn, mx);
        }
    }

    public class AeroEngineTwinCore
    {
        private readonly AeroEngineTelemetry _state  = new AeroEngineTelemetry();
        private          FlightEnvelope      _flight = new FlightEnvelope();
        private          FaultMode           _activeFault   = FaultMode.None;
        private          double              _faultSeverity = 0.0;
        private          double              _accumulatedRunHours = 120.0;
        private readonly DegradationTrendBuffer _trend = new DegradationTrendBuffer();
        private readonly Random _rng = new Random(42);

        // Rotax 914F constants
        private const double MaxBoostHpa  = 1400.0;
        private const double RatedPowerKw = 84.5;
        private const double RatedRpm     = 5800.0;

        public AeroEngineTwinCore()
        {
            _state.Rpm                   = 5000.0;
            _state.ManifoldPressureHpa   = 1150.0;
            _state.PowerOutputKw         = 65.0;
            _state.TorqueNm              = 124.0;
            _state.FuelFlowLph           = 18.5;
            _state.FuelPressureBar       = 3.0;
            _state.OilTempCelsius        = 90.0;
            _state.OilPressureBar        = 3.8;
            _state.CoolantTempCelsius    = 86.0;
            _state.TurboRpm              = 110000.0;
            _state.BusVoltageV           = 28.1;
            _state.AlternatorCurrentA    = 22.4;
            _state.OverallVibrationG     = 1.4;
            // Injection defaults
            _state.IgnitionTimingBtdc    = 26.0;
            _state.InjectionTimingBtdc   = 8.5;
            _state.InjectionPulseWidthMs = 4.2;
            _state.LambdaAfr             = 1.02;
            _state.CombustionEfficiencyPct = 92.5;

            for (int i = 0; i < 4; i++)
            {
                _state.ChtCelsius[i] = 110.0 + (i * 2);
                _state.EgtCelsius[i] = 815.0 + (i % 2 == 0 ? 5 : -5);
            }
        }

        public void SetFlightEnvelope(FlightEnvelope env) => _flight = env;

        public void InjectFault(FaultMode fault, double severity = 1.0)
        {
            _activeFault   = fault;
            _faultSeverity = Math.Clamp(severity, 0.0, 1.0);
        }

        public void ClearFault()
        {
            _activeFault   = FaultMode.None;
            _faultSeverity = 0.0;
        }

        // ── Main Physics Step ────────────────────────────────────────────────
        public void Step(double dtSeconds)
        {
            CalculateThermodynamics(dtSeconds);
            CalculateInjectionAndCombustion();
            ApplyFaultDynamics(dtSeconds);
            UpdateTrendBuffer();

            _accumulatedRunHours += dtSeconds / 3600.0;
            _state.RulHours = Math.Max(0.0, (1000.0 - _accumulatedRunHours) * _state.HealthIndex);
            _state.TimestampMs += (long)(dtSeconds * 1000.0);
        }

        // ── Thermodynamic & Mechanical Model ─────────────────────────────────
        private void CalculateThermodynamics(double dt)
        {
            double targetRpm = 1400.0 + (_flight.ThrottlePercent / 100.0) * (RatedRpm - 1400.0);
            _state.Rpm += (targetRpm - _state.Rpm) * Math.Min(1.0, dt * 3.5);

            double targetMap = _flight.AmbientPressureHpa +
                               (_flight.ThrottlePercent / 100.0) * (MaxBoostHpa - _flight.AmbientPressureHpa);
            _state.ManifoldPressureHpa += (targetMap - _state.ManifoldPressureHpa) * Math.Min(1.0, dt * 4.0);

            // Turbocharger
            double targetTurbo = (_state.ManifoldPressureHpa / MaxBoostHpa) * 145000.0;
            _state.TurboRpm += (targetTurbo - _state.TurboRpm) * Math.Min(1.0, dt * 2.0);
            _state.WastegatePct = _state.ManifoldPressureHpa > 1200.0
                ? ((_state.ManifoldPressureHpa - 1200.0) / 200.0) * 100.0 : 0.0;

            _state.PowerOutputKw = (_state.ManifoldPressureHpa / 1013.25) * (_state.Rpm / RatedRpm) * RatedPowerKw;
            _state.TorqueNm      = _state.Rpm > 100.0 ? (_state.PowerOutputKw * 9548.8 / _state.Rpm) : 0.0;
            _state.FuelFlowLph   = (_state.PowerOutputKw * 0.285) / 0.72;

            double ramAir  = (_flight.AirspeedKnots / 100.0) * 15.0;
            double heatIn  = _state.PowerOutputKw * 0.75;

            for (int i = 0; i < 4; i++)
            {
                double cf = (i == 2 || i == 3) ? 1.03 : 0.98;
                double tgt_cht = 70.0 + (heatIn * cf) - ramAir + (_flight.AmbientTempCelsius * 0.3);
                _state.ChtCelsius[i] += (tgt_cht - _state.ChtCelsius[i]) * Math.Min(1.0, dt * 0.15);
                double tgt_egt = 720.0 + (_state.ManifoldPressureHpa * 0.11) + (cf * 10.0);
                _state.EgtCelsius[i] += (tgt_egt - _state.EgtCelsius[i]) * Math.Min(1.0, dt * 0.5);
            }

            double tgt_oil = 75.0 + (_state.PowerOutputKw * 0.38) - (ramAir * 0.5);
            _state.OilTempCelsius   += (tgt_oil - _state.OilTempCelsius) * Math.Min(1.0, dt * 0.1);
            _state.OilPressureBar    = (_state.Rpm / 5000.0) * 4.2 *
                                       (1.0 - (_state.OilTempCelsius - 80.0) * 0.003);
            _state.CoolantTempCelsius = _state.OilTempCelsius * 0.92;

            // Base vibration
            double baseVib = 0.8 + (_state.Rpm / RatedRpm) * 1.2;
            _state.OverallVibrationG = baseVib;
        }

        // ── FADEC Injection & Combustion Efficiency ───────────────────────────
        private void CalculateInjectionAndCombustion()
        {
            // MBT ignition timing curve
            double rpmAdv    = (_state.Rpm / RatedRpm) * 14.0;
            double mapRetard = (_state.ManifoldPressureHpa / MaxBoostHpa) * 6.0;
            _state.IgnitionTimingBtdc = 18.0 + rpmAdv - mapRetard;

            // Injection timing advances with throttle load
            _state.InjectionTimingBtdc = 4.0 + (_flight.ThrottlePercent / 100.0) * 8.0;

            // Injector pulse width from fuel flow
            double firingFreq = (_state.Rpm / 2.0) / 60.0; // 4-stroke firing events/sec
            _state.InjectionPulseWidthMs = firingFreq > 0.1
                ? (_state.FuelFlowLph / (firingFreq * 3600.0)) * 1000.0 + 0.8 : 4.2;

            // Lambda: lean at cruise, rich at full power
            double noise = (_rng.NextDouble() - 0.5) * 0.006;
            _state.LambdaAfr = 1.08 - (_flight.ThrottlePercent / 100.0) * 0.10 + noise;

            // Combustion efficiency
            double afrPenalty = Math.Abs(_state.LambdaAfr - 1.0) * 15.0;
            double vibPenalty = Math.Max(0.0, (_state.OverallVibrationG - 1.5) * 3.0);
            _state.CombustionEfficiencyPct = Math.Max(50.0, 96.0 - afrPenalty - vibPenalty);
        }

        // ── Fault Dynamics ────────────────────────────────────────────────────
        private void ApplyFaultDynamics(double dt)
        {
            if (_activeFault == FaultMode.None)
            {
                _state.HealthIndex = 0.98;
                return;
            }

            switch (_activeFault)
            {
                case FaultMode.CylinderMisfire:
                    _state.ChtCelsius[2]        -= 45.0 * _faultSeverity * dt;
                    _state.EgtCelsius[2]        -= 175.0 * _faultSeverity * dt;
                    _state.OverallVibrationG    += 2.4 * _faultSeverity;
                    _state.PowerOutputKw        *= (1.0 - 0.22 * _faultSeverity);
                    _state.HealthIndex           = Math.Max(0.2, 0.98 - 0.45 * _faultSeverity);
                    break;

                case FaultMode.TurboDegradation:
                    _state.ManifoldPressureHpa  -= 280.0 * _faultSeverity * dt;
                    _state.TurboRpm             -= 35000.0 * _faultSeverity * dt;
                    for (int i = 0; i < 4; i++)
                        _state.EgtCelsius[i]    += 65.0 * _faultSeverity * dt;
                    _state.HealthIndex           = Math.Max(0.3, 0.98 - 0.35 * _faultSeverity);
                    break;

                case FaultMode.InjectorClogging:
                    _state.EgtCelsius[0]        += 100.0 * _faultSeverity * dt;
                    _state.ChtCelsius[0]        += 28.0 * _faultSeverity * dt;
                    _state.InjectionPulseWidthMs += 1.8 * _faultSeverity;    // partial clog
                    _state.LambdaAfr            += 0.15 * _faultSeverity;    // goes lean
                    _state.CombustionEfficiencyPct -= 14.0 * _faultSeverity;
                    _state.HealthIndex           = Math.Max(0.4, 0.98 - 0.30 * _faultSeverity);
                    break;

                case FaultMode.CoolantLoss:
                    for (int i = 0; i < 4; i++)
                        _state.ChtCelsius[i]    += 55.0 * _faultSeverity * dt;
                    _state.CoolantTempCelsius   += 35.0 * _faultSeverity * dt;
                    _state.HealthIndex           = Math.Max(0.1, 0.98 - 0.70 * _faultSeverity);
                    break;

                case FaultMode.OilStarvation:
                    _state.OilPressureBar        = Math.Max(0.5, _state.OilPressureBar - 2.0 * _faultSeverity * dt);
                    _state.OilTempCelsius       += 38.0 * _faultSeverity * dt;
                    _state.OverallVibrationG    += 1.8 * _faultSeverity;
                    _state.HealthIndex           = Math.Max(0.05, 0.98 - 0.85 * _faultSeverity);
                    break;

                case FaultMode.SensorDrift:
                    _state.ChtCelsius[3]        += 60.0 * _faultSeverity;    // false reading offset
                    _state.HealthIndex           = 0.82;
                    break;

                case FaultMode.CombustionKnock:
                    for (int i = 0; i < 4; i++)
                        _state.ChtCelsius[i]    += 20.0 * _faultSeverity * dt;
                    _state.IgnitionTimingBtdc   -= 8.0 * _faultSeverity;     // knock retard
                    _state.CombustionEfficiencyPct -= 18.0 * _faultSeverity;
                    _state.HealthIndex           = Math.Max(0.35, 0.98 - 0.40 * _faultSeverity);
                    break;

                case FaultMode.ValveLeakage:
                    _state.EgtCelsius[1]        += 110.0 * _faultSeverity * dt;
                    _state.PowerOutputKw        *= (1.0 - 0.15 * _faultSeverity);
                    _state.CombustionEfficiencyPct -= 12.0 * _faultSeverity;
                    _state.HealthIndex           = Math.Max(0.45, 0.98 - 0.35 * _faultSeverity);
                    break;
            }
        }

        // ── Trend Buffer ──────────────────────────────────────────────────────
        private void UpdateTrendBuffer()
        {
            double chtMax = _state.ChtCelsius[0];
            double egtMax = _state.EgtCelsius[0];
            for (int i = 1; i < 4; i++) {
                if (_state.ChtCelsius[i] > chtMax) chtMax = _state.ChtCelsius[i];
                if (_state.EgtCelsius[i] > egtMax) egtMax = _state.EgtCelsius[i];
            }
            _trend.Push(chtMax, egtMax, _state.OilTempCelsius,
                        _state.OverallVibrationG, _state.CombustionEfficiencyPct);
        }

        // ── JSON Serialization ────────────────────────────────────────────────
        /// <summary>
        /// Serializes telemetry to JSON for HTTP POST to FastAPI /api/telemetry/hardware-ingest.
        /// Uses System.Text — zero external NuGet packages required.
        /// </summary>
        public string BuildJsonPayload()
        {
            var s = _state;
            return $"{{" +
                   $"\"source\":\"CSHARP_EMBEDDED_SIM\"," +
                   $"\"rpm\":{s.Rpm:F1}," +
                   $"\"vibration_g\":{s.OverallVibrationG:F3}," +
                   $"\"cht_c\":[{s.ChtCelsius[0]:F1},{s.ChtCelsius[1]:F1},{s.ChtCelsius[2]:F1},{s.ChtCelsius[3]:F1}]," +
                   $"\"egt_c\":[{s.EgtCelsius[0]:F1},{s.EgtCelsius[1]:F1},{s.EgtCelsius[2]:F1},{s.EgtCelsius[3]:F1}]," +
                   $"\"oil_temperature_c\":{s.OilTempCelsius:F1}," +
                   $"\"oil_pressure_bar\":{s.OilPressureBar:F2}," +
                   $"\"manifold_pressure_hpa\":{s.ManifoldPressureHpa:F1}," +
                   $"\"bus_voltage_v\":{s.BusVoltageV:F2}," +
                   $"\"ignition_timing_btdc\":{s.IgnitionTimingBtdc:F1}," +
                   $"\"injection_timing_btdc\":{s.InjectionTimingBtdc:F2}," +
                   $"\"injection_pulse_ms\":{s.InjectionPulseWidthMs:F2}," +
                   $"\"lambda_afr\":{s.LambdaAfr:F3}," +
                   $"\"combustion_eff_pct\":{s.CombustionEfficiencyPct:F1}," +
                   $"\"health_index\":{s.HealthIndex:F3}," +
                   $"\"rul_hours\":{s.RulHours:F1}" +
                   $"}}";
        }

        public AeroEngineTelemetry GetTelemetry()             => _state;
        public DegradationTrendBuffer GetTrendBuffer()         => _trend;
    }
}
