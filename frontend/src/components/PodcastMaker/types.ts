export type Knobs = {
  voice_emotion: string;
  voice_speed: number;
  resolution: string;
  scene_length_target: number;
  sample_rate: number;
  bitrate: string;
};

export type Query = {
  id: string;
  query: string;
  rationale: string;
  needsRecentStats: boolean;
};

export type Fact = {
  id: string;
  quote: string;
  url: string;
  date: string;
  confidence: number;
};

export type Research = {
  summary: string;
  factCards: Fact[];
  mappedAngles: {
    title: string;
    why: string;
    mappedFactIds: string[];
  }[];
  searchQueries?: string[];
  searchType?: string;
  provider?: string;
  cost?: number;
  sourceCount?: number;
};

export type Line = {
  id: string;
  speaker: string;
  text: string;
  usedFactIds?: string[];
  emphasis?: boolean; // Mark lines that need vocal emphasis
};

export type Scene = {
  id: string;
  title: string;
  duration: number;
  lines: Line[];
  approved?: boolean;
  emotion?: string; // Scene-specific emotion
  audioUrl?: string; // Generated audio URL for this scene
  imageUrl?: string; // Generated image URL for this scene (for video generation)
};

export type Script = {
  scenes: Scene[];
};

export type JobStatus =
  | "idle"
  | "previewing"
  | "queued"
  | "running"
  | "completed"
  | "cancelled"
  | "failed";

export type Job = {
  sceneId: string;
  title: string;
  status: JobStatus;
  progress: number;
  previewUrl?: string | null;
  finalUrl?: string | null;
  videoUrl?: string | null;
  jobId?: string | null;
  taskId?: string | null;
  cost?: number | null;
  provider?: string | null;
  voiceId?: string | null;
  fileSize?: number | null;
  avatarImageUrl?: string | null;
  imageUrl?: string | null; // Scene-specific image URL
};

export type PodcastAnalysis = {
  audience: string;
  contentType: string;
  topKeywords: string[];
  suggestedOutlines: { id: number | string; title: string; segments: string[] }[];
  suggestedKnobs: Knobs;
  titleSuggestions: string[];
  exaSuggestedConfig?: {
    exa_search_type?: "auto" | "keyword" | "neural";
    exa_category?: string;
    exa_include_domains?: string[];
    exa_exclude_domains?: string[];
    max_sources?: number;
    include_statistics?: boolean;
    date_range?: string;
  };
};

export type PodcastEstimate = {
  ttsCost: number;
  avatarCost: number;
  videoCost: number;
  researchCost: number;
  total: number;
};

export type CreateProjectPayload = {
  ideaOrUrl: string;
  speakers: number;
  duration: number;
  knobs: Knobs;
  budgetCap: number;
  files: { voiceFile?: File | null; avatarFile?: File | null };
};

export type CreateProjectResult = {
  projectId: string;
  analysis: PodcastAnalysis;
  estimate: PodcastEstimate;
  queries: Query[];
};

export type RenderJobResult = {
  audioUrl: string;
  audioFilename: string;
  provider: string;
  model: string;
  cost: number;
  voiceId: string;
  fileSize: number;
  videoUrl?: string;
  videoFilename?: string;
};

export type TaskStatus = {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress?: number;
  message?: string;
  result?: any;
  error?: string;
  created_at?: string;
  updated_at?: string;
};

