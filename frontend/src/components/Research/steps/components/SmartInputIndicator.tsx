import React from 'react';

interface SmartInputIndicatorProps {
  keywords: string[];
}

export const SmartInputIndicator: React.FC<SmartInputIndicatorProps> = ({ keywords }) => {
  if (keywords.length === 0) return null;

  return (
    <div style={{
      marginTop: '10px',
      padding: '8px 12px',
      background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)',
      border: '1px solid rgba(34, 197, 94, 0.2)',
      borderRadius: '8px',
      fontSize: '12px',
      color: '#059669',
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
    }}>
      <span>✓</span>
      {keywords[0]?.startsWith('http') ? (
        <span>URL detected - will extract and analyze content</span>
      ) : keywords.length === 1 && keywords[0]?.split(/\s+/).length > 5 ? (
        <span>Research topic detected - will conduct comprehensive analysis</span>
      ) : (
        <span>{keywords.length} keyword{keywords.length > 1 ? 's' : ''} identified</span>
      )}
    </div>
  );
};

