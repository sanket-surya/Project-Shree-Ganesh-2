using System;

namespace AeroTwin.Embedded.CSharp
{
    public struct CanFrame
    {
        public uint   CanId;
        public byte   Dlc;
        public byte[] Data;
        public long   TimestampUs;

        public string ToSocketCanString()
        {
            string hex = BitConverter.ToString(Data).Replace("-", " ");
            return $"CAN0 {CanId:X8}# {hex}";
        }
    }

    /// <summary>
    /// SocketCAN / FADEC 2.0 Protocol Encoder — Defense-Grade CAN Frame Builder
    /// Supports 3 PGNs:
    ///   PGN 0xFEE0 — Engine Speed, MAP, Power, Health
    ///   PGN 0xFEEE — Cylinder Head & Exhaust Temperatures + Oil
    ///   PGN 0xFF10 — FADEC Injection Timing, Lambda, Combustion Efficiency  ← NEW
    /// </summary>
    public static class CanBusFadecProtocol
    {
        // ── PGN Identifiers (J1939 Extended CAN IDs) ────────────────────────
        public const uint PgnEngineSpeed       = 0x18FEE000; // RPM, MAP, Power, Health
        public const uint PgnTemperatures      = 0x18FEEE00; // CHT[1-4], Oil T/P, Coolant
        public const uint PgnInjectionFadec    = 0x18FF1000; // Ignition BTDC, Inj PW, Lambda, Eff — NEW
        public const uint PgnVibDiagnostics    = 0x18FF5000; // Vibration RMS + FFT peaks

        // ── PGN 0xFEE0: Engine Speed & Power ────────────────────────────────
        public static CanFrame EncodeSpeedAndPower(AeroEngineTelemetry telem)
        {
            // Byte 0-1: RPM  (LSB first, 0.125 rpm/bit resolution)
            ushort rawRpm = (ushort)(telem.Rpm * 8.0);
            // Byte 2-3: MAP  (LSB first, 0.1 hPa/bit)
            ushort rawMap = (ushort)(telem.ManifoldPressureHpa * 10.0);

            byte[] payload = new byte[8];
            payload[0] = (byte)(rawRpm & 0xFF);
            payload[1] = (byte)((rawRpm >> 8) & 0xFF);
            payload[2] = (byte)(rawMap & 0xFF);
            payload[3] = (byte)((rawMap >> 8) & 0xFF);
            payload[4] = (byte)Math.Clamp(telem.FuelFlowLph * 2.0, 0, 255);   // 0.5 L/h per bit
            payload[5] = (byte)Math.Clamp(telem.PowerOutputKw, 0, 255);        // 1 kW per bit
            payload[6] = (byte)Math.Clamp(telem.HealthIndex * 100.0, 0, 255); // 1% per bit
            payload[7] = (byte)Math.Clamp(telem.OverallVibrationG * 10.0, 0, 255);

            return MakeFrame(PgnEngineSpeed, payload, telem.TimestampMs);
        }

        // ── PGN 0xFEEE: Temperatures ────────────────────────────────────────
        public static CanFrame EncodeTemperatures(AeroEngineTelemetry telem)
        {
            byte[] payload = new byte[8];
            payload[0] = (byte)Math.Clamp(telem.ChtCelsius[0], 0, 255);
            payload[1] = (byte)Math.Clamp(telem.ChtCelsius[1], 0, 255);
            payload[2] = (byte)Math.Clamp(telem.ChtCelsius[2], 0, 255);
            payload[3] = (byte)Math.Clamp(telem.ChtCelsius[3], 0, 255);
            payload[4] = (byte)Math.Clamp(telem.OilTempCelsius, 0, 255);
            payload[5] = (byte)Math.Clamp(telem.OilPressureBar * 10.0, 0, 255);
            payload[6] = (byte)Math.Clamp(telem.CoolantTempCelsius, 0, 255);
            payload[7] = 0x00;  // reserved

            return MakeFrame(PgnTemperatures, payload, telem.TimestampMs);
        }

        // ── PGN 0xFF10: FADEC Injection & Combustion (NEW) ──────────────────
        public static CanFrame EncodeInjectionFadec(AeroEngineTelemetry telem)
        {
            byte[] payload = new byte[8];
            // Byte 0: Ignition timing BTDC  (1 deg/bit)
            payload[0] = (byte)Math.Clamp(telem.IgnitionTimingBtdc, 0, 255);
            // Byte 1: Injection timing BTDC (0.1 deg/bit → ×10)
            payload[1] = (byte)Math.Clamp(telem.InjectionTimingBtdc * 10.0, 0, 255);
            // Byte 2-3: Injection pulse width (0.01 ms/bit → ×100, LSB first)
            ushort rawPw = (ushort)Math.Clamp(telem.InjectionPulseWidthMs * 100.0, 0, 65535);
            payload[2] = (byte)(rawPw & 0xFF);
            payload[3] = (byte)((rawPw >> 8) & 0xFF);
            // Byte 4: Lambda AFR  (offset 0.5, 0.01/bit → ×100)
            payload[4] = (byte)Math.Clamp((telem.LambdaAfr - 0.5) * 100.0, 0, 255);
            // Byte 5: Combustion efficiency (1%/bit)
            payload[5] = (byte)Math.Clamp(telem.CombustionEfficiencyPct, 0, 255);
            payload[6] = 0x00;  // reserved
            payload[7] = 0x00;  // reserved

            return MakeFrame(PgnInjectionFadec, payload, telem.TimestampMs);
        }

        // ── PGN 0xFF50: Vibration Diagnostics ───────────────────────────────
        public static CanFrame EncodeVibration(AeroEngineTelemetry telem)
        {
            byte[] payload = new byte[8];
            payload[0] = (byte)Math.Clamp(telem.OverallVibrationG * 20.0, 0, 255); // 0.05g/bit
            payload[1] = 0xFF; // placeholder for FFT peak 1X
            payload[2] = 0xFF; // placeholder for FFT peak 2X
            payload[3] = 0x00;
            payload[4] = 0x00;
            payload[5] = 0x00;
            payload[6] = 0x00;
            payload[7] = 0x00;
            return MakeFrame(PgnVibDiagnostics, payload, telem.TimestampMs);
        }

        private static CanFrame MakeFrame(uint id, byte[] data, long tsMs) =>
            new CanFrame { CanId = id, Dlc = 8, Data = data, TimestampUs = tsMs * 1000L };
    }
}
