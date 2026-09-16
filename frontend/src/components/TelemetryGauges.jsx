import React from 'react';
import { Gauge, Droplets, Zap, Flame, Wind } from 'lucide-react';

// Reusable Mature Military Avionics Circular Gauge
function CircularGauge({ value, min = 0, max = 100, label, unit, color = '#38bdf8', warningMin, warningMax, dangerMax }) {
  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
  const strokeDashoffset = 251.2 - (251.2 * percentage) / 100;
  
  let dialColor = color;
  if (dangerMax && value >= dangerMax) dialColor = '#ef4444';
  else if (warningMax && value >= warningMax) dialColor = '#f59e0b';
  else if (warningMin && value <= warningMin) dialColor = '#f59e0b';

  return (
    <div className="flex flex-col items-center justify-center p-2.5 bg-[#0e121c] rounded border border-[#1b2130] hover:border-[#2a344d] transition-all">
      <div className="relative w-22 h-22 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Subtle Background Track */}
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="#1c2232"
            strokeWidth="5"
            fill="transparent"
          />
          {/* Active Precision Arc */}
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke={dialColor}
            strokeWidth="5"
            strokeDasharray="251.2"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{ transition: 'stroke-dashoffset 0.35s ease, stroke 0.35s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-base font-bold font-mono text-white tracking-tight leading-none">
            {typeof value === 'number' ? value.toFixed(value < 10 ? 1 : 0) : value}
          </span>
          <span className="text-[10px] font-mono text-slate-400 mt-0.5">{unit}</span>
        </div>
      </div>
      <span className="text-[11px] font-medium text-slate-300 uppercase tracking-wide mt-1.5 font-['Inter',sans-serif]">
        {label}
      </span>
    </div>
  );
}

export default function TelemetryGauges({ telemetry }) {
  const state = telemetry?.state || {};
  const rpm = state.rpm || 5000;
  const mapHpa = state.manifold_pressure_hpa || 1150;
  const oilPress = state.oil_pressure_bar || 3.85;
  const oilTemp = state.oil_temperature_c || 92;
  const fuelFlow = state.fuel_flow_lph || 18.5;
  const powerKw = state.power_output_kw || 65;
  const busVoltage = state.bus_voltage_v || 28.1;
  const turboRpm = state.turbo_rpm || 110000;

  return (
    <div className="gcs-card p-3">
      <div className="gcs-card-header mb-3">
        <span className="flex items-center gap-2">
          <Gauge size={15} className="text-sky-400" />
          <span>Propulsion Flight Telemetry (FADEC)</span>
        </span>
        <span className="text-[10.5px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 px-2 py-0.5 rounded">
          STREAM: 20 Hz LIVE
        </span>
      </div>

      {/* Main Precision Avionics Dials (Calm Aerospace Palette) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2.5">
        <CircularGauge
          value={rpm}
          min={0}
          max={6000}
          label="Engine RPM"
          unit="RPM"
          color="#38bdf8"
          warningMax={5500}
          dangerMax={5800}
        />
        <CircularGauge
          value={mapHpa}
          min={600}
          max={1500}
          label="Manifold Boost"
          unit="hPa"
          color="#60a5fa"
          warningMax={1350}
          dangerMax={1420}
        />
        <CircularGauge
          value={oilPress}
          min={0}
          max={6.0}
          label="Oil Pressure"
          unit="bar"
          color="#10b981"
          warningMin={2.0}
          dangerMax={5.5}
        />
        <CircularGauge
          value={oilTemp}
          min={40}
          max={140}
          label="Oil Temp"
          unit="°C"
          color="#f59e0b"
          warningMax={115}
          dangerMax={130}
        />
        <CircularGauge
          value={fuelFlow}
          min={0}
          max={35}
          label="Fuel Flow"
          unit="L/h"
          color="#38bdf8"
          warningMax={30}
          dangerMax={34}
        />
        <CircularGauge
          value={powerKw}
          min={0}
          max={90}
          label="Shaft Power"
          unit="kW"
          color="#e2e8f0"
          warningMax={80}
          dangerMax={86}
        />
      </div>

      {/* Auxiliary Telemetry Metrics Bar — Row 1 */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 pt-2.5 border-t border-[#1a202e] text-xs font-mono">
        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Zap size={13} className="text-amber-400" /> Bus Voltage:
          </span>
          <span className={`font-bold ${busVoltage < 27.0 ? 'text-red-400' : busVoltage < 27.5 ? 'text-amber-400' : 'text-white'}`}>
            {busVoltage.toFixed(1)} V
          </span>
        </div>

        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Zap size={13} className="text-yellow-400" /> Alternator:
          </span>
          <span className={`font-bold ${(state.alternator_current_a || 22.4) < 10 ? 'text-red-400' : 'text-slate-200'}`}>
            {(state.alternator_current_a || 22.4).toFixed(1)} A
          </span>
        </div>

        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Wind size={13} className="text-sky-400" /> Turbo Speed:
          </span>
          <span className="text-sky-300 font-bold">{(turboRpm / 1000).toFixed(0)}k RPM</span>
        </div>

        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Droplets size={13} className="text-blue-400" /> Fuel Rail:
          </span>
          <span className="text-white font-bold">{(state.fuel_pressure_bar || 3.0).toFixed(2)} bar</span>
        </div>
      </div>

      {/* Auxiliary Telemetry Metrics Bar — Row 2: FADEC Injection Parameters */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2 text-xs font-mono">
        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Flame size={13} className="text-amber-400" /> IGN Timing:
          </span>
          <span className="text-slate-200 font-bold">{(state.ignition_timing_btdc || 26.0).toFixed(1)}° BTDC</span>
        </div>

        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Droplets size={13} className="text-sky-400" /> INJ Timing:
          </span>
          <span className="text-slate-200 font-bold">{(state.injection_timing_btdc || 8.5).toFixed(1)}° BTDC</span>
        </div>

        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Wind size={13} className="text-teal-400" /> Lambda (λ):
          </span>
          <span className={`font-bold ${Math.abs((state.lambda_afr || 1.02) - 1.0) > 0.08 ? 'text-amber-400' : 'text-teal-300'}`}>
            λ {(state.lambda_afr || 1.02).toFixed(3)}
          </span>
        </div>

        <div className="bg-[#0e121c] p-2 rounded border border-[#1b2130] flex justify-between items-center">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Flame size={13} className="text-emerald-400" /> Comb. Eff:
          </span>
          <span className={`font-bold ${(state.combustion_efficiency_pct || 92.5) < 85 ? 'text-amber-400' : 'text-emerald-300'}`}>
            {(state.combustion_efficiency_pct || 92.5).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}
