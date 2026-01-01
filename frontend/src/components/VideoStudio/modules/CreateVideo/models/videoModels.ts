/**
 * Video Model Information for Content Creators
 * 
 * Non-technical, creator-focused descriptions to help users choose the right AI model
 * for their video generation needs.
 */

export interface VideoModelInfo {
  id: string;
  name: string;
  tagline: string;
  description: string;
  bestFor: string[];
  strengths: string[];
  limitations: string[];
  durations: number[];
  resolutions: string[];
  aspectRatios: string[];
  audioSupport: boolean;
  costPerSecond: {
    [resolution: string]: number;
  };
  exampleUseCases: string[];
  tips: string[];
  icon?: string;
}

export const VIDEO_MODELS: VideoModelInfo[] = [
  {
    id: 'hunyuan-video-1.5',
    name: 'HunyuanVideo 1.5',
    tagline: 'Lightweight & Fast - Perfect for Quick Content',
    description: 'A lightweight model that generates high-quality videos quickly. Great for social media content, quick iterations, and when you need fast results without breaking the bank.',
    bestFor: [
      'Instagram Reels & Stories',
      'TikTok videos',
      'Quick social media content',
      'Testing ideas and concepts',
      'Budget-conscious creators'
    ],
    strengths: [
      'Fast generation time',
      'Affordable pricing',
      'Good motion quality',
      'Works well for short clips',
      'Great for testing prompts'
    ],
    limitations: [
      'Limited to 5-10 second videos',
      'Only 480p or 720p resolution',
      'No audio generation',
      'Best for shorter content'
    ],
    durations: [5, 8, 10],
    resolutions: ['480p', '720p'],
    aspectRatios: ['16:9', '9:16'],
    audioSupport: false,
    costPerSecond: {
      '480p': 0.02,
      '720p': 0.04,
    },
    exampleUseCases: [
      'Quick product showcases for social media',
      'Story highlights and behind-the-scenes',
      'Fast-paced social media content',
      'Testing video concepts before production'
    ],
    tips: [
      'Use for 5-8 second clips for best results',
      'Describe motion and camera movement clearly',
      'Mention style and mood in your prompt',
      'Perfect for Instagram and TikTok content'
    ],
  },
  {
    id: 'lightricks/ltx-2-pro',
    name: 'LTX-2 Pro',
    tagline: 'Production Quality with Synchronized Audio',
    description: 'Professional-grade video generation with perfectly synchronized audio. Designed for real production workflows where quality and audio-video sync matter. Creates cinematic scenes with matching sound.',
    bestFor: [
      'YouTube videos',
      'Professional marketing content',
      'Music videos',
      'Film previsualization',
      'Advertising campaigns',
      'Production workflows'
    ],
    strengths: [
      'Synchronized audio generation',
      'Cinematic quality',
      'Perfect audio-video sync',
      'Production-ready output',
      '1080p native resolution',
      'Great for longer content (6-10s)'
    ],
    limitations: [
      'Fixed at 1080p (no lower resolutions)',
      'Higher cost per second',
      'Longer generation time',
      'Only 6-10 second durations'
    ],
    durations: [6, 8, 10],
    resolutions: ['1080p'],
    aspectRatios: ['16:9', '9:16'],
    audioSupport: true,
    costPerSecond: {
      '1080p': 0.06,
    },
    exampleUseCases: [
      'YouTube video intros and outros',
      'Product launch videos with music',
      'Music video sequences',
      'Professional marketing clips',
      'Film storyboard visualization'
    ],
    tips: [
      'Describe camera movements and scene composition',
      'Mention emotional tone and atmosphere',
      'Audio is automatically generated to match motion',
      'Best for 6-8 second clips for optimal quality',
      'Perfect for professional content creation'
    ],
  },
  {
    id: 'google/veo3.1',
    name: 'Google Veo 3.1',
    tagline: 'High-Quality with Flexible Options',
    description: 'Google\'s advanced video generation model that creates high-quality videos with synchronized audio. Offers flexible resolution and aspect ratio options, perfect for various content platforms.',
    bestFor: [
      'YouTube content',
      'Professional presentations',
      'Multi-platform content',
      'High-quality social media',
      'Content requiring flexibility'
    ],
    strengths: [
      '720p and 1080p options',
      'Synchronized audio generation',
      'Negative prompt support',
      'Seed control for consistency',
      'Flexible aspect ratios',
      'High visual quality'
    ],
    limitations: [
      'Shorter duration options (4-8s)',
      'Higher cost for 1080p',
      'No 480p option'
    ],
    durations: [4, 6, 8],
    resolutions: ['720p', '1080p'],
    aspectRatios: ['16:9', '9:16'],
    audioSupport: true,
    costPerSecond: {
      '720p': 0.08,
      '1080p': 0.12,
    },
    exampleUseCases: [
      'YouTube Shorts and regular videos',
      'Professional social media content',
      'Multi-platform content creation',
      'High-quality product showcases',
      'Content requiring specific aspect ratios'
    ],
    tips: [
      'Use negative prompts to exclude unwanted elements',
      'Use seed values to create consistent variations',
      '720p is great for social media, 1080p for YouTube',
      'Describe scenes with clear visual details',
      'Audio automatically matches video motion'
    ],
  },
];

/**
 * Get model information by ID
 */
export function getModelInfo(modelId: string): VideoModelInfo | undefined {
  return VIDEO_MODELS.find(m => m.id === modelId);
}

/**
 * Get recommended model based on use case
 */
export function getRecommendedModel(useCase: string): VideoModelInfo | undefined {
  const useCaseLower = useCase.toLowerCase();
  
  if (useCaseLower.includes('social') || useCaseLower.includes('instagram') || useCaseLower.includes('tiktok')) {
    return VIDEO_MODELS.find(m => m.id === 'hunyuan-video-1.5');
  }
  
  if (useCaseLower.includes('youtube') || useCaseLower.includes('professional') || useCaseLower.includes('production')) {
    return VIDEO_MODELS.find(m => m.id === 'lightricks/ltx-2-pro');
  }
  
  if (useCaseLower.includes('flexible') || useCaseLower.includes('multi-platform')) {
    return VIDEO_MODELS.find(m => m.id === 'google/veo3.1');
  }
  
  return VIDEO_MODELS[0]; // Default to first model
}

/**
 * Compare models side by side
 */
export function compareModels(modelIds: string[]): VideoModelInfo[] {
  return VIDEO_MODELS.filter(m => modelIds.includes(m.id));
}
