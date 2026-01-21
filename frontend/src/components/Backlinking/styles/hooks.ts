/**
 * Backlinking Theme Hooks
 *
 * Custom hooks for using the Backlinking feature theme.
 */

import { useTheme } from '@mui/material/styles';
import { BacklinkingTheme } from './theme';

export const useBacklinkingTheme = () => {
  const theme = useTheme();

  // Extend the theme with backlinking-specific properties
  const backlinkingTheme = {
    ...theme,
    backlinking: {
      primary: '#60A5FA',     // Electric blue
      secondary: '#A855F7',   // Neural purple
      accent: '#06B6D4',      // Quantum cyan
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      background: {
        default: '#0F172A',
        paper: '#1E293B',
        card: '#1E293B',
      },
    },
  };

  return backlinkingTheme;
};

export const useBacklinkingColors = () => {
  const theme = useBacklinkingTheme();

  return {
    primary: theme.backlinking.primary,
    secondary: theme.backlinking.secondary,
    accent: theme.backlinking.accent,
    success: theme.backlinking.success,
    warning: theme.backlinking.warning,
    error: theme.backlinking.error,
    background: theme.backlinking.background,
  };
};