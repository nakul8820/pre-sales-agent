import React, { useState, useEffect } from 'react';
import { Layers, Loader2, PlayCircle, CheckCircle2, XCircle, AlertCircle, Download, ExternalLink } from 'lucide-react';
import { batchService, BatchJobRead } from '../../services/batchService';
import { useBatchStatus } from '../../hooks/useBatchStatus';

export const BatchDashboard: React.FC = () => {
  const [batches, setBatches] = useState<BatchJobRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBatches = async () => {
      try {
        const res = await batchService.listBatches();
        setBatches(res.items);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchBatches();
    // Poll list occasionally
    const int = setInterval(fetchBatches, 10000);
    return () => clearInterval(int);
  }, []);

  if (isLoading) {
    return <div className="p-8 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-slate-500" /></div>;
  }

  if (batches.length === 0) {
    return (
      <div className="text-center p-12 bg-slate-800/50 rounded-xl border border-slate-700/50">
        <Layers className="w-12 h-12 text-slate-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-slate-300">No Batches Found</h3>
        <p className="text-slate-500 mt-1">Upload an Excel file or import from HubSpot to start processing in bulk.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {batches.map(b => (
        <BatchStatusCard key={b.id} initialBatch={b} />
      ))}
    </div>
  );
};

const BatchStatusCard: React.FC<{ initialBatch: BatchJobRead }> = ({ initialBatch }) => {
  const { batch: liveBatch } = useBatchStatus(initialBatch.id);
  const batch = liveBatch || initialBatch;

  const total = batch.total_count || 1;
  const processed = batch.processed_count;
  const progressPct = Math.round((processed / total) * 100);

  const getStatusIcon = () => {
    switch (batch.status) {
      case 'queued': return <PlayCircle className="w-5 h-5 text-slate-400" />;
      case 'running': return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'completed': return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
      case 'partially_failed': return <AlertCircle className="w-5 h-5 text-amber-400" />;
      case 'failed': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return null;
    }
  };

  const getStatusColor = () => {
    switch (batch.status) {
      case 'queued': return 'text-slate-400 bg-slate-400/10 border-slate-400/20';
      case 'running': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'completed': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'partially_failed': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-5 flex flex-col md:flex-row gap-5 items-center">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3 mb-2">
          {getStatusIcon()}
          <h4 className="text-white font-medium truncate">{batch.name}</h4>
          <span className={`text-xs px-2 py-0.5 rounded-full border uppercase tracking-wider font-semibold ${getStatusColor()}`}>
            {batch.status}
          </span>
          <span className="text-xs text-slate-500 uppercase tracking-wider">{batch.source.replace('_', ' ')}</span>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-slate-400 mb-3">
          <span>Total: <strong className="text-slate-200">{batch.total_count}</strong></span>
          <span>Processed: <strong className="text-blue-400">{batch.processed_count}</strong></span>
          <span>Failed: <strong className="text-red-400">{batch.failed_count}</strong></span>
          <span>Flagged: <strong className="text-amber-400">{batch.flagged_count}</strong></span>
        </div>

        {/* Progress bar */}
        <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${batch.status === 'failed' ? 'bg-red-500' : 'bg-blue-500'}`}
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>
      
      <div className="flex items-center gap-3 md:pl-4 md:border-l border-slate-700">
        <a
          href={batchService.getBatchDownloadUrl(batch.id)}
          download
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            batch.status === 'completed' || batch.status === 'partially_failed'
              ? 'bg-slate-700 hover:bg-slate-600 text-white'
              : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
          }`}
          onClick={(e) => {
            if (batch.status !== 'completed' && batch.status !== 'partially_failed') e.preventDefault();
          }}
        >
          <Download className="w-4 h-4" />
          ZIP
        </a>
      </div>
    </div>
  );
};
