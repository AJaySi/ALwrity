import type { MotionPreset, AspectPreset } from './types';

export const motionPresets: readonly MotionPreset[] = ['Subtle', 'Medium', 'Dynamic'] as const;
export const aspectPresets: readonly AspectPreset[] = ['9:16', '1:1', '16:9'] as const;

// Example prompts for content creators
export const examplePrompts = [
  'A modern coffee shop interior with baristas crafting latte art, warm golden hour lighting streaming through large windows, customers chatting at wooden tables, cozy atmosphere, perfect for Instagram Reels',
  'Professional workspace with laptop, notebook, and coffee cup on a minimalist desk, soft natural lighting, clean modern office environment, ideal for LinkedIn posts',
  'Dynamic product showcase with rotating view, vibrant colors, smooth camera movement, energetic music vibe, perfect for YouTube Shorts and product demos',
];

export const exampleNegativePrompts = [
  'blurry, low quality, distorted faces, text overlays',
  'grainy footage, poor lighting, shaky camera, watermark',
  'unprofessional, cluttered background, bad composition',
];

// Input styles
export const inputStyles = {
  outlinedInputBase: {
    borderRadius: 2,
    backgroundColor: '#fff',
    '& fieldset': { borderColor: '#e2e8f0' },
    '&:hover fieldset': { borderColor: '#cbd5f5' },
    '&.Mui-focused fieldset': {
      borderColor: '#7c3aed',
      boxShadow: '0 0 0 3px rgba(124, 58, 237, 0.15)',
    },
  },
  inputLabel: {
    color: '#475569',
    fontWeight: 600,
  },
};

// Color constants
export const colors = {
  primary: '#0f172a',
  muted: '#475569',
  accent: '#667eea',
  accentSecondary: '#764ba2',
};
