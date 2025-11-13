// Type definitions for Story Setup components

import { useStoryWriterState } from '../../../../hooks/useStoryWriterState';

export interface StorySetupProps {
  state: ReturnType<typeof useStoryWriterState>;
  onNext: () => void;
}

export interface CustomValuesState {
  customWritingStyles: string[];
  customStoryTones: string[];
  customNarrativePOVs: string[];
  customAudienceAgeGroups: string[];
  customContentRatings: string[];
  customEndingPreferences: string[];
}

export interface CustomValuesSetters {
  setCustomWritingStyles: React.Dispatch<React.SetStateAction<string[]>>;
  setCustomStoryTones: React.Dispatch<React.SetStateAction<string[]>>;
  setCustomNarrativePOVs: React.Dispatch<React.SetStateAction<string[]>>;
  setCustomAudienceAgeGroups: React.Dispatch<React.SetStateAction<string[]>>;
  setCustomContentRatings: React.Dispatch<React.SetStateAction<string[]>>;
  setCustomEndingPreferences: React.Dispatch<React.SetStateAction<string[]>>;
}

export interface SectionProps {
  state: ReturnType<typeof useStoryWriterState>;
  customValues: CustomValuesState;
  textFieldStyles: any;
}

