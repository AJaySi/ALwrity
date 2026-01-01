export type ModuleStatus = 'live' | 'beta' | 'coming soon';

export interface ModuleConfig {
  key: string;
  title: string;
  subtitle: string;
  description: string;
  highlights: string[];
  status: ModuleStatus;
  route: string;
  pricingNote?: string;
  eta?: string;
  icon?: React.ReactNode;
  help?: string;
  costDrivers?: string[];
}
