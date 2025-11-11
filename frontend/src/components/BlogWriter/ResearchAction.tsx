import React, { useState, useRef, useEffect } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../../services/blogWriterApi';
import { useResearchPolling } from '../../hooks/usePolling';
import ResearchProgressModal from './ResearchProgressModal';
import { researchCache } from '../../services/researchCache';

const useCopilotActionTyped = useCopilotAction as any;

interface ResearchActionProps {
  onResearchComplete?: (research: BlogResearchResponse) => void;
  navigateToPhase?: (phase: string) => void;
}

export const ResearchAction: React.FC<ResearchActionProps> = ({ onResearchComplete, navigateToPhase }) => {
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [currentMessage, setCurrentMessage] = useState<string>('');
  const [showProgressModal, setShowProgressModal] = useState<boolean>(false);
  const [forceUpdate, setForceUpdate] = useState<number>(0);
  
  // Refs for form inputs (uncontrolled, avoids typing issues inside Copilot render)
  const keywordsRef = useRef<HTMLInputElement | null>(null);
  const blogLengthRef = useRef<HTMLSelectElement | null>(null);
  
  // Track if we've navigated to research phase for this form display
  const hasNavigatedRef = useRef<boolean>(false);

  const polling = useResearchPolling({
    onProgress: (message) => {
      setCurrentMessage(message);
      setForceUpdate(prev => prev + 1); // Force re-render
    },
      onComplete: (result) => {
        console.info('[ResearchAction] ✅ Research completed', { hasResult: !!result });
        
        if (result && result.keywords) {
          researchCache.cacheResult(
            result.keywords,
            result.industry || 'General',
            result.target_audience || 'General',
            result
          );
        }
        
        // Reset navigation tracking when research completes
        hasNavigatedRef.current = false;
        
        onResearchComplete?.(result);
        setCurrentTaskId(null);
        setCurrentMessage('');
        setShowProgressModal(false);
        setForceUpdate(prev => prev + 1);
      },
    onError: (error) => {
      console.error('Research polling error:', error);
      setCurrentTaskId(null);
      setCurrentMessage('');
      setShowProgressModal(false);
      setForceUpdate(prev => prev + 1);
    }
  });

  // Close modal when research completes (status becomes 'completed' or polling stops with result)
  useEffect(() => {
    if (showProgressModal && (
      polling.currentStatus === 'completed' || 
      (!polling.isPolling && polling.result && polling.currentStatus !== 'failed')
    )) {
      console.info('[ResearchAction] Closing modal - research completed', {
        status: polling.currentStatus,
        isPolling: polling.isPolling,
        hasResult: !!polling.result
      });
      // Small delay to show completion message before closing
      const timer = setTimeout(() => {
        setShowProgressModal(false);
        setCurrentTaskId(null);
        setCurrentMessage('');
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [polling.currentStatus, polling.isPolling, polling.result, showProgressModal]);

  useCopilotActionTyped({
    name: 'showResearchForm',
    description: 'Show keyword input form for blog research',
    parameters: [],
    handler: async () => {
      // Navigate to research phase when research form is shown
      // Reset navigation tracking so form render can navigate again if needed
      hasNavigatedRef.current = false;
      // Navigate immediately when handler is called
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
      const _ = forceUpdate;
      
      // Navigate to research phase when form is rendered (if not already navigated and form is shown)
      // This ensures phase navigation updates when CopilotKit shows the research form
      // Only navigate when showing the form (not progress or completion states)
      const isShowingForm = polling.currentStatus !== 'completed' && 
                           polling.currentStatus !== 'in_progress' && 
                           polling.currentStatus !== 'running';
      
      if (isShowingForm && !hasNavigatedRef.current && navigateToPhase) {
        // Use setTimeout to avoid calling during render
        setTimeout(() => {
          if (!hasNavigatedRef.current) {
            navigateToPhase('research');
            hasNavigatedRef.current = true;
          }
        }, 0);
      }
      
      if (polling.currentStatus === 'completed' && polling.progressMessages.length > 0) {
        const latestMessage = polling.progressMessages[polling.progressMessages.length - 1];
        return (
          <div style={{ padding: '16px', backgroundColor: '#e8f5e8', borderRadius: '8px', border: '1px solid #4caf50', margin: '8px 0' }}>
            <p style={{ margin: 0, color: '#4caf50', fontWeight: '500' }}>✅ Research completed successfully!</p>
            <p style={{ margin: '8px 0 0 0', color: '#666', fontSize: '14px' }}>{latestMessage?.message || 'Research data is now available for your blog.'}</p>
          </div>
        );
      }
      
      if (polling.currentStatus === 'in_progress' || polling.currentStatus === 'running') {
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
              ref={keywordsRef}
              style={{ width: '100%', padding: '12px', border: '1px solid #ddd', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box' }}
            />
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>Blog Length (words)</label>
            <select
              id="research-blog-length-select"
              defaultValue="1000"
              ref={blogLengthRef}
              style={{ width: '100%', padding: '12px', border: '1px solid #ddd', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box' }}
            >
              <option value="500">500 words (Short blog)</option>
              <option value="1000">1000 words (Medium blog)</option>
              <option value="1500">1500 words (Long blog)</option>
              <option value="2000">2000 words (Comprehensive blog)</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              onClick={async () => {
                const keywords = (keywordsRef.current?.value || '').trim();
                const blogLength = blogLengthRef.current?.value || '1000';
                if (!keywords) return;
                try {
                  const keywordList = keywords.includes(',') ? keywords.split(',').map(k => k.trim()).filter(Boolean) : [keywords];
                  const cachedResult = researchCache.getCachedResult(keywordList, 'General', 'General');
                  if (cachedResult) {
                    onResearchComplete?.(cachedResult);
                    setForceUpdate(prev => prev + 1);
                    return;
                  }
                  const payload: BlogResearchRequest = { 
                    keywords: keywordList, 
                    industry: 'General', 
                    target_audience: 'General',
                    word_count_target: parseInt(blogLength)
                  };
                  // Navigate to research phase when research starts
                  navigateToPhase?.('research');
                  const { task_id } = await blogWriterApi.startResearch(payload);
                  setCurrentTaskId(task_id);
                  setShowProgressModal(true);
                  polling.startPolling(task_id);
                  setForceUpdate(prev => prev + 1);
                } catch (error) {
                  console.error(`Research failed: ${error}`);
                }
              }}
              style={{ padding: '12px 24px', backgroundColor: '#1976d2', color: 'white', border: 'none', borderRadius: '6px', fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}
            >
              🚀 Start Research
            </button>
          </div>
        </div>
      );
    }
  });

  // Additional action to catch the specific suggestion message
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
        const trimmed = keywords.trim();
        if (!trimmed) {
          return "Please provide keywords or a topic for research.";
        }
        const keywordList = trimmed.includes(',')
          ? trimmed.split(',').map((k: string) => k.trim()).filter(Boolean)
          : [trimmed];
        // Navigate to research phase when research starts
        navigateToPhase?.('research');
        const payload: BlogResearchRequest = { 
          keywords: keywordList, 
          industry, 
          target_audience,
          word_count_target: parseInt(blogLength)
        };
        const { task_id } = await blogWriterApi.startResearch(payload);
        setCurrentTaskId(task_id);
        setShowProgressModal(true);
        polling.startPolling(task_id);
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
          open={showProgressModal && polling.currentStatus !== 'completed'}
          title={"Research in progress"}
          status={polling.currentStatus}
          messages={polling.progressMessages}
          error={polling.error}
          onClose={() => {
            console.info('[ResearchAction] Modal closed manually');
            setShowProgressModal(false);
            setCurrentTaskId(null);
          }}
        />
      )}
    </>
  );
};

export default ResearchAction;
