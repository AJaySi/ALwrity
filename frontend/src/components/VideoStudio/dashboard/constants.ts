export const createVideoExamples = [
  {
    id: 'instagram-reel',
    label: 'Instagram Reel',
    prompt: 'A modern coffee shop interior with baristas crafting latte art, warm golden hour lighting streaming through large windows, customers chatting at wooden tables, cozy atmosphere, 9:16 vertical format',
    description: 'Perfect for Instagram Reels and TikTok. Shows how text descriptions become engaging short-form video content.',
    price: '$0.50',
    eta: '~15s',
    provider: 'Auto-select',
    video: '/videos/scene_1_user_33Gz1FPI86V_0a5d0d71.mp4',
    platform: 'Instagram',
    useCase: 'Social media content',
  },
  {
    id: 'linkedin-post',
    label: 'LinkedIn Post',
    prompt: 'Professional workspace with laptop, notebook, and coffee cup on a minimalist desk, soft natural lighting, clean modern office environment, 16:9 format',
    description: 'Ideal for LinkedIn posts and professional content. Demonstrates how simple descriptions create polished business videos.',
    price: '$0.75',
    eta: '~18s',
    provider: 'Auto-select',
    video: '/videos/text-video-voiceover.mp4',
    platform: 'LinkedIn',
    useCase: 'Professional content',
  },
  {
    id: 'youtube-short',
    label: 'YouTube Short',
    prompt: 'Dynamic product showcase with rotating view, vibrant colors, smooth camera movement, energetic music vibe, 9:16 vertical format',
    description: 'Great for YouTube Shorts and product demos. Shows how product descriptions transform into engaging video content.',
    price: '$0.60',
    eta: '~16s',
    provider: 'Auto-select',
    video: '/videos/scene_1_user_33Gz1FPI86V_0a5d0d71.mp4',
    platform: 'YouTube',
    useCase: 'Product marketing',
  },
];

export const enhanceVideoExamples = {
  before: '/videos/scene_1_user_33Gz1FPI86V_0a5d0d71.mp4',
  after: '/videos/text-video-voiceover.mp4',
  description: 'Upscale 480p to 1080p, boost frame rate from 24fps to 60fps, and enhance clarity for professional use.',
};

export const avatarExamples = {
  image: '/images/scene_1_Welcome_to_the_Cloud_Kitchen___ae6436d9.png',
  video: '/videos/text-video-voiceover.mp4',
  description: 'Upload a photo and audio to create a talking avatar perfect for explainer videos, tutorials, and personalized messages.',
};
