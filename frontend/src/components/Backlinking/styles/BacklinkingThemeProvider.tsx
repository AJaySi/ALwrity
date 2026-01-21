/**
 * Backlinking Theme Provider
 *
 * Provides the Backlinking feature theme to all child components.
 * This ensures styling is contained within the backlinking feature only.
 */

import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BacklinkingTheme } from './theme';

interface BacklinkingThemeProviderProps {
  children: React.ReactNode;
}

export const BacklinkingThemeProvider: React.FC<BacklinkingThemeProviderProps> = ({
  children
}) => {
  // Create a theme that extends the default theme with backlinking-specific overrides
  const backlinkingTheme = createTheme(BacklinkingTheme);

  // Load Inter font
  React.useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);

    return () => {
      document.head.removeChild(link);
    };
  }, []);

  return (
    <ThemeProvider theme={backlinkingTheme}>
      {children}
    </ThemeProvider>
  );
};