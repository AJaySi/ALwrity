import React from 'react';
import { WizardStepProps, ResearchExecution } from '../types/research.types';
import { ResearchResults } from '../../BlogWriter/ResearchResults';
import { BlogResearchResponse } from '../../../services/blogWriterApi';
import { IntentResultsDisplay } from './components/IntentResultsDisplay';
import { IntentDrivenResearchResponse } from '../types/intent.types';

interface StepResultsProps extends WizardStepProps {
  execution?: ResearchExecution;
}

export const StepResults: React.FC<StepResultsProps> = ({ state, onUpdate, onBack, execution }) => {
  // Check if we have intent-driven results
  const intentResult: IntentDrivenResearchResponse | null = 
    execution?.intentResult || 
    (state.results as any)?.intent_result || 
    null;
  if (!state.results) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <p style={{ color: '#666' }}>No results available</p>
      </div>
    );
  }

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

      {/* Results Display */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        border: '1px solid #e0e0e0',
        overflow: 'hidden',
        padding: intentResult ? '16px' : '0',
      }}>
        {intentResult ? (
          <IntentResultsDisplay result={intentResult} />
        ) : (
          <ResearchResults research={state.results} />
        )}
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

