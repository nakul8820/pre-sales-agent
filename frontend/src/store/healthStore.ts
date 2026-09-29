import { create } from 'zustand';
import { HealthData, healthService } from '../services/healthService';

interface HealthState {
  health: HealthData | null;
  isLoading: boolean;
  error: string | null;
  lastChecked: Date | null;
  fetchHealth: () => Promise<void>;
}

export const useHealthStore = create<HealthState>((set) => ({
  health: null,
  isLoading: false,
  error: null,
  lastChecked: null,

  fetchHealth: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await healthService.getHealth();
      set({ health: data, isLoading: false, lastChecked: new Date(), error: null });
    } catch (err: any) {
      set({
        isLoading: false,
        error: err?.message || 'Failed to connect to backend API server',
        health: null,
      });
    }
  },
}));
