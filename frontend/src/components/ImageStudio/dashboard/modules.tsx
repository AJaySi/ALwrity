import React from 'react';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import BrushIcon from '@mui/icons-material/Brush';
import UpgradeIcon from '@mui/icons-material/Upgrade';
import TransformIcon from '@mui/icons-material/Transform';
import ShareIcon from '@mui/icons-material/Share';
import EditNoteIcon from '@mui/icons-material/EditNote';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import { ModuleConfig } from './types';

export const studioModules: ModuleConfig[] = [
  {
    key: 'create',
    title: 'Create Studio',
    subtitle: 'Text-to-image generation',
    description:
      'Generate photorealistic visuals with Stability, WaveSpeed, HuggingFace, and Gemini. Templates, smart providers, and enterprise prompt controls included.',
    highlights: ['Smart provider routing', 'Platform templates', 'Cost preview'],
    status: 'live',
    route: '/image-generator',
    icon: <AutoAwesomeIcon />,
    help: 'Ideal for blog headers, social posts, ad creatives, and brand assets.',
    pricing: {
      estimate: '$0.12 - $0.48 / image (credit aware)',
      notes: 'Auto-select suggests lowest-cost provider before generation.',
    },
    example: {
      title: 'Instagram carousel hero image',
      steps: [
        'Choose Instagram template + 4:5 ratio',
        'Prompt helper enriches "fall coffee launch" copy',
        'Preview cost/time → generate 3 variations',
      ],
      eta: '~4s per variation',
    },
  },
  {
    key: 'edit',
    title: 'Edit Studio',
    subtitle: 'AI-powered editing',
    description:
      'Remove backgrounds, inpaint, outpaint, recolor, and relight images with Stability AI workflows and Hugging Face conversational edits.',
    highlights: ['Object removal', 'Canvas expansion', 'Relight + background swap'],
    status: 'live',
    route: '/image-editor',
    icon: <BrushIcon />,
    help: 'Upload existing assets and enhance them with precise AI tools.',
    pricing: {
      estimate: '$0.08 - $0.30 / edit (based on area + ops)',
      notes: 'Bulk edits share the same upload to save credits.',
    },
    example: {
      title: 'Replace dull background for LinkedIn hero',
      steps: [
        'Upload portrait → auto mask detects subject',
        'Use "Replace background" preset → choose corporate loft style',
        'Relight + save layered history for future tweaks',
      ],
      eta: '~6s render',
    },
  },
  {
    key: 'upscale',
    title: 'Upscale Studio',
    subtitle: 'Resolution enhancement',
    description:
      'Fast 4x upscale, conservative 4K, and creative 4K pipelines powered by Stability AI. Perfect for print, campaigns, and hero imagery.',
    highlights: ['Fast 4x mode', '4K creative', 'Side-by-side preview'],
    status: 'live',
    route: '/image-upscale',
    icon: <UpgradeIcon />,
    help: 'Upscale images to 4K-ready assets with one click.',
    pricing: {
      estimate: '$0.10 (Fast) · $0.32 (Creative 4K)',
      notes: 'Queue batches overnight to reduce credit burn.',
    },
    example: {
      title: 'Print-ready hero panel',
      steps: [
        'Upload 1024 hero → auto-detect recommends Creative 4K',
        'Preview side-by-side → confirm texture preservation',
        'Schedule overnight batch with 6 variants',
      ],
      eta: 'Fast = 1s · 4K = 6s',
    },
  },
  {
    key: 'transform',
    title: 'Transform Studio',
    subtitle: 'Image → Video / Avatar / 3D',
    description:
      'WaveSpeed WAN 2.5 (image-to-video), Hunyuan Avatar, and Stable Fast 3D to convert images into motion, avatars, or 3D assets.',
    highlights: ['Image-to-video', 'Talking avatars', '3D export'],
    status: 'coming soon',
    icon: <TransformIcon />,
    help: 'Designed for campaign teasers, explainers, and immersive media.',
    pricing: {
      estimate: '$0.50 (10s video 480p) · $3.60 (avatar 2 min)',
      notes: 'Text-to-speech add-on billed separately per 15s.',
    },
    example: {
      title: 'Product launch teaser video',
      steps: [
        'Pick motion preset "Medium pan + glow"',
        'Upload hero shot + 8s script for TTS',
        'Preview storyboard → export 1080p MP4',
      ],
      eta: '~15s generation',
    },
  },
  {
    key: 'optimizer',
    title: 'Social Optimizer',
    subtitle: 'Platform-ready exports',
    description:
      'Smart resize, safe zones, and engagement tips for Instagram, TikTok, LinkedIn, YouTube, Pinterest, and more in one click.',
    highlights: ['Text safe zones', 'Batch export', 'Platform presets'],
    status: 'planning',
    icon: <ShareIcon />,
    help: 'Ship consistent assets across every social surface.',
    pricing: {
      estimate: '$0.02 - $0.06 / rendition',
      notes: 'Unlimited exports on Pro + Enterprise tiers.',
    },
    example: {
      title: 'One hero → 6 platform exports',
      steps: [
        'Add source image → auto-detect focal subject',
        'Select IG, TikTok, LinkedIn, Pinterest presets',
        'Review safe zones overlay → export ZIP + schedule',
      ],
      eta: '~2s / platform',
    },
  },
  {
    key: 'control',
    title: 'Control Studio',
    subtitle: 'Sketch, structure & style',
    description:
      'Sketch-to-image, structure control, and advanced style transfer so creative directors can steer outputs precisely.',
    highlights: ['Sketch control', 'Style libraries', 'Strength sliders'],
    status: 'planning',
    icon: <EditNoteIcon />,
    help: 'For art directors who need total control over AI outputs.',
    pricing: {
      estimate: '$0.20 / render with dual-control',
      notes: 'Saved reference boards reuse controls at $0.05.',
    },
    example: {
      title: 'Storyboard consistency pack',
      steps: [
        'Upload wireframe + art-style JPEG',
        'Set control strength 60% structure / 40% style',
        'Generate 8 shots → auto-tag to Asset Library',
      ],
      eta: '~8s per shot',
    },
  },
  {
    key: 'batch',
    title: 'Batch Processor',
    subtitle: 'Scale campaigns',
    description:
      'Queue generators, edits, upscales, and exports for entire campaigns with cost previews, scheduling, and monitoring.',
    highlights: ['Bulk prompts', 'Usage tracking', 'Schedule windows'],
    status: 'planning',
    icon: <LibraryBooksIcon />,
    help: 'Turn one brief into dozens of deliverables automatically.',
    pricing: {
      estimate: 'Dynamic · e.g. 25-image pack ≈ $9',
      notes: 'Warns when batch exceeds remaining credits.',
    },
    example: {
      title: 'Evergreen blog refresh',
      steps: [
        'Upload CSV prompts grouped by persona',
        'Assign module per row (Create, Edit, Upscale)',
        'Schedule weekend window + email digest',
      ],
      eta: 'Depends on queue size',
    },
  },
  {
    key: 'library',
    title: 'Asset Library',
    subtitle: 'Searchable visual archive',
    description:
      'AI-tagged collections, favorites, history, and collaboration. Filters by platform, persona, use case, or campaign.',
    highlights: ['AI tagging', 'Version history', 'Shareable collections'],
    status: 'planning',
    icon: <LibraryBooksIcon />,
    help: 'Centralize every visual produced inside ALwrity.',
    pricing: {
      estimate: 'Included in tier · extra storage $5 / 100GB',
      notes: 'Enterprise adds S3 export + governance logs.',
    },
    example: {
      title: 'Campaign war-room board',
      steps: [
        'Filter by persona + platform → pin hero assets',
        'Share read-only board with agency partner',
        'Track usage + cost per asset inside analytics tab',
      ],
      eta: 'Instant search (<500ms)',
    },
  },
];

