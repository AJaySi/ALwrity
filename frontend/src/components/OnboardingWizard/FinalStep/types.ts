export interface OnboardingData {
  apiKeys: Record<string, string>;
  websiteUrl?: string;
  researchPreferences?: any;
  personalizationSettings?: any;
  integrations?: any;
  styleAnalysis?: any;
}

export interface Capability {
  id: string;
  title: string;
  description: string;
  icon: React.ReactElement;
  unlocked: boolean;
  required?: string[];
}

export interface FinalStepProps {
  onContinue: () => void;
  updateHeaderContent: (content: { title: string; description: string }) => void;
}
