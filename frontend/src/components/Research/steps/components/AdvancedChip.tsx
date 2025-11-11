import React, { useState } from 'react';

interface AdvancedChipProps {
  advanced: boolean;
}

export const AdvancedChip: React.FC<AdvancedChipProps> = ({ advanced }) => {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      style={{
        position: 'relative',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Chip */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          background: advanced
            ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)'
            : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%)',
          border: `1px solid ${advanced ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.2)'}`,
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: '600',
          color: advanced ? '#10b981' : '#ef4444',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          cursor: 'default',
          boxShadow: hovered
            ? '0 2px 8px rgba(0, 0, 0, 0.12)'
            : '0 1px 3px rgba(0, 0, 0, 0.08)',
          transform: hovered ? 'translateY(-1px)' : 'translateY(0)',
          letterSpacing: '-0.01em',
        }}
      >
        <span style={{ fontSize: '13px' }}>⚙️</span>
        <span>Advanced</span>
        <span style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: advanced ? '#10b981' : '#ef4444',
          boxShadow: advanced
            ? '0 0 4px rgba(16, 185, 129, 0.4)'
            : '0 0 4px rgba(239, 68, 68, 0.4)',
        }} />
      </div>

      {/* Tooltip */}
      {hovered && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            marginTop: '8px',
            padding: '10px 12px',
            background: 'rgba(15, 23, 42, 0.95)',
            color: '#f8fafc',
            fontSize: '11px',
            lineHeight: '1.5',
            borderRadius: '8px',
            maxWidth: '240px',
            zIndex: 1000,
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.25)',
            pointerEvents: 'none',
            whiteSpace: 'normal',
            wordWrap: 'break-word',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {advanced
            ? 'Advanced mode is ON. Exa and Tavily configuration options are available.'
            : 'Advanced mode is OFF. Enable to access Exa and Tavily configuration options.'}
          <div
            style={{
              position: 'absolute',
              top: '-4px',
              left: '50%',
              transform: 'translateX(-50%) rotate(45deg)',
              width: '8px',
              height: '8px',
              background: 'rgba(15, 23, 42, 0.95)',
              borderLeft: '1px solid rgba(255, 255, 255, 0.1)',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          />
        </div>
      )}
    </div>
  );
};

