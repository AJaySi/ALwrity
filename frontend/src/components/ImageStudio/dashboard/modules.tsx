import React from 'react';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import BrushIcon from '@mui/icons-material/Brush';
import UpgradeIcon from '@mui/icons-material/Upgrade';
import TransformIcon from '@mui/icons-material/Transform';
import ShareIcon from '@mui/icons-material/Share';
import EditNoteIcon from '@mui/icons-material/EditNote';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import CompressIcon from '@mui/icons-material/Compress';
import BuildIcon from '@mui/icons-material/Build';
import {
  Box,
  Typography,
  Container,
  Grid,
  Paper,
  Button,
  TextField,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert,
  AlertTitle,
  Chip,
  Avatar,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Pagination,
  Tabs,
  Tab,
  Switch,
  FormControl,
  FormControlLabel,
  Select,
  InputLabel,
  Checkbox,
  RadioGroup,
  Radio,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Breadcrumbs,
  Link,
  Tooltip,
  Fab,
  SpeedDial,
  SpeedDialAction,
  Backdrop,
  Modal
} from '../../../utils/mui-optimizer';
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
    key: 'face-swap',
    title: 'Face Swap Studio',
    subtitle: 'AI face swapping',
    description:
      'Swap faces in photos with multiple AI models. Choose from budget to premium options with auto-detection and smart recommendations.',
    highlights: ['Multi-model support', 'Auto-detection', 'Group photos'],
    status: 'live',
    route: '/image-studio/face-swap',
    icon: <SwapHorizIcon />,
    help: 'Perfect for creative projects, content creation, and marketing campaigns.',
    pricing: {
      estimate: '$0.025 - $0.16 / swap',
      notes: 'Auto-selects best model based on your images and preferences.',
    },
    example: {
      title: 'Swap face in group photo',
      steps: [
        'Upload base image and face image',
        'System auto-selects best model (or choose manually)',
        'Preview and download swapped result',
      ],
      eta: '~3-5s per swap',
    },
  },
  {
    key: 'compress',
    title: 'Compression Studio',
    subtitle: 'Optimize file sizes',
    description:
      'Smart image compression for web, email, and social media. Convert formats, target specific file sizes, and strip metadata.',
    highlights: ['Format conversion', 'Size targeting', 'Metadata stripping'],
    status: 'live',
    route: '/image-studio/compress',
    icon: <CompressIcon />,
    help: 'Reduce file sizes without visible quality loss for faster loading.',
    pricing: {
      estimate: 'Free (local processing)',
      notes: 'No credits required - processed locally.',
    },
    example: {
      title: 'Optimize blog images for web',
      steps: [
        'Upload image → see original size',
        'Select WebP format + 80% quality',
        'Download optimized file (40-60% smaller)',
      ],
      eta: '<1s per image',
    },
  },
  {
    key: 'processing',
    title: 'Image Processing Studio',
    subtitle: 'All-in-one toolkit',
    description:
      'Unified studio for compression, format conversion, resizing, and watermarking. Complete image processing toolkit in one place.',
    highlights: ['Compression', 'Format Converter', 'Resizer (coming)', 'Watermark (coming)'],
    status: 'live',
    route: '/image-studio/processing',
    icon: <BuildIcon />,
    help: 'All image processing tools in one unified interface.',
    pricing: {
      estimate: 'Free (local processing)',
      notes: 'No credits required - processed locally.',
    },
    example: {
      title: 'Complete image workflow',
      steps: [
        'Upload image → Compress to reduce size',
        'Convert format (PNG → WebP)',
        'Resize for platform (coming soon)',
        'Add watermark (coming soon)',
      ],
      eta: '<2s per operation',
    },
  },
  {
    key: 'transform',
    title: 'Transform Studio',
    subtitle: 'Image → Video / Avatar / 3D',
    description:
      'WaveSpeed WAN 2.5 (image-to-video), InfiniteTalk (talking avatars), and Stable Fast 3D to convert images into motion, avatars, or 3D assets.',
    highlights: ['Image-to-video', 'Talking avatars', '3D export'],
    status: 'live',
    route: '/image-transform',
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
    status: 'live',
    route: '/image-studio/social-optimizer',
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
    status: 'live',
    route: '/image-control',
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
    status: 'live',
    route: '/asset-library',
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

