import React, { useState } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { BlogOutlineSection, BlogResearchResponse, blogWriterApi, mediumBlogApi } from '../../services/blogWriterApi';
import { useMediumGenerationPolling } from '../../hooks/usePolling';

// Simple toast notification function
const showToast = (message: string, type: 'success' | 'error' = 'success') => {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    max-width: 400px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateX(100%);
    transition: transform 0.3s ease;
    background-color: ${type === 'success' ? '#4caf50' : '#f44336'};
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // Animate in
  setTimeout(() => {
    toast.style.transform = 'translateX(0)';
  }, 100);
  
  // Remove after 4 seconds
  setTimeout(() => {
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 4000);
};

const useCopilotActionTyped = useCopilotAction as any;

interface OutlineFeedbackFormProps {
  outline: BlogOutlineSection[];
  research: BlogResearchResponse;
  onOutlineConfirmed: () => void;
  onOutlineRefined: (feedback: string) => void;
  onMediumGenerationStarted?: (taskId: string) => void;
  onMediumGenerationTriggered?: () => void;
  sections?: Record<string, string>;
  blogTitle?: string;
  onFlowAnalysisComplete?: (analysis: any) => void;
}


// Separate component to manage feedback form state
const FeedbackForm: React.FC<{
  prompt?: string;
  onSubmit: (data: { feedback: string; action: 'refine' | 'confirm' }) => void;
  onCancel: () => void;
}> = ({ prompt, onSubmit, onCancel }) => {
  const [feedback, setFeedback] = useState('');
  const [action, setAction] = useState<'refine' | 'confirm'>('refine');
  const hasValidInput = feedback.trim().length > 0 || action === 'confirm';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (hasValidInput) {
      onSubmit({ feedback: feedback.trim(), action });
    } else {
      window.alert('Please provide feedback or confirm the outline.');
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
        📝 Outline Review & Feedback
      </h4>
      <p style={{ margin: '0 0 16px 0', color: '#666', fontSize: '14px' }}>
        {prompt || 'Please review the generated outline and provide your feedback:'}
      </p>
      
      <div style={{ display: 'grid', gap: '12px' }}>
        <div>
          <label style={{
            display: 'block',
            marginBottom: '4px',
            fontSize: '14px',
            fontWeight: '500',
            color: '#333'
          }}>
            What would you like to do? *
          </label>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="action"
                value="refine"
                checked={action === 'refine'}
                onChange={(e) => setAction(e.target.value as 'refine' | 'confirm')}
                style={{ margin: 0 }}
              />
              <span style={{ fontSize: '14px' }}>🔧 Refine/Edit Outline</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="action"
                value="confirm"
                checked={action === 'confirm'}
                onChange={(e) => setAction(e.target.value as 'refine' | 'confirm')}
                style={{ margin: 0 }}
              />
              <span style={{ fontSize: '14px' }}>✅ Confirm & Generate Content</span>
            </label>
          </div>
        </div>
        
        {action === 'refine' && (
          <div>
            <label style={{
              display: 'block',
              marginBottom: '4px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#333'
            }}>
              Your Feedback & Suggestions *
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="e.g., Add a section about implementation challenges, Remove the conclusion section, Make the introduction more engaging, Change the order of sections..."
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '2px solid #1976d2',
                borderRadius: '6px',
                fontSize: '14px',
                outline: 'none',
                backgroundColor: 'white',
                boxSizing: 'border-box',
                minHeight: '100px',
                resize: 'vertical',
                fontFamily: 'inherit'
              }}
              autoFocus
              spellCheck="true"
            />
            <div style={{ 
              marginTop: '8px', 
              fontSize: '12px', 
              color: '#666',
              fontStyle: 'italic'
            }}>
              💡 Be specific about what you want to change. The AI will use your feedback to improve the outline.
            </div>
          </div>
        )}

        {action === 'confirm' && (
          <div style={{
            padding: '12px',
            backgroundColor: '#e8f5e8',
            borderRadius: '6px',
            border: '1px solid #4caf50'
          }}>
            <p style={{ margin: 0, color: '#2e7d32', fontSize: '14px' }}>
              ✅ Ready to generate content! Click "Submit" to proceed with content generation for all sections.
            </p>
          </div>
        )}
      </div>
      
      <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
        <button
          type="submit"
          disabled={!hasValidInput}
          style={{
            flex: 1,
            padding: '10px 16px',
            backgroundColor: hasValidInput ? '#1976d2' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: hasValidInput ? 'pointer' : 'not-allowed',
            transition: 'background-color 0.2s ease'
          }}
        >
          {action === 'refine' ? '🔧 Refine Outline' : '✅ Confirm & Generate Content'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          style={{
            padding: '10px 16px',
            backgroundColor: 'transparent',
            color: '#666',
            border: '1px solid #ddd',
            borderRadius: '6px',
            fontSize: '14px',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export const OutlineFeedbackForm: React.FC<OutlineFeedbackFormProps> = ({ 
  outline, 
  research, 
  onOutlineConfirmed, 
  onOutlineRefined,
  onMediumGenerationStarted,
  onMediumGenerationTriggered,
  sections,
  blogTitle,
  onFlowAnalysisComplete
}) => {

  // Refine outline action with HITL
  useCopilotActionTyped({
    name: 'refineOutline',
    description: 'Refine the outline based on user feedback',
    parameters: [
      { name: 'prompt', type: 'string', description: 'Prompt to show user', required: false }
    ],
    handler: async ({ prompt, feedback }: { prompt?: string; feedback?: string }) => {
      // Validate input
      if (!feedback || feedback.trim().length === 0) {
        return { 
          success: false, 
          message: 'Please provide specific feedback for outline refinement.',
          suggestion: 'Try describing what you want to change, add, or remove from the outline.'
        };
      }

      if (!research) {
        return { 
          success: false, 
          message: 'No research data available for outline refinement.',
          suggestion: 'Please complete research first before refining the outline.'
        };
      }

      try {
        // Create a refined outline request with user feedback
        const refineRequest = {
          research: research,
          current_outline: outline,
          user_feedback: feedback.trim(),
          word_count: 1500
        };

        // Start async outline refinement
        const { task_id } = await blogWriterApi.startOutlineGeneration(refineRequest);
        
        return {
          success: true,
          message: `🔧 Outline refinement started based on your feedback! Task ID: ${task_id}. Progress will be shown below.`,
          task_id: task_id,
          next_step_suggestion: 'The outline is being refined based on your feedback. You can monitor progress below.'
        };
      } catch (error) {
        console.error('Outline refinement error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return { 
          success: false, 
          message: `Outline refinement failed: ${errorMessage}`,
          suggestion: 'Try providing more specific feedback or ask me to help clarify your requirements.'
        };
      }
    },
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
              ✅ Outline refinement completed! Check the progress below.
            </p>
          </div>
        );
      }

      if (status === 'executing') {
        return (
          <div style={{ 
            padding: '16px', 
            backgroundColor: '#fff3cd', 
            borderRadius: '8px',
            border: '1px solid #ffc107'
          }}>
            <p style={{ margin: 0, color: '#856404', fontWeight: '500' }}>
              ⏳ Refining outline based on your feedback...
            </p>
          </div>
        );
      }

      return (
        <FeedbackForm
          prompt={args.prompt}
          onSubmit={(formData) => {
            if (formData.action === 'confirm') {
              onOutlineConfirmed();
            } else {
              onOutlineRefined(formData.feedback);
            }
            respond?.(JSON.stringify(formData));
          }}
          onCancel={() => respond?.('CANCEL')}
        />
      );
    }
  });

  // Outline confirmation action
  useCopilotActionTyped({
    name: 'confirmOutlineAndGenerateContent',
    description: 'Confirm the outline and mark it as ready for content generation. This does NOT automatically generate content - it only confirms the outline.',
    parameters: [],
    handler: async () => {
      // Validate that we have an outline to confirm
      if (!outline || outline.length === 0) {
        return { 
          success: false, 
          message: 'No outline available to confirm.',
          suggestion: 'Please generate an outline first before confirming.'
        };
      }

      try {
        onOutlineConfirmed();

        // If research specifies a short/medium blog (<=1000), kick off medium generation
        const target = Number(
          research?.keyword_analysis?.blog_length || 
          (research as any)?.word_count_target || 
          localStorage.getItem('blog_length_target') || 
          0
        );
        
        if (target && target <= 1000) {
          // Show modal immediately when medium generation is triggered
          onMediumGenerationTriggered?.();
          // Build payload for medium generation
          const payload = {
            title: (typeof window !== 'undefined' ? localStorage.getItem('blog_selected_title') : '') || outline[0]?.heading || 'Untitled',
            sections: outline.map(s => ({
              id: s.id,
              heading: s.heading,
              keyPoints: s.key_points,
              subheadings: s.subheadings,
              keywords: s.keywords,
              targetWords: s.target_words,
              references: s.references,
            })),
            globalTargetWords: target,
            researchKeywords: research.original_keywords || research.keyword_analysis?.primary || [], // Use original research keywords for better caching
          };

          const { task_id } = await mediumBlogApi.startMediumGeneration(payload as any);

          // Notify parent to start polling for the medium generation task
          onMediumGenerationStarted?.(task_id);

          // Return message so the copilot shows feedback; UI will display modal via BlogWriter
          return {
            success: true,
            message: `✅ Outline confirmed. Medium generation started (Task: ${task_id}). You can monitor progress in the modal.`,
            task_id,
            action_taken: 'outline_confirmed_medium_generation_started'
          };
        }

        return {
          success: true,
          message: `✅ Outline confirmed! Ready to generate content for ${outline.length} sections.`,
          next_step_suggestion: 'Now you can choose to generate content for individual sections or all sections at once using the available suggestions.',
          outline_sections: outline.length,
          action_taken: 'outline_confirmed_only'
        };
      } catch (error) {
        console.error('Outline confirmation error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return { 
          success: false, 
          message: `Outline confirmation failed: ${errorMessage}`,
          suggestion: 'Please try again or contact support if the problem persists.'
        };
      }
    }
  });

  // Chat with Outline action
  useCopilotActionTyped({
    name: 'chatWithOutline',
    description: 'Chat with the outline to get insights, summaries, and interesting questions about the content structure',
    parameters: [
      { name: 'question', type: 'string', description: 'Question about the outline or content structure', required: false }
    ],
    handler: async ({ question }: { question?: string }) => {
      if (!outline || outline.length === 0) {
        return { 
          success: false, 
          message: 'No outline available to chat with.',
          suggestion: 'Please generate an outline first before chatting about it.'
        };
      }

      if (!research) {
        return { 
          success: false, 
          message: 'No research data available for outline discussion.',
          suggestion: 'Please complete research first before chatting about the outline.'
        };
      }

      try {
        // Provide comprehensive outline and research context
        const outlineContext = {
          totalSections: outline.length,
          sections: outline.map(section => ({
            heading: section.heading,
            subheadings: section.subheadings,
            keyPoints: section.key_points,
            targetWords: section.target_words
          })),
          researchSummary: {
            sources: research.sources?.length || 0,
            primaryKeywords: research.keyword_analysis?.primary || [],
            searchIntent: research.keyword_analysis?.search_intent || 'informational',
            contentAngles: research.suggested_angles || []
          },
          totalTargetWords: outline.reduce((sum, section) => sum + (section.target_words || 0), 0)
        };

        // If no specific question, provide a summary and interesting questions
        if (!question) {
          const summary = `I can see you have a well-structured outline with ${outlineContext.totalSections} sections targeting ${outlineContext.totalTargetWords} words total. The outline covers: ${outline.map(s => s.heading).join(', ')}.`;
          
          const interestingQuestions = [
            "What's the main narrative flow of this outline?",
            "How does each section build upon the previous one?",
            "What are the key takeaways readers will get from each section?",
            "How well does this outline address the search intent: " + outlineContext.researchSummary.searchIntent + "?",
            "What additional sections might strengthen this content?",
            "How can we improve the engagement factor of each section?"
          ];

          return {
            success: true,
            message: `${summary}\n\nHere are some interesting questions to explore:\n${interestingQuestions.map((q, i) => `${i + 1}. ${q}`).join('\n')}`,
            outlineContext: outlineContext,
            next_step_suggestion: 'Ask me any specific questions about the outline structure, content flow, or how to improve it.'
          };
        }

        // Handle specific questions about the outline
        return {
          success: true,
          message: `Great question about the outline! Based on the current structure and research data, I can help you analyze and improve the outline.`,
          outlineContext: outlineContext,
          question: question,
          next_step_suggestion: 'Feel free to ask more specific questions about sections, flow, or content strategy.'
        };
      } catch (error) {
        console.error('Chat with outline error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return { 
          success: false, 
          message: `Failed to chat with outline: ${errorMessage}`,
          suggestion: 'Please try again or ask a more specific question about the outline.'
        };
      }
    }
  });

  // Flow Analysis Actions
  useCopilotActionTyped({
    name: 'analyzeContentQuality',
    description: 'Analyze the flow and quality of blog content to get improvement suggestions (basic analysis)',
    parameters: [],
    handler: async () => {
      try {
        if (!sections || Object.keys(sections).length === 0) {
          return {
            success: false,
            message: 'No content available for analysis. Please generate content first.',
            suggestion: 'Generate content for your blog sections before running quality analysis.'
          };
        }

        // Prepare sections data for analysis
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
            message: 'No valid sections found for analysis.',
            suggestion: 'Ensure your blog has generated content before running analysis.'
          };
        }

        // Call basic flow analysis API
        const result = await blogWriterApi.analyzeFlowBasic({
          title: blogTitle || 'Untitled Blog',
          sections: sectionsData
        });

        if (result.success && result.analysis) {
          // Notify parent component of analysis completion
          onFlowAnalysisComplete?.(result.analysis);

          const analysis = result.analysis;
          const overallFlow = Math.round(analysis.overall_flow_score * 100);
          const overallConsistency = Math.round(analysis.overall_consistency_score * 100);
          const overallProgression = Math.round(analysis.overall_progression_score * 100);

          return {
            success: true,
            message: `Content quality analysis completed! Your blog has an overall flow score of ${overallFlow}%, consistency of ${overallConsistency}%, and progression of ${overallProgression}%.`,
            analysis: {
              overall_scores: {
                flow: overallFlow,
                consistency: overallConsistency,
                progression: overallProgression
              },
              sections: analysis.sections.map((s: any) => ({
                heading: s.heading,
                flow: Math.round(s.flow_score * 100),
                consistency: Math.round(s.consistency_score * 100),
                progression: Math.round(s.progression_score * 100),
                suggestions: s.suggestions
              })),
              overall_suggestions: analysis.overall_suggestions
            },
            next_step_suggestion: 'Use "🔍 Deep Content Analysis" for detailed, section-by-section analysis with more specific recommendations.'
          };
        } else {
          return {
            success: false,
            message: 'Content quality analysis failed.',
            error: result.error || 'Unknown error occurred',
            suggestion: 'Please try again or check if your content is properly generated.'
          };
        }
      } catch (error) {
        console.error('Content quality analysis error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          success: false,
          message: `Failed to analyze content quality: ${errorMessage}`,
          suggestion: 'Please try again or ensure your content is properly generated.'
        };
      }
    }
  });

  useCopilotActionTyped({
    name: 'analyzeContentQualityAdvanced',
    description: 'Get detailed, section-by-section analysis of content quality and flow (advanced analysis)',
    parameters: [],
    handler: async () => {
      try {
        if (!sections || Object.keys(sections).length === 0) {
          return {
            success: false,
            message: 'No content available for advanced analysis. Please generate content first.',
            suggestion: 'Generate content for your blog sections before running advanced analysis.'
          };
        }

        // Prepare sections data for analysis
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
            message: 'No valid sections found for advanced analysis.',
            suggestion: 'Ensure your blog has generated content before running analysis.'
          };
        }

        // Call advanced flow analysis API
        const result = await blogWriterApi.analyzeFlowAdvanced({
          title: blogTitle || 'Untitled Blog',
          sections: sectionsData
        });

        if (result.success && result.analysis) {
          // Notify parent component of analysis completion
          onFlowAnalysisComplete?.(result.analysis);

          const analysis = result.analysis;
          const overallFlow = Math.round(analysis.overall_flow_score * 100);
          const overallConsistency = Math.round(analysis.overall_consistency_score * 100);
          const overallProgression = Math.round(analysis.overall_progression_score * 100);

          return {
            success: true,
            message: `Advanced content analysis completed! Your blog has an overall flow score of ${overallFlow}%, consistency of ${overallConsistency}%, and progression of ${overallProgression}%.`,
            analysis: {
              overall_scores: {
                flow: overallFlow,
                consistency: overallConsistency,
                progression: overallProgression
              },
              sections: analysis.sections.map((s: any) => ({
                heading: s.heading,
                flow: Math.round(s.flow_score * 100),
                consistency: Math.round(s.consistency_score * 100),
                progression: Math.round(s.progression_score * 100),
                detailed_analysis: s.detailed_analysis,
                suggestions: s.suggestions
              }))
            },
            next_step_suggestion: 'Review the detailed analysis and implement the suggested improvements to enhance your content quality.'
          };
        } else {
          return {
            success: false,
            message: 'Advanced content analysis failed.',
            error: result.error || 'Unknown error occurred',
            suggestion: 'Please try again or check if your content is properly generated.'
          };
        }
      } catch (error) {
        console.error('Advanced content analysis error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          success: false,
          message: `Failed to perform advanced content analysis: ${errorMessage}`,
          suggestion: 'Please try again or ensure your content is properly generated.'
        };
      }
    }
  });

  return null; // This component only provides the copilot actions
};

export default OutlineFeedbackForm;
