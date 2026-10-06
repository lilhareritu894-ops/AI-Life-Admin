import React, { useEffect, useState } from 'react';
import { Clock, Plus, Sparkles, Trash2, Loader2, RefreshCw } from 'lucide-react';
import { apiRequest } from '../lib/api';

export default function CalendarView() {
  const [events, setEvents] = useState([]);
  const [title, setTitle] = useState('');
  const [timeSlot, setTimeSlot] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [recommendation, setRecommendation] = useState('');

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      setError('');
      setEvents(await apiRequest('/calendar/'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addEvent = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      const createdEvent = await apiRequest('/calendar/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title.trim(), time_slot: timeSlot, status: 'Scheduled' }),
      });
      setEvents((currentEvents) => [...currentEvents, createdEvent].sort((a, b) => a.time_slot.localeCompare(b.time_slot)));
      setTitle('');
      setTimeSlot('');
      setShowForm(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const deleteEvent = async (eventId) => {
    try {
      setError('');
      await apiRequest(`/calendar/${eventId}`, { method: 'DELETE' });
      setEvents((currentEvents) => currentEvents.filter((event) => event.id !== eventId));
    } catch (err) {
      setError(err.message);
    }
  };

  const optimizeSchedule = async () => {
    try {
      setError('');
      const result = await apiRequest('/calendar/optimize');
      setRecommendation(result.recommendation);
    } catch (err) {
      setError(err.message);
    }
  };

  const formatTime = (value) => {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-white">Smart Calendar Engine</h2>
          <p className="text-xs text-slate-400">Automated time-blocking and conflict resolution</p>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => setShowForm((visible) => !visible)} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 px-3.5 py-2 rounded-xl text-xs font-semibold text-white">
            <Plus size={14} /> Add Event
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={addEvent} className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4 sm:flex-row">
          <input required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Event title" className="min-w-0 flex-1 rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white" />
          <input required type="datetime-local" value={timeSlot} onChange={(event) => setTimeSlot(event.target.value)} className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white" />
          <button type="submit" disabled={saving} className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50">
            {saving && <Loader2 size={14} className="animate-spin" />} Save event
          </button>
        </form>
      )}

      {error && <p role="alert" className="text-xs text-rose-400">{error}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
          <h3 className="font-semibold text-xs text-slate-300">Calendar events</h3>
          {loading ? <p className="py-6 text-center text-xs text-slate-400">Loading events...</p> : events.length === 0 ? (
            <p className="py-6 text-center text-xs text-slate-500">No calendar events yet.</p>
          ) : events.map((event) => (
            <div key={event.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between border-l-4 border-l-indigo-500">
              <div>
                <h4 className="font-medium text-xs text-slate-200">{event.title}</h4>
                <span className="text-[11px] text-slate-400 flex items-center gap-1 mt-1">
                  <Clock size={12} /> {formatTime(event.time_slot)}
                </span>
              </div>
              <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-md">
                {event.status}
              </span>
              <button type="button" onClick={() => deleteEvent(event.id)} aria-label={`Delete ${event.title}`} className="ml-3 text-slate-500 hover:text-rose-400">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs">
            <Sparkles className="w-4 h-4" /> AI Conflict Engine
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">{recommendation || 'Get a recommendation based on the events currently saved in your calendar.'}</p>
          <button type="button" onClick={optimizeSchedule} className="w-full py-2 bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 rounded-xl text-xs font-medium hover:bg-indigo-600/30 flex items-center justify-center gap-2">
            <RefreshCw size={13} /> Re-Optimize Schedule
          </button>
        </div>
      </div>
    </div>
  );
}