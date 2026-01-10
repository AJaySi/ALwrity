import React from 'react';
import { BlogResearchResponse } from '../../../services/blogWriterApi';

interface DebugConsoleProps {
  showDebug: boolean;
  results: BlogResearchResponse | null;
  onToggleDebug: (show: boolean) => void;
}

export const DebugConsole: React.FC<DebugConsoleProps> = ({
  showDebug,
  results,
  onToggleDebug,
}) => {
  return (
    <div className="card-hover" style={{
      background: 'rgba(255, 255, 255, 0.8)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(14, 165, 233, 0.2)',
      borderRadius: '16px',
      padding: '20px',
      boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
      animation: 'fadeInUp 0.8s ease-out',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
          }}>
            🐛
          </div>
          <h3 style={{ margin: 0, color: '#0c4a6e', fontSize: '18px', fontWeight: '600' }}>
            Debug Console
          </h3>
        </div>
        <label style={{ 
          cursor: 'pointer', 
          fontSize: '12px',
          color: '#64748b',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <input
            type="checkbox"
            checked={showDebug}
            onChange={(e) => onToggleDebug(e.target.checked)}
            style={{ 
              marginRight: '0',
              width: '14px',
              height: '14px',
              cursor: 'pointer',
            }}
          />
          Show Data
        </label>
      </div>

      {showDebug && (
        <div style={{
          background: 'rgba(15, 23, 42, 0.05)',
          borderRadius: '10px',
          padding: '12px',
          fontSize: '11px',
          fontFamily: "'Fira Code', 'Monaco', monospace",
          maxHeight: '350px',
          overflow: 'auto',
          border: '1px solid rgba(14, 165, 233, 0.1)',
        }}>
          <pre style={{ 
            margin: 0, 
            whiteSpace: 'pre-wrap', 
            wordBreak: 'break-word',
            color: '#475569',
            lineHeight: '1.6',
          }}>
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
