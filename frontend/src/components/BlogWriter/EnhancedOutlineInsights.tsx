import React, { useState } from 'react';
import { BlogOutlineSection } from '../../services/blogWriterApi';

interface GroundingInsights {
  confidence_analysis?: {
    average_confidence: number;
    high_confidence_sources_count: number;
    confidence_distribution: { high: number; medium: number; low: number };
  };
  authority_analysis?: {
    average_authority_score: number;
    high_authority_sources: Array<{ title: string; url: string; score: number }>;
  };
  content_relationships?: {
    related_concepts: string[];
    content_gaps: string[];
    concept_coverage_score: number;
  };
  search_intent_insights?: {
    primary_intent: string;
    user_questions: string[];
  };
}

interface SourceMappingStats {
  total_sources_mapped: number;
  coverage_percentage: number;
  average_relevance_score: number;
  high_confidence_mappings: number;
}

interface OptimizationResults {
  overall_quality_score: number;
  improvements_made: string[];
  optimization_focus: string;
}

interface Props {
  sections: BlogOutlineSection[];
  groundingInsights?: GroundingInsights;
  sourceMappingStats?: SourceMappingStats;
  optimizationResults?: OptimizationResults;
  researchCoverage?: {
    sources_utilized: number;
    content_gaps_identified: number;
    competitive_advantages: string[];
  };
}

const EnhancedOutlineInsights: React.FC<Props> = ({
  sections,
  groundingInsights,
  sourceMappingStats,
  optimizationResults,
  researchCoverage
}) => {
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());

  const toggleInsight = (insightType: string) => {
    const newExpanded = new Set(expandedInsights);
    if (newExpanded.has(insightType)) {
      newExpanded.delete(insightType);
    } else {
      newExpanded.add(insightType);
    }
    setExpandedInsights(newExpanded);
  };

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

  return (
    <div style={{ 
      backgroundColor: '#f8f9fa', 
      border: '1px solid #e0e0e0', 
      borderRadius: '8px',
      margin: '20px 0',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#1976d2',
        color: 'white',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>
          🧠 Outline Intelligence & Insights
        </h3>
        <span style={{ fontSize: '12px', opacity: 0.9 }}>
          {sections.length} sections analyzed
        </span>
      </div>

      <div style={{ padding: '20px' }}>
        {/* Research Coverage */}
        {researchCoverage && (
          <div style={{ marginBottom: '20px' }}>
            <div 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                cursor: 'pointer',
                padding: '12px',
                backgroundColor: expandedInsights.has('research') ? '#e3f2fd' : 'white',
                border: '1px solid #e0e0e0',
                borderRadius: '6px'
              }}
              onClick={() => toggleInsight('research')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '18px' }}>📊</span>
                <span style={{ fontWeight: '600' }}>Research Data Utilization</span>
              </div>
              <span style={{ fontSize: '14px', color: '#666' }}>
                {expandedInsights.has('research') ? '▼' : '▶'}
              </span>
            </div>
            
            {expandedInsights.has('research') && (
              <div style={{ padding: '16px', backgroundColor: '#fafafa', borderTop: '1px solid #e0e0e0' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '24px', fontWeight: '700', color: '#1976d2' }}>
                      {researchCoverage.sources_utilized}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Sources Utilized</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '24px', fontWeight: '700', color: '#ff9800' }}>
                      {researchCoverage.content_gaps_identified}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Content Gaps Identified</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '24px', fontWeight: '700', color: '#4caf50' }}>
                      {researchCoverage.competitive_advantages.length}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Competitive Advantages</div>
                  </div>
                </div>
                
                {researchCoverage.competitive_advantages.length > 0 && (
                  <div style={{ marginTop: '16px' }}>
                    <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Key Advantages:</h5>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {researchCoverage.competitive_advantages.map((advantage, i) => (
                        <span key={i} style={{
                          backgroundColor: '#e8f5e8',
                          color: '#388e3c',
                          padding: '4px 8px',
                          borderRadius: '12px',
                          fontSize: '12px'
                        }}>
                          {advantage}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Source Mapping Intelligence */}
        {sourceMappingStats && (
          <div style={{ marginBottom: '20px' }}>
            <div 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                cursor: 'pointer',
                padding: '12px',
                backgroundColor: expandedInsights.has('mapping') ? '#e3f2fd' : 'white',
                border: '1px solid #e0e0e0',
                borderRadius: '6px'
              }}
              onClick={() => toggleInsight('mapping')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '18px' }}>🔗</span>
                <span style={{ fontWeight: '600' }}>Source Mapping Intelligence</span>
              </div>
              <span style={{ fontSize: '14px', color: '#666' }}>
                {expandedInsights.has('mapping') ? '▼' : '▶'}
              </span>
            </div>
            
            {expandedInsights.has('mapping') && (
              <div style={{ padding: '16px', backgroundColor: '#fafafa', borderTop: '1px solid #e0e0e0' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: '700', color: '#1976d2' }}>
                      {sourceMappingStats.total_sources_mapped}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Sources Mapped</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: '700', color: getConfidenceColor(sourceMappingStats.coverage_percentage / 100) }}>
                      {sourceMappingStats.coverage_percentage}%
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Coverage</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: '700', color: getConfidenceColor(sourceMappingStats.average_relevance_score) }}>
                      {(sourceMappingStats.average_relevance_score * 100).toFixed(0)}%
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Avg Relevance</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: '700', color: '#4caf50' }}>
                      {sourceMappingStats.high_confidence_mappings}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>High Confidence</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Grounding Insights */}
        {groundingInsights && (
          <div style={{ marginBottom: '20px' }}>
            <div 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                cursor: 'pointer',
                padding: '12px',
                backgroundColor: expandedInsights.has('grounding') ? '#e3f2fd' : 'white',
                border: '1px solid #e0e0e0',
                borderRadius: '6px'
              }}
              onClick={() => toggleInsight('grounding')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '18px' }}>🧠</span>
                <span style={{ fontWeight: '600' }}>Grounding Metadata Insights</span>
              </div>
              <span style={{ fontSize: '14px', color: '#666' }}>
                {expandedInsights.has('grounding') ? '▼' : '▶'}
              </span>
            </div>
            
            {expandedInsights.has('grounding') && (
              <div style={{ padding: '16px', backgroundColor: '#fafafa', borderTop: '1px solid #e0e0e0' }}>
                {/* Confidence Analysis */}
                {groundingInsights.confidence_analysis && (
                  <div style={{ marginBottom: '16px' }}>
                    <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Confidence Analysis</h5>
                    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '18px', fontWeight: '700', color: getConfidenceColor(groundingInsights.confidence_analysis.average_confidence) }}>
                          {(groundingInsights.confidence_analysis.average_confidence * 100).toFixed(0)}%
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>Avg Confidence</div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '18px', fontWeight: '700', color: '#4caf50' }}>
                          {groundingInsights.confidence_analysis.high_confidence_sources_count}
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>High Confidence Sources</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Authority Analysis */}
                {groundingInsights.authority_analysis && (
                  <div style={{ marginBottom: '16px' }}>
                    <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Authority Analysis</h5>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '18px', fontWeight: '700', color: getConfidenceColor(groundingInsights.authority_analysis.average_authority_score) }}>
                          {(groundingInsights.authority_analysis.average_authority_score * 100).toFixed(0)}%
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>Avg Authority</div>
                      </div>
                      {groundingInsights.authority_analysis.high_authority_sources.length > 0 && (
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Top Authority Sources:</div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                            {groundingInsights.authority_analysis.high_authority_sources.slice(0, 3).map((source, i) => (
                              <span key={i} style={{
                                backgroundColor: '#e3f2fd',
                                color: '#1976d2',
                                padding: '2px 6px',
                                borderRadius: '8px',
                                fontSize: '10px'
                              }}>
                                {source.title.substring(0, 30)}...
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Content Relationships */}
                {groundingInsights.content_relationships && (
                  <div style={{ marginBottom: '16px' }}>
                    <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Content Relationships</h5>
                    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '18px', fontWeight: '700', color: getConfidenceColor(groundingInsights.content_relationships.concept_coverage_score) }}>
                          {(groundingInsights.content_relationships.concept_coverage_score * 100).toFixed(0)}%
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>Concept Coverage</div>
                      </div>
                      {groundingInsights.content_relationships.related_concepts.length > 0 && (
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Related Concepts:</div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                            {groundingInsights.content_relationships.related_concepts.slice(0, 5).map((concept, i) => (
                              <span key={i} style={{
                                backgroundColor: '#fff3e0',
                                color: '#f57c00',
                                padding: '2px 6px',
                                borderRadius: '8px',
                                fontSize: '10px'
                              }}>
                                {concept}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Search Intent */}
                {groundingInsights.search_intent_insights && (
                  <div>
                    <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Search Intent Analysis</h5>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '16px', fontWeight: '700', color: '#1976d2', textTransform: 'capitalize' }}>
                          {groundingInsights.search_intent_insights.primary_intent}
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>Primary Intent</div>
                      </div>
                      {groundingInsights.search_intent_insights.user_questions.length > 0 && (
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>User Questions:</div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                            {groundingInsights.search_intent_insights.user_questions.slice(0, 3).map((question, i) => (
                              <span key={i} style={{
                                backgroundColor: '#f3e5f5',
                                color: '#7b1fa2',
                                padding: '2px 6px',
                                borderRadius: '8px',
                                fontSize: '10px'
                              }}>
                                {question.substring(0, 40)}...
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Optimization Results */}
        {optimizationResults && (
          <div>
            <div 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                cursor: 'pointer',
                padding: '12px',
                backgroundColor: expandedInsights.has('optimization') ? '#e3f2fd' : 'white',
                border: '1px solid #e0e0e0',
                borderRadius: '6px'
              }}
              onClick={() => toggleInsight('optimization')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '18px' }}>🎯</span>
                <span style={{ fontWeight: '600' }}>Optimization Results</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ 
                  fontSize: '14px', 
                  fontWeight: '700', 
                  color: getQualityGrade(optimizationResults.overall_quality_score).color 
                }}>
                  {getQualityGrade(optimizationResults.overall_quality_score).grade}
                </span>
                <span style={{ fontSize: '14px', color: '#666' }}>
                  {expandedInsights.has('optimization') ? '▼' : '▶'}
                </span>
              </div>
            </div>
            
            {expandedInsights.has('optimization') && (
              <div style={{ padding: '16px', backgroundColor: '#fafafa', borderTop: '1px solid #e0e0e0' }}>
                <div style={{ marginBottom: '16px' }}>
                  <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Quality Assessment</h5>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ 
                        fontSize: '24px', 
                        fontWeight: '700', 
                        color: getQualityGrade(optimizationResults.overall_quality_score).color 
                      }}>
                        {optimizationResults.overall_quality_score}/10
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>Overall Quality</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '16px', fontWeight: '700', color: '#1976d2', textTransform: 'capitalize' }}>
                        {optimizationResults.optimization_focus}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>Focus Area</div>
                    </div>
                  </div>
                </div>
                
                {optimizationResults.improvements_made.length > 0 && (
                  <div>
                    <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Improvements Made:</h5>
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      {optimizationResults.improvements_made.map((improvement, i) => (
                        <li key={i} style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                          {improvement}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedOutlineInsights;
