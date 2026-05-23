import React from 'react';
import {
  ContentOpportunity,
  KeywordGap,
  QuickWin,
  PageOpportunity,
  AIRecommendations,
  AIRecommendation,
  BrainstormSummary,
} from '../../api/gscBrainstorm';

interface GSCBrainstormModalProps {
  open: boolean;
  onClose: () => void;
  contentOpportunities: ContentOpportunity[];
  keywordGaps: KeywordGap[];
  quickWins: QuickWin[];
  pageOpportunities: PageOpportunity[];
  aiRecommendations: AIRecommendations | null;
  summary: BrainstormSummary | null;
  error: string | null;
  isBrainstorming: boolean;
  progressMessage?: string;
  onSelectSuggestion: (keyword: string) => void;
}

const tabLabels = [
  'Quick Wins',
  'Opportunities',
  'Keyword Gaps',
  'Pages',
  'AI Recommendations',
] as const;
type TabKey = typeof tabLabels[number];

export const GSCBrainstormModal: React.FC<GSCBrainstormModalProps> = ({
  open,
  onClose,
  contentOpportunities,
  keywordGaps,
  quickWins,
  pageOpportunities,
  aiRecommendations,
  summary,
  error,
  isBrainstorming,
  progressMessage,
  onSelectSuggestion,
}) => {
  const [activeTab, setActiveTab] = React.useState<TabKey>('Quick Wins');

  if (!open) return null;

  const hasData =
    contentOpportunities.length > 0 ||
    keywordGaps.length > 0 ||
    quickWins.length > 0 ||
    pageOpportunities.length > 0 ||
    aiRecommendations !== null;

  const getTabCount = (tab: TabKey): number => {
    switch (tab) {
      case 'Quick Wins': return quickWins.length;
      case 'Opportunities': return contentOpportunities.length;
      case 'Keyword Gaps': return keywordGaps.length;
      case 'Pages': return pageOpportunities.length;
      case 'AI Recommendations':
        return aiRecommendations
          ? (aiRecommendations.immediate_opportunities?.length ?? 0) +
            (aiRecommendations.content_strategy?.length ?? 0) +
            (aiRecommendations.long_term_strategy?.length ?? 0)
          : 0;
    }
  };

  return (
    <div
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.55)', display: 'flex',
        alignItems: 'center', justifyContent: 'center', zIndex: 9999,
        backdropFilter: 'blur(2px)',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '16px',
          width: '85vw',
          height: '85vh',
          maxWidth: '1200px',
          maxHeight: '900px',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 16px 48px rgba(0,0,0,0.25)',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '20px 28px', borderBottom: '1px solid #e8e8e8', flexShrink: 0,
        }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '20px', fontWeight: 600, color: '#1a1a1a' }}>
              Brainstorm Topics with GSC Data
            </h3>
            {summary?.site_url && (
              <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#888' }}>
                {summary.site_url} &middot; {summary.date_range?.start} to {summary.date_range?.end} &middot;{' '}
                {summary.total_keywords_analyzed} keywords
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', fontSize: '22px', cursor: 'pointer',
              color: '#999', padding: '4px 10px', borderRadius: '6px',
              transition: 'background-color 0.15s', lineHeight: 1,
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            aria-label="Close"
          >✕</button>
        </div>

        {/* Summary dashboard */}
        {summary && summary.total_keywords_analyzed > 0 && (
          <SummaryDashboard summary={summary} />
        )}

        {/* Loading with educational progress */}
        {isBrainstorming && (
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            padding: '48px', gap: '24px',
          }}>
            <div style={{ position: 'relative', width: '72px', height: '72px' }}>
              <div style={{
                position: 'absolute', inset: 0,
                borderRadius: '50%', border: '4px solid #e8e8e8',
              }} />
              <div style={{
                position: 'absolute', inset: 0,
                borderRadius: '50%', border: '4px solid transparent',
                borderTopColor: '#1976d2', borderRightColor: '#4caf50',
                animation: 'progressSpin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite',
              }} />
              <style>{`@keyframes progressSpin { to { transform: rotate(360deg); } }`}</style>
            </div>
            <div style={{ textAlign: 'center', maxWidth: '520px' }}>
              {progressMessage ? (
                <>
                  <p style={{
                    margin: '0 0 12px', fontSize: '15px', color: '#333',
                    fontWeight: 500, lineHeight: 1.5,
                  }}>
                    {progressMessage}
                  </p>
                  <div style={{
                    width: '240px', height: '3px', backgroundColor: '#e8e8e8',
                    borderRadius: '2px', margin: '0 auto', overflow: 'hidden',
                  }}>
                    <div style={{
                      width: '40%', height: '100%', backgroundColor: '#4caf50',
                      borderRadius: '2px',
                      animation: 'progressBar 2s ease-in-out infinite',
                    }} />
                    <style>{`@keyframes progressBar { 0% { transform: translateX(-100%); } 100% { transform: translateX(350%); } }`}</style>
                  </div>
                </>
              ) : (
                <p style={{ margin: 0, fontSize: '15px', color: '#666', lineHeight: 1.5 }}>
                  Analyzing your GSC data and generating topic suggestions...
                </p>
              )}
              <p style={{ margin: '16px 0 0', fontSize: '13px', color: '#999' }}>
                This usually takes 5-15 seconds
              </p>
            </div>
            <div style={{
              backgroundColor: '#f8fbff', borderRadius: '10px',
              padding: '16px 20px', maxWidth: '480px', width: '100%',
              border: '1px solid #e0ecf7',
            }}>
              <p style={{ margin: '0 0 6px', fontSize: '12px', fontWeight: 600, color: '#1565c0' }}>
                What's happening behind the scenes:
              </p>
              <p style={{ margin: 0, fontSize: '12px', color: '#555', lineHeight: 1.5 }}>
                We fetch your real Google Search Console data, scan for high-ROI keywords,
                find pages that need optimization, and ask our AI to craft topic suggestions
                tailored to your site's analytics.
              </p>
            </div>
          </div>
        )}

        {/* Error */}
        {error && !isBrainstorming && (
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', padding: '48px',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.6 }}>⚠</div>
            <p style={{ color: '#d32f2f', margin: '0 0 8px', fontWeight: 500, fontSize: '15px' }}>{error}</p>
            <p style={{ color: '#888', margin: 0, fontSize: '13px' }}>Make sure your Google Search Console is connected and has data for the last 30 days.</p>
          </div>
        )}

        {/* No data */}
        {!isBrainstorming && !error && !hasData && (
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', padding: '48px',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.4 }}>🔍</div>
            <p style={{ color: '#888', margin: 0 }}>No brainstorming data available. Try different keywords or check your GSC connection.</p>
          </div>
        )}

        {/* Results */}
        {!isBrainstorming && !error && hasData && (
          <>
            {/* Tabs */}
            <div style={{
              display: 'flex', borderBottom: '1px solid #e8e8e8',
              backgroundColor: '#fafafa', padding: '0 4px', flexShrink: 0,
            }}>
              {tabLabels.map((tab) => {
                const count = getTabCount(tab);
                const isActive = activeTab === tab;
                return (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    style={{
                      padding: '12px 20px', border: 'none',
                      borderBottom: isActive ? '2px solid #1976d2' : '2px solid transparent',
                      background: isActive ? '#fff' : 'transparent',
                      color: isActive ? '#1976d2' : '#666',
                      fontWeight: isActive ? 600 : 400,
                      cursor: 'pointer', fontSize: '14px', whiteSpace: 'nowrap',
                      transition: 'color 0.15s, background-color 0.15s',
                      display: 'flex', alignItems: 'center', gap: '6px',
                    }}
                  >
                    {tab}
                    {count > 0 && (
                      <span style={{
                        backgroundColor: isActive ? '#1976d2' : '#bbb',
                        color: '#fff', borderRadius: '10px', padding: '1px 8px',
                        fontSize: '11px', fontWeight: 600, lineHeight: '18px',
                      }}>{count}</span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Tab content */}
            <div style={{ flex: 1, overflow: 'auto', padding: '20px 28px' }}>
              {activeTab === 'Quick Wins' && <QuickWinsTab wins={quickWins} onSelect={onSelectSuggestion} />}
              {activeTab === 'Opportunities' && <OpportunitiesTab opportunities={contentOpportunities} onSelect={onSelectSuggestion} />}
              {activeTab === 'Keyword Gaps' && <GapsTab gaps={keywordGaps} onSelect={onSelectSuggestion} />}
              {activeTab === 'Pages' && <PagesTab pages={pageOpportunities} />}
              {activeTab === 'AI Recommendations' && <AIRecommendationsTab recommendations={aiRecommendations} onSelect={onSelectSuggestion} />}
            </div>
          </>
        )}

        {/* Footer */}
        <div style={{
          padding: '14px 28px', borderTop: '1px solid #e8e8e8',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          backgroundColor: '#fafafa', flexShrink: 0,
        }}>
          <span style={{ fontSize: '12px', color: '#999' }}>Click any keyword or title to use it as your research topic</span>
          <button
            onClick={onClose}
            style={{
              padding: '10px 24px', backgroundColor: '#fff',
              border: '1px solid #ddd', borderRadius: '8px',
              cursor: 'pointer', fontSize: '14px', color: '#555',
              transition: 'background-color 0.15s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fff'}
          >Close</button>
        </div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  Summary Dashboard                                                   */
/* ------------------------------------------------------------------ */

const SummaryDashboard: React.FC<{ summary: BrainstormSummary }> = ({ summary }) => {
  const dist = summary.keyword_distribution || {};
  const total = dist.positions_1_3 + dist.positions_4_10 + dist.positions_11_20 + dist.positions_21_plus || 1;
  const healthColor = summary.health_score >= 70 ? '#2e7d32' : summary.health_score >= 40 ? '#f57c00' : '#d32f2f';
  const ctrColor = summary.ctr_vs_benchmark >= 0 ? '#2e7d32' : '#d32f2f';

  return (
    <div style={{ borderBottom: '1px solid #e8e8e8', flexShrink: 0 }}>
      <div style={{
        display: 'flex', gap: '28px', padding: '14px 28px',
        backgroundColor: '#f8fbff', flexWrap: 'wrap',
      }}>
        <MetricBox label="Impressions" value={summary.total_impressions?.toLocaleString()} />
        <MetricBox label="Clicks" value={summary.total_clicks?.toLocaleString()} />
        <MetricBox
          label="Avg CTR"
          value={`${summary.avg_ctr}%`}
          sublabel={`vs 3.1% avg`}
          sublabelColor={ctrColor}
          driving
        />
        <MetricBox label="Avg Position" value={`${summary.avg_position}`} />
        <MetricBox label="SEO Health" value={`${summary.health_score}/100`} valueColor={healthColor} driving />
      </div>
      {total > 1 && (
        <div style={{
          padding: '0 28px 12px', display: 'flex', gap: '16px',
          fontSize: '12px', color: '#666', flexWrap: 'wrap', alignItems: 'center',
        }}>
          <span style={{ fontSize: '11px', fontWeight: 500, color: '#999', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Rank Distribution
          </span>
          <DistBadge label="Top 3" count={dist.positions_1_3} total={total} color="#2e7d32" />
          <DistBadge label="4-10" count={dist.positions_4_10} total={total} color="#1565c0" />
          <DistBadge label="11-20" count={dist.positions_11_20} total={total} color="#f57c00" />
          <DistBadge label="21+" count={dist.positions_21_plus} total={total} color="#999" />
        </div>
      )}
    </div>
  );
};

const MetricBox: React.FC<{
  label: string; value: string; valueColor?: string;
  sublabel?: string; sublabelColor?: string; driving?: boolean;
}> = ({ label, value, valueColor, sublabel, sublabelColor, driving }) => (
  <div style={{
    textAlign: 'center', padding: driving ? '0 20px 0 0' : 0,
    borderRight: driving ? '1px solid #e0e0e0' : 'none',
  }}>
    <div style={{ fontSize: '20px', fontWeight: 700, color: valueColor || '#1a1a1a' }}>{value}</div>
    <div style={{ fontSize: '12px', color: '#888' }}>{label}</div>
    {sublabel && <div style={{ fontSize: '10px', color: sublabelColor || '#999', fontWeight: 500 }}>{sublabel}</div>}
  </div>
);

const DistBadge: React.FC<{ label: string; count: number; total: number; color: string }> = ({ label, count, total, color }) => (
  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
    <span style={{
      width: '10px', height: '10px', borderRadius: '50%',
      backgroundColor: color, display: 'inline-block', flexShrink: 0,
    }} />
    <span>{label}: <strong>{count}</strong> <span style={{ color: '#999' }}>({Math.round(count / total * 100)}%)</span></span>
  </span>
);

/* ------------------------------------------------------------------ */
/*  Quick Wins Tab                                                      */
/* ------------------------------------------------------------------ */

const QuickWinsTab: React.FC<{ wins: QuickWin[]; onSelect: (kw: string) => void }> = ({ wins, onSelect }) => {
  if (wins.length === 0) {
    return <EmptyMessage message="No quick wins found. Your page-1 keywords may already be well-optimized." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <p style={{ margin: '0 0 4px', fontSize: '14px', color: '#555' }}>
        These keywords are already on page 1. A small optimization push could land them in the top 3 — the highest-ROI opportunities available.
      </p>
      {wins.map((win, i) => (
        <div
          key={i}
          style={{
            padding: '16px 18px', border: '1px solid #c8e6c9', borderRadius: '10px',
            cursor: 'pointer', transition: 'all 0.15s', backgroundColor: '#f1f8e9',
            borderLeft: '4px solid #4caf50',
          }}
          onClick={() => onSelect(win.keyword)}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#dcedc8'; e.currentTarget.style.borderLeftColor = '#2e7d32'; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#f1f8e9'; e.currentTarget.style.borderLeftColor = '#4caf50'; }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontWeight: 600, fontSize: '15px', color: '#2e7d32' }}>{win.keyword}</span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <Badge label={`#${Math.round(win.position)}`} color="#1565c0" />
              <Badge label={`+${win.estimated_traffic_gain} clicks/mo`} color="#2e7d32" />
            </div>
          </div>
          <p style={{ margin: '0 0 6px', fontSize: '13px', color: '#444', lineHeight: 1.5 }}>{win.reason}</p>
          <div style={{ fontSize: '12px', color: '#888' }}>
            {win.impressions.toLocaleString()} impressions &middot; {win.current_ctr}% current CTR
          </div>
        </div>
      ))}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  Opportunities Tab                                                   */
/* ------------------------------------------------------------------ */

const OpportunitiesTab: React.FC<{ opportunities: ContentOpportunity[]; onSelect: (kw: string) => void }> = ({ opportunities, onSelect }) => {
  if (opportunities.length === 0) {
    return <EmptyMessage message="No content opportunities found for this period." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {opportunities.map((opp, i) => (
        <div
          key={i}
          style={{
            padding: '16px 18px', border: '1px solid #e0e0e0', borderRadius: '10px',
            cursor: 'pointer', transition: 'all 0.15s',
            borderLeft: `4px solid ${opp.priority === 'High' ? '#d32f2f' : '#f57c00'}`,
          }}
          onClick={() => onSelect(opp.keyword)}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0f7ff'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fff'}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontWeight: 600, fontSize: '15px', color: '#1a1a1a' }}>{opp.keyword}</span>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
              <Badge
                label={opp.type === 'Content Optimization' ? 'Optimize' : 'Enhance'}
                color={opp.type === 'Content Optimization' ? '#1565c0' : '#f57c00'}
              />
              <Badge label={opp.priority} color={opp.priority === 'High' ? '#d32f2f' : '#666'} />
              {opp.suggested_format && <Badge label={opp.suggested_format} color="#6a1b9a" />}
            </div>
          </div>
          <p style={{ margin: '0 0 8px', fontSize: '13px', color: '#444', lineHeight: 1.5 }}>{opp.opportunity}</p>
          <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#888', flexWrap: 'wrap' }}>
            <span>{opp.impressions.toLocaleString()} impressions</span>
            <span>Position {opp.current_position}</span>
            <span>{opp.current_ctr}% CTR</span>
            <span style={{ color: '#2e7d32', fontWeight: 600 }}>+{opp.estimated_traffic_gain} clicks/mo potential</span>
          </div>
        </div>
      ))}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  Keyword Gaps Tab                                                   */
/* ------------------------------------------------------------------ */

const GapsTab: React.FC<{ gaps: KeywordGap[]; onSelect: (kw: string) => void }> = ({ gaps, onSelect }) => {
  if (gaps.length === 0) {
    return <EmptyMessage message="No keyword gaps identified. Your rankings look solid for this period." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <p style={{ margin: '0 0 6px', fontSize: '14px', color: '#555' }}>
        These keywords rank between positions 4-20. Writing targeted content could push them to page 1 where CTR increases dramatically.
      </p>
      {gaps.map((gap, i) => (
        <div
          key={i}
          style={{
            padding: '14px 16px', border: '1px solid #e0e0e0', borderRadius: '10px',
            cursor: 'pointer', display: 'flex', justifyContent: 'space-between',
            alignItems: 'center', transition: 'background-color 0.15s',
          }}
          onClick={() => onSelect(gap.keyword)}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0f7ff'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fff'}
        >
          <div>
            <span style={{ fontWeight: 600, fontSize: '15px', color: '#1a1a1a' }}>{gap.keyword}</span>
            <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
              {gap.current_ctr}% CTR &middot; {gap.clicks} clicks
            </div>
          </div>
          <div style={{ textAlign: 'right', fontSize: '12px' }}>
            <div style={{ color: gap.position <= 10 ? '#1565c0' : '#f57c00', fontWeight: 600 }}>Position #{gap.position.toFixed(0)}</div>
            <div style={{ color: '#2e7d32', fontWeight: 500 }}>+{gap.estimated_traffic_if_page1} clicks/mo if page 1</div>
          </div>
        </div>
      ))}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  Pages Tab                                                           */
/* ------------------------------------------------------------------ */

const PagesTab: React.FC<{ pages: PageOpportunity[] }> = ({ pages }) => {
  if (pages.length === 0) {
    return <EmptyMessage message="No page-level issues found. Your pages are performing well." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <p style={{ margin: '0 0 4px', fontSize: '14px', color: '#555' }}>
        These pages get significant impressions but low click-through rates. Improving their titles and meta descriptions can boost clicks.
      </p>
      {pages.map((pg, i) => (
        <div key={i} style={{
          padding: '16px 18px', border: '1px solid #e0e0e0', borderRadius: '10px',
          borderLeft: '4px solid #d32f2f',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontWeight: 600, fontSize: '15px', color: '#1a1a1a' }}>{pg.page_title}</span>
            <Badge label={`${pg.current_ctr}% CTR`} color={pg.current_ctr < 1 ? '#d32f2f' : '#f57c00'} />
          </div>
          <p style={{ margin: '0 0 8px', fontSize: '13px', color: '#555', lineHeight: 1.5 }}>{pg.reason}</p>
          <div style={{ fontSize: '12px', color: '#888' }}>
            {pg.impressions.toLocaleString()} impressions &middot; {pg.clicks} clicks &middot; Position {pg.current_position}
          </div>
          <div style={{ fontSize: '11px', color: '#999', marginTop: '6px', wordBreak: 'break-all' }}>{pg.page}</div>
        </div>
      ))}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  AI Recommendations Tab                                              */
/* ------------------------------------------------------------------ */

const AIRecommendationsTab: React.FC<{ recommendations: AIRecommendations | null; onSelect: (kw: string) => void }> = ({ recommendations, onSelect }) => {
  if (!recommendations) {
    return <EmptyMessage message="AI recommendations are not available right now. Try again in a moment." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <RecommendationSection title="Quick Wins (0-30 days)" items={recommendations.immediate_opportunities} onSelect={onSelect} color="#1565c0" />
      <RecommendationSection title="Content Strategy (1-3 months)" items={recommendations.content_strategy} onSelect={onSelect} color="#2e7d32" />
      <RecommendationSection title="Long-Term Vision (3-12 months)" items={recommendations.long_term_strategy} onSelect={onSelect} color="#6a1b9a" />
    </div>
  );
};

const RecommendationSection: React.FC<{ title: string; items: AIRecommendation[]; onSelect: (kw: string) => void; color: string }> = ({ title, items, onSelect, color }) => {
  if (!items || items.length === 0) return null;

  return (
    <div>
      <h4 style={{
        margin: '0 0 12px', fontSize: '15px', color, fontWeight: 600,
        display: 'flex', alignItems: 'center', gap: '8px',
      }}>
        <span style={{
          width: '8px', height: '8px', borderRadius: '50%',
          backgroundColor: color, display: 'inline-block',
        }} />
        {title}
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {items.map((item, i) => (
          <div
            key={i}
            style={{
              padding: '14px 16px', border: '1px solid #e8e8e8', borderRadius: '10px',
              cursor: 'pointer', transition: 'all 0.15s',
            }}
            onClick={() => {
              const kw = item.keyword || item.title.split(/[:(]/)[0].replace(/^[-\s]+/, '').trim();
              if (kw && kw.length > 2) onSelect(kw);
            }}
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#f8faff'; e.currentTarget.style.borderColor = '#c8d8e8'; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#fff'; e.currentTarget.style.borderColor = '#e8e8e8'; }}
          >
            <div style={{ fontWeight: 600, fontSize: '14px', color: '#1a1a1a', marginBottom: '4px' }}>{item.title}</div>
            {item.keyword && <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>
              Target: <strong style={{ color: '#555' }}>{item.keyword}</strong>
            </div>}
            {item.reason && <div style={{ fontSize: '13px', color: '#555', lineHeight: 1.5 }}>{item.reason}</div>}
            <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
              {item.format && <span style={{
                fontSize: '11px', backgroundColor: '#f0f0f0',
                padding: '2px 10px', borderRadius: '4px', color: '#666',
                fontWeight: 500,
              }}>{item.format}</span>}
              {item.estimated_impact && <span style={{
                fontSize: '11px', color: '#2e7d32', fontWeight: 600,
              }}>{item.estimated_impact}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  Shared                                                              */
/* ------------------------------------------------------------------ */

const Badge: React.FC<{ label: string; color: string }> = ({ label, color }) => (
  <span style={{
    fontSize: '11px', fontWeight: 600, padding: '3px 10px',
    borderRadius: '5px', color: '#fff', backgroundColor: color,
    whiteSpace: 'nowrap',
  }}>{label}</span>
);

const EmptyMessage: React.FC<{ message: string }> = ({ message }) => (
  <div style={{ padding: '48px 0', textAlign: 'center' }}>
    <p style={{ color: '#888', margin: 0, fontSize: '14px' }}>{message}</p>
  </div>
);

export default GSCBrainstormModal;