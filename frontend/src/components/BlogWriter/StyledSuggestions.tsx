import React from 'react';

interface StyledSuggestion {
  title: string;
  message: string;
  priority?: 'high' | 'normal';
}

interface StyledSuggestionsProps {
  suggestions: StyledSuggestion[];
  onSuggestionClick: (suggestion: StyledSuggestion) => void;
}

export const StyledSuggestions: React.FC<StyledSuggestionsProps> = ({ 
  suggestions, 
  onSuggestionClick 
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {suggestions.map((suggestion, index) => {
        const isHighPriority = suggestion.priority === 'high';
        
        return (
          <button
            key={index}
            onClick={() => onSuggestionClick(suggestion)}
            style={{
              padding: isHighPriority ? '16px 20px' : '12px 16px',
              backgroundColor: isHighPriority ? '#1976d2' : '#f5f5f5',
              color: isHighPriority ? 'white' : '#333',
              border: isHighPriority ? '2px solid #1976d2' : '1px solid #ddd',
              borderRadius: '8px',
              fontSize: isHighPriority ? '16px' : '14px',
              fontWeight: isHighPriority ? '600' : '500',
              textAlign: 'left',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: isHighPriority ? '0 2px 8px rgba(25, 118, 210, 0.2)' : '0 1px 3px rgba(0, 0, 0, 0.1)',
              position: 'relative',
              overflow: 'hidden'
            }}
            onMouseEnter={(e) => {
              if (isHighPriority) {
                e.currentTarget.style.backgroundColor = '#1565c0';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(25, 118, 210, 0.3)';
              } else {
                e.currentTarget.style.backgroundColor = '#e8e8e8';
                e.currentTarget.style.borderColor = '#1976d2';
              }
            }}
            onMouseLeave={(e) => {
              if (isHighPriority) {
                e.currentTarget.style.backgroundColor = '#1976d2';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(25, 118, 210, 0.2)';
              } else {
                e.currentTarget.style.backgroundColor = '#f5f5f5';
                e.currentTarget.style.borderColor = '#ddd';
              }
            }}
          >
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              marginBottom: isHighPriority ? '4px' : '2px'
            }}>
              <span style={{ 
                fontSize: isHighPriority ? '18px' : '16px',
                filter: isHighPriority ? 'brightness(0) invert(1)' : 'none'
              }}>
                {suggestion.title.split(' ')[0]}
              </span>
              <span style={{ 
                fontSize: isHighPriority ? '16px' : '14px',
                fontWeight: isHighPriority ? '600' : '500'
              }}>
                {suggestion.title.split(' ').slice(1).join(' ')}
              </span>
            </div>
            <div style={{ 
              fontSize: isHighPriority ? '14px' : '12px',
              opacity: isHighPriority ? '0.9' : '0.7',
              lineHeight: '1.4'
            }}>
              {suggestion.message}
            </div>
            {isHighPriority && (
              <div style={{
                position: 'absolute',
                top: '0',
                right: '0',
                width: '0',
                height: '0',
                borderLeft: '20px solid transparent',
                borderTop: '20px solid rgba(255, 255, 255, 0.1)',
                pointerEvents: 'none'
              }} />
            )}
          </button>
        );
      })}
    </div>
  );
};

export default StyledSuggestions;
