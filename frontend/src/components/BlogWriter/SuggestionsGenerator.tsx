import React, { useMemo } from 'react';
import { BlogOutlineSection, BlogResearchResponse } from '../../services/blogWriterApi';

interface SuggestionsGeneratorProps {
  research: BlogResearchResponse | null;
  outline: BlogOutlineSection[];
  outlineConfirmed?: boolean;
  researchPolling?: { isPolling: boolean; currentStatus: string };
  outlinePolling?: { isPolling: boolean; currentStatus: string };
  mediumPolling?: { isPolling: boolean; currentStatus: string };
  hasContent?: boolean;
  flowAnalysisCompleted?: boolean;
  contentConfirmed?: boolean;
}

interface SuggestionContext {
  research: BlogResearchResponse | null;
  outline: BlogOutlineSection[];
  outlineConfirmed?: boolean;
  researchPolling?: { isPolling: boolean; currentStatus: string };
  outlinePolling?: { isPolling: boolean; currentStatus: string };
  mediumPolling?: { isPolling: boolean; currentStatus: string };
  hasContent?: boolean;
  flowAnalysisCompleted?: boolean;
  contentConfirmed?: boolean;
  seoAnalysis?: any;
  seoMetadata?: any;
  seoRecommendationsApplied?: boolean;
}

export const useSuggestions = ({
  research,
  outline,
  outlineConfirmed = false,
  researchPolling,
  outlinePolling,
  mediumPolling,
  hasContent = false,
  flowAnalysisCompleted = false,
  contentConfirmed = false,
  seoAnalysis = null,
  seoMetadata = null,
  seoRecommendationsApplied = false
}: SuggestionContext) => {
  return useMemo(() => {
    const items = [] as { title: string; message: string; priority?: 'high' | 'normal' }[];
    
    // Check if any background tasks are currently running
    const isResearchRunning = researchPolling?.isPolling && researchPolling?.currentStatus !== 'completed';
    const isOutlineRunning = outlinePolling?.isPolling && outlinePolling?.currentStatus !== 'completed';
    const isMediumGenerationRunning = mediumPolling?.isPolling && mediumPolling?.currentStatus !== 'completed';
    
    // If research is running, show status instead of other suggestions
    if (isResearchRunning) {
      items.push({ 
        title: '⏳ Research in Progress...', 
        message: `Research is currently running (${researchPolling?.currentStatus}). Please wait for completion.`,
        priority: 'high'
      });
      return items;
    }
    
    // If outline generation is running, show status
    if (isOutlineRunning) {
      items.push({ 
        title: '⏳ Outline Generation in Progress...', 
        message: `Outline is being generated (${outlinePolling?.currentStatus}). Please wait for completion.`,
        priority: 'high'
      });
      return items;
    }
    
    // If medium generation is running, show status
    if (isMediumGenerationRunning) {
      items.push({ 
        title: '⏳ Content Generation in Progress...', 
        message: `Blog content is being generated (${mediumPolling?.currentStatus}). Please wait for completion.`,
        priority: 'high'
      });
      return items;
    }
    
    // Normal workflow suggestions based on current state
    if (!research) {
      items.push({ 
        title: '🔎 Start Research', 
        message: "showResearchForm",
        priority: 'high'
      });
    } else if (research && outline.length === 0) {
      // Research completed, guide user to outline creation
      items.push({ 
        title: 'Next: Create Outline', 
        message: 'Research is complete. Please generate the blog outline now using the existing research data. Use the generateOutline action immediately without asking for additional information.',
        priority: 'high'
      });
      items.push({ 
        title: '💬 Chat with Research Data', 
        message: 'I want to explore the research data and ask questions about the findings'
      });
      items.push({ 
        title: '🎨 Create Custom Outline', 
        message: 'I want to create an outline with my own specific instructions and requirements. Please ask me for my custom requirements.'
      });
    } else if (outline.length > 0 && !outlineConfirmed) {
      // Outline created but not confirmed - focus on outline review and confirmation
      items.push({ 
        title: 'Next: Confirm & Generate Content', 
        message: 'The outline is ready. Confirm the current outline and begin content generation now. Call confirmOutlineAndGenerateContent immediately and do not ask for extra confirmation.',
        priority: 'high'
      });
      items.push({ 
        title: '💬 Chat with Outline', 
        message: 'I want to discuss the outline and get insights about the content structure'
      });
      items.push({ 
        title: '🔧 Refine Outline', 
        message: 'I want to refine the outline structure based on my feedback'
      });
      items.push({ 
        title: '⚖️ Rebalance Word Counts', 
        message: 'Rebalance word count distribution across sections'
      });
    } else if (outline.length > 0 && outlineConfirmed) {
      // Outline confirmed, focus on content generation and optimization
      if (hasContent && !contentConfirmed) {
        items.push({ 
          title: '🔄 ReWrite Blog', 
          message: 'I want to rewrite my blog with different approach, tone, or focus'
        });
        items.push({ 
          title: '📊 Content Analysis', 
          message: 'Analyze the flow and quality of my blog content to get improvement suggestions'
        });
        items.push({ 
          title: 'Next: Run SEO Analysis', 
          message: 'Please analyze the blog content for SEO. Run the analyzeSEO action right away and do not ask for confirmation.'
        });
      } else if (hasContent && contentConfirmed) {
        if (!seoAnalysis) {
          // Prompt to run SEO analysis first
          items.push({
            title: 'Next: Run SEO Analysis',
            message: 'The blog content is confirmed. Execute analyzeSEO immediately to launch the SEO analysis modal without further prompts.',
            priority: 'high'
          });
          items.push({ 
            title: 'Content Analysis', 
            message: 'Analyze the flow and quality of my blog content to get improvement suggestions'
          });
          items.push({
            title: 'Content Analysis',
            message: 'Analyze the flow and quality of my blog content to get improvement suggestions'
          });
        } else if (seoAnalysis && !seoRecommendationsApplied) {
          // SEO analysis exists but recommendations not applied yet
          items.push({
            title: 'Next: Apply SEO Recommendations',
            message: 'Open the SEO analysis modal and apply the actionable recommendations right away. Call analyzeSEO to reopen the modal without extra questions.',
            priority: 'high'
          });
          items.push({
            title: 'Content Analysis',
            message: 'Run analyzeContentQuality to review narrative flow and get final improvement suggestions before publishing.'
          });
          items.push({
            title: '📈 Review SEO Analysis',
            message: 'Show me the latest SEO analysis results again by running analyzeSEO.'
          });
        } else if (seoAnalysis && seoRecommendationsApplied) {
          // SEO analysis exists and recommendations applied - show next steps
          if (!seoMetadata) {
            items.push({
              title: 'Next: Generate SEO Metadata',
              message: 'SEO recommendations are applied. Execute generateSEOMetadata immediately so we can prepare titles, descriptions, and schema without further prompts.',
              priority: 'high'
            });
          } else {
            items.push({
              title: 'Next: Publish',
              message: 'The blog is SEO-optimized. Use publishToPlatform with your preferred destination (wix|wordpress) right away—no additional confirmation needed.',
              priority: 'high'
            });
          }

          items.push({
            title: 'Content Analysis',
            message: 'Run analyzeContentQuality to validate flow, consistency, and progression before publishing.'
          });
          items.push({
            title: 'Publish',
            message: seoMetadata 
              ? 'Publish my blog to your preferred platform using publishToPlatform.'
              : 'Generate SEO metadata first, then publish your blog.'
          });

          if (seoMetadata) {
            items.push({
              title: '🚀 Publish to Wix',
              message: 'Publish my blog to Wix using publishToPlatform with platform "wix".'
            });
            items.push({
              title: '🌐 Publish to WordPress',
              message: 'Publish my blog to WordPress using publishToPlatform with platform "wordpress".'
            });
          }
        }
      } else {
        // No content yet, show generation option
        items.push({ title: '📝 Generate all sections', message: 'Generate all sections of my blog post' });
      }
    }
    
    return items;
  }, [
    research,
    outline,
    outlineConfirmed,
    researchPolling,
    outlinePolling,
    mediumPolling,
    hasContent,
    flowAnalysisCompleted,
    contentConfirmed,
    seoAnalysis,
    seoMetadata,
    seoRecommendationsApplied
  ]);
};

export const SuggestionsGenerator: React.FC<SuggestionsGeneratorProps> = ({ research, outline, outlineConfirmed = false }) => {
  useSuggestions({ research, outline, outlineConfirmed });
  return null; // This is just a utility component
};

export default SuggestionsGenerator;
