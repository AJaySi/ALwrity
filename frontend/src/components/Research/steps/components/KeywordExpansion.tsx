import React from 'react';
import { formatKeyword } from '../../../../utils/keywordExpansion';

interface KeywordExpansionProps {
  suggestions: string[];
  currentKeywords: string[];
  industry: string;
  onAddSuggestion: (suggestion: string) => void;
}

export const KeywordExpansion: React.FC<KeywordExpansionProps> = ({
  suggestions,
  currentKeywords,
  industry,
  onAddSuggestion,
}) => {
  if (suggestions.length === 0 || industry === 'General') return null;

  return (
    <div style={{
      marginTop: '12px',
      padding: '12px',
      background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 197, 253, 0.05) 100%)',
      border: '1px solid rgba(59, 130, 246, 0.15)',
      borderRadius: '8px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '10px',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '13px',
          fontWeight: '600',
          color: '#1e40af',
        }}>
          <span>💡</span>
          <span>Suggested Keywords for {industry}</span>
        </div>
      </div>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
      }}>
        {suggestions.map((suggestion, idx) => {
          const isAlreadyAdded = currentKeywords.some(k => k.toLowerCase() === suggestion.toLowerCase());
          return (
            <button
              key={idx}
              onClick={() => !isAlreadyAdded && onAddSuggestion(suggestion)}
              disabled={isAlreadyAdded}
              style={{
                padding: '6px 12px',
                background: isAlreadyAdded 
                  ? 'rgba(203, 213, 225, 0.3)' 
                  : 'rgba(59, 130, 246, 0.1)',
                border: `1px solid ${isAlreadyAdded ? 'rgba(148, 163, 184, 0.3)' : 'rgba(59, 130, 246, 0.2)'}`,
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: '500',
                color: isAlreadyAdded ? '#64748b' : '#1e40af',
                cursor: isAlreadyAdded ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
              onMouseEnter={(e) => {
                if (!isAlreadyAdded) {
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.15)';
                  e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isAlreadyAdded) {
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.2)';
                }
              }}
            >
              {isAlreadyAdded ? (
                <>
                  <span>✓</span>
                  <span>{formatKeyword(suggestion)}</span>
                </>
              ) : (
                <>
                  <span>+</span>
                  <span>{formatKeyword(suggestion)}</span>
                </>
              )}
            </button>
          );
        })}
      </div>
      <div style={{
        marginTop: '8px',
        fontSize: '11px',
        color: '#64748b',
        fontStyle: 'italic',
      }}>
        Click to add suggested keywords to your research query
      </div>
    </div>
  );
};

