import React, { useState } from 'react';
import { BlogOutlineSection, SourceMappingStats, GroundingInsights, OptimizationResults, ResearchCoverage } from '../../services/blogWriterApi';

interface OutlineIntelligenceChipsProps {
  sections: BlogOutlineSection[];
  sourceMappingStats?: SourceMappingStats | null;
  groundingInsights?: GroundingInsights | null;
  optimizationResults?: OptimizationResults | null;
  researchCoverage?: ResearchCoverage | null;
}

const OutlineIntelligenceChips: React.FC<OutlineIntelligenceChipsProps> = ({
  sections,
  sourceMappingStats,
  groundingInsights,
  optimizationResults,
  researchCoverage
}) => {
  const [activeModal, setActiveModal] = useState<string | null>(null);

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return '#4caf50'; // Green
    if (score >= 0.6) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getQualityGrade = (score: number) => {
    if (score >= 9) return { grade: 'A+', color: '#4caf50' };
    if (score >= 8) return { grade: 'A', color: '#4caf50' };
    if (score >= 7) return { grade: 'B+', color: '#8bc34a' };
    if (score >= 6) return { grade: 'B', color: '#ff9800' };
    if (score >= 5) return { grade: 'C', color: '#ff9800' };
    return { grade: 'D', color: '#f44336' };
  };

  const chips = [
    {
      id: 'research',
      label: 'Research Data',
      icon: '📊',
      color: '#e3f2fd',
      textColor: '#1976d2',
      data: researchCoverage,
      description: 'How well your research data is being utilized',
      metrics: researchCoverage ? [
        { label: 'Sources Used', value: researchCoverage.sources_utilized, color: '#1976d2' },
        { label: 'Content Gaps', value: researchCoverage.content_gaps_identified, color: '#ff9800' },
        { label: 'Advantages', value: researchCoverage.competitive_advantages.length, color: '#4caf50' }
      ] : []
    },
    {
      id: 'mapping',
      label: 'Source Mapping',
      icon: '🔗',
      color: '#f3e5f5',
      textColor: '#7b1fa2',
      data: sourceMappingStats,
      description: 'Intelligence in mapping sources to sections',
      metrics: sourceMappingStats ? [
        { label: 'Mapped', value: sourceMappingStats.total_sources_mapped, color: '#7b1fa2' },
        { label: 'Coverage', value: `${Math.round(sourceMappingStats.coverage_percentage)}%`, color: getConfidenceColor(sourceMappingStats.coverage_percentage / 100) },
        { label: 'Relevance', value: `${Math.round(sourceMappingStats.average_relevance_score * 100)}%`, color: getConfidenceColor(sourceMappingStats.average_relevance_score) },
        { label: 'High Conf', value: sourceMappingStats.high_confidence_mappings, color: '#4caf50' }
      ] : []
    },
    {
      id: 'grounding',
      label: 'Grounding Insights',
      icon: '🧠',
      color: '#e8f5e8',
      textColor: '#2e7d32',
      data: groundingInsights,
      description: 'AI-powered insights from search grounding',
      metrics: groundingInsights ? [
        { 
          label: 'Confidence', 
          value: groundingInsights.confidence_analysis ? `${Math.round(groundingInsights.confidence_analysis.average_confidence * 100)}%` : 'N/A', 
          color: groundingInsights.confidence_analysis ? getConfidenceColor(groundingInsights.confidence_analysis.average_confidence) : '#666' 
        },
        { 
          label: 'Authority', 
          value: groundingInsights.authority_analysis ? `${Math.round(groundingInsights.authority_analysis.average_authority_score * 100)}%` : 'N/A', 
          color: groundingInsights.authority_analysis ? getConfidenceColor(groundingInsights.authority_analysis.average_authority_score) : '#666' 
        },
        { 
          label: 'Coverage', 
          value: groundingInsights.content_relationships ? `${Math.round(groundingInsights.content_relationships.concept_coverage_score * 100)}%` : 'N/A', 
          color: groundingInsights.content_relationships ? getConfidenceColor(groundingInsights.content_relationships.concept_coverage_score) : '#666' 
        }
      ] : []
    },
    {
      id: 'optimization',
      label: 'Optimization',
      icon: '🎯',
      color: '#fff3e0',
      textColor: '#f57c00',
      data: optimizationResults,
      description: 'AI optimization and quality assessment',
      metrics: optimizationResults ? [
        { 
          label: 'Quality', 
          value: `${optimizationResults.overall_quality_score}/10`, 
          color: getQualityGrade(optimizationResults.overall_quality_score).color 
        },
        { 
          label: 'Grade', 
          value: getQualityGrade(optimizationResults.overall_quality_score).grade, 
          color: getQualityGrade(optimizationResults.overall_quality_score).color 
        },
        { 
          label: 'Focus', 
          value: optimizationResults.optimization_focus, 
          color: '#f57c00' 
        },
        { 
          label: 'Improvements', 
          value: optimizationResults.improvements_made.length, 
          color: '#4caf50' 
        }
      ] : []
    }
  ];

  const renderModal = (chipId: string) => {
    const chip = chips.find(c => c.id === chipId);
    if (!chip || !chip.data) return null;

    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '800px',
          width: '95%',
          maxHeight: '85vh',
          overflow: 'auto',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          border: '1px solid #e5e7eb'
        }}>
          {/* Modal Header */}
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '24px',
            paddingBottom: '16px',
            borderBottom: '2px solid #f3f4f6'
          }}>
            <div>
              <h2 style={{ margin: '0 0 4px 0', color: '#1f2937', fontSize: '24px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '28px' }}>{chip.icon}</span>
                {chip.label}
              </h2>
              <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
                {chip.description}
              </p>
            </div>
            <button
              onClick={() => setActiveModal(null)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '28px',
                cursor: 'pointer',
                color: '#9ca3af',
                padding: '4px',
                borderRadius: '6px',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
                e.currentTarget.style.color = '#374151';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#9ca3af';
              }}
            >
              ×
            </button>
          </div>

          {/* Modal Content */}
          <div style={{ color: '#333' }}>
            {chipId === 'research' && researchCoverage && (
              <div>
                {/* Key Metrics */}
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937' }}>Research Utilization Metrics</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                    <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                      <div style={{ fontSize: '32px', fontWeight: '700', color: '#1976d2', marginBottom: '8px' }}>
                        {researchCoverage.sources_utilized}
                      </div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Sources Utilized</div>
                      <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                        Research sources actively used in outline generation
                      </div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                      <div style={{ fontSize: '32px', fontWeight: '700', color: '#ff9800', marginBottom: '8px' }}>
                        {researchCoverage.content_gaps_identified}
                      </div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Content Gaps Identified</div>
                      <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                        Missing topics that could strengthen your content
                      </div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                      <div style={{ fontSize: '32px', fontWeight: '700', color: '#4caf50', marginBottom: '8px' }}>
                        {researchCoverage.competitive_advantages.length}
                      </div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Competitive Advantages</div>
                      <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                        Unique angles identified from research
                      </div>
                    </div>
                  </div>
                </div>

                {/* Competitive Advantages */}
                {researchCoverage.competitive_advantages.length > 0 && (
                  <div>
                    <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937' }}>Key Competitive Advantages</h3>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {researchCoverage.competitive_advantages.map((advantage, i) => (
                        <span key={i} style={{
                          backgroundColor: '#e8f5e8',
                          color: '#388e3c',
                          padding: '8px 16px',
                          borderRadius: '20px',
                          fontSize: '14px',
                          fontWeight: '500',
                          border: '1px solid #c8e6c9'
                        }}>
                          {advantage}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {chipId === 'mapping' && sourceMappingStats && (
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937' }}>Source Mapping Intelligence</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '28px', fontWeight: '700', color: '#7b1fa2', marginBottom: '8px' }}>
                      {sourceMappingStats.total_sources_mapped}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Sources Mapped</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      Research sources intelligently linked to sections
                    </div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '28px', fontWeight: '700', color: getConfidenceColor(sourceMappingStats.coverage_percentage / 100), marginBottom: '8px' }}>
                      {Math.round(sourceMappingStats.coverage_percentage)}%
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Coverage</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      Percentage of sections with mapped sources
                    </div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '28px', fontWeight: '700', color: getConfidenceColor(sourceMappingStats.average_relevance_score), marginBottom: '8px' }}>
                      {Math.round(sourceMappingStats.average_relevance_score * 100)}%
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Avg Relevance</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      How well sources match section content
                    </div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '28px', fontWeight: '700', color: '#4caf50', marginBottom: '8px' }}>
                      {sourceMappingStats.high_confidence_mappings}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>High Confidence</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      Mappings with &gt;80% confidence score
                    </div>
                  </div>
                </div>
              </div>
            )}

            {chipId === 'grounding' && groundingInsights && (
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937' }}>Grounding Metadata Insights</h3>
                
                {/* Confidence Analysis */}
                {groundingInsights.confidence_analysis && (
                  <div style={{ marginBottom: '24px' }}>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#1f2937' }}>Confidence Analysis</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                      <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '28px', fontWeight: '700', color: getConfidenceColor(groundingInsights.confidence_analysis.average_confidence), marginBottom: '8px' }}>
                          {Math.round(groundingInsights.confidence_analysis.average_confidence * 100)}%
                        </div>
                        <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Avg Confidence</div>
                        <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                          Average confidence score across all sources
                        </div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '28px', fontWeight: '700', color: '#4caf50', marginBottom: '8px' }}>
                          {groundingInsights.confidence_analysis.high_confidence_sources_count}
                        </div>
                        <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>High Confidence Sources</div>
                        <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                          Sources with &gt;80% confidence score
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Authority Analysis */}
                {groundingInsights.authority_analysis && (
                  <div style={{ marginBottom: '24px' }}>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#1f2937' }}>Authority Analysis</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                      <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '28px', fontWeight: '700', color: getConfidenceColor(groundingInsights.authority_analysis.average_authority_score), marginBottom: '8px' }}>
                          {Math.round(groundingInsights.authority_analysis.average_authority_score * 100)}%
                        </div>
                        <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Avg Authority</div>
                        <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                          Average authority score of sources
                        </div>
                      </div>
                    </div>
                    {groundingInsights.authority_analysis.high_authority_sources.length > 0 && (
                      <div style={{ marginTop: '16px' }}>
                        <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>Top Authority Sources:</h5>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {groundingInsights.authority_analysis.high_authority_sources.slice(0, 5).map((source, i) => (
                            <span key={i} style={{
                              backgroundColor: '#e3f2fd',
                              color: '#1976d2',
                              padding: '6px 12px',
                              borderRadius: '16px',
                              fontSize: '12px',
                              fontWeight: '500',
                              border: '1px solid #bbdefb'
                            }}>
                              {source.title.substring(0, 40)}...
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Content Relationships */}
                {groundingInsights.content_relationships && (
                  <div style={{ marginBottom: '24px' }}>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#1f2937' }}>Content Relationships</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                      <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '28px', fontWeight: '700', color: getConfidenceColor(groundingInsights.content_relationships.concept_coverage_score), marginBottom: '8px' }}>
                          {Math.round(groundingInsights.content_relationships.concept_coverage_score * 100)}%
                        </div>
                        <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Concept Coverage</div>
                        <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                          How well concepts are covered across sections
                        </div>
                      </div>
                    </div>
                    {groundingInsights.content_relationships.related_concepts.length > 0 && (
                      <div style={{ marginTop: '16px' }}>
                        <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>Related Concepts:</h5>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {groundingInsights.content_relationships.related_concepts.slice(0, 8).map((concept, i) => (
                            <span key={i} style={{
                              backgroundColor: '#fff3e0',
                              color: '#f57c00',
                              padding: '6px 12px',
                              borderRadius: '16px',
                              fontSize: '12px',
                              fontWeight: '500',
                              border: '1px solid #ffcc02'
                            }}>
                              {concept}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Search Intent */}
                {groundingInsights.search_intent_insights && (
                  <div>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#1f2937' }}>Search Intent Analysis</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                      <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '20px', fontWeight: '700', color: '#1976d2', marginBottom: '8px', textTransform: 'capitalize' }}>
                          {groundingInsights.search_intent_insights.primary_intent}
                        </div>
                        <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Primary Intent</div>
                        <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                          Main user intent identified from search data
                        </div>
                      </div>
                    </div>
                    {groundingInsights.search_intent_insights.user_questions.length > 0 && (
                      <div style={{ marginTop: '16px' }}>
                        <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1f2937' }}>User Questions:</h5>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {groundingInsights.search_intent_insights.user_questions.slice(0, 5).map((question, i) => (
                            <span key={i} style={{
                              backgroundColor: '#f3e5f5',
                              color: '#7b1fa2',
                              padding: '6px 12px',
                              borderRadius: '16px',
                              fontSize: '12px',
                              fontWeight: '500',
                              border: '1px solid #ce93d8'
                            }}>
                              {question.substring(0, 50)}...
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {chipId === 'optimization' && optimizationResults && (
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937' }}>Optimization Results</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '32px', fontWeight: '700', color: getQualityGrade(optimizationResults.overall_quality_score).color, marginBottom: '8px' }}>
                      {optimizationResults.overall_quality_score}/10
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Overall Quality</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      AI-assessed quality score of the outline
                    </div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '32px', fontWeight: '700', color: getQualityGrade(optimizationResults.overall_quality_score).color, marginBottom: '8px' }}>
                      {getQualityGrade(optimizationResults.overall_quality_score).grade}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Quality Grade</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      Letter grade based on quality assessment
                    </div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '20px', fontWeight: '700', color: '#f57c00', marginBottom: '8px', textTransform: 'capitalize' }}>
                      {optimizationResults.optimization_focus}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Focus Area</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      Primary area of optimization focus
                    </div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <div style={{ fontSize: '32px', fontWeight: '700', color: '#4caf50', marginBottom: '8px' }}>
                      {optimizationResults.improvements_made.length}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Improvements Made</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                      Number of optimizations applied
                    </div>
                  </div>
                </div>
                
                {optimizationResults.improvements_made.length > 0 && (
                  <div>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#1f2937' }}>Improvements Made:</h4>
                    <div style={{ backgroundColor: '#f8f9fa', borderRadius: '12px', padding: '16px', border: '1px solid #e5e7eb' }}>
                      <ul style={{ margin: 0, paddingLeft: '20px' }}>
                        {optimizationResults.improvements_made.map((improvement, i) => (
                          <li key={i} style={{ fontSize: '14px', color: '#374151', marginBottom: '8px', lineHeight: '1.5' }}>
                            {improvement}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const availableChips = chips.filter(chip => chip.data);

  if (availableChips.length === 0) return null;

  return (
    <>
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {availableChips.map(chip => (
          <button
            key={chip.id}
            onClick={() => setActiveModal(chip.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 16px',
              backgroundColor: chip.color,
              color: chip.textColor,
              border: 'none',
              borderRadius: '24px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              minWidth: '140px',
              justifyContent: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
            }}
          >
            <span style={{ fontSize: '16px' }}>{chip.icon}</span>
            <span>{chip.label}</span>
          </button>
        ))}
      </div>

      {activeModal && renderModal(activeModal)}
    </>
  );
};

export default OutlineIntelligenceChips;