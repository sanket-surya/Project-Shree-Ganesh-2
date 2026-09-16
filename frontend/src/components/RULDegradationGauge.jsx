import React from 'react';
import { Clock, HeartPulse, Wrench } from 'lucide-react';

export default function RULDegradationGauge({ telemetry }) {
  const ai = telemetry?.ai || {};
  const rulHours = ai.predicted_rul_hours !== undefined ? ai.predicted_rul_hours : 875.0;
  const healthIndex = ai.health_index !== undefined ? ai.health_index : 0.98;
  const primaryFault = ai.primary_fault || 'Nominal';

  // Subsystem health calculation based on active fault
  const getSubsystemHealth = () => {
    let pistons = 98;
    let turbo = 96;
    let lube = 99;
    let cooling = 97;
    let valves = 98;

    if (primaryFault === 'Cylinder_Misfire') pistons = 35;
    else if (primaryFault === 'Turbo_Degradation') turbo = 42;
    else if (primaryFault === 'Oil_Starvation') { lube = 12; pistons = 45; }
    else if (primaryFault === 'Coolant_Loss') { cooling = 18; pistons = 50; }
    else if (primaryFault === 'Combustion_Knock') { pistons = 40; valves = 55; }
    else if (primaryFault === 'Valve_Leakage') { valves = 38; }

    return { pistons, turbo, lube, cooling, valves };
  };

  const subs = getSubsystemHealth();

  const getHealthColor = (val) => {
    if (val > 80) return 'text-emerald-400 bg-emerald-500';
    if (val > 50) return 'text-amber-400 bg-amber-500';
    return 'text-red-400 bg-red-500';
  };

  return (
    <div className="gcs-card p-3 flex flex-col justify-between">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <HeartPulse size={16} className="text-emerald-400" />
          PROGNOSTICS & REMAINING USEFUL LIFE (RUL)
        </span>
        <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 rounded">
          TBO LIMIT: 1200 HRS
        </span>
      </div>

      {/* Main RUL Display Grid */}
      <div className="mt-2.5 grid grid-cols-2 gap-3">
        {/* RUL Hours Remaining */}
        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800 flex flex-col items-center justify-center text-center">
          <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400">
            <Clock size={13} className="text-cyan-400" />
            PREDICTED RUL
          </div>
          <div className={`text-2xl font-bold font-mono mt-1 ${rulHours < 200 ? 'text-red-400 glow-red' : 'text-cyan-300 glow-cyan'}`}>
            {rulHours.toFixed(1)} <span className="text-sm font-normal text-slate-400">HRS</span>
          </div>
          <div className="text-[10px] font-mono text-slate-400 mt-0.5">
            ~{Math.round(rulHours / 8)} Missions Remaining
          </div>
        </div>

        {/* Composite Health Index */}
        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800 flex flex-col items-center justify-center text-center">
          <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400">
            <Wrench size={13} className="text-amber-400" />
            HEALTH INDEX
          </div>
          <div className={`text-2xl font-bold font-mono mt-1 ${healthIndex < 0.6 ? 'text-red-400' : 'text-emerald-400 glow-green'}`}>
            {(healthIndex * 100).toFixed(0)}%
          </div>
          <div className="text-[10px] font-mono text-slate-400 mt-0.5">
            Degradation: {((1.0 - healthIndex) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Subsystem Health Progress Bars */}
      <div className="mt-3 pt-2 border-t border-slate-800 space-y-1.5 text-xs font-mono">
        <div className="text-[11px] text-slate-400 font-semibold mb-1">PROPULSION SUB-SYSTEM INTEGRITY</div>

        {/* Pistons */}
        <div className="flex items-center justify-between">
          <span className="text-slate-300 text-[11px]">Combustion & Pistons:</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full ${getHealthColor(subs.pistons).split(' ')[1]}`} style={{ width: `${subs.pistons}%` }} />
            </div>
            <span className={`w-8 text-right font-bold text-[11px] ${getHealthColor(subs.pistons).split(' ')[0]}`}>{subs.pistons}%</span>
          </div>
        </div>

        {/* Turbo */}
        <div className="flex items-center justify-between">
          <span className="text-slate-300 text-[11px]">Turbocharger & Boost:</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full ${getHealthColor(subs.turbo).split(' ')[1]}`} style={{ width: `${subs.turbo}%` }} />
            </div>
            <span className={`w-8 text-right font-bold text-[11px] ${getHealthColor(subs.turbo).split(' ')[0]}`}>{subs.turbo}%</span>
          </div>
        </div>

        {/* Lubrication */}
        <div className="flex items-center justify-between">
          <span className="text-slate-300 text-[11px]">Lubrication Circuit:</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full ${getHealthColor(subs.lube).split(' ')[1]}`} style={{ width: `${subs.lube}%` }} />
            </div>
            <span className={`w-8 text-right font-bold text-[11px] ${getHealthColor(subs.lube).split(' ')[0]}`}>{subs.lube}%</span>
          </div>
        </div>

        {/* Cooling */}
        <div className="flex items-center justify-between">
          <span className="text-slate-300 text-[11px]">Cooling System:</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full ${getHealthColor(subs.cooling).split(' ')[1]}`} style={{ width: `${subs.cooling}%` }} />
            </div>
            <span className={`w-8 text-right font-bold text-[11px] ${getHealthColor(subs.cooling).split(' ')[0]}`}>{subs.cooling}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
