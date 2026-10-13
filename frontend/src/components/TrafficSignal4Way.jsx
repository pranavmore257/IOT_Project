import React from 'react';
import { Compass, Cpu } from 'lucide-react';

function SignalHead({ direction, currentLight, label }) {
  const isRed = currentLight === 'RED';
  const isYellow = currentLight === 'YELLOW';
  const isGreen = currentLight === 'GREEN';

  return (
    <div className="flex flex-col items-center bg-slate-900/90 p-2.5 rounded-xl border border-slate-700 shadow-md">
      <span className="text-[11px] font-bold tracking-wider text-slate-300 uppercase mb-1.5">
        {label || direction}
      </span>
      {/* 3-Lamp Traffic Signal Housing */}
      <div className="bg-black/90 p-1.5 rounded-lg border border-slate-700/80 flex flex-col gap-1.5 shadow-inner">
        {/* Red Lamp */}
        <div
          className={`w-6 h-6 rounded-full transition-all duration-200 ${
            isRed
              ? 'bg-rose-500 shadow-[0_0_12px_rgba(244,63,94,0.9)] animate-pulse'
              : 'bg-rose-950/40 border border-rose-900/30'
          }`}
        />
        {/* Yellow Lamp */}
        <div
          className={`w-6 h-6 rounded-full transition-all duration-200 ${
            isYellow
              ? 'bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.9)] animate-pulse'
              : 'bg-amber-950/40 border border-amber-900/30'
          }`}
        />
        {/* Green Lamp */}
        <div
          className={`w-6 h-6 rounded-full transition-all duration-200 ${
            isGreen
              ? 'bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.9)] animate-pulse'
              : 'bg-emerald-950/40 border border-emerald-900/30'
          }`}
        />
      </div>
      <span className={`text-[10px] font-bold mt-1.5 px-1.5 py-0.5 rounded ${
        isGreen ? 'text-emerald-400 bg-emerald-950/60' : isYellow ? 'text-amber-400 bg-amber-950/60' : 'text-rose-400 bg-rose-950/60'
      }`}>
        {currentLight}
      </span>
    </div>
  );
}

export default function TrafficSignal4Way({ signalState }) {
  const signals = signalState?.signals || {
    NORTH: 'GREEN',
    SOUTH: 'GREEN',
    EAST: 'RED',
    WEST: 'RED',
  };
  const remainingSec = signalState?.remaining_seconds ?? 10;
  const stateName = signalState?.state || 'NS_GREEN';
  const mode = signalState?.mode || 'NORMAL';

  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Compass className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-sm tracking-wider text-slate-200 uppercase">
            4-Way Intersection Signal State
          </h2>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
            {stateName}
          </span>
          <span className="font-mono font-bold text-amber-400 bg-amber-950/50 border border-amber-500/40 px-2.5 py-0.5 rounded text-sm">
            {remainingSec}s
          </span>
        </div>
      </div>

      {/* 4-Way Cross Intersection Graphical Visualization */}
      <div className="relative aspect-square max-w-[340px] mx-auto w-full bg-slate-950 rounded-xl border border-slate-800 p-3 flex flex-col justify-between items-center shadow-inner overflow-hidden">
        {/* Road Layout Background Cross */}
        <div className="absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-24 bg-slate-900 border-x border-slate-800" />
        <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-24 bg-slate-900 border-y border-slate-800" />

        {/* Center Intersection Box with Countdown */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10 w-20 h-20 rounded-xl bg-slate-900/90 border border-slate-700 flex flex-col items-center justify-center shadow-2xl backdrop-blur-sm">
          <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Timer</span>
          <span className="text-2xl font-black font-mono text-amber-400">{remainingSec}</span>
          <span className="text-[9px] text-slate-500 uppercase">{mode}</span>
        </div>

        {/* NORTH Signal */}
        <div className="z-10">
          <SignalHead direction="NORTH" currentLight={signals.NORTH} label="North (GPIO 23/22/21)" />
        </div>

        {/* MIDDLE ROW: WEST & EAST */}
        <div className="w-full flex items-center justify-between z-10 px-2">
          <SignalHead direction="WEST" currentLight={signals.WEST} label="West (GPIO 0/2/15)" />
          <SignalHead direction="EAST" currentLight={signals.EAST} label="East (GPIO 17/16/4)" />
        </div>

        {/* SOUTH Signal */}
        <div className="z-10">
          <SignalHead direction="SOUTH" currentLight={signals.SOUTH} label="South (GPIO 19/18/5)" />
        </div>
      </div>

      {/* Software output footer */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
        <span className="flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          Software signal simulator: Synced
        </span>
        <span className="text-slate-500">Output: traffic/signal state</span>
      </div>
    </div>
  );
}
