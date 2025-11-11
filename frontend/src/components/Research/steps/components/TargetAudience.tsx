import React from 'react';

interface TargetAudienceProps {
  value: string;
  onChange: (value: string) => void;
}

export const TargetAudience: React.FC<TargetAudienceProps> = ({ value, onChange }) => {
  return (
    <div>
      <label style={{
        display: 'block',
        marginBottom: '8px',
        fontSize: '13px',
        fontWeight: '600',
        color: '#0c4a6e',
      }}>
        Target Audience (Optional)
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g., Marketing professionals, Tech enthusiasts, Business owners"
        style={{
          width: '100%',
          padding: '10px 12px',
          fontSize: '13px',
          border: '1px solid rgba(14, 165, 233, 0.2)',
          borderRadius: '10px',
          background: 'rgba(255, 255, 255, 0.9)',
          color: '#0f172a',
          transition: 'all 0.2s ease',
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.5)';
          e.currentTarget.style.boxShadow = '0 0 0 3px rgba(14, 165, 233, 0.1)';
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
          e.currentTarget.style.boxShadow = 'none';
        }}
      />
    </div>
  );
};

