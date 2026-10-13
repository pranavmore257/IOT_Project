import React, { useState, useEffect } from 'react';
import { History, Trash2, RefreshCw, Search } from 'lucide-react';
import { getEvents, clearEventLog } from '../services/api';

export default function EventLogTable() {
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await getEvents(50);
      setEvents(data.events || []);
    } catch (err) {
      console.error('Fetch events error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleClear = async () => {
    if (window.confirm('Clear all SQLite logged traffic events?')) {
      await clearEventLog();
      fetchEvents();
    }
  };

  const filteredEvents = events.filter(e => {
    const term = filter.toLowerCase();
    return (
      (e.event_type || '').toLowerCase().includes(term) ||
      (e.mode || '').toLowerCase().includes(term) ||
      (e.audio_class || '').toLowerCase().includes(term) ||
      (e.direction || '').toLowerCase().includes(term)
    );
  });

  return (
    <div className="glass-card rounded-xl p-4 flex flex-col gap-3">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-sm tracking-wider text-slate-200 uppercase">
            SQLite Traffic Event History Log
          </h2>
        </div>
        <div className="flex items-center gap-2">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Filter events..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg pl-8 pr-2.5 py-1 focus:outline-none focus:border-indigo-500 w-36 sm:w-48"
            />
          </div>

          <button
            onClick={fetchEvents}
            disabled={loading}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 transition"
            title="Refresh log"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={handleClear}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-900/60 border border-slate-700 hover:border-rose-500 text-slate-300 hover:text-rose-300 transition"
            title="Clear SQLite database log"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Events Table Container */}
      <div className="bg-slate-950 rounded-lg border border-slate-800 overflow-x-auto max-h-64 overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/90 text-slate-400 uppercase text-[10px] tracking-wider sticky top-0 border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3">Time</th>
              <th className="py-2.5 px-3">Event Description</th>
              <th className="py-2.5 px-3">Audio Evidence</th>
              <th className="py-2.5 px-3">Vehicles</th>
              <th className="py-2.5 px-3">Density</th>
              <th className="py-2.5 px-3">Direction</th>
              <th className="py-2.5 px-3">Mode</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-900 text-slate-300">
            {filteredEvents.length > 0 ? (
              filteredEvents.map((ev) => {
                const isEmerg = ev.mode === 'EMERGENCY';
                const isAcc = ev.mode === 'ACCIDENT_ALERT';
                const timeStr = (ev.timestamp || '').split('T')[1]?.substring(0, 8) || ev.timestamp;

                return (
                  <tr key={ev.id} className="hover:bg-slate-900/50 transition">
                    <td className="py-2 px-3 font-mono text-slate-400">{timeStr}</td>
                    <td className="py-2 px-3 font-medium text-white max-w-xs truncate">
                      {ev.event_type}
                    </td>
                    <td className="py-2 px-3 text-slate-300">
                      {ev.audio_class ? `${ev.audio_class} (${Math.round((ev.audio_confidence || 0) * 100)}%)` : '-'}
                    </td>
                    <td className="py-2 px-3 font-bold text-slate-200">{ev.vehicle_count}</td>
                    <td className="py-2 px-3">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        ev.density === 'HIGH' ? 'bg-rose-950 text-rose-400' : ev.density === 'MEDIUM' ? 'bg-amber-950 text-amber-400' : 'bg-emerald-950 text-emerald-400'
                      }`}>
                        {ev.density}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-300 font-semibold">{ev.direction || 'NONE'}</td>
                    <td className="py-2 px-3">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        isEmerg ? 'bg-rose-600 text-white' : isAcc ? 'bg-amber-500 text-slate-950' : 'bg-slate-800 text-slate-300'
                      }`}>
                        {ev.mode}
                      </span>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={7} className="py-6 text-center text-slate-500">
                  No logged traffic events found. Run a demo or let the system cycle.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
