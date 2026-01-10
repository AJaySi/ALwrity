import React from 'react';
import { PresetsCard } from './PresetsCard';
import { DebugConsole } from './DebugConsole';
import { ResearchPreset } from '../types';
import { BlogResearchResponse } from '../../../services/blogWriterApi';

interface LeftPanelProps {
  presets: ResearchPreset[];
  personaExists: boolean;
  showDebug: boolean;
  results: BlogResearchResponse | null;
  onPresetClick: (preset: ResearchPreset) => void;
  onReset: () => void;
  onToggleDebug: (show: boolean) => void;
}

export const LeftPanel: React.FC<LeftPanelProps> = ({
  presets,
  personaExists,
  showDebug,
  results,
  onPresetClick,
  onReset,
  onToggleDebug,
}) => {
  return (
    <div style={{ flex: '1 1 280px', minWidth: '280px' }}>
      <PresetsCard
        presets={presets}
        personaExists={personaExists}
        onPresetClick={onPresetClick}
        onReset={onReset}
      />
      <DebugConsole
        showDebug={showDebug}
        results={results}
        onToggleDebug={onToggleDebug}
      />
    </div>
  );
};
