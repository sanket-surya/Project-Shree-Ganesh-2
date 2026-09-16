import React, { useState, useEffect, useRef } from 'react';
import { Plane, Layers, Activity, Wrench, Rocket } from 'lucide-react';
import ThreeEngineTwin from './components/ThreeEngineTwin';
import TelemetryGauges from './components/TelemetryGauges';
import CylinderThermalMatrix from './components/CylinderThermalMatrix';
import VibrationWaterfall from './components/VibrationWaterfall';
import AIPredictivePanel from './components/AIPredictivePanel';
import RULDegradationGauge from './components/RULDegradationGauge';
import MissionStudio from './components/MissionStudio';
import ContingencyAdvisory from './components/ContingencyAdvisory';
import CanBusTerminal from './components/CanBusTerminal';
import MissionReplayBar from './components/MissionReplayBar';
import ReportModal from './components/ReportModal';
import DegradationTrendChart from './components/DegradationTrendChart';

import MaintenanceScheduler from './components/MaintenanceScheduler';
import CascadeTimelinePanel from './components/CascadeTimelinePanel';

const TABS = [
  { id: 'twin',        label: 'DIGITAL TWIN',        icon: <Layers size={14} /> },
  { id: 'trends',      label: 'DEGRADATION TRENDS',   icon: <Activity size={14} /> },
  { id: 'maintenance', label: 'MAINTENANCE',           icon: <Wrench size={14} /> },
  { id: 'cascade',     label: 'CASCADE FAILURE DEMO', icon: <Rocket size={14} className="text-orange-400" /> },
];

const FALLBACK_TELEM = {
  state: {
    rpm: 5000, manifold_pressure_hpa: 1150, power_output_kw: 65, torque_nm: 124,
    fuel_flow_lph: 18.5, fuel_pressure_bar: 3.0,
    cht_c: [110, 111.5, 113, 112], egt_c: [810, 815, 808, 812],
    oil_temperature_c: 92, oil_pressure_bar: 3.85, coolant_temperature_c: 88,
    turbo_rpm: 112000, bus_voltage_v: 28.1, overall_vibration_g: 1.45,
    fft_spectrum: [0.4, 0.9, 0.25, 0.55, 0.12, 0.08, 0.05, 0.03],
    active_fault: 'NONE',
    ignition_timing_btdc: 26.0, injection_timing_btdc: 8.5,
    injection_pulse_width_ms: 4.2, lambda_afr: 1.02,
    combustion_efficiency_pct: 92.5, accumulated_hours: 124.5,
  },
  flight: {
    mission_name: 'Nominal ISR Loiter', altitude_m: 1500,
    ambient_temp_c: 15.0, airspeed_kts: 95, throttle_pct: 75,
  },
  ai: {
    is_anomaly: false, anomaly_score: 0.08, primary_fault: 'Nominal',
    fault_confidence: 0.96,
    fault_probabilities: { Nominal: 0.96, Cylinder_Misfire: 0.02, Turbo_Degradation: 0.01, Coolant_Loss: 0.01 },
    predicted_rul_hours: 875.0, health_index: 0.98,
    xai_attributions: [],
    contingency_advisory: {
      status: 'NORMAL_OPERATION', severity_level: 'INFO',
      recommendation: 'All engine thermal and mechanical parameters nominal. Cleared for continued ISR loiter.',
      power_derate_pct: 0, glide_range_nm: 12.8,
      checklist: ['Standard cruise scan', 'Log engine telemetry at waypoint'],
    },
  },
  can_frame: 'CAN0 18FEE000# 40 9C 46 2D 25 41 5E 00',
};

export default function App() {
  const [telemetry, setTelemetry]               = useState(null);
  const [wsConnected, setWsConnected]           = useState(false);
  const [activeTab, setActiveTab]               = useState('twin');
  const [isReportOpen, setIsReportOpen]         = useState(false);
  const [isReplaying, setIsReplaying]           = useState(false);
  const [replayPercent, setReplayPercent]       = useState(100);
  const [replaySpeed, setReplaySpeed]           = useState(1);
  const [selectedComponent, setSelectedComponent] = useState(null);
  // Rolling 120-frame history buffer for Degradation Trend Chart & Black Box Replay
  const [historyBuffer, setHistoryBuffer]       = useState([]);
  const wsRef = useRef(null);

  // ── WebSocket connection to FastAPI telemetry hub ─────────────────────────
  useEffect(() => {
    let ws;
    let reconnectTimer;

    const connectWs = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws/telemetry');
        wsRef.current = ws;

        ws.onopen  = () => { setWsConnected(true); };
        ws.onclose = () => { setWsConnected(false); reconnectTimer = setTimeout(connectWs, 2000); };
        ws.onerror = ()  => { setWsConnected(false); };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setTelemetry(data);
            // Append to rolling history buffer (max 120 frames = 6 seconds of 20Hz blackbox)
            setHistoryBuffer(prev => {
              const next = [...prev, data];
              return next.length > 120 ? next.slice(next.length - 120) : next;
            });
          } catch { /* ignore parse errors */ }
        };
      } catch {
        setWsConnected(false);
        reconnectTimer = setTimeout(connectWs, 2000);
      }
    };

    connectWs();
    return () => {
      if (ws) ws.close();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  }, []);

  // Automated Replay player timer
  useEffect(() => {
    if (!isReplaying) return;
    const intervalMs = 150 / replaySpeed;
    const timer = setInterval(() => {
      setReplayPercent(prev => {
        if (prev >= 100) {
          setIsReplaying(false);
          return 100;
        }
        return Math.min(100, prev + 2);
      });
    }, intervalMs);
    return () => clearInterval(timer);
  }, [isReplaying, replaySpeed]);

  // ── API helpers ───────────────────────────────────────────────────────────
  const post = (url, body) =>
    fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .catch(console.error);

  const handleToggleFault      = (t, s) => post('http://localhost:8000/api/fault/toggle',       { fault_type: t, severity: s });
  const handleCompoundScenario = (s, v) => post('http://localhost:8000/api/fault/compound',      { scenario: s, severity: v });
  const handleClearFault       = ()      => post('http://localhost:8000/api/fault/clear',        {});
  const handleSetMissionProfile= (p)     => post('http://localhost:8000/api/mission/set-profile',{ profile_name: p });

  // Replay frame selection (Scrub into past blackbox frames)
  const isHistorical = replayPercent < 100 && historyBuffer.length > 0;
  const historyIndex = Math.min(
    historyBuffer.length - 1,
    Math.max(0, Math.floor((replayPercent / 100) * (historyBuffer.length - 1)))
  );
  const currentTelem = isHistorical ? historyBuffer[historyIndex] : (telemetry || FALLBACK_TELEM);
  const flight       = currentTelem.flight || {};
  const ai           = currentTelem.ai || {};
  const state        = currentTelem.state || {};

  // Determine header fault alert color
  const faultActive = state.active_fault && state.active_fault !== 'NONE';
  const isCritical  = ai.is_anomaly && ai.anomaly_score > 0.7;

  return (
    <div className="min-h-screen bg-[#0c0f17] text-slate-100 tactical-grid-bg flex flex-col font-sans selection:bg-sky-500 selection:text-black">

      {/* ── MATURE DEFENSE GCS HEADER ───────────────────────────────────────── */}
      <header className="border-b border-[#1e2436] bg-[#121622] px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 sticky top-0 z-40">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#182030] border border-[#2b354e] flex items-center justify-center text-sky-400">
            <Plane size={18} className="transform -rotate-45" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-wider text-white font-['Inter',sans-serif]">
                MALE UAV PROPULSION DIGITAL TWIN
              </h1>
              <span className="text-[10px] font-mono bg-[#182133] border border-[#2b3954] text-sky-300 px-1.5 py-0.2 rounded">
                SIH 2026
              </span>
              <span className="text-[10px] font-mono bg-[#142328] border border-[#1e3c3b] text-teal-300 px-1.5 py-0.2 rounded hidden sm:inline">
                DO-178C DAL-B
              </span>
            </div>
            <div className="text-[11px] font-mono text-slate-400 flex items-center gap-2 mt-0.5">
              <span>PLATFORM: <span className="text-slate-200 font-semibold">{state.engine_name || 'ROTAX 914F'} ({state.engine_power_hp || 115} HP)</span> | AIRFRAME: <span className="text-sky-300 font-semibold">TAPAS-BH-201 / HERON</span></span>
              {selectedComponent && (
                <span className="text-[10px] bg-[#1b253b] border border-sky-500/60 text-sky-300 px-1.5 py-0.2 rounded">
                  INSPECTING: {selectedComponent}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Center: Flight Envelope Strip */}
        <div className="hidden lg:flex items-center gap-3.5 text-xs font-mono bg-[#0e121c] px-3.5 py-1.5 rounded border border-[#1e2436]">
          <div><span className="text-slate-400">PROFILE:</span> <strong className="text-sky-300">{flight.mission_name || 'Nominal ISR'}</strong></div>
          <div className="h-3 w-px bg-slate-700" />
          <div><span className="text-slate-400">ALT:</span> <strong className="text-white">{flight.altitude_m ? `${flight.altitude_m.toFixed(0)}m` : '1500m'}</strong></div>
          <div className="h-3 w-px bg-slate-700" />
          <div><span className="text-slate-400">TAS:</span> <strong className="text-white">{flight.airspeed_kts || 95} kts</strong></div>
          <div className="h-3 w-px bg-slate-700" />
          <div><span className="text-slate-400">AMB:</span> <strong className="text-white">{flight.ambient_temp_c?.toFixed(1) ?? 15}°C</strong></div>
          <div className="h-3 w-px bg-slate-700" />
          <div><span className="text-slate-400">THR:</span> <strong className="text-amber-400">{flight.throttle_pct || 75}%</strong></div>
          <div className="h-3 w-px bg-slate-700" />
          <div><span className="text-slate-400">EFF:</span> <strong className="text-emerald-400">{state.combustion_efficiency_pct?.toFixed(1) ?? '92.5'}%</strong></div>
        </div>

        {/* Right: Status + Actions */}
        <div className="flex items-center gap-3">
          {faultActive && (
            <span className={`text-[10.5px] font-mono font-bold px-2 py-0.5 rounded border ${isCritical ? 'bg-red-950/80 border-red-500 text-red-300' : 'bg-amber-950/80 border-amber-500/60 text-amber-300'}`}>
              ⚠ {state.active_fault?.replaceAll('_', ' ')}
            </span>
          )}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400' : 'bg-amber-400 animate-ping'}`} />
            <span className={wsConnected ? 'text-emerald-400' : 'text-amber-400'}>
              {wsConnected ? 'FADEC CAN-BUS: LIVE' : 'CONNECTING...'}
            </span>
          </div>
          <button onClick={() => setIsReportOpen(true)} className="tactical-btn active text-xs font-mono">
            AIRWORTHINESS REPORT
          </button>
        </div>
      </header>

      {/* ── CALM DEFENSE TAB NAV ────────────────────────────────────────────── */}
      <nav className="bg-[#0f131d] border-b border-[#1c2232] px-4 flex items-center gap-1 overflow-x-auto">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-semibold tracking-wide border-b-2 transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-sky-400 text-sky-300 bg-[#161c2b]/80'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-[#131724]'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </nav>

      {/* ── MAIN CONTENT ───────────────────────────────────────────────────── */}
      <main className="flex-1 p-3 md:p-4 max-w-[1920px] mx-auto w-full">

        {/* ─ TAB: DIGITAL TWIN ─────────────────────────────────────────────── */}
        {activeTab === 'twin' && (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-3">
            {/* Left: 3D Twin + Mission Studio + CAN */}
            <div className="xl:col-span-7 flex flex-col gap-3">
              <div className="flex-1 min-h-[460px]">
                <ThreeEngineTwin telemetry={currentTelem} onSelectComponent={setSelectedComponent} />
              </div>
              <MissionStudio
                telemetry={currentTelem}
                onToggleFault={handleToggleFault}
                onCompoundScenario={handleCompoundScenario}
                onClearFault={handleClearFault}
                onSetMissionProfile={handleSetMissionProfile}
              />
              <CanBusTerminal telemetry={currentTelem} />
            </div>

            {/* Right: Avionics + AI + RUL + Advisory */}
            <div className="xl:col-span-5 flex flex-col gap-3">
              <TelemetryGauges telemetry={currentTelem} />
              <CylinderThermalMatrix telemetry={currentTelem} />
              <VibrationWaterfall telemetry={currentTelem} />
              <AIPredictivePanel telemetry={currentTelem} />
              <RULDegradationGauge telemetry={currentTelem} />
              <ContingencyAdvisory telemetry={currentTelem} />
            </div>
          </div>
        )}



        {/* ─ TAB: DEGRADATION TRENDS ───────────────────────────────────────── */}
        {activeTab === 'trends' && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
            <DegradationTrendChart telemetry={currentTelem} historyBuffer={historyBuffer} />
            {/* Right: AI Panel + RUL side by side for context */}
            <div className="flex flex-col gap-3">
              <AIPredictivePanel telemetry={currentTelem} />
              <RULDegradationGauge telemetry={currentTelem} />
              <VibrationWaterfall telemetry={currentTelem} />
            </div>
          </div>
        )}

        {/* ─ TAB: MAINTENANCE ──────────────────────────────────────────────── */}
        {activeTab === 'maintenance' && (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-3">
            <div className="xl:col-span-8 flex flex-col gap-3">
              <MaintenanceScheduler telemetry={currentTelem} />
            </div>
            <div className="xl:col-span-4 flex flex-col gap-3">
              <RULDegradationGauge telemetry={currentTelem} />
              <AIPredictivePanel telemetry={currentTelem} />
              <ContingencyAdvisory telemetry={currentTelem} />
              <CanBusTerminal telemetry={currentTelem} />
            </div>
          </div>
        )}

        {/* ─ TAB: CASCADE FAILURE DEMO ─────────────────────────────────────────── */}
        {activeTab === 'cascade' && (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-3">
            {/* Left: Mission Mangal Scenario Timeline & Judge Controls */}
            <div className="xl:col-span-7 flex flex-col gap-3">
              <CascadeTimelinePanel telemetry={currentTelem} />
            </div>

            {/* Right: Live 3D Twin (Thermal Reactions & Seizure Freeze) + Telemetry & AI */}
            <div className="xl:col-span-5 flex flex-col gap-3">
              <div className="h-[380px] min-h-[340px]">
                <ThreeEngineTwin telemetry={currentTelem} onSelectComponent={setSelectedComponent} />
              </div>
              <TelemetryGauges telemetry={currentTelem} />
              <CylinderThermalMatrix telemetry={currentTelem} />
              <AIPredictivePanel telemetry={currentTelem} />
            </div>
          </div>
        )}
      </main>

      {/* ── FOOTER REPLAY BAR ──────────────────────────────────────────────── */}
      <footer className="sticky bottom-0 z-30 p-2 bg-slate-950/95 border-t border-slate-800">
        <MissionReplayBar
          isReplaying={isReplaying}
          onToggleReplay={() => {
            if (replayPercent >= 100) setReplayPercent(0);
            setIsReplaying(!isReplaying);
          }}
          replayPercent={replayPercent}
          onScrubReplay={(pct) => {
            setReplayPercent(pct);
            if (pct === 100) setIsReplaying(false);
          }}
          historyCount={historyBuffer.length}
          speed={replaySpeed}
          onChangeSpeed={setReplaySpeed}
          onExportReport={() => setIsReportOpen(true)}
        />
      </footer>

      {/* ── REPORT MODAL ───────────────────────────────────────────────────── */}
      <ReportModal isOpen={isReportOpen} onClose={() => setIsReportOpen(false)} telemetry={currentTelem} />
    </div>
  );
}
