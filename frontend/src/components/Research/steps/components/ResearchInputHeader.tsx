/**
 * ResearchInputHeader Component
 * 
 * Header section with title, personalization indicator, and action buttons (Advanced toggle, Upload)
 */

import React from 'react';
import { PersonalizationIndicator } from './PersonalizationIndicator';

interface ResearchInputHeaderProps {
  hasPersona: boolean;
  advanced: boolean;
  onAdvancedChange: (advanced: boolean) => void;
  onFileUpload: () => void;
}

export const ResearchInputHeader: React.FC<ResearchInputHeaderProps> = ({
  hasPersona,
  advanced,
  onAdvancedChange,
  onFileUpload,
}) => {
  return (
    <div style={{
      marginBottom: '12px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: '12px',
    }}>
      <label style={{
        fontSize: '15px',
        fontWeight: '600',
        color: '#0c4a6e',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flex: '1',
      }}>
        <span style={{ fontSize: '20px' }}>🔍</span>
        Research Topic & Keywords
        <PersonalizationIndicator 
          type="placeholder" 
          hasPersona={hasPersona}
          source={hasPersona ? "from your research persona" : undefined}
        />
      </label>
      
      {/* Advanced Toggle and Upload Button */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        {/* Advanced Toggle */}
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            cursor: 'pointer',
            padding: '6px 10px',
            borderRadius: '8px',
            border: `1px solid ${advanced ? 'rgba(14, 165, 233, 0.3)' : 'rgba(15, 23, 42, 0.1)'}`,
            background: advanced
              ? 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)'
              : '#ffffff',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            fontSize: '11px',
            fontWeight: '600',
            color: advanced ? '#0369a1' : '#475569',
            boxShadow: advanced ? '0 1px 3px rgba(14, 165, 233, 0.12)' : '0 1px 2px rgba(0, 0, 0, 0.04)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = advanced ? 'rgba(14, 165, 233, 0.4)' : 'rgba(15, 23, 42, 0.15)';
            e.currentTarget.style.boxShadow = advanced
              ? '0 2px 4px rgba(14, 165, 233, 0.18)'
              : '0 1px 3px rgba(0, 0, 0, 0.06)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = advanced ? 'rgba(14, 165, 233, 0.3)' : 'rgba(15, 23, 42, 0.1)';
            e.currentTarget.style.boxShadow = advanced
              ? '0 1px 3px rgba(14, 165, 233, 0.12)'
              : '0 1px 2px rgba(0, 0, 0, 0.04)';
          }}
          title="Enable advanced research options (Exa and Tavily configurations)"
        >
          <input
            type="checkbox"
            checked={advanced}
            onChange={(e) => onAdvancedChange(e.target.checked)}
            style={{
              width: '14px',
              height: '14px',
              cursor: 'pointer',
              accentColor: '#0ea5e9',
            }}
          />
          <span>Advanced</span>
        </label>

        {/* Upload Button */}
        <button
          onClick={onFileUpload}
          type="button"
          style={{
            padding: '6px 10px',
            background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
            border: '1px solid rgba(14, 165, 233, 0.25)',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '11px',
            fontWeight: '600',
            color: '#0369a1',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 1px 2px rgba(14, 165, 233, 0.12)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%)';
            e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.35)';
            e.currentTarget.style.transform = 'translateY(-1px)';
            e.currentTarget.style.boxShadow = '0 2px 4px rgba(14, 165, 233, 0.18)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)';
            e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.25)';
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 1px 2px rgba(14, 165, 233, 0.12)';
          }}
          title="Upload Document"
        >
          <span style={{ fontSize: '13px' }}>📎</span>
          <span>Upload</span>
        </button>
      </div>
    </div>
  );
};
