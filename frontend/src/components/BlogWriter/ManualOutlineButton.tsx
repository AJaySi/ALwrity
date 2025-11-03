import React, { useState } from 'react';
import { Button, CircularProgress } from '@mui/material';

interface ManualOutlineButtonProps {
  /**
   * Ref to OutlineGenerator component with generateNow() method
   */
  outlineGenRef: React.RefObject<{ 
    generateNow: () => Promise<{ 
      success: boolean; 
      message?: string; 
      task_id?: string;
      cached?: boolean;
      outline?: any[];
      title_options?: string[];
    }> 
  }>;
  /**
   * Whether research is available (required for outline generation)
   */
  hasResearch: boolean;
  /**
   * Callback when outline generation starts
   */
  onGenerationStart?: (taskId: string) => void;
}

/**
 * Manual outline generation button that works independently of CopilotKit
 * Calls the generateNow() method from OutlineGenerator ref
 */
export const ManualOutlineButton: React.FC<ManualOutlineButtonProps> = ({
  outlineGenRef,
  hasResearch,
  onGenerationStart,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!hasResearch) {
      alert('Please complete research first before generating an outline.');
      return;
    }

    if (!outlineGenRef.current) {
      alert('Outline generator is not available. Please refresh the page.');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const result = await outlineGenRef.current.generateNow();
      
      if (result.success) {
        if (result.cached && result.outline) {
          // Handle cached result - outline is already available, no need to poll
          console.log('[ManualOutlineButton] Cached outline used', { sections: result.outline.length });
          // The outline should be set by the parent component handling the cache
        } else if (result.task_id) {
          onGenerationStart?.(result.task_id);
        }
      } else {
        setError(result.message || 'Failed to generate outline');
        alert(result.message || 'Failed to generate outline. Please try again.');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(errorMessage);
      alert(`Outline generation failed: ${errorMessage}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>Create Your Outline</h3>
      <p style={{ margin: '0 0 20px 0', color: '#666', fontSize: '14px' }}>
        Generate an AI-powered outline based on your research.
      </p>
      
      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={handleGenerate}
        disabled={!hasResearch || isGenerating}
        startIcon={isGenerating ? <CircularProgress size={20} color="inherit" /> : null}
        sx={{
          minWidth: 200,
          py: 1.5,
          px: 4,
        }}
      >
        {isGenerating ? 'Generating Outline...' : '🧩 Generate Outline'}
      </Button>

      {error && (
        <p style={{ margin: '12px 0 0 0', color: '#d32f2f', fontSize: '14px' }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default ManualOutlineButton;

