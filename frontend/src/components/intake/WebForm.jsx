import React, { useState, useMemo } from 'react';
import {
  Building2,
  Globe,
  User,
  Mail,
  Briefcase,
  Phone,
  FileText,
  Send,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  RotateCcw,
  Sparkles,
  Zap,
  TrendingUp,
  Search,
  Activity,
  Award,
  Layers,
  Link2,
  Smartphone,
  MessageSquare,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import { prospectService } from '../../services/prospectService';
import { StatusBadge } from '../common/StatusBadge';

export const WebForm = ({ onSuccess }) => {
  // Form State
  const [companyName, setCompanyName] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [contactName, setContactName] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactTitle, setContactTitle] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [notes, setNotes] = useState('');

  // UI State
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successData, setSuccessData] = useState(null);
  const [isCopied, setIsCopied] = useState(false);

  // Live extracted domain preview
  const previewDomain = useMemo(() => {
    if (!websiteUrl.trim()) return '';
    try {
      let val = websiteUrl.trim().toLowerCase();
      if (!val.startsWith('http://') && !val.startsWith('https://')) {
        val = 'https://' + val;
      }
      const parsed = new URL(val);
      let domain = parsed.hostname;
      if (domain.startsWith('www.')) {
        domain = domain.substring(4);
      }
      return domain;
    } catch {
      return '';
    }
  }, [websiteUrl]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!companyName.trim()) {
      setError('Company Name is required.');
      return;
    }
    if (!websiteUrl.trim()) {
      setError('Website URL is required.');
      return;
    }

    setIsLoading(true);
    try {
      const result = await prospectService.submitWebForm({
        company_name: companyName.trim(),
        website_url: websiteUrl.trim(),
        contact_name: contactName.trim() || undefined,
        contact_email: contactEmail.trim() || undefined,
        contact_title: contactTitle.trim() || undefined,
        contact_phone: contactPhone.trim() || undefined,
        notes: notes.trim() || undefined,
      });

      setSuccessData(result);
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err) {
      console.error('Submission & analysis failed:', err);
      const detailMsg =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        'Failed to process prospect intake and analysis.';
      setError(typeof detailMsg === 'string' ? detailMsg : JSON.stringify(detailMsg));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyId = () => {
    if (successData?.prospect_id) {
      navigator.clipboard.writeText(successData.prospect_id);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const handleReset = () => {
    setCompanyName('');
    setWebsiteUrl('');
    setContactName('');
    setContactEmail('');
    setContactTitle('');
    setContactPhone('');
    setNotes('');
    setSuccessData(null);
    setError(null);
  };

  const renderScoreColor = (score) => {
    const s = score || 0;
    if (s >= 80) return 'var(--status-success)';
    if (s >= 50) return 'var(--status-warning)';
    return 'var(--status-danger)';
  };

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        backdropFilter: 'var(--glass-blur)',
        WebkitBackdropFilter: 'var(--glass-blur)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '1rem',
        padding: '2rem',
        boxShadow: 'var(--shadow-lg)',
        maxWidth: '960px',
        margin: '0 auto',
      }}
    >
      {/* Form Header */}
      <div style={{ marginBottom: '1.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'var(--primary-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-glow)',
            }}
          >
            <Sparkles size={20} color="#fff" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Single Prospect Intake, Scoring & Safety Gate
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Runs PageSpeed, SEMrush, Logo, Crawler, Weighted Scoring Engine, and Content Appropriateness moderation.
            </p>
          </div>
        </div>
      </div>

      {/* Success Confirmation & 5-Category Scorecard */}
      {successData ? (
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.9)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '0.75rem',
            padding: '1.75rem',
            animation: 'fadeIn 0.3s ease',
            boxShadow: 'var(--shadow-glow)',
          }}
        >
          {/* Content Moderation Safety Alert Banner */}
          {successData.moderation && (
            <div
              style={{
                background: successData.moderation.is_safe ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.12)',
                border: `1px solid ${successData.moderation.is_safe ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.4)'}`,
                borderRadius: '0.6rem',
                padding: '0.85rem 1.15rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                {successData.moderation.is_safe ? (
                  <ShieldCheck size={20} color="var(--status-success)" />
                ) : (
                  <ShieldAlert size={20} color="var(--status-danger)" />
                )}
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: successData.moderation.is_safe ? 'var(--status-success)' : 'var(--status-danger)' }}>
                    {successData.moderation.is_safe ? 'Content Appropriateness: Approved for Pitching' : 'Safety Gate Alert: Inappropriate Content Flagged'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {successData.moderation.is_safe
                      ? 'Automated safety heuristics verified domain is suitable for commercial sales outreach.'
                      : `Pre-report gate flagged ${successData.moderation.flags_count} issue(s). Outreach should be reviewed.`}
                  </div>
                </div>
              </div>

              {successData.moderation.flags && successData.moderation.flags.length > 0 && (
                <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                  {successData.moderation.flags.map((f, i) => (
                    <span
                      key={i}
                      style={{
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        background: 'var(--status-danger-bg)',
                        color: 'var(--status-danger)',
                      }}
                    >
                      {f.category} ({Math.round(f.confidence_score * 100)}% conf)
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Header Banner */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
              {successData.logo_url && (
                <img
                  src={successData.logo_url}
                  alt={successData.company_name}
                  style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '8px',
                    objectFit: 'contain',
                    background: '#ffffff',
                    padding: '4px',
                    border: '1px solid var(--border-subtle)',
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              )}
              <div>
                <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ffffff' }}>
                  {successData.company_name}
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.2rem' }}>
                  <a
                    href={successData.website_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 600 }}
                  >
                    {successData.domain}
                  </a>
                  <StatusBadge
                    status={successData.status === 'flagged' ? 'warning' : 'healthy'}
                    label={successData.status === 'flagged' ? 'Flagged Prospect' : 'Evaluated & Scored'}
                  />
                  {successData.crawler_data && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      ({successData.crawler_data.pages_crawled_count} pages crawled)
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Copy Prospect ID */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <code
                style={{
                  background: 'rgba(99, 102, 241, 0.15)',
                  color: 'var(--primary-500)',
                  padding: '0.3rem 0.65rem',
                  borderRadius: '0.4rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                }}
              >
                ID: {successData.prospect_id.slice(0, 8)}...
              </code>
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleCopyId}
                style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                title="Copy Full UUID"
              >
                {isCopied ? <Check size={13} color="var(--status-success)" /> : <Copy size={13} />}
                {isCopied ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>

          {/* Overall Score Highlight Banner with Letter Grade */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.18) 0%, rgba(6, 182, 212, 0.15) 100%)',
              border: '1px solid rgba(99, 102, 241, 0.45)',
              borderRadius: '0.75rem',
              padding: '1.25rem 1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1.5rem',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div>
              <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', fontWeight: 700 }}>
                Synthesized Digital Pitch Score
              </span>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff' }}>
                Client Pitch Readiness Score
              </h3>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
              {/* Grade Badge */}
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '0.6rem',
                  padding: '0.4rem 0.85rem',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                  Rating
                </div>
                <div style={{ fontSize: '1.6rem', fontWeight: 900, color: renderScoreColor(successData.overall_score) }}>
                  Grade {successData.letter_grade || 'B'}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                  {successData.grade_label || 'Good'}
                </div>
              </div>

              {/* Number Score */}
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.35rem' }}>
                <span style={{ fontSize: '2.75rem', fontWeight: 900, color: renderScoreColor(successData.overall_score) }}>
                  {successData.overall_score ?? '—'}
                </span>
                <span style={{ fontSize: '1.1rem', color: 'var(--text-muted)', fontWeight: 600 }}>/100</span>
              </div>
            </div>
          </div>

          {/* 5-Category Score Breakdown Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
              gap: '0.85rem',
              marginBottom: '1.5rem',
            }}
          >
            {/* 1. Performance */}
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', padding: '1rem', borderRadius: '0.6rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary-500)', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>
                <Zap size={15} /> Performance (25%)
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: renderScoreColor(successData.performance_score) }}>
                {successData.performance_score ?? '—'}/100
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                LCP: {successData.pagespeed_data?.core_web_vitals?.lcp_ms || 2800}ms
              </div>
            </div>

            {/* 2. SEO */}
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', padding: '1rem', borderRadius: '0.6rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-cyan)', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>
                <TrendingUp size={15} /> SEO Search (25%)
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: renderScoreColor(successData.seo_score) }}>
                {successData.seo_score ?? '—'}/100
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                {successData.semrush_data?.organic_traffic?.toLocaleString() || '0'} Organic Visits
              </div>
            </div>

            {/* 3. Lead Generation */}
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', padding: '1rem', borderRadius: '0.6rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#10b981', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>
                <MessageSquare size={15} /> Lead Gen (25%)
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: renderScoreColor(successData.lead_gen_score) }}>
                {successData.lead_gen_score ?? '—'}/100
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Forms: {successData.crawler_data?.lead_gen?.has_contact_form ? 'Yes' : 'Missing'}
              </div>
            </div>

            {/* 4. UI/UX & Technical */}
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', padding: '1rem', borderRadius: '0.6rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#eab308', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>
                <Smartphone size={15} /> UI/UX (15%)
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: renderScoreColor(successData.ui_ux_score) }}>
                {successData.ui_ux_score ?? '—'}/100
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Alt: {successData.crawler_data?.ui_ux?.alt_coverage_percent || 100}% Coverage
              </div>
            </div>

            {/* 5. Broken Links */}
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', padding: '1rem', borderRadius: '0.6rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f43f5e', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>
                <Link2 size={15} /> Broken Links (10%)
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: renderScoreColor(successData.broken_links_score) }}>
                {successData.broken_links_score ?? '—'}/100
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                {successData.crawler_data?.broken_links?.broken_links_count || 0} Dead Links
              </div>
            </div>
          </div>

          {/* Critical Focus Areas & Pitch Angles */}
          {successData.critical_focus_areas && successData.critical_focus_areas.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h5 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '0.65rem', textTransform: 'uppercase' }}>
                Areas Requiring Critical Focus ({successData.critical_focus_areas.length} Prioritized Findings):
              </h5>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {successData.critical_focus_areas.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-subtle)',
                      padding: '0.75rem 1rem',
                      borderRadius: '0.5rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.3rem',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span
                          style={{
                            padding: '0.15rem 0.45rem',
                            borderRadius: '4px',
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            background: item.severity === 'high' ? 'var(--status-danger-bg)' : 'var(--status-warning-bg)',
                            color: item.severity === 'high' ? 'var(--status-danger)' : 'var(--status-warning)',
                          }}
                        >
                          {item.category}
                        </span>
                        <strong style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>{item.title}</strong>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.impact}</span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0.2rem 0' }}>
                      {item.description}
                    </p>
                    {item.pitch_angle && (
                      <div style={{ fontSize: '0.775rem', color: 'var(--primary-500)', fontWeight: 600 }}>
                        💡 Sales Pitch Angle: {item.pitch_angle}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Bar */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button type="button" className="btn btn-primary" onClick={handleReset}>
              <RotateCcw size={15} /> Ingest Another Prospect
            </button>
          </div>
        </div>
      ) : (
        /* Form Entry */
        <form onSubmit={handleSubmit}>
          {error && (
            <div
              style={{
                background: 'var(--status-danger-bg)',
                border: '1px solid var(--status-danger)',
                padding: '0.85rem 1.25rem',
                borderRadius: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.65rem',
                marginBottom: '1.5rem',
                fontSize: '0.875rem',
                color: '#ffffff',
              }}
            >
              <AlertCircle size={18} color="var(--status-danger)" />
              <span>{error}</span>
            </div>
          )}

          {/* Core Required Section */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
            <div>
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.825rem',
                  fontWeight: 600,
                  marginBottom: '0.4rem',
                  color: 'var(--text-secondary)',
                }}
              >
                <Building2 size={15} /> Company Name <span style={{ color: 'var(--status-danger)' }}>*</span>
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g. Linear / Vercel"
                required
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '0.5rem',
                  padding: '0.65rem 0.85rem',
                  color: '#ffffff',
                  fontSize: '0.9rem',
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <label
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    fontSize: '0.825rem',
                    fontWeight: 600,
                    color: 'var(--text-secondary)',
                  }}
                >
                  <Globe size={15} /> Website URL <span style={{ color: 'var(--status-danger)' }}>*</span>
                </label>
                {previewDomain && (
                  <span
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--accent-cyan)',
                      background: 'rgba(6, 182, 212, 0.12)',
                      padding: '0.1rem 0.5rem',
                      borderRadius: '9999px',
                      border: '1px solid rgba(6, 182, 212, 0.25)',
                    }}
                  >
                    Domain: {previewDomain}
                  </span>
                )}
              </div>
              <input
                type="text"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="e.g. https://linear.app"
                required
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '0.5rem',
                  padding: '0.65rem 0.85rem',
                  color: '#ffffff',
                  fontSize: '0.9rem',
                  outline: 'none',
                }}
              />
            </div>
          </div>

          {/* Contact Details (Optional) */}
          <div
            style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '0.75rem',
              padding: '1.25rem',
              marginBottom: '1.25rem',
            }}
          >
            <h4
              style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: 'var(--text-secondary)',
                marginBottom: '1rem',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Primary Contact Details (Optional)
            </h4>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  <User size={14} /> Contact Name
                </label>
                <input
                  type="text"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  placeholder="e.g. Karri Saarinen"
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.7)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '0.4rem',
                    padding: '0.55rem 0.75rem',
                    color: '#fff',
                    fontSize: '0.85rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  <Mail size={14} /> Contact Email
                </label>
                <input
                  type="email"
                  value={contactEmail}
                  onChange={(e) => setContactEmail(e.target.value)}
                  placeholder="karri@linear.app"
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.7)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '0.4rem',
                    padding: '0.55rem 0.75rem',
                    color: '#fff',
                    fontSize: '0.85rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  <Briefcase size={14} /> Job Title
                </label>
                <input
                  type="text"
                  value={contactTitle}
                  onChange={(e) => setContactTitle(e.target.value)}
                  placeholder="e.g. CEO"
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.7)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '0.4rem',
                    padding: '0.55rem 0.75rem',
                    color: '#fff',
                    fontSize: '0.85rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  <Phone size={14} /> Phone Number
                </label>
                <input
                  type="text"
                  value={contactPhone}
                  onChange={(e) => setContactPhone(e.target.value)}
                  placeholder="+1 (555) 000-1122"
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.7)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '0.4rem',
                    padding: '0.55rem 0.75rem',
                    color: '#fff',
                    fontSize: '0.85rem',
                    outline: 'none',
                  }}
                />
              </div>
            </div>
          </div>

          {/* Notes Section */}
          <div style={{ marginBottom: '1.75rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.825rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              <FileText size={15} /> Notes & Pitch Strategy (Optional)
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Target prospect for web app optimization and lead funnel expansion..."
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '0.5rem',
                padding: '0.65rem 0.85rem',
                color: '#ffffff',
                fontSize: '0.85rem',
                outline: 'none',
                resize: 'vertical',
              }}
            />
          </div>

          {/* Submit Button */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.85rem' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
              style={{ minWidth: '240px', fontSize: '0.9rem', padding: '0.75rem 1.5rem' }}
            >
              {isLoading ? (
                <>
                  <span className="pulsing-dot" style={{ backgroundColor: '#fff' }} />
                  Evaluating, Scoring & Gating...
                </>
              ) : (
                <>
                  <Send size={16} /> Run Full Digital Pitch Audit
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default WebForm;
