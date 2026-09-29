import { useEffect } from 'react';
import { useHealthStore } from '../store/healthStore';

export const useHealth = (pollIntervalMs: number = 10000) => {
  const { health, isLoading, error, lastChecked, fetchHealth } = useHealthStore();

  useEffect(() => {
    fetchHealth();
    if (pollIntervalMs > 0) {
      const interval = setInterval(() => {
        fetchHealth();
      }, pollIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchHealth, pollIntervalMs]);

  return { health, isLoading, error, lastChecked, refetch: fetchHealth };
};
