export type Mode = 't2v' | 'i2v';

export type MotionPreset = 'Subtle' | 'Medium' | 'Dynamic';
export type AspectPreset = '9:16' | '1:1' | '16:9';
export type Resolution = '480p' | '720p' | '1080p';
export type Duration = 5 | 8 | 10;

export interface VideoGenerationSettings {
  mode: Mode;
  prompt: string;
  negativePrompt: string;
  duration: Duration;
  resolution: Resolution;
  aspect: AspectPreset;
  motion: MotionPreset;
  audioAttached: boolean;
}

export interface ExampleVideo {
  id: string;
  label: string;
  prompt: string;
  description: string;
  price: string;
  eta: string;
  provider: string;
  video: string;
  platform: string;
  useCase: string;
}
