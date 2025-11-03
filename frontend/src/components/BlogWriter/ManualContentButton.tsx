import React, { useState } from 'react';
import { Button, CircularProgress } from '@mui/material';
import { mediumBlogApi } from '../../services/blogWriterApi';
import { BlogOutlineSection, BlogResearchResponse } from '../../services/blogWriterApi';

interface ManualContentButtonProps {
  /**
   * The confirmed outline sections
   */
  outline: BlogOutlineSection[];
  /**
   * The research data
   */
  research: BlogResearchResponse;
  /**
   * Blog title (optional)
   */
  blogTitle?: string;
  /**
   * Existing sections content (optional)
   */
  sections?: Record<string, string>;
  /**
   * Callback when content generation starts
   */
  onGenerationStart?: (taskId: string) => void;
}

/**
 * Manual content generation button that works independently of CopilotKit
 * Triggers medium blog generation via mediumBlogApi
 */
export const ManualContentButton: React.FC<ManualContentButtonProps> = ({
  outline,
  research,
  blogTitle,
  sections,
  onGenerationStart,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!outline || outline.length === 0) {
      alert('Please confirm an outline first before generating content.');
      return;
    }

    if (!research) {
      alert('Research data is required for content generation.');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const payload = {
        outline,
        research,
        title: blogTitle || outline[0]?.heading || 'Blog Post',
        existing_sections: sections || {},
      };

      const { task_id } = await mediumBlogApi.startMediumGeneration(payload as any);
      
      if (task_id) {
        onGenerationStart?.(task_id);
      } else {
        throw new Error('Failed to start content generation - no task ID returned');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(errorMessage);
      alert(`Content generation failed: ${errorMessage}`);
      setIsGenerating(false);
    }
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>Generate Blog Content</h3>
      <p style={{ margin: '0 0 20px 0', color: '#666', fontSize: '14px' }}>
        Generate full content for all sections in your confirmed outline.
      </p>
      
      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={handleGenerate}
        disabled={!outline || outline.length === 0 || !research || isGenerating}
        startIcon={isGenerating ? <CircularProgress size={20} color="inherit" /> : null}
        sx={{
          minWidth: 200,
          py: 1.5,
          px: 4,
        }}
      >
        {isGenerating ? 'Generating Content...' : '📝 Generate Content'}
      </Button>

      {error && (
        <p style={{ margin: '12px 0 0 0', color: '#d32f2f', fontSize: '14px' }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default ManualContentButton;

