import React, { useState } from 'react';
import { Bot, Loader2 } from 'lucide-react';
import { apiRequest, setAccessToken } from '../lib/api';

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const credentials = { email: email.trim().toLowerCase(), password };
      if (mode === 'register') await apiRequest('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });

      const session = await apiRequest('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      setAccessToken(session.access_token);
      const user = await apiRequest('/auth/me');
      onAuthenticated(user);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-slate-100">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-5 rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-indigo-600 p-2.5"><Bot size={22} /></div>
          <div>
            <h1 className="text-base font-bold">AI Life Admin</h1>
            <p className="text-xs text-slate-400">{mode === 'login' ? 'Sign in to your workspace' : 'Create your workspace account'}</p>
          </div>
        </div>

        <label className="block space-y-1.5 text-xs text-slate-300">
          Email
          <input required autoComplete="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500" />
        </label>
        <label className="block space-y-1.5 text-xs text-slate-300">
          Password
          <input required minLength={mode === 'register' ? 8 : 1} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500" />
        </label>

        {error && <p role="alert" className="text-xs text-rose-400">{error}</p>}

        <button type="submit" disabled={submitting} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50">
          {submitting && <Loader2 size={14} className="animate-spin" />}
          {mode === 'login' ? 'Sign in' : 'Create account'}
        </button>

        <p className="text-center text-xs text-slate-400">
          {mode === 'login' ? 'New here?' : 'Already have an account?'}{' '}
          <button type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }} className="font-medium text-indigo-400 hover:text-indigo-300">
            {mode === 'login' ? 'Create account' : 'Sign in'}
          </button>
        </p>
      </form>
    </main>
  );
}