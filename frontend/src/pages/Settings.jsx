import React, { useState } from 'react';
import { CheckCircle2, KeyRound, Save, Server, Settings as SettingsIcon } from 'lucide-react';
import { apiRequest, getApiBaseUrl } from '../lib/api';

export default function Settings({ user, onUserUpdated }) {
  const [email, setEmail] = useState(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const updateAccount = async (event) => {
    event.preventDefault();
    setError('');
    setSaved(false);

    const updates = { current_password: currentPassword };
    if (email.trim() && email.trim().toLowerCase() !== user?.email) updates.email = email.trim().toLowerCase();
    if (newPassword) updates.new_password = newPassword;
    if (Object.keys(updates).length === 1) {
      setError('Enter a new email address or password.');
      return;
    }

    setSaving(true);
    try {
      const updatedUser = await apiRequest('/auth/me', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      onUserUpdated(updatedUser);
      setCurrentPassword('');
      setNewPassword('');
      setSaved(true);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="flex items-center gap-2 text-lg font-bold text-white"><SettingsIcon size={18} className="text-indigo-400" /> Account Settings</h2>
        <p className="mt-1 text-xs text-slate-400">Manage account access and view the active backend endpoint.</p>
      </div>

      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="mb-4 flex items-center gap-2 text-xs font-semibold text-slate-200"><Server size={15} className="text-indigo-400" /> Backend</h3>
        <p className="mb-1 text-[11px] text-slate-400">API base URL</p>
        <code className="block break-all rounded-lg bg-slate-950 px-3 py-2 text-xs text-slate-200">{getApiBaseUrl()}</code>
        <p className="mt-3 text-[11px] text-slate-500">Database URI, JWT signing key, and Gemini API key belong in the backend `.env`; they are never entered or stored in this browser.</p>
      </section>

      <form onSubmit={updateAccount} className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-200"><KeyRound size={15} className="text-indigo-400" /> Account credentials</h3>
        <label className="block space-y-1.5 text-xs text-slate-400">
          Email address
          <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500" />
        </label>
        <label className="block space-y-1.5 text-xs text-slate-400">
          Current password
          <input required type="password" autoComplete="current-password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500" />
        </label>
        <label className="block space-y-1.5 text-xs text-slate-400">
          New password <span className="text-slate-600">(optional, at least 8 characters)</span>
          <input minLength={8} type="password" autoComplete="new-password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500" />
        </label>

        {error && <p role="alert" className="text-xs text-rose-400">{error}</p>}
        {saved && <p role="status" className="flex items-center gap-1.5 text-xs text-emerald-400"><CheckCircle2 size={14} /> Account updated.</p>}

        <div className="flex justify-end">
          <button type="submit" disabled={saving} className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50">
            <Save size={14} /> {saving ? 'Saving...' : 'Update account'}
          </button>
        </div>
      </form>
    </div>
  );
}