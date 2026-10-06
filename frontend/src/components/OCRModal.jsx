import React, { useState } from 'react';
import { X, Upload, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import { apiRequest } from '../lib/api';

export default function OCRModal({ isOpen, onClose }) {
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setExtractedText('');
      setError('');
    }
  };

  const handleProcessScan = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const document = await apiRequest('/documents/scan', {
        method: 'POST',
        body: formData,
      });
      setExtractedText(document.extracted_text);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 w-full max-w-md rounded-2xl p-6 shadow-2xl relative space-y-4">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white">
          <X size={18} />
        </button>

        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <FileText className="text-indigo-400" size={18} /> Document Scan
        </h3>
        <p className="text-xs text-slate-400">Extract and save text from a document or receipt.</p>

        <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-6 text-center transition cursor-pointer">
          <input type="file" onChange={handleFileChange} className="hidden" id="ocr-input" accept=".txt,.md,.csv,.pdf,.png,.jpg,.jpeg,.webp,text/plain,text/markdown,text/csv,application/pdf,image/png,image/jpeg,image/webp" />
          <label htmlFor="ocr-input" className="cursor-pointer space-y-2 block">
            <Upload size={24} className="mx-auto text-slate-400" />
            <span className="text-xs text-slate-300 block">
              {file ? file.name : "Select a text, PDF, PNG, JPEG, or WebP file"}
            </span>
          </label>
        </div>

        {error && <p role="alert" className="text-xs text-rose-400">{error}</p>}

        {file && !extractedText && (
          <button
            onClick={handleProcessScan}
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : "Extract and save text"}
          </button>
        )}

        {extractedText && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-300 space-y-2">
            <div className="flex items-center gap-1.5 font-semibold">
              <CheckCircle2 size={15} /> Document extracted and saved
            </div>
            <p className="text-[11px] text-slate-300">{extractedText}</p>
          </div>
        )}
      </div>
    </div>
  );
}