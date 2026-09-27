import React, { useState, useEffect, useRef } from 'react';
import { Plane, Layers, Activity, Wrench, Rocket, ShieldCheck, Film } from 'lucide-react';
import FleetHealthOverview from './components/FleetHealthOverview';
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
import PreFlightMRI from './components/PreFlightMRI';
import MissionReplayPanel from './components/MissionReplayPanel';
import AirworthinessReport from './components/AirworthinessReport';

import MaintenanceScheduler from './components/MaintenanceScheduler';
import CascadeTimelinePanel from './components/CascadeTimelinePanel';

const TABS = [
  { id: 'twin',        label: 'LIVE ENGINE',           icon: <Layers size={14} />,      desc: 'Real-time 3D engine digital twin & telemetry' },
  { id: 'trends',      label: 'WEAR ANALYSIS',         icon: <Activity size={14} />,    desc: 'AI-predicted degradation & aging trends' },
  { id: 'preflight',   label: 'FLIGHT READINESS',      icon: <ShieldCheck size={14} />, desc: 'Go / No-Go pre-flight safety check' },
  { id: 'fleet',       label: 'FLEET STATUS',          icon: <Plane size={14} />,       desc: 'Multi-UAV fleet health overview' },
  { id: 'replay',      label: 'BLACK BOX REPLAY',      icon: <Film size={14} />,        desc: 'Replay past mission data frame-by-frame' },
  { id: 'maintenance', label: 'MAINTENANCE LOG',        icon: <Wrench size={14} />,      desc: 'Scheduled maintenance & overhaul tracking' },
  { id: 'cascade',     label: 'FAILURE SIMULATION',    icon: <Rocket size={14} />,      desc: 'Cascading fault injection demo for analysis' },
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

  // Health status helper
  const healthIndex = ai.health_index !== undefined ? ai.health_index : 0.98;
  const healthPct = Math.round(healthIndex * 100);
  const healthLabel = healthPct >= 85 ? 'ALL SYSTEMS NOMINAL' : healthPct >= 60 ? 'CAUTION — DEGRADED' : 'CRITICAL — FAULT ACTIVE';
  const healthPillClass = healthPct >= 85 ? 'health-pill-good' : healthPct >= 60 ? 'health-pill-warn' : 'health-pill-crit';

  return (
    <div className="min-h-screen tactical-grid-bg flex flex-col font-sans" style={{ color: 'var(--text-primary)', background: 'var(--bg-primary)' }}>

      {/* ── HEADER ──────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3"
        style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-card)' }}>

        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #0A2040, #0D3060)', border: '1px solid rgba(0,212,255,0.3)' }}>
            <Plane size={18} style={{ color: '#00D4FF' }} className="transform -rotate-45" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-wider" style={{ color: '#E8F4FD' }}>
                AeroTwin — UAV Engine Digital Twin
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded font-semibold"
                style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)', color: '#00D4FF' }}>
                SIH 2026
              </span>
            </div>
            <div className="text-[11px] font-mono mt-0.5 flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
              <span>Engine: <span style={{ color: '#E8F4FD', fontWeight: 600 }}>{state.engine_name || 'ROTAX 914F'}</span></span>
              <span style={{ color: 'var(--border-hover)' }}>|</span>
              <span>Airframe: <span style={{ color: '#00D4FF', fontWeight: 600 }}>TAPAS-BH-201</span></span>
              {selectedComponent && (
                <span className="text-[10px] px-1.5 py-0.5 rounded"
                  style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.4)', color: '#00D4FF' }}>
                  🔍 {selectedComponent}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Center: Live Flight Strip */}
        <div className="hidden lg:flex items-center gap-3 text-xs font-mono px-3.5 py-1.5 rounded-lg"
          style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
          <div><span style={{ color: 'var(--text-secondary)' }}>Mission:</span> <strong style={{ color: '#00D4FF' }}>{flight.mission_name || 'ISR Loiter'}</strong></div>
          <div style={{ width: 1, height: 12, background: 'var(--border-card)' }} />
          <div><span style={{ color: 'var(--text-secondary)' }}>Alt:</span> <strong style={{ color: '#E8F4FD' }}>{flight.altitude_m ? `${Math.round(flight.altitude_m)} m` : '1500 m'}</strong></div>
          <div style={{ width: 1, height: 12, background: 'var(--border-card)' }} />
          <div><span style={{ color: 'var(--text-secondary)' }}>Speed:</span> <strong style={{ color: '#E8F4FD' }}>{flight.airspeed_kts || 95} kts</strong></div>
          <div style={{ width: 1, height: 12, background: 'var(--border-card)' }} />
          <div><span style={{ color: 'var(--text-secondary)' }}>Throttle:</span> <strong style={{ color: '#FFB800' }}>{flight.throttle_pct || 75}%</strong></div>
          <div style={{ width: 1, height: 12, background: 'var(--border-card)' }} />
          <div><span style={{ color: 'var(--text-secondary)' }}>Efficiency:</span> <strong style={{ color: '#00FFA3' }}>{state.combustion_efficiency_pct?.toFixed(1) ?? '92.5'}%</strong></div>
        </div>

        {/* Right: Status */}
        <div className="flex items-center gap-3">
          {faultActive && (
            <span className="text-[10.5px] font-mono font-bold px-2 py-1 rounded-md"
              style={isCritical
                ? { background: 'rgba(255,59,59,0.15)', border: '1px solid rgba(255,59,59,0.5)', color: '#FF3B3B' }
                : { background: 'rgba(255,184,0,0.12)', border: '1px solid rgba(255,184,0,0.4)', color: '#FFB800' }}>
              ⚠ FAULT: {state.active_fault?.replaceAll('_', ' ')}
            </span>
          )}
          <div className="flex items-center gap-2">
            {wsConnected ? <span className="live-dot" /> : <span className="warn-dot" />}
            <span className="text-xs font-mono" style={{ color: wsConnected ? '#00FFA3' : '#FFB800' }}>
              {wsConnected ? 'LIVE TELEMETRY' : 'CONNECTING...'}
            </span>
          </div>
          <button onClick={() => setIsReportOpen(true)} className="tactical-btn active text-xs">
            📋 AIRWORTHINESS REPORT
          </button>
        </div>
      </header>

      {/* ── HEALTH STATUS BANNER (Phase 1) ──────────────────────────────────── */}
      <div className="px-4 py-2 flex flex-wrap items-center gap-3"
        style={{ background: 'var(--bg-card)', borderBottom: '1px solid var(--border-subtle)' }}>
        {/* Big Health Pill */}
        <div className={`${healthPillClass} flex items-center gap-2 text-sm font-bold`}>
          <span>{healthPct >= 85 ? '✅' : healthPct >= 60 ? '⚠️' : '🚨'}</span>
          <span>ENGINE HEALTH: {healthPct}% — {healthLabel}</span>
        </div>

        {/* Quick stat chips */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1.5 rounded"
            style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Remaining Life (RUL):</span>
            <strong style={{ color: ai.predicted_rul_hours < 200 ? '#FF3B3B' : '#00FFA3' }}>
              {(ai.predicted_rul_hours ?? 875).toFixed(0)} hrs
            </strong>
          </div>
          <div className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1.5 rounded"
            style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Fault Detected:</span>
            <strong style={{ color: ai.primary_fault === 'Nominal' ? '#00FFA3' : '#FF3B3B' }}>
              {ai.primary_fault === 'Nominal' ? 'NONE' : (ai.primary_fault || 'NONE').replaceAll('_', ' ')}
            </strong>
          </div>
          <div className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1.5 rounded"
            style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>AI Confidence:</span>
            <strong style={{ color: '#A78BFA' }}>{((ai.fault_confidence ?? 0.96) * 100).toFixed(0)}%</strong>
          </div>
          <div className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1.5 rounded"
            style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-card)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Flight Hours:</span>
            <strong style={{ color: '#00D4FF' }}>{state.accumulated_hours ?? 124.5} hrs</strong>
          </div>
        </div>
      </div>

      {/* ── TAB NAVIGATION ──────────────────────────────────────────────────── */}
      <nav className="px-4 flex items-center gap-0.5 overflow-x-auto"
        style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-card)' }}>
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            title={tab.desc}
            className="flex items-center gap-2 px-3.5 py-2.5 text-xs font-semibold tracking-wide whitespace-nowrap transition-colors duration-150"
            style={activeTab === tab.id
              ? { borderBottom: '2px solid #00D4FF', color: '#00D4FF', background: 'rgba(0,212,255,0.06)', marginBottom: '-1px' }
              : { borderBottom: '2px solid transparent', color: 'var(--text-secondary)', marginBottom: '-1px' }}
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

        {/* ─ TAB: PRE-FLIGHT GO/NO-GO ──────────────────────────────────────── */}
        {activeTab === 'preflight' && (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-3">
            <div className="xl:col-span-7 flex flex-col gap-3">
              <PreFlightMRI telemetry={currentTelem} />
              <AirworthinessReport telemetry={currentTelem} />
            </div>
            <div className="xl:col-span-5 flex flex-col gap-3">
              <div className="h-[380px] min-h-[340px]">
                <ThreeEngineTwin telemetry={currentTelem} onSelectComponent={setSelectedComponent} />
              </div>
              <TelemetryGauges telemetry={currentTelem} />
              <RULDegradationGauge telemetry={currentTelem} />
            </div>
          </div>
        )}

        {/* ─ TAB: MISSION REPLAY ───────────────────────────────────────────── */}
        {activeTab === 'replay' && (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-3">
            <div className="xl:col-span-8 flex flex-col gap-3">
              <MissionReplayPanel />
              <DegradationTrendChart telemetry={currentTelem} historyBuffer={historyBuffer} />
            </div>
            <div className="xl:col-span-4 flex flex-col gap-3">
              <AIPredictivePanel telemetry={currentTelem} />
              <ContingencyAdvisory telemetry={currentTelem} />
              <CanBusTerminal telemetry={currentTelem} />
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

        {/* ─ TAB: FLEET HEALTH ─────────────────────────────────────────────────── */}
        {activeTab === 'fleet' && (
          <FleetHealthOverview telemetry={currentTelem} />
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
      <footer className="sticky bottom-0 z-30 p-2" style={{ background: 'rgba(7,11,20,0.97)', borderTop: '1px solid var(--border-card)' }}>
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
