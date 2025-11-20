import React from 'react';

export type ModuleStatus = 'live' | 'coming soon' | 'planning';

export type ModuleConfig = {
  key: string;
  title: string;
  subtitle: string;
  description: string;
  highlights: string[];
  status: ModuleStatus;
  route?: string;
  icon: React.ReactNode;
  help: string;
  pricing: {
    estimate: string;
    notes: string;
  };
  example: {
    title: string;
    steps: string[];
    eta: string;
  };
};

