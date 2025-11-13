import React from 'react';
import ResearchResults from '../ResearchResults';
import EnhancedTitleSelector from '../EnhancedTitleSelector';
import EnhancedOutlineEditor from '../EnhancedOutlineEditor';
import { BlogEditor } from '../WYSIWYG';
import OutlineCtaBanner from './OutlineCtaBanner';
import ManualResearchForm from '../ManualResearchForm';
import ManualOutlineButton from '../ManualOutlineButton';
import ManualContentButton from '../ManualContentButton';

interface PhaseContentProps {
  currentPhase: string;
  research: any;
  outline: any[];
  outlineConfirmed: boolean;
  titleOptions: any[];
  selectedTitle?: string | null;
  researchTitles: any[];
  aiGeneratedTitles: any[];
  sourceMappingStats: any;
  groundingInsights: any;
  optimizationResults: any;
  researchCoverage: any;
  setOutline: (o: any) => void;
  sections: Record<string, string>;
  handleContentUpdate: any;
  handleContentSave: any;
  continuityRefresh: number | null;
  flowAnalysisResults: any;
  outlineGenRef: React.RefObject<any>;
  blogWriterApi: any;
  contentConfirmed: boolean;
  seoAnalysis: any;
  seoMetadata: any;
  onTitleSelect: any;
  onCustomTitle: any;
  sectionImages?: Record<string, string>;
  setSectionImages?: (images: Record<string, string> | ((prev: Record<string, string>) => Record<string, string>)) => void;
  copilotKitAvailable?: boolean; // Whether CopilotKit is available
  onResearchComplete?: (research: any) => void; // Callback when research completes (for manual form)
  onOutlineGenerationStart?: (taskId: string) => void; // Callback when outline generation starts
  onContentGenerationStart?: (taskId: string) => void; // Callback when content generation starts
}

export const PhaseContent: React.FC<PhaseContentProps> = ({
  currentPhase,
  research,
  outline,
  outlineConfirmed,
  titleOptions,
  selectedTitle,
  researchTitles,
  aiGeneratedTitles,
  sourceMappingStats,
  groundingInsights,
  optimizationResults,
  researchCoverage,
  setOutline,
  sections,
  handleContentUpdate,
  handleContentSave,
  continuityRefresh,
  flowAnalysisResults,
  outlineGenRef,
  blogWriterApi,
  contentConfirmed,
  seoAnalysis,
  seoMetadata,
  onTitleSelect,
  onCustomTitle,
  sectionImages,
  setSectionImages,
  copilotKitAvailable = true,
  onResearchComplete,
  onOutlineGenerationStart,
  onContentGenerationStart,
}) => {
  return (
    <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
      <div style={{ flex: 1, overflow: 'auto' }}>
        {currentPhase === 'research' && (
          <>
            {research ? (
              <ResearchResults research={research} />
            ) : (
              <>
                {copilotKitAvailable ? (
                  <div style={{ padding: '20px', textAlign: 'center' }}>
                    <h3>Start Your Research</h3>
                    <p>Use the copilot to begin researching your blog topic.</p>
                  </div>
                ) : (
                  <ManualResearchForm onResearchComplete={onResearchComplete} />
                )}
              </>
            )}
          </>
        )}

        {currentPhase === 'outline' && research && (
          <>
            {outline.length === 0 && (
              <>
                {copilotKitAvailable ? (
                  <OutlineCtaBanner onGenerate={() => outlineGenRef.current?.generateNow()} />
                ) : (
                  <ManualOutlineButton
                    outlineGenRef={outlineGenRef}
                    hasResearch={!!research}
                    onGenerationStart={onOutlineGenerationStart}
                  />
                )}
              </>
            )}
            {outline.length > 0 ? (
              <>
                <EnhancedTitleSelector
                  titleOptions={titleOptions}
                  selectedTitle={selectedTitle || undefined}
                  sections={outline}
                  researchTitles={researchTitles}
                  aiGeneratedTitles={aiGeneratedTitles}
                  onTitleSelect={onTitleSelect}
                  onCustomTitle={onCustomTitle}
                  research={research}
                />
                <EnhancedOutlineEditor 
                  outline={outline} 
                  research={research}
                  sourceMappingStats={sourceMappingStats}
                  groundingInsights={groundingInsights}
                  optimizationResults={optimizationResults}
                  researchCoverage={researchCoverage}
                  onRefine={(op: any, id: any, payload: any) => blogWriterApi.refineOutline({ outline, operation: op, section_id: id, payload }).then((res: any) => setOutline(res.outline))}
                  sectionImages={sectionImages}
                  setSectionImages={setSectionImages}
                />
              </>
            ) : !copilotKitAvailable ? (
              <ManualOutlineButton
                outlineGenRef={outlineGenRef}
                hasResearch={!!research}
                onGenerationStart={onOutlineGenerationStart}
              />
            ) : (
              <div style={{ padding: '20px', textAlign: 'center' }}>
                <h3>Create Your Outline</h3>
                <p>Use the copilot to generate an outline based on your research.</p>
              </div>
            )}
          </>
        )}

        {currentPhase === 'content' && outline.length > 0 && (
          <>
            {outlineConfirmed ? (
              <BlogEditor
                outline={outline}
                research={research}
                initialTitle={selectedTitle || (typeof window !== 'undefined' ? localStorage.getItem('blog_selected_title') : '') || 'Your Amazing Blog Title'}
                titleOptions={titleOptions}
                researchTitles={researchTitles}
                aiGeneratedTitles={aiGeneratedTitles}
                sections={sections}
                onContentUpdate={handleContentUpdate}
                onSave={handleContentSave}
                continuityRefresh={continuityRefresh || undefined}
                flowAnalysisResults={flowAnalysisResults}
                sectionImages={sectionImages}
              />
            ) : (
              <>
                {copilotKitAvailable ? (
                  <div style={{ padding: '20px', textAlign: 'center' }}>
                    <h3>Confirm Your Outline</h3>
                    <p>Review and confirm your outline before generating content.</p>
                  </div>
                ) : (
                  <ManualContentButton
                    outline={outline}
                    research={research}
                    blogTitle={selectedTitle || undefined}
                    sections={sections}
                    onGenerationStart={onContentGenerationStart}
                  />
                )}
              </>
            )}
          </>
        )}

        {currentPhase === 'seo' && contentConfirmed && outline.length > 0 && outlineConfirmed && (
          <>
            {Object.keys(sections).length > 0 && Object.values(sections).some(content => content && content.trim().length > 0) ? (
              <BlogEditor
                outline={outline}
                research={research}
                initialTitle={selectedTitle || (typeof window !== 'undefined' ? localStorage.getItem('blog_selected_title') : '') || 'Your Amazing Blog Title'}
                titleOptions={titleOptions}
                researchTitles={researchTitles}
                aiGeneratedTitles={aiGeneratedTitles}
                sections={sections}
                onContentUpdate={handleContentUpdate}
                onSave={handleContentSave}
                continuityRefresh={continuityRefresh || undefined}
                flowAnalysisResults={flowAnalysisResults}
                sectionImages={sectionImages}
              />
            ) : (
              <div style={{ padding: '20px', textAlign: 'center' }}>
                <h3>Loading Content...</h3>
                <p>Please wait while your content is being optimized.</p>
              </div>
            )}
          </>
        )}

        {/* Fallback for SEO phase if conditions not met */}
        {currentPhase === 'seo' && (!contentConfirmed || outline.length === 0 || !outlineConfirmed) && (
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <h3>Optimize your blog for search engines.</h3>
            <p>Complete the content phase first to enable SEO optimization.</p>
          </div>
        )}

        {currentPhase === 'publish' && seoAnalysis && seoMetadata && (
          <div style={{ padding: '20px' }}>
            <h3>Publish Your Blog</h3>
            <p>Your blog is ready to publish!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PhaseContent;


