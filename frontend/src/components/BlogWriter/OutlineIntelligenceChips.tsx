import React, { useState } from 'react';
import { BlogOutlineSection, SourceMappingStats, GroundingInsights, ResearchCoverage } from '../../services/blogWriterApi';

interface OutlineIntelligenceChipsProps {
  sections: BlogOutlineSection[];
  sourceMappingStats?: SourceMappingStats | null;
  groundingInsights?: GroundingInsights | null;
  researchCoverage?: ResearchCoverage | null;
}

const fmtPct = (v: number | undefined | null) =>
  v != null && v > 0 ? `${Math.round(v * 100)}%` : 'N/A';

const fmtPctRaw = (v: number | undefined | null) =>
  v != null && v > 0 ? `${Math.round(v)}%` : 'N/A';

const chipBtn = (color: string, textColor: string) => ({
  display: 'flex' as const,
  alignItems: 'center' as const,
  gap: '8px',
  padding: '10px 14px',
  backgroundColor: color,
  color: textColor,
  border: 'none',
  borderRadius: '24px',
  fontSize: '13px',
  fontWeight: '600',
  cursor: 'pointer' as const,
  transition: 'all 0.2s ease',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  minWidth: '130px',
  justifyContent: 'center' as const,
});

const metricCard = (compact = false) => ({
  textAlign: 'center' as const,
  padding: compact ? '10px 8px' : '14px 10px',
  backgroundColor: '#f8f9fa',
  borderRadius: '8px',
  border: '1px solid #e5e7eb',
});

const metricValue = (size = '20px') => ({
  fontSize: size,
  fontWeight: '700' as const,
  marginBottom: '4px',
});

const metricLabel = { fontSize: '12px', color: '#6b7280', fontWeight: '500' as const };

const getConfidenceColor = (score: number) => {
  if (score >= 0.8) return '#4caf50';
  if (score >= 0.6) return '#ff9800';
  return '#f44336';
};

const modalOverlay: React.CSSProperties = {
  position: 'fixed',
  top: 0, left: 0, right: 0, bottom: 0,
  backgroundColor: 'rgba(0,0,0,0.5)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
};

const modalCard: React.CSSProperties = {
  backgroundColor: 'white',
  borderRadius: '12px',
  padding: '24px',
  maxWidth: '80vw',
  width: '80vw',
  maxHeight: '80vh',
  overflow: 'auto',
  boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
  border: '1px solid #e5e7eb',
};

const OutlineIntelligenceChips: React.FC<OutlineIntelligenceChipsProps> = ({
  sections,
  sourceMappingStats,
  groundingInsights,
  researchCoverage,
}) => {
  const [activeModal, setActiveModal] = useState<string | null>(null);

  const researchUtilData = sourceMappingStats && researchCoverage
    ? {
        sourcesMapped: sourceMappingStats.total_sources_mapped,
        coveragePercent: sourceMappingStats.coverage_percentage,
        avgRelevance: sourceMappingStats.average_relevance_score,
        highConfMappings: sourceMappingStats.high_confidence_mappings,
        contentGaps: researchCoverage.content_gaps_identified,
        advantages: researchCoverage.competitive_advantages,
      }
    : null;

  const ci = groundingInsights;

  const contentIntelData = ci
    ? {
        confidence: ci.confidence_analysis,
        authority: ci.authority_analysis,
        relationships: ci.content_relationships,
        searchIntent: ci.search_intent_insights,
      }
    : null;

  const chips = [
    {
      id: 'utilization',
      label: 'Research to Outline',
      icon: '📊',
      color: '#e8eaf6',
      textColor: '#283593',
      data: researchUtilData,
      description: 'How research sources are mapped and leveraged in the outline',
      metrics: researchUtilData
        ? [
            { label: 'Mapped', value: researchUtilData.sourcesMapped, color: '#283593', tooltip: 'Research sources intelligently linked to outline sections' },
            { label: 'Coverage', value: fmtPctRaw(researchUtilData.coveragePercent), color: getConfidenceColor(researchUtilData.coveragePercent / 100), tooltip: 'Percentage of sections with at least one mapped source' },
            { label: 'Gaps', value: researchUtilData.contentGaps, color: '#ff9800', tooltip: 'Content gaps identified from keyword analysis' },
            { label: 'Advantages', value: researchUtilData.advantages.length, color: '#4caf50', tooltip: 'Unique competitive advantages from research' },
          ]
        : [],
    },
    {
      id: 'intelligence',
      label: 'Content Intelligence',
      icon: '🧠',
      color: '#e8f5e8',
      textColor: '#2e7d32',
      data: contentIntelData,
      description: 'AI-powered insights from search grounding data',
      metrics: contentIntelData
        ? [
            { label: 'Confidence', value: fmtPct(contentIntelData.confidence?.average_confidence), color: contentIntelData.confidence?.average_confidence ? getConfidenceColor(contentIntelData.confidence.average_confidence) : '#666', tooltip: 'Average confidence score across all sources' },
            { label: 'Authority', value: fmtPct(contentIntelData.authority?.average_authority_score), color: contentIntelData.authority?.average_authority_score ? getConfidenceColor(contentIntelData.authority.average_authority_score) : '#666', tooltip: 'Average authority score of sources' },
            { label: 'Coverage', value: fmtPct(contentIntelData.relationships?.concept_coverage_score), color: contentIntelData.relationships?.concept_coverage_score ? getConfidenceColor(contentIntelData.relationships.concept_coverage_score) : '#666', tooltip: 'How well concepts are covered across sections' },
          ]
        : [],
    },
  ];

  const renderModal = (chipId: string) => {
    const chip = chips.find((c) => c.id === chipId);
    if (!chip || !chip.data) return null;

    return (
      <div style={modalOverlay}>
        <div style={modalCard}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', paddingBottom: '12px', borderBottom: '2px solid #f3f4f6' }}>
            <div>
              <h2 style={{ margin: 0, color: '#1f2937', fontSize: '20px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span>{chip.icon}</span>
                {chip.label}
              </h2>
              <p style={{ margin: '4px 0 0 0', color: '#6b7280', fontSize: '13px' }}>{chip.description}</p>
            </div>
            <button
              onClick={() => setActiveModal(null)}
              style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#9ca3af', padding: '2px 6px', borderRadius: '4px', lineHeight: 1 }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#f3f4f6'; e.currentTarget.style.color = '#374151'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#9ca3af'; }}
            >
              ×
            </button>
          </div>

          <div style={{ color: '#333' }}>
            {chipId === 'utilization' && researchUtilData && (
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: '8px', marginBottom: '12px' }}>
                  {[
                    { value: researchUtilData.sourcesMapped, label: 'Sources Mapped', hint: 'Sources linked to outline sections', color: '#283593' },
                    { value: `${Math.round(researchUtilData.coveragePercent)}%`, label: 'Coverage', hint: 'Sections with mapped sources', color: getConfidenceColor(researchUtilData.coveragePercent / 100) },
                    { value: `${Math.round(researchUtilData.avgRelevance * 100)}%`, label: 'Avg Relevance', hint: 'Source-section match quality', color: getConfidenceColor(researchUtilData.avgRelevance) },
                    { value: researchUtilData.highConfMappings, label: 'High Conf', hint: 'Mappings with >80% confidence', color: '#4caf50' },
                    { value: researchUtilData.contentGaps, label: 'Content Gaps', hint: 'Missing topics to strengthen content', color: '#ff9800' },
                    { value: researchUtilData.advantages.length, label: 'Advantages', hint: 'Unique angles from research', color: '#4caf50' },
                  ].map((m, i) => (
                    <div key={i} style={metricCard(true)} title={m.hint}>
                      <div style={{ ...metricValue('20px'), color: m.color }}>{m.value}</div>
                      <div style={metricLabel}>{m.label}</div>
                    </div>
                  ))}
                </div>

                {researchUtilData.advantages.length > 0 && (
                  <div>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>Key Competitive Advantages</h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {researchUtilData.advantages.map((a, i) => (
                        <span key={i} style={{ backgroundColor: '#e8f5e8', color: '#388e3c', padding: '4px 12px', borderRadius: '16px', fontSize: '12px', fontWeight: '500', border: '1px solid #c8e6c9' }}>{a}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {chipId === 'intelligence' && contentIntelData && (
              <div>
                {/* Confidence Analysis — always visible */}
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>Confidence Analysis</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '8px' }}>
                    <div style={metricCard(true)} title="Average confidence score across all sources">
                      <div style={{ ...metricValue('20px'), color: contentIntelData.confidence?.average_confidence ? getConfidenceColor(contentIntelData.confidence.average_confidence) : '#9ca3af' }}>
                        {contentIntelData.confidence?.average_confidence ? `${Math.round(contentIntelData.confidence.average_confidence * 100)}%` : 'N/A'}
                      </div>
                      <div style={metricLabel}>Avg Confidence</div>
                    </div>
                    <div style={metricCard(true)} title="Sources with >80% confidence">
                      <div style={{ ...metricValue('20px'), color: '#4caf50' }}>
                        {contentIntelData.confidence?.high_confidence_sources_count ?? 'N/A'}
                      </div>
                      <div style={metricLabel}>High Conf Sources</div>
                    </div>
                  </div>
                </div>

                {/* Authority Analysis — always visible */}
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>Authority Analysis</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '8px' }}>
                    <div style={metricCard(true)} title="Average authority score of sources">
                      <div style={{ ...metricValue('20px'), color: contentIntelData.authority?.average_authority_score ? getConfidenceColor(contentIntelData.authority.average_authority_score) : '#9ca3af' }}>
                        {contentIntelData.authority?.average_authority_score ? `${Math.round(contentIntelData.authority.average_authority_score * 100)}%` : 'N/A'}
                      </div>
                      <div style={metricLabel}>Avg Authority</div>
                    </div>
                  </div>
                </div>

                {/* Content Relationships — always visible */}
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>Content Relationships</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '8px' }}>
                    <div style={metricCard(true)} title="How well concepts are covered across sections">
                      <div style={{ ...metricValue('20px'), color: contentIntelData.relationships?.concept_coverage_score ? getConfidenceColor(contentIntelData.relationships.concept_coverage_score) : '#9ca3af' }}>
                        {contentIntelData.relationships?.concept_coverage_score ? `${Math.round(contentIntelData.relationships.concept_coverage_score * 100)}%` : 'N/A'}
                      </div>
                      <div style={metricLabel}>Concept Coverage</div>
                    </div>
                  </div>
                  {(contentIntelData.relationships?.related_concepts?.length ?? 0) > 0 && (
                    <div style={{ marginTop: '8px' }}>
                      <h5 style={{ margin: '0 0 6px 0', fontSize: '12px', color: '#1f2937' }}>Related Concepts:</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {contentIntelData.relationships?.related_concepts?.slice(0, 8).map((c: string, i: number) => (
                          <span key={i} style={{ backgroundColor: '#fff3e0', color: '#f57c00', padding: '4px 10px', borderRadius: '14px', fontSize: '11px', fontWeight: '500', border: '1px solid #ffcc02' }}>{c}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Search Intent Analysis — always visible */}
                <div>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>Search Intent Analysis</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '8px' }}>
                    <div style={metricCard(true)} title="Main user intent identified from search data">
                      <div style={{ ...metricValue('16px'), color: '#1976d2', textTransform: 'capitalize' }}>
                        {contentIntelData.searchIntent?.primary_intent || 'N/A'}
                      </div>
                      <div style={metricLabel}>Primary Intent</div>
                    </div>
                  </div>
                  {(contentIntelData.searchIntent?.user_questions?.length ?? 0) > 0 && (
                    <div style={{ marginTop: '8px' }}>
                      <h5 style={{ margin: '0 0 6px 0', fontSize: '12px', color: '#1f2937' }}>User Questions:</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {contentIntelData.searchIntent?.user_questions?.slice(0, 5).map((q: string, i: number) => (
                          <span key={i} style={{ backgroundColor: '#f3e5f5', color: '#7b1fa2', padding: '4px 10px', borderRadius: '14px', fontSize: '11px', fontWeight: '500', border: '1px solid #ce93d8' }}>{q}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const availableChips = chips.filter((chip) => chip.data);

  if (availableChips.length === 0) return null;

  return (
    <>
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {availableChips.map((chip) => (
          <button
            key={chip.id}
            onClick={() => setActiveModal(chip.id)}
            style={chipBtn(chip.color, chip.textColor)}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)'; }}
          >
            <span>{chip.icon}</span>
            <span>{chip.label}</span>
          </button>
        ))}
      </div>

      {activeModal && renderModal(activeModal)}
    </>
  );
};

export default OutlineIntelligenceChips;
