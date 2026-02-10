import React, { useState, useEffect } from 'react';
import { Tooltip, CircularProgress, Select, MenuItem, FormControl } from '@mui/material';
import { Psychology as BrainIcon, Info as InfoIcon } from '@mui/icons-material';
import { ResearchPurpose, ContentOutput, ResearchDepthLevel } from '../../types/intent.types';

interface ResearchInputContainerProps {
  keywords: string[];
  placeholder: string;
  onKeywordsChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  // New props for unified intent & options
  onIntentAndOptions?: () => void;
  isAnalyzingIntent?: boolean;
  hasIntentAnalysis?: boolean;
  intentConfidence?: number;
  // User-provided intent settings
  userPurpose?: ResearchPurpose;
  userContentOutput?: ContentOutput;
  userDepth?: ResearchDepthLevel;
  onPurposeChange?: (purpose: ResearchPurpose) => void;
  onContentOutputChange?: (output: ContentOutput) => void;
  onDepthChange?: (depth: ResearchDepthLevel) => void;
}

const PURPOSE_OPTIONS: { value: ResearchPurpose; label: string }[] = [
  { value: 'learn', label: 'Learn' },
  { value: 'create_content', label: 'Create Content' },
  { value: 'make_decision', label: 'Make Decision' },
  { value: 'compare', label: 'Compare' },
  { value: 'solve_problem', label: 'Solve Problem' },
  { value: 'find_data', label: 'Find Data' },
  { value: 'explore_trends', label: 'Explore Trends' },
  { value: 'validate', label: 'Validate' },
  { value: 'generate_ideas', label: 'Generate Ideas' },
];

const CONTENT_OUTPUT_OPTIONS: { value: ContentOutput; label: string }[] = [
  { value: 'blog', label: 'Blog Post' },
  { value: 'podcast', label: 'Podcast' },
  { value: 'video', label: 'Video' },
  { value: 'social_post', label: 'Social Post' },
  { value: 'newsletter', label: 'Newsletter' },
  { value: 'presentation', label: 'Presentation' },
  { value: 'report', label: 'Report' },
  { value: 'whitepaper', label: 'Whitepaper' },
  { value: 'email', label: 'Email' },
  { value: 'general', label: 'General' },
];

const DEPTH_OPTIONS: { value: ResearchDepthLevel; label: string }[] = [
  { value: 'overview', label: 'Overview' },
  { value: 'detailed', label: 'Detailed' },
  { value: 'expert', label: 'Expert-Level' },
];

export const ResearchInputContainer: React.FC<ResearchInputContainerProps> = ({
  keywords,
  placeholder,
  onKeywordsChange,
  onIntentAndOptions,
  isAnalyzingIntent = false,
  hasIntentAnalysis = false,
  intentConfidence = 0,
  userPurpose,
  userContentOutput,
  userDepth,
  onPurposeChange,
  onContentOutputChange,
  onDepthChange,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const MAX_WORDS = 1000;
  const MIN_WORDS_FOR_INTENT = 2; // Enable button after 2+ words

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
          minHeight: '150px', // Reduced to make room for controls
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

      {/* Compact Select Controls - Purpose, Creating, Depth */}
      <div style={{
        display: 'flex',
        gap: '8px',
        padding: '8px 0',
        borderTop: '1px solid rgba(14, 165, 233, 0.1)',
        borderBottom: '1px solid rgba(14, 165, 233, 0.1)',
        marginTop: '8px',
      }}>
        {/* Purpose */}
        <FormControl size="small" sx={{ flex: 1, minWidth: 100 }}>
          <Select
            value={userPurpose || ''}
            onChange={(e) => onPurposeChange?.(e.target.value as ResearchPurpose)}
            displayEmpty
            sx={{
              backgroundColor: '#ffffff',
              color: '#1e293b',
              fontSize: '0.75rem',
              height: '32px',
              '& .MuiSelect-select': {
                padding: '6px 10px',
                color: '#1e293b',
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#d1d5db',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#9ca3af',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#0ea5e9',
                borderWidth: '1.5px',
              },
              '& .MuiSelect-icon': {
                color: '#64748b',
              },
            }}
            MenuProps={{
              PaperProps: {
                sx: {
                  backgroundColor: '#ffffff',
                  '& .MuiMenuItem-root': {
                    color: '#1e293b',
                    fontSize: '0.75rem',
                    '&:hover': {
                      backgroundColor: '#f3f4f6',
                    },
                    '&.Mui-selected': {
                      backgroundColor: '#e0f2fe',
                      color: '#0284c7',
                    },
                  },
                },
              },
            }}
          >
            <MenuItem value="" disabled>
              <em style={{ color: '#9ca3af', fontSize: '0.75rem' }}>Purpose</em>
            </MenuItem>
            {PURPOSE_OPTIONS.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Creating (Content Output) */}
        <FormControl size="small" sx={{ flex: 1, minWidth: 100 }}>
          <Select
            value={userContentOutput || ''}
            onChange={(e) => onContentOutputChange?.(e.target.value as ContentOutput)}
            displayEmpty
            sx={{
              backgroundColor: '#ffffff',
              color: '#1e293b',
              fontSize: '0.75rem',
              height: '32px',
              '& .MuiSelect-select': {
                padding: '6px 10px',
                color: '#1e293b',
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#d1d5db',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#9ca3af',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#0ea5e9',
                borderWidth: '1.5px',
              },
              '& .MuiSelect-icon': {
                color: '#64748b',
              },
            }}
            MenuProps={{
              PaperProps: {
                sx: {
                  backgroundColor: '#ffffff',
                  '& .MuiMenuItem-root': {
                    color: '#1e293b',
                    fontSize: '0.75rem',
                    '&:hover': {
                      backgroundColor: '#f3f4f6',
                    },
                    '&.Mui-selected': {
                      backgroundColor: '#e0f2fe',
                      color: '#0284c7',
                    },
                  },
                },
              },
            }}
          >
            <MenuItem value="" disabled>
              <em style={{ color: '#9ca3af', fontSize: '0.75rem' }}>Creating</em>
            </MenuItem>
            {CONTENT_OUTPUT_OPTIONS.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Depth */}
        <FormControl size="small" sx={{ flex: 1, minWidth: 100 }}>
          <Select
            value={userDepth || ''}
            onChange={(e) => onDepthChange?.(e.target.value as ResearchDepthLevel)}
            displayEmpty
            sx={{
              backgroundColor: '#ffffff',
              color: '#1e293b',
              fontSize: '0.75rem',
              height: '32px',
              '& .MuiSelect-select': {
                padding: '6px 10px',
                color: '#1e293b',
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#d1d5db',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#9ca3af',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#0ea5e9',
                borderWidth: '1.5px',
              },
              '& .MuiSelect-icon': {
                color: '#64748b',
              },
            }}
            MenuProps={{
              PaperProps: {
                sx: {
                  backgroundColor: '#ffffff',
                  '& .MuiMenuItem-root': {
                    color: '#1e293b',
                    fontSize: '0.75rem',
                    '&:hover': {
                      backgroundColor: '#f3f4f6',
                    },
                    '&.Mui-selected': {
                      backgroundColor: '#e0f2fe',
                      color: '#0284c7',
                    },
                  },
                },
              },
            }}
          >
            <MenuItem value="" disabled>
              <em style={{ color: '#9ca3af', fontSize: '0.75rem' }}>Depth</em>
            </MenuItem>
            {DEPTH_OPTIONS.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </div>

      {/* Bottom bar with word count and Intent & Options button */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: '12px',
        borderTop: '1px solid rgba(14, 165, 233, 0.1)',
        marginTop: '8px',
      }}>
        {/* Word count indicator */}
        <div style={{
          fontSize: '12px',
          color: wordCount >= MAX_WORDS ? '#ef4444' : '#64748b',
          fontWeight: wordCount >= MAX_WORDS ? '600' : '400',
        }}>
          {wordCount} / {MAX_WORDS} words
        </div>

        {/* Intent & Options Button */}
        <Tooltip
          title={
            wordCount < MIN_WORDS_FOR_INTENT
              ? `Enter at least ${MIN_WORDS_FOR_INTENT} words to analyze intent`
              : hasIntentAnalysis
                ? `Intent analyzed with ${Math.round(intentConfidence * 100)}% confidence. Click to re-analyze.`
                : 'Let AI understand what you want to accomplish and configure optimal settings'
          }
          arrow
          placement="top"
        >
          <span>
            <button
              onClick={onIntentAndOptions}
              disabled={wordCount < MIN_WORDS_FOR_INTENT || isAnalyzingIntent}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                background: wordCount >= MIN_WORDS_FOR_INTENT && !isAnalyzingIntent
                  ? hasIntentAnalysis
                    ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : 'rgba(100, 116, 139, 0.15)',
                color: wordCount >= MIN_WORDS_FOR_INTENT && !isAnalyzingIntent ? 'white' : '#94a3b8',
                border: 'none',
                borderRadius: '10px',
                cursor: wordCount >= MIN_WORDS_FOR_INTENT && !isAnalyzingIntent ? 'pointer' : 'not-allowed',
                fontSize: '13px',
                fontWeight: '600',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: wordCount >= MIN_WORDS_FOR_INTENT && !isAnalyzingIntent
                  ? '0 2px 8px rgba(102, 126, 234, 0.3)'
                  : 'none',
              }}
              onMouseEnter={(e) => {
                if (wordCount >= MIN_WORDS_FOR_INTENT && !isAnalyzingIntent) {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
                }
              }}
              onMouseLeave={(e) => {
                if (wordCount >= MIN_WORDS_FOR_INTENT && !isAnalyzingIntent) {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
                }
              }}
            >
              {isAnalyzingIntent ? (
                <>
                  <CircularProgress size={14} sx={{ color: 'inherit' }} />
                  Analyzing...
                </>
              ) : hasIntentAnalysis ? (
                <>
                  <BrainIcon sx={{ fontSize: 16 }} />
                  ✓ Intent Ready
                </>
              ) : (
                <>
                  <BrainIcon sx={{ fontSize: 16 }} />
                  Intent & Options
                  <Tooltip title="AI analyzes your research goals and configures optimal Exa/Tavily settings automatically" arrow>
                    <InfoIcon sx={{ fontSize: 12, opacity: 0.7 }} />
                  </Tooltip>
                </>
              )}
            </button>
          </span>
        </Tooltip>
      </div>
    </div>
  );
};

