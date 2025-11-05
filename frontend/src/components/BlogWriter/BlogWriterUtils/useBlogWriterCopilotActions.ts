import { useRef } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { debug } from '../../../utils/debug';

type ConfirmCb = () => string | Promise<string>;
type AnalyzeCb = () => string | Promise<string>;
type OpenMetadataCb = () => void;

interface UseBlogWriterCopilotActionsParams {
  isSEOAnalysisModalOpen: boolean;
  lastSEOModalOpenRef: React.MutableRefObject<number>;
  runSEOAnalysisDirect: AnalyzeCb;
  confirmBlogContent: ConfirmCb;
  sections: Record<string, string>;
  research: any;
  openSEOMetadata: OpenMetadataCb;
  navigateToPhase?: (phase: string) => void;
}

// Consolidates all Copilot actions used by BlogWriter
export function useBlogWriterCopilotActions({
  isSEOAnalysisModalOpen,
  lastSEOModalOpenRef,
  runSEOAnalysisDirect,
  confirmBlogContent,
  sections,
  research,
  openSEOMetadata,
  navigateToPhase,
}: UseBlogWriterCopilotActionsParams) {
  // Maintain the same any-cast pattern for parity with component
  const useCopilotActionTyped = useCopilotAction as any;

  // confirmBlogContent
  useCopilotActionTyped({
    name: 'confirmBlogContent',
    description: 'Confirm that the blog content is ready and move to the next stage (SEO analysis)',
    parameters: [],
    handler: async () => {
      // Navigate to SEO phase when content is confirmed
      navigateToPhase?.('seo');
      const msg = await confirmBlogContent();
      return msg;
    },
  });

  // analyzeSEO
  useCopilotActionTyped({
    name: 'analyzeSEO',
    description: 'Analyze the blog content for SEO optimization and provide detailed recommendations',
    parameters: [],
    handler: async () => {
      // Navigate to SEO phase when SEO analysis starts
      navigateToPhase?.('seo');
      
      debug.log('[BlogWriter] SEO analysis action', {
        modalOpen: isSEOAnalysisModalOpen,
        hasSections: !!sections && Object.keys(sections).length > 0,
        hasResearch: !!research && !!(research as any)?.keyword_analysis,
      });
      const now = Date.now();
      if (isSEOAnalysisModalOpen || now - lastSEOModalOpenRef.current < 750) {
        return 'SEO analysis is already open.';
      }
      const msg = await runSEOAnalysisDirect();
      return msg;
    },
  });

  // generateSEOMetadata
  useCopilotActionTyped({
    name: 'generateSEOMetadata',
    description: 'Generate comprehensive SEO metadata including titles, descriptions, Open Graph tags, Twitter cards, and structured data',
    parameters: [
      {
        name: 'title',
        type: 'string',
        description: 'Optional blog title to use for metadata generation',
        required: false,
      },
    ],
    handler: async ({ title }: { title?: string }) => {
      // Navigate to SEO phase when SEO metadata generation starts
      navigateToPhase?.('seo');
      
      if (!sections || Object.keys(sections).length === 0) {
        return 'Please generate blog content first before creating SEO metadata. Use the content generation features to create your blog post.';
      }
      if (!research || !research.keyword_analysis) {
        return 'Please complete research first to get keyword data for SEO metadata generation. Use the research features to gather keyword insights.';
      }
      openSEOMetadata();
      return 'Opening SEO metadata generator! This will create optimized titles, descriptions, Open Graph tags, Twitter cards, and structured data for your blog post.';
    },
  });
}

export default useBlogWriterCopilotActions;


