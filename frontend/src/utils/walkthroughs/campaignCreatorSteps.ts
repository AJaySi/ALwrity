import { Step } from 'react-joyride';

export const campaignCreatorSteps: Step[] = [
  {
    target: 'body',
    content: 'Welcome to the Campaign Creator! Let’s cover the essentials in under a minute.',
    disableBeacon: true,
    placement: 'center',
  },
  {
    target: '[data-tour="cc-recommendations"]',
    content: 'Start with AI recommendations tailored to your industry, style, and platforms.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="cc-journeys"]',
    content: 'Pick a journey: launch a campaign, audit assets, or go straight to a studio.',
    placement: 'top',
  },
  {
    target: '[data-tour="quick-actions"]',
    content: 'Quick actions for creating campaigns or auditing existing assets.',
    placement: 'top',
  },
  {
    target: '[data-tour="active-campaigns"]',
    content: 'Monitor active campaigns and jump back into proposals or asset generation.',
    placement: 'top',
  },
];
