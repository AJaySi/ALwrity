import React from 'react';
import { formatKeyword } from '../../../../utils/keywordExpansion';

interface CurrentKeywordsProps {
  keywords: string[];
  onRemoveKeyword: (keyword: string) => void;
}

export const CurrentKeywords: React.FC<CurrentKeywordsProps> = ({ keywords, onRemoveKeyword }) => {
  if (keywords.length === 0) return null;

  return (
    <div style={{
      marginTop: '12px',
      padding: '10px',
      background: 'rgba(241, 245, 249, 0.5)',
      border: '1px solid rgba(203, 213, 225, 0.3)',
      borderRadius: '8px',
    }}>
      <div style={{
        fontSize: '12px',
        fontWeight: '600',
        color: '#475569',
        marginBottom: '8px',
      }}>
        Current Keywords ({keywords.length})
      </div>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '6px',
      }}>
        {keywords.map((keyword, idx) => (
          <div
            key={idx}
            style={{
              padding: '5px 10px',
              background: 'white',
              border: '1px solid rgba(203, 213, 225, 0.5)',
              borderRadius: '6px',
              fontSize: '12px',
              color: '#334155',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span>{formatKeyword(keyword)}</span>
            <button
              onClick={() => onRemoveKeyword(keyword)}
              style={{
                background: 'none',
                border: 'none',
                color: '#ef4444',
                cursor: 'pointer',
                fontSize: '14px',
                padding: '0',
                width: '16px',
                height: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '50%',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'none';
              }}
              title="Remove keyword"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

