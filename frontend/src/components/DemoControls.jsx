import React, { useState } from 'react';
import { Play, RotateCcw, AlertTriangle, Flame, Shield, Car, Volume2, Video } from 'lucide-react';
import { triggerDemoScenario } from '../services/api';

export default function DemoControls({ isDemoMode, onTrigger }) {
  const [loadingScenario, setLoadingScenario] = useState(null);
  const [activeScenarioName, setActiveScenarioName] = useState('LIVE_SENSORS');
  const [scenarioNote, setScenarioNote] = useState('Running on live sensors. Select a scenario below to test demonstration cases.');

  const handleTrigger = async (scenario, label, note) => {
    setLoadingScenario(scenario);
    try {
      await triggerDemoScenario(scenario);
      setActiveScenarioName(label);
      setScenarioNote(note);
      if (onTrigger) onTrigger();
    } catch (err) {
      console.error('Demo trigger error:', err);
    } finally {
      setLoadingScenario(null);
    }
  };

  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Play className="w-5 h-5 text-rose-400" />
          <h2 className="font-semibold text-sm tracking-wider text-slate-200 uppercase">
            College Presentation Demo Mode
          </h2>
        </div>
        <div className="flex items-center gap-2">
          {isDemoMode ? (
            <span className="px-2.5 py-0.5 rounded text-xs font-black bg-rose-600 text-white animate-pulse border border-rose-400">
              DEMO MODE
            </span>
          ) : (
            <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-500/40">
              LIVE SENSORS
            </span>
          )}
        </div>
      </div>

      {/* Presentation Scenario Explanation Box */}
      <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-800 text-xs text-slate-300 flex flex-col gap-1">
        <div className="flex items-center justify-between font-semibold text-white">
          <span>Active Scenario: <strong className="text-amber-400">{activeScenarioName}</strong></span>
          <span className="text-[10px] text-slate-400">For Viva Presentation</span>
        </div>
        <p className="text-[11px] text-slate-400">
          {scenarioNote}
        </p>
      </div>

      {/* Demo Action Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 text-xs">
        {/* Ambulance Case 1 (MAIN DEMO) */}
        <button
          onClick={() => handleTrigger(
            'ambulance',
            'Ambulance Dual Confirmation (Case 1)',
            '⭐ MAIN DEMO: Combines Ambulance Siren (95%) + Visual Ambulance (92%) → Multimodal Fusion (93.5%) → Activates the NORTH Green Corridor in the software signal simulator.'
          )}
          disabled={loadingScenario === 'ambulance'}
          className="p-2.5 rounded-lg bg-rose-950/80 hover:bg-rose-900 border border-rose-500/50 text-rose-200 font-bold flex flex-col items-center gap-1 transition shadow-sm hover:scale-[1.02]"
        >
          <span className="text-base">🚑</span>
          <span>Ambulance (Dual AI)</span>
          <span className="text-[9px] text-rose-400 font-normal">⭐ Case 1 Green Corridor</span>
        </button>

        {/* Heavy Traffic Adaptive Case 5 */}
        <button
          onClick={() => handleTrigger(
            'heavy-traffic',
            'Heavy Congestion Adaptive Green (Case 5)',
            'Case 5: High traffic density (14 vehicles, heavy honking) → Decision Engine automatically extends green duration from 10s to 20s.'
          )}
          disabled={loadingScenario === 'heavy-traffic'}
          className="p-2.5 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-500/50 text-indigo-200 font-bold flex flex-col items-center gap-1 transition shadow-sm hover:scale-[1.02]"
        >
          <Car className="w-4 h-4 text-indigo-400" />
          <span>Heavy Traffic</span>
          <span className="text-[9px] text-indigo-400 font-normal">Adaptive Green (20s)</span>
        </button>

        {/* Fire Truck */}
        <button
          onClick={() => handleTrigger(
            'fire-truck',
            'Fire Truck Siren & Visual Priority',
            'Case 1 Variant: Fire Truck siren and visual vehicle detected from East approach → Initiates EAST Emergency Green Corridor.'
          )}
          disabled={loadingScenario === 'fire-truck'}
          className="p-2.5 rounded-lg bg-orange-950/80 hover:bg-orange-900 border border-orange-500/50 text-orange-200 font-bold flex flex-col items-center gap-1 transition shadow-sm hover:scale-[1.02]"
        >
          <Flame className="w-4 h-4 text-orange-400" />
          <span>Fire Truck</span>
          <span className="text-[9px] text-orange-400 font-normal">Emergency Priority</span>
        </button>

        {/* Police Siren */}
        <button
          onClick={() => handleTrigger(
            'police',
            'Police Siren & Visual Priority',
            'Police rapid wail siren and vehicle detected from West approach → Initiates WEST Emergency Green Corridor.'
          )}
          disabled={loadingScenario === 'police'}
          className="p-2.5 rounded-lg bg-blue-950/80 hover:bg-blue-900 border border-blue-500/50 text-blue-200 font-bold flex flex-col items-center gap-1 transition shadow-sm hover:scale-[1.02]"
        >
          <Shield className="w-4 h-4 text-blue-400" />
          <span>Police Siren</span>
          <span className="text-[9px] text-blue-400 font-normal">Emergency Priority</span>
        </button>

        {/* Accident Case 4 */}
        <button
          onClick={() => handleTrigger(
            'accident',
            'Accident Impact Sound (Case 4)',
            'Case 4: Sudden crash/impact acoustic signature detected (94%) → Triggers Accident Alert & Immediate Safe All-RED Hold.'
          )}
          disabled={loadingScenario === 'accident'}
          className="p-2.5 rounded-lg bg-amber-950/80 hover:bg-amber-900 border border-amber-500/50 text-amber-200 font-bold flex flex-col items-center gap-1 transition shadow-sm hover:scale-[1.02]"
        >
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>Accident Sound</span>
          <span className="text-[9px] text-amber-400 font-normal">Case 4 Safe Hold</span>
        </button>

        {/* Audio Only Siren Case 2 */}
        <button
          onClick={() => handleTrigger(
            'audio-only',
            'Audio Siren Only (Case 2 False Alarm Prevention)',
            'Case 2: Siren heard, but no visual ambulance visible on camera → Enters Possible Emergency, waiting for camera confirmation.'
          )}
          disabled={loadingScenario === 'audio-only'}
          className="p-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-medium flex flex-col items-center gap-1 transition"
        >
          <Volume2 className="w-4 h-4 text-emerald-400" />
          <span>Audio Siren Only</span>
          <span className="text-[9px] text-slate-400 font-normal">Verification Hold</span>
        </button>

        {/* Video Only Ambulance Case 3 */}
        <button
          onClick={() => handleTrigger(
            'video-only',
            'Visual Ambulance Only (Case 3 Silent Siren)',
            'Case 3: Ambulance visible on webcam with silent siren → Confers lower-confidence emergency priority.'
          )}
          disabled={loadingScenario === 'video-only'}
          className="p-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-medium flex flex-col items-center gap-1 transition"
        >
          <Video className="w-4 h-4 text-cyan-400" />
          <span>Video Only</span>
          <span className="text-[9px] text-slate-400 font-normal">Silent Siren</span>
        </button>

        {/* Normal / Reset */}
        <button
          onClick={() => handleTrigger(
            'reset',
            'Live Sensory Reset',
            'Reset all simulation overrides. Returned cleanly to real-time webcam and microphone inputs.'
          )}
          disabled={loadingScenario === 'reset'}
          className="p-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 font-bold flex flex-col items-center gap-1 transition shadow-sm"
        >
          <RotateCcw className="w-4 h-4 text-slate-300" />
          <span>Reset to Live</span>
          <span className="text-[9px] text-slate-400 font-normal">Clear Overrides</span>
        </button>
      </div>
    </div>
  );
}
