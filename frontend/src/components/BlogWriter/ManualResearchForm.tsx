import React, { useState } from 'react';
import { BlogResearchResponse } from '../../services/blogWriterApi';
import { useResearchSubmit } from '../../hooks/useResearchSubmit';
import ResearchProgressModal from './ResearchProgressModal';
import { BrainstormButton } from './BrainstormButton';

interface ManualResearchFormProps {
  onResearchComplete?: (research: BlogResearchResponse) => void;
  onKeywordsChange?: (kw: string) => void;
  blogLengthRef?: React.MutableRefObject<string>;
  researchRef?: React.MutableRefObject<((keywords: string, blogLength?: string) => Promise<any>) | null>;
  onBrainstormResult?: (result: import('../../api/gscBrainstorm').BrainstormResult) => void;
}

export const ManualResearchForm: React.FC<ManualResearchFormProps> = ({ onResearchComplete, onKeywordsChange, blogLengthRef, researchRef, onBrainstormResult }) => {
  const [keywords, setKeywords] = useState('');
  const [blogLength, setBlogLength] = useState('1000');

  // Sync keywords to parent for header chip label
  React.useEffect(() => {
    onKeywordsChange?.(keywords);
  }, [keywords, onKeywordsChange]);

  // Sync blog length to parent ref
  React.useEffect(() => {
    if (blogLengthRef) blogLengthRef.current = blogLength;
  }, [blogLength, blogLengthRef]);

  const {
    startResearch,
    isSubmitting,
    showProgressModal,
    setShowProgressModal,
    currentMessage,
    currentStatus,
    progressMessages,
    error,
  } = useResearchSubmit({ onResearchComplete });

  // Expose startResearch to parent for header chip "Click To Research"
  React.useEffect(() => {
    if (researchRef) researchRef.current = startResearch;
    return () => { if (researchRef) researchRef.current = null; };
  }, [startResearch, researchRef]);

  const handleSubmit = async () => {
    const trimmed = keywords.trim();
    if (!trimmed) {
      alert('Please enter keywords or a topic for research.');
      return;
    }
    try {
      await startResearch(trimmed, blogLength);
    } catch (err) {
      alert(`Research failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
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
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
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
            value={blogLength}
            onChange={(e) => setBlogLength(e.target.value)}
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
          <BrainstormButton
            keywords={keywords}
            onKeywordsChange={setKeywords}
            onBrainstormResult={onBrainstormResult}
            disabled={isSubmitting}
          />
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
            {isSubmitting ? '⏳ Researching...' : '🔍 Click To Research'}
          </button>
        </div>
      </div>

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

export default ManualResearchForm;