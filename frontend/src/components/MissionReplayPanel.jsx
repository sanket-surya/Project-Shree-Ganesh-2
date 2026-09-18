import React, { useState, useCallback } from "react";
const API = "http://localhost:8000";
export default function MissionReplayPanel() {
  const [replayData, setReplayData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sliderIdx, setSliderIdx] = useState(0);
  const [error, setError] = useState(null);

  const fetchReplay = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch(API + "/api/mission-replay?downsample=2");
      if (!r.ok) throw new Error("Server " + r.status);
      const d = await r.json();
      setReplayData(d); setSliderIdx(0);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  const frame = replayData?.replay?.[sliderIdx] ?? null;
  const col = (v, good, warn) => v >= good ? "#00ff9d" : v >= warn ? "#fbbf24" : "#ff4d6d";

  return (
    <div style={{ background:"linear-gradient(135deg,rgba(10,20,40,0.97),rgba(0,30,60,0.97))", border:"1px solid rgba(0,255,157,0.2)", borderRadius:"16px", padding:"22px", color:"#e2e8f0", fontFamily:"Inter,sans-serif" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:"18px" }}>
        <div>
          <h2 style={{ margin:0, color:"#00ff9d", fontSize:"1.1rem" }}>📼 MISSION REPLAY</h2>
          <p style={{ margin:"4px 0 0", fontSize:"0.75rem", color:"#94a3b8" }}>Post-flight black-box telemetry analysis</p>
        </div>
        <button onClick={fetchReplay} disabled={loading} style={{ background: loading ? "#1e3a5f" : "linear-gradient(135deg,#00ff9d,#00b4ff)", border:"none", borderRadius:"8px", padding:"8px 18px", color: loading ? "#64748b" : "#001a33", fontWeight:700, cursor: loading ? "not-allowed" : "pointer", fontSize:"0.82rem" }}>
          {loading ? "Loading..." : "▶ Load Flight Record"}
        </button>
      </div>
      {error && <div style={{ background:"rgba(255,77,109,0.12)", border:"1px solid #ff4d6d", borderRadius:"8px", padding:"10px 14px", marginBottom:"14px", color:"#ff4d6d", fontSize:"0.8rem" }}>⚠ {error}</div>}
      {replayData && replayData.count > 0 && (
        <>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"10px", marginBottom:"16px" }}>
            {[
              { label:"Duration", val:`${replayData.duration_s?.toFixed(0)}s`, icon:"⏱" },
              { label:"Frames", val:replayData.count, icon:"📊" },
              { label:"Min Health", val:`${replayData.summary?.min_health?.toFixed(1)}%`, icon:"❤️" },
              { label:"Faults Seen", val:replayData.summary?.faults_seen?.length||0, icon:"⚡" },
            ].map(({ label, val, icon }) => (
              <div key={label} style={{ background:"rgba(0,255,157,0.06)", borderRadius:"10px", padding:"10px", textAlign:"center", border:"1px solid rgba(0,255,157,0.12)" }}>
                <div>{icon}</div>
                <div style={{ fontWeight:700, color:"#00ff9d" }}>{val}</div>
                <div style={{ fontSize:"0.7rem", color:"#64748b" }}>{label}</div>
              </div>
            ))}
          </div>
          {replayData.summary?.faults_seen?.length > 0 && (
            <div style={{ marginBottom:"12px", padding:"8px 14px", background:"rgba(255,77,109,0.08)", borderRadius:"8px", border:"1px solid rgba(255,77,109,0.2)", fontSize:"0.78rem" }}>
              <span style={{ color:"#fbbf24" }}>⚡ Faults: </span>
              <span style={{ color:"#ff4d6d", fontWeight:700 }}>{replayData.summary.faults_seen.join(" | ")}</span>
            </div>
          )}
          <div style={{ marginBottom:"14px" }}>
            <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"4px" }}>
              <span style={{ fontSize:"0.75rem", color:"#94a3b8" }}>T+{frame?.t?.toFixed(1)}s</span>
              <span style={{ fontSize:"0.75rem", color:"#94a3b8" }}>Frame {sliderIdx+1} / {replayData.count}</span>
            </div>
            <input type="range" min={0} max={replayData.count-1} value={sliderIdx} onChange={e => setSliderIdx(+e.target.value)} style={{ width:"100%", accentColor:"#00ff9d" }} />
          </div>
          {frame && (
            <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"8px" }}>
              {[
                { label:"RPM", val:frame.rpm?.toFixed(0), unit:"rpm", c:col(frame.rpm,4000,2000) },
                { label:"Health", val:frame.health_pct?.toFixed(1), unit:"%", c:col(frame.health_pct,80,60) },
                { label:"CHT Max", val:frame.cht_max?.toFixed(1), unit:"C", c:col(135-frame.cht_max,15,5) },
                { label:"EGT Spread", val:frame.egt_spread?.toFixed(1), unit:"C", c:col(50-frame.egt_spread,30,0) },
                { label:"Oil Press", val:frame.oil_press?.toFixed(2), unit:"bar", c:col(frame.oil_press,3,1.5) },
                { label:"Fault", val:frame.fault==="NONE"?"OK":frame.fault?.substring(0,10), unit:"", c:frame.fault==="NONE"?"#00ff9d":"#ff4d6d" },
              ].map(({ label, val, unit, c }) => (
                <div key={label} style={{ background:"rgba(255,255,255,0.04)", borderRadius:"10px", padding:"10px 12px", border:"1px solid rgba(255,255,255,0.07)" }}>
                  <div style={{ fontSize:"0.7rem", color:"#64748b" }}>{label}</div>
                  <div style={{ fontSize:"0.95rem", fontWeight:700, color:c }}>{val} <span style={{ fontSize:"0.65rem", color:"#94a3b8" }}>{unit}</span></div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
      {replayData?.count === 0 && <div style={{ textAlign:"center", padding:"30px", color:"#64748b" }}>No flight data. Start live stream first.</div>}
    </div>
  );
}
