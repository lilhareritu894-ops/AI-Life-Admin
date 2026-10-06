import React, { useEffect, useRef, useState } from 'react';
import { Mic, MicOff, Sparkles } from 'lucide-react';

export default function VoiceAssistant({ onVoiceCommand }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);

  useEffect(() => () => recognitionRef.current?.stop(), []);

  const toggleListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Voice recognition is not supported by this browser.');
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      return;
    }

    setError('');
    setTranscript('');
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => {
      recognitionRef.current = null;
      setIsListening(false);
    };
    recognition.onerror = (event) => setError(event.error === 'not-allowed' ? 'Microphone permission was denied.' : 'Voice recognition stopped unexpectedly.');

    recognition.onresult = (event) => {
      const current = event.resultIndex;
      const resultText = event.results[current][0].transcript;
      setTranscript(resultText);
      if (event.results[current].isFinal) {
        onVoiceCommand(resultText);
      }
    };

    try {
      recognition.start();
    } catch {
      setError('Voice recognition could not start.');
      setIsListening(false);
    }
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-slate-900 border border-slate-800 rounded-2xl shadow-lg">
      <button
        type="button"
        onClick={toggleListening}
        aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
        className={`p-3 rounded-xl transition-all ${
          isListening 
            ? 'bg-rose-500 animate-pulse text-white shadow-lg shadow-rose-500/30' 
            : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20'
        }`}
      >
        {isListening ? <MicOff size={18} /> : <Mic size={18} />}
      </button>
      <div className="flex-1">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
          <Sparkles size={13} className="text-indigo-400" /> Executive Voice Engine
        </div>
        <p role={error ? 'alert' : undefined} className={`text-[11px] truncate mt-0.5 ${error ? 'text-rose-400' : 'text-slate-400'}`}>
          {error || (isListening ? (transcript || 'Listening... Speak command...') : (transcript || 'Click mic to ask Gemini by voice.'))}
        </p>
      </div>
    </div>
  );
}