import React from 'react';
import {
  ContentOpportunity,
  KeywordGap,
  AIRecommendations,
  BrainstormSummary,
} from '../../api/gscBrainstorm';

interface GSCBrainstormModalProps {
  open: boolean;
  onClose: () => void;
  contentOpportunities: ContentOpportunity[];
  keywordGaps: KeywordGap[];
  aiRecommendations: AIRecommendations | null;
  summary: BrainstormSummary | null;
  error: string | null;
  isBrainstorming: boolean;
  onSelectSuggestion: (keyword: string) => void;
}

const tabLabels = ['Opportunities', 'Keyword Gaps', 'AI Recommendations'] as const;
type TabKey = typeof tabLabels[number];

export const GSCBrainstormModal: React.FC<GSCBrainstormModalProps> = ({
  open,
  onClose,
  contentOpportunities,
  keywordGaps,
  aiRecommendations,
  summary,
  error,
  isBrainstorming,
  onSelectSuggestion,
}) => {
  const [activeTab, setActiveTab] = React.useState<TabKey>('Opportunities');

  if (!open) return null;

  const hasNoData =
    !isBrainstorming &&
    !error &&
    contentOpportunities.length === 0 &&
    keywordGaps.length === 0 &&
    !aiRecommendations;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          width: '90%',
          maxWidth: '720px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 24px',
            borderBottom: '1px solid #e0e0e0',
          }}
        >
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', color: '#333' }}>
              Brainstorm Topics with GSC Data
            </h3>
            {summary && (
              <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#888' }}>
                {summary.site_url} &middot; {summary.date_range?.start} to {summary.date_range?.end} &middot;{' '}
                {summary.total_keywords_analyzed} keywords analyzed
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer',
              color: '#888',
              padding: '4px 8px',
            }}
            aria-label="Close"
          >
            x
          </button>
        </div>

        {/* Summary metrics bar */}
        {summary && summary.total_keywords_analyzed > 0 && (
          <div
            style={{
              display: 'flex',
              gap: '16px',
              padding: '12px 24px',
              backgroundColor: '#f0f7ff',
              borderBottom: '1px solid #e0e0e0',
              fontSize: '13px',
              flexWrap: 'wrap',
            }}
          >
            <span>
              <strong>{summary.total_impressions?.toLocaleString()}</strong> impressions
            </span>
            <span>
              <strong>{summary.total_clicks?.toLocaleString()}</strong> clicks
            </span>
            <span>
              <strong>{summary.avg_ctr}%</strong> avg CTR
            </span>
            <span>
              <strong>{summary.avg_position}</strong> avg position
            </span>
          </div>
        )}

        {/* Loading */}
        {isBrainstorming && (
          <div
            style={{
              padding: '48px 24px',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: '40px',
                height: '40px',
                border: '3px solid #e0e0e0',
                borderTopColor: '#1976d2',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 16px',
              }}
            />
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            <p style={{ color: '#666', margin: 0 }}>
              Analyzing your GSC data and generating topic suggestions...
            </p>
          </div>
        )}

        {/* Error */}
        {error && !isBrainstorming && (
          <div
            style={{
              padding: '24px',
              textAlign: 'center',
            }}
          >
            <p style={{ color: '#d32f2f', margin: '0 0 8px', fontWeight: 500 }}>
              {error}
            </p>
            <p style={{ color: '#888', margin: 0, fontSize: '13px' }}>
              Make sure your Google Search Console is connected and has data for the last 30 days.
            </p>
          </div>
        )}

        {/* No data */}
        {hasNoData && (
          <div
            style={{
              padding: '48px 24px',
              textAlign: 'center',
            }}
          >
            <p style={{ color: '#888', margin: 0 }}>
              No brainstorming data available. Try different keywords or check your GSC connection.
            </p>
          </div>
        )}

        {/* Results */}
        {!isBrainstorming && !error && !hasNoData && (
          <>
            {/* Tabs */}
            <div
              style={{
                display: 'flex',
                borderBottom: '1px solid #e0e0e0',
                backgroundColor: '#fafafa',
              }}
            >
              {tabLabels.map((tab) => {
                const count =
                  tab === 'Opportunities'
                    ? contentOpportunities.length
                    : tab === 'Keyword Gaps'
                    ? keywordGaps.length
                    : aiRecommendations
                    ? (aiRecommendations.immediate_opportunities?.length ?? 0) +
                      (aiRecommendations.content_strategy?.length ?? 0) +
                      (aiRecommendations.long_term_strategy?.length ?? 0)
                    : 0;
                return (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    style={{
                      padding: '10px 20px',
                      border: 'none',
                      borderBottom: activeTab === tab ? '2px solid #1976d2' : '2px solid transparent',
                      background: activeTab === tab ? '#fff' : 'transparent',
                      color: activeTab === tab ? '#1976d2' : '#666',
                      fontWeight: activeTab === tab ? 600 : 400,
                      cursor: 'pointer',
                      fontSize: '13px',
                    }}
                  >
                    {tab}
                    {count > 0 && (
                      <span
                        style={{
                          marginLeft: '6px',
                          backgroundColor: activeTab === tab ? '#1976d2' : '#ccc',
                          color: '#fff',
                          borderRadius: '10px',
                          padding: '1px 7px',
                          fontSize: '11px',
                        }}
                      >
                        {count}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Tab content */}
            <div style={{ flex: 1, overflow: 'auto', padding: '16px 24px' }}>
              {activeTab === 'Opportunities' && (
                <OpportunitiesTab
                  opportunities={contentOpportunities}
                  onSelect={onSelectSuggestion}
                />
              )}
              {activeTab === 'Keyword Gaps' && (
                <GapsTab gaps={keywordGaps} onSelect={onSelectSuggestion} />
              )}
              {activeTab === 'AI Recommendations' && (
                <AIRecommendationsTab
                  recommendations={aiRecommendations}
                  onSelect={onSelectSuggestion}
                />
              )}
            </div>
          </>
        )}

        {/* Footer */}
        <div
          style={{
            padding: '12px 24px',
            borderTop: '1px solid #e0e0e0',
            display: 'flex',
            justifyContent: 'flex-end',
          }}
        >
          <button
            onClick={onClose}
            style={{
              padding: '8px 20px',
              backgroundColor: '#f5f5f5',
              border: '1px solid #ddd',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  Sub-components                                                      */
/* ------------------------------------------------------------------ */

const OpportunitiesTab: React.FC<{
  opportunities: ContentOpportunity[];
  onSelect: (keyword: string) => void;
}> = ({ opportunities, onSelect }) => {
  if (opportunities.length === 0) {
    return <EmptyMessage message="No content opportunities found for this period." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {opportunities.map((opp, i) => (
        <div
          key={i}
          style={{
            padding: '12px',
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'background-color 0.15s',
          }}
          onClick={() => onSelect(opp.keyword)}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f0f7ff')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#fff')}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '4px',
            }}
          >
            <span style={{ fontWeight: 600, fontSize: '14px', color: '#333' }}>
              {opp.keyword}
            </span>
            <div style={{ display: 'flex', gap: '6px' }}>
              <Badge
                label={opp.type === 'Content Optimization' ? 'Optimize' : 'Enhance'}
                color={opp.type === 'Content Optimization' ? '#1565c0' : '#f57c00'}
              />
              <Badge
                label={opp.priority}
                color={opp.priority === 'High' ? '#d32f2f' : '#666'}
              />
            </div>
          </div>
          <p style={{ margin: '0 0 4px', fontSize: '13px', color: '#555' }}>
            {opp.opportunity}
          </p>
          <div style={{ fontSize: '12px', color: '#999' }}>
            {opp.impressions.toLocaleString()} impressions &middot; Position {opp.current_position}
          </div>
        </div>
      ))}
      <p style={{ fontSize: '12px', color: '#aaa', margin: '8px 0 0' }}>
        Click any keyword to use it as your research topic.
      </p>
    </div>
  );
};

const GapsTab: React.FC<{
  gaps: KeywordGap[];
  onSelect: (keyword: string) => void;
}> = ({ gaps, onSelect }) => {
  if (gaps.length === 0) {
    return (
      <EmptyMessage message="No keyword gaps identified. Your rankings look solid for this period." />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {gaps.map((gap, i) => (
        <div
          key={i}
          style={{
            padding: '12px',
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            transition: 'background-color 0.15s',
          }}
          onClick={() => onSelect(gap.keyword)}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f0f7ff')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#fff')}
        >
          <span style={{ fontWeight: 500, fontSize: '14px' }}>{gap.keyword}</span>
          <div style={{ fontSize: '12px', color: '#999' }}>
            Position {gap.position} &middot; {gap.impressions.toLocaleString()} impressions
          </div>
        </div>
      ))}
      <p style={{ fontSize: '12px', color: '#aaa', margin: '8px 0 0' }}>
        These keywords rank between positions 4-20. Writing targeted content could push them to page 1.
      </p>
    </div>
  );
};

const AIRecommendationsTab: React.FC<{
  recommendations: AIRecommendations | null;
  onSelect: (keyword: string) => void;
}> = ({ recommendations, onSelect }) => {
  if (!recommendations) {
    return <EmptyMessage message="AI recommendations are not available right now." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <RecommendationSection
        title="Immediate Opportunities (0-30 days)"
        items={recommendations.immediate_opportunities}
        onSelect={onSelect}
        color="#1565c0"
      />
      <RecommendationSection
        title="Content Strategy (1-3 months)"
        items={recommendations.content_strategy}
        onSelect={onSelect}
        color="#2e7d32"
      />
      <RecommendationSection
        title="Long-Term Vision (3-12 months)"
        items={recommendations.long_term_strategy}
        onSelect={onSelect}
        color="#6a1b9a"
      />
    </div>
  );
};

const RecommendationSection: React.FC<{
  title: string;
  items: string[];
  onSelect: (keyword: string) => void;
  color: string;
}> = ({ title, items, onSelect, color }) => {
  if (!items || items.length === 0) return null;

  return (
    <div>
      <h4 style={{ margin: '0 0 8px', fontSize: '14px', color }}>{title}</h4>
      <ul style={{ margin: 0, paddingLeft: '20px', listStyle: 'disc' }}>
        {items.map((item, i) => (
          <li
            key={i}
            style={{
              fontSize: '13px',
              color: '#444',
              marginBottom: '4px',
              cursor: 'pointer',
            }}
            onClick={() => {
              const short = item.split(/[:(]/)[0].replace(/^[-\s]+/, '').trim();
              if (short) onSelect(short);
            }}
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
};

const Badge: React.FC<{ label: string; color: string }> = ({ label, color }) => (
  <span
    style={{
      fontSize: '11px',
      fontWeight: 600,
      padding: '2px 8px',
      borderRadius: '4px',
      color: '#fff',
      backgroundColor: color,
    }}
  >
    {label}
  </span>
);

const EmptyMessage: React.FC<{ message: string }> = ({ message }) => (
  <div style={{ padding: '32px 0', textAlign: 'center' }}>
    <p style={{ color: '#888', margin: 0 }}>{message}</p>
  </div>
);

export default GSCBrainstormModal;