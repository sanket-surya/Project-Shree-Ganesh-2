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

  const lvl = advisory.severity_level;
  const statusStyle = lvl === 'CRITICAL'
    ? { bg: 'rgba(255,59,59,0.12)',  border: 'rgba(255,59,59,0.4)',  color: '#FF3B3B',  pulse: true }
    : lvl === 'WARNING'
    ? { bg: 'rgba(255,184,0,0.10)',  border: 'rgba(255,184,0,0.35)', color: '#FFB800',  pulse: false }
    : { bg: 'rgba(0,255,163,0.07)',  border: 'rgba(0,255,163,0.25)', color: '#00FFA3',  pulse: false };

  return (
    <div className="gcs-card p-3 flex flex-col gap-2.5">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <ShieldAlert size={16} style={{ color: '#FFB800' }} />
          AI Advisory &amp; Recommended Action
        </span>
        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded"
          style={{ background: statusStyle.bg, border: `1px solid ${statusStyle.border}`, color: statusStyle.color,
            animation: statusStyle.pulse ? 'pulse-crit 1.4s ease-in-out infinite' : 'none' }}>
          {advisory.status.replace(/_/g, ' ')}
        </span>
      </div>

      {/* Recommendation — plain language */}
      <div className="flex items-start gap-2 text-[11px] font-mono p-2.5 rounded"
        style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
        <ArrowRightCircle size={14} style={{ color: '#00D4FF', flexShrink: 0, marginTop: 1 }} />
        <span style={{ color: '#C8DDF0', lineHeight: '1.5' }}>{advisory.recommendation}</span>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
        <div className="p-2 rounded flex items-center justify-between"
          style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Power De-rate:</span>
          <span className="font-bold" style={{ color: advisory.power_derate_pct > 0 ? '#FFB800' : '#00FFA3' }}>
            {advisory.power_derate_pct > 0 ? `-${advisory.power_derate_pct}%` : 'FULL POWER'}
          </span>
        </div>
        <div className="p-2 rounded flex items-center justify-between"
          style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
          <span className="flex items-center gap-1" style={{ color: 'var(--text-secondary)' }}>
            <Compass size={12} style={{ color: '#00D4FF' }} /> Glide Range:
          </span>
          <span className="font-bold" style={{ color: '#00D4FF' }}>{advisory.glide_range_nm} NM</span>
        </div>
      </div>

      {/* Action Checklist */}
      <div className="pt-1" style={{ borderTop: '1px solid var(--border-divider)' }}>
        <div className="flex items-center gap-1.5 text-[11px] font-semibold mb-1.5" style={{ color: '#8BADC8' }}>
          <CheckSquare size={12} style={{ color: '#00D4FF' }} />
          PILOT CHECKLIST:
        </div>
        <ul className="space-y-1">
          {advisory.checklist.map((item, idx) => (
            <li key={idx} className="flex items-start gap-1.5 px-2 py-1 rounded text-[11px] font-mono"
              style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-subtle)' }}>
              <span className="font-bold" style={{ color: '#00D4FF' }}>{idx + 1}.</span>
              <span style={{ color: '#B0C8E0' }}>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
