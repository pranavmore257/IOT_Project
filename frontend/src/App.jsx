import React, { useState, useEffect } from 'react';
import SystemStatusBar from './components/SystemStatusBar';
import LiveVideoFeed from './components/LiveVideoFeed';
import AudioMonitor from './components/AudioMonitor';
import DecisionCard from './components/DecisionCard';
import TrafficSignal4Way from './components/TrafficSignal4Way';
import DataFlowDiagram from './components/DataFlowDiagram';
import DemoControls from './components/DemoControls';
import EventLogTable from './components/EventLogTable';
import ModelInfoModal from './components/ModelInfoModal';
import UploadDemoView from './components/UploadDemoView';
import { wsClient } from './services/websocket';
import { getSystemStatus } from './services/api';
import { BookOpen, GitBranch, LayoutDashboard, Radio, Sparkles, Upload } from 'lucide-react';

export default function App() {
  const [systemData, setSystemData] = useState({});
  const [videoData, setVideoData] = useState({});
  const [audioData, setAudioData] = useState({});
  const [decisionData, setDecisionData] = useState({});
  const [signalState, setSignalState] = useState({});
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeView, setActiveView] = useState('overview');

  useEffect(() => {
    // Initial fetch
    getSystemStatus().then(data => {
      setSystemData(data.system || {});
      setIsDemoMode(data.demo_mode || false);
    }).catch(() => {});

    // Connect WebSocket
    wsClient.connect();
    const unsubscribe = wsClient.subscribe((payload) => {
      if (payload.video) setVideoData(payload.video);
      if (payload.audio) setAudioData(payload.audio);
      if (payload.decision) setDecisionData(payload.decision);
      if (payload.signals) setSignalState(payload.signals);
      if (payload.system) {
        setSystemData(payload.system);
        setIsDemoMode(payload.system.demo_mode || false);
      }
    });

    // Fallback status poller every 3s
    const poller = setInterval(() => {
      getSystemStatus().then(data => {
        setIsDemoMode(data.demo_mode || false);
      }).catch(() => {});
    }, 3000);

    return () => {
      unsubscribe();
      clearInterval(poller);
      wsClient.disconnect();
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top software pipeline status bar */}
      <SystemStatusBar system={systemData} isDemoMode={isDemoMode} />

      {/* Main App Container */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 flex flex-col gap-6">
        {/* Navigation & Action Header */}
        <header className="flex flex-wrap items-center justify-between gap-4 pb-2 border-b border-slate-800/80">
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-2">
              <span>Smart Acoustic & Vision Traffic Signal</span>
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Software-only multimodal traffic signal demo using uploaded audio and video
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-600/90 hover:bg-indigo-600 border border-indigo-500 text-white font-semibold text-xs flex items-center gap-1.5 transition shadow-sm hover:shadow-indigo-500/20"
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>AI Models & Viva Specs</span>
            </button>
          </div>
        </header>

        <nav className="grid grid-cols-2 gap-2 rounded-xl border border-slate-800 bg-slate-900/70 p-2 md:grid-cols-4" aria-label="Demo views">
          {[
            ['overview', 'Overview', LayoutDashboard],
            ['upload', 'Upload & Analyze', Upload],
            ['trace', 'Decision Trace', GitBranch],
            ['signals', 'Signal Board', Radio],
          ].map(([id, label, Icon]) => (
            <button key={id} type="button" onClick={() => setActiveView(id)} className={`flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-bold transition ${activeView === id ? 'bg-cyan-400 text-slate-950' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}>
              <Icon className="h-4 w-4" />{label}
            </button>
          ))}
        </nav>

        {activeView === 'overview' && <>
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-2"><LiveVideoFeed videoData={videoData} /><AudioMonitor audioData={audioData} /></section>
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-2"><DecisionCard decisionData={decisionData} videoData={videoData} audioData={audioData} /><TrafficSignal4Way signalState={signalState} /></section>
          <DemoControls isDemoMode={isDemoMode} onTrigger={() => getSystemStatus().then(d => setIsDemoMode(d.demo_mode || false))} />
        </>}

        {activeView === 'upload' && <UploadDemoView onAnalyzed={() => getSystemStatus().then(d => setIsDemoMode(d.demo_mode || false))} />}

        {activeView === 'trace' && <>
          <DecisionCard decisionData={decisionData} videoData={videoData} audioData={audioData} />
          <DataFlowDiagram system={systemData} isEmergency={decisionData?.mode === 'EMERGENCY'} mode={decisionData?.mode || 'NORMAL'} />
          <EventLogTable />
        </>}

        {activeView === 'signals' && <>
          <TrafficSignal4Way signalState={signalState} />
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-2"><LiveVideoFeed videoData={videoData} /><AudioMonitor audioData={audioData} /></section>
        </>}

        {/* Footer */}
        <footer className="pt-4 pb-6 border-t border-slate-900 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Smart Acoustic & Vision Traffic Signal — Software Demo</span>
          <span>FastAPI + OpenCV + YOLOv8 + Audio AI</span>
        </footer>
      </div>

      {/* College Presentation & Examiner Viva Cheatsheet Modal */}
      <ModelInfoModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
