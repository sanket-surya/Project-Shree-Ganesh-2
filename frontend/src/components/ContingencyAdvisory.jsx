import React from 'react';
import { ShieldAlert, Compass, CheckSquare, ArrowRightCircle } from 'lucide-react';

export default function ContingencyAdvisory({ telemetry }) {
  const advisory = telemetry?.ai?.contingency_advisory || {
    status: 'NORMAL_OPERATION',
    severity_level: 'INFO',
    recommendation: 'All engine thermal and mechanical parameters nominal. Cleared for continued ISR loiter.',
    power_derate_pct: 0,
    glide_range_nm: 12.5,
    checklist: ['Standard cruise scan', 'Log engine telemetry at waypoint']
  };

  const getStatusBadge = (lvl) => {
    if (lvl === 'CRITICAL') return 'bg-red-950/90 border-red-500/70 text-red-400 animate-pulse';
    if (lvl === 'WARNING') return 'bg-amber-950/80 border-amber-500/50 text-amber-400';
    return 'bg-emerald-950/70 border-emerald-500/40 text-emerald-400';
  };

  return (
    <div className="gcs-card p-3 flex flex-col justify-between">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <ShieldAlert size={16} className="text-amber-400" />
          AUTONOMOUS MISSION RELIABILITY & CONTINGENCY ADVISORY
        </span>
        <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getStatusBadge(advisory.severity_level)}`}>
          {advisory.status.replace(/_/g, ' ')}
        </span>
      </div>

      {/* Recommendation — single line chip */}
      <div className="mt-2 flex items-start gap-2 text-[11px] font-mono">
        <ArrowRightCircle size={13} className="text-cyan-400 shrink-0 mt-0.5" />
        <span className="text-slate-300 leading-tight">{advisory.recommendation}</span>
      </div>

      {/* Numerical Metrics: De-rate and Glide Envelope */}
      <div className="mt-2.5 grid grid-cols-2 gap-2.5 text-xs font-mono">
        <div className="bg-slate-900/50 p-2 rounded border border-slate-800 flex items-center justify-between">
          <span className="text-slate-400">Power De-rate:</span>
          <span className={`font-bold ${advisory.power_derate_pct > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {advisory.power_derate_pct > 0 ? `-${advisory.power_derate_pct}% MAX` : '0% (FULL)'}
          </span>
        </div>

        <div className="bg-slate-900/50 p-2 rounded border border-slate-800 flex items-center justify-between">
          <span className="text-slate-400 flex items-center gap-1">
            <Compass size={13} className="text-cyan-400" /> Max Glide:
          </span>
          <span className="text-cyan-300 font-bold">{advisory.glide_range_nm} NM</span>
        </div>
      </div>

      {/* Action Checklist */}
      <div className="mt-2.5 pt-2 border-t border-slate-800">
        <div className="text-[11px] font-mono text-slate-400 mb-1 flex items-center gap-1 font-semibold text-slate-200">
          <CheckSquare size={12} className="text-cyan-400" />
          PILOT / AUTOPILOT CONTINGENCY CHECKLIST:
        </div>
        <ul className="space-y-1 text-[11px] font-mono text-slate-300">
          {advisory.checklist.map((item, idx) => (
            <li key={idx} className="flex items-start gap-1.5 bg-slate-950/40 px-2 py-1 rounded border border-slate-800/60">
              <span className="text-cyan-400 font-bold">{idx + 1}.</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
