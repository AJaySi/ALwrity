import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { createTheme, ThemeProvider, Paper, IconButton, Tooltip, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box, Divider, TextField } from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  MoreHoriz as MoreHorizIcon,
} from '@mui/icons-material';
import { BlogOutlineSection, BlogResearchResponse, blogWriterApi } from '../../../services/blogWriterApi';
import BlogSection from './BlogSection';
import EditorSidebar from './EditorSidebar';
import HoverMenu from './HoverMenu';

const theme = createTheme({
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  palette: {
    primary: { main: '#4f46e5' },
  },
});

interface BlogEditorProps {
  outline: BlogOutlineSection[];
  research: BlogResearchResponse | null;
  initialTitle?: string;
  titleOptions?: string[];
  researchTitles?: string[];
  aiGeneratedTitles?: string[];
  sections?: Record<string, string>;
  onContentUpdate?: (sections: any[]) => void;
  onSave?: (content: any) => void;
  continuityRefresh?: number;
  flowAnalysisResults?: any;
  sectionImages?: Record<string, string>;
}

const BlogEditor: React.FC<BlogEditorProps> = ({ 
  outline, 
  research, 
  initialTitle,
  titleOptions = [],
  researchTitles = [],
  aiGeneratedTitles = [],
  sections: parentSections,
  onContentUpdate, 
  onSave,
  continuityRefresh,
  flowAnalysisResults,
  sectionImages = {}
}) => {
  const [blogTitle, setBlogTitle] = useState(initialTitle || 'Your Amazing Blog Title');
  const [introduction, setIntroduction] = useState('');
  const [sections, setSections] = useState<any[]>([]);
  const [isIntroductionLoading, setIsIntroductionLoading] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<any>>(new Set());
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [showIntroductionModal, setShowIntroductionModal] = useState(false);
  const [generatedIntroductions, setGeneratedIntroductions] = useState<string[]>([]);
  const [editingTitle, setEditingTitle] = useState(false);
  const [editingIntro, setEditingIntro] = useState(false);
  const [titleMenuAnchor, setTitleMenuAnchor] = useState<HTMLElement | null>(null);
  const titleInputRef = useRef<HTMLInputElement>(null);
  const introInputRef = useRef<HTMLInputElement>(null);

  const totalWords = useMemo(() =>
    sections.reduce((sum, s) => sum + (s.content?.split(/\s+/).filter(Boolean).length || 0), 0),
    [sections]
  );

  const readingTime = useMemo(() => Math.max(1, Math.ceil(totalWords / 200)), [totalWords]);

  useEffect(() => {
    if (outline && outline.length > 0) {
      const initialSections = outline.map((section, index) => ({
        id: section.id || index + 1,
        title: section.heading,
        content: parentSections?.[section.id] || section.key_points?.join(' ') || '',
        wordCount: section.target_words || 0,
        sources: section.references?.length || 0,
        outlineData: {
          subheadings: section.subheadings || [],
          keyPoints: section.key_points || [],
          keywords: section.keywords || [],
          references: section.references || [],
          targetWords: section.target_words || 0
        }
      }));
      setSections(initialSections);
    }
  }, [outline, parentSections]);

  const prevParentSectionsRef = useRef<string>('');
  const prevContinuityRefreshRef = useRef<number | undefined>(undefined);
  
  useEffect(() => {
    if (!parentSections || !outline || outline.length === 0) return;

    const parentSectionsString = JSON.stringify(parentSections);
    const continuityRefreshChanged = continuityRefresh !== prevContinuityRefreshRef.current;
    
    if (parentSectionsString === prevParentSectionsRef.current && !continuityRefreshChanged) {
      return;
    }
    
    prevParentSectionsRef.current = parentSectionsString;
    prevContinuityRefreshRef.current = continuityRefresh;

    setSections(prevSections => {
      const updatedSections = prevSections.map(section => {
        const sectionIdStr = String(section.id);
        const parentContent = parentSections[section.id] || 
                              parentSections[sectionIdStr] || 
                              parentSections[Number(section.id)];
        
        if (parentContent !== undefined && parentContent !== section.content) {
          return { ...section, content: parentContent };
        }
        return section;
      });
      
      const hasUpdates = updatedSections.some((section, index) => 
        section.content !== prevSections[index]?.content
      );
      
      if (onContentUpdate && hasUpdates) {
        onContentUpdate(updatedSections);
      }
      
      return updatedSections;
    });
  }, [parentSections, outline, continuityRefresh, onContentUpdate]);

  useEffect(() => {
    if (initialTitle && initialTitle.trim().length > 0) {
      setBlogTitle(initialTitle);
    }
  }, [initialTitle]);

  useEffect(() => {
    if (editingTitle && titleInputRef.current) {
      titleInputRef.current.focus();
      titleInputRef.current.select();
    }
  }, [editingTitle]);

  useEffect(() => {
    if (editingIntro && introInputRef.current) {
      introInputRef.current.focus();
      introInputRef.current.select();
    }
  }, [editingIntro]);

  const handleSuggestTitle = useCallback(() => {
    setShowTitleModal(true);
  }, []);

  const handleTitleAction = useCallback((action: string) => {
    switch (action) {
      case 'generate-titles':
      case 'research-titles':
        setShowTitleModal(true);
        break;
      case 'seo-optimize':
      case 'ab-test':
        break;
    }
  }, []);

  const handleTitleSelect = useCallback((selectedTitle: string) => {
    setBlogTitle(selectedTitle);
    setShowTitleModal(false);
  }, []);

  const handleGenerateIntroductions = useCallback(async () => {
    if (!research || !outline.length || isIntroductionLoading) return;

    setIsIntroductionLoading(true);
    try {
      const keywordAnalysis = research.keyword_analysis || {};
      const primaryKeywords = keywordAnalysis.primary || [];
      const searchIntent = keywordAnalysis.search_intent || 'informational';

      const sectionsContent: Record<string, string> = {};
      sections.forEach(section => {
        if (section.content) {
          sectionsContent[section.id] = section.content;
        }
      });

      const result = await blogWriterApi.generateIntroductions({
        blog_title: blogTitle,
        research,
        outline,
        sections_content: sectionsContent,
        primary_keywords: primaryKeywords,
        search_intent: searchIntent
      });

      if (result.success && result.introductions) {
        setGeneratedIntroductions(result.introductions);
        setShowIntroductionModal(true);
      }
    } catch (error) {
      console.error('Failed to generate introductions:', error);
    } finally {
      setIsIntroductionLoading(false);
    }
  }, [research, outline, sections, blogTitle, isIntroductionLoading]);

  const handleIntroductionSelect = useCallback((selectedIntroduction: string) => {
    setIntroduction(selectedIntroduction);
    setShowIntroductionModal(false);
  }, []);

  const toggleSectionExpansion = useCallback((sectionId: any) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) newSet.delete(sectionId);
      else newSet.add(sectionId);
      return newSet;
    });
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <div className="min-h-screen bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex gap-8">
            {/* Main editor column */}
            <div className="flex-1 min-w-0 max-w-4xl">
              <Paper elevation={0} className="bg-white p-8 md:p-10 rounded-xl border border-gray-200/60">
                {/* Title */}
                <div className="mb-6 pb-6 border-b border-gray-100">
                  <div className="flex items-start gap-2 group">
                    {editingTitle ? (
                      <TextField
                        inputRef={titleInputRef}
                        fullWidth
                        variant="standard"
                        value={blogTitle}
                        onChange={(e) => setBlogTitle(e.target.value)}
                        onBlur={() => setEditingTitle(false)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') setEditingTitle(false);
                          if (e.key === 'Escape') setEditingTitle(false);
                        }}
                        InputProps={{
                          disableUnderline: true,
                          className: 'text-2xl md:text-4xl font-bold font-serif text-gray-900 leading-tight truncate min-w-0',
                        }}
                      />
                    ) : (
                      <h1
                        className="flex-1 min-w-0 text-2xl md:text-4xl font-bold font-serif text-gray-900 leading-tight cursor-text hover:bg-gray-50/50 px-2 -ml-2 py-1 rounded transition-colors duration-150 truncate"
                        onClick={() => setEditingTitle(true)}
                      >
                        {blogTitle}
                      </h1>
                    )}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 mt-1 shrink-0 flex items-center gap-1">
                      <Tooltip title="Title actions">
                        <IconButton size="small" onClick={(e) => setTitleMenuAnchor(e.currentTarget)}>
                          <MoreHorizIcon className="text-gray-400" fontSize="small"/>
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Choose from AI titles">
                        <IconButton onClick={handleSuggestTitle} size="small">
                          <AutoAwesomeIcon className="text-purple-500" fontSize="small"/>
                        </IconButton>
                      </Tooltip>
                    </div>
                    <HoverMenu
                      anchorEl={titleMenuAnchor}
                      open={Boolean(titleMenuAnchor)}
                      onClose={() => setTitleMenuAnchor(null)}
                      type="title"
                      onAction={handleTitleAction}
                    />
                  </div>

                  {/* Introduction */}
                  <div className="mt-4 group/intro">
                    <div className="flex items-start gap-2">
                      {editingIntro ? (
                        <TextField
                          inputRef={introInputRef}
                          fullWidth
                          variant="standard"
                          multiline
                          minRows={2}
                          value={introduction}
                          onChange={(e) => setIntroduction(e.target.value)}
                          onBlur={() => setEditingIntro(false)}
                          placeholder="Write an engaging introduction..."
                          InputProps={{
                            disableUnderline: true,
                            className: 'text-base text-gray-600 leading-relaxed',
                          }}
                        />
                      ) : (
                        <p
                          className={`flex-1 text-base leading-relaxed cursor-text hover:bg-gray-50/50 px-2 -ml-2 py-1 rounded transition-colors duration-150 ${
                            introduction ? 'text-gray-600' : 'text-gray-400'
                          }`}
                          onClick={() => setEditingIntro(true)}
                        >
                          {introduction || 'Click to write your introduction...'}
                        </p>
                      )}
                      <div className="opacity-0 group-hover/intro:opacity-100 transition-opacity duration-200 shrink-0">
                        <Tooltip title="Generate Introduction">
                          <IconButton
                            onClick={handleGenerateIntroductions}
                            disabled={isIntroductionLoading || !research || !outline.length}
                            size="small"
                          >
                            {isIntroductionLoading ? (
                              <CircularProgress size={18} />
                            ) : (
                              <AutoAwesomeIcon className="text-blue-500" fontSize="small"/>
                            )}
                          </IconButton>
                        </Tooltip>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Sections */}
                <div className="space-y-1">
                  {sections.map((section, index) => {
                    const imageIdByIndex = outline[index]?.id;
                    const outlineSection = outline.find(s => (s.id === section.id) || (s.heading === section.title));
                    const imageId = imageIdByIndex || outlineSection?.id || section.id;
                    const sectionImage = sectionImages?.[imageId] || null;
                    return (
                      <BlogSection 
                        key={section.id} 
                        {...section} 
                        onContentUpdate={onContentUpdate}
                        expandedSections={expandedSections}
                        toggleSectionExpansion={toggleSectionExpansion}
                        refreshToken={continuityRefresh}
                        flowAnalysisResults={flowAnalysisResults}
                        sectionImage={sectionImage}
                      />
                    );
                  })}
                </div>

                {/* Stats bar */}
                <div className="mt-8 pt-4 border-t border-gray-100">
                  <div className="flex items-center justify-between text-sm text-gray-400">
                    <div className="flex items-center gap-4">
                      <span>{sections.length} {sections.length === 1 ? 'section' : 'sections'}</span>
                      <span className="text-gray-300">|</span>
                      <span>{totalWords.toLocaleString()} words</span>
                      <span className="text-gray-300">|</span>
                      <span>{readingTime} min read</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(100, (totalWords / Math.max(1, sections.reduce((s, sec) => s + (sec.outlineData?.targetWords || 500), 0))) * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400">
                        {totalWords > 0
                          ? `${Math.round(Math.min(100, (totalWords / Math.max(1, sections.reduce((s, sec) => s + (sec.outlineData?.targetWords || 500), 0))) * 100))}%`
                          : '0%'}
                      </span>
                    </div>
                  </div>
                </div>
              </Paper>
            </div>

            {/* Sidebar */}
            <div className="hidden lg:block w-72 shrink-0">
              <div className="sticky top-6">
                <EditorSidebar sections={sections} totalWords={totalWords} />
              </div>
            </div>
          </div>
        </div>

        {/* Title Selection Modal */}
        <Dialog open={showTitleModal} onClose={() => setShowTitleModal(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              Choose Your Blog Title
            </Typography>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              {researchTitles.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: 'primary.main' }}>
                    Research-Based Titles
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {researchTitles.map((title, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        fullWidth
                        onClick={() => handleTitleSelect(title)}
                        sx={{ justifyContent: 'flex-start', textAlign: 'left', textTransform: 'none', py: 1.5, px: 2 }}
                      >
                        {title}
                      </Button>
                    ))}
                  </Box>
                </Box>
              )}
              {aiGeneratedTitles.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: 'secondary.main' }}>
                    AI Generated Titles
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {aiGeneratedTitles.map((title, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        fullWidth
                        onClick={() => handleTitleSelect(title)}
                        sx={{ justifyContent: 'flex-start', textAlign: 'left', textTransform: 'none', py: 1.5, px: 2 }}
                      >
                        {title}
                      </Button>
                    ))}
                  </Box>
                </Box>
              )}
              {titleOptions.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: 'success.main' }}>
                    Additional Options
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {titleOptions.map((title, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        fullWidth
                        onClick={() => handleTitleSelect(title)}
                        sx={{ justifyContent: 'flex-start', textAlign: 'left', textTransform: 'none', py: 1.5, px: 2 }}
                      >
                        {title}
                      </Button>
                    ))}
                  </Box>
                </Box>
              )}
              {researchTitles.length === 0 && aiGeneratedTitles.length === 0 && titleOptions.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No title options available. Please generate an outline first.
                </Typography>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowTitleModal(false)}>Cancel</Button>
          </DialogActions>
        </Dialog>

        {/* Introduction Selection Modal */}
        <Dialog open={showIntroductionModal} onClose={() => setShowIntroductionModal(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              Choose Your Blog Introduction
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
              Select one of the AI-generated introductions below.
            </Typography>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              {generatedIntroductions.map((intro, index) => (
                <Box
                  key={index}
                  sx={{
                    mb: 3, p: 2,
                    border: '1px solid',
                    borderColor: index === 0 ? 'primary.main' : index === 1 ? 'secondary.main' : 'success.main',
                    borderRadius: 2,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': { backgroundColor: 'action.hover' },
                  }}
                  onClick={() => handleIntroductionSelect(intro)}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1, color: index === 0 ? 'primary.main' : index === 1 ? 'secondary.main' : 'success.main' }}>
                    {index === 0 ? 'Problem-Focused' : index === 1 ? 'Benefit-Focused' : 'Story/Statistic-Focused'}
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'text.primary', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                    {intro}
                  </Typography>
                </Box>
              ))}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowIntroductionModal(false)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      </div>
    </ThemeProvider>
  );
};

export default BlogEditor;
