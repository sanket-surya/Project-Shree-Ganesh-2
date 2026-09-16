import React from 'react';
import { Thermometer, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function CylinderThermalMatrix({ telemetry }) {
  const cht = telemetry?.state?.cht_c || [110, 111.5, 113, 112];
  const egt = telemetry?.state?.egt_c || [810, 815, 808, 812];

  const maxCht = Math.max(...cht);
  const minCht = Math.min(...cht);
  const deltaCht = maxCht - minCht;

  const maxEgt = Math.max(...egt);
  const minEgt = Math.min(...egt);
  const deltaEgt = maxEgt - minEgt;

  // Imbalance alerts
  const isChtImbalance = deltaCht > 25.0;
  const isEgtImbalance = deltaEgt > 65.0;

  const getChtBarColor = (temp) => {
    if (temp >= 135) return 'bg-red-500';
    if (temp >= 122) return 'bg-amber-500';
    return 'bg-sky-500';
  };

  const getEgtBarColor = (temp) => {
    if (temp >= 860) return 'bg-red-500';
    if (temp >= 840) return 'bg-amber-500';
    return 'bg-blue-600';
  };

  return (
    <div className="gcs-card p-3 flex flex-col justify-between">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <Thermometer size={15} className="text-amber-400" />
          <span>CYLINDER THERMAL BALANCE MATRIX</span>
        </span>
        <div className="flex items-center gap-2">
          {isChtImbalance || isEgtImbalance ? (
            <span className="text-[10px] font-mono text-red-400 bg-red-950/60 border border-red-500/50 px-2 py-0.5 rounded flex items-center gap-1">
              <AlertCircle size={12} /> IMBALANCE DETECTED
            </span>
          ) : (
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
              <CheckCircle2 size={12} /> BALANCED
            </span>
          )}
        </div>
      </div>

      {/* 4-Cylinder Head Temperatures (CHT) */}
      <div className="mt-2">
        <div className="flex justify-between items-center text-xs font-mono text-slate-400 mb-1.5">
          <span className="font-semibold text-slate-300">CYLINDER HEAD TEMPS (CHT)</span>
          <span>Spread ΔT: <strong className={isChtImbalance ? 'text-red-400' : 'text-slate-200'}>{deltaCht.toFixed(1)}°C</strong> (Limit: 30°C)</span>
        </div>
        <div className="grid grid-cols-4 gap-2">
          {cht.map((temp, idx) => {
            const pct = Math.min(100, Math.max(0, ((temp - 60) / (150 - 60)) * 100));
            return (
              <div key={`cht-${idx}`} className="bg-[#0e121b] p-2 rounded border border-[#1a202e] flex flex-col">
                <div className="flex justify-between text-[11px] font-mono">
                  <span className="text-slate-400">CYL {idx + 1}</span>
                  <span className={`font-bold ${temp > 130 ? 'text-red-400' : 'text-slate-100'}`}>{temp.toFixed(1)}°C</span>
                </div>
                {/* Horizontal Progress Bar */}
                <div className="w-full h-1.5 bg-[#161a26] rounded-full mt-1.5 overflow-hidden">
                  <div
                    className={`h-full ${getChtBarColor(temp)} transition-all duration-300`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4-Cylinder Exhaust Gas Temperatures (EGT) */}
      <div className="mt-3">
        <div className="flex justify-between items-center text-xs font-mono text-slate-400 mb-1.5">
          <span className="font-semibold text-slate-200">EXHAUST GAS TEMPS (EGT)</span>
          <span>Spread ΔT: <strong className={isEgtImbalance ? 'text-red-400' : 'text-orange-400'}>{deltaEgt.toFixed(1)}°C</strong> (Limit: 75°C)</span>
        </div>
        <div className="grid grid-cols-4 gap-2">
          {egt.map((temp, idx) => {
            const pct = Math.min(100, Math.max(0, ((temp - 650) / (950 - 650)) * 100));
            return (
              <div key={`egt-${idx}`} className="bg-slate-900/60 p-2 rounded border border-slate-800 flex flex-col">
                <div className="flex justify-between text-[11px] font-mono">
                  <span className="text-slate-400">EXH {idx + 1}</span>
                  <span className={`font-bold ${temp > 880 ? 'text-red-400' : 'text-slate-100'}`}>{temp.toFixed(0)}°C</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
                  <div
                    className={`h-full ${getEgtBarColor(temp)} transition-all duration-300`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
