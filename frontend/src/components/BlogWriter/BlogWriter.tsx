import React, { useState, useEffect } from 'react';
import { CopilotSidebar } from '@copilotkit/react-ui';
import { useCopilotAction } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import { blogWriterApi } from '../../services/blogWriterApi';
import { useOutlinePolling, useMediumGenerationPolling, useResearchPolling, useRewritePolling } from '../../hooks/usePolling';
import { useClaimFixer } from '../../hooks/useClaimFixer';
import { useMarkdownProcessor } from '../../hooks/useMarkdownProcessor';
import { useBlogWriterState } from '../../hooks/useBlogWriterState';
import { useSuggestions } from './SuggestionsGenerator';
import EnhancedOutlineEditor from './EnhancedOutlineEditor';
import ContinuityBadge from './ContinuityBadge';
import EnhancedTitleSelector from './EnhancedTitleSelector';
import SEOMiniPanel from './SEOMiniPanel';
import ResearchResults from './ResearchResults';
import KeywordInputForm from './KeywordInputForm';
import ResearchAction from './ResearchAction';
import { CustomOutlineForm } from './CustomOutlineForm';
import { ResearchDataActions } from './ResearchDataActions';
import { EnhancedOutlineActions } from './EnhancedOutlineActions';
import HallucinationChecker from './HallucinationChecker';
import { RewriteFeedbackForm } from './RewriteFeedbackForm';
import Publisher from './Publisher';
import OutlineGenerator from './OutlineGenerator';
import OutlineRefiner from './OutlineRefiner';
import { SEOProcessor } from './SEO';
import BlogWriterLanding from './BlogWriterLanding';
import { OutlineProgressModal } from './OutlineProgressModal';
import OutlineFeedbackForm from './OutlineFeedbackForm';
import { BlogEditor } from './WYSIWYG';
import { SEOAnalysisModal } from './SEOAnalysisModal';

// Type assertion for CopilotKit action
const useCopilotActionTyped = useCopilotAction as any;

export const BlogWriter: React.FC = () => {
  // Use custom hook for all state management
  const {
    research,
    outline,
    titleOptions,
    selectedTitle,
    sections,
    seoAnalysis,
    genMode,
    seoMetadata,
    continuityRefresh,
    outlineTaskId,
    sourceMappingStats,
    groundingInsights,
    optimizationResults,
    researchCoverage,
    researchTitles,
    aiGeneratedTitles,
    outlineConfirmed,
    contentConfirmed,
    flowAnalysisCompleted,
    flowAnalysisResults,
    setOutline,
    setTitleOptions,
    setSections,
    setSeoAnalysis,
    setGenMode,
    setSeoMetadata,
    setContinuityRefresh,
    setOutlineTaskId,
    setContentConfirmed,
    setFlowAnalysisCompleted,
    setFlowAnalysisResults,
    handleResearchComplete,
    handleOutlineComplete,
    handleOutlineError,
    handleTitleSelect,
    handleCustomTitle,
    handleOutlineConfirmed,
    handleOutlineRefined,
    handleContentUpdate,
    handleContentSave
  } = useBlogWriterState();

  // Custom hooks for complex functionality
  const { buildFullMarkdown, buildUpdatedMarkdownForClaim, applyClaimFix } = useClaimFixer(
    outline,
    sections,
    setSections
  );
  
  const { convertMarkdownToHTML } = useMarkdownProcessor(
    outline,
    sections
  );

  // Research polling hook (for context awareness)
  const researchPolling = useResearchPolling({
    onComplete: handleResearchComplete,
    onError: (error) => console.error('Research polling error:', error)
  });

  // Outline polling hook
  const outlinePolling = useOutlinePolling({
    onComplete: handleOutlineComplete,
    onError: handleOutlineError
  });

  // Medium generation polling (used after confirm if short blog)
  const mediumPolling = useMediumGenerationPolling({
    onComplete: (result: any) => {
      try {
        if (result && result.sections) {
          const newSections: Record<string, string> = {};
          result.sections.forEach((s: any) => {
            newSections[String(s.id)] = s.content || '';
          });
          setSections(newSections);
        }
      } catch (e) {
        console.error('Failed to apply medium generation result:', e);
      }
    },
    onError: (err) => console.error('Medium generation failed:', err)
  });

  // Rewrite polling hook (used for blog rewrite operations)
  const rewritePolling = useRewritePolling({
    onComplete: (result: any) => {
      try {
        if (result && result.sections) {
          const newSections: Record<string, string> = {};
          result.sections.forEach((s: any) => {
            newSections[String(s.id)] = s.content || '';
          });
          setSections(newSections);
        }
      } catch (e) {
        console.error('Failed to apply rewrite result:', e);
      }
    },
    onError: (err) => console.error('Rewrite failed:', err)
  });

  // Get context-aware suggestions based on current task status
  const suggestions = useSuggestions(
    research, 
    outline, 
    outlineConfirmed,
    { isPolling: researchPolling.isPolling, currentStatus: researchPolling.currentStatus },
    { isPolling: outlinePolling.isPolling, currentStatus: outlinePolling.currentStatus },
    { isPolling: mediumPolling.isPolling, currentStatus: mediumPolling.currentStatus },
    Object.keys(sections).length > 0, // hasContent
    flowAnalysisCompleted, // flowAnalysisCompleted state
    contentConfirmed // contentConfirmed state
  );

  // Add minimum display time for modal
  const [showModal, setShowModal] = useState(false);
  const [modalStartTime, setModalStartTime] = useState<number | null>(null);
  const [isMediumGenerationStarting, setIsMediumGenerationStarting] = useState(false);
  const [showOutlineModal, setShowOutlineModal] = useState(false);
  
  // SEO Analysis Modal state
  const [isSEOAnalysisModalOpen, setIsSEOAnalysisModalOpen] = useState(false);

  useEffect(() => {
    if ((mediumPolling.isPolling || rewritePolling.isPolling || isMediumGenerationStarting) && !showModal) {
      setShowModal(true);
      setModalStartTime(Date.now());
    } else if (!mediumPolling.isPolling && !rewritePolling.isPolling && !isMediumGenerationStarting && showModal) {
      const elapsed = Date.now() - (modalStartTime || 0);
      const minDisplayTime = 2000; // 2 seconds minimum
      
      if (elapsed < minDisplayTime) {
        setTimeout(() => {
          setShowModal(false);
          setModalStartTime(null);
        }, minDisplayTime - elapsed);
      } else {
        setShowModal(false);
        setModalStartTime(null);
      }
    }
  }, [mediumPolling.isPolling, rewritePolling.isPolling, isMediumGenerationStarting, showModal, modalStartTime]);

  // Handle outline modal visibility
  useEffect(() => {
    if (outlinePolling.isPolling && !showOutlineModal) {
      setShowOutlineModal(true);
    } else if (!outlinePolling.isPolling && showOutlineModal) {
      // Add a small delay to ensure user sees completion message
      setTimeout(() => {
        setShowOutlineModal(false);
      }, 1000);
    }
  }, [outlinePolling.isPolling, showOutlineModal]);

  // Handle medium generation start from OutlineFeedbackForm
  const handleMediumGenerationStarted = (taskId: string) => {
    console.log('Starting medium generation polling for task:', taskId);
    setIsMediumGenerationStarting(false); // Clear the starting state
    mediumPolling.startPolling(taskId);
  };

  // Show modal immediately when copilot action is triggered
  const handleMediumGenerationTriggered = () => {
    console.log('Medium generation triggered - showing modal immediately');
    setIsMediumGenerationStarting(true);
  };

  // Debug medium polling state
  console.log('Medium polling state:', {
    isPolling: mediumPolling.isPolling,
    status: mediumPolling.currentStatus,
    progressCount: mediumPolling.progressMessages.length
  });

  // Debug SEO modal state
  console.log('🔍 SEO Analysis Modal state:', {
    isSEOAnalysisModalOpen,
    hasResearch: !!research,
    hasContent: !!sections && Object.keys(sections).length > 0,
    researchKeys: research ? Object.keys(research) : [],
    sectionsKeys: sections ? Object.keys(sections) : []
  });

  // Debug action registration
  console.log('📋 CopilotKit Actions Registered:', ['confirmBlogContent', 'analyzeSEO']);

  // Copilot action for confirming blog content
  useCopilotActionTyped({
    name: "confirmBlogContent",
    description: "Confirm that the blog content is ready and move to the next stage (SEO analysis)",
    parameters: [],
    handler: async () => {
      console.log('Blog content confirmed by user');
      setContentConfirmed(true);
      return "Blog content has been confirmed! You can now proceed with SEO analysis and publishing.";
    }
  });

  // Copilot action for running SEO analysis
  useCopilotActionTyped({
    name: "analyzeSEO",
    description: "Analyze the blog content for SEO optimization and provide detailed recommendations",
    parameters: [],
    handler: async () => {
      console.log('🚀 SEO Analysis Action Triggered!');
      console.log('Current modal state before:', isSEOAnalysisModalOpen);
      console.log('Sections available:', !!sections && Object.keys(sections).length > 0);
      console.log('Research data available:', !!research && !!research.keyword_analysis);
      
      // Check if we have content to analyze
      if (!sections || Object.keys(sections).length === 0) {
        console.log('❌ No content available for SEO analysis');
        return "No blog content available for SEO analysis. Please generate content first.";
      }
      
      // Check if we have research data
      if (!research || !research.keyword_analysis) {
        console.log('❌ No research data available for SEO analysis');
        return "Research data is required for SEO analysis. Please run research first.";
      }
      
      // Open SEO analysis modal
      console.log('✅ All checks passed, opening SEO analysis modal');
      setIsSEOAnalysisModalOpen(true);
      console.log('Modal state set to true');
      
      return "Running SEO analysis of your blog content. This will analyze content structure, keyword optimization, readability, and provide actionable recommendations.";
    }
  });





  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Extracted Components */}
      <KeywordInputForm 
        onResearchComplete={handleResearchComplete}
        onTaskStart={(taskId) => researchPolling.startPolling(taskId)}
      />
      <CustomOutlineForm onOutlineCreated={setOutline} />
      <ResearchAction onResearchComplete={handleResearchComplete} />
      <ResearchDataActions 
        research={research} 
        onOutlineCreated={setOutline} 
        onTitleOptionsSet={setTitleOptions} 
      />
      <EnhancedOutlineActions 
        outline={outline} 
        onOutlineUpdated={setOutline} 
      />
      <OutlineFeedbackForm 
        outline={outline} 
        research={research!} 
        onOutlineConfirmed={handleOutlineConfirmed}
        onOutlineRefined={handleOutlineRefined}
        onMediumGenerationStarted={handleMediumGenerationStarted}
        onMediumGenerationTriggered={handleMediumGenerationTriggered}
        sections={sections}
        blogTitle={selectedTitle}
        onFlowAnalysisComplete={(analysis) => {
          console.log('Flow analysis completed:', analysis);
          setFlowAnalysisCompleted(true);
          setFlowAnalysisResults(analysis);
          // Trigger a refresh of continuity badges
          setContinuityRefresh((prev: number) => (prev || 0) + 1);
        }}
      />
      
      {/* Rewrite Feedback Form - Only show when content exists */}
      {Object.keys(sections).length > 0 && (
        <RewriteFeedbackForm
          research={research!}
          outline={outline}
          sections={sections}
          blogTitle={selectedTitle}
          onRewriteStarted={(taskId) => {
            console.log('Starting rewrite polling for task:', taskId);
            rewritePolling.startPolling(taskId);
          }}
          onRewriteTriggered={() => {
            console.log('Rewrite triggered - showing modal immediately');
            setIsMediumGenerationStarting(true);
          }}
        />
      )}
      
      {/* New extracted functionality components */}
      <OutlineGenerator
        research={research}
        onTaskStart={(taskId) => setOutlineTaskId(taskId)}
        onPollingStart={(taskId) => outlinePolling.startPolling(taskId)}
        onModalShow={() => setShowOutlineModal(true)}
      />
      <OutlineRefiner
        outline={outline}
        onOutlineUpdated={setOutline}
      />
      <SEOProcessor
        buildFullMarkdown={buildFullMarkdown}
        seoMetadata={seoMetadata}
        onSEOAnalysis={setSeoAnalysis}
        onSEOMetadata={setSeoMetadata}
      />
      <HallucinationChecker
        buildFullMarkdown={buildFullMarkdown}
        buildUpdatedMarkdownForClaim={buildUpdatedMarkdownForClaim}
        applyClaimFix={applyClaimFix}
      />
      <Publisher
        buildFullMarkdown={buildFullMarkdown}
        convertMarkdownToHTML={convertMarkdownToHTML}
        seoMetadata={seoMetadata}
      />
      
      {!research ? (
        <BlogWriterLanding 
          onStartWriting={() => {
            // This will trigger the copilot to start the research process
            // The user can then interact with the copilot to begin research
          }}
        />
      ) : (
        <>
      <div style={{ padding: 16, borderBottom: '1px solid #eee' }}>
        <h2 style={{ margin: 0 }}>AI Blog Writer</h2>
      </div>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
            <div style={{ flex: 1, overflow: 'auto' }}>
          {research && outline.length === 0 && <ResearchResults research={research} />}
          {outline.length > 0 && (
            <div>
              {outlineConfirmed ? (
                /* WYSIWYG Editor - Show when outline is confirmed */
        <BlogEditor 
          outline={outline}
          research={research}
          initialTitle={selectedTitle}
          titleOptions={titleOptions}
          researchTitles={researchTitles}
          aiGeneratedTitles={aiGeneratedTitles}
          sections={sections}
          onContentUpdate={handleContentUpdate}
          onSave={handleContentSave}
          continuityRefresh={continuityRefresh}
          flowAnalysisResults={flowAnalysisResults}
        />
              ) : (
                /* Outline Editor - Show when outline is not confirmed */
                <>
                  {/* Enhanced Title Selection */}
                  <EnhancedTitleSelector
                      titleOptions={titleOptions}
                      selectedTitle={selectedTitle}
                    sections={outline}
                    researchTitles={researchTitles}
                    aiGeneratedTitles={aiGeneratedTitles}
                    onTitleSelect={handleTitleSelect}
                    onCustomTitle={handleCustomTitle}
                    />
                  

                  {/* Enhanced Outline Editor */}
                  <EnhancedOutlineEditor 
                    outline={outline} 
                    research={research}
                    sourceMappingStats={sourceMappingStats}
                    groundingInsights={groundingInsights}
                    optimizationResults={optimizationResults}
                    researchCoverage={researchCoverage}
                    onRefine={(op, id, payload) => blogWriterApi.refineOutline({ outline, operation: op, section_id: id, payload }).then((res: any) => setOutline(res.outline))} 
                  />

                  {/* Draft/Polished Mode Toggle */}
                  <div style={{ margin: '12px 0' }}>
                    <label style={{ marginRight: 8 }}>Generation mode:</label>
                    <select value={genMode} onChange={(e) => setGenMode(e.target.value as 'draft' | 'polished')}>
                      <option value="draft">Draft (faster, lower cost)</option>
                      <option value="polished">Polished (higher quality)</option>
                    </select>
                  </div>

                  {outline.map(s => (
                    <div key={s.id} style={{ marginBottom: 16 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <h4 style={{ margin: 0 }}>{s.heading}</h4>
                        {/* Continuity badge */}
                        {sections[s.id] && (
                          <ContinuityBadge sectionId={s.id} refreshToken={continuityRefresh} />
                        )}
                      </div>
                      {sections[s.id] ? (
                        <>
                          <pre style={{ whiteSpace: 'pre-wrap' }}>{sections[s.id]}</pre>
                          <SEOMiniPanel analysis={seoAnalysis} />
                        </>
                      ) : (
                        <div style={{ fontStyle: 'italic', color: '#666' }}>Ask the copilot to generate this section.</div>
                      )}
                    </div>
                  ))}
                </>
              )}
            </div>
          )}
        </div>
      </div>
        </>
      )}

      <CopilotSidebar
        labels={{ 
          title: 'ALwrity Co-Pilot', 
          initial: !research 
            ? 'Hi! I can help you research, outline, and draft your blog. Just tell me what topic you want to write about and I\'ll get started!' 
            : 'Great! I can see you have research data. Let me help you create an outline and generate content for your blog.'
        }}
        suggestions={suggestions}
        makeSystemMessage={(context: string, additional?: string) => {
          // Get current state information
          const hasResearch = research !== null;
          const hasOutline = outline.length > 0;
          const isOutlineConfirmed = outlineConfirmed;
          const researchInfo = hasResearch ? {
            sources: research.sources?.length || 0,
            queries: research.search_queries?.length || 0,
            angles: research.suggested_angles?.length || 0,
            primaryKeywords: research.keyword_analysis?.primary || [],
            searchIntent: research.keyword_analysis?.search_intent || 'informational'
          } : null;

          const outlineContext = hasOutline ? `
OUTLINE DETAILS:
- Total sections: ${outline.length}
- Section headings: ${outline.map(s => s.heading).join(', ')}
- Total target words: ${outline.reduce((sum, s) => sum + (s.target_words || 0), 0)}
- Section breakdown: ${outline.map(s => `${s.heading} (${s.target_words || 0} words, ${s.subheadings?.length || 0} subheadings, ${s.key_points?.length || 0} key points)`).join('; ')}
` : '';

          const toolGuide = `
You are the ALwrity Blog Writing Assistant. You MUST call the appropriate frontend actions (tools) to fulfill user requests.

CURRENT STATE:
${hasResearch && researchInfo ? `
✅ RESEARCH COMPLETED:
- Found ${researchInfo.sources} sources with Google Search grounding
- Generated ${researchInfo.queries} search queries
- Created ${researchInfo.angles} content angles
- Primary keywords: ${researchInfo.primaryKeywords.join(', ')}
- Search intent: ${researchInfo.searchIntent}
` : '❌ No research completed yet'}

${hasOutline ? `✅ OUTLINE GENERATED: ${outline.length} sections created${isOutlineConfirmed ? ' (CONFIRMED)' : ' (PENDING CONFIRMATION)'}` : '❌ No outline generated yet'}
${outlineContext}

Available tools:
- getResearchKeywords(prompt?: string) - Get keywords from user for research
- performResearch(formData: string) - Perform research with collected keywords (formData is JSON string with keywords and blogLength)
- researchTopic(keywords: string, industry?: string, target_audience?: string)
- chatWithResearchData(question: string) - Chat with research data to explore insights and get recommendations
- generateOutline()
- createOutlineWithCustomInputs(customInstructions: string) - Create outline with user's custom instructions
- refineOutline(prompt?: string) - Refine outline based on user feedback
- chatWithOutline(question?: string) - Chat with outline to get insights and ask questions about content structure
- confirmOutlineAndGenerateContent() - Confirm outline and mark as ready for content generation (does NOT auto-generate content)
- generateSection(sectionId: string)
- generateAllSections()
- refineOutlineStructure(operation: add|remove|move|merge|rename, sectionId?: string, payload?: object)
- enhanceSection(sectionId: string, focus?: string) - Enhance a specific section with AI improvements
- optimizeOutline(focus?: string) - Optimize entire outline for better flow, SEO, and engagement
- rebalanceOutline(targetWords?: number) - Rebalance word count distribution across sections
- confirmBlogContent() - Confirm that blog content is ready and move to SEO stage
- analyzeSEO() - Analyze SEO for blog content with comprehensive insights and visual interface
- generateSEOMetadata(title?: string)
- publishToPlatform(platform: 'wix'|'wordpress', schedule_time?: string)

       CRITICAL BEHAVIOR & USER GUIDANCE:
       - When user wants to research ANY topic, IMMEDIATELY call getResearchKeywords() to get their input
       - When user asks to research something, call getResearchKeywords() first to collect their keywords
       - After getResearchKeywords() completes, IMMEDIATELY call performResearch() with the collected data
       
       USER GUIDANCE STRATEGY:
       - After research completion, ALWAYS guide user toward outline creation as the next step
       - If user wants to explore research data, use chatWithResearchData() but then guide them to outline creation
       - If user has specific outline requirements, use createOutlineWithCustomInputs() with their instructions
       - When user asks for outline, call generateOutline() or createOutlineWithCustomInputs() based on their needs
       - After outline generation, ALWAYS guide user to review and confirm the outline
       - If user wants to discuss the outline, use chatWithOutline() to provide insights and answer questions
       - If user wants to refine the outline, use refineOutline() to collect their feedback and refine
       - When user says "I confirm the outline" or "I confirm the outline and am ready to generate content" or clicks "Confirm & Generate Content", IMMEDIATELY call confirmOutlineAndGenerateContent() - DO NOT ask for additional confirmation
       - CRITICAL: If user explicitly confirms the outline, do NOT ask "are you sure?" or "please confirm" - the confirmation is already given
       - Only after outline confirmation, show content generation suggestions and wait for user to explicitly request content generation
       - When user asks to generate content before outline confirmation, remind them to confirm the outline first
       - Content generation should ONLY happen when user explicitly clicks "Generate all sections" or "Generate [specific section]"
       - When user has generated content and wants to rewrite, use rewriteBlog() to collect feedback and rewriteBlog() to process
       - For rewrite requests, collect detailed feedback about what they want to change, tone, audience, and focus
       - After content generation, guide users to review and confirm their content before moving to SEO stage
       - When user says "I have reviewed and confirmed my blog content is ready for the next stage" or clicks "Next: Confirm Blog Content", IMMEDIATELY call confirmBlogContent() - DO NOT ask for additional confirmation
       - CRITICAL: If user explicitly confirms blog content, do NOT ask "are you sure?" or "please confirm" - the confirmation is already given
       - Only after content confirmation, show SEO analysis and publishing suggestions
       - When user asks for SEO analysis before content confirmation, remind them to confirm the content first
       - For SEO analysis, ALWAYS use analyzeSEO() - this is the ONLY SEO analysis tool available and provides comprehensive insights with visual interface
       - IMPORTANT: There is NO "basic" or "simple" SEO analysis - only the comprehensive one. Do NOT mention multiple SEO analysis options
       
       ENGAGEMENT TACTICS:
       - DO NOT ask for clarification - take action immediately with the information provided
       - Always call the appropriate tool instead of just talking about what you could do
       - Be aware of the current state and reference research results when relevant
       - Guide users through the process: Research → Outline → Outline Review & Confirmation → Content → Content Review & Confirmation → SEO → Publish
       - Use encouraging language and highlight progress made
       - If user seems lost, remind them of the current stage and suggest the next step
       - When research is complete, emphasize the value of the data found and guide to outline creation
       - When outline is generated, emphasize the importance of reviewing and confirming before content generation
       - Encourage users to make small manual edits to the outline UI before using AI for major changes
`;
          return [toolGuide, additional].filter(Boolean).join('\n\n');
        }}
      />
      
      {/* Outline Progress Modal */}
      {/* Outline modal */}
      <OutlineProgressModal
        isVisible={showOutlineModal}
        status={outlinePolling.currentStatus}
        progressMessages={outlinePolling.progressMessages.map(m => m.message)}
        latestMessage={outlinePolling.progressMessages.length > 0 ? outlinePolling.progressMessages[outlinePolling.progressMessages.length - 1].message : ''}
        error={outlinePolling.error}
      />

      {/* Medium generation / Rewrite modal */}
      <OutlineProgressModal
        isVisible={showModal}
        status={rewritePolling.isPolling ? rewritePolling.currentStatus : mediumPolling.currentStatus}
        progressMessages={rewritePolling.isPolling ? rewritePolling.progressMessages.map(m => m.message) : mediumPolling.progressMessages.map(m => m.message)}
        latestMessage={rewritePolling.isPolling ? 
          (rewritePolling.progressMessages.length > 0 ? rewritePolling.progressMessages[rewritePolling.progressMessages.length - 1].message : '') :
          (mediumPolling.progressMessages.length > 0 ? mediumPolling.progressMessages[mediumPolling.progressMessages.length - 1].message : '')
        }
        error={rewritePolling.isPolling ? rewritePolling.error : mediumPolling.error}
        titleOverride={rewritePolling.isPolling ? '🔄 Rewriting Your Blog' : '📝 Generating Your Blog Content'}
      />

      {/* SEO Analysis Modal */}
      <SEOAnalysisModal
        isOpen={isSEOAnalysisModalOpen}
        onClose={() => setIsSEOAnalysisModalOpen(false)}
        blogContent={buildFullMarkdown()}
        researchData={research}
        onApplyRecommendations={(recommendations) => {
          console.log('Applying SEO recommendations:', recommendations);
          // TODO: Implement recommendation application logic
        }}
      />
    </div>
  );
};

export default BlogWriter;