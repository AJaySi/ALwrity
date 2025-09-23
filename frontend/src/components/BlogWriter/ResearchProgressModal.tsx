import React from 'react';

interface ResearchProgressModalProps {
  open: boolean;
  title?: string;
  status?: string;
  messages: Array<{ timestamp: string; message: string }>;
  error?: string | null;
  onClose: () => void;
}

const ResearchProgressModal: React.FC<ResearchProgressModalProps> = ({
  open,
  title = 'Research in progress',
  status,
  messages,
  error,
  onClose
}) => {
  if (!open) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.55)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000
    }}>
      <div style={{
        width: '92%',
        maxWidth: 900,
        maxHeight: '82vh',
        background: 'white',
        borderRadius: 16,
        overflow: 'hidden',
        boxShadow: '0 24px 60px rgba(0,0,0,0.3)',
        border: '1px solid #e5e7eb'
      }}>
        {/* Header with background illustration */}
        <div style={{
          position: 'relative',
          padding: '28px 28px 24px 28px',
          background: '#f8fafc'
        }}>
          <div style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: 'url(/blog-writer-bg.png)',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'left center',
            backgroundSize: '38% auto',
            opacity: 0.12
          }} />
          <div style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: 20, color: '#111827' }}>{title}</h3>
              <p style={{ margin: '6px 0 0 0', color: '#6b7280', fontSize: 13 }}>We are gathering sources, extracting insights, and preparing high‑quality research.</p>
              {status && (
                <div style={{ marginTop: 8, fontSize: 12, color: '#374151' }}>Status: {status}</div>
              )}
            </div>
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: '1px solid #e5e7eb',
                borderRadius: 10,
                padding: '8px 12px',
                cursor: 'pointer',
                color: '#374151'
              }}
            >
              Close
            </button>
          </div>
        </div>

        {/* Messages list */}
        <div style={{ padding: 20 }}>
          <div style={{
            border: '1px solid #e5e7eb',
            borderRadius: 12,
            overflow: 'hidden',
            background: '#ffffff'
          }}>
            <div style={{ maxHeight: '48vh', overflowY: 'auto' }}>
              {messages.length === 0 && (
                <div style={{ padding: 16, color: '#6b7280', fontSize: 14 }}>Awaiting progress updates…</div>
              )}
              {messages.map((m, idx) => (
                <div key={idx} style={{ display: 'flex', gap: 12, padding: '12px 16px', borderTop: idx === 0 ? 'none' : '1px solid #f3f4f6' }}>
                  <div style={{ color: '#9ca3af', minWidth: 120, fontSize: 12 }}>{new Date(m.timestamp).toLocaleTimeString()}</div>
                  <div style={{ color: '#374151', fontSize: 14 }}>{m.message}</div>
                </div>
              ))}
            </div>
          </div>

          {error && (
            <div style={{ marginTop: 12, color: '#b91c1c', fontSize: 13 }}>Error: {error}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResearchProgressModal;


