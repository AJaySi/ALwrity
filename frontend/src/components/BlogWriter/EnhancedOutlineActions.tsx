import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogOutlineSection } from '../../services/blogWriterApi';

const useCopilotActionTyped = useCopilotAction as any;

interface EnhancedOutlineActionsProps {
  outline: BlogOutlineSection[];
  onOutlineUpdated: (outline: BlogOutlineSection[]) => void;
}

export const EnhancedOutlineActions: React.FC<EnhancedOutlineActionsProps> = ({
  outline,
  onOutlineUpdated
}) => {
  // Enhanced Outline Actions
  useCopilotActionTyped({
    name: 'enhanceSection',
    description: 'Enhance a specific outline section with AI improvements',
    parameters: [
      { name: 'sectionId', type: 'string', description: 'ID of the section to enhance', required: true },
      { name: 'focus', type: 'string', description: 'Enhancement focus (SEO, engagement, depth, etc.)', required: false }
    ],
    handler: async ({ sectionId, focus = 'general improvement' }: { sectionId: string; focus?: string }) => {
      const section = outline.find(s => s.id === sectionId);
      if (!section) return { success: false, message: 'Section not found' };
      
      try {
        const enhancedSection = await blogWriterApi.enhanceSection(section, focus);
        onOutlineUpdated(outline.map(s => s.id === sectionId ? enhancedSection : s));
        return { 
          success: true, 
          message: `Enhanced section "${section.heading}" with focus on ${focus}`,
          enhanced_section: enhancedSection
        };
      } catch (error) {
        return { success: false, message: `Enhancement failed: ${error}` };
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
                border: '2px solid #9c27b0',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <h4 style={{ margin: 0, color: '#9c27b0' }}>✨ Enhancing Section</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Analyzing section content and structure...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Generating enhanced subheadings and key points...</p>
              <p style={{ margin: '0' }}>• Optimizing for better engagement and SEO...</p>
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

  useCopilotActionTyped({
    name: 'optimizeOutline',
    description: 'Optimize entire outline for better flow, SEO, and engagement',
    parameters: [
      { name: 'focus', type: 'string', description: 'Optimization focus (flow, SEO, engagement, etc.)', required: false }
    ],
    handler: async ({ focus = 'general optimization' }: { focus?: string }) => {
      if (outline.length === 0) return { success: false, message: 'No outline to optimize' };
      
      try {
        const optimizedOutline = await blogWriterApi.optimizeOutline({ outline }, focus);
        onOutlineUpdated(optimizedOutline.outline);
        return { 
          success: true, 
          message: `Optimized outline with focus on ${focus}`,
          optimized_outline: optimizedOutline.outline
        };
      } catch (error) {
        return { success: false, message: `Optimization failed: ${error}` };
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
                border: '2px solid #ff9800',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <h4 style={{ margin: 0, color: '#ff9800' }}>🎯 Optimizing Outline</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Analyzing outline structure and flow...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Optimizing headings for SEO and engagement...</p>
              <p style={{ margin: '0' }}>• Improving narrative progression and reader experience...</p>
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

  useCopilotActionTyped({
    name: 'rebalanceOutline',
    description: 'Rebalance word count distribution across outline sections',
    parameters: [
      { name: 'targetWords', type: 'number', description: 'Target total word count', required: false }
    ],
    handler: async ({ targetWords = 1500 }: { targetWords?: number }) => {
      if (outline.length === 0) return { success: false, message: 'No outline to rebalance' };
      
      try {
        const rebalancedOutline = await blogWriterApi.rebalanceOutline({ outline }, targetWords);
        onOutlineUpdated(rebalancedOutline.outline);
        return { 
          success: true, 
          message: `Rebalanced outline for ${targetWords} words`,
          rebalanced_outline: rebalancedOutline.outline
        };
      } catch (error) {
        return { success: false, message: `Rebalancing failed: ${error}` };
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
                border: '2px solid #4caf50',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <h4 style={{ margin: 0, color: '#4caf50' }}>⚖️ Rebalancing Word Counts</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Calculating optimal word distribution...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Adjusting section word counts...</p>
              <p style={{ margin: '0' }}>• Ensuring balanced content structure...</p>
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
