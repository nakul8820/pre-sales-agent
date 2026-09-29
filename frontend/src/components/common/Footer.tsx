import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '1.75rem 1.5rem',
        background: 'rgba(9, 13, 22, 0.95)',
        textAlign: 'center',
        fontSize: '0.825rem',
        color: 'var(--text-muted)',
      }}
    >
      <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <span>Prospect Digital Analyzer © 2026. Automated B2B Website Audit & Pitch Engine.</span>
        </div>
        <div style={{ display: 'flex', gap: '1.5rem' }}>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            style={{ color: 'var(--primary-500)', textDecoration: 'none' }}
          >
            FastAPI Swagger Docs
          </a>
          <a
            href="http://localhost:8000/redoc"
            target="_blank"
            rel="noreferrer"
            style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}
          >
            ReDoc API Specs
          </a>
        </div>
      </div>
    </footer>
  );
};
