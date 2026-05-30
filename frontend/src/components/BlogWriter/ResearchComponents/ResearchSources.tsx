import React, { useState, useMemo, useCallback } from 'react';
import { BlogResearchResponse } from '../../../services/blogWriterApi';
import { BrainstormResult } from '../../../api/gscBrainstorm';
import { useGSCBrainstorm } from '../../../hooks/useGSCBrainstorm';
import { GSCBrainstormModal } from '../GSCBrainstormModal';
import { TextToSpeechButton } from '../../shared/TextToSpeechButton';

interface ResearchSourcesProps {
  research: BlogResearchResponse;
  brainstormResult?: BrainstormResult;
  onResearchWithKeywords?: (keywords: string) => void;
  selectedContentAngle?: string;
  onAngleSelect?: (angle: string) => void;
  selectedCompetitiveAdvantage?: string;
  onCompetitiveAdvantageSelect?: (advantage: string) => void;
}

interface KeywordChipGroupProps {
  title: string;
  keywords: string[];
  color: string;
  backgroundColor: string;
  icon: string;
  showCount: number;
  tooltip: string;
  lockedCount?: number;
}

const KeywordChipGroup: React.FC<KeywordChipGroupProps> = ({
  title,
  keywords,
  color,
  backgroundColor,
  icon,
  showCount,
  tooltip,
  lockedCount = 0
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
        {visibleKeywords.map((keyword: string, index: number) => {
          const isLocked = index < lockedCount;
          return (
          <span key={index} style={{
            backgroundColor: backgroundColor,
            color: '#374151',
            padding: isLocked ? '4px 8px 4px 6px' : '4px 8px',
            borderRadius: '6px',
            fontSize: '11px',
            fontWeight: '500',
            border: isLocked ? `1.5px solid ${color}` : `1px solid ${color}40`,
            boxShadow: isLocked ? `0 0 0 1px ${color}20, 0 1px 2px 0 rgba(0, 0, 0, 0.05)` : '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            transition: 'all 0.2s ease',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '3px'
          }}
          title={isLocked ? `🔒 Locked for outline generation` : keyword}
          >
            {isLocked && <span style={{ fontSize: '10px', lineHeight: '1' }}>🔒</span>}
            {keyword}
          </span>
          );
        })}
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

export const ResearchSources: React.FC<ResearchSourcesProps> = ({ research, brainstormResult: propBrainstormResult, onResearchWithKeywords, selectedContentAngle, onAngleSelect, selectedCompetitiveAdvantage, onCompetitiveAdvantageSelect }) => {
  const {
    gscConnected,
    isBrainstorming,
    brainstormError,
    contentOpportunities,
    keywordGaps,
    quickWins,
    pageOpportunities,
    aiRecommendations,
    summary,
    progressMessage,
    brainstorm: localBrainstorm,
    reset: resetBrainstorm,
  } = useGSCBrainstorm();

  const [showGSCModal, setShowGSCModal] = useState(false);
  const [localBrainstormResult, setLocalBrainstormResult] = useState<BrainstormResult | null>(null);

  const brainstormResult = propBrainstormResult || localBrainstormResult;

  const handleLocalBrainstorm = useCallback(async () => {
    const kw = (research as any).original_keywords
      ? (Array.isArray((research as any).original_keywords) ? (research as any).original_keywords.join(', ') : String((research as any).original_keywords))
      : (research.keywords?.join(', ') || (research as any).topic || '');
    if (!kw) {
      console.warn('[GSC] No keywords available for brainstorming');
      return;
    }
    setShowGSCModal(true);
    const result = await localBrainstorm(kw);
    if (result) {
      setLocalBrainstormResult(result);
    }
  }, [research, localBrainstorm]);

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

          {/* Curation Summary Bar */}
          <div style={{
            marginBottom: '12px',
            padding: '6px 10px',
            backgroundColor: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '6px',
            fontSize: '11px',
            color: '#166534',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            flexWrap: 'wrap'
          }}
          title="To prevent keyword stuffing, only the top keywords in each category are locked for outline generation. The LLM receives these ~13 curated keywords as strict placement directives."
          >
            <span>🧹</span>
            <span style={{ fontWeight: 500 }}>Smart Curation Active:</span>
            <span>~{(() => {
              const primary = research.keyword_analysis?.primary?.length || 0;
              const secondary = research.keyword_analysis?.secondary?.length || 0;
              const longTail = research.keyword_analysis?.long_tail?.length || 0;
              const semantic = research.keyword_analysis?.semantic_keywords?.length || 0;
              const trending = research.keyword_analysis?.trending_terms?.length || 0;
              const gaps = research.keyword_analysis?.content_gaps?.length || 0;
              return primary + secondary + longTail + semantic + trending + gaps;
            })()} raw</span>
            <span>→</span>
            <span style={{ fontWeight: 600 }}>13 locked</span>
            <span style={{
              backgroundColor: '#166534',
              color: '#f0fdf4',
              padding: '1px 6px',
              borderRadius: '10px',
              fontSize: '10px',
              fontWeight: 600
            }}>
              🔒 H1/H2/H3 assigned
            </span>
          </div>
          
          {/* Progressive Disclosure Keyword Chips */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {/* Primary Keywords — lock top 2 for H1 */}
            {research.keyword_analysis?.primary && research.keyword_analysis.primary.length > 0 && (
              <KeywordChipGroup
                title="Primary"
                keywords={research.keyword_analysis.primary}
                color="#1976d2"
                backgroundColor="#e3f2fd"
                icon="🎯"
                showCount={2}
                lockedCount={2}
                tooltip="Core keywords that directly match your main topic. These are the most important terms for SEO and should be naturally integrated throughout your content. Primary keywords typically have high search volume and strong commercial intent."
              />
            )}

            {/* Secondary Keywords — lock top 2 for H2 */}
            {research.keyword_analysis?.secondary && research.keyword_analysis.secondary.length > 0 && (
              <KeywordChipGroup
                title="Secondary"
                keywords={research.keyword_analysis.secondary}
                color="#7b1fa2"
                backgroundColor="#f3e5f5"
                icon="🔗"
                showCount={2}
                lockedCount={2}
                tooltip="Supporting keywords that complement your primary terms. These help create topic clusters and improve content depth. Secondary keywords often have lower competition but still drive valuable traffic and enhance topical authority."
              />
            )}

            {/* Long-tail Keywords — lock top 2 for H3 */}
            {research.keyword_analysis?.long_tail && research.keyword_analysis.long_tail.length > 0 && (
              <KeywordChipGroup
                title="Long-tail"
                keywords={research.keyword_analysis.long_tail}
                color="#2e7d32"
                backgroundColor="#e8f5e8"
                icon="📏"
                showCount={2}
                lockedCount={2}
                tooltip="Specific, longer phrases that users search for. These keywords have lower search volume but higher conversion rates and less competition. Long-tail keywords help capture users with specific intent and often lead to better engagement."
              />
            )}

            {/* Semantic Keywords — lock top 4 for body-level signals */}
            {research.keyword_analysis?.semantic_keywords && research.keyword_analysis.semantic_keywords.length > 0 && (
              <KeywordChipGroup
                title="Semantic"
                keywords={research.keyword_analysis.semantic_keywords}
                color="#f57c00"
                backgroundColor="#fff3e0"
                icon="🧠"
                showCount={4}
                lockedCount={4}
                tooltip="Contextually related terms that help search engines understand your content's meaning. These keywords improve semantic relevance and help with featured snippets. They're crucial for modern SEO and natural language processing algorithms."
              />
            )}

            {/* Trending Terms — lock top 2 for contextual mentions */}
            {research.keyword_analysis?.trending_terms && research.keyword_analysis.trending_terms.length > 0 && (
              <KeywordChipGroup
                title="Trending"
                keywords={research.keyword_analysis.trending_terms}
                color="#c2185b"
                backgroundColor="#fce4ec"
                icon="📈"
                showCount={2}
                lockedCount={2}
                tooltip="Currently popular and rising search terms in your industry. These keywords can provide opportunities for timely content and increased visibility. Trending terms often have growing search volume and can help you capture emerging market interest."
              />
            )}

            {/* Content Gaps — lock top 1 for competitive edge */}
            {research.keyword_analysis?.content_gaps && research.keyword_analysis.content_gaps.length > 0 && (
              <KeywordChipGroup
                title="Content Gaps"
                keywords={research.keyword_analysis.content_gaps}
                color="#c62828"
                backgroundColor="#ffebee"
                icon="🕳️"
                showCount={2}
                lockedCount={1}
                tooltip="Underserved topics and keywords that competitors aren't adequately covering. These represent opportunities to create unique, valuable content that can help you stand out. Content gaps often lead to easier ranking opportunities and less saturated markets."
              />
            )}

            {/* Top Competitors — no lock (display only, not used for keyword placement) */}
            {research.competitor_analysis?.top_competitors && research.competitor_analysis.top_competitors.length > 0 && (
              <KeywordChipGroup
                title="Top Competitors"
                keywords={research.competitor_analysis.top_competitors}
                color="#1e40af"
                backgroundColor="#dbeafe"
                icon="🏁"
                showCount={2}
                tooltip="Main competing domains and publications covering this topic. Understanding who ranks for your target keywords helps identify benchmark content quality and uncover differentiation opportunities."
              />
            )}

            {/* GSC — inside keywords card, below chips */}
            {brainstormResult ? (
              <GSCInsightsCard brainstormResult={brainstormResult} research={research} />
            ) : (
              <div onClick={handleLocalBrainstorm} style={{
                marginTop: '12px',
                padding: '12px',
                backgroundColor: '#faf5ff',
                border: '1px solid #ddd6fe',
                borderRadius: '8px',
                borderLeft: '4px solid #7c3aed',
                cursor: 'pointer',
              }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#1f2937', marginBottom: '4px' }}>
                  📊 Unlock GSC Insights
                </div>
                <p style={{ margin: '0 0 8px', fontSize: '11px', color: '#6b7280', lineHeight: '1.4' }}>
                  Find keyword gaps, quick wins, and AI recommendations from your GSC data.
                </p>
                <span style={{
                  display: 'inline-block',
                  padding: '5px 12px',
                  backgroundColor: gscConnected ? '#7c3aed' : '#4caf50',
                  color: '#fff',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 500,
                }}>
                  {isBrainstorming ? 'Analyzing...' : gscConnected ? '📊 Brainstorm Topics' : '🔗 Connect GSC'}
                </span>
                {brainstormError && (
                  <p style={{ margin: '8px 0 0', fontSize: '11px', color: '#dc2626' }}>{brainstormError}</p>
                )}
              </div>
            )}
          </div>

          {/* GSC Brainstorm Modal */}
          <GSCBrainstormModal
            open={showGSCModal}
            onClose={() => {
              setShowGSCModal(false);
              resetBrainstorm();
            }}
            contentOpportunities={contentOpportunities}
            keywordGaps={keywordGaps}
            quickWins={quickWins}
            pageOpportunities={pageOpportunities}
            aiRecommendations={aiRecommendations}
            summary={summary}
            error={brainstormError}
            isBrainstorming={isBrainstorming}
            progressMessage={progressMessage}
            onSelectSuggestion={() => {}}
            initialKeywords={typeof research.original_keywords === 'string' ? research.original_keywords : research.keywords?.join(', ') || ''}
            onReRun={async (newKw) => {
              const result = await localBrainstorm(newKw, undefined, true);
              if (result) setLocalBrainstormResult(result);
            }}
          />
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
              <h4 style={{ margin: 0, color: '#1e40af', fontSize: '14px', fontWeight: '600' }} title="AI-generated summary of key findings from the research, including search intent analysis and difficulty score.">Research Insights</h4>
              <TextToSpeechButton text={research.keyword_analysis.analysis_insights || ''} size="small" showSettings={false} />
            </div>
            
            {/* Key Metrics in Research Insights - Moved to right corner */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {research.keyword_analysis?.search_intent && (
                <div title="The primary search intent category for this topic — informational, navigational, commercial, or transactional. Helps align content structure with what users are actually looking for." style={{
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
                <div title="Keyword difficulty score out of 10 — higher values indicate stronger competition and more effort required to rank. Use this to prioritize keywords that balance opportunity with achievability." style={{
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
          
          <p title="AI-generated synthesis of key research findings summarizing the strategic direction, search intent, and competitive landscape for this topic." style={{
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

      {/* Market Positioning Section */}
      {research.competitor_analysis?.market_positioning && (
        <div style={{
          marginBottom: '20px',
          padding: '16px',
          backgroundColor: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          borderLeft: '4px solid #8b5cf6',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '16px' }}>🎯</span>
            <h4 style={{ margin: 0, color: '#6d28d9', fontSize: '14px', fontWeight: '600' }} title="Strategic market positioning analysis — how this topic fits within the competitive landscape and where unique value can be created.">Market Positioning</h4>
          </div>
          <p style={{ margin: 0, color: '#475569', fontSize: '13px', lineHeight: '1.6' }}>
            {research.competitor_analysis.market_positioning}
          </p>
        </div>
      )}

      {/* Content Angles Section */}
      {research.suggested_angles && research.suggested_angles.length > 0 && (
        <div style={{
          marginBottom: '20px',
          padding: '16px',
          backgroundColor: '#f0fdf4',
          border: '1px solid #bbf7d0',
          borderRadius: '8px',
          borderLeft: '4px solid #22c55e',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '16px' }}>💡</span>
              <h4 style={{ margin: 0, color: '#166534', fontSize: '14px', fontWeight: '600' }} title="Different narrative perspectives derived from research data. Select one to focus your outline, or run new research on any angle.">Select Content Angle For Blog Outline</h4>
            </div>
            <span style={{
              backgroundColor: '#dcfce7',
              color: '#166534',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: '600',
            }}>
              {research.suggested_angles.length} angles
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {research.suggested_angles.map((angle, index) => (
              <div key={index} style={{
                border: `2px solid ${selectedContentAngle === angle ? '#16a34a' : '#bbf7d0'}`,
                borderRadius: '8px',
                padding: '12px',
                backgroundColor: selectedContentAngle === angle ? '#f0fdf4' : '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onClick={() => onAngleSelect?.(angle)}
              onMouseEnter={(e) => {
                if (selectedContentAngle !== angle) {
                  e.currentTarget.style.borderColor = '#86efac';
                  e.currentTarget.style.backgroundColor = '#f0fdf4';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedContentAngle !== angle) {
                  e.currentTarget.style.borderColor = '#bbf7d0';
                  e.currentTarget.style.backgroundColor = '#fff';
                }
              }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: 0 }}>
                  <span style={{
                    backgroundColor: selectedContentAngle === angle ? '#16a34a' : '#22c55e',
                    color: 'white',
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '11px',
                    fontWeight: '600',
                    flexShrink: 0,
                  }}>
                    {selectedContentAngle === angle ? '✓' : index + 1}
                  </span>
                  <span title={`Click to select "${angle}" as the primary angle for outline generation. This will guide the AI to structure the outline around this perspective.`} style={{ fontSize: '13px', color: '#374151', lineHeight: '1.4', fontWeight: selectedContentAngle === angle ? 600 : 400 }}>
                    {angle}
                  </span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onResearchWithKeywords?.(angle);
                  }}
                  style={{
                    padding: '6px 14px',
                    backgroundColor: '#22c55e',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    flexShrink: 0,
                    transition: 'background-color 0.15s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#16a34a'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#22c55e'}
                >
                  🔍 Run Research
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Competitive Advantages Section */}
      {research.competitor_analysis?.competitive_advantages?.length > 0 && (
        <div style={{
          marginBottom: '20px',
          padding: '16px',
          backgroundColor: '#fffbeb',
          border: '1px solid #fde68a',
          borderRadius: '8px',
          borderLeft: '4px solid #f59e0b',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '16px' }}>✅</span>
              <h4 style={{ margin: 0, color: '#92400e', fontSize: '14px', fontWeight: '600' }} title="Key competitive advantages identified in research. Select one to emphasize as a differentiator in your outline.">Select Competitive Advantage For Blog Outline</h4>
            </div>
            <span style={{
              backgroundColor: '#fef3c7',
              color: '#92400e',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: '600',
            }}>
              {research.competitor_analysis.competitive_advantages.length} advantages
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {(research.competitor_analysis.competitive_advantages as string[]).map((advantage, index) => (
              <div key={index} style={{
                border: `2px solid ${selectedCompetitiveAdvantage === advantage ? '#d97706' : '#fde68a'}`,
                borderRadius: '8px',
                padding: '12px',
                backgroundColor: selectedCompetitiveAdvantage === advantage ? '#fffbeb' : '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onClick={() => onCompetitiveAdvantageSelect?.(advantage)}
              onMouseEnter={(e) => {
                if (selectedCompetitiveAdvantage !== advantage) {
                  e.currentTarget.style.borderColor = '#fcd34d';
                  e.currentTarget.style.backgroundColor = '#fffbeb';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCompetitiveAdvantage !== advantage) {
                  e.currentTarget.style.borderColor = '#fde68a';
                  e.currentTarget.style.backgroundColor = '#fff';
                }
              }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: 0 }}>
                  <span style={{
                    backgroundColor: selectedCompetitiveAdvantage === advantage ? '#d97706' : '#f59e0b',
                    color: 'white',
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '11px',
                    fontWeight: '600',
                    flexShrink: 0,
                  }}>
                    {selectedCompetitiveAdvantage === advantage ? '✓' : index + 1}
                  </span>
                  <span title={`Click to select "${advantage}" as the primary competitive advantage for outline emphasis.`} style={{ fontSize: '13px', color: '#374151', lineHeight: '1.4', fontWeight: selectedCompetitiveAdvantage === advantage ? 600 : 400 }}>
                    {advantage}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Note: Google Search Widget is shown in GoogleSearchModal instead */}
      <div style={{ 
        display: 'grid', 
        gap: '12px',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        width: '100%',
        overflow: 'hidden'
      }}>
        {research.sources.map((source, index) => (
          <SourceCard key={index} source={source as any} />
        ))}
        </div>
      </div>

    </div>
  );
};

// ============================================================================
// Source Card Component — each research source with expandable content
// ============================================================================

interface SourceCardProps {
  source: BlogResearchResponse['sources'][0] & { highlights?: string[]; summary?: string; image?: string; author?: string; content?: string };
}

const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  const [showExtra, setShowExtra] = useState(false);
  const [showFullText, setShowFullText] = useState(false);
  const allHighlights = source.highlights || [];
  const remainingHighlights = allHighlights.length > 1 ? allHighlights.slice(1) : [];
  const hasSummary = !!source.summary;
  const hasContent = !!source.content;

  const renderCredibilityScore = (score: number | undefined | null): React.ReactNode => {
    if (score === undefined || score === null) return null;
    const percentage = Math.round(score * 100);
    const radius = 18;
    const circumference = 2 * Math.PI * radius;
    const strokeDasharray = `${circumference} ${circumference}`;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;
    const color = percentage >= 80 ? '#22c55e' : percentage >= 60 ? '#f59e0b' : '#ef4444';
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ position: 'relative', width: '44px', height: '44px' }}>
          <svg width="44" height="44" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="22" cy="22" r={radius} stroke="#e0e0e0" strokeWidth="4" fill="none" />
            <circle cx="22" cy="22" r={radius} stroke={color} strokeWidth="4" fill="none" strokeDasharray={strokeDasharray} strokeDashoffset={strokeDashoffset} strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.3s ease' }} />
          </svg>
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: '10px', fontWeight: '600', color }}>
            {percentage}%
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{
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
            <span style={{ backgroundColor: '#e3f2fd', color: '#1976d2', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: '600' }}>
              SERP Ranking {source.index !== undefined ? source.index + 1 : '?'}
            </span>
            <span style={{ backgroundColor: '#f3e5f5', color: '#7b1fa2', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>
              Research Type: {source.source_type || 'web'}
            </span>
            {source.published_at ? (
              <span style={{ backgroundColor: '#e8f5e8', color: '#2e7d32', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>
                {source.published_at}
              </span>
            ) : (
              <span style={{ backgroundColor: '#f5f5f5', color: '#666', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>
                No date
              </span>
            )}
            {source.author && (
              <span style={{ backgroundColor: '#fff7ed', color: '#c2410c', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: '500' }}>
                ✍️ {source.author}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', marginTop: '4px' }}>
            {source.image && (
              <img src={source.image} alt="" style={{ width: '60px', height: '60px', borderRadius: '6px', objectFit: 'cover', flexShrink: 0, border: '1px solid #e0e0e0' }}
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
              />
            )}
            <div style={{ flex: 1, minWidth: 0 }}>
              <h4 style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#333', lineHeight: '1.3' }}>
                {source.title}
              </h4>
            </div>
          </div>
        </div>
        {renderCredibilityScore(source.credibility_score)}
      </div>

      <p style={{ margin: '8px 0 6px 0', fontSize: '12px', color: '#666', lineHeight: '1.4' }}>
        {source.excerpt}
      </p>

      {/* Show more toggle for highlights + summary */}
      {(remainingHighlights.length > 0 || hasSummary) && (
        <div style={{ marginBottom: '6px' }}>
          <button onClick={() => setShowExtra(!showExtra)} style={{ background: 'none', border: 'none', color: '#1976d2', fontSize: '11px', fontWeight: 500, cursor: 'pointer', padding: '0', display: 'flex', alignItems: 'center', gap: '4px' }}>
            {showExtra ? '▾ Show less' : `▸ Show more (${remainingHighlights.length + (hasSummary ? 1 : 0)} more)`}
          </button>
          {showExtra && (
            <div style={{ marginTop: '6px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {hasSummary && (
                <div style={{ fontSize: '11px', color: '#475569', backgroundColor: '#f0f9ff', borderRadius: '4px', padding: '6px 8px', borderLeft: '2px solid #3b82f6' }}>
                  <span style={{ fontWeight: 600, color: '#1e40af' }}>Summary: </span>
                  {source.summary}
                </div>
              )}
              {remainingHighlights.map((h, i) => (
                <div key={i} style={{ fontSize: '11px', color: '#555', padding: '4px 8px', backgroundColor: '#f9fafb', borderRadius: '4px', borderLeft: '2px solid #d1d5db' }}>
                  {h}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Full-text preview toggle */}
      {hasContent && (
        <div style={{ marginBottom: '6px' }}>
          <button onClick={() => setShowFullText(!showFullText)} style={{ background: 'none', border: 'none', color: '#7b1fa2', fontSize: '11px', fontWeight: 500, cursor: 'pointer', padding: '0', display: 'flex', alignItems: 'center', gap: '4px' }}>
            {showFullText ? '▾ Hide full text' : '▸ View full text'}
          </button>
          {showFullText && source.content && (
            <div style={{ marginTop: '6px', fontSize: '11px', color: '#555', lineHeight: '1.6', maxHeight: '200px', overflowY: 'auto', backgroundColor: '#f9fafb', borderRadius: '4px', padding: '8px', border: '1px solid #e5e7eb' }}>
              {source.content.length > 2000 ? source.content.substring(0, 2000) + '...' : source.content}
            </div>
          )}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: '11px', color: '#666' }}>
          <a href={source.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2', textDecoration: 'none', fontWeight: '500' }}>
            Source from {(() => { try { return new URL(source.url).hostname; } catch { return source.url; } })()}
          </a>
        </div>
        <TextToSpeechButton text={`${source.title}. ${source.excerpt}`} size="small" showSettings={false} />
      </div>
    </div>
  );
};

interface GSCInsightsCardProps {
  brainstormResult: BrainstormResult;
  research: BlogResearchResponse;
}

const GSCInsightsCard: React.FC<GSCInsightsCardProps> = ({ brainstormResult, research }) => {
  const keywordGaps = brainstormResult.keyword_gaps || [];
  const quickWins = brainstormResult.quick_wins || [];
  const contentGaps = research.keyword_analysis?.content_gaps || [];

  const intersectingGaps = useMemo(() => {
    return keywordGaps.filter((g) =>
      contentGaps.some((cg: string) => cg.toLowerCase().includes(g.keyword.toLowerCase()) || g.keyword.toLowerCase().includes(cg.toLowerCase()))
    );
  }, [keywordGaps, contentGaps]);

  const gapOnly = useMemo(() => {
    return keywordGaps.filter((g) =>
      !contentGaps.some((cg: string) => cg.toLowerCase().includes(g.keyword.toLowerCase()) || g.keyword.toLowerCase().includes(cg.toLowerCase()))
    );
  }, [keywordGaps, contentGaps]);

  const aiRecs = brainstormResult.ai_recommendations
    && 'immediate_opportunities' in brainstormResult.ai_recommendations
    ? (brainstormResult.ai_recommendations as import('../../../api/gscBrainstorm').AIRecommendations)
    : null;

  const allAiRecs = aiRecs
    ? [...(aiRecs.immediate_opportunities || []), ...(aiRecs.content_strategy || []), ...(aiRecs.long_term_strategy || [])]
    : [];

  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '12px',
      padding: '20px',
      backgroundColor: '#ffffff',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      borderLeft: '4px solid #7c3aed',
      marginTop: '16px',
    }}>
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{
          margin: 0,
          color: '#1f2937',
          fontSize: '18px',
          fontWeight: '700',
          letterSpacing: '-0.025em'
        }}>
          📊 GSC Insights
        </h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {/* 1. Search Intent + CTR overlay */}
        {brainstormResult.summary && 'site_url' in brainstormResult.summary && (
          <div style={{
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '12px',
            backgroundColor: '#faf5ff',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px' }}>🎯</span>
              <span style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>GSC Performance</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '12px', color: '#4b5563' }}>
              {research.keyword_analysis?.search_intent && (
                <div style={{ padding: '4px 8px', backgroundColor: '#f0f9ff', borderRadius: '4px', border: '1px solid #bae6fd' }}>
                  <span style={{ color: '#0369a1', fontWeight: '500' }}>Intent: </span>
                  <span style={{ color: '#0c4a6e' }}>{research.keyword_analysis.search_intent}</span>
                </div>
              )}
              <div style={{ padding: '4px 8px', backgroundColor: '#f0fdf4', borderRadius: '4px', border: '1px solid #bbf7d0' }}>
                <span style={{ color: '#15803d', fontWeight: '500' }}>Avg CTR: </span>
                <span style={{ color: '#166534' }}>{(brainstormResult.summary as any).avg_ctr?.toFixed(1)}%</span>
              </div>
              <div style={{ padding: '4px 8px', backgroundColor: '#fef2f2', borderRadius: '4px', border: '1px solid #fecaca' }}>
                <span style={{ color: '#dc2626', fontWeight: '500' }}>Avg Pos: </span>
                <span style={{ color: '#991b1b' }}>{(brainstormResult.summary as any).avg_position?.toFixed(1)}</span>
              </div>
              <div style={{ padding: '4px 8px', backgroundColor: '#fff7ed', borderRadius: '4px', border: '1px solid #fed7aa' }}>
                <span style={{ color: '#c2410c', fontWeight: '500' }}>Health: </span>
                <span style={{ color: '#9a3412' }}>{(brainstormResult.summary as any).health_score ?? 'N/A'}</span>
              </div>
            </div>
          </div>
        )}

        {/* 2. Intersecting Keyword Gaps */}
        {intersectingGaps.length > 0 && (
          <div style={{
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '12px',
            backgroundColor: '#fef2f2',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px' }}>🔄</span>
              <span style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Gap Overlap ({intersectingGaps.length})</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {intersectingGaps.map((g, i) => (
                <span key={i} style={{
                  backgroundColor: '#fee2e2',
                  color: '#991b1b',
                  padding: '3px 6px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: '500',
                  border: '1px solid #fecaca',
                }}>
                  {g.keyword}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 3. New Keyword Gaps (not in research) */}
        {gapOnly.length > 0 && (
          <div style={{
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '12px',
            backgroundColor: '#fff7ed',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px' }}>🕳️</span>
              <span style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>New Gaps ({gapOnly.length})</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {gapOnly.map((g, i) => (
                <span key={i} style={{
                  backgroundColor: '#ffedd5',
                  color: '#9a3412',
                  padding: '3px 6px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: '500',
                  border: '1px solid #fed7aa',
                }}>
                  {g.keyword} <span style={{ opacity: 0.6 }}>(pos {g.position})</span>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 4. Quick Wins anchor keywords */}
        {quickWins.length > 0 && (
          <div style={{
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '12px',
            backgroundColor: '#f0fdf4',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px' }}>⚡</span>
              <span style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Quick Wins ({quickWins.length})</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {quickWins.slice(0, 5).map((w, i) => (
                <div key={i} style={{
                  padding: '6px 8px',
                  backgroundColor: '#dcfce7',
                  borderRadius: '4px',
                  border: '1px solid #bbf7d0',
                  fontSize: '11px',
                  color: '#166534',
                }}>
                  <strong>{w.keyword}</strong> — pos {w.position}, CTR {w.current_ctr?.toFixed(1)}%
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 5. AI Recommendations */}
        {allAiRecs.length > 0 && (
          <div style={{
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '12px',
            backgroundColor: '#f0f9ff',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px' }}>🤖</span>
              <span style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>AI Subheading Ideas ({allAiRecs.length})</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {allAiRecs.slice(0, 5).map((r, i) => (
                <div key={i} style={{
                  padding: '6px 8px',
                  backgroundColor: '#e0f2fe',
                  borderRadius: '4px',
                  border: '1px solid #bae6fd',
                  fontSize: '11px',
                  color: '#0c4a6e',
                }}>
                  <strong>{r.title}</strong>
                  <div style={{ fontSize: '10px', color: '#0369a1', marginTop: '2px' }}>{r.reason}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchSources;
