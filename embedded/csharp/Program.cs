using System;
using System.Threading;

namespace AeroTwin.Embedded.CSharp
{
    class Program
    {
        static void PrintSeparator(string title = "")
        {
            Console.WriteLine("─────────────────────────────────────────────────────────────────────────────");
            if (!string.IsNullOrEmpty(title))
                Console.WriteLine($"  {title}");
        }

        static void PrintCanFrame(CanFrame f, string label)
        {
            Console.WriteLine($"  [CAN] {label,-26} | {f.ToSocketCanString()}");
        }

        static void Main(string[] args)
        {
            Console.WriteLine("=============================================================================");
            Console.WriteLine("  MALE UAV AERO PISTON DIGITAL TWIN — C# EMBEDDED EDGE RUNNER (SIH 2026)");
            Console.WriteLine("  Platform : Rotax 914 Turbocharged 4-Cylinder Boxer (115 HP / 84.5 kW)");
            Console.WriteLine("  Protocol : FADEC 2.0 / SocketCAN / J1939 Extended PGN");
            Console.WriteLine("  Layers   : C# Physics → CAN Framing → JSON → FastAPI Backend");
            Console.WriteLine("=============================================================================\n");

            var twin = new AeroEngineTwinCore();

            // ── PHASE 1: Nominal ISR Loiter ───────────────────────────────────
            twin.SetFlightEnvelope(new FlightEnvelope
            {
                AltitudeMeters     = 4000.0,
                AmbientTempCelsius = -11.0,
                AmbientPressureHpa = 620.0,
                AirspeedKnots      = 110.0,
                ThrottlePercent    = 82.0
            });

            PrintSeparator("PHASE 1 — HIGH-ALTITUDE ISR LOITER  (4000m / 82% THR)");
            for (int i = 0; i < 10; i++)
            {
                twin.Step(0.1);
                var t = twin.GetTelemetry();
                Console.WriteLine(
                    $"[T+{i * 0.1:F1}s] RPM:{t.Rpm:F0} | MAP:{t.ManifoldPressureHpa:F1}hPa | " +
                    $"CHT:[{t.ChtCelsius[0]:F0},{t.ChtCelsius[1]:F0},{t.ChtCelsius[2]:F0},{t.ChtCelsius[3]:F0}]°C | " +
                    $"Oil:{t.OilPressureBar:F1}b/{t.OilTempCelsius:F0}°C | Health:{t.HealthIndex * 100:F1}%");
            }

            // Print FADEC injection data
            var tNominal = twin.GetTelemetry();
            Console.WriteLine($"\n  [FADEC] IGN:{tNominal.IgnitionTimingBtdc:F1}°BTDC | " +
                              $"INJ:{tNominal.InjectionTimingBtdc:F1}°BTDC | " +
                              $"PW:{tNominal.InjectionPulseWidthMs:F2}ms | " +
                              $"λ={tNominal.LambdaAfr:F3} | " +
                              $"η={tNominal.CombustionEfficiencyPct:F1}%");

            // CAN frame output — all 3 PGNs
            Console.WriteLine("\n  [SocketCAN FRAME STREAM]");
            PrintCanFrame(CanBusFadecProtocol.EncodeSpeedAndPower(tNominal),  "PGN-0xFEE000 RPM/MAP  ");
            PrintCanFrame(CanBusFadecProtocol.EncodeTemperatures(tNominal),   "PGN-0xFEEE00 CHT/OIL  ");
            PrintCanFrame(CanBusFadecProtocol.EncodeInjectionFadec(tNominal), "PGN-0xFF1000 INJECTION ");
            PrintCanFrame(CanBusFadecProtocol.EncodeVibration(tNominal),      "PGN-0xFF5000 VIBRATION ");

            // ── PHASE 2: Fault Injection — Coolant Loss ───────────────────────
            Console.WriteLine("\n");
            PrintSeparator("PHASE 2 — FAULT INJECTION: COOLANT RADIATOR LOSS (Severity 0.85)");
            twin.InjectFault(FaultMode.CoolantLoss, 0.85);

            for (int i = 10; i < 20; i++)
            {
                twin.Step(0.1);
                var t = twin.GetTelemetry();
                double chtAvg = (t.ChtCelsius[0] + t.ChtCelsius[1] + t.ChtCelsius[2] + t.ChtCelsius[3]) / 4.0;
                Console.WriteLine(
                    $"[T+{i * 0.1:F1}s] ⚠ OVERHEAT | CHT avg:{chtAvg:F1}°C | " +
                    $"Coolant:{t.CoolantTempCelsius:F1}°C | Health:{t.HealthIndex * 100:F1}% | RUL:{t.RulHours:F0}h");
            }

            // ── PHASE 3: Combustion Knock ─────────────────────────────────────
            Console.WriteLine("\n");
            PrintSeparator("PHASE 3 — FAULT INJECTION: COMBUSTION KNOCK (Severity 0.75)");
            twin.ClearFault();
            twin.InjectFault(FaultMode.CombustionKnock, 0.75);

            for (int i = 0; i < 8; i++)
            {
                twin.Step(0.1);
                var t = twin.GetTelemetry();
                Console.WriteLine(
                    $"[T+{i * 0.1:F1}s] KNOCK | IGN:{t.IgnitionTimingBtdc:F1}°BTDC (RETARDED) | " +
                    $"η={t.CombustionEfficiencyPct:F1}% | Health:{t.HealthIndex * 100:F1}%");
            }

            // ── PHASE 4: Degradation Trend Buffer ────────────────────────────
            Console.WriteLine("\n");
            PrintSeparator("PHASE 4 — DEGRADATION TREND BUFFER ANALYSIS");
            var trend = twin.GetTrendBuffer();
            var (chtMin, chtMax) = trend.Range(trend.ChtMax);
            var (effMax, effMin) = trend.Range(trend.Efficiency); // reversed (high=nominal)
            Console.WriteLine($"  Trend points captured : {trend.Count} / {DegradationTrendBuffer.MaxPoints}");
            Console.WriteLine($"  CHT max range         : {chtMin:F1} → {chtMax:F1} °C  (rise: {chtMax - chtMin:F1}°C)");
            Console.WriteLine($"  Combustion efficiency : {effMax:F1} → {effMin:F1} %   (drop: {effMax - effMin:F1}%)");

            // ── PHASE 5: JSON Payload for FastAPI ─────────────────────────────
            Console.WriteLine("\n");
            PrintSeparator("PHASE 5 — JSON PAYLOAD  →  FastAPI /api/telemetry/hardware-ingest");
            twin.ClearFault();
            twin.Step(0.1);
            string json = twin.BuildJsonPayload();
            Console.WriteLine($"  {json}\n");

            Console.WriteLine("=============================================================================");
            Console.WriteLine("  C# Embedded Edge Runner COMPLETE. Architecture layers demonstrated:");
            Console.WriteLine("  [C# Physics Model] → [FADEC CAN PGN Framing] → [JSON → FastAPI Backend]");
            Console.WriteLine("=============================================================================");
        }
    }
}
