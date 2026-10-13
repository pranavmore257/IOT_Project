import React from 'react';
import { X, BookOpen, Cpu, Mic, Zap, Activity, CheckCircle } from 'lucide-react';

export default function ModelInfoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-card w-full max-w-4xl max-h-[90vh] rounded-2xl overflow-hidden flex flex-col border border-slate-700 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-950 text-indigo-400 border border-indigo-700/50">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">
                AI Models & System Architecture (College Viva Manual)
              </h2>
              <p className="text-xs text-slate-400">
                Detailed technical specifications, training metrics, and examiner Q&A
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {/* Section 1: Vision Model (YOLOv8) */}
          <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
              <Cpu className="w-4 h-4" />
              <span>1. Computer Vision: Ultralytics YOLOv8n (Nano)</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">Model Architecture</span>
                <p className="font-bold text-white mt-0.5">YOLOv8n (3.2M params)</p>
              </div>
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">Inference Runtime</span>
                <p className="font-bold text-white mt-0.5">Auto (CUDA / CPU Fallback)</p>
              </div>
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">Target Classes</span>
                <p className="font-bold text-white mt-0.5">Car, Bike, Bus, Truck, Ambulance</p>
              </div>
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">Direction Estimation</span>
                <p className="font-bold text-white mt-0.5">Centroid ROI (N, S, E, W)</p>
              </div>
            </div>
            <p className="text-slate-400 leading-relaxed">
              <strong>Viva Explanation:</strong> YOLOv8 uses a CSPDarknet backbone with PAN-FPN neck and anchor-free decoupled head. We evaluate the bounding box centroid relative to 4 quadrant ROIs to classify approaching vehicle directions without needing complex GPS telemetry.
            </p>
          </div>

          {/* Section 2: Audio AI Classifier */}
          <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
              <Mic className="w-4 h-4" />
              <span>2. Audio AI Classifier: MFCC Feature Extraction + Random Forest</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">Audio Pipeline</span>
                <p className="font-bold text-white mt-0.5">16kHz Mono, 1.5s Chunks</p>
              </div>
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">Feature Extraction</span>
                <p className="font-bold text-white mt-0.5">20 MFCC Coefficients</p>
              </div>
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">Model Accuracy</span>
                <p className="font-bold text-emerald-400 mt-0.5">96.67% (Test Split)</p>
              </div>
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="text-slate-400">F1 Score</span>
                <p className="font-bold text-emerald-400 mt-0.5">96.63% (Macro Weighted)</p>
              </div>
            </div>
            <p className="text-slate-400 leading-relaxed">
              <strong>Viva Explanation:</strong> Audio signals from the laptop microphone are windowed with 50% overlap. Mel-Frequency Cepstral Coefficients (MFCCs) represent the short-term power spectrum on the non-linear human Mel scale. The Random Forest ensemble classifies ambulance sirens (alternating ~750Hz/960Hz tones), fire trucks, police sirens, heavy honking, accident impacts, and ambient traffic.
            </p>
          </div>

          {/* Section 3: Multimodal Decision Engine */}
          <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
              <Zap className="w-4 h-4" />
              <span>3. Multimodal Decision Engine & Fusion Rules</span>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono text-[11px] text-amber-200">
              EmergencyScore = (Audio_Weight × Audio_Conf) + (Video_Weight × Video_Conf)
            </div>
            <ul className="space-y-1.5 list-disc list-inside text-slate-300">
              <li><strong>Case 1 (Dual Confirmation):</strong> Both Audio Siren + Video Ambulance exceed threshold → Immediate Emergency Green Corridor on target direction.</li>
              <li><strong>Case 2 (Audio Only):</strong> Siren heard but camera does not see vehicle yet → Holds in "Possible Emergency" for 3.0s confirmation window to eliminate false sirens.</li>
              <li><strong>Case 3 (Video Only):</strong> Ambulance visible with silent siren → Confers lower-confidence priority green.</li>
              <li><strong>Case 4 (Accident Impact):</strong> Acoustic impact sound detected (high crest factor + broadband transient) → Safe all-RED hold.</li>
              <li><strong>Case 5 (Heavy Traffic):</strong> Vehicle density HIGH (11+ vehicles) → Extends green time dynamically from 10s to 20s.</li>
            </ul>
          </div>

          {/* Section 4: Software signal simulator */}
          <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm">
              <Activity className="w-4 h-4" />
              <span>4. Software 4-Way Signal Simulator</span>
            </div>
            <p className="text-slate-400 leading-relaxed">
              The software signal simulator receives the multimodal decision as structured <code className="text-indigo-300 font-mono">traffic/signal</code> state and renders the North, South, East, and West RED, YELLOW, GREEN outputs for demonstration. It includes the same timing and safe-clearance rules without requiring external hardware.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition"
          >
            Close Manual
          </button>
        </div>
      </div>
    </div>
  );
}
