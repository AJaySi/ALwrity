import React, { useState } from 'react';
import { WizardStepProps, ResearchExecution } from '../types/research.types';
import { ResearchResults } from '../../BlogWriter/ResearchResults';
import { ResearchResponse } from '../../../services/researchApi';
import { BlogResearchResponse } from '../../../services/blogWriterApi';
import { IntentResultsDisplay } from './components/IntentResultsDisplay';
import { IntentDrivenResearchResponse } from '../types/intent.types';

type ResultTab = 'summary' | 'deliverables' | 'sources' | 'analysis';

interface StepResultsProps extends WizardStepProps {
  execution?: ResearchExecution;
}

export const StepResults: React.FC<StepResultsProps> = ({ state, onUpdate, onBack, execution }) => {
  const [activeTab, setActiveTab] = useState<ResultTab>('summary');
  
  // Check if we have intent-driven results
  const intentResult: IntentDrivenResearchResponse | null = 
    execution?.intentResult || 
    (state.results as any)?.intent_result || 
    null;
    
  // Determine if we have both types of results
  const hasIntentResults = !!intentResult;
  const hasTraditionalResults = !!state.results && !intentResult;
  const hasAnyResults = hasIntentResults || hasTraditionalResults;
    
  if (!hasAnyResults) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <p style={{ color: '#666' }}>No results available</p>
      </div>
    );
  }
  
  // Get counts for tab badges
  const getTabBadge = (tab: ResultTab): number | undefined => {
    if (!intentResult) return undefined;
    switch (tab) {
      case 'deliverables':
        return (intentResult.statistics?.length || 0) +
               (intentResult.expert_quotes?.length || 0) +
               (intentResult.case_studies?.length || 0) +
               (intentResult.trends?.length || 0) +
               (intentResult.best_practices?.length || 0);
      case 'sources':
        return intentResult.sources?.length || state.results?.sources?.length || 0;
      default:
        return undefined;
    }
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(state.results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `research-${state.keywords.join('-')}-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleStartNew = () => {
    // Reset to step 1 and clear results
    onUpdate({ 
      currentStep: 1, 
      results: null 
    });
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        <h2 style={{ margin: 0, color: '#333' }}>Research Results</h2>
        
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={onBack}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f5f5f5',
              color: '#333',
              border: '1px solid #ddd',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            ← Back
          </button>
          
          <button
            onClick={handleExport}
            style={{
              padding: '8px 16px',
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            📥 Export JSON
          </button>
          
          <button
            onClick={handleStartNew}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f5f5f5',
              color: '#333',
              border: '1px solid #ddd',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            🔄 Start New Research
          </button>
        </div>
      </div>

      {/* Unified Tabbed Results Display */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        border: '1px solid #e0e0e0',
        overflow: 'hidden',
      }}>
        {/* Tab Navigation */}
        {hasIntentResults && (
          <div style={{
            display: 'flex',
            borderBottom: '2px solid #e5e7eb',
            backgroundColor: '#f8fafc',
          }}>
            {[
              { id: 'summary', label: '📋 Summary', icon: '📋' },
              { id: 'deliverables', label: '📊 Deliverables', icon: '📊' },
              { id: 'sources', label: '🔗 Sources', icon: '🔗' },
              { id: 'analysis', label: '📈 Analysis', icon: '📈' },
            ].map((tab) => {
              const badge = getTabBadge(tab.id as ResultTab);
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as ResultTab)}
                  style={{
                    flex: 1,
                    padding: '14px 16px',
                    border: 'none',
                    background: isActive 
                      ? 'white' 
                      : 'transparent',
                    borderBottom: isActive 
                      ? '3px solid #0ea5e9' 
                      : '3px solid transparent',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: isActive ? '600' : '500',
                    color: isActive ? '#0c4a6e' : '#64748b',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = '#f1f5f9';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <span>{tab.label}</span>
                  {badge !== undefined && badge > 0 && (
                    <span style={{
                      backgroundColor: isActive ? '#0ea5e9' : '#e2e8f0',
                      color: isActive ? 'white' : '#64748b',
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '11px',
                      fontWeight: '600',
                    }}>
                      {badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}

        {/* Tab Content */}
        <div style={{ padding: '20px' }}>
          {hasIntentResults ? (
            <>
              {/* Summary Tab */}
              {activeTab === 'summary' && (
                <div style={{ animation: 'fadeIn 0.3s ease' }}>
                  {intentResult.executive_summary && (
                    <div style={{
                      backgroundColor: '#f0f9ff',
                      border: '1px solid #bae6fd',
                      borderRadius: '8px',
                      padding: '16px',
                      marginBottom: '20px',
                    }}>
                      <h4 style={{ margin: '0 0 8px 0', color: '#0c4a6e' }}>Executive Summary</h4>
                      <p style={{ margin: 0, color: '#334155', lineHeight: 1.6 }}>
                        {intentResult.executive_summary}
                      </p>
                    </div>
                  )}
                  
                  {intentResult.primary_answer && (
                    <div style={{
                      backgroundColor: '#f0fdf4',
                      border: '1px solid #86efac',
                      borderRadius: '8px',
                      padding: '16px',
                      marginBottom: '20px',
                    }}>
                      <h4 style={{ margin: '0 0 8px 0', color: '#166534' }}>Direct Answer</h4>
                      <p style={{ margin: 0, color: '#334155', lineHeight: 1.6 }}>
                        {intentResult.primary_answer}
                      </p>
                    </div>
                  )}
                  
                  {intentResult.key_takeaways && intentResult.key_takeaways.length > 0 && (
                    <div style={{ marginBottom: '20px' }}>
                      <h4 style={{ margin: '0 0 12px 0', color: '#333' }}>Key Takeaways</h4>
                      <ul style={{ margin: 0, paddingLeft: '20px' }}>
                        {intentResult.key_takeaways.map((takeaway, idx) => (
                          <li key={idx} style={{ color: '#334155', marginBottom: '8px', lineHeight: 1.5 }}>
                            {takeaway}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Deliverables Tab - Uses IntentResultsDisplay */}
              {activeTab === 'deliverables' && (
                <div style={{ animation: 'fadeIn 0.3s ease' }}>
                  <IntentResultsDisplay result={intentResult} hideHeader />
                </div>
              )}

              {/* Sources Tab - Shows traditional sources view */}
              {activeTab === 'sources' && (
                <div style={{ animation: 'fadeIn 0.3s ease' }}>
                  {intentResult.sources && intentResult.sources.length > 0 ? (
                    <div>
                      <h4 style={{ margin: '0 0 16px 0', color: '#333' }}>
                        {intentResult.sources.length} Sources Found
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {intentResult.sources.map((source: any, idx: number) => (
                          <div 
                            key={idx}
                            style={{
                              padding: '16px',
                              backgroundColor: '#f8fafc',
                              borderRadius: '8px',
                              border: '1px solid #e2e8f0',
                            }}
                          >
                            <a 
                              href={source.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              style={{
                                fontSize: '15px',
                                fontWeight: '600',
                                color: '#0ea5e9',
                                textDecoration: 'none',
                              }}
                            >
                              {source.title}
                            </a>
                            <div style={{ 
                              fontSize: '12px', 
                              color: '#64748b',
                              marginTop: '4px',
                            }}>
                              {source.url}
                            </div>
                            {source.excerpt && (
                              <p style={{
                                margin: '8px 0 0 0',
                                fontSize: '13px',
                                color: '#475569',
                                lineHeight: 1.5,
                              }}>
                                {source.excerpt}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : state.results?.sources ? (
                    <ResearchResults research={state.results} showSourcesOnly />
                  ) : (
                    <p style={{ color: '#666' }}>No sources available</p>
                  )}
                </div>
              )}

              {/* Analysis Tab - Shows keyword analysis, angles, etc. */}
              {activeTab === 'analysis' && (
                <div style={{ animation: 'fadeIn 0.3s ease' }}>
                  {state.results ? (
                    <ResearchResults research={state.results as BlogResearchResponse} showAnalysisOnly />
                  ) : (
                    <div>
                      {intentResult.suggested_outline && intentResult.suggested_outline.length > 0 && (
                        <div style={{ marginBottom: '20px' }}>
                          <h4 style={{ margin: '0 0 12px 0', color: '#333' }}>Suggested Outline</h4>
                          <ol style={{ margin: 0, paddingLeft: '24px' }}>
                            {intentResult.suggested_outline.map((item, idx) => (
                              <li key={idx} style={{ color: '#334155', marginBottom: '8px' }}>
                                {item}
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}
                      
                      {intentResult.gaps_identified && intentResult.gaps_identified.length > 0 && (
                        <div style={{
                          backgroundColor: '#fff7ed',
                          border: '1px solid #fdba74',
                          borderRadius: '8px',
                          padding: '16px',
                        }}>
                          <h4 style={{ margin: '0 0 12px 0', color: '#9a3412' }}>Gaps Identified</h4>
                          <ul style={{ margin: 0, paddingLeft: '20px' }}>
                            {intentResult.gaps_identified.map((gap, idx) => (
                              <li key={idx} style={{ color: '#9a3412', marginBottom: '4px' }}>
                                {gap}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </>
          ) : state.results ? (
            // Traditional results display (no tabs)
            <ResearchResults research={state.results as BlogResearchResponse} />
          ) : (
            <p style={{ color: '#666', textAlign: 'center', padding: '40px' }}>
              No results available
            </p>
          )}
        </div>
      </div>

      {/* Action Section */}
      <div style={{
        marginTop: '24px',
        padding: '16px',
        backgroundColor: '#f0f7ff',
        borderRadius: '8px',
        border: '1px solid #b3d9ff',
      }}>
        <h4 style={{ marginBottom: '8px', color: '#004085' }}>Next Steps</h4>
        <ul style={{ margin: 0, paddingLeft: '20px', color: '#004085', fontSize: '14px' }}>
          <li>Review the research insights and sources</li>
          <li>Explore content angles and competitor analysis</li>
          <li>Use this research to create your blog outline</li>
          <li>Export the data for reference</li>
        </ul>
      </div>
    </div>
  );
};

