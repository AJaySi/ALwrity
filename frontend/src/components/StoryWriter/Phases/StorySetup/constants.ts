// Story setup constants

export const WRITING_STYLES = [
  'Formal',
  'Casual',
  'Poetic',
  'Humorous',
  'Academic',
  'Journalistic',
  'Narrative',
];

export const STORY_TONES = [
  'Dark',
  'Uplifting',
  'Suspenseful',
  'Whimsical',
  'Melancholic',
  'Mysterious',
  'Romantic',
  'Adventurous',
];

export const NARRATIVE_POVS = [
  'First Person',
  'Third Person Limited',
  'Third Person Omniscient',
];

export const AUDIENCE_AGE_GROUPS = [
  'Children (5-12)',
  'Young Adults (13-17)',
  'Adults (18+)',
  'All Ages',
];

export const CONTENT_RATINGS = ['G', 'PG', 'PG-13', 'R'];

export const ENDING_PREFERENCES = [
  'Happy',
  'Tragic',
  'Cliffhanger',
  'Twist',
  'Open-ended',
  'Bittersweet',
];

export const STORY_LENGTHS = [
  'Short (>1000 words)',
  'Medium (>5000 words)',
  'Long (>10000 words)',
];

export const IMAGE_PROVIDERS = [
  { value: '', label: 'Auto (Default)' },
  { value: 'gemini', label: 'Gemini' },
  { value: 'huggingface', label: 'HuggingFace' },
  { value: 'stability', label: 'Stability AI' },
];

export const AUDIO_PROVIDERS = [
  { value: 'gtts', label: 'Google TTS (gTTS)' },
  { value: 'pyttsx3', label: 'pyttsx3' },
];

export const COMMON_IMAGE_SIZES = [
  { width: 512, height: 512, label: '512x512 (Square)' },
  { width: 768, height: 768, label: '768x768 (Square)' },
  { width: 1024, height: 1024, label: '1024x1024 (Square)' },
  { width: 1024, height: 768, label: '1024x768 (Landscape)' },
  { width: 768, height: 1024, label: '768x1024 (Portrait)' },
];

export const STORY_IDEA_PLACEHOLDERS = [
  "A young wizard discovers a magical artifact in an ancient forest. The artifact holds the power to restore balance to a dying realm, but it comes with a terrible cost. The wizard must choose between saving the world and losing everything they hold dear.",
  "In a cyberpunk future where memories can be bought and sold, a detective with no past must solve a murder that threatens to expose a conspiracy spanning decades. The deeper they dig, the more they realize their own memories might have been stolen.",
  "A retired space explorer returns to their home planet after 50 years, only to find it has been transformed into a utopian society that erases all traces of the past. They must uncover the truth about what happened while avoiding the watchful eyes of the perfect world they helped create.",
];

