import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  icon,
  action,
  children,
  className = '',
  style = {},
}) => {
  return (
    <div className={`glass-card ${className}`} style={style}>
      {(title || icon || action) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1.25rem',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '0.85rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {icon && (
              <div
                style={{
                  color: 'var(--primary-500)',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                {icon}
              </div>
            )}
            <div>
              {title && (
                <h3
                  style={{
                    fontSize: '1.05rem',
                    fontWeight: 700,
                    color: 'var(--text-primary)',
                  }}
                >
                  {title}
                </h3>
              )}
              {subtitle && (
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div>{children}</div>
    </div>
  );
};
