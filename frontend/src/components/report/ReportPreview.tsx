import React, { useState } from 'react';
import { ExternalLink, FileText, Download, X } from 'lucide-react';
import { reportService } from '../../services/reportService';

interface ReportPreviewProps {
  prospectId: string;
  onClose: () => void;
}

export const ReportPreview: React.FC<ReportPreviewProps> = ({ prospectId, onClose }) => {
  const previewUrl = reportService.getPreviewUrl(prospectId);
  const pdfUrl = reportService.getPdfUrl(prospectId);
  const docxUrl = reportService.getDocxUrl(prospectId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 md:p-8">
      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full h-full max-w-6xl flex flex-col overflow-hidden">
        
        {/* Header toolbar */}
        <div className="h-16 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-900/50">
          <div className="flex items-center gap-2 text-slate-300">
            <FileText className="w-5 h-5 text-blue-400" />
            <h3 className="font-medium">Audit Report Preview</h3>
          </div>
          
          <div className="flex items-center gap-3">
            <a
              href={pdfUrl}
              download
              className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-slate-700"
            >
              <Download className="w-4 h-4" />
              PDF
            </a>
            <a
              href={docxUrl}
              download
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              <Download className="w-4 h-4" />
              Word (DOCX)
            </a>
            <div className="w-px h-6 bg-slate-700 mx-2" />
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Iframe container */}
        <div className="flex-1 bg-white relative">
          <iframe 
            src={previewUrl} 
            className="w-full h-full border-none"
            title="Report Preview"
          />
        </div>
      </div>
    </div>
  );
};
