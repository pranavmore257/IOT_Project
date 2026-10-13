import React, { useState } from 'react';
import { Camera, Car, Bike, Bus, Truck, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function LiveVideoFeed({ videoData }) {
  const [streamError, setStreamError] = useState(false);

  const counts = videoData?.counts || {};
  const totalVehicles = videoData?.vehicle_count || 0;
  const density = videoData?.density || 'LOW';
  const isEmergency = videoData?.ambulance_detected;
  const ambulanceConf = videoData?.ambulance_confidence || 0;
  const ambulanceDir = videoData?.ambulance_direction || 'NONE';
  const fps = videoData?.fps || 0;
  const infMs = videoData?.inference_ms || 0;
  const dirCounts = videoData?.direction_counts || {};

  const densityColors = {
    LOW: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
    MEDIUM: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
    HIGH: 'bg-rose-500/20 text-rose-400 border-rose-500/40'
  };

  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Camera className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-sm tracking-wider text-slate-200 uppercase">
            Live Traffic Camera (YOLOv8)
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${densityColors[density] || densityColors.LOW}`}>
            DENSITY: {density}
          </span>
          <span className="text-[11px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
            {fps} FPS | {infMs}ms
          </span>
        </div>
      </div>

      {/* Video Feed Window */}
      <div className="relative aspect-[4/3] bg-slate-950 rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center">
        {!streamError ? (
          <img
            src="/api/video/feed"
            alt="Live Traffic Video Feed"
            className="w-full h-full object-contain"
            onError={() => setStreamError(true)}
          />
        ) : (
          <div className="text-center p-4">
            <Camera className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="text-sm font-medium text-slate-300">Camera Feed Initializing / Reconnecting</p>
            <p className="text-xs text-slate-500 mt-1">Check webcam permissions or click to retry</p>
            <button
              onClick={() => setStreamError(false)}
              className="mt-3 px-3 py-1 bg-indigo-600/80 hover:bg-indigo-600 text-xs rounded transition"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Emergency Detection Banner */}
        {isEmergency && (
          <div className="absolute top-3 left-3 right-3 bg-rose-600/90 backdrop-blur-sm text-white px-3 py-1.5 rounded-md flex items-center justify-between text-xs font-semibold shadow-lg border border-rose-400/50 animate-pulse">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              <span>🚑 AMBULANCE VISUALLY DETECTED ({Math.round(ambulanceConf * 100)}%)</span>
            </div>
            <span className="bg-white/20 px-2 py-0.5 rounded">APPROACH: {ambulanceDir}</span>
          </div>
        )}
      </div>

      {/* Vehicle Count HUD Breakdown */}
      <div className="grid grid-cols-5 gap-2 text-center text-xs">
        <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/60">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <Car className="w-3.5 h-3.5 text-blue-400" />
            <span>Cars</span>
          </div>
          <span className="text-base font-bold text-white">{counts.car || 0}</span>
        </div>

        <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/60">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <Bike className="w-3.5 h-3.5 text-amber-400" />
            <span>Bikes</span>
          </div>
          <span className="text-base font-bold text-white">{counts.motorcycle || 0}</span>
        </div>

        <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/60">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <Bus className="w-3.5 h-3.5 text-purple-400" />
            <span>Buses</span>
          </div>
          <span className="text-base font-bold text-white">{counts.bus || 0}</span>
        </div>

        <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/60">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <Truck className="w-3.5 h-3.5 text-orange-400" />
            <span>Trucks</span>
          </div>
          <span className="text-base font-bold text-white">{counts.truck || 0}</span>
        </div>

        <div className={`p-2 rounded-lg border ${
          isEmergency ? 'bg-rose-950/60 border-rose-500/50' : 'bg-slate-800/60 border-slate-700/60'
        }`}>
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-rose-400" />
            <span>Ambulance</span>
          </div>
          <span className={`text-base font-bold ${isEmergency ? 'text-rose-400 animate-pulse' : 'text-white'}`}>
            {counts.ambulance || (isEmergency ? 1 : 0)}
          </span>
        </div>
      </div>

      {/* ROI Directional Distribution Bar */}
      <div className="bg-slate-900/60 px-3 py-2 rounded-lg border border-slate-800 text-[11px] flex items-center justify-between text-slate-400">
        <span className="font-medium text-slate-300">ROI Breakdown:</span>
        <span>North: <strong className="text-white">{dirCounts.NORTH || 0}</strong></span>
        <span>South: <strong className="text-white">{dirCounts.SOUTH || 0}</strong></span>
        <span>East: <strong className="text-white">{dirCounts.EAST || 0}</strong></span>
        <span>West: <strong className="text-white">{dirCounts.WEST || 0}</strong></span>
        <span className="text-slate-200">Total: <strong className="text-emerald-400 font-bold">{totalVehicles}</strong></span>
      </div>
    </div>
  );
}
