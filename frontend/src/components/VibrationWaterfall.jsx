import React, { useEffect, useRef } from 'react';
import { Activity } from 'lucide-react';

const DEFAULT_FFT_PEAKS = [0.4, 0.9, 0.25, 0.55, 0.12, 0.08, 0.05, 0.03];

export default function VibrationWaterfall({ telemetry }) {
  const canvasRef = useRef(null);
  const fftHistoryRef = useRef([]);

  const overallG = telemetry?.state?.overall_vibration_g || 1.45;
  const fftPeaks = telemetry?.state?.fft_spectrum || DEFAULT_FFT_PEAKS;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Push new spectrum to waterfall history
    fftHistoryRef.current.unshift([...fftPeaks]);
    if (fftHistoryRef.current.length > 30) {
      fftHistoryRef.current.pop();
    }

    // Clear Canvas
    ctx.fillStyle = '#080c14';
    ctx.fillRect(0, 0, width, height);

    // Draw Frequency Grid & Labels
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.1)';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += width / 8) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Draw Waterfall Heatmap Rows
    const rowHeight = height / 30;
    fftHistoryRef.current.forEach((row, rIdx) => {
      const y = rIdx * rowHeight;
      const barWidth = width / row.length;

      row.forEach((amp, cIdx) => {
        const x = cIdx * barWidth;
        // Map amplitude to color
        let r = 0, g = 240, b = 255, a = 0.2;
        if (amp > 2.0) { r = 239; g = 68; b = 68; a = 0.9; }
        else if (amp > 1.2) { r = 245; g = 158; b = 11; a = 0.7; }
        else if (amp > 0.6) { r = 16; g = 185; b = 129; a = 0.5; }

        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a * (1 - rIdx / 32)})`;
        ctx.fillRect(x + 1, y, barWidth - 2, rowHeight - 1);
      });
    });

    // Draw Top Real-time FFT Peak Outline Curve
    ctx.beginPath();
    const barW = width / fftPeaks.length;
    fftPeaks.forEach((amp, idx) => {
      const x = idx * barW + barW / 2;
      const peakY = Math.max(10, height - (amp / 3.5) * height);
      if (idx === 0) ctx.moveTo(x, peakY);
      else ctx.lineTo(x, peakY);
    });
    ctx.strokeStyle = overallG > 2.5 ? '#ef4444' : '#00f0ff';
    ctx.lineWidth = 2;
    ctx.stroke();

  }, [fftPeaks, overallG]);

  const getVibStatus = (g) => {
    if (g < 1.8) return { text: 'NOMINAL (< 1.8G)', color: 'text-emerald-400', bg: 'bg-emerald-950/60 border-emerald-500/30' };
    if (g < 2.8) return { text: 'ELEVATED (1.8 - 2.8G)', color: 'text-amber-400', bg: 'bg-amber-950/60 border-amber-500/30' };
    return { text: 'CRITICAL VIBRATION (> 2.8G)', color: 'text-red-400', bg: 'bg-red-950/70 border-red-500/50 animate-pulse' };
  };

  const status = getVibStatus(overallG);

  return (
    <div className="gcs-card p-3 flex flex-col justify-between">
      <div className="gcs-card-header">
        <span className="flex items-center gap-2">
          <Activity size={16} className="text-cyan-400" />
          VIBRATION FFT SPECTRAL WATERFALL
        </span>
        <span className={`text-[10px] font-mono ${status.color} ${status.bg} border px-2 py-0.5 rounded`}>
          RMS: {overallG.toFixed(2)} G | {status.text}
        </span>
      </div>

      {/* Waterfall Canvas */}
      <div className="mt-2 relative rounded overflow-hidden border border-slate-800 bg-slate-950">
        <canvas
          ref={canvasRef}
          width={360}
          height={130}
          className="w-full h-32 block"
        />
        {/* Frequency Band Labels */}
        <div className="flex justify-between px-2 py-1 text-[9px] font-mono text-slate-400 bg-slate-900/90 border-t border-slate-800">
          <span>0.5X (Misfire)</span>
          <span>1X (Prop)</span>
          <span>2X (Crank)</span>
          <span>4X (Combust)</span>
          <span>&gt;1kHz (Knock)</span>
        </div>
      </div>
    </div>
  );
}
