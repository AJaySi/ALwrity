import { Step } from 'react-joyride';

export const productMarketingSteps: Step[] = [
  {
    target: 'body',
    content: 'Welcome! This short tour shows how to generate product assets fast.',
    disableBeacon: true,
    placement: 'center',
  },
  {
    target: '[data-tour="pm-recommendations"]',
    content: 'Personalized picks based on your onboarding—templates, platforms, and quick starts.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="pm-product-grid"]',
    content: 'Jump into product studios: animations, videos, and avatars tailored to your brand.',
    placement: 'top',
  },
  {
    target: '[data-tour="quick-actions"]',
    content: 'Quick actions to create a campaign or audit existing assets without extra steps.',
    placement: 'top',
  },
  {
    target: '[data-tour="active-campaigns"]',
    content: 'Track active campaigns and reopen proposals or assets from here.',
    placement: 'top',
  },
];
