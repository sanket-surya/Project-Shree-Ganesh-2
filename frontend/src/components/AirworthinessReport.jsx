import React, { useState } from "react";
const API = "http://localhost:8000";

const HealthBar = ({ pct, label, status }) => {
  const c = pct >= 80 ? "#00ff9d" : pct >= 60 ? "#fbbf24" : "#ff4d6d";
  return (
    <div style={{ marginBottom:"10px" }}>
      <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"3px" }}>
        <span style={{ fontSize:"0.78rem", color:"#94a3b8" }}>{label}</span>
        <span style={{ fontSize:"0.78rem", fontWeight:700, color:c }}>{pct?.toFixed(1)}% <span style={{ color:"#64748b", fontWeight:400 }}>{status}</span></span>
      </div>
      <div style={{ background:"rgba(255,255,255,0.08)", borderRadius:"4px", height:"6px" }}>
        <div style={{ width:`${Math.min(100,pct||0)}%`, background:c, borderRadius:"4px", height:"6px", transition:"width 0.4s" }} />
      </div>
    </div>
  );
};

export default function AirworthinessReport() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReport = async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch(API + "/api/airworthiness-report");
      if (!r.ok) throw new Error("Server " + r.status);
      setData(await r.json());
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const statusBg = data ? (data.is_airworthy ? "rgba(0,255,157,0.08)" : "rgba(255,77,109,0.08)") : "transparent";
  const statusBorder = data ? (data.is_airworthy ? "rgba(0,255,157,0.3)" : "rgba(255,77,109,0.3)") : "transparent";
  const statusTxt = data ? (data.is_airworthy ? "#00ff9d" : "#ff4d6d") : "#94a3b8";

  return (
    <div style={{ background:"linear-gradient(135deg,rgba(10,20,40,0.97),rgba(0,20,40,0.97))", border:"1px solid rgba(0,255,157,0.2)", borderRadius:"16px", padding:"22px", color:"#e2e8f0", fontFamily:"Inter,sans-serif" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:"18px" }}>
        <div>
          <h2 style={{ margin:0, color:"#00ff9d", fontSize:"1.1rem" }}>📋 AIRWORTHINESS REPORT</h2>
          <p style={{ margin:"4px 0 0", fontSize:"0.75rem", color:"#94a3b8" }}>AeroTwin virtual airworthiness assessment</p>
        </div>
        <button onClick={fetchReport} disabled={loading} style={{ background: loading ? "#1e3a5f" : "linear-gradient(135deg,#00ff9d,#00b4ff)", border:"none", borderRadius:"8px", padding:"8px 18px", color: loading ? "#64748b" : "#001a33", fontWeight:700, cursor: loading ? "not-allowed" : "pointer", fontSize:"0.82rem" }}>
          {loading ? "Generating..." : "Generate Report"}
        </button>
      </div>

      {error && <div style={{ background:"rgba(255,77,109,0.12)", border:"1px solid #ff4d6d", borderRadius:"8px", padding:"10px 14px", marginBottom:"14px", color:"#ff4d6d", fontSize:"0.8rem" }}>⚠ {error}</div>}

      {data && (
        <>
          {/* Status Banner */}
          <div style={{ background:statusBg, border:`1px solid ${statusBorder}`, borderRadius:"12px", padding:"14px 18px", marginBottom:"16px", textAlign:"center" }}>
            <div style={{ fontSize:"1.4rem", fontWeight:900, color:statusTxt, letterSpacing:"0.08em" }}>{data.airworthiness_status}</div>
            <div style={{ fontSize:"0.75rem", color:"#64748b", marginTop:"2px" }}>{data.engine_name} | Report: {data.report_timestamp?.substring(0,10)}</div>
          </div>

          {/* TBO Status */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"8px", marginBottom:"16px" }}>
            {[
              { label:"Hours Flown", val:data.hours_accumulated?.toFixed(1), unit:"hrs", icon:"🕐" },
              { label:"TBO Remaining", val:data.tbo_remaining_hrs?.toFixed(0), unit:"hrs", icon:"⏳" },
              { label:"TBO Extension", val:data.tbo_extension_hrs?.toFixed(0), unit:"hrs", icon:"✨" },
            ].map(({ label, val, unit, icon }) => (
              <div key={label} style={{ background:"rgba(255,255,255,0.04)", borderRadius:"10px", padding:"10px 12px", textAlign:"center", border:"1px solid rgba(255,255,255,0.07)" }}>
                <div style={{ fontSize:"1.1rem" }}>{icon}</div>
                <div style={{ fontWeight:700, color:"#00b4ff", fontSize:"1rem" }}>{val}</div>
                <div style={{ fontSize:"0.65rem", color:"#64748b" }}>{unit} | {label}</div>
              </div>
            ))}
          </div>

          {/* Per-Cylinder Health */}
          <div style={{ marginBottom:"16px" }}>
            <h3 style={{ margin:"0 0 10px", fontSize:"0.82rem", color:"#64748b", textTransform:"uppercase", letterSpacing:"0.08em" }}>Cylinder Health</h3>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"8px" }}>
              {data.cylinders?.map(cyl => {
                const c = cyl.health_pct >= 80 ? "#00ff9d" : cyl.health_pct >= 60 ? "#fbbf24" : "#ff4d6d";
                return (
                  <div key={cyl.cylinder} style={{ background:"rgba(255,255,255,0.04)", borderRadius:"10px", padding:"10px 8px", textAlign:"center", border:`1px solid ${c}40` }}>
                    <div style={{ fontSize:"0.7rem", color:"#64748b" }}>CYL {cyl.cylinder}</div>
                    <div style={{ fontWeight:700, color:c, fontSize:"0.95rem" }}>{cyl.health_pct?.toFixed(0)}%</div>
                    <div style={{ fontSize:"0.62rem", color:"#94a3b8" }}>{cyl.cht_c?.toFixed(0)}°C CHT</div>
                    <div style={{ fontSize:"0.62rem", color:"#94a3b8" }}>{cyl.egt_c?.toFixed(0)}°C EGT</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Component Health Bars */}
          <div style={{ marginBottom:"14px" }}>
            <h3 style={{ margin:"0 0 10px", fontSize:"0.82rem", color:"#64748b", textTransform:"uppercase", letterSpacing:"0.08em" }}>System Components</h3>
            <HealthBar pct={data.components?.turbocharger?.health_pct} label="Turbocharger" status={data.components?.turbocharger?.status} />
            <HealthBar pct={data.components?.oil_system?.health_pct} label="Oil System" status={data.components?.oil_system?.status} />
            <HealthBar pct={data.components?.mechanical?.health_pct} label="Mechanical" status={data.components?.mechanical?.status} />
            <HealthBar pct={data.overall_health_pct} label="Overall Engine" status="" />
          </div>

          {/* Footer */}
          <div style={{ display:"flex", justifyContent:"space-between", fontSize:"0.72rem", color:"#475569", borderTop:"1px solid rgba(255,255,255,0.07)", paddingTop:"10px" }}>
            <span>Next Inspection: {data.next_inspection_hrs?.toFixed(0)} hrs</span>
            <span>Cert: {data.certification_ref}</span>
            <span>Condition-Based RUL: {data.condition_based_rul_hrs?.toFixed(0)} hrs</span>
          </div>
        </>
      )}
      {!data && !loading && <div style={{ textAlign:"center", padding:"30px", color:"#64748b" }}>Click Generate Report to assess airworthiness status.</div>}
    </div>
  );
}
