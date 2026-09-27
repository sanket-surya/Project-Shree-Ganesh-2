import React from 'react';
import { Clock, HeartPulse, Wrench } from 'lucide-react';

export default function RULDegradationGauge({ telemetry }) {
  const ai = telemetry?.ai || {};
  const rulHours   = ai.predicted_rul_hours !== undefined ? ai.predicted_rul_hours : 875.0;
  const healthIndex = ai.health_index !== undefined ? ai.health_index : 0.98;
  const primaryFault = ai.primary_fault || 'Nominal';

  const getSubsystemHealth = () => {
    let pistons = 98, turbo = 96, lube = 99, cooling = 97, valves = 98;
    if (primaryFault === 'Cylinder_Misfire')  pistons = 35;
    else if (primaryFault === 'Turbo_Degradation') turbo = 42;
    else if (primaryFault === 'Oil_Starvation')    { lube = 12; pistons = 45; }
    else if (primaryFault === 'Coolant_Loss')       { cooling = 18; pistons = 50; }
    else if (primaryFault === 'Combustion_Knock')   { pistons = 40; valves = 55; }
    else if (primaryFault === 'Valve_Leakage')      valves = 38;
    return { pistons, turbo, lube, cooling, valves };
  };

  const subs = getSubsystemHealth();
  const healthPct = Math.round(healthIndex * 100);
  const rulPct    = Math.min(100, (rulHours / 1200) * 100);

  const getBarClass = (val) => val > 80 ? 'bar-good' : val > 50 ? 'bar-warn' : 'bar-crit';
  const getTextColor = (val) => val > 80 ? '#00FFA3' : val > 50 ? '#FFB800' : '#FF3B3B';

  return (
    <div className="gcs-card p-3 flex flex-col gap-3">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <HeartPulse size={16} style={{ color: '#00FFA3' }} />
          Engine Remaining Life (RUL) &amp; Health
        </span>
        <span className="text-[10.5px] font-mono font-semibold px-2 py-0.5 rounded"
          style={{ background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.25)', color: '#00D4FF' }}>
          TBO LIMIT: 1200 HRS
        </span>
      </div>

      {/* Main RUL + Health Index */}
      <div className="grid grid-cols-2 gap-3">
        {/* RUL */}
        <div className="p-3 rounded-lg flex flex-col items-center justify-center text-center gap-1"
          style={{ background: 'var(--bg-card-inner)', border: `1px solid ${rulHours < 200 ? 'rgba(255,59,59,0.3)' : 'rgba(0,255,163,0.2)'}` }}>
          <div className="flex items-center gap-1 text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>
            <Clock size={13} style={{ color: '#00D4FF' }} />
            Remaining Life
          </div>
          <div className="text-2xl font-bold font-mono" style={{ color: rulHours < 200 ? '#FF3B3B' : '#00FFA3' }}>
            {rulHours.toFixed(0)}
            <span className="text-sm font-normal ml-1" style={{ color: 'var(--text-muted)' }}>hrs</span>
          </div>
          {/* RUL Progress Bar */}
          <div className="w-full h-2 rounded-full overflow-hidden mt-1" style={{ background: 'var(--border-card)' }}>
            <div className={`h-full rounded-full ${getBarClass(rulPct)}`} style={{ width: `${rulPct}%`, transition: 'width 0.5s ease' }} />
          </div>
          <div className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>
            ~{Math.round(rulHours / 8)} Missions Left
          </div>
        </div>

        {/* Health Index */}
        <div className="p-3 rounded-lg flex flex-col items-center justify-center text-center gap-1"
          style={{ background: 'var(--bg-card-inner)', border: `1px solid ${healthPct < 60 ? 'rgba(255,59,59,0.3)' : 'rgba(0,255,163,0.2)'}` }}>
          <div className="flex items-center gap-1 text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>
            <Wrench size={13} style={{ color: '#FFB800' }} />
            Health Index
          </div>
          <div className="text-2xl font-bold font-mono" style={{ color: healthPct < 60 ? '#FF3B3B' : '#00FFA3' }}>
            {healthPct}%
          </div>
          {/* Health Bar */}
          <div className="w-full h-2 rounded-full overflow-hidden mt-1" style={{ background: 'var(--border-card)' }}>
            <div className={`h-full rounded-full ${getBarClass(healthPct)}`} style={{ width: `${healthPct}%`, transition: 'width 0.5s ease' }} />
          </div>
          <div className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>
            Wear: {((1.0 - healthIndex) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Sub-system Health Bars */}
      <div className="pt-2 space-y-2 text-xs font-mono" style={{ borderTop: '1px solid var(--border-divider)' }}>
        <div className="text-[11px] font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>
          COMPONENT-LEVEL HEALTH
        </div>

        {[
          { label: 'Combustion & Pistons', val: subs.pistons },
          { label: 'Turbocharger & Boost',   val: subs.turbo },
          { label: 'Lubrication Circuit',     val: subs.lube },
          { label: 'Cooling System',          val: subs.cooling },
        ].map(({ label, val }) => (
          <div key={label} className="flex items-center justify-between gap-3">
            <span className="text-[11px] w-44 shrink-0" style={{ color: '#A8BDD0' }}>{label}</span>
            <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: 'var(--border-card)' }}>
              <div className={`h-full rounded-full ${getBarClass(val)}`} style={{ width: `${val}%`, transition: 'width 0.4s ease' }} />
            </div>
            <span className="text-[11px] font-bold w-9 text-right" style={{ color: getTextColor(val) }}>{val}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
