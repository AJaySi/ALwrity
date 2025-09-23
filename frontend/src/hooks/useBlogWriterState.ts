import { useState, useEffect, useCallback } from 'react';
import { BlogOutlineSection, BlogResearchResponse, BlogSEOMetadataResponse, BlogSEOAnalyzeResponse, SourceMappingStats, GroundingInsights, OptimizationResults, ResearchCoverage } from '../services/blogWriterApi';
import { researchCache } from '../services/researchCache';

export const useBlogWriterState = () => {
  // Core state
  const [research, setResearch] = useState<BlogResearchResponse | null>(null);
  const [outline, setOutline] = useState<BlogOutlineSection[]>([]);
  const [titleOptions, setTitleOptions] = useState<string[]>([]);
  const [selectedTitle, setSelectedTitle] = useState<string>('');
  const [sections, setSections] = useState<Record<string, string>>({});
  const [seoAnalysis, setSeoAnalysis] = useState<BlogSEOAnalyzeResponse | null>(null);
  const [genMode, setGenMode] = useState<'draft' | 'polished'>('polished');
  const [seoMetadata, setSeoMetadata] = useState<BlogSEOMetadataResponse | null>(null);
  const [continuityRefresh, setContinuityRefresh] = useState<number>(0);
  const [outlineTaskId, setOutlineTaskId] = useState<string | null>(null);
  const [flowAnalysisCompleted, setFlowAnalysisCompleted] = useState<boolean>(false);
  const [flowAnalysisResults, setFlowAnalysisResults] = useState<any>(null);
  
  // Enhanced metadata state
  const [sourceMappingStats, setSourceMappingStats] = useState<SourceMappingStats | null>(null);
  const [groundingInsights, setGroundingInsights] = useState<GroundingInsights | null>(null);
  const [optimizationResults, setOptimizationResults] = useState<OptimizationResults | null>(null);
  const [researchCoverage, setResearchCoverage] = useState<ResearchCoverage | null>(null);
  
  // Separate research titles from AI-generated titles
  const [researchTitles, setResearchTitles] = useState<string[]>([]);
  const [aiGeneratedTitles, setAiGeneratedTitles] = useState<string[]>([]);
  
  // Outline confirmation state
  const [outlineConfirmed, setOutlineConfirmed] = useState<boolean>(false);
  
  // Content confirmation state
  const [contentConfirmed, setContentConfirmed] = useState<boolean>(false);

  // Cache recovery - restore most recent research on page load
  useEffect(() => {
    const cachedEntries = researchCache.getAllCachedEntries();
    if (cachedEntries.length > 0) {
      // Get the most recent cached research
      const mostRecent = cachedEntries[0];
      console.log('Restoring cached research from page load:', mostRecent.keywords);
      setResearch(mostRecent.result);
      
      // Also try to restore outline if it exists in localStorage
      try {
        const savedOutline = localStorage.getItem('blog_outline');
        const savedTitleOptions = localStorage.getItem('blog_title_options');
        const savedSelectedTitle = localStorage.getItem('blog_selected_title');
        
        if (savedOutline) {
          setOutline(JSON.parse(savedOutline));
        }
        if (savedTitleOptions) {
          setTitleOptions(JSON.parse(savedTitleOptions));
        }
        if (savedSelectedTitle) {
          setSelectedTitle(savedSelectedTitle);
        }
        
        console.log('Restored outline and title data from localStorage');
      } catch (error) {
        console.error('Error restoring outline data:', error);
      }
    }
  }, []);

  // Handle research completion
  const handleResearchComplete = useCallback((researchData: BlogResearchResponse) => {
    setResearch(researchData);
  }, []);

  // Handle outline completion with enhanced metadata
  const handleOutlineComplete = useCallback((result: any) => {
    if (result?.outline) {
      setOutline(result.outline);
      setTitleOptions(result.title_options || []);
      
      // Store enhanced metadata
      if (result.source_mapping_stats) {
        setSourceMappingStats(result.source_mapping_stats);
      }
      if (result.grounding_insights) {
        setGroundingInsights(result.grounding_insights);
      }
      if (result.optimization_results) {
        setOptimizationResults(result.optimization_results);
      }
      if (result.research_coverage) {
        setResearchCoverage(result.research_coverage);
      }
      
      // Separate research titles from AI-generated titles
      if (result.title_options && research) {
        const researchAngles = research.suggested_angles || [];
        const researchTitlesList = result.title_options.filter((title: string) => 
          researchAngles.some((angle: string) => title.toLowerCase().includes(angle.toLowerCase().substring(0, 20)))
        );
        const aiTitlesList = result.title_options.filter((title: string) => 
          !researchTitlesList.includes(title)
        );
        
        setResearchTitles(researchTitlesList);
        setAiGeneratedTitles(aiTitlesList);
        
        // Auto-select first AI-generated title if available, otherwise first research title
        if (aiTitlesList.length > 0) {
          setSelectedTitle(aiTitlesList[0]);
        } else if (researchTitlesList.length > 0) {
          setSelectedTitle(researchTitlesList[0]);
        } else if (result.title_options.length > 0) {
          setSelectedTitle(result.title_options[0]);
        }
      }
      
      // Save to localStorage for persistence
      try {
        localStorage.setItem('blog_outline', JSON.stringify(result.outline));
        localStorage.setItem('blog_title_options', JSON.stringify(result.title_options || []));
        localStorage.setItem('blog_selected_title', result.title_options?.[0] || '');
        console.log('Saved outline data to localStorage');
      } catch (error) {
        console.error('Error saving outline data:', error);
      }
    }
    setOutlineTaskId(null);
    // Reset outline confirmation when new outline is generated
    setOutlineConfirmed(false);
  }, [research]);

  // Handle outline error
  const handleOutlineError = useCallback((error: any) => {
    console.error('Outline generation error:', error);
    setOutlineTaskId(null);
  }, []);

  // Handle section generation
  const handleSectionGenerated = useCallback((sectionId: string, markdown: string) => {
    setSections(prev => ({ ...prev, [sectionId]: markdown }));
  }, []);

  // Handle continuity refresh
  const handleContinuityRefresh = useCallback(() => {
    setContinuityRefresh(Date.now());
  }, []);

  // Handle title selection
  const handleTitleSelect = useCallback((title: string) => {
    setSelectedTitle(title);
    localStorage.setItem('blog_selected_title', title);
  }, []);

  // Handle custom title
  const handleCustomTitle = useCallback((title: string) => {
    const newTitleOptions = [...titleOptions, title];
    setTitleOptions(newTitleOptions);
    setSelectedTitle(title);
    localStorage.setItem('blog_title_options', JSON.stringify(newTitleOptions));
    localStorage.setItem('blog_selected_title', title);
  }, [titleOptions]);

  // Handle outline confirmation
  const handleOutlineConfirmed = useCallback(() => {
    setOutlineConfirmed(true);
    console.log('Outline confirmed by user');
  }, []);

  // Handle outline refinement
  const handleOutlineRefined = useCallback((feedback: string) => {
    console.log('Outline refinement requested with feedback:', feedback);
    // The actual refinement will be handled by the copilot action
  }, []);

  // Handle content updates from WYSIWYG editor
  const handleContentUpdate = useCallback((updatedSections: any[]) => {
    console.log('Content updated:', updatedSections);
    // Update sections state with new content
    const newSections: { [key: string]: string } = {};
    updatedSections.forEach(section => {
      newSections[section.id] = section.content;
    });
    setSections(newSections);
  }, [setSections]);

  // Handle content saving
  const handleContentSave = useCallback((content: any) => {
    console.log('Content saved:', content);
    // Here you could save to backend or local storage
    // For now, just log the content
  }, []);

  return {
    // State
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
    
    // Setters
    setResearch,
    setOutline,
    setTitleOptions,
    setSelectedTitle,
    setSections,
    setSeoAnalysis,
    setGenMode,
    setSeoMetadata,
    setContinuityRefresh,
    setOutlineTaskId,
    setSourceMappingStats,
    setGroundingInsights,
    setOptimizationResults,
    setResearchCoverage,
    setResearchTitles,
    setAiGeneratedTitles,
    setOutlineConfirmed,
    setContentConfirmed,
    setFlowAnalysisCompleted,
    setFlowAnalysisResults,
    
    // Handlers
    handleResearchComplete,
    handleOutlineComplete,
    handleOutlineError,
    handleSectionGenerated,
    handleContinuityRefresh,
    handleTitleSelect,
    handleCustomTitle,
    handleOutlineConfirmed,
    handleOutlineRefined,
    handleContentUpdate,
    handleContentSave
  };
};
