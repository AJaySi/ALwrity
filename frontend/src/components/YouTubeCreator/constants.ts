/**
 * Constants for YouTube Creator Studio
 */

export const YT_RED = '#FF0000';
export const YT_BG = '#f9f9f9';
export const YT_BORDER = '#e5e5e5';
export const YT_TEXT = '#0f0f0f';

export const STEPS = ['Plan Your Video', 'Review Scenes', 'Render Video'] as const;

export const RESOLUTIONS = ['480p', '720p', '1080p'] as const;
export type Resolution = typeof RESOLUTIONS[number];

export const DURATION_TYPES = ['shorts', 'medium', 'long'] as const;
export type DurationType = typeof DURATION_TYPES[number];

export const VIDEO_TYPES = [
  'tutorial',
  'review',
  'educational',
  'entertainment',
  'vlog',
  'product_demo',
  'reaction',
  'storytelling',
] as const;
export type VideoType = typeof VIDEO_TYPES[number];

export interface VideoTypeConfig {
  label: string;
  description: string;
  optimalDurations: DurationType[];
  typicalScenes: { min: number; max: number };
}

export const VIDEO_TYPE_CONFIGS: Record<VideoType, VideoTypeConfig> = {
  tutorial: {
    label: 'Tutorial / How-To',
    description: 'Step-by-step guides, instructions, and how-to content',
    optimalDurations: ['medium', 'long'],
    typicalScenes: { min: 3, max: 8 },
  },
  review: {
    label: 'Review / Unboxing',
    description: 'Product reviews, unboxings, and comparisons',
    optimalDurations: ['medium', 'long'],
    typicalScenes: { min: 4, max: 10 },
  },
  educational: {
    label: 'Educational / Explainer',
    description: 'Concept explanations, learning content, and educational videos',
    optimalDurations: ['medium', 'long'],
    typicalScenes: { min: 4, max: 12 },
  },
  entertainment: {
    label: 'Entertainment',
    description: 'Funny, engaging, viral content',
    optimalDurations: ['shorts', 'medium'],
    typicalScenes: { min: 3, max: 8 },
  },
  vlog: {
    label: 'Vlog / Personal',
    description: 'Personal storytelling, daily experiences, and vlogs',
    optimalDurations: ['medium', 'long'],
    typicalScenes: { min: 5, max: 15 },
  },
  product_demo: {
    label: 'Product Demo / Commercial',
    description: 'Product showcases, demos, and sales-focused content',
    optimalDurations: ['shorts', 'medium'],
    typicalScenes: { min: 3, max: 7 },
  },
  reaction: {
    label: 'Reaction / Commentary',
    description: 'Reaction videos, commentary, and responses to content',
    optimalDurations: ['medium', 'long'],
    typicalScenes: { min: 4, max: 12 },
  },
  storytelling: {
    label: 'Storytelling / Documentary',
    description: 'Narrative-driven content, documentaries, and stories',
    optimalDurations: ['long'],
    typicalScenes: { min: 6, max: 20 },
  },
};

// Target Audience Options
export interface TargetAudienceOption {
  value: string;
  label: string;
  description: string;
}

export const TARGET_AUDIENCE_OPTIONS: TargetAudienceOption[] = [
  {
    value: 'tech_professionals',
    label: 'Tech Professionals',
    description: 'Developers, engineers, IT professionals aged 25-45',
  },
  {
    value: 'business_owners',
    label: 'Business Owners & Entrepreneurs',
    description: 'Small business owners, startups, entrepreneurs',
  },
  {
    value: 'students',
    label: 'Students & Learners',
    description: 'High school, college students, lifelong learners',
  },
  {
    value: 'parents',
    label: 'Parents & Families',
    description: 'Parents with children, family-oriented content',
  },
  {
    value: 'creators',
    label: 'Content Creators',
    description: 'YouTubers, streamers, social media creators',
  },
  {
    value: 'fitness_enthusiasts',
    label: 'Fitness & Health Enthusiasts',
    description: 'Gym-goers, athletes, health-conscious individuals',
  },
  {
    value: 'gamers',
    label: 'Gamers',
    description: 'Gaming enthusiasts, esports fans',
  },
  {
    value: 'travelers',
    label: 'Travelers & Adventurers',
    description: 'Travel enthusiasts, adventure seekers',
  },
  {
    value: 'foodies',
    label: 'Food Enthusiasts',
    description: 'Cooking enthusiasts, food lovers, home chefs',
  },
  {
    value: 'fashion_style',
    label: 'Fashion & Style',
    description: 'Fashion-conscious individuals, style enthusiasts',
  },
];

// Video Goal Options
export interface VideoGoalOption {
  value: string;
  label: string;
  description: string;
}

export const VIDEO_GOAL_OPTIONS: VideoGoalOption[] = [
  {
    value: 'educate',
    label: 'Educate & Inform',
    description: 'Teach concepts, explain topics, share knowledge',
  },
  {
    value: 'entertain',
    label: 'Entertain & Engage',
    description: 'Make viewers laugh, keep them engaged, build audience',
  },
  {
    value: 'sell',
    label: 'Drive Sales & Conversions',
    description: 'Promote products, drive purchases, generate leads',
  },
  {
    value: 'build_brand',
    label: 'Build Brand Awareness',
    description: 'Increase visibility, establish authority, grow recognition',
  },
  {
    value: 'grow_subscribers',
    label: 'Grow Subscribers',
    description: 'Attract new subscribers, build community',
  },
  {
    value: 'increase_views',
    label: 'Maximize Views & Reach',
    description: 'Boost watch time, improve algorithm ranking',
  },
  {
    value: 'inspire',
    label: 'Inspire & Motivate',
    description: 'Motivate action, share success stories, inspire change',
  },
  {
    value: 'document',
    label: 'Document & Share',
    description: 'Share experiences, document processes, create memories',
  },
];

// Brand Style Options
export interface BrandStyleOption {
  value: string;
  label: string;
  description: string;
}

export const BRAND_STYLE_OPTIONS: BrandStyleOption[] = [
  {
    value: 'modern_minimalist',
    label: 'Modern Minimalist',
    description: 'Clean, simple, tech-forward aesthetic',
  },
  {
    value: 'energetic_vibrant',
    label: 'Energetic & Vibrant',
    description: 'Colorful, dynamic, high-energy visuals',
  },
  {
    value: 'professional_polished',
    label: 'Professional & Polished',
    description: 'Corporate, trustworthy, refined style',
  },
  {
    value: 'warm_friendly',
    label: 'Warm & Friendly',
    description: 'Approachable, inviting, personable feel',
  },
  {
    value: 'bold_edgy',
    label: 'Bold & Edgy',
    description: 'Daring, unconventional, attention-grabbing',
  },
  {
    value: 'natural_organic',
    label: 'Natural & Organic',
    description: 'Earth tones, authentic, unpolished',
  },
  {
    value: 'luxury_premium',
    label: 'Luxury & Premium',
    description: 'High-end, sophisticated, exclusive',
  },
  {
    value: 'playful_fun',
    label: 'Playful & Fun',
    description: 'Lighthearted, whimsical, entertaining',
  },
];

export const POLLING_INTERVAL_MS = 2000; // 2 seconds
