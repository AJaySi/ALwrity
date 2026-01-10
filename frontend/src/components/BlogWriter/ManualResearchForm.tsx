import React, { useState, useRef } from 'react';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../../services/blogWriterApi';
import { useBlogWriterResearchPolling } from '../../hooks/usePolling';
import ResearchProgressModal from './ResearchProgressModal';
import { researchCache } from '../../services/researchCache';

interface ManualResearchFormProps {
  onResearchComplete?: (research: BlogResearchResponse) => void;
}

/**
 * Manual research form component that works independently of CopilotKit
 * Extracted from ResearchAction.tsx for use when CopilotKit is unavailable
 */
export const ManualResearchForm: React.FC<ManualResearchFormProps> = ({ onResearchComplete }) => {
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [currentMessage, setCurrentMessage] = useState<string>('');
  const [showProgressModal, setShowProgressModal] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Refs for form inputs (uncontrolled, avoids typing issues)
  const keywordsRef = useRef<HTMLInputElement | null>(null);
  const blogLengthRef = useRef<HTMLSelectElement | null>(null);

  const polling = useBlogWriterResearchPolling({
    onProgress: (message) => {
      setCurrentMessage(message);
    },
    onComplete: (result) => {
      if (result && result.keywords) {
        researchCache.cacheResult(
          result.keywords,
          result.industry || 'General',
          result.target_audience || 'General',
          result
        );
      }
      
      onResearchComplete?.(result);
      setCurrentTaskId(null);
      setCurrentMessage('');
      setShowProgressModal(false);
      setIsSubmitting(false);
    },
    onError: (error) => {
      console.error('Research polling error:', error);
      setCurrentTaskId(null);
      setCurrentMessage('');
      setShowProgressModal(false);
      setIsSubmitting(false);
    }
  });

  const handleSubmit = async () => {
    const keywords = (keywordsRef.current?.value || '').trim();
    const blogLength = blogLengthRef.current?.value || '1000';
    
    if (!keywords) {
      alert('Please enter keywords or a topic for research.');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const keywordList = keywords.includes(',') 
        ? keywords.split(',').map(k => k.trim()).filter(Boolean) 
        : [keywords];
      
      // Check cache first
      const cachedResult = researchCache.getCachedResult(keywordList, 'General', 'General');
      if (cachedResult) {
        onResearchComplete?.(cachedResult);
        setIsSubmitting(false);
        return;
      }
      
      const payload: BlogResearchRequest = { 
        keywords: keywordList, 
        industry: 'General', 
        target_audience: 'General',
        word_count_target: parseInt(blogLength)
      };
      
      const { task_id } = await blogWriterApi.startResearch(payload);
      setCurrentTaskId(task_id);
      setShowProgressModal(true);
      polling.startPolling(task_id);
    } catch (error) {
      console.error('Research failed:', error);
      alert(`Research failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setIsSubmitting(false);
    }
  };

  return (
    <>
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
            disabled={isSubmitting}
            style={{ 
              width: '100%', 
              padding: '12px', 
              border: '1px solid #ddd', 
              borderRadius: '6px', 
              fontSize: '14px', 
              boxSizing: 'border-box',
              opacity: isSubmitting ? 0.6 : 1
            }}
          />
        </div>
        
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>Blog Length (words)</label>
          <select
            id="research-blog-length-select"
            defaultValue="1000"
            ref={blogLengthRef}
            disabled={isSubmitting}
            style={{ 
              width: '100%', 
              padding: '12px', 
              border: '1px solid #ddd', 
              borderRadius: '6px', 
              fontSize: '14px', 
              boxSizing: 'border-box',
              opacity: isSubmitting ? 0.6 : 1
            }}
          >
            <option value="500">500 words (Short blog)</option>
            <option value="1000">1000 words (Medium blog)</option>
            <option value="1500">1500 words (Long blog)</option>
            <option value="2000">2000 words (Comprehensive blog)</option>
          </select>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            style={{ 
              padding: '12px 24px', 
              backgroundColor: isSubmitting ? '#ccc' : '#1976d2', 
              color: 'white', 
              border: 'none', 
              borderRadius: '6px', 
              fontSize: '14px', 
              fontWeight: '500', 
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.7 : 1
            }}
          >
            {isSubmitting ? '⏳ Starting Research...' : '🚀 Start Research'}
          </button>
        </div>
      </div>

      {showProgressModal && (
        <ResearchProgressModal
          open={showProgressModal}
          title="Research in progress"
          status={polling.currentStatus}
          messages={polling.progressMessages}
          error={polling.error}
          onClose={() => setShowProgressModal(false)}
        />
      )}
    </>
  );
};

export default ManualResearchForm;

