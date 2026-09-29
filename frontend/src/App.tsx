import React, { useState, useEffect, useCallback } from 'react';
import {
  Database,
  Server,
  Zap,
  RefreshCw,
  Cpu,
  Layers,
  FileText,
  Search,
  Sliders,
  CheckCircle2,
  AlertCircle,
  PlusCircle,
  ListFilter,
  ExternalLink,
  ShieldCheck,
  Building,
  UploadCloud,
} from 'lucide-react';
import { Header } from './components/common/Header';
import { Footer } from './components/common/Footer';
import { Card } from './components/common/Card';
import { StatusBadge } from './components/common/StatusBadge';
import { WebForm } from './components/intake/WebForm';
import { ExcelUpload } from './components/intake/ExcelUpload';
import { HubSpotPicker } from './components/intake/HubSpotPicker';
import { BatchDashboard } from './components/batch/BatchDashboard';
import { ReportPreview } from './components/report/ReportPreview';
import { useHealth } from './hooks/useHealth';
import { prospectService, ProspectItem, ProspectWebFormResponse } from './services/prospectService';

type TabType = 'intake' | 'batch' | 'prospects' | 'system';

export const App: React.FC = () => {
  const { health, isLoading: isHealthLoading, error: healthError, lastChecked, refetch: refetchHealth } = useHealth(10000);

  const [activeTab, setActiveTab] = useState<TabType>('intake');
  const [prospects, setProspects] = useState<ProspectItem[]>([]);
  const [totalProspects, setTotalProspects] = useState<number>(0);
  const [isProspectsLoading, setIsProspectsLoading] = useState<boolean>(false);
  const [recentNotification, setRecentNotification] = useState<string | null>(null);
  const [reportPreviewId, setReportPreviewId] = useState<string | null>(null);

  const fetchProspects = useCallback(async () => {
    setIsProspectsLoading(true);
    try {
      const data = await prospectService.getProspects(1, 20);
      setProspects(data.items);
      setTotalProspects(data.total);
    } catch (err) {
      console.error('Failed to load prospects list:', err);
    } finally {
      setIsProspectsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProspects();
  }, [fetchProspects]);

  const handleIntakeSuccess = (res: ProspectWebFormResponse) => {
    setRecentNotification(`Prospect "${res.company_name}" (${res.domain}) saved to PostgreSQL!`);
    fetchProspects();
    setTimeout(() => setRecentNotification(null), 5000);
  };

  const handleBatchStarted = (batch: any) => {
    setRecentNotification(`Batch "${batch.name}" started!`);
    setActiveTab('batch');
    setTimeout(() => setRecentNotification(null), 5000);
  };

  const modules = [
    {
      id: 'intake',
      title: 'Intake Channels',
      icon: <Layers size={20} />,
      status: 'Sprint 3 In Progress (Web Form Live)',
      badge: 'active',
      description:
        'Manual prospect input (Sprint 3 Live), HubSpot CRM list picker, and Excel bulk upload.',
      items: ['Manual Form Input (Active)', 'HubSpot Contact/List Picker', 'Excel / CSV Batch Upload'],
    },
    {
      id: 'crawler',
      title: 'Crawler & Audit Engines',
      icon: <Search size={20} />,
      status: 'Ready for Sprint 4',
      badge: 'planned',
      description:
        'Internal multi-page crawler for lead-gen gaps, broken links, UX audits + Google PageSpeed & SEMrush APIs.',
      items: ['Lead Gen Gap Detection', 'Broken Link Crawl', 'PageSpeed & SEMrush APIs'],
    },
    {
      id: 'scoring',
      title: 'Scoring & Content Moderation',
      icon: <Sliders size={20} />,
      status: 'Ready for Sprint 5',
      badge: 'planned',
      description:
        'Weighted score synthesis across 5 categories with automated content appropriateness heuristics.',
      items: ['Weighted Score Engine', 'Content Appropriateness Heuristics', 'Critical Focus Areas'],
    },
    {
      id: 'reports',
      title: 'Multi-Format Reports',
      icon: <FileText size={20} />,
      status: 'Ready for Sprint 6',
      badge: 'planned',
      description:
        'Live interactive HTML preview, pixel-perfect PDF via WeasyPrint, and editable Word (.docx) export.',
      items: ['Live HTML Preview', 'PDF Export (WeasyPrint)', 'Word (.docx) Export'],
    },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />
      
      {reportPreviewId && (
        <ReportPreview prospectId={reportPreviewId} onClose={() => setReportPreviewId(null)} />
      )}
      
      <main className="container-custom" style={{ flex: 1, padding: '2rem 1.5rem', width: '100%' }}>
        {recentNotification && (
          <div
            style={{
              padding: '1rem',
              backgroundColor: 'var(--success-500)',
              color: 'var(--bg-card)',
              borderRadius: '0.75rem',
              marginBottom: '1.5rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              animation: 'slideDown 0.3s ease',
            }}
          >
            <CheckCircle2 size={20} />
            {recentNotification}
          </div>
        )}

        {/* Hero Section */}
        <section style={{ marginBottom: '2.5rem' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: 'var(--primary-500-alpha)',
              padding: '0.4rem 0.8rem',
              borderRadius: '2rem',
              color: 'var(--primary-500)',
              fontSize: '0.8rem',
              fontWeight: 600,
              marginBottom: '0.85rem',
            }}
          >
            <Zap size={14} /> Sprint 9 — Batch Dashboard & Reports UI
          </div>
          <h2
            style={{
              fontSize: '2.15rem',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              marginBottom: '0.5rem',
            }}
          >
            B2B Website Pitch Intelligence Engine
          </h2>
          <p
            style={{
              fontSize: '1rem',
              color: 'var(--text-secondary)',
              maxWidth: '820px',
              lineHeight: 1.5,
            }}
          >
            Upload target lists, auto-crawl websites, analyze performance and SEO, and generate dynamic PDF sales reports.
          </p>
        </section>

        {/* Tab Navigation */}
        <div
          style={{
            display: 'flex',
            gap: '0.75rem',
            borderBottom: '1px solid var(--border-subtle)',
            marginBottom: '2rem',
            paddingBottom: '0.5rem',
            flexWrap: 'wrap',
          }}
        >
          <button
            className={`btn ${activeTab === 'intake' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('intake')}
            style={{ fontSize: '0.875rem' }}
          >
            <PlusCircle size={16} /> Single Prospect
          </button>
          <button
            className={`btn ${activeTab === 'batch' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('batch')}
            style={{ fontSize: '0.875rem' }}
          >
            <Layers size={16} /> Batch Operations
          </button>
          <button
            className={`btn ${activeTab === 'prospects' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => {
              setActiveTab('prospects');
              fetchProspects();
            }}
            style={{ fontSize: '0.875rem' }}
          >
            <ListFilter size={16} /> Prospects Directory ({totalProspects})
          </button>
          <button
            className={`btn ${activeTab === 'system' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('system')}
            style={{ fontSize: '0.875rem' }}
          >
            <Cpu size={16} /> System Health & Roadmap
          </button>
        </div>

        {/* Tab 1: Single Web Form Intake */}
        {activeTab === 'intake' && (
          <section style={{ animation: 'fadeIn 0.25s ease' }}>
            <WebForm onSuccess={handleIntakeSuccess} />
          </section>
        )}

        {/* Tab 2: Batch Operations */}
        {activeTab === 'batch' && (
          <section style={{ animation: 'fadeIn 0.25s ease' }} className="flex flex-col gap-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ExcelUpload onBatchStarted={handleBatchStarted} />
              <HubSpotPicker onBatchStarted={handleBatchStarted} />
            </div>
            
            <h3 className="text-xl font-bold mt-4 mb-2 flex items-center gap-2">
              <Layers className="w-6 h-6 text-blue-500" />
              Batch History
            </h3>
            <BatchDashboard />
          </section>
        )}

        {/* Tab 3: Prospects Directory */}
        {activeTab === 'prospects' && (
          <section style={{ animation: 'fadeIn 0.25s ease' }}>
            <Card
              title="Persistent Prospects Directory"
              subtitle="All company targets stored permanently in PostgreSQL"
              icon={<Building size={20} />}
              action={
                <button
                  className="btn btn-outline"
                  onClick={fetchProspects}
                  disabled={isProspectsLoading}
                  style={{ fontSize: '0.8rem', padding: '0.4rem 0.85rem' }}
                >
                  <RefreshCw size={14} className={isProspectsLoading ? 'pulsing-dot' : ''} />
                  {isProspectsLoading ? 'Loading...' : 'Refresh List'}
                </button>
              }
            >
              {prospects.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                  <Building size={36} style={{ margin: '0 auto 1rem', opacity: 0.4 }} />
                  <p>No prospects recorded yet. Use the Intake tab to submit your first target!</p>
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Company</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Normalized Domain</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Source</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Contact</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Ingested At</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {prospects.map((p) => (
                        <tr
                          key={p.id}
                          style={{
                            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                            transition: 'background var(--transition-fast)',
                          }}
                        >
                          <td style={{ padding: '0.85rem 1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                            {p.company_name}
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <a
                              href={p.website_url}
                              target="_blank"
                              rel="noreferrer"
                              style={{ color: 'var(--accent-cyan)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                            >
                              {p.domain} <ExternalLink size={12} />
                            </a>
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <span
                              style={{
                                textTransform: 'uppercase',
                                fontSize: '0.7rem',
                                fontWeight: 700,
                                padding: '0.15rem 0.45rem',
                                borderRadius: '0.3rem',
                                background: 'rgba(255, 255, 255, 0.05)',
                                color: 'var(--text-secondary)',
                              }}
                            >
                              {p.source}
                            </span>
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <StatusBadge status={p.status === 'completed' ? 'healthy' : p.status === 'moderation_flagged' ? 'error' : 'pending'} label={p.status} />
                          </td>
                          <td style={{ padding: '0.85rem 1rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                            {p.contact_name || p.contact_email || '—'}
                          </td>
                          <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                            {new Date(p.created_at).toLocaleDateString()} {new Date(p.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            {p.status === 'completed' && (
                              <button
                                onClick={() => setReportPreviewId(p.id)}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-600/30 rounded text-xs font-medium transition-colors"
                              >
                                <FileText className="w-3.5 h-3.5" />
                                View Report
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </section>
        )}

        {/* Tab 3: System Telemetry & Architecture */}
        {activeTab === 'system' && (
          <section style={{ animation: 'fadeIn 0.25s ease' }}>
            {/* System Health Card */}
            <div style={{ marginBottom: '2rem' }}>
              <Card
                title="System Health & Core Telemetry"
                subtitle="Real-time connectivity to FastAPI, PostgreSQL, and Redis"
                icon={<Cpu size={22} />}
                action={
                  <button
                    className="btn btn-outline"
                    onClick={() => refetchHealth()}
                    disabled={isHealthLoading}
                    style={{ fontSize: '0.8rem', padding: '0.4rem 0.85rem' }}
                  >
                    <RefreshCw size={14} className={isHealthLoading ? 'pulsing-dot' : ''} />
                    {isHealthLoading ? 'Refreshing...' : 'Refresh Status'}
                  </button>
                }
              >
                {healthError ? (
                  <div
                    style={{
                      background: 'var(--status-danger-bg)',
                      border: '1px solid var(--status-danger)',
                      padding: '1rem',
                      borderRadius: '0.5rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                    }}
                  >
                    <AlertCircle size={20} color="var(--status-danger)" />
                    <span>{healthError}</span>
                  </div>
                ) : (
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                      gap: '1.25rem',
                    }}
                  >
                    <div
                      style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--border-subtle)',
                        padding: '1.25rem',
                        borderRadius: '0.75rem',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>FastAPI API Server</span>
                        <StatusBadge
                          status={health?.status === 'healthy' ? 'healthy' : 'degraded'}
                          label={health?.status || 'Waiting...'}
                        />
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                        Env: <strong>{health?.environment}</strong> | v{health?.version}
                      </div>
                    </div>

                    <div
                      style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--border-subtle)',
                        padding: '1.25rem',
                        borderRadius: '0.75rem',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>PostgreSQL 16</span>
                        <StatusBadge
                          status={health?.services.database === 'connected' ? 'connected' : 'error'}
                          label={health?.services.database || 'Connecting...'}
                        />
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                        Persistent Storage Active
                      </div>
                    </div>

                    <div
                      style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--border-subtle)',
                        padding: '1.25rem',
                        borderRadius: '0.75rem',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Redis & Celery</span>
                        <StatusBadge
                          status={health?.services.redis === 'connected' ? 'connected' : 'error'}
                          label={health?.services.redis || 'Connecting...'}
                        />
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                        Broker & Cache Ready
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            </div>

            {/* Architecture Roadmap Grid */}
            <div>
              <div style={{ marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>System Architecture & Roadmap</h3>
              </div>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '1.5rem',
                }}
              >
                {modules.map((mod) => (
                  <Card key={mod.id} title={mod.title} icon={mod.icon}>
                    <p
                      style={{
                        fontSize: '0.85rem',
                        color: 'var(--text-secondary)',
                        marginBottom: '1rem',
                        lineHeight: 1.5,
                      }}
                    >
                      {mod.description}
                    </p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {mod.items.map((item, idx) => (
                        <div
                          key={idx}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            fontSize: '0.8rem',
                            color: 'var(--text-muted)',
                          }}
                        >
                          <CheckCircle2 size={14} color="var(--primary-500)" />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
};
export default App;
