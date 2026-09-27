import React, { useEffect, useRef } from 'react';
import { Activity } from 'lucide-react';

const HISTORY = 120; // points to show

export default function VibrationWaterfall({ telemetry }) {
  const canvasRef    = useRef(null);
  const historyRef   = useRef([]);
  const animFrameRef = useRef(null);
  const phaseRef     = useRef(0);

  const overallG = telemetry?.state?.overall_vibration_g || 1.45;

  // Accumulate real telemetry values
  useEffect(() => {
    historyRef.current.push(overallG);
    if (historyRef.current.length > HISTORY) historyRef.current.shift();
  }, [overallG]);

  // Status
  const getStatus = (g) => {
    if (g < 1.8) return { label: 'NOMINAL',   color: '#10b981', glow: 'rgba(16,185,129,0.5)' };
    if (g < 2.8) return { label: 'ELEVATED',  color: '#f59e0b', glow: 'rgba(245,158,11,0.5)' };
    return             { label: 'CRITICAL',   color: '#ef4444', glow: 'rgba(239,68,68,0.5)'  };
  };

  // Animate oscilloscope
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // ── Retina/4K fix: scale canvas to devicePixelRatio ──────────────────
    const setupCanvas = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.parentElement?.getBoundingClientRect();
      const cssW = rect ? rect.width : 400;
      const cssH = 130;
      canvas.width  = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      canvas.style.width  = `${cssW}px`;
      canvas.style.height = `${cssH}px`;
      ctx.scale(dpr, dpr);
      return { W: cssW, H: cssH };
    };

    let { W, H } = setupCanvas();

    const draw = () => {
      // Recalc in case resize
      W = canvas.width  / (window.devicePixelRatio || 1);
      H = canvas.height / (window.devicePixelRatio || 1);
      const PAD = { top: 14, right: 10, bottom: 18, left: 36 };
      const cW = W - PAD.left - PAD.right;
      const cH = H - PAD.top  - PAD.bottom;
      const midY = PAD.top + cH / 2;

      const G_RANGE = 2.0; // ±1.0g around center shown
      const toY = (g) => midY - ((g - overallG) / G_RANGE) * cH;

      // ── Background ───────────────────────────────────────
      ctx.fillStyle = '#020608';
      ctx.fillRect(0, 0, W, H);

      // CRT scanline effect
      for (let y = 0; y < H; y += 3) {
        ctx.fillStyle = 'rgba(0,0,0,0.18)';
        ctx.fillRect(0, y, W, 1);
      }

      // ── Grid (oscilloscope-style) ────────────────────────
      const COLS = 10, ROWS = 6;
      ctx.strokeStyle = 'rgba(0,255,100,0.08)';
      ctx.lineWidth = 0.5;
      ctx.setLineDash([]);
      for (let i = 0; i <= COLS; i++) {
        const x = PAD.left + (i / COLS) * cW;
        ctx.beginPath(); ctx.moveTo(x, PAD.top); ctx.lineTo(x, PAD.top + cH); ctx.stroke();
      }
      for (let i = 0; i <= ROWS; i++) {
        const y = PAD.top + (i / ROWS) * cH;
        ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + cW, y); ctx.stroke();
      }

      // Centre tick marks (minor grid)
      ctx.strokeStyle = 'rgba(0,255,100,0.05)';
      for (let i = 0; i <= COLS * 5; i++) {
        const x = PAD.left + (i / (COLS * 5)) * cW;
        ctx.beginPath(); ctx.moveTo(x, midY - 3); ctx.lineTo(x, midY + 3); ctx.stroke();
      }

      // ── Y-axis labels ─────────────────────────────────────
      const st = getStatus(overallG);
      ctx.font = '8px monospace';
      ctx.textAlign = 'right';
      [overallG + 1.0, overallG + 0.5, overallG, overallG - 0.5, overallG - 1.0].forEach((g, i) => {
        const y = PAD.top + (i / 4) * cH;
        ctx.fillStyle = 'rgba(0,220,80,0.55)';
        ctx.fillText(`${g.toFixed(1)}`, PAD.left - 3, y + 3);
      });

      // ── X-axis label ──────────────────────────────────────
      ctx.fillStyle = 'rgba(0,200,70,0.4)';
      ctx.textAlign = 'left';
      ctx.fillText('TIME →', PAD.left, H - 4);
      ctx.textAlign = 'right';
      ctx.fillText('g-FORCE', PAD.left - 2, PAD.top - 2);

      // ── Zero line (centre) ────────────────────────────────
      ctx.strokeStyle = 'rgba(0,255,100,0.18)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(PAD.left, midY);
      ctx.lineTo(PAD.left + cW, midY);
      ctx.stroke();
      ctx.setLineDash([]);

      // ── Build waveform from real data ─────────────────────
      const data = historyRef.current;
      const pts  = [];

      // Smooth the data using rolling avg to avoid jagged spikes
      const smoothed = data.map((v, i) => {
        const w = 3;
        const slice = data.slice(Math.max(0, i - w), i + w + 1);
        return slice.reduce((a, b) => a + b, 0) / slice.length;
      });

      // Add slight organic oscillation on top (simulates sensor noise)
      phaseRef.current += 0.12;
      smoothed.forEach((g, i) => {
        const x   = PAD.left + (i / (HISTORY - 1)) * cW;
        const noise = Math.sin(phaseRef.current + i * 0.4) * 0.04
                    + Math.sin(phaseRef.current * 1.7 + i * 0.9) * 0.02;
        const y = toY(g + noise);
        pts.push({ x, y });
      });

      if (pts.length < 2) { animFrameRef.current = requestAnimationFrame(draw); return; }

      // ── Glow passes ──────────────────────────────────────
      [
        { lw: 8, alpha: 0.08 },
        { lw: 4, alpha: 0.18 },
        { lw: 2, alpha: 0.55 },
        { lw: 1, alpha: 1.00 },
      ].forEach(({ lw, alpha }) => {
        ctx.beginPath();
        ctx.moveTo(pts[0].x, pts[0].y);
        for (let i = 1; i < pts.length; i++) {
          // Smooth curve
          const cpx = (pts[i - 1].x + pts[i].x) / 2;
          const cpy = (pts[i - 1].y + pts[i].y) / 2;
          ctx.quadraticCurveTo(pts[i - 1].x, pts[i - 1].y, cpx, cpy);
        }
        ctx.strokeStyle = st.color.replace(')', `,${alpha})`).replace('#', 'rgba(').replace('rgba(#', 'rgba(');

        // Hex to rgba manually
        const hex = st.color;
        const r = parseInt(hex.slice(1, 3), 16);
        const g2 = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        ctx.strokeStyle = `rgba(${r},${g2},${b},${alpha})`;
        ctx.lineWidth = lw;
        ctx.lineJoin = 'round';
        ctx.lineCap  = 'round';
        ctx.stroke();
      });

      // ── Live dot at end ───────────────────────────────────
      const last = pts[pts.length - 1];
      if (last) {
        // Outer glow ring
        const grad = ctx.createRadialGradient(last.x, last.y, 0, last.x, last.y, 10);
        const r2 = parseInt(st.color.slice(1, 3), 16);
        const g3 = parseInt(st.color.slice(3, 5), 16);
        const b2 = parseInt(st.color.slice(5, 7), 16);
        grad.addColorStop(0,   `rgba(${r2},${g3},${b2},0.8)`);
        grad.addColorStop(0.5, `rgba(${r2},${g3},${b2},0.2)`);
        grad.addColorStop(1,   `rgba(${r2},${g3},${b2},0)`);
        ctx.beginPath();
        ctx.arc(last.x, last.y, 10, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();
        // Solid dot
        ctx.beginPath();
        ctx.arc(last.x, last.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = st.color;
        ctx.fill();
      }

      // ── Screen edge vignette ──────────────────────────────
      const vgr = ctx.createRadialGradient(W/2, H/2, H*0.3, W/2, H/2, H*0.85);
      vgr.addColorStop(0, 'rgba(0,0,0,0)');
      vgr.addColorStop(1, 'rgba(0,0,0,0.55)');
      ctx.fillStyle = vgr;
      ctx.fillRect(0, 0, W, H);

      animFrameRef.current = requestAnimationFrame(draw);
    };

    animFrameRef.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animFrameRef.current);
  }, [overallG]);

  const st = getStatus(overallG);

  return (
    <div className="gcs-card p-3 flex flex-col gap-2">
      {/* Header */}
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <Activity size={15} style={{ color: st.color }} />
          VIBRATION OSCILLOSCOPE
        </span>
        <span
          className="text-[10px] font-bold px-2 py-0.5 rounded border font-mono"
          style={{ color: st.color, borderColor: st.color + '55', background: st.color + '15' }}
        >
          {overallG.toFixed(3)} G — {st.label}
        </span>
      </div>

      {/* Canvas */}
      <div
        className="relative rounded overflow-hidden"
        style={{ background: '#020608', border: `1px solid ${st.color}22`, boxShadow: `0 0 12px ${st.glow}` }}
      >
        <canvas
          ref={canvasRef}
          className="w-full block"
          style={{ height: '130px', display: 'block' }}
        />
        {/* CRT corner labels */}
        <div className="absolute top-1 left-10 text-[8px] font-mono" style={{ color: st.color + 'aa' }}>
          CH1 · 0.5g/DIV · 1s/DIV
        </div>
        <div className="absolute top-1 right-2 text-[8px] font-mono" style={{ color: st.color + 'aa' }}>
          AUTO
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between text-[9px] font-mono px-1">
        <span style={{ color: st.color }}>● LIVE</span>
        <span className="text-slate-500">TRIG: RISING EDGE</span>
        <span className="text-slate-500">BW: 20kHz</span>
        <span style={{ color: overallG >= 2.8 ? '#ef4444' : overallG >= 1.8 ? '#f59e0b' : '#10b981' }}>
          {overallG >= 2.8 ? '⚠ CRITICAL' : overallG >= 1.8 ? '△ ELEVATED' : '✓ NOMINAL'}
        </span>
      </div>
    </div>
  );
}
