import React from 'react';
import { Gauge, Droplets, Zap, Flame, Wind } from 'lucide-react';

// Deep Space Tactical Circular Gauge
function CircularGauge({ value, min = 0, max = 100, label, unit, color = '#00D4FF', warningMin, warningMax, dangerMax }) {
  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
  const strokeDashoffset = 251.2 - (251.2 * percentage) / 100;

  let dialColor = color;
  if (dangerMax && value >= dangerMax) dialColor = '#FF3B3B';
  else if (warningMax && value >= warningMax) dialColor = '#FFB800';
  else if (warningMin && value <= warningMin) dialColor = '#FFB800';

  const isWarn   = dialColor === '#FFB800';
  const isCrit   = dialColor === '#FF3B3B';
  const glowColor = isCrit ? 'rgba(255,59,59,0.25)' : isWarn ? 'rgba(255,184,0,0.2)' : 'rgba(0,212,255,0.15)';

  return (
    <div className="flex flex-col items-center justify-center p-2.5 rounded-lg transition-all"
      style={{ background: 'var(--bg-card-inner)', border: `1px solid ${isCrit ? 'rgba(255,59,59,0.35)' : isWarn ? 'rgba(255,184,0,0.25)' : 'var(--border-card)'}` }}>
      <div className="relative w-22 h-22 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background Track */}
          <circle cx="50" cy="50" r="40" stroke="#1A2640" strokeWidth="5" fill="transparent" />
          {/* Active Arc */}
          <circle
            cx="50" cy="50" r="40"
            stroke={dialColor}
            strokeWidth="5"
            strokeDasharray="251.2"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 0.35s ease, stroke 0.35s ease',
              filter: `drop-shadow(0 0 4px ${glowColor})`
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-base font-bold font-mono leading-none" style={{ color: dialColor }}>
            {typeof value === 'number' ? value.toFixed(value < 10 ? 1 : 0) : value}
          </span>
          <span className="text-[10px] font-mono mt-0.5" style={{ color: 'var(--text-muted)' }}>{unit}</span>
        </div>
      </div>
      <span className="text-[11px] font-semibold uppercase tracking-wide mt-1.5 text-center"
        style={{ color: isCrit ? '#FF3B3B' : isWarn ? '#FFB800' : 'var(--text-secondary)' }}>
        {label}
      </span>
    </div>
  );
}

export default function TelemetryGauges({ telemetry }) {
  const state = telemetry?.state || {};
  const rpm       = state.rpm || 5000;
  const mapHpa    = state.manifold_pressure_hpa || 1150;
  const oilPress  = state.oil_pressure_bar || 3.85;
  const oilTemp   = state.oil_temperature_c || 92;
  const fuelFlow  = state.fuel_flow_lph || 18.5;
  const powerKw   = state.power_output_kw || 65;
  const busVoltage = state.bus_voltage_v || 28.1;
  const turboRpm  = state.turbo_rpm || 110000;

  return (
    <div className="gcs-card p-3">
      <div className="gcs-card-header mb-3">
        <span className="flex items-center gap-2">
          <Gauge size={15} style={{ color: '#00D4FF' }} />
          <span>Engine Telemetry — Live Sensors</span>
        </span>
        <span className="text-[10.5px] font-mono font-semibold px-2 py-0.5 rounded"
          style={{ background: 'rgba(0,255,163,0.08)', border: '1px solid rgba(0,255,163,0.3)', color: '#00FFA3' }}>
          ● LIVE 20 Hz
        </span>
      </div>

      {/* Primary Gauges — 4 most important (Phase 1: simplified) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-2">
        <CircularGauge value={rpm}      min={0}    max={6000} label="Engine RPM"    unit="RPM"  color="#00D4FF" warningMax={5500} dangerMax={5800} />
        <CircularGauge value={oilTemp}  min={40}   max={140}  label="Oil Temp"      unit="°C"   color="#FFB800" warningMax={115}  dangerMax={130} />
        <CircularGauge value={fuelFlow} min={0}    max={35}   label="Fuel Flow"     unit="L/h"  color="#00D4FF" warningMax={30}   dangerMax={34} />
        <CircularGauge value={powerKw}  min={0}    max={90}   label="Shaft Power"   unit="kW"   color="#00FFA3" warningMax={80}   dangerMax={86} />
      </div>

      {/* Secondary Gauges */}
      <div className="grid grid-cols-2 sm:grid-cols-2 gap-2.5">
        <CircularGauge value={oilPress} min={0}    max={6.0}  label="Oil Pressure"  unit="bar"  color="#00FFA3" warningMin={2.0} dangerMax={5.5} />
        <CircularGauge value={mapHpa}   min={600}  max={1500} label="Boost (MAP)"   unit="hPa"  color="#A78BFA" warningMax={1350} dangerMax={1420} />
      </div>

      {/* Aux Bar Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 pt-2.5 text-xs font-mono"
        style={{ borderTop: '1px solid var(--border-divider)' }}>
        <div className="p-2 rounded flex justify-between items-center"
          style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
          <span className="flex items-center gap-1.5" style={{ color: 'var(--text-secondary)' }}>
            <Zap size={13} style={{ color: '#FFB800' }} /> Bus Voltage
          </span>
          <span className="font-bold" style={{ color: busVoltage < 27.0 ? '#FF3B3B' : busVoltage < 27.5 ? '#FFB800' : '#E8F4FD' }}>
            {busVoltage.toFixed(1)} V
          </span>
        </div>

        <div className="p-2 rounded flex justify-between items-center"
          style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
          <span className="flex items-center gap-1.5" style={{ color: 'var(--text-secondary)' }}>
            <Wind size={13} style={{ color: '#00D4FF' }} /> Turbo
          </span>
          <span className="font-bold" style={{ color: '#00D4FF' }}>{(turboRpm / 1000).toFixed(0)}k RPM</span>
        </div>

        <div className="p-2 rounded flex justify-between items-center"
          style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
          <span className="flex items-center gap-1.5" style={{ color: 'var(--text-secondary)' }}>
            <Droplets size={13} style={{ color: '#A78BFA' }} /> Fuel Rail
          </span>
          <span className="font-bold" style={{ color: '#E8F4FD' }}>{(state.fuel_pressure_bar || 3.0).toFixed(2)} bar</span>
        </div>

        <div className="p-2 rounded flex justify-between items-center"
          style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
          <span className="flex items-center gap-1.5" style={{ color: 'var(--text-secondary)' }}>
            <Flame size={13} style={{ color: '#00FFA3' }} /> Efficiency
          </span>
          <span className="font-bold" style={{ color: (state.combustion_efficiency_pct || 92.5) < 85 ? '#FFB800' : '#00FFA3' }}>
            {(state.combustion_efficiency_pct || 92.5).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}
