import React from 'react';
import { Camera, Mic, Cpu, Activity, AlertCircle } from 'lucide-react';

export default function SystemStatusBar({ system, isDemoMode }) {
  const isCamera = system?.camera_connected;
  const isMic = system?.microphone_connected;

  return (
    <div className="w-full bg-slate-900/90 border-b border-slate-800 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs">
      {/* Brand & Subtitle */}
      <div className="flex items-center gap-3">
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
        <div>
          <span className="font-bold text-white text-sm tracking-wide">
            SMART ACOUSTIC & VISION TRAFFIC SIGNAL
          </span>
          <span className="hidden md:inline-block ml-2 text-slate-400 text-xs">
            | Multimodal AI Software Demo
          </span>
        </div>
      </div>

      {/* Sensor and software badges */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Webcam */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-medium ${
          isCamera 
            ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300' 
            : 'bg-amber-950/60 border-amber-500/40 text-amber-300'
        }`}>
          <Camera className="w-3.5 h-3.5" />
          <span>Webcam: {isCamera ? 'LIVE' : 'SIMULATED'}</span>
        </div>

        {/* Microphone */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-medium ${
          isMic 
            ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300' 
            : 'bg-amber-950/60 border-amber-500/40 text-amber-300'
        }`}>
          <Mic className="w-3.5 h-3.5" />
          <span>Mic: {isMic ? 'LIVE' : 'SIMULATED'}</span>
        </div>

        {/* AI Models */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border bg-cyan-950/60 border-cyan-500/40 text-cyan-300 font-medium">
          <Cpu className="w-3.5 h-3.5" />
          <span>YOLOv8n + Audio AI</span>
        </div>

        <div className="flex items-center gap-1.5 rounded-md border border-cyan-500/40 bg-cyan-950/60 px-2.5 py-1 font-medium text-cyan-300">
          <Activity className="h-3.5 w-3.5" />
          <span>Signal Output: SOFTWARE SIM</span>
        </div>

        {/* Demo Mode Pill */}
        {isDemoMode && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-600/90 text-white font-bold animate-pulse">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>DEMO MODE ACTIVE</span>
          </div>
        )}
      </div>
    </div>
  );
}
