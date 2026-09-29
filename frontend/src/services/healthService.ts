import apiClient from './api';

export interface ServiceStatus {
  database: string;
  redis: string;
}

export interface HealthData {
  status: 'healthy' | 'degraded';
  timestamp: string;
  environment: string;
  version: string;
  services: ServiceStatus;
}

export const healthService = {
  getHealth: async (): Promise<HealthData> => {
    const response = await apiClient.get<HealthData>('/health');
    return response.data;
  },
};
