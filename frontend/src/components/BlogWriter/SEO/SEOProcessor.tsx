import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogSEOMetadataResponse } from '../../../services/blogWriterApi';

interface SEOProcessorProps {
  buildFullMarkdown: () => string;
  seoMetadata: BlogSEOMetadataResponse | null;
  onSEOAnalysis: (analysis: any) => void;
  onSEOMetadata: (metadata: BlogSEOMetadataResponse) => void;
}

const useCopilotActionTyped = useCopilotAction as any;

export const SEOProcessor: React.FC<SEOProcessorProps> = ({
  buildFullMarkdown,
  seoMetadata,
  onSEOAnalysis,
  onSEOMetadata
}) => {
  // Removed old runSEOAnalyze action - now using runComprehensiveSEOAnalysis in BlogWriter.tsx

  useCopilotActionTyped({
    name: 'generateSEOMetadata',
    description: 'Generate SEO metadata for the full draft',
    parameters: [ { name: 'title', type: 'string', description: 'Preferred title', required: false } ],
    handler: async ({ title }: { title?: string }) => {
      const content = buildFullMarkdown();
      const res = await blogWriterApi.seoMetadata({ content, title, keywords: [] });
      onSEOMetadata(res);
      return { success: true };
    },
    renderAndWaitForResponse: ({ respond }: any) => (
      <div style={{ padding: 12 }}>
        <div style={{ fontWeight: 600, marginBottom: 8 }}>SEO Metadata Ready</div>
        <div style={{ marginBottom: 8 }}>Review the generated title, meta description, and OG/Twitter tags in the editor.</div>
        <button onClick={() => respond?.('accept')}>Accept Metadata</button>
      </div>
    )
  });

  useCopilotActionTyped({
    name: 'optimizeSection',
    description: 'Optimize a section for readability/EEAT/examples/data with HITL diff',
    parameters: [
      { name: 'sectionId', type: 'string', description: 'Section ID', required: true },
      { name: 'goals', type: 'string', description: 'Comma-separated goals', required: false },
    ],
    handler: async ({ sectionId, goals }: { sectionId: string; goals?: string }) => {
      const current = buildFullMarkdown();
      if (!current) return { success: false, message: 'No content yet for this section' };
      
      // Use comprehensive SEO analysis endpoint
      const response = await fetch('/api/blog-writer/seo/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: current,
          keywords: []
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze blog content');
      }
      
      const res = await response.json();
      onSEOAnalysis(res);
      return { success: true, message: 'Analysis ready' };
    },
    renderAndWaitForResponse: ({ respond, args, status }: any) => {
      if (status === 'complete') return <div>Optimization applied.</div>;
      return (
        <div style={{ padding: 12 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Optimization preview</div>
          <div style={{ marginBottom: 8 }}>Goals: {args.goals || 'readability, EEAT'}</div>
          <button onClick={() => respond?.('apply')}>Apply Changes</button>
        </div>
      );
    }
  });

  return null; // This component only provides the copilot actions
};

export default SEOProcessor;
