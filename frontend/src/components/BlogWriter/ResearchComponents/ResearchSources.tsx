import React, { useEffect, useState } from 'react';
import { BlogResearchResponse } from '../../../services/blogWriterApi';

interface ResearchSourcesProps {
  research: BlogResearchResponse;
}

interface KeywordChipGroupProps {
  title: string;
  keywords: string[];
  color: string;
  backgroundColor: string;
  icon: string;
  showCount: number;
  tooltip: string;
}

const KeywordChipGroup: React.FC<KeywordChipGroupProps> = ({
  title,
  keywords,
  color,
  backgroundColor,
  icon,
  showCount,
  tooltip
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const visibleKeywords = isExpanded ? keywords : keywords.slice(0, showCount);
  const hasMore = keywords.length > showCount;

  return (
    <div
      style={{
        position: 'relative',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '12px',
        backgroundColor: '#ffffff',
        cursor: hasMore ? 'pointer' : 'default',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
      }}
      onMouseEnter={(e) => {
        if (hasMore) {
          setIsExpanded(true);
          e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
          e.currentTarget.style.borderColor = color;
          e.currentTarget.style.transform = 'translateY(-1px)';
        }
      }}
      onMouseLeave={(e) => {
        if (hasMore) {
          setIsExpanded(false);
          e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)';
          e.currentTarget.style.borderColor = '#e5e7eb';
          e.currentTarget.style.transform = 'translateY(0)';
        }
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', paddingRight: '8px' }}>
        <span style={{ fontSize: '14px' }}>{icon}</span>
        <span style={{ 
          fontSize: '13px', 
          fontWeight: '600', 
          color: '#374151',
          letterSpacing: '0.025em',
          flex: 1,
          minWidth: 0
        }}>
          {title}
        </span>
        <span style={{ 
          fontSize: '11px', 
          color: '#6b7280',
          backgroundColor: '#f3f4f6',
          padding: '2px 6px',
          borderRadius: '12px',
          fontWeight: '500',
          border: '1px solid #e5e7eb',
          flexShrink: 0
        }}>
          {keywords.length}
        </span>
        {/* Help Icon */}
        <span 
          onClick={() => setShowTooltip(!showTooltip)}
          style={{
            fontSize: '12px',
            color: '#9ca3af',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '50%',
            transition: 'all 0.2s ease',
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: '20px',
            minHeight: '20px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#6b7280';
            e.currentTarget.style.backgroundColor = '#f3f4f6';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = '#9ca3af';
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          ❓
        </span>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {visibleKeywords.map((keyword: string, index: number) => (
          <span key={index} style={{
            backgroundColor: backgroundColor,
            color: '#374151',
            padding: '4px 8px',
            borderRadius: '6px',
            fontSize: '11px',
            fontWeight: '500',
            border: `1px solid ${color}40`,
            boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            transition: 'all 0.2s ease'
          }}>
            {keyword}
          </span>
        ))}
        {hasMore && !isExpanded && (
          <span style={{
            backgroundColor: '#f9fafb',
            color: '#6b7280',
            padding: '4px 8px',
            borderRadius: '6px',
            fontSize: '11px',
            fontWeight: '500',
            border: '1px solid #d1d5db',
            fontStyle: 'italic'
          }}>
            +{keywords.length - showCount} more
          </span>
        )}
      </div>

            {/* Professional Tooltip - Only show when clicked */}
            {showTooltip && (
        <div style={{
          position: 'absolute',
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: '8px',
          backgroundColor: '#1f2937',
          color: '#f9fafb',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '12px',
          lineHeight: '1.5',
          maxWidth: '280px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          zIndex: 1000,
          border: '1px solid #374151'
        }}>
          <div style={{ fontWeight: '600', marginBottom: '4px', color: '#f3f4f6' }}>
            {title} Keywords
          </div>
          <div style={{ color: '#d1d5db' }}>
            {tooltip}
          </div>
          {/* Tooltip arrow */}
          <div style={{
            position: 'absolute',
            top: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 0,
            height: 0,
            borderLeft: '6px solid transparent',
            borderRight: '6px solid transparent',
            borderTop: '6px solid #1f2937'
          }} />
        </div>
      )}
    </div>
  );
};

export const ResearchSources: React.FC<ResearchSourcesProps> = ({ research }) => {
  const [showWebSearchHelp, setShowWebSearchHelp] = useState(false);

  // Fix search widget overflow after render
  useEffect(() => {
    if (research.search_widget) {
      const searchWidget = document.querySelector('[data-search-widget]');
      if (searchWidget) {
        const allElements = searchWidget.querySelectorAll('*');
        allElements.forEach((el: any) => {
          el.style.maxWidth = '100%';
          el.style.overflow = 'hidden';
          el.style.wordWrap = 'break-word';
          el.style.whiteSpace = 'normal';
          el.style.boxSizing = 'border-box';
        });
      }
    }
  }, [research.search_widget]);

  const renderCredibilityScore = (score: number | undefined) => {
    const safeScore = score ?? 0.8; // Default to 0.8 if undefined
    const percentage = Math.round(safeScore * 100);
    const color = safeScore >= 0.8 ? '#4CAF50' : safeScore >= 0.6 ? '#FF9800' : '#F44336';
    const radius = 20;
    const circumference = 2 * Math.PI * radius;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (safeScore * circumference);
    
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ position: 'relative', width: '44px', height: '44px' }}>
          <svg width="44" height="44" style={{ transform: 'rotate(-90deg)' }}>
            <circle
              cx="22"
              cy="22"
              r={radius}
              stroke="#e0e0e0"
              strokeWidth="4"
              fill="none"
            />
            <circle
              cx="22"
              cy="22"
              r={radius}
              stroke={color}
              strokeWidth="4"
              fill="none"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.3s ease' }}
            />
          </svg>
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: '10px',
            fontWeight: '600',
            color: color
          }}>
            {percentage}%
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', gap: '16px', padding: '16px', width: '100%', overflow: 'hidden' }}>
      {/* Keywords Sidebar - Moved to Left */}
      <div style={{ flex: 1, minWidth: '300px', maxWidth: '400px', overflow: 'hidden' }}>
        <div style={{
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          padding: '20px',
          backgroundColor: '#ffffff',
          position: 'sticky',
          top: '16px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          borderLeft: '4px solid #3b82f6'
        }}>
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ 
              margin: 0, 
              color: '#1f2937', 
              fontSize: '18px',
              fontWeight: '700',
              letterSpacing: '-0.025em'
            }}>
              🎯 Keywords
            </h3>
          </div>
          
          {/* Progressive Disclosure Keyword Chips */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {/* Primary Keywords */}
            {research.keyword_analysis?.primary && research.keyword_analysis.primary.length > 0 && (
              <KeywordChipGroup
                title="Primary"
                keywords={research.keyword_analysis.primary}
                color="#1976d2"
                backgroundColor="#e3f2fd"
                icon="🎯"
                showCount={2}
                tooltip="Core keywords that directly match your main topic. These are the most important terms for SEO and should be naturally integrated throughout your content. Primary keywords typically have high search volume and strong commercial intent."
              />
            )}

            {/* Secondary Keywords */}
            {research.keyword_analysis?.secondary && research.keyword_analysis.secondary.length > 0 && (
              <KeywordChipGroup
                title="Secondary"
                keywords={research.keyword_analysis.secondary}
                color="#7b1fa2"
                backgroundColor="#f3e5f5"
                icon="🔗"
                showCount={2}
                tooltip="Supporting keywords that complement your primary terms. These help create topic clusters and improve content depth. Secondary keywords often have lower competition but still drive valuable traffic and enhance topical authority."
              />
            )}

            {/* Long-tail Keywords */}
            {research.keyword_analysis?.long_tail && research.keyword_analysis.long_tail.length > 0 && (
              <KeywordChipGroup
                title="Long-tail"
                keywords={research.keyword_analysis.long_tail}
                color="#2e7d32"
                backgroundColor="#e8f5e8"
                icon="📏"
                showCount={2}
                tooltip="Specific, longer phrases that users search for. These keywords have lower search volume but higher conversion rates and less competition. Long-tail keywords help capture users with specific intent and often lead to better engagement."
              />
            )}

            {/* Semantic Keywords */}
            {research.keyword_analysis?.semantic_keywords && research.keyword_analysis.semantic_keywords.length > 0 && (
              <KeywordChipGroup
                title="Semantic"
                keywords={research.keyword_analysis.semantic_keywords}
                color="#f57c00"
                backgroundColor="#fff3e0"
                icon="🧠"
                showCount={2}
                tooltip="Contextually related terms that help search engines understand your content's meaning. These keywords improve semantic relevance and help with featured snippets. They're crucial for modern SEO and natural language processing algorithms."
              />
            )}

            {/* Trending Terms */}
            {research.keyword_analysis?.trending_terms && research.keyword_analysis.trending_terms.length > 0 && (
              <KeywordChipGroup
                title="Trending"
                keywords={research.keyword_analysis.trending_terms}
                color="#c2185b"
                backgroundColor="#fce4ec"
                icon="📈"
                showCount={2}
                tooltip="Currently popular and rising search terms in your industry. These keywords can provide opportunities for timely content and increased visibility. Trending terms often have growing search volume and can help you capture emerging market interest."
              />
            )}

            {/* Content Gaps */}
            {research.keyword_analysis?.content_gaps && research.keyword_analysis.content_gaps.length > 0 && (
              <KeywordChipGroup
                title="Content Gaps"
                keywords={research.keyword_analysis.content_gaps}
                color="#c62828"
                backgroundColor="#ffebee"
                icon="🕳️"
                showCount={2}
                tooltip="Underserved topics and keywords that competitors aren't adequately covering. These represent opportunities to create unique, valuable content that can help you stand out. Content gaps often lead to easier ranking opportunities and less saturated markets."
              />
            )}
          </div>
        </div>
      </div>

      {/* Main Sources Content */}
      <div style={{ flex: 2, minWidth: 0, overflow: 'hidden' }}>
      <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>🔍 Research Sources ({research.sources.length})</h3>
      
      {/* Research Insights Section */}
      {research.keyword_analysis?.analysis_insights && (
        <div style={{
          marginBottom: '20px',
          padding: '16px',
          backgroundColor: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          borderLeft: '4px solid #3b82f6'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '16px' }}>💡</span>
              <h4 style={{ margin: 0, color: '#1e40af', fontSize: '14px', fontWeight: '600' }}>Research Insights</h4>
            </div>
            
            {/* Key Metrics in Research Insights - Moved to right corner */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {research.keyword_analysis?.search_intent && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  backgroundColor: '#f0f9ff',
                  border: '1px solid #0ea5e9',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  fontSize: '11px',
                  fontWeight: '500'
                }}>
                  <span style={{ color: '#0369a1', fontSize: '10px' }}>🎯</span>
                  <span style={{ color: '#0369a1' }}>Search Intent:</span>
                  <span style={{ 
                    color: '#0c4a6e', 
                    fontWeight: '600',
                    backgroundColor: '#e0f2fe',
                    padding: '1px 4px',
                    borderRadius: '3px',
                    fontSize: '10px'
                  }}>
                    {research.keyword_analysis.search_intent}
                  </span>
                </div>
              )}
              {research.keyword_analysis?.difficulty && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  backgroundColor: '#fef2f2',
                  border: '1px solid #ef4444',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  fontSize: '11px',
                  fontWeight: '500'
                }}>
                  <span style={{ color: '#dc2626', fontSize: '10px' }}>📊</span>
                  <span style={{ color: '#dc2626' }}>Difficulty:</span>
                  <span style={{ 
                    color: '#991b1b', 
                    fontWeight: '600',
                    backgroundColor: '#fee2e2',
                    padding: '1px 4px',
                    borderRadius: '3px',
                    fontSize: '10px'
                  }}>
                    {research.keyword_analysis.difficulty}/10
                  </span>
                </div>
              )}
            </div>
          </div>
          
          <p style={{
            margin: 0,
            color: '#475569',
            fontSize: '13px',
            lineHeight: '1.6',
            fontStyle: 'italic'
          }}>
            {research.keyword_analysis.analysis_insights}
          </p>
        </div>
      )}
        
        {/* Interactive Web Search - Moved from Header */}
        {research.search_widget && (
          <div style={{ marginBottom: '20px', width: '100%', overflow: 'hidden' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', position: 'relative' }}>
              <h4 style={{ margin: 0, color: '#555', fontSize: '16px' }}>
                🔍 Explore More Research Topics
              </h4>
              {/* Help Icon for Web Search */}
              <span 
                onClick={() => setShowWebSearchHelp(!showWebSearchHelp)}
                style={{
                  fontSize: '14px',
                  color: '#9ca3af',
                  cursor: 'pointer',
                  padding: '4px',
                  borderRadius: '50%',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minWidth: '24px',
                  minHeight: '24px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#6b7280';
                  e.currentTarget.style.backgroundColor = '#f3f4f6';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#9ca3af';
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                ❓
              </span>
              
              {/* Help Tooltip for Web Search */}
              {showWebSearchHelp && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: '0',
                  marginTop: '8px',
                  backgroundColor: '#1f2937',
                  color: '#f9fafb',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  fontSize: '12px',
                  lineHeight: '1.5',
                  maxWidth: '300px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  zIndex: 1000,
                  border: '1px solid #374151'
                }}>
                  <div style={{ fontWeight: '600', marginBottom: '4px', color: '#f3f4f6' }}>
                    Research Enhancement
                  </div>
                  <div style={{ color: '#d1d5db' }}>
                    Click on any search suggestion below to explore additional research topics and gather more insights for your blog. These searches will open in a new tab to help you discover trending topics, expert opinions, and current statistics.
                  </div>
                  {/* Tooltip arrow */}
                  <div style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: '20px',
                    width: 0,
                    height: 0,
                    borderLeft: '6px solid transparent',
                    borderRight: '6px solid transparent',
                    borderBottom: '6px solid #1f2937'
                  }} />
                </div>
              )}
            </div>
            <div style={{
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              padding: '16px',
              backgroundColor: '#fafafa',
              maxHeight: '400px',
              overflow: 'auto',
              width: '100%',
              maxWidth: '100%',
              boxSizing: 'border-box',
              overflowX: 'hidden',
              position: 'relative'
            }}
            onClick={(e) => {
              // Make all links open in new tabs
              const target = e.target as HTMLElement;
              if (target.tagName === 'A' || target.closest('a')) {
                const link = target.tagName === 'A' ? target as HTMLAnchorElement : target.closest('a') as HTMLAnchorElement;
                if (link && link.href) {
                  link.target = '_blank';
                  link.rel = 'noopener noreferrer';
                }
              }
            }}>
              <div 
                data-search-widget
                dangerouslySetInnerHTML={{ __html: research.search_widget }}
                style={{ 
                  fontSize: '14px',
                  width: '100%',
                  maxWidth: '100%',
                  overflow: 'hidden',
                  overflowX: 'hidden',
                  wordWrap: 'break-word',
                  overflowWrap: 'break-word',
                  whiteSpace: 'normal',
                  display: 'block',
                  position: 'relative'
                }}
              />
              
              {/* Custom CSS to make Google icon larger */}
              <style>
                {`
                  [data-search-widget] svg {
                    width: 24px !important;
                    height: 24px !important;
                  }
                  [data-search-widget] .logo-light,
                  [data-search-widget] .logo-dark {
                    width: 24px !important;
                    height: 24px !important;
                  }
                `}
              </style>
            </div>
          </div>
        )}
        
      <div style={{ 
        display: 'grid', 
        gap: '12px',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        width: '100%',
        overflow: 'hidden'
      }}>
        {research.sources.map((source, index) => (
          <div key={index} style={{
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            padding: '12px',
            backgroundColor: '#fafafa',
            width: '100%',
            minWidth: 0,
            overflow: 'hidden',
            boxSizing: 'border-box'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', flexWrap: 'wrap' }}>
                  <span style={{ 
                    backgroundColor: '#e3f2fd', 
                    color: '#1976d2', 
                    padding: '2px 6px', 
                    borderRadius: '4px', 
                    fontSize: '10px', 
                    fontWeight: '600' 
                  }}>
                    SERP Ranking {source.index !== undefined ? source.index + 1 : '?'}
                  </span>
                  <span style={{ 
                    backgroundColor: '#f3e5f5', 
                    color: '#7b1fa2', 
                    padding: '2px 6px', 
                    borderRadius: '4px', 
                    fontSize: '10px' 
                  }}>
                    Research Type: {source.source_type || 'web'}
                  </span>
                  {source.published_at && (
                    <span style={{ 
                      backgroundColor: '#e8f5e8', 
                      color: '#2e7d32', 
                      padding: '2px 6px', 
                      borderRadius: '4px', 
                      fontSize: '10px' 
                    }}>
                      {source.published_at}
                    </span>
                  )}
                  {!source.published_at && (
                    <span style={{ 
                      backgroundColor: '#f5f5f5', 
                      color: '#666', 
                      padding: '2px 6px', 
                      borderRadius: '4px', 
                      fontSize: '10px' 
                    }}>
                      No date
                    </span>
                  )}
                </div>
                <h4 style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#333', lineHeight: '1.3' }}>
                  {source.title}
                </h4>
              </div>
              {renderCredibilityScore(source.credibility_score)}
            </div>
            <p style={{ 
              margin: '0 0 6px 0', 
              fontSize: '12px', 
              color: '#666',
              lineHeight: '1.4'
            }}>
              {source.excerpt}
            </p>
            <div style={{ fontSize: '11px', color: '#666', marginTop: '6px' }}>
              <a 
                href={source.url} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ 
                  color: '#1976d2', 
                  textDecoration: 'none',
                  fontWeight: '500'
                }}
              >
                Source from {new URL(source.url).hostname}
              </a>
            </div>
          </div>
        ))}
        </div>
      </div>

    </div>
  );
};

export default ResearchSources;
