import api from './api';
import { ProspectWebFormResponse } from './prospectService';

export interface BatchJobRead {
  id: string;
  name: string;
  source: 'excel_upload' | 'hubspot' | 'manual_bulk';
  status: 'queued' | 'running' | 'completed' | 'partially_failed' | 'failed' | 'cancelled';
  total_count: number;
  processed_count: number;
  failed_count: number;
  flagged_count: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface BatchJobListResponse {
  items: BatchJobRead[];
  total: number;
  page: number;
  page_size: number;
}

export const batchService = {
  submitExcelBatch: async (name: string, file: File): Promise<BatchJobRead> => {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);
    
    const response = await api.post<BatchJobRead>('/batch/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getHubSpotLists: async (): Promise<{ items: { id: string; name: string }[] }> => {
    const response = await api.get<{ items: { id: string; name: string }[] }>('/batch/hubspot/lists');
    return response.data;
  },

  submitHubSpotBatch: async (name: string, listId: string): Promise<BatchJobRead> => {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('list_id', listId);
    
    const response = await api.post<BatchJobRead>('/batch/hubspot', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  getBatchStatus: async (id: string): Promise<BatchJobRead> => {
    const response = await api.get<BatchJobRead>(`/batch/status/${id}`);
    return response.data;
  },

  listBatches: async (page = 1, limit = 20): Promise<BatchJobListResponse> => {
    const response = await api.get<BatchJobListResponse>(`/batch/?page=${page}&limit=${limit}`);
    return response.data;
  },

  getBatchDownloadUrl: (id: string): string => {
    // Return full URL for anchor tag downloading
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/batch/download/${id}/zip`;
  }
};
