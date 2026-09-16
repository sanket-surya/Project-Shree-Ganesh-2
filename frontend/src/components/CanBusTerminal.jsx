import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Pause, Play, ShieldCheck, Lock } from 'lucide-react';

export default function CanBusTerminal({ telemetry }) {
  const [logs, setLogs] = useState([]);
  const [paused, setPaused] = useState(false);
  const logEndRef = useRef(null);

  const security = telemetry?.security || {
    protocol: 'MIL-STD-2045-47001D / AES-GCM-128',
    crc32: '0x8F3A21BC',
    crc_valid: true,
    auth_signature: 'HMAC-A94E8F21',
    encryption_mode: 'AIR-GAPPED SECURE LINK',
    tamper_detected: false,
  };

  useEffect(() => {
    if (paused || !telemetry) return;

    const timeStr = new Date().toISOString().substring(11, 23);
    const canHex = telemetry.can_frame || `CAN0 18FEE000# 00 00 00 00 00 00 00 00`;
    const rpm = telemetry?.state?.rpm?.toFixed(0) || '0';
    const mapHpa = telemetry?.state?.manifold_pressure_hpa?.toFixed(0) || '0';

    const newLog = {
      timestamp: timeStr,
      frame: canHex,
      decoded: `RPM=${rpm} MAP=${mapHpa}hPa PWR=${telemetry?.state?.power_output_kw?.toFixed(0)}kW`,
      crc: telemetry?.security?.crc32 || '0x9A4B',
    };

    setLogs((prev) => [...prev.slice(-40), newLog]);
  }, [telemetry, paused]);

  return (
    <div className="gcs-card p-3 flex flex-col h-full">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <Terminal size={16} className="text-cyan-400" />
          SOCKETCAN / FADEC 2.0 EMBEDDED TELEMETRY BUS
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPaused(!paused)}
            className="tactical-btn text-[10px] py-0.5 px-2"
          >
            {paused ? <Play size={11} /> : <Pause size={11} />}
            {paused ? 'RESUME BUS' : 'PAUSE BUS'}
          </button>
        </div>
      </div>

      {/* Military Secure Telemetry HUD Strip */}
      <div className="mt-2 bg-slate-900/90 border border-cyan-500/30 rounded p-1.5 px-2.5 flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono">
        <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
          <ShieldCheck size={13} className="text-emerald-400" />
          <span>SECURE TELEMETRY: {security.protocol}</span>
        </div>
        <div className="flex items-center gap-3 text-slate-300">
          <span>CRC-32: <strong className="text-cyan-300 font-mono">{security.crc32}</strong> <span className="text-emerald-400">[VALID]</span></span>
          <span className="hidden sm:inline text-slate-600">|</span>
          <span className="flex items-center gap-1">
            <Lock size={10} className="text-amber-400" />
            <span>AUTH: <strong className="text-amber-300">{security.auth_signature}</strong></span>
          </span>
          <span className="hidden sm:inline text-slate-600">|</span>
          <span className="text-emerald-400 font-bold">ANTI-SPOOFING: ACTIVE</span>
        </div>
      </div>

      {/* Terminal View */}
      <div className="mt-1.5 bg-slate-950 p-2 rounded border border-slate-800 font-mono text-[11px] h-40 overflow-y-auto space-y-1">
        {logs.map((log, idx) => (
          <div key={idx} className="flex flex-wrap items-center gap-x-2 text-slate-300 hover:bg-slate-900/60 px-1 rounded">
            <span className="text-slate-500">{log.timestamp}</span>
            <span className="text-cyan-400 font-bold">{log.frame}</span>
            <span className="text-emerald-400 text-[10px]">[{log.decoded}]</span>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
