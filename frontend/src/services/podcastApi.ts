import { blogWriterApi, BlogResearchRequest, BlogResearchResponse, ResearchProvider } from "./blogWriterApi";
import {
  storyWriterApi,
  StoryGenerationRequest,
  StoryScene,
  StorySetupGenerationResponse,
} from "./storyWriterApi";
import { getResearchConfig, ResearchPersona } from "../api/researchConfig";
import { aiApiClient } from "../api/client";
import {
  CreateProjectPayload,
  CreateProjectResult,
  Fact,
  Knobs,
  Line,
  PodcastAnalysis,
  PodcastEstimate,
  Query,
  RenderJobResult,
  Research,
  Scene,
  Script,
} from "../components/PodcastMaker/types";
import { checkPreflight, PreflightOperation } from "./billingService";
import { TaskStatusResponse } from "./blogWriterApi";

type WaitForTaskFn = (taskId: string) => Promise<TaskStatusResponse>;

const DEFAULT_KNOBS: Knobs = {
  voice_emotion: "neutral",
  voice_speed: 1,
  resolution: "720p",
  scene_length_target: 45,
  sample_rate: 24000,
  bitrate: "standard",
};

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const createId = (prefix: string) => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `${prefix}_${crypto.randomUUID()}`;
  }
  return `${prefix}_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
};

const deriveSegments = (option?: StorySetupGenerationResponse["options"][0]): string[] => {
  const segments: string[] = [];
  if (option?.plot_elements) {
    option.plot_elements
      .split(/[,.;]+/)
      .map((p) => p.trim())
      .filter(Boolean)
      .forEach((p) => segments.push(p));
  }
  if (!segments.length && option?.premise) {
    segments.push("Intro", "Key Takeaways", "Examples", "CTA");
  }
  return segments.slice(0, 5);
};

const estimateCosts = ({
  minutes,
  scenes,
  chars,
  quality,
  avatars,
}: {
  minutes: number;
  scenes: number;
  chars: number;
  quality: string;
  avatars: number;
}): PodcastEstimate => {
  const secs = Math.max(60, minutes * 60);
  const ttsCost = (chars / 1000) * 0.05;
  const avatarCost = avatars * 0.15;
  const videoRate = quality === "hd" ? 0.06 : 0.03;
  const videoCost = secs * videoRate;
  const researchCost = 0.5;
  const total = +(ttsCost + avatarCost + videoCost + researchCost).toFixed(2);
  return {
    ttsCost: +ttsCost.toFixed(2),
    avatarCost: +avatarCost.toFixed(2),
    videoCost: +videoCost.toFixed(2),
    researchCost,
    total,
  };
};

const mapPersonaQueries = (persona: ResearchPersona | undefined, seed: string): Query[] => {
  const keywords = persona?.suggested_keywords?.length ? persona.suggested_keywords : seed.split(/\s+/).filter(Boolean);
  if (!keywords.length) {
    return [
      {
        id: createId("q"),
        query: seed || "ai marketing small business",
        rationale: "Seed query derived from idea/topic",
        needsRecentStats: true,
      },
    ];
  }

  const angles = persona?.research_angles ?? [];
  return keywords.slice(0, 6).map((keyword, idx) => ({
    id: createId("q"),
    query: `${keyword}`.trim(),
    rationale: angles[idx % angles.length] || "High-impact persona angle",
    needsRecentStats: /202[45]|latest|trend/i.test(keyword),
  }));
};

const mapSourcesToFacts = (sources: BlogResearchResponse["sources"]): Fact[] => {
  if (!sources || !sources.length) return [];
  return sources.slice(0, 12).map((source, idx) => ({
    id: source.url || createId("fact"),
    quote: source.excerpt || source.title || "Insight",
    url: source.url || "",
    date: source.published_at || "Unknown",
    confidence: typeof source.credibility_score === "number" ? source.credibility_score : 0.8 - idx * 0.02,
  }));
};

const mapResearchResponse = (response: BlogResearchResponse): Research => {
  const factCards = mapSourcesToFacts(response.sources);
  const summary =
    response.keyword_analysis?.summary ||
    response.keyword_analysis?.key_insights?.join(" • ") ||
    "Research completed. Review fact cards for details.";
  const mappedAngles =
    response.suggested_angles?.map((angle, idx) => ({
      title: angle,
      why: response.keyword_analysis?.angle_breakdown?.[angle]?.reason || "High priority topic from research insights.",
      mappedFactIds: factCards.slice(idx, idx + 2).map((fact) => fact.id),
    })) || [];
  return {
    summary,
    factCards,
    mappedAngles,
  };
};

const splitIntoLines = (text: string, speakers: number): Line[] => {
  const sentences = text
    .split(/(?<=[.?!])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 4);
  if (!sentences.length) {
    return [
      {
        id: createId("line"),
        speaker: "Host",
        text: text || "Let's dive into today’s topic.",
      },
    ];
  }
  return sentences.map((sentence, idx) => ({
    id: createId("line"),
    speaker: idx % speakers === 0 ? "Host" : `Guest ${((idx % speakers) + 1).toString()}`,
    text: sentence,
  }));
};

const storySceneToPodcastScene = (scene: StoryScene, knobs: Knobs, speakers: number): Scene => {
  const text = scene.description || scene.audio_narration || scene.image_prompt || scene.title || "Narration";
  return {
    id: `scene-${scene.scene_number || createId("scene")}`,
    title: scene.title || `Scene ${scene.scene_number}`,
    duration: Math.max(20, knobs.scene_length_target || DEFAULT_KNOBS.scene_length_target),
    lines: splitIntoLines(text, Math.max(1, speakers)),
    approved: false,
  };
};

const ensureScenes = (outline: StorySetupGenerationResponse["options"] | StoryScene[] | string | undefined): StoryScene[] => {
  if (!outline) return [];
  if (typeof outline === "string") {
    return [
      {
        scene_number: 1,
        title: outline.slice(0, 60),
        description: outline,
        image_prompt: outline,
        audio_narration: outline,
      } as StoryScene,
    ];
  }
  if (Array.isArray(outline)) {
    return outline as StoryScene[];
  }
  return [];
};

const waitForTaskCompletion = async (taskId: string, poll: WaitForTaskFn): Promise<any> => {
  let attempts = 0;
  while (attempts < 120) {
    const status = await poll(taskId);
    if (status.status === "completed") {
      return status.result;
    }
    if (status.status === "failed") {
      throw new Error(status.error || "Task failed");
    }
    await sleep(2500);
    attempts += 1;
  }
  throw new Error("Task polling timed out");
};

const ensurePreflight = async (operation: PreflightOperation) => {
  const result = await checkPreflight(operation);
  if (!result.can_proceed) {
    const message = result.operations[0]?.message || "Pre-flight validation failed";
    throw new Error(message);
  }
  return result;
};

export const podcastApi = {
  async createProject(payload: CreateProjectPayload): Promise<CreateProjectResult> {
    const storyIdea = payload.ideaOrUrl || "AI marketing for small businesses";
    const setup = await storyWriterApi.generateStorySetup({ story_idea: storyIdea });
    const primary = setup.options?.[0];

    const suggestedOutlines = [
      {
        id: "primary",
        title: primary?.premise?.slice(0, 60) || "Episode Outline",
        segments: deriveSegments(primary),
      },
    ];

    const analysis: PodcastAnalysis = {
      audience: primary?.audience_age_group || "Growth-minded pros",
      contentType: primary?.persona || "How-to podcast",
      topKeywords: suggestedOutlines[0].segments.slice(0, 3),
      suggestedOutlines,
      suggestedKnobs: { ...DEFAULT_KNOBS, ...payload.knobs },
      titleSuggestions: [
        primary?.premise?.slice(0, 80),
        `${primary?.persona || "AI Host"} on ${primary?.story_setting || "automation"}`,
      ].filter(Boolean) as string[],
    };

    const researchConfig = await getResearchConfig().catch(() => null);
    const queries = mapPersonaQueries(researchConfig?.research_persona, storyIdea);

    const projectId = createId("podcast");
    const estimate = estimateCosts({
      minutes: payload.duration,
      scenes: Math.ceil((payload.duration * 60) / (payload.knobs.scene_length_target || DEFAULT_KNOBS.scene_length_target)),
      chars: Math.max(1000, payload.duration * 900),
      quality: payload.knobs.bitrate || "standard",
      avatars: payload.speakers,
    });

    return {
      projectId,
      analysis,
      estimate,
      queries,
    };
  },

  async runResearch(params: {
    projectId: string;
    topic: string;
    approvedQueries: Query[];
    provider?: ResearchProvider;
  }): Promise<{ research: Research; raw: BlogResearchResponse }> {
    const keywords = params.approvedQueries.map((q) => q.query).filter(Boolean);
    if (!keywords.length) {
      throw new Error("At least one query must be approved for research.");
    }

    const researchPayload: BlogResearchRequest = {
      keywords,
      topic: params.topic || keywords[0],
      research_mode: "basic",
      config: {
        provider: params.provider || "google",
        include_statistics: params.approvedQueries.some((q) => q.needsRecentStats),
      },
    };

    await ensurePreflight({
      provider: params.provider === "exa" ? "exa" : "gemini",
      operation_type: params.provider === "exa" ? "exa_neural_search" : "google_grounding",
      tokens_requested: params.provider === "exa" ? 0 : 1200,
      actual_provider_name: params.provider || "google",
    });

    const { task_id } = await blogWriterApi.startResearch(researchPayload);
    const result = (await waitForTaskCompletion(task_id, blogWriterApi.pollResearchStatus)) as BlogResearchResponse;
    const mapped = mapResearchResponse(result);
    return { research: mapped, raw: result };
  },

  async generateScript(params: {
    projectId: string;
    idea: string;
    research?: BlogResearchResponse | null;
    knobs: Knobs;
    speakers: number;
    durationMinutes: number;
  }): Promise<Script> {
    await ensurePreflight({
      provider: "gemini",
      operation_type: "script_generation",
      tokens_requested: 2000,
      actual_provider_name: "gemini",
    });

    const premise =
      params.research?.keyword_analysis?.summary ||
      params.research?.keyword_analysis?.key_insights?.join(" ") ||
      params.idea;

    const storyRequest: StoryGenerationRequest = {
      persona: "AI Podcast Host",
      story_setting: "Modern marketing studio",
      character_input: "Host and guest conversation",
      plot_elements: params.research?.suggested_angles?.join(", ") || params.idea,
      writing_style: "Conversational",
      story_tone: "Informative",
      narrative_pov: "first-person",
      audience_age_group: "Adults",
      content_rating: "G",
      ending_preference: "Call to action",
      story_length: params.durationMinutes > 15 ? "Long" : "Medium",
    };

    const outlineResponse = await storyWriterApi.generateOutline(premise, storyRequest);
    const storyScenes = ensureScenes(outlineResponse.outline);
    const scriptScenes = storyScenes.map((scene) => storySceneToPodcastScene(scene, params.knobs, params.speakers));

    return { scenes: scriptScenes };
  },

  async previewLine(
    text: string,
    options: { voiceId?: string; speed?: number; emotion?: string } = {}
  ): Promise<{ ok: boolean; message: string; audioUrl?: string }> {
    await ensurePreflight({
      provider: "audio",
      operation_type: "tts_preview",
      tokens_requested: text.length,
      actual_provider_name: "wavespeed",
    });

    const response = await storyWriterApi.generateAIAudio({
      scene_number: 0,
      scene_title: "Preview",
      text,
      voice_id: options.voiceId || "Wise_Woman",
      speed: options.speed || 1.0,
      emotion: options.emotion || "neutral",
    });

    if (!response.success) {
      throw new Error(response.error || "Preview failed");
    }

    return {
      ok: true,
      message: "Preview ready – opening audio in new tab.",
      audioUrl: response.audio_url,
    };
  },

  async renderSceneAudio(params: { scene: Scene; voiceId?: string; emotion?: string; speed?: number }): Promise<RenderJobResult> {
    const text = params.scene.lines.map((line) => line.text).join(" ");
    await ensurePreflight({
      provider: "audio",
      operation_type: "tts_full_render",
      tokens_requested: text.length,
      actual_provider_name: "wavespeed",
    });

    const response = await storyWriterApi.generateAIAudio({
      scene_number: Number(params.scene.id.replace(/\D+/g, "")) || 0,
      scene_title: params.scene.title,
      text,
      voice_id: params.voiceId || "Wise_Woman",
      speed: params.speed || 1.0,
      emotion: params.emotion || "neutral",
    });

    if (!response.success) {
      throw new Error(response.error || "Render failed");
    }

    return {
      audioUrl: response.audio_url,
      audioFilename: response.audio_filename,
      provider: response.provider,
      model: response.model,
      cost: response.cost,
      voiceId: response.voice_id,
      fileSize: response.file_size,
    };
  },

  async approveScene(params: { projectId: string; sceneId: string; notes?: string }) {
    await aiApiClient.post("/api/story/script/approve", {
      project_id: params.projectId,
      scene_id: params.sceneId,
      approved: true,
      notes: params.notes,
    });
  },
};

export type PodcastApi = typeof podcastApi;

