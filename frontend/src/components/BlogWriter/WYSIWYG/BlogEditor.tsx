import React, { useState, useCallback, useEffect } from 'react';
import { createTheme, ThemeProvider, Paper, IconButton, TextField, Tooltip, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box, Divider } from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
} from '@mui/icons-material';
import { BlogOutlineSection, BlogResearchResponse } from '../../../services/blogWriterApi';
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
  flowAnalysisResults
}) => {
  const [blogTitle, setBlogTitle] = useState(initialTitle || 'Your Amazing Blog Title');
  const [sections, setSections] = useState<any[]>([]);
  const [isTitleLoading, setIsTitleLoading] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<any>>(new Set());
  const [showTitleModal, setShowTitleModal] = useState(false);

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
                        wordBreak: 'break-word',
                        overflowWrap: 'break-word',
                        whiteSpace: 'normal',
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
                  <p className="mt-3 text-gray-500 text-sm">
                    This is where your blog's subtitle or a brief one-line description will appear. It's editable too!
                  </p>
                  <Divider sx={{ mt: 3, opacity: 0.3 }} />
                </div>
                <div>
                  {sections.map((section) => (
                    <BlogSection 
                      key={section.id} 
                      {...section} 
                      onContentUpdate={onContentUpdate}
                      expandedSections={expandedSections}
                      toggleSectionExpansion={toggleSectionExpansion}
                      refreshToken={continuityRefresh}
                      flowAnalysisResults={flowAnalysisResults}
                    />
                  ))}
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
      </div>
    </ThemeProvider>
  );
};

export default BlogEditor;