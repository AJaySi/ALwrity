import { useState, useEffect, useCallback } from 'react';
import { BlogOutlineSection, BlogResearchResponse, BlogSEOMetadataResponse, BlogSEOAnalyzeResponse, SourceMappingStats, GroundingInsights, OptimizationResults, ResearchCoverage } from '../services/blogWriterApi';
import { researchCache } from '../services/researchCache';
import { blogWriterCache } from '../services/blogWriterCache';

const MINOR_TITLE_WORDS = new Set([
  'a', 'an', 'and', 'or', 'but', 'the', 'for', 'nor', 'on', 'at', 'to', 'from', 'by',
  'of', 'in', 'with', 'as', 'vs', 'vs.', 'into', 'over', 'under'
]);

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

  // Section images state - persists images generated in outline phase to content phase
  const [sectionImages, setSectionImages] = useState<Record<string, string>>({});

  const formatContentAngleToTitle = useCallback((angle: string): string => {
    if (!angle || typeof angle !== 'string') {
      return '';
    }
    const cleaned = angle.replace(/\s+/g, ' ').trim();
    if (!cleaned) {
      return '';
    }

    const words = cleaned.split(' ');
    const formattedWords = words.map((word, index) => {
      const lower = word.toLowerCase();
      if (index !== 0 && MINOR_TITLE_WORDS.has(lower)) {
        return lower;
      }
      if (!lower) {
        return '';
      }
      return lower.charAt(0).toUpperCase() + lower.slice(1);
    }).filter(Boolean);

    let formatted = formattedWords.join(' ');
    if (formatted.length > 120) {
      formatted = formatted.slice(0, 117).trimEnd() + '...';
    }
    return formatted;
  }, []);

  const dedupeTitles = useCallback((titles: string[]): string[] => {
    const seen = new Set<string>();
    const result: string[] = [];

    titles.forEach((title) => {
      if (!title) {
        return;
      }
      const normalized = title.replace(/\s+/g, ' ').trim();
      if (!normalized) {
        return;
      }
      const key = normalized.toLowerCase();
      if (seen.has(key)) {
        return;
      }
      seen.add(key);
      result.push(normalized);
    });

    return result;
  }, []);

  const [restoreAttempted, setRestoreAttempted] = useState(false);

  // Cache recovery - restore most recent research on page load
  useEffect(() => {
    const restoreState = async () => {
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
            const parsedOutline = JSON.parse(savedOutline);
            setOutline(parsedOutline);
            
            // Restore content sections from cache when outline is available
            const outlineIds = parsedOutline.map((s: any) => String(s.id));
            const cachedContent = blogWriterCache.getCachedContent(outlineIds);
            if (cachedContent && Object.keys(cachedContent).length > 0) {
              setSections(cachedContent);
              console.log('Restored content sections from cache', { sections: Object.keys(cachedContent).length });
            }
          }
          if (savedTitleOptions) {
            setTitleOptions(JSON.parse(savedTitleOptions));
          }
          if (savedSelectedTitle) {
            setSelectedTitle(savedSelectedTitle);
          }
          
          // Restore contentConfirmed from localStorage
          const savedContentConfirmed = localStorage.getItem('blog_content_confirmed');
          if (savedContentConfirmed === 'true') {
            setContentConfirmed(true);
          }
          
          console.log('Restored outline, content, and title data from localStorage');
          // Restore seoAnalysis and seoMetadata from localStorage
        const savedSeoAnalysis = localStorage.getItem('blog_seo_analysis');
        if (savedSeoAnalysis) {
          try { setSeoAnalysis(JSON.parse(savedSeoAnalysis)); } catch {}
        }
        const savedSeoMetadata = localStorage.getItem('blog_seo_metadata');
        if (savedSeoMetadata) {
          try { setSeoMetadata(JSON.parse(savedSeoMetadata)); } catch {}
        }

        // Restore outlineConfirmed - if outline exists and was previously confirmed, mark as confirmed.
        // The user had to confirm outline to reach content/SEO/publish phases.
        const savedOutlineConfirmed = localStorage.getItem('blog_outline_confirmed');
        if (savedOutlineConfirmed === 'true') {
          setOutlineConfirmed(true);
        } else if (savedOutline) {
          // Backward compatibility: if outline exists but outline_confirmed wasn't saved,
          // assume it was confirmed (user wouldn't have progressed without confirming).
          setOutlineConfirmed(true);
        }
      } catch (error) {
          console.error('Error restoring outline data:', error);
        }
      }
      setRestoreAttempted(true);
    };

    restoreState();
  }, []);

  // Persist contentConfirmed to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('blog_content_confirmed', String(contentConfirmed));
    } catch {}
  }, [contentConfirmed]);

  // Persist outlineConfirmed to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('blog_outline_confirmed', String(outlineConfirmed));
    } catch {}
  }, [outlineConfirmed]);

  // Persist seoAnalysis to localStorage whenever it changes
  useEffect(() => {
    try {
      if (seoAnalysis) {
        localStorage.setItem('blog_seo_analysis', JSON.stringify(seoAnalysis));
      }
    } catch {}
  }, [seoAnalysis]);

  // Persist seoMetadata to localStorage whenever it changes
  useEffect(() => {
    try {
      if (seoMetadata) {
        localStorage.setItem('blog_seo_metadata', JSON.stringify(seoMetadata));
      }
    } catch {}
  }, [seoMetadata]);

  // Persist sections to blogWriterCache whenever they change
  useEffect(() => {
    const outlineIds = outline.map(s => String(s.id));
    if (outlineIds.length > 0 && Object.keys(sections).length > 0) {
      const normalized: Record<string, string> = {};
      const values = Object.values(sections);
      outline.forEach((s, idx) => {
        const id = String(s.id);
        normalized[id] = sections[id] ?? values[idx] ?? '';
      });
      blogWriterCache.cacheContent(normalized, outlineIds);
    }
  }, [sections, outline]);

  // Handle research completion
  const handleResearchComplete = useCallback((researchData: BlogResearchResponse) => {
    setResearch(researchData);
    const formattedAngles = dedupeTitles(
      (researchData?.suggested_angles || []).map(formatContentAngleToTitle)
    );
    setResearchTitles(formattedAngles);
    
    // Prefill title from research if no title is currently selected
    if (!selectedTitle && formattedAngles.length > 0) {
      const firstTitle = formattedAngles[0];
      setSelectedTitle(firstTitle);
      localStorage.setItem('blog_selected_title', firstTitle);
    }
  }, [dedupeTitles, formatContentAngleToTitle, selectedTitle]);

  // Handle outline completion with enhanced metadata
  const handleOutlineComplete = useCallback((result: any) => {
    if (result?.outline) {
      setOutline(result.outline);

      const aiTitleOptions: string[] = result.title_options || [];
      const formattedAngles = dedupeTitles(
        (research?.suggested_angles || []).map(formatContentAngleToTitle)
      );
      const combinedTitleOptions = dedupeTitles([
        ...formattedAngles,
        ...aiTitleOptions
      ]);

      setTitleOptions(combinedTitleOptions);
      setResearchTitles(formattedAngles);

      const aiTitlesList = dedupeTitles(
        aiTitleOptions.filter((title: string) => !formattedAngles.some(angle => angle.toLowerCase() === (title || '').toLowerCase().trim()))
      );
      setAiGeneratedTitles(aiTitlesList);

      const nextSelectedTitle = aiTitlesList[0] || formattedAngles[0] || combinedTitleOptions[0] || '';
      if (nextSelectedTitle) {
        setSelectedTitle(nextSelectedTitle);
      }

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

      // Save to localStorage for persistence (using shared cache utility)
      try {
        const { blogWriterCache } = require('../services/blogWriterCache');
        blogWriterCache.cacheOutline(result.outline, combinedTitleOptions);
        localStorage.setItem('blog_title_options', JSON.stringify(combinedTitleOptions));
        localStorage.setItem('blog_selected_title', nextSelectedTitle || '');
        console.log('Saved outline data to localStorage');
      } catch (error) {
        console.error('Error saving outline data:', error);
      }
    }
    setOutlineTaskId(null);
    // Reset outline confirmation when new outline is generated
    setOutlineConfirmed(false);
  }, [research, dedupeTitles, formatContentAngleToTitle]);

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
    sectionImages,
    restoreAttempted,
    
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
    setSectionImages,
    
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
