import api from './api';

export interface ReportMeta {
  status: string;
  overall_score: number | null;
  links: {
    preview: string;
    pdf: string;
    docx: string;
  };
}

export const reportService = {
  getReportMeta: async (prospectId: string): Promise<ReportMeta> => {
    const response = await api.get<ReportMeta>(`/reports/${prospectId}`);
    return response.data;
  },

  getPreviewUrl: (prospectId: string): string => {
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/${prospectId}/preview`;
  },

  getPdfUrl: (prospectId: string): string => {
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/${prospectId}/pdf`;
  },

  getDocxUrl: (prospectId: string): string => {
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/${prospectId}/docx`;
  }
};
