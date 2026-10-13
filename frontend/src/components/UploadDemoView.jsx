import React, { useEffect, useState } from 'react';
import { AudioLines, FileAudio, FileVideo, Loader2, Play, Upload, X } from 'lucide-react';
import { uploadDemoMedia } from '../services/api';

function FileDrop({ label, accept, icon: Icon, file, onChange, onClear }) {
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return undefined;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  return (
    <div className="relative min-w-0 rounded-xl border border-dashed border-slate-700 bg-slate-950/70 p-4 transition hover:border-cyan-500/60">
      <input
        type="file"
        accept={accept}
        onChange={(event) => onChange(event.target.files?.[0] || null)}
        className="absolute inset-0 z-10 cursor-pointer opacity-0"
      />
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="rounded-lg bg-cyan-400/10 p-2 text-cyan-300"><Icon className="h-5 w-5" /></div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-white">{label}</p>
            <p className="mt-1 truncate text-xs text-slate-500">{file ? file.name : 'Choose a file to simulate this sensor'}</p>
          </div>
        </div>
        {file && (
          <button type="button" onClick={onClear} className="relative z-20 rounded-md p-1 text-slate-500 hover:bg-slate-800 hover:text-white" aria-label={`Remove ${label}`}>
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
      {file?.type.startsWith('video/') && <video src={previewUrl} controls className="mt-4 aspect-video w-full rounded-lg bg-black object-contain" />}
      {file?.type.startsWith('audio/') && <audio src={previewUrl} controls className="mt-4 w-full" />}
    </div>
  );
}

export default function UploadDemoView({ onAnalyzed }) {
  const [videoFile, setVideoFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('Add one or both files. The software pipeline will turn them into a traffic signal decision.');

  const analyze = async () => {
    if (!videoFile && !audioFile) return;
    setIsUploading(true);
    setMessage('Uploading media and running the multimodal decision simulation...');
    try {
      const result = await uploadDemoMedia(videoFile, audioFile);
      setMessage(result.message || `${result.scenario} is now driving the signal board.`);
      onAnalyzed?.();
    } catch {
      setMessage('Upload failed. Check that the FastAPI server is running.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <section className="glass-card rounded-xl p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-cyan-300"><Upload className="h-5 w-5" /><span className="text-xs font-bold uppercase tracking-[0.18em]">Software input lab</span></div>
          <h2 className="mt-2 text-2xl font-black text-white">Upload a scene, get a signal decision.</h2>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">Video and audio stay inside the software demo. File names select a reproducible scenario, while the existing multimodal engine generates the final four-way signal state.</p>
        </div>
        <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/5 px-3 py-2 text-right text-xs text-cyan-200"><AudioLines className="mb-1 ml-auto h-4 w-4" />No hardware required</div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <FileDrop label="Traffic video" accept="video/*" icon={FileVideo} file={videoFile} onChange={setVideoFile} onClear={() => setVideoFile(null)} />
        <FileDrop label="Traffic audio" accept="audio/*" icon={FileAudio} file={audioFile} onChange={setAudioFile} onClear={() => setAudioFile(null)} />
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 pt-4">
        <p className="max-w-xl text-xs text-slate-400">{message}</p>
        <button type="button" onClick={analyze} disabled={isUploading || (!videoFile && !audioFile)} className="inline-flex items-center gap-2 rounded-lg bg-cyan-400 px-4 py-2 text-sm font-black text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-40">
          {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Analyze media
        </button>
      </div>
    </section>
  );
}