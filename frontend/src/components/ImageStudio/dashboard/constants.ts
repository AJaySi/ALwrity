export const createExamples = [
  {
    id: 'ig-hero',
    label: 'Instagram hero',
    prompt:
      '"Cinematic coffee shop hero shot, golden hour lighting, stylish barista pouring latte art, 4k, depth of field, film grain"',
    provider: 'WaveSpeed Ideogram V3 Turbo',
    image:
      'https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80',
    description:
      'Polished hero visual for carousel slides and blog headers with photorealistic signage.',
    price: '$0.18',
    eta: '~4s',
  },
  {
    id: 'linkedin-thought',
    label: 'LinkedIn thought-leadership',
    prompt:
      '"Minimalist workspace flat lay, teal gradients, AI workflow diagrams, overhead view, ultra clean, 8k render"',
    provider: 'Gemini Imagen',
    image:
      'https://images.unsplash.com/photo-1487017159836-4e23ece2e4cf?auto=format&fit=crop&w=1200&q=80',
    description: 'Clean layout for LinkedIn posts that need professional, text-friendly framing.',
    price: '$0.11',
    eta: '~3s',
  },
  {
    id: 'tiktok-hook',
    label: 'TikTok hook frame',
    prompt:
      '"Vibrant neon studio, bold typography reading Growth Hacks, 9:16 layout, dynamic lighting, energetic vibe"',
    provider: 'WaveSpeed Qwen Image',
    image:
      'https://images.unsplash.com/photo-1504196606672-aef5c9cefc92?auto=format&fit=crop&w=1200&q=80',
    description: 'High-energy vertical frame to start TikTok/Reels with bold colors and legible copy.',
    price: '$0.07',
    eta: '~2s',
  },
];

export const upscaleSamples = {
  lowRes: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=600&q=30',
  hiRes: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1600&q=80',
};

export const transformAssets = {
  storyboard: '/images/scene_1_Welcome_to_the_Cloud_Kitchen___ae6436d9.png',
  video: '/videos/scene_1_user_33Gz1FPI86V_0a5d0d71.mp4',
  script:
    "Welcome to the Cloud Kitchen! Meet Ava, your virtual chef companion. Let's explore how she runs three delivery brands from one AI-powered hub.",
};

export const controlAssets = {
  inputImage: '/images/scene_1_Welcome_to_the_Cloud_Kitchen___ae6436d9.png',
  outputVideo: '/videos/text-video-voiceover.mp4',
  prompt:
    "A confident woman in her 40s stands on a stage with a microphone. The background shows a large LED screen with abstract visuals. She smiles and begins speaking to the audience: \"Good evening everyone. Tonight, I want to share three powerful lessons about leadership and innovation.\" Her lip movements match her voice, and she uses expressive hand gestures while speaking.",
  seed: 2133312826,
  resolution: '720p',
  duration: 5,
};

export const editBeforeAfter = [
  {
    before: 'https://images.unsplash.com/photo-1455587734955-081b22074882?auto=format&fit=crop&w=800&q=80',
    after: 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=800&q=80',
    prompt: 'Inpainted background swap with studio lighting and relit subject',
  },
  {
    before: 'https://images.unsplash.com/photo-1472506200026-38c43d5fbf97?auto=format&fit=crop&w=800&q=80',
    after: 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80',
    prompt: 'Recolored wardrobe + added morning haze',
  },
  {
    before: 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=800&q=80',
    after: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=800&q=80',
    prompt: 'Reframed hero crop with dramatic sky replacement',
  },
];

export const platformPresets = [
  { label: 'IG Feed 1:1', top: '10%', left: '5%', width: '35%', height: '35%' },
  { label: 'TikTok 9:16', top: '5%', right: '5%', width: '25%', height: '60%' },
  { label: 'LinkedIn 1.91:1', bottom: '8%', left: '10%', width: '55%', height: '25%' },
  { label: 'Pinterest 2:3', bottom: '12%', right: '8%', width: '22%', height: '30%' },
];

export const statusStyles = {
  live: { label: 'Live', color: '#10b981' },
  'coming soon': { label: 'Coming Soon', color: '#f97316' },
  planning: { label: 'In Planning', color: '#d1d5db' },
};

