import React, { useState } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogResearchResponse, BlogOutlineSection } from '../../services/blogWriterApi';

// Type assertion for CopilotKit action
const useCopilotActionTyped = useCopilotAction as any;

// Separate component to manage rewrite feedback form state
const RewriteFeedbackFormComponent: React.FC<{
  prompt?: string;
  onSubmit: (data: { feedback: string; tone?: string; audience?: string; focus?: string }) => void;
  onCancel: () => void;
}> = ({ prompt, onSubmit, onCancel }) => {
  const [feedback, setFeedback] = useState('');
  const [tone, setTone] = useState('');
  const [audience, setAudience] = useState('');
  const [focus, setFocus] = useState('');
  const hasValidInput = feedback.trim().length >= 10;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (hasValidInput) {
      onSubmit({ 
        feedback: feedback.trim(), 
        tone: tone.trim() || undefined,
        audience: audience.trim() || undefined,
        focus: focus.trim() || undefined
      });
    } else {
      window.alert('Please provide detailed feedback about what you want to change (at least 10 characters).');
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
        🔄 Let's Rewrite Your Blog
      </h4>
      <p style={{ margin: '0 0 16px 0', color: '#666', fontSize: '14px' }}>
        {prompt || 'Please provide feedback about what you\'d like to change in your blog:'}
      </p>
      
      <div style={{ display: 'grid', gap: '12px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
            What do you want to change? *
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="e.g., I want to focus more on practical applications, make the tone more casual, emphasize real-world examples, etc."
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '2px solid #1976d2',
              borderRadius: '6px',
              fontSize: '14px',
              outline: 'none',
              backgroundColor: 'white',
              boxSizing: 'border-box',
              minHeight: '80px',
              resize: 'vertical'
            }}
            autoFocus
            autoComplete="off"
            spellCheck="false"
          />
          <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
            {feedback.length}/10 characters minimum
          </div>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
            Desired Tone (optional)
          </label>
          <select
            value={tone}
            onChange={(e) => setTone(e.target.value)}
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
            <option value="">Keep current tone</option>
            <option value="professional">Professional</option>
            <option value="casual">Casual</option>
            <option value="authoritative">Authoritative</option>
            <option value="conversational">Conversational</option>
            <option value="humorous">Humorous</option>
            <option value="empathetic">Empathetic</option>
            <option value="academic">Academic</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
            Target Audience (optional)
          </label>
          <input
            type="text"
            value={audience}
            onChange={(e) => setAudience(e.target.value)}
            placeholder="e.g., beginners, professionals, students, general audience"
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
            autoComplete="off"
            spellCheck="false"
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
            Main Focus/Angle (optional)
          </label>
          <input
            type="text"
            value={focus}
            onChange={(e) => setFocus(e.target.value)}
            placeholder="e.g., practical applications, technical deep-dive, beginner-friendly, industry trends"
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
            autoComplete="off"
            spellCheck="false"
          />
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
          🔄 Rewrite Blog {hasValidInput ? '(Enabled)' : '(Disabled)'}
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

interface RewriteFeedbackFormProps {
  research: BlogResearchResponse;
  outline: BlogOutlineSection[];
  sections: Record<string, string>;
  blogTitle: string;
  onRewriteStarted?: (taskId: string) => void;
  onRewriteTriggered?: () => void;
}

export const RewriteFeedbackForm: React.FC<RewriteFeedbackFormProps> = ({
  research,
  outline,
  sections,
  blogTitle,
  onRewriteStarted,
  onRewriteTriggered
}) => {
  const [isCollectingFeedback, setIsCollectingFeedback] = useState(false);

  // Rewrite Blog Action with HITL
  useCopilotActionTyped({
    name: 'rewriteBlog',
    description: 'Rewrite the entire blog based on user feedback and preferences',
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
              ✅ Rewrite feedback received! Starting blog rewrite...
            </p>
          </div>
        );
      }

      return (
        <RewriteFeedbackFormComponent
          prompt={args.prompt}
          onSubmit={(formData) => {
            onRewriteTriggered?.();
            respond?.(JSON.stringify(formData));
          }}
          onCancel={() => respond?.('CANCEL')}
        />
      );
    }
  });

  // Process Rewrite Feedback Action
  useCopilotActionTyped({
    name: 'processRewriteFeedback',
    description: 'Process the rewrite feedback and start the blog rewrite task',
    parameters: [
      { name: 'formData', type: 'string', description: 'JSON string with feedback, tone, audience, and focus', required: true }
    ],
    handler: async ({ formData }: { formData: string }) => {
      try {
        const data = JSON.parse(formData);
        const { feedback, tone, audience, focus } = data;
        
        if (!feedback || feedback.trim().length < 10) {
          return {
            success: false,
            message: 'Please provide more detailed feedback about what you\'d like to change.',
            suggestion: 'Be specific about what aspects of the blog you want to improve, change, or rewrite.'
          };
        }

        // Prepare the rewrite request
        const sectionsData = Object.entries(sections).map(([id, content]: [string, any]) => {
          const outlineSection = outline.find(s => s.id === id);
          return {
            id,
            heading: outlineSection?.heading || 'Untitled Section',
            content: typeof content === 'string' ? content : (content?.content || '')
          };
        });

        if (sectionsData.length === 0) {
          return {
            success: false,
            message: 'No content found to rewrite. Please generate content first.',
            suggestion: 'Generate content for your blog before attempting to rewrite it.'
          };
        }

        // Call the rewrite API
        const result = await blogWriterApi.rewriteBlog({
          title: blogTitle,
          sections: sectionsData,
          research: research,
          outline: outline,
          feedback: feedback.trim(),
          tone: tone?.trim() || undefined,
          audience: audience?.trim() || undefined,
          focus: focus?.trim() || undefined
        });

        if (result.success && result.taskId) {
          onRewriteStarted?.(result.taskId);
          setIsCollectingFeedback(false);

          return {
            success: true,
            message: `Blog rewrite initiated successfully! Your feedback has been processed and the rewrite is in progress.`,
            taskId: result.taskId,
            feedback: {
              original: feedback,
              tone: tone || 'Maintain current tone',
              audience: audience || 'Keep current audience',
              focus: focus || 'Maintain current focus'
            },
            nextStep: 'The rewrite process will take a few moments. You\'ll be notified when it\'s complete.'
          };
        } else {
          return {
            success: false,
            message: 'Failed to initiate blog rewrite.',
            error: result.error || 'Unknown error occurred',
            suggestion: 'Please try again or check if your content is properly generated.'
          };
        }
      } catch (error) {
        console.error('Collect rewrite feedback error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          success: false,
          message: `Failed to process rewrite feedback: ${errorMessage}`,
          suggestion: 'Please try again or provide more specific feedback about what you\'d like to change.'
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
              <h4 style={{ margin: 0, color: '#1976d2' }}>🔄 Rewriting Your Blog</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Analyzing your feedback and preferences...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Processing current content structure...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Generating improved content with new approach...</p>
              <p style={{ margin: '0' }}>• Applying tone and audience adjustments...</p>
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

  return null; // This component doesn't render anything, it just provides actions
};

export default RewriteFeedbackForm;
