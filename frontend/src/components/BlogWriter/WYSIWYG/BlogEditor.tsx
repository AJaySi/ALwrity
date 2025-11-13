import React, { useState, useCallback, useEffect, useRef } from 'react';
import { createTheme, ThemeProvider, Paper, IconButton, TextField, Tooltip, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box, Divider } from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
} from '@mui/icons-material';
import { BlogOutlineSection, BlogResearchResponse, blogWriterApi } from '../../../services/blogWriterApi';
import BlogSection from './BlogSection';

// Helper to create a consistent theme
const theme = createTheme({
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  palette: {
    primary: {
      main: '#4f46e5',
    },
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
  const [introduction, setIntroduction] = useState('Click "Generate Introduction" to create a compelling opening for your blog post based on your content and research.');
  const [sections, setSections] = useState<any[]>([]);
  const [isTitleLoading, setIsTitleLoading] = useState(false);
  const [isIntroductionLoading, setIsIntroductionLoading] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<any>>(new Set());
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [showIntroductionModal, setShowIntroductionModal] = useState(false);
  const [generatedIntroductions, setGeneratedIntroductions] = useState<string[]>([]);

  // Initialize sections from outline or use parent sections
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

  // Update sections when parentSections content changes (e.g., after SEO recommendations are applied)
  // This effect specifically watches for content changes in parentSections and updates the corresponding sections
  // Use a ref to track the previous parentSections content to detect actual content changes
  const prevParentSectionsRef = useRef<string>('');
  const prevContinuityRefreshRef = useRef<number | undefined>(undefined);
  
  useEffect(() => {
    if (!parentSections || !outline || outline.length === 0) return;

    // Create a stringified version of parentSections for comparison
    const parentSectionsString = JSON.stringify(parentSections);
    const continuityRefreshChanged = continuityRefresh !== prevContinuityRefreshRef.current;
    
    // Update if content changed OR continuityRefresh changed (forced refresh)
    if (parentSectionsString === prevParentSectionsRef.current && !continuityRefreshChanged) {
      return; // No changes detected
    }
    
    prevParentSectionsRef.current = parentSectionsString;
    prevContinuityRefreshRef.current = continuityRefresh;

    setSections(prevSections => {
      // Update sections with new content from parentSections
      const updatedSections = prevSections.map(section => {
        // Try multiple ID formats to match sections (string, number, or stringified number)
        const sectionIdStr = String(section.id);
        const parentContent = parentSections[section.id] || 
                              parentSections[sectionIdStr] || 
                              parentSections[Number(section.id)];
        
        // Update if parent has content for this section ID and it's different
        if (parentContent !== undefined && parentContent !== section.content) {
          console.log(`[BlogEditor] Updating section ${section.id} with new content (length: ${parentContent.length})`);
          return {
            ...section,
            content: parentContent
          };
        }
        return section;
      });
      
      // Check if any sections were actually updated
      const hasUpdates = updatedSections.some((section, index) => 
        section.content !== prevSections[index]?.content
      );
      
      // Notify parent component of content update if changes were made
      if (onContentUpdate && hasUpdates) {
        onContentUpdate(updatedSections);
      }
      
      return updatedSections;
    });
  }, [parentSections, outline, continuityRefresh, onContentUpdate]);

  // Initialize title from parent when provided
  useEffect(() => {
    if (initialTitle && initialTitle.trim().length > 0) {
      setBlogTitle(initialTitle);
    }
  }, [initialTitle]);

  const handleSuggestTitle = useCallback(() => {
    console.log('Available titles:', { researchTitles, aiGeneratedTitles, titleOptions });
    setShowTitleModal(true);
  }, [researchTitles, aiGeneratedTitles, titleOptions]);

  const handleTitleSelect = useCallback((selectedTitle: string) => {
    setBlogTitle(selectedTitle);
    setShowTitleModal(false);
  }, []);

  const handleGenerateIntroductions = useCallback(async () => {
    if (!research || !outline.length || isIntroductionLoading) {
      return;
    }

    setIsIntroductionLoading(true);
    try {
      const keywordAnalysis = research.keyword_analysis || {};
      const primaryKeywords = keywordAnalysis.primary || [];
      const searchIntent = keywordAnalysis.search_intent || 'informational';

      // Build sections_content from current sections
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
      alert('Failed to generate introductions. Please try again.');
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
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  }, []);


  // Main Render - Exactly like your example
  return (
    <ThemeProvider theme={theme}>
      <div className="bg-gray-50 min-h-screen font-sans">
        <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
          <div className="w-full max-w-4xl mx-auto">
            <Paper elevation={0} className="bg-white p-8 md:p-12 rounded-xl border border-gray-200/80 w-full">
                <div className="mb-8 pb-6 border-b">
                  <div className="flex items-start gap-2 group">
                    <h1 
                      className="flex-1 text-2xl md:text-4xl font-bold font-serif text-gray-900 leading-tight cursor-pointer hover:bg-gray-50 p-2 rounded-md transition-colors duration-200"
                      style={{
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        lineHeight: '1.3'
                      }}
                      onClick={() => {
                        const newTitle = prompt('Edit blog title:', blogTitle);
                        if (newTitle !== null) {
                          setBlogTitle(newTitle);
                        }
                      }}
                      title="Click to edit title"
                    >
                      {blogTitle}
                    </h1>
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 mt-1">
                      <Tooltip title="✨ ALwrity it">
                        <IconButton onClick={handleSuggestTitle} disabled={isTitleLoading} size="small">
                          {isTitleLoading ? <CircularProgress size={20} /> : <AutoAwesomeIcon className="text-purple-500" fontSize="small"/>}
                        </IconButton>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="mt-3 group/intro">
                    <div className="flex items-start gap-2">
                      <p 
                        className="flex-1 text-gray-600 text-sm leading-relaxed cursor-pointer hover:bg-gray-50 p-2 rounded-md transition-colors duration-200"
                        onClick={() => {
                          const newIntro = prompt('Edit introduction:', introduction);
                          if (newIntro !== null && newIntro.trim()) {
                            setIntroduction(newIntro.trim());
                          }
                        }}
                        title="Click to edit introduction"
                      >
                        {introduction}
                      </p>
                      <div className="opacity-0 group-hover/intro:opacity-100 transition-opacity duration-300">
                        <Tooltip title="✨ Generate Introduction">
                          <IconButton 
                            onClick={handleGenerateIntroductions} 
                            disabled={isIntroductionLoading || !research || !outline.length} 
                            size="small"
                          >
                            {isIntroductionLoading ? (
                              <CircularProgress size={20} />
                            ) : (
                              <AutoAwesomeIcon className="text-blue-500" fontSize="small"/>
                            )}
                          </IconButton>
                        </Tooltip>
                      </div>
                    </div>
                  </div>
                  <Divider sx={{ mt: 3, opacity: 0.3 }} />
                </div>
                <div>
                  {sections.map((section, index) => {
                    // Robust image mapping: prefer outline index id (order is consistent across phases)
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
            </Paper>
          </div>
        </main>
        
        {/* Title Selection Modal */}
        <Dialog 
          open={showTitleModal} 
          onClose={() => setShowTitleModal(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              Choose Your Blog Title
            </Typography>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              {/* Research Titles */}
              {researchTitles.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: 'primary.main' }}>
                    📊 Research-Based Titles
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {researchTitles.map((title, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        fullWidth
                        onClick={() => handleTitleSelect(title)}
                        sx={{ 
                          justifyContent: 'flex-start',
                          textAlign: 'left',
                          textTransform: 'none',
                          py: 1.5,
                          px: 2,
                          '&:hover': {
                            backgroundColor: 'primary.light',
                            color: 'white',
                          }
                        }}
                      >
                        {title}
                      </Button>
                    ))}
                  </Box>
                </Box>
              )}
              
              {/* AI Generated Titles */}
              {aiGeneratedTitles.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: 'secondary.main' }}>
                    🤖 AI Generated Titles
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {aiGeneratedTitles.map((title, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        fullWidth
                        onClick={() => handleTitleSelect(title)}
                        sx={{ 
                          justifyContent: 'flex-start',
                          textAlign: 'left',
                          textTransform: 'none',
                          py: 1.5,
                          px: 2,
                          '&:hover': {
                            backgroundColor: 'secondary.light',
                            color: 'white',
                          }
                        }}
                      >
                        {title}
                      </Button>
                    ))}
                  </Box>
                </Box>
              )}
              
              {/* Title Options */}
              {titleOptions.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: 'success.main' }}>
                    ✨ Additional Options
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {titleOptions.map((title, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        fullWidth
                        onClick={() => handleTitleSelect(title)}
                        sx={{ 
                          justifyContent: 'flex-start',
                          textAlign: 'left',
                          textTransform: 'none',
                          py: 1.5,
                          px: 2,
                          '&:hover': {
                            backgroundColor: 'success.light',
                            color: 'white',
                          }
                        }}
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
              
              {/* Debug info */}
              {process.env.NODE_ENV === 'development' && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Debug: Research titles: {researchTitles.length}, AI titles: {aiGeneratedTitles.length}, Options: {titleOptions.length}
                  </Typography>
                </Box>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowTitleModal(false)}>
              Cancel
            </Button>
          </DialogActions>
        </Dialog>

        {/* Introduction Selection Modal */}
        <Dialog 
          open={showIntroductionModal} 
          onClose={() => setShowIntroductionModal(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              Choose Your Blog Introduction
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
              Select one of the AI-generated introductions below. Each offers a different approach to hooking your readers.
            </Typography>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              {generatedIntroductions.map((intro, index) => (
                <Box 
                  key={index} 
                  sx={{ 
                    mb: 3,
                    p: 2,
                    border: '1px solid',
                    borderColor: index === 0 ? 'primary.main' : index === 1 ? 'secondary.main' : 'success.main',
                    borderRadius: 2,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onClick={() => handleIntroductionSelect(intro)}
                >
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      fontWeight: 'bold', 
                      mb: 1,
                      color: index === 0 ? 'primary.main' : index === 1 ? 'secondary.main' : 'success.main'
                    }}
                  >
                    {index === 0 ? '📌 Option 1: Problem-Focused' : index === 1 ? '✨ Option 2: Benefit-Focused' : '📊 Option 3: Story/Statistic-Focused'}
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: 'text.primary',
                      lineHeight: 1.7,
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {intro}
                  </Typography>
                </Box>
              ))}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowIntroductionModal(false)}>
              Cancel
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    </ThemeProvider>
  );
};

export default BlogEditor;