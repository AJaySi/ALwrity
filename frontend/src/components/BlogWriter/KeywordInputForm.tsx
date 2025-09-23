import React, { useState } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../../services/blogWriterApi';
import ResearchPollingHandler from './ResearchPollingHandler';
import { researchCache } from '../../services/researchCache';

const useCopilotActionTyped = useCopilotAction as any;

interface KeywordInputFormProps {
  onKeywordsReceived?: (data: { keywords: string; blogLength: string }) => void;
  onResearchComplete?: (researchData: BlogResearchResponse) => void;
  onTaskStart?: (taskId: string) => void;
}

// Separate component to manage form state
const ResearchForm: React.FC<{
  prompt?: string;
  onSubmit: (data: { keywords: string; blogLength: string }) => void;
  onCancel: () => void;
}> = ({ prompt, onSubmit, onCancel }) => {
  const [keywords, setKeywords] = useState('');
  const [blogLength, setBlogLength] = useState('1000');
  const hasValidInput = keywords.trim().length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (hasValidInput) {
      onSubmit({ keywords: keywords.trim(), blogLength });
    } else {
      window.alert('Please enter keywords or a topic to start research.');
    }
  };

  return (
    <form 
      onSubmit={handleSubmit}
      style={{ 
        padding: '20px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '12px',
        border: '1px solid #e0e0e0',
        margin: '8px 0'
      }}
    >
      <h4 style={{ margin: '0 0 16px 0', color: '#333' }}>
        🔍 Let's Research Your Blog Topic
      </h4>
      <p style={{ margin: '0 0 16px 0', color: '#666', fontSize: '14px' }}>
        {prompt || 'Please provide the keywords or topic you want to research for your blog:'}
      </p>
      
      <div style={{ display: 'grid', gap: '12px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
            Keywords or Topic *
          </label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            onFocus={(e) => e.target.select()}
            placeholder="e.g., artificial intelligence, machine learning, AI trends"
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '2px solid #1976d2',
              borderRadius: '6px',
              fontSize: '14px',
              outline: 'none',
              backgroundColor: 'white',
              boxSizing: 'border-box'
            }}
            autoFocus
            autoComplete="off"
            spellCheck="false"
          />
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
            Blog Length (words)
          </label>
          <select
            value={blogLength}
            onChange={(e) => setBlogLength(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '2px solid #1976d2',
              borderRadius: '6px',
              fontSize: '14px',
              outline: 'none',
              backgroundColor: 'white',
              boxSizing: 'border-box'
            }}
          >
            <option value="500">500 words (Short blog)</option>
            <option value="1000">1000 words (Medium blog)</option>
            <option value="1500">1500 words (Long blog)</option>
            <option value="2000">2000+ words (Comprehensive guide)</option>
          </select>
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
        <button
          type="submit"
          disabled={!hasValidInput}
          style={{
            backgroundColor: hasValidInput ? '#1976d2' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '10px 20px',
            cursor: hasValidInput ? 'pointer' : 'not-allowed',
            fontSize: '14px',
            fontWeight: '500',
            flex: 1
          }}
        >
          🚀 Start Research {hasValidInput ? '(Enabled)' : '(Disabled)'}
        </button>
        
        <button
          type="button"
          onClick={onCancel}
          style={{
            backgroundColor: 'transparent',
            border: '1px solid #ddd',
            borderRadius: '6px',
            padding: '10px 20px',
            cursor: 'pointer',
            fontSize: '14px',
            color: '#666'
          }}
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export const KeywordInputForm: React.FC<KeywordInputFormProps> = ({ onKeywordsReceived, onResearchComplete, onTaskStart }) => {
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  // Keyword input action with Human-in-the-Loop
  useCopilotActionTyped({
    name: 'getResearchKeywords',
    description: 'Get keywords from user for blog research',
    parameters: [
      { name: 'prompt', type: 'string', description: 'Prompt to show user', required: false }
    ],
    renderAndWaitForResponse: ({ respond, args, status }: { respond?: (value: string) => void; args: { prompt?: string }; status: string }) => {
      if (status === 'complete') {
        return (
          <div style={{ 
            padding: '16px', 
            backgroundColor: '#f0f8ff', 
            borderRadius: '8px',
            border: '1px solid #1976d2'
          }}>
            <p style={{ margin: 0, color: '#1976d2', fontWeight: '500' }}>
              ✅ Research keywords received! Starting research...
            </p>
          </div>
        );
      }

      return (
        <ResearchForm
          prompt={args.prompt}
          onSubmit={(formData) => {
            onKeywordsReceived?.(formData);
            respond?.(JSON.stringify(formData));
          }}
          onCancel={() => respond?.('CANCEL')}
        />
      );
    }
  });

  // Research action that actually performs the research
  useCopilotActionTyped({
    name: 'performResearch',
    description: 'Perform research with collected keywords and blog length',
    parameters: [
      { name: 'formData', type: 'string', description: 'JSON string with keywords and blogLength', required: true }
    ],
    handler: async ({ formData }: { formData: string }) => {
      try {
        const data = JSON.parse(formData);
        const { keywords, blogLength } = data;
        
        const keywordList = keywords.includes(',') 
          ? keywords.split(',').map((k: string) => k.trim())
          : [keywords.trim()]; // Preserve single phrases as-is
        
        // Check frontend cache first
        const cachedResult = researchCache.getCachedResult(keywordList, 'General', 'General');
        if (cachedResult) {
          console.log('Frontend cache hit - returning cached result instantly');
          onResearchComplete?.(cachedResult);
          return { 
            success: true, 
            message: `✅ Found cached research for "${keywords}"! Results loaded instantly.`,
            cached: true
          };
        }
        
        const payload: BlogResearchRequest = { 
          keywords: keywordList, 
          industry: 'General', 
          target_audience: 'General',
          word_count_target: parseInt(blogLength)
        };
        
        // Store the blog length in localStorage for later use
        localStorage.setItem('blog_length_target', blogLength);
        
        // Start async research
        const { task_id } = await blogWriterApi.startResearch(payload);
        setCurrentTaskId(task_id);
        onTaskStart?.(task_id); // Notify parent component to start polling
        
        return { 
          success: true, 
          message: `🔍 Research started for "${keywords}"! Task ID: ${task_id}. Progress will be shown below.`,
          task_id: task_id
        };
      } catch (error) {
        console.error(`Research failed: ${error}`);
        return { 
          success: false, 
          message: `❌ Research failed: ${error}. Please try again with different keywords.` 
        };
      }
    },
    render: ({ status }: any) => {
      if (status === 'inProgress' || status === 'executing') {
        return (
          <div style={{ 
            padding: '16px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            border: '1px solid #e0e0e0',
            margin: '8px 0'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '20px', 
                height: '20px', 
                border: '2px solid #1976d2',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <h4 style={{ margin: 0, color: '#1976d2' }}>🔍 Researching Your Topic</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Connecting to Google Search grounding...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Analyzing keywords and search intent...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Gathering relevant sources and statistics...</p>
              <p style={{ margin: '0' }}>• Generating content angles and search queries...</p>
            </div>
            <style>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        );
      }
      return null;
    }
  });

  return (
    <>
      {/* Polling handler for research progress */}
      <ResearchPollingHandler
        taskId={currentTaskId}
        onResearchComplete={(result) => {
          onResearchComplete?.(result);
          setCurrentTaskId(null);
        }}
        onError={(error) => {
          console.error('Research error:', error);
          setCurrentTaskId(null);
        }}
      />
    </>
  );
};

export default KeywordInputForm;
