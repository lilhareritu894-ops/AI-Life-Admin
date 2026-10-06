import React, { useState, useEffect } from 'react';
import { Plus, Loader2, Trash2 } from 'lucide-react';
import { apiRequest } from '../lib/api';

export default function TasksView() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setError('');
      const data = await apiRequest('/tasks/');
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;
    setSaving(true);
    setError('');
    try {
      const task = await apiRequest('/tasks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTask.trim() }),
      });
      setTasks((currentTasks) => [task, ...currentTasks]);
      setNewTask('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const toggleTask = async (task) => {
    setError('');
    try {
      const updatedTask = await apiRequest(`/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_completed: !task.is_completed }),
      });
      setTasks((currentTasks) => currentTasks.map((item) => item.id === task.id ? updatedTask : item));
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteTask = async (taskId) => {
    setError('');
    try {
      await apiRequest(`/tasks/${taskId}`, { method: 'DELETE' });
      setTasks((currentTasks) => currentTasks.filter((task) => task.id !== taskId));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-white">Live Task Queue</h2>
          <p className="text-xs text-slate-400">Direct CRUD sync with Cloud MongoDB Atlas</p>
        </div>
      </div>

      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <form onSubmit={handleAddTask} className="flex gap-2 mb-6">
          <input
            type="text"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="Add task to cloud database..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={saving || !newTask.trim()}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-white text-xs font-semibold flex items-center gap-1.5 disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />} Add Task
          </button>
        </form>

        {error && <p role="alert" className="mb-4 text-xs text-rose-400">{error}</p>}

        <div className="space-y-2">
          {loading ? (
            <p className="text-slate-400 text-xs text-center py-6">Loading tasks...</p>
          ) : tasks.length === 0 ? (
            <p className="text-slate-500 text-xs text-center py-6">No tasks yet.</p>
          ) : (
            tasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between gap-3 p-3.5 bg-slate-950 rounded-xl border border-slate-800">
                <label className="flex min-w-0 items-center gap-3 text-xs font-medium text-slate-200">
                  <input
                    type="checkbox"
                    checked={task.is_completed}
                    onChange={() => toggleTask(task)}
                    aria-label={`Mark ${task.title} ${task.is_completed ? 'pending' : 'completed'}`}
                    className="accent-indigo-500"
                  />
                  <span className={task.is_completed ? 'truncate text-slate-500 line-through' : 'truncate'}>{task.title}</span>
                </label>
                <div className="flex shrink-0 items-center gap-2">
                  <span className="text-[10px] px-2.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                    {task.is_completed ? 'Completed' : 'Pending'}
                  </span>
                  <button type="button" onClick={() => deleteTask(task.id)} aria-label={`Delete ${task.title}`} className="p-1 text-slate-500 hover:text-rose-400">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}