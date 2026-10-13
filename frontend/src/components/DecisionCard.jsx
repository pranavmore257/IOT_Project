import React from 'react';
import { Cpu, Zap, ShieldAlert, ArrowRight, CheckCircle2, Clock } from 'lucide-react';

export default function DecisionCard({ decisionData, videoData, audioData }) {
  const mode = decisionData?.mode || 'NORMAL';
  const priority = decisionData?.priority || 'LOW';
  const score = decisionData?.emergency_score || 0.0;
  const targetDir = decisionData?.target_direction || 'NONE';
  const reason = decisionData?.reason || 'Routine traffic operation';
  const adaptiveGreen = decisionData?.adaptive_green_seconds || 10;
  const fusion = decisionData?.fusion_math || {
    audio_weight: 0.5,
    video_weight: 0.5,
    audio_score: 0.0,
    video_score: 0.0,
    threshold: 0.75
  };

  const isEmergency = mode === 'EMERGENCY';
  const isAccident = mode === 'ACCIDENT_ALERT';
  const isAdaptive = mode === 'ADAPTIVE';

  const modeBadges = {
    EMERGENCY: 'bg-rose-500 text-white animate-pulse',
    ACCIDENT_ALERT: 'bg-amber-500 text-slate-950 font-bold',
    ADAPTIVE: 'bg-indigo-600 text-white',
    NORMAL: 'bg-emerald-600 text-white'
  };

  return (
    <div className={`glass-card rounded-xl p-4 flex flex-col gap-3 transition-all ${
      isEmergency ? 'ring-2 ring-rose-500/60 shadow-xl shadow-rose-900/30' : ''
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-400" />
          <h2 className="font-semibold text-sm tracking-wider text-slate-200 uppercase">
            Multimodal Decision Engine
          </h2>
        </div>
        <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${modeBadges[mode] || modeBadges.NORMAL}`}>
          MODE: {mode}
        </span>
      </div>

      {/* Decision Summary Card */}
      <div className={`p-3.5 rounded-xl border flex flex-col gap-2 ${
        isEmergency
          ? 'bg-rose-950/50 border-rose-500/60'
          : isAccident
          ? 'bg-amber-950/50 border-amber-500/60'
          : 'bg-slate-900/80 border-slate-800'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400">Current Action</span>
            <h3 className="text-lg font-black text-white flex items-center gap-2 mt-0.5">
              {isEmergency && <ShieldAlert className="w-5 h-5 text-rose-400 animate-bounce" />}
              {isEmergency 
                ? `🚨 GREEN CORRIDOR (${targetDir})` 
                : isAccident 
                ? '🛑 INTERSECTION SAFETY HOLD' 
                : isAdaptive 
                ? `🚦 EXTENDED GREEN (${adaptiveGreen}s)` 
                : '🟢 NORMAL 4-WAY ROTATION'}
            </h3>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400">Priority Level</span>
            <p className={`text-sm font-bold mt-0.5 ${
              priority === 'HIGH' || priority === 'CRITICAL' ? 'text-rose-400' : 'text-slate-200'
            }`}>
              {priority}
            </p>
          </div>
        </div>

        <p className="text-xs text-slate-300 bg-slate-950/50 p-2 rounded border border-slate-800/80">
          <strong className="text-indigo-300">Reason:</strong> {reason}
        </p>
      </div>

      {/* Multimodal Fusion Math Breakdown */}
      <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col gap-2 text-xs">
        <div className="flex items-center justify-between text-slate-300 font-medium">
          <span>Multimodal Confidence Fusion Formula</span>
          <span className="text-[11px] text-slate-400">Threshold: ≥ 75%</span>
        </div>

        <div className="bg-slate-950 p-2.5 rounded font-mono text-[11px] text-slate-300 border border-slate-800/80 flex items-center justify-between">
          <div>
            Score = (<span className="text-emerald-400">{fusion.audio_weight}</span> × <span className="text-amber-300">{Math.round(fusion.audio_score * 100)}%</span>) + (<span className="text-emerald-400">{fusion.video_weight}</span> × <span className="text-cyan-300">{Math.round(fusion.video_score * 100)}%</span>)
          </div>
          <div className={`font-bold text-sm ${score >= 0.75 ? 'text-rose-400' : 'text-emerald-400'}`}>
            = {Math.round(score * 100)}%
          </div>
        </div>

        {/* Emergency Score Meter */}
        <div>
          <div className="flex justify-between text-[10px] text-slate-400 mb-1">
            <span>Emergency Probability Meter</span>
            <span className="font-semibold text-slate-200">{Math.round(score * 100)}%</span>
          </div>
          <div className="relative w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                score >= 0.75 ? 'bg-rose-500' : score >= 0.4 ? 'bg-amber-400' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, Math.max(0, score * 100))}%` }}
            />
            {/* 75% Threshold Marker Line */}
            <div className="absolute top-0 bottom-0 left-[75%] w-0.5 bg-white shadow-sm" />
          </div>
        </div>
      </div>

      {/* Decision Engine Specs Footer */}
      <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-indigo-400" />
          <span>Adaptive Green: <strong className="text-white">{adaptiveGreen}s</strong></span>
        </div>
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Yellow Safety Interval: <strong className="text-white">3s</strong></span>
        </div>
      </div>
    </div>
  );
}
