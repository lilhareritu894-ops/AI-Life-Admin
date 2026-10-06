import React, { useEffect, useState } from 'react';
import { Activity, BarChart3, Calendar, CheckSquare, FileText, RefreshCw, Sparkles } from 'lucide-react';
import { apiRequest } from '../lib/api';

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAnalytics = async () => {
    try {
      setError('');
      setSummary(await apiRequest('/analytics/summary'));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const dailyActivity = summary?.daily_activity || [];
  const maxTasks = Math.max(1, ...dailyActivity.map((item) => item.tasks_created));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white">Account Analytics</h2>
          <p className="text-xs text-slate-400">Counts and activity from your saved records</p>
        </div>
        <button type="button" onClick={loadAnalytics} disabled={loading} aria-label="Refresh analytics" className="rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-300 hover:text-white disabled:opacity-50"><RefreshCw size={15} className={loading ? 'animate-spin' : ''} /></button>
      </div>

      {error && <p role="alert" className="text-xs text-rose-400">{error}</p>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Tasks" value={summary?.tasks_total} detail={`${summary?.tasks_completed ?? 0} completed · ${summary?.tasks_pending ?? 0} pending`} icon={<CheckSquare size={16} />} loading={loading} />
        <Metric label="Calendar events" value={summary?.calendar_events} icon={<Calendar size={16} />} loading={loading} />
        <Metric label="Documents" value={summary?.documents} icon={<FileText size={16} />} loading={loading} />
        <Metric label="AI responses saved" value={summary?.agent_runs} icon={<Sparkles size={16} />} loading={loading} />
      </div>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="mb-5 flex items-center gap-2 text-xs font-semibold text-slate-300"><BarChart3 size={16} className="text-indigo-400" /> Task activity · last 7 days</div>
        {loading ? <p className="py-6 text-center text-xs text-slate-400">Loading activity...</p> : dailyActivity.length === 0 ? (
          <p className="py-6 text-center text-xs text-slate-500">No activity recorded yet.</p>
        ) : (
          <div className="grid h-52 grid-cols-7 items-end gap-3 border-b border-slate-800 px-2">
            {dailyActivity.map((day) => (
              <div key={day.date} className="flex h-full min-w-0 flex-col items-center justify-end gap-2">
                <div className="flex h-full w-full items-end justify-center gap-1">
                  <div title={`${day.tasks_created} tasks created`} className="w-1/3 rounded-t bg-indigo-500" style={{ height: `${Math.max(4, (day.tasks_created / maxTasks) * 100)}%` }} />
                  <div title={`${day.tasks_completed} tasks completed`} className="w-1/3 rounded-t bg-emerald-500" style={{ height: `${Math.max(4, (day.tasks_completed / maxTasks) * 100)}%` }} />
                </div>
                <span className="pb-2 text-[10px] text-slate-400">{new Date(`${day.date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short' })}</span>
              </div>
            ))}
          </div>
        )}
        <div className="mt-3 flex items-center gap-4 text-[10px] text-slate-400"><span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-indigo-500" /> Created</span><span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-emerald-500" /> Completed</span><span className="ml-auto flex items-center gap-1"><Activity size={12} /> {summary?.agent_runs ?? 0} saved responses</span></div>
      </section>
    </div>
  );
}

function Metric({ label, value, detail, icon, loading }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between text-[11px] text-slate-400"><span>{label}</span><span className="text-indigo-400">{icon}</span></div>
      <div className="mt-2 text-2xl font-bold text-white">{loading ? '...' : value ?? 0}</div>
      {detail && <div className="mt-1 text-[10px] text-slate-500">{detail}</div>}
    </div>
  );
}