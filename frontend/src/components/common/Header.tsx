import React from 'react';
import { Activity, ShieldCheck, Layers } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { useHealthStore } from '../../store/healthStore';

export const Header: React.FC = () => {
  const { health, isLoading } = useHealthStore();

  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(9, 13, 22, 0.8)',
        backdropFilter: 'var(--glass-blur)',
        WebkitBackdropFilter: 'var(--glass-blur)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '1rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Logo and Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              background: 'var(--primary-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-glow)',
            }}
          >
            <Layers size={22} color="#ffffff" />
          </div>
          <div>
            <h1
              style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                letterSpacing: '-0.025em',
                background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Prospect Digital Analyzer
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              B2B Sales Intelligence & Pitch Deck Engine
            </p>
          </div>
        </div>

        {/* Live System Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-subtle)',
              padding: '0.4rem 0.85rem',
              borderRadius: '9999px',
            }}
          >
            <Activity size={15} color="var(--text-secondary)" />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              API Status:
            </span>
            <StatusBadge
              status={
                isLoading
                  ? 'pending'
                  : health?.status === 'healthy'
                  ? 'healthy'
                  : 'error'
              }
              label={isLoading ? 'Checking...' : health?.status || 'Offline'}
            />
          </div>
        </div>
      </div>
    </header>
  );
};
