import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import Dashboard from './Dashboard';
import CalendarView from './CalendarView';
import TasksView from './TasksView';
import FinanceView from './FinanceView';
import Analytics from './Analytics';
import Settings from './Settings';
import AuthPage from './AuthPage';
import OCRModal from '../components/OCRModal';
import { apiRequest, clearAccessToken, getAccessToken } from '../lib/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isOCRModalOpen, setIsOCRModalOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [sessionStatus, setSessionStatus] = useState('checking');
  const [sessionError, setSessionError] = useState('');
  const [voiceCommand, setVoiceCommand] = useState('');

  const verifySession = async () => {
    if (!getAccessToken()) {
      setSessionStatus('signed-out');
      return;
    }
    setSessionStatus('checking');
    setSessionError('');
    try {
      setUser(await apiRequest('/auth/me'));
      setSessionStatus('signed-in');
    } catch (error) {
      if (error.status === 401) {
        clearAccessToken();
        setUser(null);
        setSessionStatus('signed-out');
      } else {
        setSessionError(error.message);
        setSessionStatus('error');
      }
    }
  };

  useEffect(() => {
    verifySession();
    const handleSessionExpired = () => {
      setUser(null);
      setSessionStatus('signed-out');
    };
    window.addEventListener('ai-life-admin:auth-expired', handleSessionExpired);
    return () => window.removeEventListener('ai-life-admin:auth-expired', handleSessionExpired);
  }, []);

  const handleVoiceCommand = (command) => {
    setVoiceCommand({ id: `${Date.now()}-${Math.random()}`, text: command });
  };

  if (sessionStatus === 'checking') return <main className="grid min-h-screen place-items-center bg-slate-950 text-sm text-slate-300">Checking session...</main>;
  if (sessionStatus === 'error') return (
    <main className="grid min-h-screen place-items-center bg-slate-950 px-4 text-center text-sm text-rose-300">
      <div className="space-y-3"><p>{sessionError}</p><button onClick={verifySession} className="rounded-lg bg-indigo-600 px-4 py-2 text-white">Retry</button></div>
    </main>
  );
  if (!user) return <AuthPage onAuthenticated={(authenticatedUser) => { setUser(authenticatedUser); setSessionStatus('signed-in'); }} />;

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onOpenOCR={() => setIsOCRModalOpen(true)}
        user={user}
        onLogout={() => { clearAccessToken(); setUser(null); setSessionStatus('signed-out'); }}
      />
      
      <main className="flex-1 p-8 overflow-y-auto">
        {activeTab === 'dashboard' && <Dashboard onVoiceCommand={handleVoiceCommand} voiceCommand={voiceCommand} />}
        {activeTab === 'calendar' && <CalendarView />}
        {activeTab === 'tasks' && <TasksView />}
        {activeTab === 'finance' && <FinanceView />}
        {activeTab === 'analytics' && <Analytics />}
        {activeTab === 'settings' && <Settings user={user} onUserUpdated={setUser} />}
      </main>

      <OCRModal 
        isOpen={isOCRModalOpen} 
        onClose={() => setIsOCRModalOpen(false)} 
      />
    </div>
  );
}
