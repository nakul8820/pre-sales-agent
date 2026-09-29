import React from 'react';

interface StatusBadgeProps {
  status: 'connected' | 'healthy' | 'degraded' | 'error' | 'pending' | 'offline';
  label?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  const isHealthy = status === 'connected' || status === 'healthy';
  const isWarning = status === 'degraded' || status === 'pending';

  const badgeBg = isHealthy
    ? 'var(--status-success-bg)'
    : isWarning
    ? 'var(--status-warning-bg)'
    : 'var(--status-danger-bg)';

  const dotColor = isHealthy
    ? 'var(--status-success)'
    : isWarning
    ? 'var(--status-warning)'
    : 'var(--status-danger)';

  const textColor = isHealthy
    ? 'var(--status-success)'
    : isWarning
    ? 'var(--status-warning)'
    : 'var(--status-danger)';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.45rem',
        padding: '0.25rem 0.65rem',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: badgeBg,
        color: textColor,
        border: `1px solid ${dotColor}33`,
        textTransform: 'capitalize',
      }}
    >
      <span
        className="pulsing-dot"
        style={{
          backgroundColor: dotColor,
        }}
      />
      {label || status}
    </span>
  );
};
