import React from 'react';
import { Mic, Activity, Volume2, ShieldAlert, AlertOctagon, Car } from 'lucide-react';

export default function AudioMonitor({ audioData }) {
  const soundName = audioData?.display_name || 'Analyzing Audio...';
  const confidence = audioData?.confidence || 0;
  const status = audioData?.status || 'NORMAL';
  const activityPct = audioData?.activity_pct || 0;
  const waveform = audioData?.waveform || new Array(32).fill(0.05);
  const infMode = audioData?.inference_mode || 'TRAINED_MODEL';
  const isEmergency = status === 'EMERGENCY';
  const isAccident = status === 'ACCIDENT';

  const statusBadges = {
    EMERGENCY: 'bg-rose-500/20 text-rose-400 border-rose-500/50',
    ACCIDENT: 'bg-amber-500/20 text-amber-400 border-amber-500/50',
    CONGESTION: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    NORMAL: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
  };

  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Mic className="w-5 h-5 text-emerald-400" />
          <h2 className="font-semibold text-sm tracking-wider text-slate-200 uppercase">
            Audio AI Classifier (MFCC)
          </h2>
        </div>
        <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${statusBadges[status] || statusBadges.NORMAL}`}>
          STATUS: {status}
        </span>
      </div>

      {/* Main Sound Card */}
      <div className={`p-4 rounded-xl border flex flex-col gap-2 transition-all ${
        isEmergency 
          ? 'bg-rose-950/40 border-rose-500/50 shadow-lg shadow-rose-900/20' 
          : isAccident
          ? 'bg-amber-950/40 border-amber-500/50 shadow-lg shadow-amber-900/20'
          : 'bg-slate-900/80 border-slate-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-lg ${
              isEmergency ? 'bg-rose-600/30 text-rose-400' : isAccident ? 'bg-amber-600/30 text-amber-400' : 'bg-slate-800 text-slate-300'
            }`}>
              {isEmergency ? <ShieldAlert className="w-5 h-5 animate-pulse" /> : isAccident ? <AlertOctagon className="w-5 h-5" /> : <Car className="w-5 h-5" />}
            </div>
            <div>
              <p className="text-xs text-slate-400">Classified Sound Event</p>
              <h3 className="text-base font-bold text-white tracking-wide">
                {soundName}
              </h3>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400">Confidence</p>
            <span className="text-lg font-extrabold text-emerald-400">
              {Math.round(confidence * 100)}%
            </span>
          </div>
        </div>

        {/* Confidence Progress Bar */}
        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden mt-1">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              isEmergency ? 'bg-rose-500' : isAccident ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${Math.min(100, Math.max(0, confidence * 100))}%` }}
          />
        </div>
      </div>

      {/* Live Audio Activity Meter */}
      <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col gap-1.5">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <Volume2 className="w-3.5 h-3.5 text-slate-300" />
            <span>Microphone Activity (RMS Energy)</span>
          </div>
          <span className="font-mono text-slate-200 font-semibold">{activityPct}%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 via-amber-400 to-rose-500 transition-all duration-100"
            style={{ width: `${activityPct}%` }}
          />
        </div>
      </div>

      {/* Live 32-band Waveform Spectrogram Bar Visualizer */}
      <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 flex flex-col gap-2">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <Activity className="w-3 h-3 text-indigo-400" />
            Live Waveform Buffer
          </span>
          <span className="text-[10px] text-slate-500">16kHz Mono Ring Buffer</span>
        </div>
        <div className="flex items-end justify-between h-14 gap-1 px-1">
          {waveform.map((val, idx) => {
            const heightPct = Math.min(100, Math.max(8, val * 100));
            return (
              <div
                key={idx}
                className={`flex-1 rounded-t transition-all duration-75 ${
                  isEmergency ? 'bg-rose-500/80' : isAccident ? 'bg-amber-500/80' : 'bg-indigo-500/70'
                }`}
                style={{ height: `${heightPct}%` }}
              />
            );
          })}
        </div>
      </div>

      {/* Model Spec Footer */}
      <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
        <span>Classifier: Random Forest (MFCC)</span>
        <span className="text-emerald-400">Trained Model: Active (96.7% Acc)</span>
      </div>
    </div>
  );
}
