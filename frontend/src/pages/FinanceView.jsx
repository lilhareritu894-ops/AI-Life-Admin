import React, { useEffect, useState } from 'react';
import { ArrowDownRight, ArrowUpRight, Loader2, Plus, Trash2, Wallet } from 'lucide-react';
import { apiRequest } from '../lib/api';

const currentLocalDateTime = () => {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
};

export default function FinanceView() {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('General');
  const [amount, setAmount] = useState('');
  const [kind, setKind] = useState('expense');
  const [occurredAt, setOccurredAt] = useState(currentLocalDateTime);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const loadFinance = async () => {
    try {
      setError('');
      const [records, totals] = await Promise.all([
        apiRequest('/finance/?limit=500'),
        apiRequest('/finance/summary'),
      ]);
      setTransactions(records);
      setSummary(totals);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFinance();
  }, []);

  const addTransaction = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      const transaction = await apiRequest('/finance/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          category: category.trim() || 'General',
          amount: Number(amount),
          kind,
          occurred_at: new Date(occurredAt).toISOString(),
        }),
      });
      setTransactions((current) => [transaction, ...current]);
      setTitle('');
      setAmount('');
      setCategory('General');
      setOccurredAt(currentLocalDateTime());
      setShowForm(false);
      await loadFinance();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const deleteTransaction = async (transactionId) => {
    try {
      setError('');
      await apiRequest(`/finance/${transactionId}`, { method: 'DELETE' });
      setTransactions((current) => current.filter((transaction) => transaction.id !== transactionId));
      await loadFinance();
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const formatMoney = (value) => new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: summary?.currency || 'USD',
  }).format(value || 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white">Financial & Ledger Tracker</h2>
          <p className="text-xs text-slate-400">Transactions saved to your account</p>
        </div>
        <button type="button" onClick={() => setShowForm((visible) => !visible)} className="flex items-center gap-2 rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-500">
          <Plus size={14} /> Log Entry
        </button>
      </div>

      {showForm && (
        <form onSubmit={addTransaction} className="grid grid-cols-1 gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4 md:grid-cols-2 xl:grid-cols-5">
          <input required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Description" className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white" />
          <input maxLength={100} value={category} onChange={(event) => setCategory(event.target.value)} placeholder="Category" className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white" />
          <input required type="number" min="0.01" step="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="Amount (USD)" className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white" />
          <select value={kind} onChange={(event) => setKind(event.target.value)} className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white">
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
          <input required type="datetime-local" value={occurredAt} onChange={(event) => setOccurredAt(event.target.value)} className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white" />
          <button type="submit" disabled={saving} className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50 md:col-span-2 xl:col-span-5">
            {saving && <Loader2 size={14} className="animate-spin" />} Save transaction
          </button>
        </form>
      )}

      {error && <p role="alert" className="text-xs text-rose-400">{error}</p>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <SummaryCard label="Balance" value={formatMoney(summary?.balance)} icon={<Wallet size={14} />} loading={loading} />
        <SummaryCard label="Income this month" value={formatMoney(summary?.month_income)} icon={<ArrowUpRight size={14} />} loading={loading} />
        <SummaryCard label="Expenses this month" value={formatMoney(summary?.month_expenses)} icon={<ArrowDownRight size={14} />} loading={loading} />
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="mb-4 text-xs font-semibold text-slate-300">Transaction History</h3>
        <div className="space-y-2.5">
          {loading ? <p className="py-6 text-center text-xs text-slate-400">Loading transactions...</p> : transactions.length === 0 ? (
            <p className="py-6 text-center text-xs text-slate-500">No transactions recorded yet.</p>
          ) : transactions.map((transaction) => (
            <div key={transaction.id} className="flex items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-950 p-3.5">
              <div className="flex min-w-0 items-center gap-3">
                <div className={`rounded-lg p-2 ${transaction.kind === 'income' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}><Wallet size={15} /></div>
                <div className="min-w-0">
                  <div className="truncate text-xs font-medium text-slate-200">{transaction.title}</div>
                  <div className="text-[10px] text-slate-500">{transaction.category} · {new Date(transaction.occurred_at).toLocaleString()}</div>
                </div>
              </div>
              <div className="flex shrink-0 items-center gap-3">
                <span className={`text-xs font-semibold ${transaction.kind === 'income' ? 'text-emerald-400' : 'text-slate-300'}`}>
                  {transaction.kind === 'income' ? '+' : '-'}{formatMoney(transaction.amount)}
                </span>
                <button type="button" onClick={() => deleteTransaction(transaction.id)} aria-label={`Delete ${transaction.title}`} className="text-slate-500 hover:text-rose-400"><Trash2 size={14} /></button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ label, value, icon, loading }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="flex items-center justify-between text-xs text-slate-400"><span>{label}</span><span className="text-indigo-400">{icon}</span></div>
      <div className="mt-2 text-xl font-bold text-white">{loading ? '...' : value}</div>
    </div>
  );
}