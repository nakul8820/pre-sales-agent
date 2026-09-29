import React, { useState, useEffect } from 'react';
import { Database, Loader2, XCircle } from 'lucide-react';
import { batchService, BatchJobRead } from '../../services/batchService';

interface HubSpotPickerProps {
  onBatchStarted: (batch: BatchJobRead) => void;
}

interface HubSpotList {
  id: string;
  name: string;
}

export const HubSpotPicker: React.FC<HubSpotPickerProps> = ({ onBatchStarted }) => {
  const [lists, setLists] = useState<HubSpotList[]>([]);
  const [selectedList, setSelectedList] = useState('');
  const [batchName, setBatchName] = useState('');
  const [isLoadingLists, setIsLoadingLists] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLists = async () => {
      setIsLoadingLists(true);
      try {
        const data = await batchService.getHubSpotLists();
        setLists(data.items);
        if (data.items.length > 0) {
          setSelectedList(data.items[0].id);
        }
      } catch (err: any) {
        setError('Failed to load HubSpot lists. Ensure token is configured.');
      } finally {
        setIsLoadingLists(false);
      }
    };
    fetchLists();
  }, []);

  const handleSubmit = async () => {
    if (!selectedList || !batchName) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const batch = await batchService.submitHubSpotBatch(batchName, selectedList);
      onBatchStarted(batch);
      setBatchName('');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Import failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 flex flex-col gap-4">
      <div>
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <Database className="w-5 h-5 text-orange-400" />
          Import from HubSpot
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          Select a contact list from your HubSpot CRM to import and analyze.
        </p>
      </div>

      {isLoadingLists ? (
        <div className="py-8 flex justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-slate-500" />
        </div>
      ) : (
        <div className="flex flex-col gap-4 mt-2">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Batch Name</label>
            <input
              type="text"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Inbound Leads Aug 2026"
              value={batchName}
              onChange={(e) => setBatchName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">HubSpot List</label>
            <select
              value={selectedList}
              onChange={(e) => setSelectedList(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
            >
              <option value="" disabled>Select a list...</option>
              {lists.map(list => (
                <option key={list.id} value={list.id}>{list.name}</option>
              ))}
            </select>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-3 text-sm flex items-start gap-2 mt-2">
          <XCircle className="w-5 h-5 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div className="mt-2 flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={!selectedList || !batchName || isSubmitting || lists.length === 0}
          className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Importing...
            </>
          ) : (
            'Import & Process'
          )}
        </button>
      </div>
    </div>
  );
};
