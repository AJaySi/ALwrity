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

export const STORY_IDEA_PLACEHOLDERS_BY_COMBINATION: Record<string, string[]> = {
  "marketing:product_story": [
    "Tell the story of a busy marketer who discovers your tool on a late night, runs their first A/B test in minutes, and wakes up to a dashboard that finally makes sense to their whole team.",
    "Describe a customer who was drowning in spreadsheets before your product automated their reporting, freeing them to focus on creative campaigns that grew revenue.",
    "Share how a small agency used your platform to win a bigger client by showing a clear, story-driven campaign plan powered by your analytics.",
  ],
  "marketing:brand_manifesto": [
    "Write a brand manifesto for a company that believes thoughtful, long-form content can still win in a world of short attention spans.",
    "Describe a brand that sees storytelling as infrastructure, not decoration, and wants every article, email, and video to feel like chapter in a larger narrative.",
    "Create a manifesto for a founder-led brand that wants to sound confident but humble, optimistic but realistic, in every story it tells.",
  ],
  "marketing:founder_story": [
    "Tell the story of a founder who built this product after years of frustration using clunky tools that never understood how real marketers work.",
    "Describe how the founder went from freelancing at a kitchen table to building a small remote team around a shared belief in better creative workflows.",
    "Write about the moment the founder realized their side project could become a real company after one early customer sent an emotional thank-you email.",
  ],
  "marketing:customer_story": [
    "Describe a customer who struggled to publish consistent content until they layered your product into their weekly planning ritual.",
    "Tell the story of a skeptical customer who tried your platform for a single campaign, then gradually replaced three different tools after seeing the results.",
    "Write about a customer who used your product to launch a new product line and turned a quiet list into an engaged community.",
  ],
  "pure:short_fiction": [
    "A commuter misses their usual train by seconds and steps onto a nearly empty carriage, where each passenger seems to know a different version of their life.",
    "On an ordinary Tuesday, everyone in a small town wakes up with the same dream fresh in their mind and realizes it contains instructions.",
    "A barista begins to notice that the same stranger appears in the background of every photo they have ever taken, even those from childhood.",
  ],
  "pure:long_fiction": [
    "Across several decades, follow three generations of one family whose small decisions around a single house slowly reshape an entire neighborhood.",
    "Tell the intertwined stories of five strangers who unknowingly influence each other’s lives through a series of anonymous letters.",
    "A researcher discovers a pattern in global news events that suggests someone is editing the timeline, but only on very small, personal scales.",
  ],
  "pure:anime_fiction": [
    "In a floating city powered by forgotten songs, a quiet student discovers they can hear the original melodies and must decide whether to restore or rewrite them.",
    "A shy mechanic repairs battle mechs that secretly contain fragments of their pilots’ memories, and one day hears a voice speak back.",
    "Every night at midnight, the neon signs in a dense anime metropolis rearrange to spell a new prophecy that only one teenager seems able to read.",
  ],
  "pure:experimental_fiction": [
    "Write a story told entirely through error messages on a failing smart home device that has begun to care about its owners.",
    "Describe a city where every conversation leaves behind a visible echo that lingers in the air for days, overlapping into unreadable noise.",
    "A retired space explorer returns to their home planet after 50 years, only to find it has been transformed into a utopian society that erases all traces of the past.",
  ],
};

