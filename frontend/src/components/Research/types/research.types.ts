import { BlogResearchResponse, ResearchMode, ResearchConfig } from '../../../services/blogWriterApi';

export interface WizardState {
  currentStep: number;
  keywords: string[];
  industry: string;
  targetAudience: string;
  researchMode: ResearchMode;
  config: ResearchConfig;
  results: BlogResearchResponse | null;
}

export interface WizardStepProps {
  state: WizardState;
  onUpdate: (updates: Partial<WizardState>) => void;
  onNext: () => void;
  onBack: () => void;
}

export interface ResearchWizardProps {
  onComplete?: (results: BlogResearchResponse) => void;
  onCancel?: () => void;
  initialKeywords?: string[];
  initialIndustry?: string;
}

export interface ModeCardInfo {
  mode: ResearchMode;
  title: string;
  description: string;
  features: string[];
  icon: string;
}

