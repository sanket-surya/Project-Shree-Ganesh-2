import React, { useState } from "react";
const API = "http://localhost:8000";

const MISSION_TYPES = [
  { id:"ISR_PATROL", label:"ISR Patrol", dur:8, alt:4572 },
  { id:"BORDER_WATCH", label:"Border Watch", dur:12, alt:3048 },
  { id:"RECON", label:"Recon Strike", dur:4, alt:6096 },
  { id:"RELAY", label:"Comms Relay", dur:24, alt:9144 },
];

export default function PreFlightMRI() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [missionType, setMissionType] = useState("ISR_PATROL");
  const [duration, setDuration] = useState(8);
  const [altitude, setAltitude] = useState(4572);

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
      <p style={{ margin:"0 0 18px", fontSize:"0.75rem", color:"#94a3b8" }}>Mission Reliability Index — Weibull + AHP engine clearance</p>

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
          <div style={{ background:`${decColor}14`, border:`2px solid ${decColor}80`, borderRadius:"14px", padding:"20px", textAlign:"center", marginBottom:"16px" }}>
            <div style={{ fontSize:"2.2rem", fontWeight:900, color:decColor, letterSpacing:"0.1em" }}>{mri.decision}</div>
            <div style={{ fontSize:"1.4rem", fontWeight:700, color:"#e2e8f0", marginTop:"4px" }}>{mriPct}% MRI</div>
            <div style={{ fontSize:"0.78rem", color:"#94a3b8", marginTop:"6px" }}>{result?.recommendation}</div>
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
