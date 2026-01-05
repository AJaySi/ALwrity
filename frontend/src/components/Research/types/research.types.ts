import { BlogResearchResponse, ResearchMode, ResearchConfig } from '../../../services/blogWriterApi';
import { 
  ResearchIntent, 
  AnalyzeIntentResponse, 
  IntentDrivenResearchResponse,
  ResearchQuery,
} from './intent.types';

export interface WizardState {
  currentStep: number;
  keywords: string[];
  industry: string;
  targetAudience: string;
  researchMode: ResearchMode;
  config: ResearchConfig;
  results: BlogResearchResponse | null;
}

export interface ResearchExecution {
  // Legacy API
  executeResearch: (state: WizardState) => Promise<string | null>;
  stopExecution: () => void;
  isExecuting: boolean;
  error: string | null;
  progressMessages: Array<{ timestamp: string; message: string }>;
  currentStatus: string;
  result: any;
  
  // Intent-driven API
  useIntentMode: boolean;
  setUseIntentMode: (enabled: boolean) => void;
  isAnalyzingIntent: boolean;
  intentAnalysis: AnalyzeIntentResponse | null;
  confirmedIntent: ResearchIntent | null;
  intentResult: IntentDrivenResearchResponse | null;
  analyzeIntent: (state: WizardState) => Promise<AnalyzeIntentResponse | null>;
  confirmIntent: (intent: ResearchIntent) => void;
  updateIntentField: <K extends keyof ResearchIntent>(field: K, value: ResearchIntent[K]) => void;
  executeIntentResearch: (state: WizardState, selectedQueries?: ResearchQuery[]) => Promise<IntentDrivenResearchResponse | null>;
  clearIntent: () => void;
}

export interface WizardStepProps {
  state: WizardState;
  onUpdate: (updates: Partial<WizardState>) => void;
  onNext: () => void;
  onBack: () => void;
  execution?: ResearchExecution;
}

export interface ResearchWizardProps {
  onComplete?: (results: BlogResearchResponse) => void;
  onCancel?: () => void;
  initialKeywords?: string[];
  initialIndustry?: string;
  initialTargetAudience?: string;
  initialResearchMode?: ResearchMode;
  initialConfig?: ResearchConfig;
}

export interface ModeCardInfo {
  mode: ResearchMode;
  title: string;
  description: string;
  features: string[];
  icon: string;
}

