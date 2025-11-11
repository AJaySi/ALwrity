import React, { useState, useEffect } from 'react';

interface ResearchInputContainerProps {
  keywords: string[];
  placeholder: string;
  onKeywordsChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export const ResearchInputContainer: React.FC<ResearchInputContainerProps> = ({
  keywords,
  placeholder,
  onKeywordsChange,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const MAX_WORDS = 1000;

  // Initialize input value from keywords only on mount or when keywords are cleared
  useEffect(() => {
    const keywordValue = keywords.length > 0 ? keywords.join(', ') : '';
    // Only update if the input is empty or if keywords were cleared
    if (inputValue === '' || (keywords.length === 0 && inputValue !== '')) {
      setInputValue(keywordValue);
      const words = keywordValue.trim().split(/\s+/).filter(w => w.length > 0);
      setWordCount(words.length);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keywords.length]); // Only reinitialize if keywords array length changes

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const words = value.trim().split(/\s+/).filter(w => w.length > 0);
    const currentWordCount = words.length;

    // Only update if within word limit
    if (currentWordCount <= MAX_WORDS) {
      setInputValue(value);
      setWordCount(currentWordCount);
      // Create a new event with the current value for the parent handler
      const syntheticEvent = {
        ...e,
        target: {
          ...e.target,
          value: value,
        },
      } as React.ChangeEvent<HTMLTextAreaElement>;
      onKeywordsChange(syntheticEvent);
    } else {
      // Truncate to last valid word boundary
      const truncatedWords = words.slice(0, MAX_WORDS);
      const truncatedValue = truncatedWords.join(' ');
      setInputValue(truncatedValue);
      setWordCount(MAX_WORDS);
      // Create synthetic event with truncated value
      const syntheticEvent = {
        ...e,
        target: {
          ...e.target,
          value: truncatedValue,
        },
      } as React.ChangeEvent<HTMLTextAreaElement>;
      onKeywordsChange(syntheticEvent);
    }
  };
  return (
    <div style={{
      position: 'relative',
      minHeight: '227px', // Reduced by 35% from 350px
      width: '65%', // Reduced by 35% from 100%
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      border: '1px solid rgba(14, 165, 233, 0.2)',
      borderRadius: '16px',
      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 250, 251, 0.95) 100%)',
      boxShadow: 'inset 0 2px 8px rgba(14, 165, 233, 0.06), 0 1px 2px rgba(0, 0, 0, 0.05)',
      overflow: 'hidden',
      transition: 'all 0.3s ease',
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.3)';
      e.currentTarget.style.boxShadow = 'inset 0 2px 8px rgba(14, 165, 233, 0.08), 0 2px 4px rgba(0, 0, 0, 0.08)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
      e.currentTarget.style.boxShadow = 'inset 0 2px 8px rgba(14, 165, 233, 0.06), 0 1px 2px rgba(0, 0, 0, 0.05)';
    }}
    >
      {/* Textarea for input - takes full space */}
      <textarea
        value={inputValue}
        onChange={handleInputChange}
        placeholder={placeholder}
        style={{
          width: '100%',
          flex: '1',
          minHeight: '195px', // Reduced by 35% from 300px
          padding: '12px',
          fontSize: '15px',
          lineHeight: '1.7',
          border: 'none',
          background: 'transparent',
          color: '#1e293b',
          resize: 'vertical',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif',
          outline: 'none',
          fontWeight: '400',
          letterSpacing: '-0.01em',
          overflowWrap: 'break-word',
          wordWrap: 'break-word',
          boxSizing: 'border-box',
        }}
      />

      {/* Word count indicator */}
      <div style={{
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        paddingTop: '8px',
        fontSize: '12px',
        color: wordCount >= MAX_WORDS ? '#ef4444' : '#64748b',
        fontWeight: wordCount >= MAX_WORDS ? '600' : '400',
      }}>
        {wordCount} / {MAX_WORDS} words
      </div>
    </div>
  );
};

