import React from 'react';
import { LayoutDashboard, Calendar, CheckSquare, Wallet, BarChart3, Settings, Bot, Scan, LogOut } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, onOpenOCR, user, onLogout }) {
  const menuItems = [
    { id: 'dashboard', label: 'Executive Hub', icon: LayoutDashboard },
    { id: 'calendar', label: 'Smart Calendar', icon: Calendar },
    { id: 'tasks', label: 'Task Queue', icon: CheckSquare },
    { id: 'finance', label: 'Finance Ledger', icon: Wallet },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-slate-900/90 backdrop-blur-md border-r border-slate-800 h-screen p-4 flex flex-col justify-between select-none">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2 py-4 mb-6">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 rounded-xl shadow-lg shadow-indigo-500/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white text-base tracking-wide">AI Life Admin</h1>
            <p className="text-[10px] text-indigo-400 font-semibold tracking-wider uppercase">Executive Engine v2.0</p>
          </div>
        </div>

        {/* Action Button */}
        <button 
          onClick={onOpenOCR}
          className="w-full mb-6 py-2.5 px-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 shadow-md transition-all active:scale-95"
        >
          <Scan size={15} /> Scan Document / Receipt
        </button>

        {/* Navigation */}
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-inner'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Connection Indicator */}
      <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
        <div className="truncate text-[11px] text-slate-300">{user?.email}</div>
        <button type="button" onClick={onLogout} className="mt-3 flex w-full items-center gap-2 text-[11px] text-slate-400 hover:text-white">
          <LogOut size={14} /> Sign out
        </button>
      </div>
    </div>
  );
}