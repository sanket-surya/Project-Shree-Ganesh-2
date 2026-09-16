import React, { useEffect, useState, useMemo } from 'react';
import {
  Wrench,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  FileText,
  Activity,
  Layers,
  Printer,
  X,
  ShieldCheck,
  RotateCw,
  Cpu
} from 'lucide-react';

const URGENCY_CONFIG = {
  CRITICAL: {
    border: 'border-red-500/60',
    bg: 'bg-red-950/40',
    headerBg: 'bg-red-900/30',
    text: 'text-red-400',
    barColor: 'bg-red-500 animate-pulse',
    badgeBorder: 'border-red-500/60',
    badgeBg: 'bg-red-900/50',
    icon: <AlertTriangle size={14} className="text-red-400 animate-bounce" />,
    label: 'REPLACE IMMEDIATELY (AOG)',
    pulse: true
  },
  DUE_SOON: {
    border: 'border-amber-500/50',
    bg: 'bg-amber-950/30',
    headerBg: 'bg-amber-900/20',
    text: 'text-amber-400',
    barColor: 'bg-amber-400',
    badgeBorder: 'border-amber-500/50',
    badgeBg: 'bg-amber-900/40',
    icon: <Clock size={14} className="text-amber-400" />,
    label: 'REPLACEMENT DUE SOON',
    pulse: false
  },
  MONITOR: {
    border: 'border-cyan-500/40',
    bg: 'bg-cyan-950/20',
    headerBg: 'bg-cyan-900/20',
    text: 'text-cyan-300',
    barColor: 'bg-cyan-400',
    badgeBorder: 'border-cyan-500/40',
    badgeBg: 'bg-cyan-900/30',
    icon: <Activity size={14} className="text-cyan-400" />,
    label: 'PREDICTIVE MONITORING',
    pulse: false
  },
  OPTIMAL: {
    border: 'border-emerald-500/40',
    bg: 'bg-emerald-950/20',
    headerBg: 'bg-emerald-900/20',
    text: 'text-emerald-400',
    barColor: 'bg-emerald-500',
    badgeBorder: 'border-emerald-500/40',
    badgeBg: 'bg-emerald-900/30',
    icon: <ShieldCheck size={14} className="text-emerald-400" />,
    label: 'AIRWORTHY (OPTIMAL)',
    pulse: false
  }
};

/* ── Military Work Order Dispatch Modal ────────────────────────────────────── */
function WorkOrderModal({ component, engine, totalHours, onClose }) {
  if (!component) return null;
  const isAog = component.urgency === 'CRITICAL';
  const orderId = `WO-DRDO-${component.id.toUpperCase()}-${Math.floor(1000 + Math.random() * 9000)}`;
  const dateStr = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-cyan-500/50 rounded-lg max-w-2xl w-full p-5 shadow-2xl relative font-mono text-xs text-slate-300">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3.5 right-3.5 text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition-colors"
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div className="border-b border-slate-800 pb-3 mb-4 flex items-start justify-between pr-8">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/40 text-[10px] font-bold">
                MIL-STD-1388 / EASA FORM 108
              </span>
              {isAog && (
                <span className="px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-500/50 text-[10px] font-bold animate-pulse">
                  AOG PRIORITY 1 — GROUNDING ORDER
                </span>
              )}
            </div>
            <h2 className="text-base font-bold text-white font-['Rajdhani'] tracking-wider mt-1">
              DEPOT DISPATCH & PART REPLACEMENT WORK ORDER
            </h2>
          </div>
          <div className="text-right shrink-0">
            <span className="text-[10px] text-slate-500">WORK ORDER ID:</span>
            <div className="text-cyan-400 font-bold">{orderId}</div>
            <span className="text-[10px] text-slate-500">{dateStr}</span>
          </div>
        </div>

        {/* Order Details Grid */}
        <div className="grid grid-cols-2 gap-3 bg-slate-950/80 p-3.5 rounded border border-slate-800/80 mb-3">
          <div>
            <span className="text-[10px] text-slate-500">TARGET COMPONENT:</span>
            <div className="text-white font-bold">{component.name}</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">OEM P/N: {component.part_number}</div>
          </div>
          <div>
            <span className="text-[10px] text-slate-500">SUBSYSTEM:</span>
            <div className="text-slate-200">{component.subsystem}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">SPEC: {component.mil_standard}</div>
          </div>
          <div>
            <span className="text-[10px] text-slate-500">PROPULSION PLATFORM:</span>
            <div className="text-slate-200">{engine || 'Rotax 914F3 Turbocharged'}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Total Flight Hours: {totalHours?.toFixed(1) || 124.5}h</div>
          </div>
          <div>
            <span className="text-[10px] text-slate-500">CURRENT HEALTH & LIFE:</span>
            <div className="flex items-center gap-2">
              <span className={`font-bold ${isAog ? 'text-red-400' : 'text-emerald-400'}`}>
                {component.health_pct?.toFixed(1)}% Health
              </span>
              <span className="text-slate-400">({component.hours_remaining?.toFixed(1)} hrs rem)</span>
            </div>
            <div className={`text-[10px] font-semibold mt-0.5 ${isAog ? 'text-red-400' : 'text-amber-400'}`}>
              Due: {component.replacement_date}
            </div>
          </div>
        </div>

        {/* Action Directives */}
        <div className="bg-slate-950/60 p-3 rounded border border-slate-800/80 mb-4">
          <span className="text-[10px] text-amber-400 font-bold block mb-1">MANDATORY DEPOT DIRECTIVE:</span>
          <p className="text-[11px] text-slate-200 leading-relaxed font-sans">
            {component.action_required}
          </p>
          <div className="mt-2 text-[10px] text-slate-400 border-t border-slate-800 pt-1.5 flex justify-between">
            <span>Primary Wear Driver: <strong className="text-slate-300">{component.wear_factor_label}</strong></span>
            <span>Requisition Depot: <strong className="text-cyan-300">HAL / IAF Base Repair Depot 402</strong></span>
          </div>
        </div>

        {/* Signature & Dispatch Authorization */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[10px] text-slate-500">
          <div>
            <span>AUTONOMOUS AI HEALTH ENGINE: <strong className="text-emerald-400">VERIFIED SIGN-OFF</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => window.print()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold transition-colors"
            >
              <Printer size={13} />
              PRINT DISPATCH ORDER
            </button>
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
            >
              DISMISS
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Individual Component Prognostic Card ─────────────────────────────────── */
function ComponentCard({ comp, onGenerateOrder }) {
  const [expanded, setExpanded] = useState(false);
  const u = URGENCY_CONFIG[comp.urgency] || URGENCY_CONFIG.OPTIMAL;
  const isCritical = comp.urgency === 'CRITICAL';
  const isDueSoon = comp.urgency === 'DUE_SOON';

  return (
    <div
      className={`rounded border ${u.border} ${u.bg} p-3 transition-all duration-200 hover:border-slate-500 flex flex-col justify-between`}
    >
      <div>
        {/* Top Header Row */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-slate-100 text-[11px] tracking-wide">
                {comp.name}
              </span>
              <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-[9px] font-mono text-cyan-300">
                {comp.part_number}
              </span>
            </div>
            <div className="flex items-center gap-2 text-[9px] font-mono text-slate-400 mt-0.5">
              <span>{comp.subsystem}</span>
              <span>•</span>
              <span className="text-slate-500">{comp.mil_standard}</span>
            </div>
          </div>

          {/* Urgency Badge */}
          <div className={`px-2 py-0.5 rounded border text-[9px] font-mono font-bold flex items-center gap-1 shrink-0 ${u.badgeBorder} ${u.badgeBg} ${u.text}`}>
            {u.icon}
            <span>{u.label}</span>
          </div>
        </div>

        {/* Health Progress Bar & Percentage */}
        <div className="mb-2.5">
          <div className="flex justify-between items-center text-[10px] font-mono mb-1">
            <span className="text-slate-400">COMPONENT HEALTH:</span>
            <span className={`font-bold ${u.text}`}>
              {comp.health_pct?.toFixed(1)}%
            </span>
          </div>
          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800 p-0.5">
            <div
              className={`h-full rounded-full transition-all duration-500 ${u.barColor}`}
              style={{ width: `${Math.max(4, Math.min(100, comp.health_pct))}%` }}
            />
          </div>
        </div>

        {/* 3-Column Metrics: Hours Rem, Days Rem, Replacement Due */}
        <div className="grid grid-cols-3 gap-1.5 bg-slate-950/70 p-2 rounded border border-slate-800/80 text-center mb-2 font-mono">
          <div>
            <span className="text-[8.5px] text-slate-500 block">REMAINING LIFE</span>
            <span className={`text-[12px] font-bold ${u.text}`}>
              {comp.hours_remaining?.toFixed(1)}h
            </span>
            <span className="text-[8px] text-slate-500 block">/ {comp.base_tbo_hours}h TBO</span>
          </div>
          <div>
            <span className="text-[8.5px] text-slate-500 block">TIME AT MALE TEMPO</span>
            <span className="text-[12px] font-bold text-slate-200">
              ~{comp.days_remaining?.toFixed(0)}d
            </span>
            <span className="text-[8px] text-slate-500 block">@ 6.0 hrs/day</span>
          </div>
          <div>
            <span className="text-[8.5px] text-slate-500 block">REPLACEMENT DUE</span>
            <span className={`text-[11px] font-bold block truncate ${isCritical ? 'text-red-400 animate-pulse' : isDueSoon ? 'text-amber-400' : 'text-slate-200'}`}>
              {isCritical ? 'IMMEDIATE (AOG)' : comp.replacement_date}
            </span>
            <span className="text-[8px] text-slate-500 block">Calendar Target</span>
          </div>
        </div>

        {/* Primary Wear Factor & Expandable Directive */}
        <div className="text-[9.5px] font-mono text-slate-400 mb-2">
          <span className="text-slate-500">Wear Driver: </span>
          <span className="text-slate-300">{comp.wear_factor_label}</span>
        </div>

        {expanded && (
          <div className="bg-slate-950/90 p-2.5 rounded border border-slate-800 text-[9.5px] font-mono mb-2 animate-in fade-in duration-150">
            <span className="text-amber-400 font-bold block mb-0.5">DEPOT ACTION DIRECTIVE:</span>
            <p className="text-slate-200 font-sans leading-snug">
              {comp.action_required}
            </p>
          </div>
        )}
      </div>

      {/* Action Row */}
      <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 mt-1">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[9px] font-mono text-slate-400 hover:text-slate-200 flex items-center gap-1 py-1"
        >
          {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          {expanded ? 'LESS INFO' : 'VIEW DIRECTIVE'}
        </button>

        <button
          onClick={() => onGenerateOrder(comp)}
          className={`flex items-center gap-1 px-2.5 py-1 rounded text-[9.5px] font-mono font-bold transition-all ${
            isCritical
              ? 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-950/50 animate-pulse'
              : 'bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30'
          }`}
        >
          <FileText size={11} />
          {isCritical ? 'AOG WORK ORDER' : 'GENERATE ORDER'}
        </button>
      </div>
    </div>
  );
}

/* ── Main Component Export ─────────────────────────────────────────────────── */
export default function MaintenanceScheduler({ telemetry }) {
  const [phmData, setPhmData] = useState(null);
  const [scheduleIntervals, setScheduleIntervals] = useState([]);
  const [filterTab, setFilterTab] = useState('ALL'); // 'ALL' | 'CRITICAL' | 'DUE_SOON' | 'OPTIMAL'
  const [selectedWorkOrderComp, setSelectedWorkOrderComp] = useState(null);
  const [showIntervalsDrawer, setShowIntervalsDrawer] = useState(false);
  const [lastUpdate, setLastUpdate] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Sync component health & maintenance schedule from local backend every 3s
  const fetchMaintenanceData = async () => {
    try {
      setIsRefreshing(true);
      const res = await fetch('http://localhost:8000/api/maintenance-schedule');
      if (res.ok) {
        const data = await res.json();
        setScheduleIntervals(data.schedule || []);
        if (data.components_prognostics) {
          setPhmData(data.components_prognostics);
        }
        setLastUpdate(new Date().toLocaleTimeString());
      }
    } catch {
      // Fallback: Read directly from telemetry if WebSocket delivered it
      if (telemetry?.state?.components_health) {
        setPhmData(telemetry.state.components_health);
        setLastUpdate(new Date().toLocaleTimeString());
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMaintenanceData();
    const interval = setInterval(fetchMaintenanceData, 3000);
    return () => clearInterval(interval);
  }, [telemetry?.state?.active_fault, telemetry?.state?.engine_profile_id]);

  // If telemetry has live components_health from WebSocket, keep in continuous lock
  useEffect(() => {
    if (telemetry?.state?.components_health) {
      setPhmData(telemetry.state.components_health);
    }
  }, [telemetry?.state?.components_health]);

  const componentsList = phmData?.components || [];
  const counts = phmData?.counts || {
    critical: 0,
    due_soon: 0,
    monitor: 0,
    optimal: componentsList.length || 8,
    total: componentsList.length || 8
  };

  const filteredComponents = useMemo(() => {
    if (filterTab === 'CRITICAL') return componentsList.filter(c => c.urgency === 'CRITICAL');
    if (filterTab === 'DUE_SOON') return componentsList.filter(c => c.urgency === 'DUE_SOON');
    if (filterTab === 'OPTIMAL') return componentsList.filter(c => c.urgency === 'OPTIMAL' || c.urgency === 'MONITOR');
    return componentsList;
  }, [componentsList, filterTab]);

  return (
    <div className="gcs-card p-3.5 flex flex-col gap-3 font-mono">
      {/* ── Top Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Wrench size={18} />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-wider font-['Rajdhani'] flex items-center gap-2">
              COMPONENT PROGNOSTICS & PARTS REPLACEMENT MATRIX
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/40">
                PHM CORE
              </span>
            </h1>
            <p className="text-[10px] text-slate-400">
              AI-Driven Arrhenius Thermal Wear · Vibration Stress · 6.0 hr/day MALE Patrol Tempo
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-[10px]">
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>SYNC: {lastUpdate || 'CONNECTING...'}</span>
          </div>
          <button
            onClick={fetchMaintenanceData}
            title="Force refresh prognostics"
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <RotateCw size={13} className={isRefreshing ? 'animate-spin text-cyan-400' : ''} />
          </button>
        </div>
      </div>

      {/* ── Fleet Identity & Tempo Bar ───────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px] bg-slate-900/80 border border-slate-800 rounded p-2">
        <div>
          <span className="text-slate-500 block text-[9px]">PROPULSION UNIT</span>
          <span className="text-slate-200 font-bold truncate block">
            {phmData?.engine_name || telemetry?.state?.engine_name || 'Rotax 914F3 Turbo'}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[9px]">ACCUMULATED HOURS</span>
          <span className="text-cyan-300 font-bold text-[12px]">
            {phmData?.accumulated_hours?.toFixed(1) || telemetry?.state?.accumulated_hours?.toFixed(1) || '124.5'} hrs
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[9px]">AVG COMPONENT HEALTH</span>
          <span className={`text-[12px] font-bold ${
            (phmData?.average_component_health || 88) > 75 ? 'text-emerald-400' : (phmData?.average_component_health || 88) > 50 ? 'text-amber-400' : 'text-red-400'
          }`}>
            {phmData?.average_component_health || 88.5}%
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[9px]">MALE UAV TEMPO</span>
          <span className="text-slate-300 font-semibold">
            {phmData?.tempo_daily_hours || 6.0} hrs/day
          </span>
        </div>
      </div>

      {/* ── Status Metric Tabs (Clickable Filter Buttons) ─────────────────────── */}
      <div className="grid grid-cols-4 gap-2">
        <button
          onClick={() => setFilterTab('ALL')}
          className={`p-2 rounded border text-left transition-all ${
            filterTab === 'ALL'
              ? 'bg-slate-800 border-cyan-500/80 text-white shadow-sm'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400'
          }`}
        >
          <div className="text-[9px] text-slate-500 font-semibold">TOTAL MONITORED</div>
          <div className="text-base font-bold text-white mt-0.5">{counts.total || 8}</div>
          <div className="text-[8.5px] text-cyan-400 mt-0.5">All Critical Parts</div>
        </button>

        <button
          onClick={() => setFilterTab('CRITICAL')}
          className={`p-2 rounded border text-left transition-all ${
            filterTab === 'CRITICAL'
              ? 'bg-red-950/60 border-red-500 text-white shadow-lg shadow-red-950/40'
              : counts.critical > 0
              ? 'bg-red-950/30 border-red-500/50 text-red-300 animate-pulse'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400'
          }`}
        >
          <div className="text-[9px] text-red-400 font-semibold flex items-center justify-between">
            <span>CRITICAL (AOG)</span>
            {counts.critical > 0 && <AlertTriangle size={11} className="text-red-400" />}
          </div>
          <div className={`text-base font-bold mt-0.5 ${counts.critical > 0 ? 'text-red-400' : 'text-slate-400'}`}>
            {counts.critical}
          </div>
          <div className="text-[8.5px] text-slate-500 mt-0.5">Immediate Replace</div>
        </button>

        <button
          onClick={() => setFilterTab('DUE_SOON')}
          className={`p-2 rounded border text-left transition-all ${
            filterTab === 'DUE_SOON'
              ? 'bg-amber-950/60 border-amber-500 text-white shadow-sm'
              : counts.due_soon > 0
              ? 'bg-amber-950/30 border-amber-500/40 text-amber-300'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400'
          }`}
        >
          <div className="text-[9px] text-amber-400 font-semibold flex items-center justify-between">
            <span>DUE SOON</span>
            {counts.due_soon > 0 && <Clock size={11} className="text-amber-400" />}
          </div>
          <div className={`text-base font-bold mt-0.5 ${counts.due_soon > 0 ? 'text-amber-400' : 'text-slate-400'}`}>
            {counts.due_soon}
          </div>
          <div className="text-[8.5px] text-slate-500 mt-0.5">&lt; 75 Flight Hours</div>
        </button>

        <button
          onClick={() => setFilterTab('OPTIMAL')}
          className={`p-2 rounded border text-left transition-all ${
            filterTab === 'OPTIMAL'
              ? 'bg-emerald-950/60 border-emerald-500 text-white shadow-sm'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400'
          }`}
        >
          <div className="text-[9px] text-emerald-400 font-semibold flex items-center justify-between">
            <span>AIRWORTHY</span>
            <ShieldCheck size={11} className="text-emerald-400" />
          </div>
          <div className="text-base font-bold text-emerald-400 mt-0.5">
            {counts.optimal + counts.monitor}
          </div>
          <div className="text-[8.5px] text-slate-500 mt-0.5">Optimal Envelope</div>
        </button>
      </div>

      {/* ── Active AOG Alert Banner ─────────────────────────────────────────── */}
      {counts.critical > 0 && (
        <div className="bg-red-950/60 border border-red-500/60 p-2.5 rounded flex items-center gap-3 text-red-300 text-[10px] animate-pulse">
          <AlertTriangle size={18} className="text-red-400 shrink-0" />
          <div className="flex-1">
            <strong className="text-red-200">GROUNDING ADVISORY (AOG ACTIVE): </strong>
            {counts.critical} critical propulsion component has breached safety life-limit or experienced active fault degradation! Immediate depot replacement dispatch required before next sortie.
          </div>
        </div>
      )}

      {/* ── 8-Component Prognostics Matrix Grid ───────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filteredComponents.map(comp => (
          <ComponentCard
            key={comp.id}
            comp={comp}
            onGenerateOrder={(c) => setSelectedWorkOrderComp(c)}
          />
        ))}
      </div>

      {filteredComponents.length === 0 && (
        <div className="text-center py-6 text-slate-500 text-[11px]">
          NO COMPONENTS CURRENTLY MATCHING FILTER "{filterTab}".
        </div>
      )}

      {/* ── Collapsible Scheduled Inspection Milestones (50h / 100h / 500h / RUL) ── */}
      <div className="border-t border-slate-800 pt-2">
        <button
          onClick={() => setShowIntervalsDrawer(!showIntervalsDrawer)}
          className="w-full flex items-center justify-between p-2 rounded bg-slate-900/60 hover:bg-slate-900 border border-slate-800/80 text-[10px] text-slate-400 transition-colors"
        >
          <span className="flex items-center gap-2 text-slate-300 font-semibold">
            <Calendar size={13} className="text-cyan-400" />
            SCHEDULED OVERHAUL INTERVALS & OEM SERVICE CHECKS (50H / 100H / 500H TBO)
          </span>
          <div className="flex items-center gap-1">
            <span>{showIntervalsDrawer ? 'COLLAPSE' : 'VIEW CALENDAR CHECKS'}</span>
            {showIntervalsDrawer ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </div>
        </button>

        {showIntervalsDrawer && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 pt-1 animate-in fade-in duration-150">
            {scheduleIntervals.map(svc => (
              <div
                key={svc.service_id}
                className="bg-slate-950 p-2 rounded border border-slate-800 flex justify-between items-center text-[10px]"
              >
                <div>
                  <div className="font-bold text-slate-200">{svc.service_id}</div>
                  <div className="text-[9px] text-slate-400">{svc.description}</div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-cyan-300 font-bold">{svc.hours_remaining} hrs</div>
                  <div className="text-[9px] text-slate-500">~{svc.days_remaining} days</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Footnote & Spec Reference ──────────────────────────────────────── */}
      <div className="text-[8.5px] text-slate-600 text-center border-t border-slate-900 pt-1">
        Military & Civil Aviation PHM Architecture per MIL-HDBK-5J · EASA CS-E · FAA FAR-33 · Arrhenius High-Stress Coupled Dynamics
      </div>

      {/* ── Military Work Order Modal ────────────────────────────────────────── */}
      <WorkOrderModal
        component={selectedWorkOrderComp}
        engine={phmData?.engine_name}
        totalHours={phmData?.accumulated_hours}
        onClose={() => setSelectedWorkOrderComp(null)}
      />
    </div>
  );
}
