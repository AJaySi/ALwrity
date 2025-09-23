import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogOutlineSection, BlogResearchResponse } from '../../services/blogWriterApi';

interface SectionGeneratorProps {
  outline: BlogOutlineSection[];
  research: BlogResearchResponse | null;
  genMode: 'draft' | 'polished';
  onSectionGenerated: (sectionId: string, markdown: string) => void;
  onContinuityRefresh: () => void;
}

const useCopilotActionTyped = useCopilotAction as any;

export const SectionGenerator: React.FC<SectionGeneratorProps> = ({
  outline,
  research,
  genMode,
  onSectionGenerated,
  onContinuityRefresh
}) => {
  useCopilotActionTyped({
    name: 'generateSection',
    description: 'Generate content for a specific section using research and outline',
    parameters: [ { name: 'sectionId', type: 'string', description: 'Section ID', required: true } ],
    handler: async ({ sectionId }: { sectionId: string }) => {
      const section = outline.find(s => s.id === sectionId);
      if (!section) return { success: false, message: 'Section not found. Please generate an outline first.' };
      
      try {
        const res = await blogWriterApi.generateSection({ section, mode: genMode });
        if (res?.markdown) {
          onSectionGenerated(sectionId, res.markdown);
          onContinuityRefresh();
          
          return { 
            success: true, 
            message: `✍️ Content generated for "${section.heading}"! The section incorporates your research findings and primary keywords. You can now review the content, run SEO analysis, or generate more sections.`,
            section_summary: {
              heading: section.heading,
              content_length: res.markdown.length,
              primary_keywords: research?.keyword_analysis?.primary || []
            }
          };
        }
      } catch (error) {
        console.error('Section generation failed:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return { 
          success: false, 
          message: `❌ Content generation failed for "${section.heading}": ${errorMessage}. Please try again or contact support if the problem persists.` 
        };
      }
      return { success: false, message: 'Failed to generate section content. Please try again.' };
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
                border: '2px solid #f57c00',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <h4 style={{ margin: 0, color: '#f57c00' }}>✍️ Generating Section Content</h4>
            </div>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>• Analyzing section requirements and research data...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Incorporating primary keywords and SEO best practices...</p>
              <p style={{ margin: '0 0 8px 0' }}>• Writing engaging content with proper structure...</p>
              <p style={{ margin: '0' }}>• Ensuring factual accuracy and readability...</p>
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
    name: 'generateAllSections',
    description: 'Generate content for every section in the outline',
    parameters: [],
    handler: async () => {
      for (const s of outline) {
        const res = await blogWriterApi.generateSection({ section: s, mode: genMode });
        onSectionGenerated(s.id, res.markdown);
        onContinuityRefresh();
      }
      return { success: true };
    },
    render: ({ status }: any) => (status === 'inProgress' || status === 'executing') ? <div>Generating all sections…</div> : null
  });

  return null; // This component only provides the copilot actions
};

export default SectionGenerator;
