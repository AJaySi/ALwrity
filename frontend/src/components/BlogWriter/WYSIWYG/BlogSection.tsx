import React, { useState, useEffect, useRef } from 'react';
import { 
  Paper, 
  IconButton, 
  Chip, 
  TextField, 
  Tooltip, 
  CircularProgress,
  Divider,
  Button,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import {
  Edit as EditIcon,
  DeleteOutline as DeleteOutlineIcon,
  FileCopyOutlined as FileCopyOutlinedIcon,
  Link as LinkIcon,
  AutoAwesome as AutoAwesomeIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import useBlogTextSelectionHandler from './BlogTextSelectionHandler';
import { ContinuityBadge } from '../ContinuityBadge';
import { blogWriterApi } from '../../../services/blogWriterApi';

interface BlogSectionProps {
  id: any;
  title: string;
  content: string;
  wordCount: number;
  sources: number;
  outlineData?: {
    subheadings: string[];
    keyPoints: string[];
    keywords: string[];
    references: any[];
    targetWords: number;
  };
  onContentUpdate?: (sections: any[]) => void;
  expandedSections: Set<any>;
  toggleSectionExpansion: (sectionId: any) => void;
  refreshToken?: number;
  flowAnalysisResults?: any;
  sectionImage?: string;
}

const BlogSection: React.FC<BlogSectionProps> = ({ 
  id, 
  title, 
  content: initialContent, 
  wordCount, 
  sources, 
  outlineData, 
  onContentUpdate,
  expandedSections,
  toggleSectionExpansion,
  refreshToken,
  flowAnalysisResults,
  sectionImage
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [sectionTitle, setSectionTitle] = useState(title);
  const [content, setContent] = useState(initialContent);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const contentRef = useRef<HTMLTextAreaElement>(null);
  const [toolsAnchorEl, setToolsAnchorEl] = useState<HTMLElement | null>(null);
  const [activeTool, setActiveTool] = useState<null | 'originality' | 'optimize' | 'fact' | 'links' | 'flow'>(null);
  const [toolLoading, setToolLoading] = useState(false);
  const [toolResult, setToolResult] = useState<any>(null);
  const [toolDialogOpen, setToolDialogOpen] = useState(false);

  // Initialize assistive writing handler
  const assistiveWriting = useBlogTextSelectionHandler(
    contentRef,
    (originalText: string, newText: string, editType: string) => {
      // Handle text replacement in the textarea
      if (contentRef.current) {
        const textarea = contentRef.current;
        
        // For smart suggestions, newText is already the complete updated content with insertion
        // For other edits (like text selection improvements), we need to replace originalText with newText
        let updatedContent: string;
        
        if (editType === 'smart-suggestion') {
          // newText already contains the full content with suggestion inserted
          updatedContent = newText;
        } else {
          // For other edits, replace the selected text
          const currentContent = textarea.value;
          updatedContent = currentContent.replace(originalText, newText);
        }
        
        console.log('🔍 [BlogSection] Text updated, editType:', editType, 'New length:', updatedContent.length);
        setContent(updatedContent);
        
        // Update parent state
        if (onContentUpdate) {
          onContentUpdate([{ id, content: updatedContent }]);
        }
        
        // Note: Cursor positioning is handled by SmartTypingAssist for smart-suggestion edits
        // For other edits, we may need to handle cursor positioning here if needed
      }
    }
  );

  // Format content helper - ensures proper paragraph breaks
  const formatContent = (rawContent: string) => {
    if (!rawContent) return rawContent;
    
    // Ensure double line breaks between paragraphs
    // Replace single line breaks with double line breaks if they're not already double
    let formatted = rawContent
      .replace(/\n{3,}/g, '\n\n') // Replace 3+ line breaks with double
      .replace(/\n(?!\n)/g, '\n\n') // Replace single line breaks with double
      .trim();
    
    return formatted;
  };

  // Sync content when initialContent changes (e.g., from AI generation)
  useEffect(() => {
    if (initialContent !== content) {
      const formattedContent = formatContent(initialContent);
      setContent(formattedContent);
    }
  }, [initialContent]);
  
  const handleContentChange = (e: any) => {
    const newContent = e.target.value;
    console.log('🔍 [BlogSection] handleContentChange called, content length:', newContent.length);
    setContent(newContent);
    
    // Trigger smart typing assist
    assistiveWriting.handleTypingChange(newContent);
  };
  
  const handleFocus = () => setIsFocused(true);
  const handleBlur = () => setIsFocused(false);

  const openToolsMenu = (event: React.MouseEvent<HTMLElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setToolsAnchorEl(event.currentTarget);
  };

  const closeToolsMenu = () => {
    setToolsAnchorEl(null);
  };

  const closeToolDialog = () => {
    setToolDialogOpen(false);
    setToolLoading(false);
  };

  const runSectionTool = async (tool: 'originality' | 'optimize' | 'fact' | 'links' | 'flow') => {
    closeToolsMenu();
    setActiveTool(tool);
    setToolResult(null);
    setToolLoading(true);
    setToolDialogOpen(true);

    try {
      if (tool === 'originality') {
        const res = await blogWriterApi.sectionOriginalityTools({
          section_id: String(id),
          title: sectionTitle,
          content
        });
        setToolResult(res);
        return;
      }

      if (tool === 'links') {
        const res = await blogWriterApi.sectionInternalLinkTools({
          section_id: String(id),
          title: sectionTitle,
          content
        });
        setToolResult(res);
        return;
      }

      if (tool === 'fact') {
        const res = await blogWriterApi.sectionFactCheckTools({
          section_id: String(id),
          title: sectionTitle,
          content
        });
        setToolResult(res);
        return;
      }

      if (tool === 'optimize') {
        const res = await blogWriterApi.sectionOptimizeTools({
          section_id: String(id),
          title: sectionTitle,
          content,
          keywords: outlineData?.keywords || [],
          goal: 'readability'
        });
        setToolResult(res);
        return;
      }

      if (tool === 'flow') {
        const res = await blogWriterApi.analyzeFlowAdvanced({
          title: sectionTitle,
          sections: [{ id: String(id), heading: sectionTitle, content }]
        });
        setToolResult(res);
        return;
      }
    } catch (error: any) {
      setToolResult({ success: false, error: error?.message || 'Request failed' });
    } finally {
      setToolLoading(false);
    }
  };

  const applyOptimizedContent = () => {
    const next = toolResult?.optimized_content;
    if (!next) return;
    setContent(next);
    if (onContentUpdate) {
      onContentUpdate([{ id, content: next }]);
    }
    closeToolDialog();
  };

  const insertLinkSuggestion = (url: string) => {
    if (!url) return;
    const insertion = `\n\n[Related](${url})`;
    const next = `${content || ''}${insertion}`;
    setContent(next);
    if (onContentUpdate) {
      onContentUpdate([{ id, content: next }]);
    }
  };
  

  const handleGenerateContent = async () => {
    setIsGenerating(true);
    try {
      // This would call your AI service for content generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      const generated = `This is AI-generated content for "${sectionTitle}" with engaging, well-structured paragraphs grounded in your research.`;
      setContent(generated);
      // Update parent state if needed
      if (onContentUpdate) {
        onContentUpdate([{ id, content: generated }]);
      }
    } catch (error) {
      console.error('Failed to generate content:', error);
    } finally {
      setIsGenerating(false);
    }
  };


  return (
    <div 
      className="group relative mb-6" 
      id={`section-${id}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      
      <div className="flex items-center gap-3 mb-4">
        {isEditing ? (
          <TextField
            fullWidth
            variant="standard"
            value={sectionTitle}
            onChange={(e) => setSectionTitle(e.target.value)}
            onBlur={() => setIsEditing(false)}
            autoFocus
            InputProps={{ className: 'text-2xl md:text-3xl font-bold !font-serif text-gray-800' }}
          />
        ) : (
          <h2
            className="text-2xl md:text-3xl font-bold font-serif text-gray-800 cursor-pointer"
            onClick={() => setIsEditing(true)}
          >
            {sectionTitle}
          </h2>
        )}
        
      </div>

      {/* Section Image Display */}
      {sectionImage && (
        <div style={{ marginBottom: '16px', marginTop: '8px' }}>
          <div style={{ 
            border: '1px solid #e0e0e0', 
            borderRadius: '8px', 
            overflow: 'hidden',
            maxWidth: '100%',
            backgroundColor: '#fff'
          }}>
            <img 
              src={`data:image/png;base64,${sectionImage}`} 
              alt={`Cover image for ${sectionTitle}`}
              style={{ 
                width: '100%', 
                height: 'auto',
                display: 'block',
                maxHeight: '400px',
                objectFit: 'contain'
              }} 
            />
          </div>
        </div>
      )}
      
      <div 
        className="relative"
        onMouseUp={assistiveWriting.handleTextSelection}
        onKeyUp={assistiveWriting.handleTextSelection}
      >
        <TextField
          multiline
          fullWidth
          variant="standard"
          value={content}
          onChange={handleContentChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder="Start writing your section here... Select text for assistive writing features!"
          InputProps={{
            disableUnderline: true,
            className: 'text-gray-600 leading-relaxed text-base md:text-lg focus-within:bg-indigo-50/50 p-2 rounded-md transition-colors duration-200',
            style: {
              whiteSpace: 'pre-wrap', // Preserve line breaks and spaces
              lineHeight: '1.8', // Better line spacing for readability
            },
          }}
          inputRef={contentRef}
        />
        
        {/* Render assistive writing selection menu */}
        {assistiveWriting.renderSelectionMenu()}
        {/* Simple AI generation button - only show when no text selection menu is active */}
        {content && isFocused && !assistiveWriting.selectionMenu && (
          <div 
            className="absolute z-10"
            style={{
              right: '8px',
              bottom: '8px',
            }}
          >
            <Tooltip title="✨ Generate Content">
              <IconButton 
                size="small" 
                onClick={handleGenerateContent} 
                disabled={isGenerating}
                sx={{
                  background: 'rgba(79, 70, 229, 0.1)',
                  color: '#4f46e5',
                  border: '1px solid rgba(79, 70, 229, 0.2)',
                  '&:hover': {
                    background: 'rgba(79, 70, 229, 0.2)',
                    transform: 'translateY(-1px)',
                  },
                  '&:disabled': {
                    background: 'rgba(255, 255, 255, 0.7)',
                    color: '#9CA3AF',
                  },
                }}
              >
                {isGenerating ? (
                  <CircularProgress size={16} color="inherit" />
                ) : (
                  <AutoAwesomeIcon fontSize="small" />
                )}
              </IconButton>
            </Tooltip>
          </div>
        )}
      </div>

      {/* Outline Information Section */}
      {outlineData && expandedSections.has(id) && (
        <div className="mt-4">
          <Paper elevation={0} sx={{ p: 2, bgcolor: '#f8f9fa', borderRadius: 2, mb: 2 }}>
            <div className="flex flex-col gap-4">
              {/* Key Points */}
              {outlineData.keyPoints && outlineData.keyPoints.length > 0 && (
                <div>
                  <div className="text-sm font-bold text-blue-600 mb-2">Key Points:</div>
                  <div className="flex flex-wrap gap-1">
                    {outlineData.keyPoints.map((point: any, index: any) => (
                      <Chip
                        key={index}
                        label={point}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Subheadings */}
              {outlineData.subheadings && outlineData.subheadings.length > 0 && (
                <div>
                  <div className="text-sm font-bold text-blue-600 mb-2">Subheadings:</div>
                  <div className="flex flex-wrap gap-1">
                    {outlineData.subheadings.map((subheading: any, index: any) => (
                      <Chip
                        key={index}
                        label={subheading}
                        size="small"
                        variant="outlined"
                        color="secondary"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Keywords */}
              {outlineData.keywords && outlineData.keywords.length > 0 && (
                <div>
                  <div className="text-sm font-bold text-blue-600 mb-2">Keywords:</div>
                  <div className="flex flex-wrap gap-1">
                    {outlineData.keywords.map((keyword: any, index: any) => (
                      <Chip
                        key={index}
                        label={keyword}
                        size="small"
                        variant="filled"
                        color="primary"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Target Words */}
              {outlineData.targetWords > 0 && (
                <div>
                  <div className="text-sm font-bold text-blue-600 mb-2">
                    Target Words: {outlineData.targetWords}
                  </div>
                </div>
              )}

              {/* References */}
              {outlineData.references && outlineData.references.length > 0 && (
                <div>
                  <div className="text-sm font-bold text-blue-600 mb-2">
                    References ({outlineData.references.length}):
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {outlineData.references.slice(0, 3).map((ref: any, index: any) => (
                      <Chip
                        key={index}
                        label={ref.title || `Source ${index + 1}`}
                        size="small"
                        variant="outlined"
                        color="info"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    ))}
                    {outlineData.references.length > 3 && (
                      <Chip
                        label={`+${outlineData.references.length - 3} more`}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    )}
                  </div>
                </div>
              )}
            </div>
          </Paper>
        </div>
      )}
      
      <div className="absolute -bottom-4 right-0 flex items-center space-x-1" style={{ opacity: isHovered ? 1 : 0, transition: 'opacity 0.3s' }}>
        <Chip label={`${content.split(' ').length} words`} size="small" variant="outlined" className="!text-gray-500" />
        <Chip icon={<LinkIcon />} label={`${sources} sources`} size="small" variant="outlined" className="!text-gray-500" />
        {outlineData && (
          <Chip
            icon={expandedSections.has(id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            label="Outline Info"
            size="small"
            variant="outlined"
            clickable
            onClick={() => toggleSectionExpansion(id)}
            sx={{ 
              fontSize: '0.75rem',
              '&:hover': {
                backgroundColor: 'rgba(25, 118, 210, 0.08)',
              }
            }}
          />
        )}
        <Tooltip title="Generate Content">
          <IconButton size="small" onClick={handleGenerateContent}>
            <AutoAwesomeIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        {/* Flow Analysis Badge - Enabled when flow analysis results are available */}
        <ContinuityBadge 
          sectionId={id} 
          refreshToken={refreshToken}
          disabled={!flowAnalysisResults}
          flowAnalysisResults={flowAnalysisResults}
        />

        <Tooltip title="Section Tools">
          <IconButton size="small" onClick={openToolsMenu}>
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Copy Section"><IconButton size="small"><FileCopyOutlinedIcon fontSize="small" /></IconButton></Tooltip>
        <Tooltip title="Edit Metadata"><IconButton size="small"><EditIcon fontSize="small" /></IconButton></Tooltip>
        <Tooltip title="Delete Section"><IconButton size="small" className="text-red-500"><DeleteOutlineIcon fontSize="small" /></IconButton></Tooltip>
      </div>

      <Menu
        anchorEl={toolsAnchorEl}
        open={Boolean(toolsAnchorEl)}
        onClose={closeToolsMenu}
      >
        <MenuItem onClick={() => runSectionTool('originality')}>Originality Check</MenuItem>
        <MenuItem onClick={() => runSectionTool('optimize')}>Optimize Section</MenuItem>
        <MenuItem onClick={() => runSectionTool('fact')}>SIF Fact Check</MenuItem>
        <MenuItem onClick={() => runSectionTool('links')}>Internal Link Suggestions</MenuItem>
        <MenuItem onClick={() => runSectionTool('flow')}>Flow Analysis</MenuItem>
      </Menu>

      <Dialog open={toolDialogOpen} onClose={closeToolDialog} fullWidth maxWidth="md">
        <DialogTitle>
          {activeTool === 'originality' && 'Originality Check'}
          {activeTool === 'optimize' && 'Optimize Section'}
          {activeTool === 'fact' && 'SIF Fact Check'}
          {activeTool === 'links' && 'Internal Link Suggestions'}
          {activeTool === 'flow' && 'Flow Analysis'}
        </DialogTitle>
        <DialogContent dividers>
          {toolLoading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <CircularProgress size={18} />
              <div>Working…</div>
            </div>
          )}

          {!toolLoading && toolResult?.error && (
            <div style={{ color: '#b91c1c', fontWeight: 600 }}>{toolResult.error}</div>
          )}

          {!toolLoading && activeTool === 'optimize' && toolResult?.optimized_content && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {toolResult?.diff_summary && (
                <div style={{ fontWeight: 600 }}>{toolResult.diff_summary}</div>
              )}
              {Array.isArray(toolResult?.changes_made) && toolResult.changes_made.length > 0 && (
                <List dense>
                  {toolResult.changes_made.map((c: string, idx: number) => (
                    <ListItem key={idx}>
                      <ListItemText primary={c} />
                    </ListItem>
                  ))}
                </List>
              )}
              <TextField
                multiline
                minRows={10}
                value={toolResult.optimized_content}
                fullWidth
                InputProps={{ readOnly: true }}
              />
            </div>
          )}

          {!toolLoading && activeTool === 'links' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {Array.isArray(toolResult?.suggestions) && toolResult.suggestions.length > 0 ? (
                <List>
                  {toolResult.suggestions.map((s: any, idx: number) => (
                    <ListItem key={idx} secondaryAction={
                      <Button size="small" onClick={() => insertLinkSuggestion(s.url)}>Insert</Button>
                    }>
                      <ListItemText
                        primary={s.url}
                        secondary={`confidence: ${(s.confidence ?? 0).toFixed?.(2) ?? s.confidence} • ${s.reason ?? ''}`}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <div>No suggestions yet. Make sure SIF index has your website content.</div>
              )}
            </div>
          )}

          {!toolLoading && activeTool === 'originality' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {toolResult?.cannibalization && (
                <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(toolResult.cannibalization, null, 2)}</pre>
              )}
              {Array.isArray(toolResult?.matches) && toolResult.matches.length > 0 ? (
                <List>
                  {toolResult.matches.map((m: any, idx: number) => (
                    <ListItem key={idx}>
                      <ListItemText
                        primary={`${m.id ?? 'unknown'} (${(m.score ?? 0).toFixed?.(3) ?? m.score})`}
                        secondary={m.excerpt}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <div>No close matches found.</div>
              )}
            </div>
          )}

          {!toolLoading && activeTool === 'fact' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {toolResult?.verification && (
                <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(toolResult.verification, null, 2)}</pre>
              )}
              {Array.isArray(toolResult?.citations) && toolResult.citations.length > 0 && (
                <List>
                  {toolResult.citations.map((c: any, idx: number) => (
                    <ListItem key={idx}>
                      <ListItemText primary={c.citation_text || c.title || c.source} secondary={c.source} />
                    </ListItem>
                  ))}
                </List>
              )}
            </div>
          )}

          {!toolLoading && activeTool === 'flow' && (
            <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(toolResult, null, 2)}</pre>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeToolDialog}>Close</Button>
          {activeTool === 'optimize' && toolResult?.optimized_content && (
            <Button variant="contained" onClick={applyOptimizedContent}>Replace Section Content</Button>
          )}
        </DialogActions>
      </Dialog>
      
      {/* Section Divider */}
      <Divider sx={{ mt: 1.2, mb: 1, opacity: 0.3 }} />
    </div>
  );
};

export default BlogSection;
