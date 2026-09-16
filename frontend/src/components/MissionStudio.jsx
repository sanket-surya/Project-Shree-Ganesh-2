import React, { useState } from 'react';
import { Plane, AlertTriangle, ShieldCheck, Sliders, Play, RotateCcw, Mountain, Sun, Flame, Zap, AlertOctagon, Cpu } from 'lucide-react';

export default function MissionStudio({ telemetry, onToggleFault, onCompoundScenario, onClearFault, onSetMissionProfile }) {
  const [severity, setSeverity] = useState(0.85);
  const [activeProfile, setActiveProfile] = useState('Nominal');
  const [selectedEngine, setSelectedEngine] = useState('ROTAX_914F');
  
  const activeFaults = telemetry?.state?.active_faults || (telemetry?.state?.active_fault && telemetry?.state?.active_fault !== 'NONE' ? telemetry.state.active_fault.split(' + ') : []);
  const hasActiveFaults = activeFaults.length > 0;

  const engineOptions = [
    {
      id: 'ROTAX_914F',
      badge: 'DEFENSE DEFAULT',
      name: 'ROTAX 914F3 TURBO',
      hp: '115 HP',
      kw: '84.5 kW',
      type: '4-Cyl Boxer Turbo (1211 cc)',
      fuel: 'MOGAS 95 / AVGAS 100LL',
      rpm: '5800 RPM',
      tbo: '2,000 hrs TBO',
      airframe: 'DRDO Tapas-BH-201, IAI Heron Mk I, Hermes 900',
      cert: 'EASA.E.122 / FAR-33'
    },
    {
      id: 'AUSTRO_AE300',
      badge: 'HEAVY FUEL DIESEL',
      name: 'AUSTRO AE300 DIESEL',
      hp: '168 HP',
      kw: '123.5 kW',
      type: 'Inline-4 Turbo Common-Rail (1991 cc)',
      fuel: 'Jet-A1 / Diesel F-54 (Single Fuel Concept)',
      rpm: '3880 RPM',
      tbo: '1,800 hrs TBO',
      airframe: 'Schiebel Camcopter S-100, Diamond DA42 MPP',
      cert: 'EASA.E.118 / JAR-E'
    },
    {
      id: 'LYCOMING_IO360',
      badge: 'DIRECT DRIVE',
      name: 'LYCOMING IO-360 FLAT-4',
      hp: '180 HP',
      kw: '134 kW',
      type: '4-Cyl Horizontally Opposed (5916 cc)',
      fuel: '100LL Avgas Direct-Drive',
      rpm: '2700 RPM',
      tbo: '2,000 hrs TBO',
      airframe: 'Tactical Target Drones, Border Decoy Airframes',
      cert: 'FAA TCDS 1E10'
    }
  ];

  const handleEngineSelect = async (engId) => {
    setSelectedEngine(engId);
    try {
      await fetch('http://localhost:8000/api/engine/select-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine_id: engId })
      });
    } catch (err) {
      console.error('Failed to switch engine profile:', err);
    }
  };

  const currentEngineObj = engineOptions.find(e => e.id === selectedEngine) || engineOptions[0];

  const missionProfiles = [
    {
      id: 'Nominal',
      label: 'Nominal ISR Loiter',
      theater: 'Maritime / Coastal EEZ',
      theaterBadge: 'INDIAN OCEAN',
      alt: '1,500m (5,000 ft)',
      temp: '+15°C Ambient',
      throttle: '75% Throttle',
      tacticalRole: 'Continuous 24-hr maritime reconnaissance & coastal border surveillance.',
      icon: Plane
    },
    {
      id: 'High_Altitude_Loiter',
      label: 'High Altitude Recon',
      theater: 'LAC Ladakh / Siachen',
      theaterBadge: 'SIACHEN / LAC',
      alt: '7,600m (25,000 ft)',
      temp: '-34°C Sub-Zero',
      throttle: 'Turbo Boost (95%)',
      tacticalRole: 'High-altitude mountain reconnaissance in low-density rarefied air.',
      icon: Mountain
    },
    {
      id: 'Hot_Desert_Ops',
      label: 'Hot Desert Patrol',
      theater: 'Thar Desert / Rajasthan',
      theaterBadge: 'THAR SECTOR',
      alt: '800m (2,500 ft)',
      temp: '+46°C Extreme Heat',
      throttle: 'Thermal Stress (80%)',
      tacticalRole: 'Hot-and-high border patrol with elevated ram-air heat exchanger loads.',
      icon: Sun
    },
    {
      id: 'Rapid_Climb',
      label: 'Combat Scramble Climb',
      theater: 'Forward Base Scramble',
      theaterBadge: 'INTERCEPT DASH',
      alt: '0 to 4,000m Rapid',
      temp: 'Dynamic Gradient',
      throttle: '100% Takeoff Power',
      tacticalRole: 'Immediate quick-reaction threat intercept at maximum BSFC fuel burn rate.',
      icon: Play
    },
  ];

  const faultTypes = [
    { id: 'Cylinder_Misfire',   label: 'Cylinder 3 Misfire',     desc: 'Ignition coil failure on Cyl 3' },
    { id: 'Turbo_Degradation',  label: 'Turbo Wastegate Jam',    desc: 'Loss of manifold boost pressure' },
    { id: 'Oil_Starvation',     label: 'Oil Line Rupture',       desc: 'Lubrication pressure collapse' },
    { id: 'Coolant_Loss',       label: 'Radiator Puncture',      desc: 'Thermal runaway across all heads' },
    { id: 'Injector_Clogging',  label: 'Injector Clogging',      desc: 'Lean fuel burn & extreme EGT spike' },
    { id: 'Sensor_Drift',       label: 'Thermocouple Drift',     desc: 'False +65°C sensor calibration bias' },
    { id: 'Combustion_Knock',   label: 'Combustion Knock',       desc: 'Detonation — IGN retard & CHT rise' },
    { id: 'Valve_Leakage',      label: 'Exhaust Valve Leakage',  desc: 'Blowby — EGT Cyl-2 spike & power loss' },
  ];

  const compoundScenarios = [
    {
      id: 'THERMAL_RUNAWAY',
      label: 'Cascading Thermal Runaway',
      desc: 'Turbo Jam + Radiator Puncture (Severe Overheat)',
      icon: Flame,
      color: 'border-[#382024] bg-[#161216] text-red-300 hover:border-red-600'
    },
    {
      id: 'MECHANICAL_TRAUMA',
      label: 'Catastrophic Mechanical Trauma',
      desc: 'Cylinder Misfire + Oil Pressure Loss (High Vib & Friction)',
      icon: AlertOctagon,
      color: 'border-[#382d20] bg-[#161412] text-amber-300 hover:border-amber-600'
    },
    {
      id: 'DETONATION_SURGE',
      label: 'Detonation & Knock Surge',
      desc: 'Injector Clogging + Severe Combustion Knock',
      icon: Zap,
      color: 'border-[#202738] bg-[#12141c] text-sky-300 hover:border-sky-600'
    }
  ];

  const handleProfileSelect = (pId) => {
    setActiveProfile(pId);
    if (onSetMissionProfile) onSetMissionProfile(pId);
  };

  const currentProfileObj = missionProfiles.find(p => p.id === activeProfile) || missionProfiles[0];

  return (
    <div className="gcs-card p-3 flex flex-col justify-between">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <Sliders size={15} className="text-sky-400" />
          <span>MISSION SCENARIOS & IN-FLIGHT FAULT INJECTION</span>
        </span>
        {hasActiveFaults ? (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-mono font-bold text-red-400 bg-red-950/80 border border-red-500/80 px-2 py-0.5 rounded flex items-center gap-1">
              <AlertTriangle size={12} /> {activeFaults.length} FAULT(S) ACTIVE: {activeFaults.join(' + ')}
            </span>
          </div>
        ) : (
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
            <ShieldCheck size={12} /> NOMINAL IN-FLIGHT TWIN
          </span>
        )}
      </div>

      {/* 0. Propulsion Architecture Selection (Engine-Agnostic Modular Core) */}
      <div className="mt-2 mb-3 p-2.5 rounded bg-[#0d121c] border border-[#1e273b]">
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <div className="flex items-center gap-1.5 text-slate-200 font-semibold">
            <Cpu size={13} className="text-emerald-400" />
            <span>PROPULSION PLATFORM ARCHITECTURE (ENGINE-AGNOSTIC MODULAR CORE)</span>
          </div>
          <span className="text-[10px] text-emerald-400 font-mono bg-emerald-950/60 border border-emerald-700/40 px-1.5 py-0.2 rounded">
            MODULAR THERMODYNAMIC ABSTRACTION
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {engineOptions.map((eng) => {
            const isEngSelected = selectedEngine === eng.id;
            return (
              <button
                key={eng.id}
                onClick={() => handleEngineSelect(eng.id)}
                className={`p-2 rounded border text-left transition-all ${
                  isEngSelected
                    ? 'bg-[#182336] border-emerald-500/80 text-white shadow-sm ring-1 ring-emerald-500/40'
                    : 'bg-[#0f1420] border-[#1d2538] text-slate-300 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span className="text-[11px] font-mono font-bold tracking-wide text-slate-100">
                    {eng.name}
                  </span>
                  <span className={`text-[8.5px] font-mono px-1 py-0.2 rounded font-bold ${
                    isEngSelected ? 'bg-emerald-900/80 text-emerald-300 border border-emerald-600/60' : 'bg-[#131926] text-slate-400 border border-slate-700/50'
                  }`}>
                    {eng.badge}
                  </span>
                </div>
                <div className="text-[10px] text-emerald-300 font-mono font-semibold">
                  {eng.hp} ({eng.kw}) • {eng.rpm}
                </div>
                <div className="text-[9.5px] text-slate-400 font-mono mt-0.5 truncate">
                  {eng.type}
                </div>
              </button>
            );
          })}
        </div>
        <div className="mt-2 pt-1.5 border-t border-[#1a2234] flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span className="text-slate-500">FUEL:</span>
            <span className="text-slate-200 font-medium">{currentEngineObj.fuel}</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-500">TBO:</span>
            <span className="text-amber-300 font-medium">{currentEngineObj.tbo}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-slate-500">AIRFRAMES:</span>
            <span className="text-sky-300 font-medium">{currentEngineObj.airframe}</span>
            <span className="text-slate-600">|</span>
            <span className="text-emerald-400 font-mono">{currentEngineObj.cert}</span>
          </div>
        </div>
      </div>

      {/* 1. Mission Profile Presets with Defense Deployment Theaters */}
      <div className="mt-2">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
          <span className="font-semibold text-slate-300">OPERATIONAL FLIGHT PROFILES & DEPLOYMENT THEATERS</span>
          <span className="text-[10px] text-sky-400 font-mono">AIRFRAME: {currentEngineObj.airframe.split(',')[0]}</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {missionProfiles.map((p) => {
            const Icon = p.icon;
            const isSelected = activeProfile === p.id;
            return (
              <button
                key={p.id}
                onClick={() => handleProfileSelect(p.id)}
                className={`p-2.5 rounded border text-left transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-[#182336] border-sky-500 text-white shadow-sm'
                    : 'bg-[#0f131d] border-[#1d2436] text-slate-300 hover:border-slate-600'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="text-[9.5px] font-mono font-bold px-1 py-0.2 rounded bg-[#101522] border border-[#232d42] text-sky-300">
                      {p.theaterBadge}
                    </span>
                    <Icon size={12} className={isSelected ? 'text-sky-400' : 'text-slate-500'} />
                  </div>
                  <div className="text-[11.5px] font-semibold tracking-tight text-slate-100">
                    {p.label}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    {p.alt} • {p.temp}
                  </div>
                </div>
                <div className="text-[9.5px] font-mono text-sky-400/90 mt-1.5 pt-1 border-t border-[#1d2436]">
                  {p.throttle}
                </div>
              </button>
            );
          })}
        </div>

        {/* Operational Theater Briefing Strip */}
        <div className="mt-2 p-2 rounded bg-[#0b0e16] border border-[#1a2030] text-[11px] font-mono flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 truncate">
            <span className="text-slate-400">ACTIVE DEPLOYMENT:</span>
            <span className="text-white font-bold">{currentProfileObj.theater}</span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-300 truncate hidden md:inline">{currentProfileObj.tacticalRole}</span>
          </div>
          <span className="text-[10px] bg-[#162032] border border-sky-500/40 text-sky-300 px-2 py-0.5 rounded whitespace-nowrap">
            TRL-4 TESTED
          </span>
        </div>
      </div>

      {/* 2. Compound Defense Emergency Scenarios */}
      <div className="mt-3 pt-2.5 border-t border-[#1a202e]">
        <div className="text-xs font-mono text-slate-400 mb-1.5 font-semibold text-amber-400 flex items-center gap-1.5">
          <AlertOctagon size={13} className="text-amber-400" />
          COMPOUND DEFENSE EMERGENCY SCENARIOS (MULTIPLE SIMULTANEOUS FAILURES)
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {compoundScenarios.map((cs) => {
            const Icon = cs.icon;
            return (
              <button
                key={cs.id}
                onClick={() => onCompoundScenario && onCompoundScenario(cs.id, severity)}
                className={`p-2 rounded border text-left transition-all ${cs.color} shadow-sm`}
              >
                <div className="flex items-center gap-1.5 text-xs font-['Rajdhani'] font-bold uppercase">
                  <Icon size={14} />
                  {cs.label}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Individual Mid-Air Fault Toggle Buttons */}
      <div className="mt-3 pt-2.5 border-t border-slate-800">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
          <span className="font-semibold text-slate-200">INDIVIDUAL FAULT TOGGLES (CLICK TO COMBINE)</span>
          <div className="flex items-center gap-2">
            <span className="text-[10px]">Severity: {(severity * 100).toFixed(0)}%</span>
            <input
              type="range"
              min="0.2"
              max="1.0"
              step="0.05"
              value={severity}
              onChange={(e) => setSeverity(parseFloat(e.target.value))}
              className="w-16 h-1 accent-cyan-400 bg-slate-700 rounded cursor-pointer"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {faultTypes.map((f) => {
            const isActive = activeFaults.includes(f.id);
            return (
              <button
                key={f.id}
                onClick={() => onToggleFault && onToggleFault(f.id, severity)}
                className={`tactical-btn text-xs justify-between ${
                  isActive ? 'danger active ring-2 ring-red-500' : 'danger'
                }`}
              >
                <span className="flex items-center gap-1.5 truncate">
                  <AlertTriangle size={13} className={isActive ? 'text-white' : 'text-amber-400'} />
                  <span className="truncate">{f.label}</span>
                </span>
                <span className={`text-[10px] px-1 rounded ${isActive ? 'bg-red-500 text-white font-bold' : 'bg-slate-800 text-slate-400'}`}>
                  {isActive ? 'ACTIVE' : 'OFF'}
                </span>
              </button>
            );
          })}
        </div>

        {/* Clear Fault / Return to Nominal Button */}
        {hasActiveFaults && (
          <div className="mt-2.5 flex justify-end">
            <button
              onClick={onClearFault}
              className="tactical-btn active bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs"
            >
              <RotateCcw size={13} />
              CLEAR ALL FAULTS & RESTORE NOMINAL PHYSICS
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
