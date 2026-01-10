/**
 * AdvancedOptionsSection Component
 * 
 * Displays advanced provider options (Exa/Tavily) when advanced mode is enabled
 */

import React from 'react';
import { ProviderAvailability } from '../../../../api/researchConfig';
import { ResearchConfig } from '../../../../services/researchApi';
import { ExaOptions } from './ExaOptions';
import { TavilyOptions } from './TavilyOptions';

interface AdvancedOptionsSectionProps {
  advanced: boolean;
  providerAvailability: ProviderAvailability | null;
  config: ResearchConfig;
  onConfigUpdate: (updates: Partial<ResearchConfig>) => void;
}

export const AdvancedOptionsSection: React.FC<AdvancedOptionsSectionProps> = ({
  advanced,
  providerAvailability,
  config,
  onConfigUpdate,
}) => {
  if (!advanced) return null;

  return (
    <>
      {/* Tavily-Specific Options */}
      {providerAvailability?.tavily_available && (
        <TavilyOptions
          config={config}
          onConfigUpdate={onConfigUpdate}
        />
      )}

      {/* Exa-Specific Options */}
      {providerAvailability?.exa_available && (
        <ExaOptions
          config={config}
          onConfigUpdate={onConfigUpdate}
        />
      )}
    </>
  );
};
