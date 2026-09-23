import React, { useState, useMemo } from "react";
const API = "http://localhost:8000";

const MISSION_TYPES = [
  { id:"ISR_PATROL", label:"ISR Patrol", dur:8, alt:4572 },
  { id:"BORDER_WATCH", label:"Border Watch", dur:12, alt:3048 },
  { id:"RECON", label:"Recon Strike", dur:4, alt:6096 },
  { id:"RELAY", label:"Comms Relay", dur:24, alt:9144 },
];

// Compute live Mission Success Probability from AI telemetry (Weibull-lite)
function computeLiveMissionSuccess(telemetry, durationHrs) {
  if (!telemetry) return null;
  const ai = telemetry?.ai || {};
  const health = ai.health_index ?? 0.95;           // 0-1
  const anomaly = ai.anomaly_score ?? 0.05;          // 0-1 (high = bad)
  const rul = ai.predicted_rul_hours ?? 875;          // hours
  const activeFault = telemetry?.state?.active_fault || 'NONE';
  const isCritical = activeFault !== 'NONE' && activeFault !== '';

  // Weibull-lite: β=2.2 (typical bearing wearout), η calibrated from health
  const beta = 2.2;
  // eta (characteristic life) scales with health and RUL
  const eta = Math.max(10, rul * health * (1 - anomaly * 0.5));
  // P(fail) over mission duration using Weibull CDF: 1 - exp(-(t/eta)^beta)
  const t = Math.max(0.5, durationHrs);
  const pFail = 1 - Math.exp(-Math.pow(t / eta, beta));
  const pSuccess = Math.max(0, Math.min(100, (1 - pFail) * 100));

  return {
    pSuccess: parseFloat(pSuccess.toFixed(1)),
    pFail: parseFloat((pFail * 100).toFixed(2)),
    health: parseFloat((health * 100).toFixed(1)),
    rul: parseFloat(rul.toFixed(0)),
    anomaly: parseFloat(anomaly.toFixed(3)),
    activeFault,
    isCritical,
    eta: parseFloat(eta.toFixed(0)),
  };
}

export default function PreFlightMRI({ telemetry }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [missionType, setMissionType] = useState("ISR_PATROL");
  const [duration, setDuration] = useState(8);
  const [altitude, setAltitude] = useState(4572);

  // ── LIVE reactive Mission Success from AI telemetry ──────────────
  const live = useMemo(() => computeLiveMissionSuccess(telemetry, duration), [telemetry, duration]);

  const compute = async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch(API + "/api/mission-reliability", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ mission_duration_hrs:duration, mission_altitude_m:altitude, mission_type:missionType })
      });
      if (!r.ok) throw new Error("Server " + r.status);
      setResult(await r.json());
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const onMissionSelect = (m) => { setMissionType(m.id); setDuration(m.dur); setAltitude(m.alt); };

  const mri = result?.mri;
  const decColor = mri?.decision === "GO" ? "#00ff9d" : mri?.decision === "CAUTION" ? "#fbbf24" : "#ff4d6d";
  const mriPct = Math.round(mri?.mri_pct || 0);

  return (
    <div style={{ background:"linear-gradient(135deg,rgba(10,20,40,0.97),rgba(0,20,40,0.97))", border:"1px solid rgba(0,180,255,0.25)", borderRadius:"16px", padding:"22px", color:"#e2e8f0", fontFamily:"Inter,sans-serif" }}>
      <h2 style={{ margin:"0 0 5px", color:"#00b4ff", fontSize:"1.1rem" }}>🛫 PRE-FLIGHT GO / NO-GO</h2>
      <p style={{ margin:"0 0 12px", fontSize:"0.75rem", color:"#94a3b8" }}>Mission Reliability Index — Weibull + AHP engine clearance</p>

      {/* ── LIVE MISSION SUCCESS PROBABILITY — PREMIUM DEFENSE HUD ── */}
      {live && (() => {
        const col = live.isCritical ? '#ff4d6d' : live.pSuccess >= 90 ? '#00ff9d' : '#fbbf24';
        const bgGrad = live.isCritical
          ? 'linear-gradient(135deg,rgba(255,30,30,0.13),rgba(20,0,10,0.95))'
          : live.pSuccess >= 90
            ? 'linear-gradient(135deg,rgba(0,255,157,0.07),rgba(0,50,80,0.95))'
            : 'linear-gradient(135deg,rgba(251,191,36,0.10),rgba(40,25,0,0.95))';
        // SVG arc: 180° half-circle gauge
        const R = 52, cx = 70, cy = 68;
        const startAngle = 180, sweep = 180;
        const angle = startAngle + (live.pSuccess / 100) * sweep;
        const toRad = d => (d * Math.PI) / 180;
        const arcX = cx + R * Math.cos(toRad(angle));
        const arcY = cy + R * Math.sin(toRad(angle));
        const trackEnd = { x: cx + R * Math.cos(toRad(360)), y: cy + R * Math.sin(toRad(360)) };
        return (
          <div style={{
            background: bgGrad,
            border: `1.5px solid ${col}55`,
            borderRadius: '14px',
            padding: '14px 16px 10px',
            marginBottom: '12px',
            boxShadow: `0 0 24px ${col}18`,
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Animated pulse overlay on critical */}
            {live.isCritical && (
              <div style={{
                position:'absolute', inset:0, borderRadius:'14px',
                background:'rgba(255,30,30,0.04)',
                animation:'pulse 1.2s ease-in-out infinite'
              }} />
            )}
            <style>{`@keyframes pulse{0%,100%{opacity:0.3}50%{opacity:1}}`}</style>

            <div style={{ display:'flex', alignItems:'center', gap:'16px' }}>
              {/* SVG Arc Gauge */}
              <svg width="140" height="80" viewBox="0 0 140 80" style={{ flexShrink:0 }}>
                {/* Track */}
                <path d={`M ${cx-R},${cy} A ${R},${R} 0 0,1 ${cx+R},${cy}`}
                  fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="9" strokeLinecap="round"/>
                {/* Progress */}
                <path d={`M ${cx-R},${cy} A ${R},${R} 0 0,1 ${arcX},${arcY}`}
                  fill="none" stroke={col} strokeWidth="9" strokeLinecap="round"
                  style={{ filter:`drop-shadow(0 0 6px ${col}88)` }}/>
                {/* Dot at tip */}
                <circle cx={arcX} cy={arcY} r="5" fill={col} style={{ filter:`drop-shadow(0 0 5px ${col})` }}/>
                {/* Value */}
                <text x={cx} y={cy-4} textAnchor="middle" fill={col}
                  style={{ fontSize:'22px', fontWeight:900, fontFamily:'monospace' }}>
                  {live.pSuccess}%
                </text>
                <text x={cx} y={cy+12} textAnchor="middle" fill="#475569"
                  style={{ fontSize:'8px', fontFamily:'monospace' }}>
                  P(success)
                </text>
                <text x={cx-R+4} y={cy+14} fill="#374151" style={{ fontSize:'8px' }}>0%</text>
                <text x={cx+R-16} y={cy+14} fill="#374151" style={{ fontSize:'8px' }}>100%</text>
              </svg>

              {/* Right: Status + Sub-metrics */}
              <div style={{ flex:1 }}>
                <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'6px' }}>
                  <span style={{ fontSize:'0.65rem', fontWeight:800, letterSpacing:'0.1em', color:col }}>
                    ⚡ LIVE · MISSION SUCCESS
                  </span>
                  <span style={{ fontSize:'0.58rem', color:'#1e3a5f', background:col+'22', border:`1px solid ${col}44`, borderRadius:'4px', padding:'1px 6px', fontWeight:700 }}>
                    20 Hz
                  </span>
                </div>
                <div style={{ fontSize:'0.6rem', color:'#475569', marginBottom:'8px' }}>
                  Weibull CDF · β=2.2 · η={live.eta}h · {duration}h sortie
                </div>

                {/* Sub-indicator bars */}
                {[
                  { label:'Engine Health', val:live.health, unit:'%', max:100, col:'#00ff9d' },
                  { label:'RUL', val:Math.min(live.rul, 1000), unit:'h', max:1000, col:'#00b4ff' },
                  { label:'Anomaly Score', val:Math.round(live.anomaly*100), unit:'%', max:100, col:'#f59e0b', invert:true },
                ].map(({ label, val, unit, max, col:bc, invert }) => (
                  <div key={label} style={{ marginBottom:'5px' }}>
                    <div style={{ display:'flex', justifyContent:'space-between', fontSize:'0.6rem', color:'#475569', marginBottom:'2px' }}>
                      <span>{label}</span>
                      <span style={{ color: bc, fontWeight:700 }}>{val}{unit}</span>
                    </div>
                    <div style={{ height:'4px', background:'rgba(255,255,255,0.06)', borderRadius:'99px', overflow:'hidden' }}>
                      <div style={{
                        height:'100%', borderRadius:'99px',
                        width: `${invert ? (100 - (val/max)*100) : (val/max)*100}%`,
                        background: bc,
                        boxShadow: `0 0 6px ${bc}88`,
                        transition: 'width 0.4s ease'
                      }}/>
                    </div>
                  </div>
                ))}

                {/* Fault alert */}
                {live.isCritical && (
                  <div style={{ marginTop:'6px', fontSize:'0.62rem', color:'#ff4d6d', fontWeight:700,
                    background:'rgba(255,77,109,0.1)', border:'1px solid rgba(255,77,109,0.3)',
                    borderRadius:'6px', padding:'4px 8px' }}>
                    ⚠ {live.activeFault.replace(/_/g,' ')} — Reliability degraded!
                  </div>
                )}
              </div>
            </div>

            {/* P(fail) footer */}
            <div style={{ marginTop:'8px', paddingTop:'6px', borderTop:'1px solid rgba(255,255,255,0.05)',
              fontSize:'0.6rem', color:'#374151', display:'flex', gap:'16px' }}>
              <span>P(fail) = <strong style={{ color:'#94a3b8' }}>{live.pFail}%</strong></span>
              <span>P(success) = <strong style={{ color: col }}>{live.pSuccess}%</strong></span>
              <span>Anomaly = <strong style={{ color:'#94a3b8' }}>{live.anomaly}</strong></span>
            </div>
          </div>
        );
      })()}


      {/* Mission Selector */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"8px", marginBottom:"14px" }}>
        {MISSION_TYPES.map(m => (
          <button key={m.id} onClick={() => onMissionSelect(m)} style={{ background: missionType===m.id ? "rgba(0,180,255,0.2)" : "rgba(255,255,255,0.04)", border:`1px solid ${missionType===m.id ? "#00b4ff" : "rgba(255,255,255,0.1)"}`, borderRadius:"8px", padding:"8px 4px", color: missionType===m.id ? "#00b4ff" : "#64748b", fontSize:"0.72rem", cursor:"pointer", fontWeight:700 }}>
            {m.label}<br/><span style={{ fontWeight:400, color:"#475569" }}>{m.dur}h @ {(m.alt*3.28/1000).toFixed(0)}kft</span>
          </button>
        ))}
      </div>

      {/* Custom inputs */}
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"10px", marginBottom:"14px" }}>
        {[
          { label:"Mission Duration (hours)", val:duration, set:setDuration, min:0.5, max:48, step:0.5 },
          { label:"Mission Altitude (meters)", val:altitude, set:setAltitude, min:500, max:11000, step:100 },
        ].map(({ label, val, set, min, max, step }) => (
          <div key={label}>
            <label style={{ fontSize:"0.72rem", color:"#64748b", display:"block", marginBottom:"4px" }}>{label}</label>
            <input type="number" value={val} min={min} max={max} step={step} onChange={e => set(+e.target.value)} style={{ width:"100%", background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.12)", borderRadius:"8px", padding:"7px 10px", color:"#e2e8f0", fontSize:"0.85rem", boxSizing:"border-box" }} />
          </div>
        ))}
      </div>

      <button onClick={compute} disabled={loading} style={{ width:"100%", background: loading ? "#1e3a5f" : "linear-gradient(135deg,#00b4ff,#7c3aed)", border:"none", borderRadius:"10px", padding:"11px", color:"white", fontWeight:700, fontSize:"0.9rem", cursor: loading ? "not-allowed" : "pointer", marginBottom:"16px" }}>
        {loading ? "Computing MRI..." : "⚡ Compute Mission Reliability"}
      </button>

      {error && <div style={{ background:"rgba(255,77,109,0.12)", border:"1px solid #ff4d6d", borderRadius:"8px", padding:"10px 14px", marginBottom:"14px", color:"#ff4d6d", fontSize:"0.8rem" }}>⚠ {error}</div>}

      {mri && (
        <>
          {/* Decision Banner */}
          <div style={{ background:`${decColor}14`, border:`2px solid ${decColor}80`, borderRadius:"14px", padding:"20px", textAlign:"center", marginBottom:"12px" }}>
            <div style={{ fontSize:"2.2rem", fontWeight:900, color:decColor, letterSpacing:"0.1em" }}>{mri.decision}</div>
            <div style={{ fontSize:"1.4rem", fontWeight:700, color:"#e2e8f0", marginTop:"4px" }}>{mriPct}% MRI</div>
            <div style={{ fontSize:"0.78rem", color:"#94a3b8", marginTop:"6px" }}>{result?.recommendation}</div>
          </div>


          {/* ── COMPUTED Mission Success Probability (from server Weibull) ── */}
          <div style={{ background:"rgba(0,180,255,0.06)", border:"1px solid rgba(0,180,255,0.2)", borderRadius:"10px", padding:"10px 14px", marginBottom:"14px", display:"flex", alignItems:"center", justifyContent:"space-between" }}>
            <div>
              <div style={{ fontSize:"0.68rem", color:"#00b4ff", fontWeight:700, letterSpacing:"0.08em" }}>
                🔍 COMPUTED · SERVER WEIBULL (η={mri.weibull_eta}h β={mri.weibull_beta})
              </div>
              <div style={{ fontSize:"0.62rem", color:"#475569", marginTop:"2px" }}>
                {duration}h sortie @ {(altitude/0.3048/1000).toFixed(1)}kft · P(fail)={mri.p_fail_mission?.toFixed(3)}%
              </div>
            </div>
            <div style={{ textAlign:"right" }}>
              <div style={{ fontSize:"1.8rem", fontWeight:900, lineHeight:1, color: mriPct >= 80 ? "#00ff9d" : mriPct >= 60 ? "#fbbf24" : "#ff4d6d" }}>
                {(100 - (mri.p_fail_mission || 0)).toFixed(1)}%
              </div>
              <div style={{ fontSize:"0.6rem", color:"#475569" }}>P(success)</div>
            </div>
          </div>

          {/* MRI Progress Arc */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"8px", marginBottom:"14px" }}>
            {[
              { label:"Health Index", val:(mri.sub_health_index*100)?.toFixed(1)+"%", w:"35%", c:"#00ff9d" },
              { label:"Fail Prob SI", val:(mri.sub_fail_prob_si*100)?.toFixed(1)+"%", w:"30%", c:"#00b4ff" },
              { label:"RUL Ratio", val:(mri.sub_rul_ratio*100)?.toFixed(1)+"%", w:"25%", c:"#a78bfa" },
              { label:"Oil Margin", val:(mri.sub_oil_margin*100)?.toFixed(1)+"%", w:"10%", c:"#fbbf24" },
            ].map(({ label, val, w, c }) => (
              <div key={label} style={{ background:"rgba(255,255,255,0.04)", borderRadius:"10px", padding:"10px 8px", textAlign:"center", border:`1px solid ${c}30` }}>
                <div style={{ fontSize:"0.95rem", fontWeight:700, color:c }}>{val}</div>
                <div style={{ fontSize:"0.62rem", color:"#64748b", marginTop:"2px" }}>{label}</div>
                <div style={{ fontSize:"0.6rem", color:"#475569" }}>AHP {w}</div>
              </div>
            ))}
          </div>

          {/* ISA Conditions */}
          <div style={{ background:"rgba(0,180,255,0.06)", border:"1px solid rgba(0,180,255,0.15)", borderRadius:"10px", padding:"12px", marginBottom:"12px" }}>
            <div style={{ fontSize:"0.75rem", color:"#00b4ff", fontWeight:700, marginBottom:"8px" }}>🌡 ISA CONDITIONS @ {result?.mission_altitude_ft?.toFixed(0)} ft</div>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"6px", fontSize:"0.75rem" }}>
              <div><span style={{ color:"#64748b" }}>Temp: </span><span style={{ color:"#e2e8f0" }}>{result?.isa_conditions?.temperature_c?.toFixed(1)}°C</span></div>
              <div><span style={{ color:"#64748b" }}>Power: </span><span style={{ color:"#fbbf24" }}>{result?.isa_conditions?.power_fraction?.toFixed(1)}%</span></div>
              <div><span style={{ color:"#64748b" }}>BSFC: </span><span style={{ color:"#e2e8f0" }}>{result?.isa_conditions?.bsfc_alt_lbhrhp?.toFixed(3)}</span></div>
            </div>
          </div>

          <div style={{ fontSize:"0.72rem", color:"#475569", textAlign:"center" }}>
            Weibull β={mri.weibull_beta} η={mri.weibull_eta}h | P(fail)={mri.p_fail_mission?.toFixed(3)}% | GO≥{mri.go_threshold*100}% | CAUTION≥{mri.caution_threshold*100}%
          </div>
        </>
      )}
    </div>
  );
}
