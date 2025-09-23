import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogResearchResponse, BlogOutlineSection } from '../../services/blogWriterApi';

const useCopilotActionTyped = useCopilotAction as any;

interface ResearchDataActionsProps {
  research: BlogResearchResponse | null;
  onOutlineCreated: (outline: BlogOutlineSection[]) => void;
  onTitleOptionsSet: (titles: string[]) => void;
}

export const ResearchDataActions: React.FC<ResearchDataActionsProps> = ({
  research,
  onOutlineCreated,
  onTitleOptionsSet
}) => {
  // Chat with Research Data
  useCopilotActionTyped({
    name: 'chatWithResearchData',
    description: 'Chat with the research data to explore insights, ask questions, and get recommendations',
    parameters: [
      { name: 'question', type: 'string', description: 'Question or topic to explore in the research data', required: true }
    ],
    handler: async ({ question }: { question: string }) => {
      if (!research) {
        return { 
          success: false, 
          message: 'No research data available. Please complete research first.',
          suggestion: 'Try asking: "I want to research a topic for my blog"'
        };
      }

      // Provide comprehensive research context for the copilot to answer intelligently
      const researchContext = {
        sources: research.sources.length,
        primaryKeywords: research.keyword_analysis?.primary || [],
        secondaryKeywords: research.keyword_analysis?.secondary || [],
        longTailKeywords: research.keyword_analysis?.long_tail || [],
        searchIntent: research.keyword_analysis?.search_intent || 'informational',
        contentAngles: research.suggested_angles || [],
        competitorAnalysis: research.competitor_analysis || {},
        searchQueries: research.search_queries || [],
        topSources: research.sources.slice(0, 5).map(s => ({
          title: s.title,
          credibility: s.credibility_score,
          excerpt: s.excerpt?.substring(0, 200)
        }))
      };

      return {
        success: true,
        message: `I can help you explore the research data! Here's what I found:`,
        research_context: researchContext,
        user_question: question,
        next_step_suggestion: 'Ready to create an outline? Try: "Create outline with custom inputs" or "Let\'s proceed to create an outline"'
      };
    },
    render: ({ status, result }: any) => {
      if (status === 'complete' && result?.success) {
        return (
          <div style={{ 
            padding: '16px', 
            backgroundColor: '#f0f8ff', 
            borderRadius: '8px',
            border: '1px solid #1976d2',
            margin: '8px 0'
          }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#1976d2' }}>🔍 Research Data Insights</h4>
            <div style={{ fontSize: '14px', color: '#333', lineHeight: '1.5', marginBottom: '12px' }}>
              <p style={{ margin: '0 0 8px 0' }}><strong>Your Question:</strong> {result.user_question}</p>
              <p style={{ margin: '0 0 8px 0' }}><strong>Research Summary:</strong></p>
              <ul style={{ margin: '0 0 8px 0', paddingLeft: '20px' }}>
                <li>{result.research_context.sources} authoritative sources found</li>
                <li>Primary keywords: {result.research_context.primaryKeywords.join(', ')}</li>
                <li>Search intent: {result.research_context.searchIntent}</li>
                <li>{result.research_context.contentAngles.length} content angles identified</li>
              </ul>
            </div>
            <div style={{ 
              padding: '12px', 
              backgroundColor: '#e3f2fd', 
              borderRadius: '6px',
              border: '1px solid #1976d2'
            }}>
              <p style={{ margin: '0 0 8px 0', fontWeight: '500', color: '#1976d2' }}>💡 Next Step:</p>
              <p style={{ margin: '0', fontSize: '14px', color: '#333' }}>{result.next_step_suggestion}</p>
            </div>
          </div>
        );
      }
      return null;
    }
  });

  // Create Outline with Custom Inputs
  useCopilotActionTyped({
    name: 'createOutlineWithCustomInputs',
    description: 'Create an outline with custom instructions and requirements from the user',
    parameters: [
      { name: 'customInstructions', type: 'string', description: 'Custom instructions for outline generation', required: true }
    ],
    handler: async ({ customInstructions }: { customInstructions: string }) => {
      if (!research) {
        return { 
          success: false, 
          message: 'No research data available. Please complete research first.',
          suggestion: 'Try asking: "I want to research a topic for my blog"'
        };
      }

      try {
        // Create a custom outline request with user instructions
        const customOutlineRequest = {
          research: research,
          word_count: 1500,
          custom_instructions: customInstructions
        };

        // Start async outline generation
        const { task_id } = await blogWriterApi.startOutlineGeneration(customOutlineRequest);
        
        return {
          success: true,
          message: `Custom outline generation started! Task ID: ${task_id}. Progress will be shown below.`,
          task_id: task_id,
          next_step_suggestion: 'The outline is being generated based on your custom instructions. You can monitor progress below.'
        };
      } catch (error) {
        return { 
          success: false, 
          message: `Custom outline creation failed: ${error}`,
          suggestion: 'Try providing more specific instructions or ask me to help refine your requirements.'
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
                border: '2px solid #673ab7',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <h4 style={{ margin: 0, color: '#673ab7' }}>🎨 Creating Custom Outline</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Analyzing your custom instructions...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Applying requirements to research data...</p>
              <p style={{ margin: '0' }}>• Generating tailored outline structure...</p>
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

  return null; // This component only provides the CopilotKit actions, no UI
};
