/**
 * Scene Helper Utilities
 * 
 * Shared utility functions for scene-related operations across YouTube Creator components.
 */

import React from 'react';
import { Movie, CallMade, Shuffle, PlayArrow } from '@mui/icons-material';

/**
 * Get icon component for scene emphasis type
 */
export const getSceneIcon = (emphasisTag: string, fontSize: 'small' | 'medium' = 'small'): React.ReactElement => {
  switch (emphasisTag) {
    case 'hook':
      return <Movie fontSize={fontSize} />;
    case 'cta':
      return <CallMade fontSize={fontSize} />;
    case 'transition':
      return <Shuffle fontSize={fontSize} />;
    case 'main_content':
    default:
      return <PlayArrow fontSize={fontSize} />;
  }
};

/**
 * Get color hex code for scene emphasis type
 */
export const getSceneColor = (emphasisTag: string): string => {
  switch (emphasisTag) {
    case 'hook':
      return '#3b82f6'; // Blue
    case 'cta':
      return '#8b5cf6'; // Purple
    case 'transition':
      return '#10b981'; // Green
    case 'main_content':
    default:
      return '#6b7280'; // Gray
  }
};

/**
 * Get human-readable label for scene type
 */
export const getSceneTypeLabel = (type: string): string => {
  switch (type) {
    case 'hook':
      return 'Hook';
    case 'cta':
      return 'CTA';
    case 'transition':
      return 'Transition';
    case 'main_content':
      return 'Content';
    default:
      return type.charAt(0).toUpperCase() + type.slice(1);
  }
};

/**
 * Format duration in seconds to human-readable string
 */
export const formatDuration = (seconds: number): string => {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
};

