import { useState, useEffect, useCallback } from 'react';
import { batchService, BatchJobRead } from '../services/batchService';

export function useBatchStatus(batchId: string | null, pollingIntervalMs = 3000) {
  const [batch, setBatch] = useState<BatchJobRead | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!batchId) return;
    try {
      const data = await batchService.getBatchStatus(batchId);
      setBatch(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    }
  }, [batchId]);

  useEffect(() => {
    fetchStatus();

    let intervalId: ReturnType<typeof setInterval>;
    
    // Only poll if the batch is in a non-terminal state
    if (batchId && batch && ['queued', 'running'].includes(batch.status)) {
      intervalId = setInterval(fetchStatus, pollingIntervalMs);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [batchId, batch?.status, fetchStatus, pollingIntervalMs]);

  return { batch, error, fetchStatus };
}
