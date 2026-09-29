import React, { useState, useRef } from 'react';
import { UploadCloud, FileSpreadsheet, Loader2, XCircle } from 'lucide-react';
import { batchService, BatchJobRead } from '../../services/batchService';

interface ExcelUploadProps {
  onBatchStarted: (batch: BatchJobRead) => void;
}

export const ExcelUpload: React.FC<ExcelUploadProps> = ({ onBatchStarted }) => {
  const [file, setFile] = useState<File | null>(null);
  const [batchName, setBatchName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.name.endsWith('.csv') || selected.name.endsWith('.xlsx')) {
        setFile(selected);
        if (!batchName) {
          setBatchName(selected.name.split('.')[0] + ' Batch');
        }
        setError(null);
      } else {
        setError('Only .csv and .xlsx files are supported');
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file || !batchName) return;
    setIsUploading(true);
    setError(null);
    try {
      const batch = await batchService.submitExcelBatch(batchName, file);
      onBatchStarted(batch);
      setFile(null);
      setBatchName('');
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 flex flex-col gap-4">
      <div>
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
          Bulk Upload via Excel/CSV
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          Upload a spreadsheet containing company names and website URLs.
        </p>
      </div>

      <div className="flex flex-col gap-3 mt-2">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Batch Name</label>
          <input
            type="text"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g. Q3 SaaS Target List"
            value={batchName}
            onChange={(e) => setBatchName(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">File</label>
          <div className="relative">
            <input
              type="file"
              accept=".csv, .xlsx"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className={`w-full flex items-center justify-center gap-2 border-2 border-dashed rounded-lg px-4 py-8 text-center transition-colors ${file ? 'border-blue-500/50 bg-blue-500/10' : 'border-slate-600 hover:border-slate-500 hover:bg-slate-800/50'}`}>
              {file ? (
                <>
                  <FileSpreadsheet className="w-6 h-6 text-blue-400" />
                  <span className="text-blue-100 font-medium">{file.name}</span>
                </>
              ) : (
                <>
                  <UploadCloud className="w-6 h-6 text-slate-400" />
                  <span className="text-slate-300">Click or drag file to upload (.csv, .xlsx)</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-3 text-sm flex items-start gap-2">
          <XCircle className="w-5 h-5 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div className="mt-2 flex justify-end">
        <button
          onClick={handleUpload}
          disabled={!file || !batchName || isUploading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Uploading...
            </>
          ) : (
            'Process Batch'
          )}
        </button>
      </div>
    </div>
  );
};
