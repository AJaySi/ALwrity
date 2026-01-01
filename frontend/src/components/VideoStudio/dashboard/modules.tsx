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
      'Describe your video idea and we create it for you. Perfect for Instagram Reels, TikTok, YouTube Shorts, LinkedIn posts, and more. We automatically choose the best settings for your platform.',
    highlights: ['Text to Video', 'Image to Video', 'Platform Ready'],
    status: 'live',
    route: '/video-studio/create',
    pricingNote: 'Cost depends on video length and quality. We show you the price before generating.',
    eta: 'Now',
    icon: <MovieCreationIcon />,
    help: 'Perfect for creating engaging social media content. Just describe what you want and we handle the rest. Add background music or voiceover later.',
    costDrivers: ['Video length (5–10 seconds)', 'Quality (480p/720p/1080p)', 'Platform format'],
  },
  {
    key: 'avatar',
    title: 'Avatar Studio',
    subtitle: 'Create talking videos from photos',
    description:
      'Upload a photo and audio to create a talking avatar. Perfect for explainer videos, tutorials, personalized messages, and social media content. Your photo comes to life with perfect lip-sync.',
    highlights: ['Talking Avatars', 'Lip-sync', 'Translation'],
    status: 'beta',
    route: '/video-studio/avatar',
    pricingNote: 'Cost depends on video length and quality',
    eta: 'Beta',
    icon: <FaceRetouchingNaturalIcon />,
    help: 'Great for creating personalized video messages, explainer videos, and tutorials. Upload your photo and audio, and we create a talking video.',
    costDrivers: ['Video length', 'Quality'],
  },
  {
    key: 'enhance',
    title: 'Enhance Studio',
    subtitle: 'Upgrade your video quality',
    description:
      'Transform low-resolution videos into professional-quality content. Upscale from 480p to 1080p or 4K, boost frame rate, and improve clarity. Perfect for upgrading social media content or preparing videos for YouTube.',
    highlights: ['Upscale Quality', 'Smooth Motion', 'Frame Rate Boost'],
    status: 'live',
    route: '/video-studio/enhance',
    pricingNote: 'Cost depends on original quality and target quality',
    eta: 'Now',
    icon: <HighQualityIcon />,
    help: 'Perfect for improving videos shot on phones or upgrading old content. Make your videos look professional and ready for any platform.',
    costDrivers: ['Original quality', 'Target quality', 'Video length'],
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
    subtitle: 'Trim, enhance, and customize',
    description:
      'Trim and cut videos, adjust speed, stabilize shaky footage, replace backgrounds, swap faces, add captions and subtitles, and color grade. All the editing tools you need in one place.',
    highlights: ['Trim & Cut', 'Background Swap', 'Add Captions'],
    status: 'coming soon',
    route: '/video-studio/edit',
    pricingNote: 'Cost depends on video length and number of edits',
    eta: 'Coming soon',
    icon: <EditIcon />,
    help: 'Complete video editing suite for content creators. Make your videos perfect before sharing on social media.',
    costDrivers: ['Video length', 'Number of edits'],
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
  },
  {
    key: 'library',
    title: 'Asset Library',
    subtitle: 'Organize and manage your videos',
    description:
      'Keep all your videos organized with AI-powered tagging, version tracking, usage analytics, and secure sharing. Manage your video content library like a pro.',
    highlights: ['AI Tagging', 'Version Control', 'Usage Analytics'],
    status: 'beta',
    route: '/video-studio/library',
    pricingNote: 'Storage and download costs',
    eta: 'Beta',
    icon: <LibraryBooksIcon />,
    help: 'Perfect for content creators managing multiple videos. Keep everything organized, track usage, and share securely.',
    costDrivers: ['Storage space', 'Downloads'],
  },
];
