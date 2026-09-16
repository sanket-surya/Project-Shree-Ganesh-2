import React, { useState } from 'react';
import { Play, Pause, FastForward, Film, Download } from 'lucide-react';

export default function MissionReplayBar({
  isReplaying,
  onToggleReplay,
  onExportReport,
  replayPercent = 100,
  onScrubReplay,
  historyCount = 0,
  speed = 1,
  onChangeSpeed,
}) {
  return (
    <div className="gcs-card p-2 px-4 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
      {/* Playback Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={onToggleReplay}
          className={`tactical-btn text-xs ${isReplaying ? 'active bg-amber-500 text-black font-bold' : ''}`}
          title="Play / Pause Historical Flight Telemetry Replay"
        >
          {isReplaying ? <Pause size={13} /> : <Play size={13} />}
          {isReplaying ? 'PAUSE REPLAY' : (replayPercent < 100 ? 'RESUME REPLAY' : 'REPLAY BLACK BOX')}
        </button>

        {replayPercent < 100 && (
          <button
            onClick={() => onScrubReplay && onScrubReplay(100)}
            className="tactical-btn text-xs text-cyan-300 border-cyan-500/50"
            title="Jump back to live 20Hz stream"
          >
            GO LIVE (T-0)
          </button>
        )}

        <button
          onClick={() => onChangeSpeed && onChangeSpeed(speed === 1 ? 2 : speed === 2 ? 5 : 1)}
          className="tactical-btn text-xs"
        >
          <FastForward size={13} />
          {speed}x SPEED
        </button>
      </div>

      {/* Scrubbing Timeline Bar */}
      <div className="flex-1 min-w-[220px] flex items-center gap-3">
        <span className="text-slate-400 text-[11px] whitespace-nowrap flex items-center gap-1.5">
          <Film size={12} className={replayPercent < 100 ? "text-amber-400 animate-pulse" : "text-cyan-400"} />
          BLACK BOX ({historyCount} FRAMES):
        </span>
        <input
          type="range"
          min="0"
          max="100"
          value={replayPercent}
          onChange={(e) => onScrubReplay && onScrubReplay(Number(e.target.value))}
          className="w-full h-2 bg-slate-700 accent-cyan-400 rounded cursor-pointer transition-all"
        />
        <span className={`font-bold text-[11px] whitespace-nowrap ${replayPercent === 100 ? 'text-emerald-400' : 'text-amber-400'}`}>
          {replayPercent === 100 ? '● LIVE (T-00:00)' : `HISTORICAL (-${Math.round((100 - replayPercent) * 0.6)}s)`}
        </span>
      </div>

      {/* Export Report Action */}
      <div className="flex items-center gap-2">
        <button
          onClick={onExportReport}
          className="tactical-btn active bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs"
        >
          <Download size={13} />
          EXPORT AIRWORTHINESS REPORT
        </button>
      </div>
    </div>
  );
}
