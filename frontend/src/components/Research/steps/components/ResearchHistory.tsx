import React from 'react';
import { 
  clearResearchHistory, 
  formatHistoryTimestamp, 
  getHistorySummary,
  ResearchHistoryEntry 
} from '../../../../utils/researchHistory';
import { WizardState } from '../../types/research.types';

interface ResearchHistoryProps {
  history: ResearchHistoryEntry[];
  onLoadHistory: (entry: Partial<WizardState>) => void;
  onHistoryCleared: () => void;
}

export const ResearchHistory: React.FC<ResearchHistoryProps> = ({ 
  history, 
  onLoadHistory, 
  onHistoryCleared 
}) => {
  if (history.length === 0) return null;

  const handleClear = () => {
    clearResearchHistory();
    onHistoryCleared();
  };

  return (
    <div style={{
      marginBottom: '12px',
      padding: '12px',
      background: 'rgba(14, 165, 233, 0.03)',
      border: '1px solid rgba(14, 165, 233, 0.1)',
      borderRadius: '10px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '10px',
      }}>
        <span style={{
          fontSize: '12px',
          fontWeight: '600',
          color: '#0369a1',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <span>🕐</span>
          Recently Researched
        </span>
        <button
          onClick={handleClear}
          style={{
            padding: '4px 10px',
            fontSize: '11px',
            color: '#64748b',
            background: 'transparent',
            border: '1px solid rgba(100, 116, 139, 0.2)',
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
            e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)';
            e.currentTarget.style.color = '#dc2626';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.borderColor = 'rgba(100, 116, 139, 0.2)';
            e.currentTarget.style.color = '#64748b';
          }}
        >
          Clear
        </button>
      </div>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
      }}>
        {history.map((entry) => (
          <button
            key={entry.timestamp}
            onClick={() => {
              onLoadHistory({
                keywords: entry.keywords,
                industry: entry.industry,
                targetAudience: entry.targetAudience,
                researchMode: entry.researchMode,
              });
            }}
            title={`Industry: ${entry.industry} | Audience: ${entry.targetAudience} | Mode: ${entry.researchMode} | ${formatHistoryTimestamp(entry.timestamp)}`}
            style={{
              padding: '8px 14px',
              fontSize: '12px',
              color: '#0369a1',
              background: 'rgba(255, 255, 255, 0.9)',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              maxWidth: '100%',
              textAlign: 'left',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(14, 165, 233, 0.1)';
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(14, 165, 233, 0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.9)';
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <span style={{ fontSize: '14px' }}>🔍</span>
            <span style={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: '200px',
            }}>
              {getHistorySummary(entry)}
            </span>
            <span style={{
              fontSize: '10px',
              color: '#64748b',
              marginLeft: '4px',
            }}>
              {formatHistoryTimestamp(entry.timestamp)}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

