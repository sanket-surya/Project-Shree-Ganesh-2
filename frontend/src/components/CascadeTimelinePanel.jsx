import React, { useState, useEffect, useRef } from 'react';
import { 
  Rocket, AlertTriangle, ShieldCheck, Play, Pause, Square, 
  ChevronRight, ChevronLeft, Zap, Volume2, VolumeX, ShieldAlert, 
  CheckCircle2, Flame, RefreshCw 
} from 'lucide-react';

const STAGE_COLORS = {
  NORMAL:    { bg: 'bg-emerald-950/60', border: 'border-emerald-500/50', text: 'text-emerald-300', dot: 'bg-emerald-400', glow: '#10b981' },
  CAUTION:   { bg: 'bg-yellow-950/60',  border: 'border-yellow-500/50',  text: 'text-yellow-300',  dot: 'bg-yellow-400',  glow: '#eab308' },
  WARNING:   { bg: 'bg-orange-950/60',  border: 'border-orange-500/50',  text: 'text-orange-300',  dot: 'bg-orange-400',  glow: '#f97316' },
  CRITICAL:  { bg: 'bg-red-950/70',     border: 'border-red-500/60',     text: 'text-red-300',     dot: 'bg-red-500',     glow: '#ef4444' },
  EMERGENCY: { bg: 'bg-slate-950/95',   border: 'border-red-600/80',     text: 'text-red-400',     dot: 'bg-red-600',     glow: '#dc2626' },
};

// Web Audio API Tactical Sound Synthesizer (No external assets required)
class TacticalAudio {
  constructor() {
    this.ctx = null;
    this.muted = false;
  }

  init() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playTone(freq, type = 'sine', duration = 0.15, delay = 0) {
    if (this.muted) return;
    try {
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime + delay);
      gain.gain.setValueAtTime(0.08, this.ctx.currentTime + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + delay + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(this.ctx.currentTime + delay);
      osc.stop(this.ctx.currentTime + delay + duration);
    } catch (e) {}
  }

  playStage(stage) {
    if (stage === 1) {
      this.playTone(440, 'triangle', 0.12);
      this.playTone(660, 'triangle', 0.16, 0.12);
    } else if (stage === 2) {
      this.playTone(520, 'square', 0.12);
      this.playTone(440, 'square', 0.15, 0.14);
    } else if (stage === 3) {
      this.playTone(780, 'sawtooth', 0.1);
      this.playTone(780, 'sawtooth', 0.1, 0.12);
      this.playTone(780, 'sawtooth', 0.15, 0.24);
    } else if (stage === 4) {
      this.playTone(280, 'sawtooth', 0.4);
      this.playTone(180, 'sawtooth', 0.6, 0.35);
    }
  }

  playMitigateSuccess() {
    this.playTone(523.25, 'sine', 0.15);
    this.playTone(659.25, 'sine', 0.15, 0.12);
    this.playTone(783.99, 'sine', 0.25, 0.24);
    this.playTone(1046.50, 'sine', 0.4, 0.38);
  }
}

const audioSynth = new TacticalAudio();

export default function CascadeTimelinePanel({ telemetry, onStartCascade, onStopCascade }) {
  const [isRunning, setIsRunning]     = useState(false);
  const [allStages, setAllStages]     = useState([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [isMitigating, setIsMitigating] = useState(false);
  const lastStageRef = useRef(-1);

  const cascade      = telemetry?.cascade || null;
  const currentStage = cascade?.stage ?? 0;
  const stageTick    = cascade?.stage_tick ?? 0;
  const ticksTotal   = cascade?.ticks_per_stage ?? 100;
  const stageInfo    = cascade?.current_stage_info || null;
  const isActive     = cascade?.active || false;
  const isPaused     = cascade?.paused || false;
  const isMitigated  = cascade?.mitigated || false;
  const isSeized     = cascade?.engine_seized || (currentStage === 4 && !isMitigated);
  const mode         = cascade?.mode || 'auto';

  audioSynth.muted = !soundEnabled;

  // Audio cues on stage transitions
  useEffect(() => {
    if (isActive && currentStage !== lastStageRef.current) {
      lastStageRef.current = currentStage;
      if (isMitigated) {
        audioSynth.playMitigateSuccess();
      } else {
        audioSynth.playStage(currentStage);
      }
    }
  }, [isActive, currentStage, isMitigated]);

  // Fetch all stage definitions on first render
  useEffect(() => {
    fetch('http://localhost:8000/api/fault/cascade-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'status' })
    })
      .then(r => r.json())
      .then(d => { if (d.all_stages) setAllStages(d.all_stages); })
      .catch(() => {});
  }, []);

  // Sync local running state from telemetry
  useEffect(() => {
    setIsRunning(isActive);
  }, [isActive]);

  const sendControl = (actionPayload) => {
    return fetch('http://localhost:8000/api/fault/cascade-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(actionPayload)
    })
      .then(r => r.json())
      .catch(() => {});
  };

  const handleStart = () => {
    sendControl({ action: 'start' }).then(d => {
      if (d?.stages) setAllStages(d.stages);
      setIsRunning(true);
      lastStageRef.current = 0;
      audioSynth.playTone(587, 'sine', 0.15);
      if (onStartCascade) onStartCascade();
    });
  };

  const handleStop = () => {
    sendControl({ action: 'stop' }).then(() => {
      setIsRunning(false);
      lastStageRef.current = -1;
      if (onStopCascade) onStopCascade();
    });
  };

  const handleTogglePause = () => {
    sendControl({ action: isPaused ? 'resume' : 'pause' });
  };

  const handleNextStage = () => {
    sendControl({ action: 'next_stage' });
  };

  const handlePrevStage = () => {
    sendControl({ action: 'prev_stage' });
  };

  const handleJumpStage = (stageIdx) => {
    sendControl({ action: 'set_stage', stage: stageIdx });
  };

  const handleToggleMode = () => {
    sendControl({ action: 'set_mode', mode: mode === 'auto' ? 'manual' : 'auto' });
  };

  const handleEngageMitigation = () => {
    setIsMitigating(true);
    audioSynth.playMitigateSuccess();
    sendControl({ action: 'mitigate' }).finally(() => {
      setIsMitigating(false);
    });
  };

  const progressPct = ticksTotal > 0 ? Math.round((stageTick / ticksTotal) * 100) : 0;
  const rulEstimate = isMitigated ? 750 : (stageInfo?.rul_estimate ?? 875);

  // Asset threat per stage: 0%→20%→45%→75%→100%
  const ASSET_RISK_PCT = [0, 20, 45, 75, 100];
  const assetRiskPct = isMitigated ? 0 : (isActive ? (ASSET_RISK_PCT[currentStage] ?? 0) : 0);
  const assetValueCr = 85;
  const assetAtRiskCr = ((assetRiskPct / 100) * assetValueCr).toFixed(0);

  // Detection advantage: minutes AI detects ahead of threshold per stage
  const DETECTION_ADV_MIN = [null, 4, 2.5, 0.8, null];
  const detAdvMin = isActive && !isMitigated ? DETECTION_ADV_MIN[currentStage] : null;

  const CHAIN_NODES = [
    { stage: 0, label: 'NOMINAL',  icon: '✅', color: 'text-emerald-400 border-emerald-500/60 bg-emerald-950/60' },
    { stage: 1, label: 'INJECTOR', icon: '💉', color: 'text-yellow-400 border-yellow-500/60 bg-yellow-950/60' },
    { stage: 2, label: 'KNOCK',    icon: '🔥', color: 'text-orange-400 border-orange-500/60 bg-orange-950/60' },
    { stage: 3, label: 'THERMAL',  icon: '♨️', color: 'text-red-400 border-red-500/60 bg-red-950/60' },
    { stage: 4, label: 'SEIZURE',  icon: '💀', color: 'text-slate-400 border-red-700/80 bg-slate-950/90' },
  ];


  return (
    <div className="gcs-card p-3 flex flex-col gap-3">

      {/* Header */}
      <div className="gcs-card-header flex items-center justify-between">
        <span className="flex items-center gap-2">
          <Rocket size={16} className="text-orange-400" />
          <span className="font-['Rajdhani'] tracking-wider text-base font-bold">
            MISSION MANGAL SCENARIO — REAL CASCADE SIMULATION
          </span>
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`px-2 py-1 rounded text-[10px] font-mono flex items-center gap-1 border transition-all ${
              soundEnabled ? 'border-cyan-500/40 text-cyan-300 bg-cyan-950/40' : 'border-slate-700 text-slate-500 bg-slate-900'
            }`}
            title="Toggle Tactical Audio Warning Synthesizer"
          >
            {soundEnabled ? <Volume2 size={12} /> : <VolumeX size={12} />}
            {soundEnabled ? 'AUDIO ON' : 'MUTED'}
          </button>
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-bold ${
            isMitigated
              ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300'
              : isSeized
              ? 'bg-red-950/90 border-red-600 text-red-300 animate-pulse'
              : isActive
              ? 'bg-orange-950/80 border-orange-500 text-orange-300'
              : 'bg-slate-900 border-slate-700 text-slate-400'
          }`}>
            {isMitigated ? 'MITIGATED (SAVED)' : isSeized ? 'ENGINE SEIZED' : isActive ? `STAGE ${currentStage}/4 ACTIVE` : 'READY'}
          </span>
        </div>
      </div>



      {/* ── CASCADE CHAIN VISUALIZER ─────────────────────────── */}
      <div className="bg-slate-950/70 border border-slate-800 rounded p-2.5">
        <div className="text-[9px] font-mono text-slate-500 mb-2 tracking-widest">FAILURE PROPAGATION CHAIN</div>
        <div className="flex items-center justify-between gap-1">
          {CHAIN_NODES.map((node, idx) => {
            const isNodeActive    = isActive && node.stage === currentStage && !isMitigated && !isSeized;
            const isNodePast      = isActive && node.stage < currentStage && !isMitigated;
            const isNodeMitigated = isMitigated && node.stage <= currentStage;
            const isNodeSeized    = isSeized && node.stage <= 4;
            return (
              <React.Fragment key={node.stage}>
                <div className={`flex flex-col items-center gap-1 flex-1 rounded border px-1 py-1.5 transition-all duration-500 ${
                  isNodeMitigated && node.stage <= currentStage
                    ? 'border-emerald-500/60 bg-emerald-950/50'
                    : isNodeActive
                    ? `${node.color} ring-1 ring-current shadow-[0_0_10px_rgba(255,255,255,0.1)]`
                    : isNodePast
                    ? 'border-red-800/60 bg-red-950/50 opacity-80'
                    : 'border-slate-800 bg-slate-900/40 opacity-40'
                }`}>
                  <span className={`text-base leading-none ${isNodeActive ? 'animate-bounce' : ''}`}>{node.icon}</span>
                  <span className={`text-[8px] font-mono font-bold ${
                    isNodeMitigated && node.stage <= currentStage ? 'text-emerald-400' :
                    isNodeActive ? 'text-white' :
                    isNodePast ? 'text-red-400' : 'text-slate-600'
                  }`}>{node.label}</span>
                </div>
                {idx < CHAIN_NODES.length - 1 && (
                  <div className={`text-[10px] font-bold shrink-0 transition-colors duration-500 ${
                    isNodePast || isNodeActive ? 'text-red-500' : 'text-slate-700'
                  }`}>→</div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* ── ASSET THREAT + DETECTION ADVANTAGE ──────────────── */}
      <div className="grid grid-cols-2 gap-2">
        {/* Asset Loss Meter */}
        <div className="bg-slate-950/70 border border-slate-800 rounded p-2">
          <div className="text-[9px] font-mono text-slate-500 mb-1 tracking-widest">ASSET AT RISK (₹{assetValueCr} CR UAV)</div>
          <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${isMitigated ? 100 : assetRiskPct}%`,
                background: isMitigated
                  ? '#10b981'
                  : assetRiskPct > 60 ? '#ef4444' : assetRiskPct > 30 ? '#f59e0b' : '#10b981',
                boxShadow: isMitigated ? '0 0 8px #10b981' : assetRiskPct > 60 ? '0 0 8px #ef4444' : 'none'
              }}
            />
          </div>
          <div className="flex justify-between mt-1 text-[10px] font-mono font-bold">
            <span className={isMitigated ? 'text-emerald-400' : assetRiskPct > 60 ? 'text-red-400' : 'text-slate-400'}>
              {isMitigated ? '✅ SAVED' : assetRiskPct > 0 ? `⚠ ₹${assetAtRiskCr} Cr RISK` : 'NOMINAL'}
            </span>
            <span className="text-slate-500">{isMitigated ? '100%' : `${assetRiskPct}%`}</span>
          </div>
        </div>

        {/* Detection Advantage */}
        <div className={`border rounded p-2 transition-all duration-500 ${
          detAdvMin !== null
            ? 'bg-cyan-950/60 border-cyan-600/60'
            : isMitigated
            ? 'bg-emerald-950/60 border-emerald-600/60'
            : 'bg-slate-950/70 border-slate-800'
        }`}>
          <div className="text-[9px] font-mono text-slate-500 mb-1 tracking-widest">AI DETECTION ADVANTAGE</div>
          {detAdvMin !== null ? (
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold font-mono text-cyan-300 leading-none">{detAdvMin}</span>
              <span className="text-[10px] font-mono text-cyan-400">min</span>
              <span className="text-[9px] font-mono text-slate-400 ml-1">AHEAD OF<br/>THRESHOLD</span>
            </div>
          ) : isMitigated ? (
            <div className="text-xs font-mono text-emerald-400 font-bold">ASSET PRESERVED<br/><span className="text-[10px] text-slate-400">Mitigation successful</span></div>
          ) : (
            <div className="text-[10px] font-mono text-slate-500">Start simulation<br/>to see advantage</div>
          )}
        </div>
      </div>

      {/* Stage Progress (Auto Mode) */}
      {isActive && !isMitigated && !isSeized && mode === 'auto' && (
        <div className="flex items-center gap-3 text-xs font-mono bg-slate-950/40 p-2 rounded border border-cyan-900/30">
          <span className="text-slate-400 shrink-0 w-24">Stage {currentStage}/4:</span>
          <div className="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-cyan-400 transition-all duration-100 shadow-[0_0_8px_rgba(0,240,255,0.7)]"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          <span className="text-cyan-400 w-16 text-right font-bold">{progressPct}%</span>
        </div>
      )}

      {/* Interactive Presentation Controls (Sticky Top) */}
      <div className="bg-slate-900/80 p-2 rounded border border-slate-700/60 flex flex-wrap gap-2 items-center justify-between shadow-md">
        <div className="flex gap-2 flex-1 min-w-[280px]">
          {!isRunning ? (
            <button
              onClick={handleStart}
              className="flex items-center gap-2 px-4 py-2 bg-orange-950/90 border border-orange-500/70 text-orange-200 rounded text-xs font-mono font-bold hover:bg-orange-900 transition-all flex-1 justify-center shadow-[0_0_12px_rgba(249,115,22,0.35)] cursor-pointer"
            >
              <Rocket size={14} className="text-orange-400" />
              START REAL CASCADE SIMULATION (Mission Mangal)
            </button>
          ) : (
            <>
              <button
                onClick={handleTogglePause}
                className={`flex items-center gap-1.5 px-3 py-1.5 border rounded text-xs font-mono font-bold transition-all cursor-pointer ${
                  isPaused 
                    ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300 hover:bg-emerald-900' 
                    : 'bg-amber-950/80 border-amber-500 text-amber-300 hover:bg-amber-900'
                }`}
                title={isPaused ? 'Resume Auto Run' : 'Pause at Current Stage to Explain to Judges'}
              >
                {isPaused ? <Play size={13} /> : <Pause size={13} />}
                {isPaused ? 'RESUME' : 'PAUSE'}
              </button>

              <button
                onClick={handlePrevStage}
                disabled={currentStage <= 0}
                className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 text-slate-300 rounded text-xs font-mono font-bold hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                title="Step to Previous Stage"
              >
                <ChevronLeft size={14} />
              </button>

              <button
                onClick={handleNextStage}
                disabled={currentStage >= 4}
                className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 text-slate-300 rounded text-xs font-mono font-bold hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                title="Step to Next Stage"
              >
                <ChevronRight size={14} />
              </button>

              <button
                onClick={handleStop}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 border border-slate-700 text-slate-300 rounded text-xs font-mono font-bold hover:bg-slate-800 transition-all cursor-pointer"
                title="Reset to Nominal Operation"
              >
                <Square size={13} />
                RESET
              </button>
            </>
          )}
        </div>

        {/* Mode Selector */}
        {isRunning && (
          <button
            onClick={handleToggleMode}
            className="px-2.5 py-1.5 bg-slate-900/90 border border-cyan-500/40 text-cyan-300 rounded text-xs font-mono hover:bg-slate-800 transition-all cursor-pointer"
            title="Switch between 5-second automatic progression and step-by-step judge presentation mode"
          >
            MODE: {mode === 'auto' ? 'AUTO (5s)' : 'MANUAL STEP'}
          </button>
        )}
      </div>

      {/* ── HERO ACTION: AUTONOMOUS AI MITIGATION BUTTON ── */}
      {isActive && !isMitigated && currentStage < 4 && (
        <div className="p-2.5 bg-gradient-to-r from-emerald-950/80 via-teal-950/90 to-emerald-950/80 border border-emerald-500/70 rounded-lg shadow-[0_0_20px_rgba(16,185,129,0.25)] flex flex-col sm:flex-row items-center justify-between gap-3 animate-pulse">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-emerald-500/20 rounded-full border border-emerald-400/40 text-emerald-300">
              <ShieldAlert size={20} />
            </div>
            <div>
              <div className="text-emerald-300 font-bold font-mono text-xs tracking-wider flex items-center gap-1.5">
                AUTONOMOUS EMERGENCY MITIGATION READY
              </div>
              <div className="text-[11px] text-slate-300">
                Deploy FADEC countermeasure: Auto-derate throttle to 50%, enrich mixture, cool cylinder, command RTB.
              </div>
            </div>
          </div>
          <button
            onClick={handleEngageMitigation}
            disabled={isMitigating}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-slate-950 font-bold text-xs font-mono rounded shadow-[0_0_12px_rgba(16,185,129,0.6)] hover:scale-105 active:scale-95 transition-all shrink-0 cursor-pointer"
          >
            🛡️ ENGAGE AI MITIGATION (SAVE ASSET)
          </button>
        </div>
      )}

      {/* Mission Saved Banner */}
      {isMitigated && (
        <div className="p-2.5 bg-emerald-950/80 border border-emerald-500/60 rounded flex items-center gap-2.5">
          <CheckCircle2 size={20} className="text-emerald-400 shrink-0" />
          <div>
            <div className="text-emerald-300 font-bold font-mono text-xs tracking-wider">✅ ASSET PRESERVED — AUTONOMOUS RTB INITIATED</div>
            <div className="text-[10px] font-mono text-slate-400 mt-0.5">FADEC: Power derated 50% · Mixture enriched · CHT stabilized · 3,300 RPM safe loiter</div>
          </div>
        </div>
      )}

      {/* Engine Seizure Banner */}
      {isSeized && (
        <div className="p-2.5 bg-red-950/90 border border-red-600/80 rounded flex items-center gap-2.5 animate-pulse">
          <Flame size={20} className="text-red-500 shrink-0" />
          <div>
            <div className="text-red-300 font-bold font-mono text-xs tracking-wider">💀 ENGINE SEIZURE — 0 RPM — IN-FLIGHT FLAMEOUT</div>
            <div className="text-[10px] font-mono text-slate-400 mt-0.5">Piston #1 thermally welded · Crankshaft locked · Asset lost · Threshold alarm: 4 min too late</div>
          </div>
        </div>
      )}

      {/* Timeline Stages List */}
      <div className="space-y-1.5 max-h-[420px] overflow-y-auto pr-1">
        {(allStages.length > 0 ? allStages : [{ stage: 0, label: 'STAGE 0: NOMINAL', severity_level: 'NORMAL', description: 'Loading...', old_system: '...', our_system: '...', rul_estimate: 875 }]).map((s) => {
          const col = STAGE_COLORS[s.severity_level] || STAGE_COLORS.NORMAL;
          const isCurrentStage = isActive && s.stage === currentStage;
          const isPastStage    = isActive && s.stage < currentStage;
          const isFutureStage  = isActive && s.stage > currentStage;

          return (
            <div
              key={s.stage}
              onClick={() => isActive && handleJumpStage(s.stage)}
              className={`rounded border p-2.5 transition-all duration-300 cursor-pointer ${col.bg} ${col.border}
                ${isCurrentStage ? 'ring-1 ring-cyan-400/70 shadow-[0_0_12px_rgba(0,240,255,0.25)] scale-[1.005]' : 'hover:border-slate-600'}
                ${isFutureStage ? 'opacity-35' : ''}
              `}
            >
              {/* Stage Header Row */}
              <div className="flex items-center gap-2">
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${col.dot} ${isCurrentStage ? 'animate-pulse' : ''}`}
                  style={{ boxShadow: isCurrentStage ? `0 0 8px ${col.glow}` : 'none' }}
                />
                <span className={`text-[11px] font-mono font-bold flex-1 ${col.text}`}>{s.label}</span>
                <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border shrink-0 ${
                  isPastStage ? 'text-slate-500 border-slate-700 bg-slate-900/60' :
                  isCurrentStage ? 'text-cyan-400 border-cyan-500/50 bg-cyan-950/60 animate-pulse' : ''
                }`}>
                  {isPastStage ? 'PASSED' : isCurrentStage ? '● ACTIVE' : ''}
                </span>
              </div>

              {/* Compact Chip Row: Old System vs AI Twin */}
              <div className="mt-1.5 flex flex-col gap-1 pl-4">
                <div className="flex items-start gap-1.5">
                  <span className="text-[9px] font-mono font-bold text-red-400 bg-red-950/60 border border-red-800/50 px-1.5 py-0.5 rounded shrink-0">❌ OLD</span>
                  <span className="text-[10px] font-mono text-slate-400 leading-tight">{s.old_system.replace(/^[❌⚠✅💀]/,' ').trim()}</span>
                </div>
                <div className="flex items-start gap-1.5">
                  <span className="text-[9px] font-mono font-bold text-cyan-400 bg-cyan-950/60 border border-cyan-800/50 px-1.5 py-0.5 rounded shrink-0">⚡ AI</span>
                  <span className="text-[10px] font-mono text-slate-200 leading-tight">{s.our_system.replace(/^[🚨✅⚡]/,' ').trim()}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
