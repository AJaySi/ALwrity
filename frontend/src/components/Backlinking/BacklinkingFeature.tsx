/**
 * Backlinking Feature Wrapper
 *
 * Wraps all backlinking components with the feature-specific theme and styling.
 * This ensures that backlinking styling is contained and doesn't affect other ALwrity features.
 */

import React from 'react';
import { BacklinkingThemeProvider } from './styles';
import { BacklinkingDashboard } from './BacklinkingDashboard';

interface BacklinkingFeatureProps {
  children?: React.ReactNode;
}

export const BacklinkingFeature: React.FC<BacklinkingFeatureProps> = ({
  children
}) => {
  return (
    <BacklinkingThemeProvider>
      {children || <BacklinkingDashboard />}
    </BacklinkingThemeProvider>
  );
};