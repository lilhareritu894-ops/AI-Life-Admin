import React, { useEffect, useState } from 'react';
import AiExecutiveBox from '../components/AiExecutiveBox';
import VoiceAssistant from '../components/VoiceAssistant';
import { Calendar, CheckSquare, FileText, Zap, ShieldCheck } from 'lucide-react';
import { apiRequest } from '../lib/api';

export default function Dashboard({ onVoiceCommand, voiceCommand }) {
  const [overview, setOverview] = useState({ openTasks: 0, completedTasks: 0, events: 0, documents: 0 });
  const [backendStatus, setBackendStatus] = useState('Connecting');

  useEffect(() => {
    const loadOverview = async () => {
      try {
        const [tasks, events, documents] = await Promise.all([
          apiRequest('/tasks/'),
          apiRequest('/calendar/'),
          apiRequest('/documents/'),
        ]);
        setOverview({
          openTasks: tasks.filter((task) => !task.is_completed).length,
          completedTasks: tasks.filter((task) => task.is_completed).length,
          events: events.length,
          documents: documents.length,
        });
        setBackendStatus('Connected');
      } catch {
        setBackendStatus('Unavailable');
      }
    };

    loadOverview();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-slate-900 border border-slate-800 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider">Executive Overview</span>
          <h2 className="text-xl font-bold text-white mt-1">AI Autonomous Life Command Center</h2>
          <p className="text-xs text-slate-400 mt-0.5">Tasks, calendar, and documents synced from the backend.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`px-3 py-1.5 border rounded-xl text-xs flex items-center gap-1.5 font-medium ${backendStatus === 'Connected' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' : 'bg-amber-500/10 border-amber-500/20 text-amber-300'}`}>
            <Zap size={14} /> Backend: {backendStatus}
          </div>
          <div className="px-3 py-1.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-xs text-indigo-300 flex items-center gap-1.5 font-medium">
            <ShieldCheck size={14} className="text-indigo-400" /> API v1
          </div>
        </div>
      </div>

      {/* Voice Assistant Integration Bar */}
      <VoiceAssistant onVoiceCommand={onVoiceCommand} />

      {/* Core AI Orchestrator Box */}
      <AiExecutiveBox voiceCommand={voiceCommand} />

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-2xl flex items-center gap-3">
          <div className="p-3 bg-indigo-500/10 rounded-xl text-indigo-400"><CheckSquare size={20} /></div>
          <div>
            <div className="text-[11px] text-slate-400">Open tasks</div>
            <div className="text-base font-bold text-slate-200">{overview.openTasks}</div>
            <div className="text-[10px] text-slate-500">{overview.completedTasks} completed</div>
          </div>
        </div>
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-2xl flex items-center gap-3">
          <div className="p-3 bg-purple-500/10 rounded-xl text-purple-400"><Calendar size={20} /></div>
          <div>
            <div className="text-[11px] text-slate-400">Calendar events</div>
            <div className="text-base font-bold text-slate-200">{overview.events}</div>
          </div>
        </div>
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-2xl flex items-center gap-3">
          <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400"><FileText size={20} /></div>
          <div>
            <div className="text-[11px] text-slate-400">Documents scanned</div>
            <div className="text-base font-bold text-slate-200">{overview.documents}</div>
          </div>
        </div>
      </div>
    </div>
  );
}