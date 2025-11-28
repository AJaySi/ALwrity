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
};

export type Line = {
  id: string;
  speaker: string;
  text: string;
  usedFactIds?: string[];
};

export type Scene = {
  id: string;
  title: string;
  duration: number;
  lines: Line[];
  approved?: boolean;
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
  jobId?: string | null;
  cost?: number | null;
  provider?: string | null;
  voiceId?: string | null;
  fileSize?: number | null;
};

export type PodcastAnalysis = {
  audience: string;
  contentType: string;
  topKeywords: string[];
  suggestedOutlines: { id: number | string; title: string; segments: string[] }[];
  suggestedKnobs: Knobs;
  titleSuggestions: string[];
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
};

