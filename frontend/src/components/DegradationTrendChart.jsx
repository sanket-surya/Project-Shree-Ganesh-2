import React, { useEffect, useRef, useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';

// Pure local SVG-based mini sparkline — zero external dependencies
function Sparkline({ data, color, height = 40, width = 180, alertVal, critVal, unit = '' }) {
  if (!data || data.length < 2) return (
    <div className="flex items-center justify-center h-10 text-[10px] font-mono text-slate-500">COLLECTING DATA...</div>
  );

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * height;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  const lastVal = data[data.length - 1];
  const prevVal = data[Math.max(0, data.length - 5)];
  const trend = lastVal - prevVal;

  // Alert/critical lines
  const alertY = alertVal !== undefined ? height - ((alertVal - min) / range) * height : null;
  const critY = critVal !== undefined ? height - ((critVal - min) / range) * height : null;

  return (
    <div className="relative">
      <svg width={width} height={height} className="overflow-visible">
        {/* Alert band */}
        {alertY !== null && alertY >= 0 && alertY <= height && (
          <line x1="0" y1={alertY} x2={width} y2={alertY} stroke="#f59e0b" strokeWidth="0.8" strokeDasharray="3,2" opacity="0.6" />
        )}
        {critY !== null && critY >= 0 && critY <= height && (
          <line x1="0" y1={critY} x2={width} y2={critY} stroke="#ef4444" strokeWidth="0.8" strokeDasharray="3,2" opacity="0.6" />
        )}
        {/* Glow fill */}
        <defs>
          <linearGradient id={`grad-${color.replace('#','')}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0.02" />
          </linearGradient>
        </defs>
        <polyline
          points={pts + ` ${width},${height} 0,${height}`}
          fill={`url(#grad-${color.replace('#','')})`}
          stroke="none"
        />
        {/* Main line */}
        <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
        {/* Last point dot */}
        <circle
          cx={((data.length - 1) / (data.length - 1)) * width}
          cy={height - ((lastVal - min) / range) * height}
          r="2.5" fill={color}
        />
      </svg>
      <div className="absolute top-0 right-0 text-[10px] font-mono" style={{ color }}>
        {lastVal?.toFixed(1)}{unit}
        <span className="ml-1 text-slate-500">
          {trend > 0.1 ? '↑' : trend < -0.1 ? '↓' : '→'}
        </span>
      </div>
    </div>
  );
}

function TrendLabel({ trend, threshWarn, threshCrit }) {
  if (Math.abs(trend) < 0.05) return (
    <span className="flex items-center gap-0.5 text-emerald-400"><Minus size={10} />STABLE</span>
  );
  if (trend > threshCrit) return (
    <span className="flex items-center gap-0.5 text-red-400 animate-pulse"><TrendingUp size={10} />RISING CRITICAL</span>
  );
  if (trend > threshWarn) return (
    <span className="flex items-center gap-0.5 text-amber-400"><TrendingUp size={10} />RISING</span>
  );
  return (
    <span className="flex items-center gap-0.5 text-cyan-400"><TrendingDown size={10} />DECREASING</span>
  );
}

export default function DegradationTrendChart({ telemetry, historyBuffer }) {
  const state = telemetry?.state || {};

  // Use passed history buffer from App (last 60 telemetry frames)
  const chtData = (historyBuffer || []).map(f => f?.state?.cht_c ? Math.max(...f.state.cht_c) : null).filter(v => v !== null);
  const egtData = (historyBuffer || []).map(f => f?.state?.egt_c ? Math.max(...f.state.egt_c) : null).filter(v => v !== null);
  const oilData = (historyBuffer || []).map(f => f?.state?.oil_temperature_c ?? null).filter(v => v !== null);
  const vibData = (historyBuffer || []).map(f => f?.state?.overall_vibration_g ?? null).filter(v => v !== null);
  const effData = (historyBuffer || []).map(f => f?.state?.combustion_efficiency_pct ?? null).filter(v => v !== null);

  const chtTrend = chtData.length > 5 ? chtData[chtData.length - 1] - chtData[Math.max(0, chtData.length - 10)] : 0;
  const egtTrend = egtData.length > 5 ? egtData[egtData.length - 1] - egtData[Math.max(0, egtData.length - 10)] : 0;
  const vibTrend = vibData.length > 5 ? vibData[vibData.length - 1] - vibData[Math.max(0, vibData.length - 10)] : 0;

  const rows = [
    {
      label: 'CHT MAX',
      unit: '°C',
      color: '#f97316',
      data: chtData,
      alertVal: 150,
      critVal: 170,
      threshWarn: 3,
      threshCrit: 10,
      trend: chtTrend,
      current: state.cht_c ? Math.max(...state.cht_c) : null,
      limit: '170°C',
    },
    {
      label: 'EGT MAX',
      unit: '°C',
      color: '#ef4444',
      data: egtData,
      alertVal: 900,
      critVal: 950,
      threshWarn: 5,
      threshCrit: 20,
      trend: egtTrend,
      current: state.egt_c ? Math.max(...state.egt_c) : null,
      limit: '950°C',
    },
    {
      label: 'OIL TEMP',
      unit: '°C',
      color: '#a78bfa',
      data: oilData,
      alertVal: 120,
      critVal: 140,
      threshWarn: 2,
      threshCrit: 8,
      trend: oilData.length > 5 ? oilData[oilData.length - 1] - oilData[Math.max(0, oilData.length - 10)] : 0,
      current: state.oil_temperature_c,
      limit: '140°C',
    },
    {
      label: 'VIBRATION',
      unit: 'g',
      color: '#22d3ee',
      data: vibData,
      alertVal: 2.5,
      critVal: 4.0,
      threshWarn: 0.2,
      threshCrit: 0.8,
      trend: vibTrend,
      current: state.overall_vibration_g,
      limit: '4.0g',
    },
    {
      label: 'COMBUSTION EFF.',
      unit: '%',
      color: '#4ade80',
      data: effData,
      alertVal: null,
      critVal: null,
      threshWarn: -3,
      threshCrit: -8,
      trend: effData.length > 5 ? effData[effData.length - 1] - effData[Math.max(0, effData.length - 10)] : 0,
      current: state.combustion_efficiency_pct,
      limit: '>85%',
    },
  ];

  return (
    <div className="gcs-card p-3 flex flex-col gap-2">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <Activity size={16} className="text-purple-400" />
          DEGRADATION TREND MONITOR — ROLLING 60-POINT ANALYSIS
        </span>
        <span className="text-[11px] font-mono text-purple-300 bg-purple-950/60 border border-purple-500/30 px-2 py-0.5 rounded">
          {historyBuffer?.length || 0} / 60 FRAMES
        </span>
      </div>

      <div className="mt-1 space-y-3">
        {rows.map((row) => (
          <div key={row.label} className="bg-slate-900/60 rounded border border-slate-800 p-2">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold" style={{ color: row.color }}>{row.label}</span>
                <span className="text-[10px] font-mono text-slate-400">LIMIT: {row.limit}</span>
              </div>
              <div className="flex items-center gap-2 text-[10px] font-mono">
                <TrendLabel trend={row.trend} threshWarn={row.threshWarn} threshCrit={row.threshCrit} />
                {row.current != null && (
                  <span className="text-slate-200 font-bold">{row.current?.toFixed(1)}{row.unit}</span>
                )}
              </div>
            </div>
            <Sparkline
              data={row.data}
              color={row.color}
              alertVal={row.alertVal}
              critVal={row.critVal}
              unit={row.unit}
              width={320}
              height={38}
            />
            {row.alertVal && (
              <div className="flex items-center gap-3 mt-1 text-[9px] font-mono text-slate-500">
                <span className="text-amber-400">─ ─ WARN: {row.alertVal}{row.unit}</span>
                <span className="text-red-400">─ ─ CRIT: {row.critVal}{row.unit}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
