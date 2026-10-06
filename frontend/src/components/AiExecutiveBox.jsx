import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Send, Bot, Sparkles, Zap, RefreshCw } from 'lucide-react';
import { apiRequest } from '../lib/api';

export default function AiExecutiveBox({ voiceCommand }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [error, setError] = useState('');
  const lastVoiceCommandId = useRef(null);

  const sendPrompt = useCallback(async (value) => {
    const normalizedPrompt = value.trim();
    if (!normalizedPrompt) return;

    setLoading(true);
    setAiResponse(null);
    setError('');
    setPrompt(normalizedPrompt);

    try {
      const data = await apiRequest('/agent/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: normalizedPrompt }),
      });
      setAiResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!voiceCommand || voiceCommand.id === lastVoiceCommandId.current) return;
    lastVoiceCommandId.current = voiceCommand.id;
    sendPrompt(voiceCommand.text);
  }, [sendPrompt, voiceCommand]);

  const handleExecutePrompt = (event) => {
    event.preventDefault();
    sendPrompt(prompt);
  };

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl space-y-4 relative overflow-hidden backdrop-blur-md">
      {/* Decorative Glow */}
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* Box Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-xl shadow-md">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              Gemini Assistant
              <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-semibold">
                AI response
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">Ask for suggestions; changes are not made automatically.</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg">
          <Zap className="w-3.5 h-3.5" /> Ready
        </div>
      </div>

      {/* Prompt Input Form */}
      <form onSubmit={handleExecutePrompt} className="relative">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask Gemini for help planning your day"
          className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-xs text-slate-100 rounded-xl pl-4 pr-24 py-3.5 focus:outline-none transition-all placeholder:text-slate-500"
        />
        <button
          type="submit"
          disabled={loading || !prompt.trim()}
          className="absolute right-1.5 top-1.5 bottom-1.5 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all disabled:opacity-50 shadow-md active:scale-95"
        >
          {loading ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Processing...
            </>
          ) : (
            <>
              Ask <Send className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </form>

      {error && <p role="alert" className="text-xs text-rose-400">{error}</p>}

      {/* Execution Feedback / AI Output */}
      {aiResponse && (
        <div className="p-4 bg-slate-950/90 border border-indigo-500/30 rounded-xl space-y-3 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-semibold text-indigo-400 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" /> {aiResponse.agent_name}
            </span>
          </div>
          <p className="text-xs text-slate-200 font-medium whitespace-pre-wrap">{aiResponse.response}</p>
        </div>
      )}
    </div>
  );
}