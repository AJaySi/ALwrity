import React, { useState } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';

const useCopilotActionTyped = useCopilotAction as any;

interface CustomOutlineFormProps {
  onOutlineCreated?: (outline: any) => void;
}

export const CustomOutlineForm: React.FC<CustomOutlineFormProps> = ({ onOutlineCreated }) => {
  const [customInstructions, setCustomInstructions] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useCopilotActionTyped({
    name: 'getCustomOutlineInstructions',
    description: 'Get custom instructions from user for outline generation',
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
              ✅ Custom outline instructions received! Creating your personalized outline...
            </p>
          </div>
        );
      }

      return (
        <div style={{
          padding: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '12px',
          border: '1px solid #e0e0e0',
          margin: '8px 0'
        }}>
          <h4 style={{ margin: '0 0 16px 0', color: '#333' }}>
            🎨 Create Custom Outline
          </h4>
          <p style={{ margin: '0 0 16px 0', color: '#666', fontSize: '14px' }}>
            {args.prompt || 'Tell me your specific requirements for the blog outline. What should it focus on? What structure do you prefer?'}
          </p>

          <div style={{ display: 'grid', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
                Custom Instructions *
              </label>
              <textarea
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                placeholder="e.g., Focus on beginner-friendly explanations, include case studies, emphasize practical applications, create a step-by-step guide format..."
                style={{
                  width: '100%',
                  minHeight: '120px',
                  padding: '12px',
                  border: '2px solid #1976d2',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  backgroundColor: 'white',
                  boxSizing: 'border-box',
                  resize: 'vertical',
                  fontFamily: 'inherit'
                }}
                autoFocus
                autoComplete="off"
                spellCheck="true"
              />
            </div>

            <div style={{ 
              padding: '12px', 
              backgroundColor: '#e3f2fd', 
              borderRadius: '6px',
              border: '1px solid #1976d2'
            }}>
              <h5 style={{ margin: '0 0 8px 0', color: '#1976d2', fontSize: '14px' }}>💡 Examples:</h5>
              <ul style={{ margin: '0', paddingLeft: '20px', fontSize: '13px', color: '#333' }}>
                <li>"Focus on beginner-friendly explanations with practical examples"</li>
                <li>"Include case studies and real-world applications"</li>
                <li>"Create a step-by-step tutorial format"</li>
                <li>"Emphasize the business benefits and ROI"</li>
                <li>"Make it more technical and detailed for developers"</li>
              </ul>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <button
              onClick={() => {
                if (customInstructions.trim()) {
                  respond?.(customInstructions.trim());
                } else {
                  window.alert('Please provide your custom instructions for the outline.');
                }
              }}
              disabled={!customInstructions.trim() || isSubmitting}
              style={{
                backgroundColor: customInstructions.trim() ? '#1976d2' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                cursor: customInstructions.trim() ? 'pointer' : 'not-allowed',
                fontSize: '14px',
                fontWeight: '500',
                flex: 1
              }}
            >
              {isSubmitting ? '⏳ Creating...' : '🚀 Create Custom Outline'}
            </button>

            <button
              onClick={() => respond?.('CANCEL')}
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
        </div>
      );
    }
  });

  return null; // This component only provides the CopilotKit action, no UI
};
