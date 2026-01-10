import { BlogResearchResponse } from '../../services/blogWriterApi';
import { PersonaDefaults, ResearchPersona, CompetitorAnalysisResponse } from '../../api/researchConfig';

export interface ResearchPreset {
  name: string;
  keywords: string;
  industry: string;
  targetAudience: string;
  researchMode: 'comprehensive' | 'targeted' | 'basic';
  icon: string;
  gradient: string;
  config: any;
}

export interface ResearchDashboardState {
  results: BlogResearchResponse | null;
  showDebug: boolean;
  presetKeywords: string[] | undefined;
  presetIndustry: string | undefined;
  presetTargetAudience: string | undefined;
  presetMode: any;
  presetConfig: any;
  personaData: PersonaDefaults | null;
  displayPresets: ResearchPreset[];
  showPersonaModal: boolean;
  personaChecked: boolean;
  researchPersona: ResearchPersona | null;
  showCompetitorModal: boolean;
  competitorData: CompetitorAnalysisResponse | null;
  loadingCompetitors: boolean;
  competitorError: string | null;
  showPersonaDetailsModal: boolean;
  personaExists: boolean;
  loadingPersonaDetails: boolean;
  restoredProject: any | null;
}

export interface UsePersonaManagementReturn {
  personaData: PersonaDefaults | null;
  researchPersona: ResearchPersona | null;
  personaExists: boolean;
  personaChecked: boolean;
  displayPresets: ResearchPreset[];
  showPersonaModal: boolean;
  loadingPersonaDetails: boolean;
  handleGeneratePersona: () => Promise<void>;
  handleCancelPersona: () => void;
  handleOpenPersonaDetails: () => Promise<void>;
  setShowPersonaModal: (show: boolean) => void;
  setPersonaExists: (exists: boolean) => void;
  setResearchPersona: (persona: ResearchPersona | null) => void;
  setDisplayPresets: (presets: ResearchPreset[]) => void;
}

export interface UseProjectRestorationReturn {
  restoredProject: any | null;
  presetKeywords: string[] | undefined;
  presetIndustry: string | undefined;
  presetTargetAudience: string | undefined;
  presetMode: any;
  presetConfig: any;
  results: BlogResearchResponse | null;
  setPresetKeywords: (keywords: string[] | undefined) => void;
  setPresetIndustry: (industry: string | undefined) => void;
  setPresetTargetAudience: (audience: string | undefined) => void;
  setPresetMode: (mode: any) => void;
  setPresetConfig: (config: any) => void;
  setResults: (results: BlogResearchResponse | null) => void;
}
