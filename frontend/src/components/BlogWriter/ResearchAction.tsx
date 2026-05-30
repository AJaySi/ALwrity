import React, { useState, useRef, useEffect } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { BlogResearchResponse } from '../../services/blogWriterApi';
import { useResearchSubmit } from '../../hooks/useResearchSubmit';
import ResearchProgressModal from './ResearchProgressModal';
import { BrainstormButton } from './BrainstormButton';

const useCopilotActionTyped = useCopilotAction as any;

interface ResearchActionProps {
  onResearchComplete?: (research: BlogResearchResponse) => void;
  navigateToPhase?: (phase: string) => void;
  researchRef?: React.MutableRefObject<((keywords: string, blogLength?: string) => Promise<any>) | null>;
  onBrainstormResult?: (result: import('../../api/gscBrainstorm').BrainstormResult) => void;
}

export const ResearchAction: React.FC<ResearchActionProps> = ({ onResearchComplete, navigateToPhase, researchRef, onBrainstormResult }) => {
  const [copilotKeywords, setCopilotKeywords] = useState('');
  const [copilotBlogLength, setCopilotBlogLength] = useState('1000');
  const hasNavigatedRef = useRef<boolean>(false);

  const {
    startResearch,
    isSubmitting,
    showProgressModal,
    setShowProgressModal,
    currentMessage,
    currentStatus,
    progressMessages,
    error,
    isPolling,
    result,
  } = useResearchSubmit({ onResearchComplete, navigateToPhase });

  // Expose startResearch to parent for header chip "Re-Research"
  React.useEffect(() => {
    if (researchRef) researchRef.current = startResearch;
    return () => { if (researchRef) researchRef.current = null; };
  }, [startResearch, researchRef]);

  // Close modal when research completes (status becomes a completed state or polling stops with a result)
  const COMPLETED_STATUSES = React.useMemo(
    () => new Set(['completed', 'success', 'succeeded', 'finished']),
    []
  );

  useEffect(() => {
    const normalizedStatus = (currentStatus || '').toLowerCase();
    const isCompleted = COMPLETED_STATUSES.has(normalizedStatus);
    const hasResult = !!result;
    const shouldClose = showProgressModal && (
      isCompleted || 
      (hasResult && normalizedStatus !== 'failed') ||
      (!isPolling && hasResult && normalizedStatus !== 'failed')
    );

    if (shouldClose) {
      setShowProgressModal(false);
    }
  }, [COMPLETED_STATUSES, currentStatus, isPolling, result, showProgressModal, setShowProgressModal]);

  useCopilotActionTyped({
    name: 'showResearchForm',
    description: 'Show keyword input form for blog research',
    parameters: [],
    handler: async () => {
      hasNavigatedRef.current = false;
      if (navigateToPhase) {
        navigateToPhase('research');
      }
      return {
        success: true,
        message: "🔍 Let's Research Your Blog Topic\n\nWhat keywords and information would you like to use for your research? Please also specify the desired length of the blog post.\n\nKeywords or Topic *\ne.g., artificial intelligence, machine learning, AI trends\n\nBlog Length (words)\n\n1000 words (Medium blog)\n\n🚀 Start Research",
        showForm: true
      };
    },
    render: ({ status }: any) => {
      const isShowingForm = currentStatus !== 'completed' && 
                           currentStatus !== 'in_progress' && 
                           currentStatus !== 'running';
      
      if (isShowingForm && !hasNavigatedRef.current && navigateToPhase) {
        setTimeout(() => {
          if (!hasNavigatedRef.current) {
            navigateToPhase('research');
            hasNavigatedRef.current = true;
          }
        }, 0);
      }
      
      if (currentStatus === 'completed' && progressMessages.length > 0) {
        const latestMessage = progressMessages[progressMessages.length - 1];
        return (
          <div style={{ padding: '16px', backgroundColor: '#e8f5e8', borderRadius: '8px', border: '1px solid #4caf50', margin: '8px 0' }}>
            <p style={{ margin: 0, color: '#4caf50', fontWeight: '500' }}>✅ Research completed successfully!</p>
            <p style={{ margin: '8px 0 0 0', color: '#666', fontSize: '14px' }}>{latestMessage?.message || 'Research data is now available for your blog.'}</p>
          </div>
        );
      }
      
      if (currentStatus === 'in_progress' || currentStatus === 'running') {
        return (
          <div style={{ padding: '16px', backgroundColor: '#fff3e0', borderRadius: '8px', border: '1px solid #ff9800', margin: '8px 0' }}>
            <p style={{ margin: 0, color: '#ff9800', fontWeight: '500' }}>🔄 Research in progress...</p>
            <p style={{ margin: '8px 0 0 0', color: '#666', fontSize: '14px' }}>{currentMessage || 'Gathering research data...'}</p>
          </div>
        );
      }
      
      return (
        <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e0e0e0', margin: '8px 0' }}>
          <h4 style={{ margin: '0 0 16px 0', color: '#333' }}>🔍 Let's Research Your Blog Topic</h4>
          <p style={{ margin: '0 0 16px 0', color: '#666', fontSize: '14px' }}>
            What keywords and information would you like to use for your research? Please also specify the desired length of the blog post.
          </p>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>Keywords or Topic *</label>
            <input
              type="text"
              id="research-keywords-input"
              placeholder="e.g., artificial intelligence, machine learning, AI trends"
              value={copilotKeywords}
              onChange={(e) => setCopilotKeywords(e.target.value)}
              disabled={isSubmitting}
              style={{ width: '100%', padding: '12px', border: '1px solid #ddd', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box', opacity: isSubmitting ? 0.6 : 1 }}
            />
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>Blog Length (words)</label>
            <select
              id="research-blog-length-select"
              value={copilotBlogLength}
              onChange={(e) => setCopilotBlogLength(e.target.value)}
              disabled={isSubmitting}
              style={{ width: '100%', padding: '12px', border: '1px solid #ddd', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box', opacity: isSubmitting ? 0.6 : 1 }}
            >
              <option value="500">500 words (Short blog)</option>
              <option value="1000">1000 words (Medium blog)</option>
              <option value="1500">1500 words (Long blog)</option>
              <option value="2000">2000 words (Comprehensive blog)</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <BrainstormButton
              keywords={copilotKeywords}
              onKeywordsChange={setCopilotKeywords}
              onBrainstormResult={onBrainstormResult}
              disabled={isSubmitting}
            />
<button
                  onClick={async () => {
                    const kw = copilotKeywords.trim();
                    const bl = copilotBlogLength;
                    if (!kw) return;
                    try {
                      await startResearch(kw, bl);
                    } catch (error) {
                      console.error(`Research failed: ${error}`);
                    }
                  }}
                disabled={isSubmitting}
              style={{ padding: '12px 24px', backgroundColor: isSubmitting ? '#ccc' : '#1976d2', color: 'white', border: 'none', borderRadius: '6px', fontSize: '14px', fontWeight: '500', cursor: isSubmitting ? 'not-allowed' : 'pointer' }}
            >
              {isSubmitting ? '⏳ Researching...' : '🔍 Click To Research'}
            </button>
          </div>
        </div>
      );
    }
  });

  // CopilotKit chat action: research topic with keywords
  useCopilotActionTyped({
    name: 'researchTopic',
    description: 'Research topic with keywords and persona context using Google Search grounding',
    parameters: [
      { name: 'keywords', type: 'string', description: 'Comma-separated keywords or topic description', required: false },
      { name: 'industry', type: 'string', description: 'Industry', required: false },
      { name: 'target_audience', type: 'string', description: 'Target audience', required: false },
      { name: 'blogLength', type: 'string', description: 'Target blog length in words', required: false }
    ],
    handler: async ({ keywords = '', industry = 'General', target_audience = 'General', blogLength = '1000' }: any) => {
      try {
        await startResearch(keywords, blogLength, industry, target_audience);
        return "Starting research with your provided keywords.";
      } catch (error) {
        console.error('Failed to start research:', error);
        return "Failed to start research. Please try again.";
      }
    }
  });

  return (
    <>
      {showProgressModal && (
        <ResearchProgressModal
          open={showProgressModal}
          title="Research in progress"
          status={currentStatus}
          messages={progressMessages}
          error={error}
          onClose={() => setShowProgressModal(false)}
        />
      )}
    </>
  );
};

export default ResearchAction;
