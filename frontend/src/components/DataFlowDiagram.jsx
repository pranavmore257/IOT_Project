import React from 'react';
import { Network, Camera, Mic, Cpu, Zap, Activity, ArrowRight, ArrowDown } from 'lucide-react';

export default function DataFlowDiagram({ system, isEmergency, mode }) {
  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-sm tracking-wider text-slate-200 uppercase">
            Live Multimodal System Data Pipeline
          </h2>
        </div>
        <span className="text-[11px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
          End-to-End Software Flow
        </span>
      </div>

      {/* Interactive Flow Diagram */}
      <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col gap-4">
        {/* Row 1: Sensors -> AI Inference */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Vision Pipeline Branch */}
          <div className="bg-slate-900/90 p-3 rounded-lg border border-indigo-500/30 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-indigo-950 text-indigo-400 border border-indigo-700/50">
                <Camera className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">Webcam</p>
                <p className="text-[10px] text-slate-400">OpenCV Capture</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-indigo-400" />
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-indigo-950 text-indigo-400 border border-indigo-700/50">
                <Cpu className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">YOLOv8n</p>
                <p className="text-[10px] text-slate-400">Vehicles & Density</p>
              </div>
            </div>
          </div>

          {/* Audio Pipeline Branch */}
          <div className="bg-slate-900/90 p-3 rounded-lg border border-emerald-500/30 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-700/50">
                <Mic className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">Microphone</p>
                <p className="text-[10px] text-slate-400">Audio Ring Buffer</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-emerald-400" />
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-700/50">
                <Cpu className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">Audio AI</p>
                <p className="text-[10px] text-slate-400">MFCC + Classifier</p>
              </div>
            </div>
          </div>
        </div>

        {/* Convergence Connector */}
        <div className="flex items-center justify-center -my-2 text-slate-500">
          <ArrowDown className="w-5 h-5 animate-bounce" />
        </div>

        {/* Row 2: Multimodal Decision Engine */}
        <div className={`p-3.5 rounded-xl border text-center transition-all ${
          isEmergency 
            ? 'bg-rose-950/60 border-rose-500 shadow-lg shadow-rose-900/30' 
            : 'bg-slate-900/90 border-amber-500/40'
        }`}>
          <div className="flex items-center justify-center gap-2 mb-1">
            <Zap className={`w-5 h-5 ${isEmergency ? 'text-rose-400 animate-pulse' : 'text-amber-400'}`} />
            <span className="font-bold text-sm tracking-wide text-white">
              MULTIMODAL DECISION ENGINE (AI FUSION)
            </span>
          </div>
          <p className="text-xs text-slate-300">
            Fuses Audio Siren/Crash + Video BBoxes + Vehicle Density → Generates Signal Commands
          </p>
        </div>

        {/* Convergence Connector */}
        <div className="flex items-center justify-center -my-2 text-slate-500">
          <ArrowDown className="w-5 h-5 animate-bounce" />
        </div>

        {/* Row 3: Software decision output */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-center">
          <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex flex-col items-center gap-1.5">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold text-white">Signal Decision</span>
            <span className="text-[10px] text-slate-400">traffic/signal JSON</span>
          </div>

          <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex flex-col items-center gap-1.5">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-bold text-white">Signal Simulator</span>
            <span className="text-[10px] text-slate-400">Software state machine</span>
          </div>

          <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex flex-col items-center gap-1.5">
            <Activity className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-bold text-white">Demo Visualization</span>
            <span className="text-[10px] text-slate-400">4-way signal board</span>
          </div>
        </div>
      </div>
    </div>
  );
}
