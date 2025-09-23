import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogResearchResponse } from '../../services/blogWriterApi';

interface OutlineGeneratorProps {
  research: BlogResearchResponse | null;
  onTaskStart: (taskId: string) => void;
  onPollingStart: (taskId: string) => void;
  onModalShow?: () => void; // Callback to show progress modal immediately
}

const useCopilotActionTyped = useCopilotAction as any;

export const OutlineGenerator: React.FC<OutlineGeneratorProps> = ({
  research,
  onTaskStart,
  onPollingStart,
  onModalShow
}) => {
  useCopilotActionTyped({
    name: 'generateOutline',
    description: 'Generate outline from research results using AI analysis',
    parameters: [],
    handler: async () => {
      if (!research) return { success: false, message: 'No research yet. Please research a topic first.' };
      
      try {
        // Show progress modal immediately when user clicks "Create outline"
        onModalShow?.();
        
        // Start async outline generation
        const { task_id } = await blogWriterApi.startOutlineGeneration({ research });
        
        // Start polling immediately after getting task_id
        // This ensures we catch progress messages from the very beginning
        onTaskStart(task_id);
        onPollingStart(task_id);
        
        return { 
          success: true, 
          message: `🧩 Outline generation started! Task ID: ${task_id}. Progress will be shown below.`,
          task_id: task_id
        };
      } catch (error) {
        console.error('Outline generation failed:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        
        // Provide more specific error messages based on the error type
        let userMessage = '❌ Outline generation failed. ';
        if (errorMessage.includes('503') || errorMessage.includes('overloaded')) {
          userMessage += 'The AI service is temporarily overloaded. Please try again in a few minutes.';
        } else if (errorMessage.includes('timeout')) {
          userMessage += 'The request timed out. Please try again.';
        } else if (errorMessage.includes('Invalid outline structure')) {
          userMessage += 'The AI generated an invalid response. Please try again with different research data.';
        } else {
          userMessage += `${errorMessage}. Please try again or contact support if the problem persists.`;
        }
        
        return { 
          success: false, 
          message: userMessage
        };
      }
    },
    render: ({ status }: any) => {
      console.log('generateOutline render called with status:', status);
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
                border: '2px solid #388e3c',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <h4 style={{ margin: 0, color: '#388e3c' }}>🧩 Generating Outline</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Analyzing research results and content angles...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Structuring content based on keyword analysis...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Creating logical flow and section hierarchy...</p>
              <p style={{ margin: '0' }}>• Optimizing for SEO and reader engagement...</p>
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

  return null; // This component only provides the copilot action
};

export default OutlineGenerator;
