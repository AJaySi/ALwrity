import React from 'react';
import MovieCreationIcon from '@mui/icons-material/MovieCreation';
import FaceRetouchingNaturalIcon from '@mui/icons-material/FaceRetouchingNatural';
import EditIcon from '@mui/icons-material/Edit';
import HighQualityIcon from '@mui/icons-material/HighQuality';
import TimelineIcon from '@mui/icons-material/Timeline';
import TransformIcon from '@mui/icons-material/Transform';
import ShareIcon from '@mui/icons-material/Share';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import TranslateIcon from '@mui/icons-material/Translate';
import WallpaperIcon from '@mui/icons-material/Wallpaper';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import type { ModuleConfig } from './types';
import type { AIModel, PerfectForUseCase, CostDetail } from './InfoModal';

export const statusStyles = {
  live: { label: 'Live', color: '#10b981' },
  beta: { label: 'Beta', color: '#3b82f6' },
  'coming soon': { label: 'Coming Soon', color: '#f97316' },
};

export const videoStudioModules: ModuleConfig[] = [
  {
    key: 'create',
    title: 'Create Studio',
    subtitle: 'Turn your ideas into videos',
    description:
      'Transform text descriptions into engaging video content instantly. Perfect for content creators producing daily social media content, marketers creating campaign videos, and businesses generating product showcases. Supports text-to-video and image-to-video with automatic platform optimization for Instagram Reels, TikTok, YouTube Shorts, and LinkedIn.',
    highlights: ['Text to Video', 'Image to Video', 'Auto Platform Optimization'],
    status: 'live',
    route: '/video-studio/create',
    pricingNote: 'Cost depends on video length and quality. We show you the exact price before generating. Typical range: $0.50-$1.50 per video.',
    eta: 'Now',
    icon: <MovieCreationIcon />,
    help: 'Perfect for content creators producing daily social media content, marketers creating campaign videos, and businesses generating product showcases. Just describe your video idea (e.g., "A modern coffee shop with baristas crafting latte art") and we create it with optimal settings for your chosen platform. Add background music or voiceover in post-production.',
    costDrivers: ['Video duration (5–15 seconds recommended)', 'Resolution (480p/720p/1080p)', 'Platform format (9:16, 16:9, 1:1)'],
    perfectFor: [
      {
        title: 'Content Creators',
        description: 'Produce daily social media content for Instagram Reels, TikTok, and YouTube Shorts. Create engaging videos from simple text descriptions without video editing skills.',
        examples: ['Instagram Reels', 'TikTok Videos', 'YouTube Shorts', 'Daily Content'],
      },
      {
        title: 'Digital Marketers',
        description: 'Create campaign videos, product showcases, and promotional content quickly. Generate multiple variations for A/B testing and multi-platform campaigns.',
        examples: ['Campaign Videos', 'Product Showcases', 'Social Media Ads', 'A/B Testing'],
      },
      {
        title: 'Businesses',
        description: 'Generate professional product videos, explainer content, and brand storytelling videos. Perfect for e-commerce, SaaS, and service businesses.',
        examples: ['Product Demos', 'Explainer Videos', 'Brand Content', 'E-commerce'],
      },
    ],
    costDetails: {
      factors: [
        'Video duration: 5-15 seconds recommended for optimal cost',
        'Resolution: 480p ($0.50), 720p ($0.75), 1080p ($1.00+)',
        'Platform format: Auto-optimized for Instagram, TikTok, YouTube, LinkedIn',
        'Provider selection: Auto-selects best model based on requirements',
      ],
      typicalRange: '$0.50 - $1.50 per video',
      examples: [
        { scenario: '5-second Instagram Reel (720p)', cost: '$0.50' },
        { scenario: '10-second TikTok video (1080p)', cost: '$1.00' },
        { scenario: '15-second LinkedIn post (1080p)', cost: '$1.50' },
      ],
    },
    aiModels: [
      {
        name: 'WAN 2.5',
        provider: 'WaveSpeed AI',
        capabilities: ['Text-to-Video', 'Image-to-Video', 'High Quality', 'Fast Generation'],
        pricing: {
          model: 'per_second',
          rate: 0.05,
          unit: '/second',
          description: '$0.05 per second (minimum 5 seconds, typical 5-15 seconds)',
        },
        features: [
          'Best for short-form social media content',
          'Automatic platform optimization',
          'Motion and style control',
          'High-quality output ready for social platforms',
        ],
      },
      {
        name: 'Seedance 1.5 Pro',
        provider: 'WaveSpeed AI',
        capabilities: ['Text-to-Video', 'Longer Duration', 'Professional Quality'],
        pricing: {
          model: 'per_second',
          rate: 0.08,
          unit: '/second',
          description: '$0.08 per second (best for 10-30 second videos)',
        },
        features: [
          'Ideal for longer-form content',
          'Professional-grade quality',
          'Better motion continuity',
          'Suitable for YouTube and LinkedIn',
        ],
      },
    ],
  },
  {
    key: 'avatar',
    title: 'Avatar Studio',
    subtitle: 'Create talking videos from photos',
    description:
      'Transform static photos into dynamic talking videos with perfect lip-sync. Ideal for content creators building personal brands, marketers creating personalized campaigns, and businesses producing explainer videos. Upload a photo and audio to generate professional talking avatars that engage audiences across social platforms.',
    highlights: ['Talking Avatars', 'Perfect Lip-sync', 'Multi-language Support'],
    status: 'beta',
    route: '/video-studio/avatar',
    pricingNote: 'Cost depends on video length and quality. Perfect for short-form content (5-30 seconds)',
    eta: 'Beta',
    icon: <FaceRetouchingNaturalIcon />,
    help: 'Perfect for content creators building personal brands, marketers creating personalized video campaigns, and businesses producing explainer videos. Upload your photo and audio, and we create a talking video with perfect lip-sync. Great for Instagram Reels, LinkedIn videos, YouTube intros, and personalized customer messages.',
    costDrivers: ['Video duration (seconds)', 'Resolution (480p/720p/1080p)'],
    perfectFor: [
      {
        title: 'Personal Branding',
        description: 'Build your personal brand with talking avatar videos. Perfect for content creators, coaches, and thought leaders who want to create engaging video content without appearing on camera.',
        examples: ['YouTube Intros', 'Instagram Reels', 'LinkedIn Videos', 'Personal Branding'],
      },
      {
        title: 'Marketing Campaigns',
        description: 'Create personalized video messages for customers, product explainers, and campaign videos. Scale personalized video content without hiring actors or video production teams.',
        examples: ['Customer Messages', 'Product Explainer', 'Campaign Videos', 'Personalization'],
      },
      {
        title: 'Business Content',
        description: 'Produce professional explainer videos, training content, and corporate communications. Transform static presentations into dynamic talking videos.',
        examples: ['Explainer Videos', 'Training Content', 'Corporate Communications', 'E-learning'],
      },
    ],
    costDetails: {
      factors: [
        'Video duration: 5-30 seconds recommended',
        'Resolution: 480p ($0.20), 720p ($0.40), 1080p ($0.60+)',
        'Audio length determines video duration',
        'Perfect lip-sync quality across all resolutions',
      ],
      typicalRange: '$0.20 - $0.60 per video',
      examples: [
        { scenario: '10-second talking avatar (720p)', cost: '$0.40' },
        { scenario: '20-second explainer video (1080p)', cost: '$0.60' },
        { scenario: '30-second personalized message (720p)', cost: '$0.60' },
      ],
    },
    aiModels: [
      {
        name: 'Hunyuan Avatar',
        provider: 'Tencent',
        capabilities: ['Talking Avatars', 'Perfect Lip-sync', 'Natural Expressions'],
        pricing: {
          model: 'per_second',
          rate: 0.02,
          unit: '/second',
          description: '$0.02 per second (minimum 5 seconds)',
        },
        features: [
          'Industry-leading lip-sync accuracy',
          'Natural facial expressions and movements',
          'Supports multiple languages',
          'High-quality output for professional use',
        ],
      },
    ],
  },
  {
    key: 'enhance',
    title: 'Enhance Studio',
    subtitle: 'Upgrade your video quality',
    description:
      'Transform low-resolution videos into professional-quality content. Upscale from 480p to 1080p or 4K, boost frame rate from 24fps to 60fps, and dramatically improve clarity. Essential for content creators upgrading phone footage, marketers repurposing old content, and businesses preparing videos for professional presentations.',
    highlights: ['AI Upscaling', 'Frame Rate Boost', 'Professional Quality'],
    status: 'live',
    route: '/video-studio/enhance',
    pricingNote: 'Cost depends on original quality and target quality. FlashVSR AI model provides best results',
    eta: 'Now',
    icon: <HighQualityIcon />,
    help: 'Perfect for content creators upgrading phone footage to professional quality, marketers repurposing old content for new campaigns, and businesses preparing videos for presentations. Transform 480p phone videos into 1080p professional content ready for YouTube, LinkedIn, and marketing materials. FlashVSR AI model ensures superior upscaling with motion preservation.',
    costDrivers: ['Original resolution', 'Target resolution (1080p/4K)', 'Video duration'],
    perfectFor: [
      {
        title: 'Content Upgrading',
        description: 'Upgrade phone footage to professional quality. Transform 480p videos shot on mobile devices into 1080p content ready for YouTube, LinkedIn, and marketing materials.',
        examples: ['Phone to Professional', 'YouTube Ready', 'LinkedIn Quality', 'Marketing Materials'],
      },
      {
        title: 'Content Repurposing',
        description: 'Repurpose old content for new campaigns. Enhance archived videos, upgrade legacy content, and breathe new life into existing video assets.',
        examples: ['Archive Enhancement', 'Legacy Content', 'Campaign Repurposing', 'Asset Upgrading'],
      },
      {
        title: 'Professional Presentations',
        description: 'Prepare videos for professional presentations, client deliverables, and corporate communications. Ensure consistent quality across all video assets.',
        examples: ['Client Deliverables', 'Corporate Videos', 'Presentations', 'Professional Quality'],
      },
    ],
    costDetails: {
      factors: [
        'Original resolution: Lower resolution = higher upscaling cost',
        'Target resolution: 1080p ($0.10/s), 4K ($0.20/s)',
        'Video duration: Cost scales with video length',
        'Frame rate boost: Additional cost for 60fps conversion',
      ],
      typicalRange: '$0.10 - $0.20 per second',
      examples: [
        { scenario: '480p to 1080p (10 seconds)', cost: '$1.00' },
        { scenario: '720p to 4K (15 seconds)', cost: '$3.00' },
        { scenario: '1080p to 4K with 60fps (20 seconds)', cost: '$4.00' },
      ],
    },
    aiModels: [
      {
        name: 'FlashVSR',
        provider: 'WaveSpeed AI',
        capabilities: ['Video Upscaling', 'Motion Preservation', 'Quality Enhancement'],
        pricing: {
          model: 'per_second',
          rate: 0.10,
          unit: '/second',
          description: '$0.10 per second for 1080p, $0.20 per second for 4K',
        },
        features: [
          'Superior upscaling with motion preservation',
          'Maintains video quality and details',
          'Supports up to 4K resolution',
          'Frame rate boost to 60fps available',
        ],
      },
    ],
  },
  {
    key: 'extend',
    title: 'Extend Studio',
    subtitle: 'Extend short clips seamlessly',
    description:
      'Turn short video clips into longer videos with seamless motion and audio continuity. Perfect for extending social media content, creating longer scenes from existing footage, and adding smooth transitions.',
    highlights: ['Motion Continuity', 'Audio Sync', 'Seamless Extension'],
    status: 'live',
    route: '/video-studio/extend',
    pricingNote: 'Cost depends on extension duration and resolution',
    eta: 'Now',
    icon: <TimelineIcon />,
    help: 'Great for extending short clips into longer videos. Describe how you want the video to continue, and we create a seamless extension with preserved motion and style.',
    costDrivers: ['Extension duration', 'Resolution', 'Video length'],
  },
  {
    key: 'edit',
    title: 'Edit Studio',
    subtitle: 'Trim, speed control, and stabilization',
    description:
      'Free video editing using FFmpeg: trim/cut to time range, slow motion or fast forward (0.25x–4x), and camera stabilization with vidstab. Perfect for polishing social clips and fixing shaky footage.',
    highlights: ['Trim & Cut', 'Speed Control', 'Stabilization'],
    status: 'live',
    route: '/video-studio/edit',
    pricingNote: 'Free (FFmpeg processing)',
    eta: 'Now',
    icon: <EditIcon />,
    help: 'Free editing operations: Trim video to specific time range, adjust playback speed (slow motion or fast forward), and stabilize shaky footage. More features coming soon!',
    costDrivers: ['Free - no cost'],
    perfectFor: [
      {
        title: 'Content Polishing',
        description: 'Polish your social media content with professional editing tools. Trim unwanted sections, adjust speed for dramatic effect, and stabilize shaky footage.',
        examples: ['Social Media', 'Content Polishing', 'Quick Edits', 'Post-Production'],
      },
      {
        title: 'Video Optimization',
        description: 'Optimize videos for different platforms. Trim to platform-specific durations, adjust speed for engagement, and fix camera shake.',
        examples: ['Platform Optimization', 'Duration Control', 'Speed Adjustment', 'Quality Fix'],
      },
    ],
    costDetails: {
      factors: ['All operations are free', 'No cost for trim, speed, or stabilization', 'FFmpeg-based processing', 'Unlimited usage'],
      typicalRange: 'Free',
      examples: [
        { scenario: 'Trim 10-second clip', cost: 'Free' },
        { scenario: 'Speed adjustment (2x)', cost: 'Free' },
        { scenario: 'Stabilize shaky footage', cost: 'Free' },
      ],
    },
    aiModels: [
      {
        name: 'FFmpeg',
        provider: 'Open Source',
        capabilities: ['Video Editing', 'Trim & Cut', 'Speed Control', 'Stabilization'],
        pricing: {
          model: 'free',
          description: 'Free - No cost for all operations',
        },
        features: [
          'Professional-grade video editing',
          'Trim and cut to precise time ranges',
          'Speed control from 0.25x to 4x',
          'Camera stabilization with vidstab',
          'Text overlay and audio controls',
        ],
      },
    ],
  },
  {
    key: 'transform',
    title: 'Transform Studio',
    subtitle: 'Change format and style',
    description:
      'Convert videos between different formats (MP4, MOV, WebM, GIF), change aspect ratios (16:9, 9:16, 1:1), adjust speed, scale resolution, and compress files. All transformations use fast FFmpeg processing.',
    highlights: ['Format Conversion', 'Aspect Ratio', 'Speed Control', 'Resolution Scaling', 'Compression'],
    status: 'live',
    route: '/video-studio/transform',
    pricingNote: 'Free (FFmpeg processing)',
    eta: 'Now',
    icon: <TransformIcon />,
    help: 'Perfect for adapting one video for multiple platforms. Convert formats, change aspect ratios, adjust speed, scale resolution, and compress files - all for free using FFmpeg.',
    costDrivers: ['Free processing'],
  },
  {
    key: 'social',
    title: 'Social Optimizer',
    subtitle: 'One-click platform optimization',
    description:
      'Create optimized versions of your video for Instagram, TikTok, YouTube, LinkedIn, and Twitter with one click. Includes safe zones, compression, and thumbnails. Make your content platform-ready instantly.',
    highlights: ['Multi-Platform', 'Safe Zones', 'Auto Thumbnails'],
    status: 'live',
    route: '/video-studio/social',
    pricingNote: 'Free (FFmpeg processing)',
    eta: 'Now',
    icon: <ShareIcon />,
    help: 'Save time by creating platform-optimized versions automatically. One video, multiple platforms, perfect formatting for each.',
    costDrivers: ['Free processing'],
  },
  {
    key: 'faceswap',
    title: 'Face Swap Studio',
    subtitle: 'Replace characters in videos',
    description:
      'Swap faces or characters in videos using MoCha AI. Upload a reference image and source video to seamlessly replace characters while preserving motion, emotion, and camera perspective.',
    highlights: ['Character Replacement', 'Motion Preservation', 'Identity Consistency'],
    status: 'live',
    route: '/video-studio/face-swap',
    pricingNote: '$0.04/s (480p) or $0.08/s (720p), min 5s charge',
    eta: 'Now',
    icon: <SwapHorizIcon />,
    help: 'Perfect for film, advertising, digital avatars, and creative character transformation. No pose or depth maps needed.',
    costDrivers: ['Video duration', 'Resolution (480p/720p)'],
  },
  {
    key: 'video-translate',
    title: 'Video Translate Studio',
    subtitle: 'Translate videos to 70+ languages',
    description:
      'Translate videos to 70+ languages and 175+ dialects with AI. Preserves lip-sync and natural voice. Perfect for global content, localization, and reaching international audiences.',
    highlights: ['70+ Languages', 'Lip-sync Preservation', 'Natural Voice'],
    status: 'live',
    route: '/video-studio/video-translate',
    pricingNote: '$0.0375/second',
    eta: 'Now',
    icon: <TranslateIcon />,
    help: 'Perfect for global content creators, localization, and reaching international audiences. No voice actors or dubbing needed.',
    costDrivers: ['Video duration'],
    perfectFor: [
      {
        title: 'Global Content',
        description: 'Reach international audiences with translated video content. Perfect for content creators expanding to new markets and businesses going global.',
        examples: ['International Marketing', 'Global Expansion', 'Multi-market Content', 'Localization'],
      },
      {
        title: 'Localization',
        description: 'Localize video content for different regions and languages. Maintain brand voice and messaging across all markets without hiring voice actors.',
        examples: ['Content Localization', 'Regional Adaptation', 'Brand Consistency', 'Market Entry'],
      },
      {
        title: 'Accessibility',
        description: 'Make content accessible to diverse audiences. Translate educational content, tutorials, and informational videos to multiple languages.',
        examples: ['Educational Content', 'Tutorials', 'Accessibility', 'Inclusive Content'],
      },
    ],
    costDetails: {
      factors: [
        'Video duration: Cost scales with video length',
        'Language selection: All 70+ languages same price',
        'Lip-sync preservation: Automatic and included',
        'Natural voice: AI-generated voices maintain quality',
      ],
      typicalRange: '$0.19 - $0.75 per video',
      examples: [
        { scenario: '5-second video translation', cost: '$0.19' },
        { scenario: '10-second video translation', cost: '$0.38' },
        { scenario: '20-second video translation', cost: '$0.75' },
      ],
    },
    aiModels: [
      {
        name: 'HeyGen Video Translate',
        provider: 'HeyGen',
        capabilities: ['Video Translation', 'Lip-sync Preservation', '70+ Languages', 'Natural Voice'],
        pricing: {
          model: 'per_second',
          rate: 0.0375,
          unit: '/second',
          description: '$0.0375 per second (70+ languages, 175+ dialects)',
        },
        features: [
          'Translates to 70+ languages and 175+ dialects',
          'Preserves perfect lip-sync',
          'Natural-sounding AI voices',
          'No voice actors or dubbing needed',
          'Maintains original emotion and tone',
        ],
      },
    ],
  },
  {
    key: 'video-background-remover',
    title: 'Background Remover Studio',
    subtitle: 'Remove or replace video backgrounds',
    description:
      'Remove or replace video backgrounds with clean matting and edge-aware blending. Upload a background image to replace, or leave empty for transparent background. Perfect for product videos, presentations, and creative content.',
    highlights: ['Clean Matting', 'Edge-Aware Blending', 'Background Replacement'],
    status: 'live',
    route: '/video-studio/video-background-remover',
    pricingNote: '$0.01/second (min $0.05, max $6.00)',
    eta: 'Now',
    icon: <WallpaperIcon />,
    help: 'Perfect for product videos, presentations, and creative content. Remove backgrounds or replace them with custom images.',
    costDrivers: ['Video duration'],
    perfectFor: [
      {
        title: 'Product Videos',
        description: 'Create professional product videos with clean backgrounds. Remove distracting backgrounds or replace with branded environments for e-commerce and marketing.',
        examples: ['E-commerce', 'Product Showcase', 'Marketing Videos', 'Branded Content'],
      },
      {
        title: 'Presentations',
        description: 'Prepare videos for presentations and corporate communications. Remove backgrounds for clean, professional look or replace with branded backgrounds.',
        examples: ['Corporate Videos', 'Presentations', 'Professional Content', 'Business Communications'],
      },
      {
        title: 'Creative Content',
        description: 'Create creative video content with custom backgrounds. Perfect for social media, advertising, and artistic projects.',
        examples: ['Social Media', 'Advertising', 'Creative Projects', 'Visual Effects'],
      },
    ],
    costDetails: {
      factors: [
        'Video duration: $0.01 per second',
        'Minimum charge: $0.05 for videos ≤5 seconds',
        'Maximum charge: $6.00 for videos up to 600 seconds',
        'Background replacement: Same price as removal',
      ],
      typicalRange: '$0.05 - $1.00 per video',
      examples: [
        { scenario: '5-second background removal', cost: '$0.05' },
        { scenario: '10-second background replacement', cost: '$0.10' },
        { scenario: '30-second product video', cost: '$0.30' },
      ],
    },
    aiModels: [
      {
        name: 'Video Background Remover',
        provider: 'WaveSpeed AI',
        capabilities: ['Background Removal', 'Background Replacement', 'Clean Matting', 'Edge-Aware Blending'],
        pricing: {
          model: 'per_second',
          rate: 0.01,
          unit: '/second',
          min: 0.05,
          max: 6.00,
          description: '$0.01 per second (min $0.05, max $6.00)',
        },
        features: [
          'Automatic background detection and removal',
          'Clean matting with edge-aware blending',
          'Custom background replacement support',
          'Transparent background option',
          'Production-ready quality output',
        ],
      },
    ],
  },
  {
    key: 'add-audio-to-video',
    title: 'Add Audio to Video Studio',
    subtitle: 'Generate realistic Foley and ambient audio',
    description:
      'Generate realistic Foley and ambient audio directly from video using AI. Choose between Hunyuan Video Foley (48 kHz hi-fi, multi-scene sync) or Think Sound (context-aware, flat rate pricing). Perfect for post-production, social content, and prototyping.',
    highlights: ['2 AI Models', '48 kHz Hi-Fi', 'Context-Aware'],
    status: 'live',
    route: '/video-studio/add-audio-to-video',
    pricingNote: '$0.02/s (Hunyuan) or $0.05/video (Think Sound)',
    eta: 'Now',
    icon: <MusicNoteIcon />,
    help: 'Perfect for post-production, social content, and prototyping. Use optional text prompts to guide specific sounds or let AI automatically generate appropriate audio based on visual cues.',
    costDrivers: ['Video duration'],
    perfectFor: [
      {
        title: 'Post-Production',
        description: 'Add professional Foley and ambient audio to videos. Perfect for film, animation, and video production workflows.',
        examples: ['Film Production', 'Animation', 'Video Production', 'Post-Production'],
      },
      {
        title: 'Social Content',
        description: 'Generate audio for social media content. Create engaging audio tracks for silent footage or enhance existing videos.',
        examples: ['Social Media', 'Content Creation', 'Silent Footage', 'Audio Enhancement'],
      },
    ],
    costDetails: {
      factors: [
        'Model selection: Hunyuan (per-second) or Think Sound (flat rate)',
        'Video duration: Longer videos cost more with Hunyuan',
        'Audio quality: 48 kHz hi-fi output',
        'Optional text prompts for sound guidance',
      ],
      typicalRange: '$0.05 - $0.20 per video',
      examples: [
        { scenario: '5-second video (Hunyuan)', cost: '$0.10' },
        { scenario: '10-second video (Think Sound)', cost: '$0.05' },
        { scenario: '15-second video (Hunyuan)', cost: '$0.30' },
      ],
    },
    aiModels: [
      {
        name: 'Hunyuan Video Foley',
        provider: 'Tencent',
        capabilities: ['Foley Generation', '48 kHz Hi-Fi', 'Multi-Scene Sync'],
        pricing: {
          model: 'per_second',
          rate: 0.02,
          unit: '/second',
          description: '$0.02 per second (48 kHz hi-fi output)',
        },
        features: [
          '48 kHz hi-fi audio quality',
          'Multi-scene synchronization',
          'Timing-accurate audio tracks',
          'Optional text prompt control',
        ],
      },
      {
        name: 'Think Sound',
        provider: 'WaveSpeed AI',
        capabilities: ['Context-Aware Audio', 'Prompt-Guided', 'Flat Rate'],
        pricing: {
          model: 'flat_rate',
          rate: 0.05,
          description: '$0.05 per video (flat rate, any duration)',
        },
        features: [
          'Context-aware sound generation',
          'Built-in prompt enhancer',
          'Flat rate pricing (any duration)',
          'Best for consistent pricing',
        ],
      },
    ],
  },
  {
    key: 'library',
    title: 'Asset Library',
    subtitle: 'Organize and manage your videos',
    description:
      'Search, filter, and organize all your video assets. Create collections, mark favorites, track usage, and manage your video content library with powerful search and filtering tools.',
    highlights: ['Search & Filter', 'Collections', 'Favorites', 'Usage Tracking'],
    status: 'live',
    route: '/video-studio/library',
    pricingNote: 'Free (storage included)',
    eta: 'Now',
    icon: <LibraryBooksIcon />,
    help: 'Perfect for content creators managing multiple videos. Search by title, model, or prompt. Create collections to organize videos by project or campaign. Track downloads and usage.',
    costDrivers: ['Free - no cost'],
  },
];
