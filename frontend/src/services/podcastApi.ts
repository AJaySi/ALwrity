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
import { TaskStatus } from "./storyWriterApi";

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

type OptionLike = StorySetupGenerationResponse["options"][0] | { plot_elements?: string; premise?: string };

const deriveSegments = (option?: OptionLike): string[] => {
  const segments: string[] = [];
  if (option?.plot_elements) {
    option.plot_elements
      .split(/[,.;]+/)
      .map((p) => p.trim())
      .filter(Boolean)
      .forEach((p) => segments.push(p));
  }
  if (!segments.length && "premise" in (option || {}) && (option as any)?.premise) {
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
  queryCount = 3,
}: {
  minutes: number;
  scenes: number;
  chars: number;
  quality: string;
  avatars: number;
  queryCount?: number;
}): PodcastEstimate => {
  const secs = Math.max(60, minutes * 60);
  const ttsCost = (chars / 1000) * 0.05;
  const avatarCost = avatars * 0.15;
  const videoRate = quality === "hd" ? 0.06 : 0.03;
  const videoCost = secs * videoRate;
  const researchCost = +(Math.max(1, queryCount) * 0.1).toFixed(2);
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
  const baseIdea = seed || "AI marketing for small businesses";
  const personaKeywords = persona?.suggested_keywords?.filter(Boolean) || [];
  const angles = persona?.research_angles ?? [];
  const generated: Query[] = [];

  const addQuery = (q: string, why: string, needsRecent = false) => {
    if (!q.trim()) return;
    generated.push({
      id: createId("q"),
      query: q.trim(),
      rationale: why,
      needsRecentStats: needsRecent,
    });
  };

  if (personaKeywords.length) {
    personaKeywords.slice(0, 4).forEach((k, idx) =>
      addQuery(k, angles[idx % Math.max(1, angles.length)] || "Persona-aligned query", /202[45]|latest|trend/i.test(k))
    );
  }

  if (!generated.length) {
    addQuery(`How is ${baseIdea} evolving in 2024?`, "Trend + outcome focus", true);
    addQuery(`Best practices for ${baseIdea}`, "Actionable guidance", false);
    addQuery(`${baseIdea} case studies with ROI`, "Proof and outcomes", true);
    addQuery(`${baseIdea} risks and objections`, "Address listener concerns", false);
  }

  return generated.slice(0, 6);
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

const waitForTaskCompletion = async (
  taskId: string, 
  poll: WaitForTaskFn,
  onProgress?: (status: { status: string; progress?: number; message?: string }) => void
): Promise<any> => {
  let attempts = 0;
  while (attempts < 120) {
    const status = await poll(taskId);
    
    // Report progress if callback provided
    if (onProgress) {
      // Extract latest progress message if available
      const latestMessage = status.progress_messages && status.progress_messages.length > 0
        ? status.progress_messages[status.progress_messages.length - 1].message
        : undefined;
      
      onProgress({
        status: status.status,
        progress: undefined, // TaskStatusResponse doesn't have progress field
        message: latestMessage,
      });
    }
    
    if (status.status === "completed") {
      return status.result;
    }
    if (status.status === "failed") {
      const errorMsg = status.error || "Task failed";
      throw new Error(errorMsg);
    }
    await sleep(2500);
    attempts += 1;
  }
  throw new Error("Task polling timed out after 5 minutes");
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

    // Podcast-specific analysis (not story setup)
    const analysisResp = await aiApiClient.post("/api/podcast/analyze", {
      idea: storyIdea,
      duration: payload.duration,
      speakers: payload.speakers,
    });

    const outlines = (analysisResp.data?.suggested_outlines || []).map((o: any, idx: number) => ({
      id: o.id || `outline-${idx + 1}`,
      title: o.title || `Outline ${idx + 1}`,
      segments: Array.isArray(o.segments) ? o.segments : deriveSegments({ plot_elements: o.segments }),
    }));

    const analysis: PodcastAnalysis = {
      audience: analysisResp.data?.audience || "Growth-minded pros",
      contentType: analysisResp.data?.content_type || "Podcast interview",
      topKeywords: analysisResp.data?.top_keywords || outlines[0]?.segments?.slice(0, 3) || [],
      suggestedOutlines: outlines,
      suggestedKnobs: { ...DEFAULT_KNOBS, ...payload.knobs },
      titleSuggestions: (analysisResp.data?.title_suggestions || []).filter(Boolean),
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
      queryCount: queries.length || 3,
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
    onProgress?: (message: string) => void;
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
    let lastProgressMessage = "";
    const result = (await waitForTaskCompletion(
      task_id, 
      blogWriterApi.pollResearchStatus,
      (status) => {
        // Extract latest progress message and notify caller
        if (status.message && status.message !== lastProgressMessage) {
          lastProgressMessage = status.message;
          if (params.onProgress) {
            params.onProgress(status.message);
          }
        } else if (status.status === "running" && !status.message) {
          // Provide default status messages if none available
          const defaultMessage = params.provider === "exa" 
            ? "Deep research in progress..." 
            : "Gathering research sources...";
          if (params.onProgress && lastProgressMessage !== defaultMessage) {
            lastProgressMessage = defaultMessage;
            params.onProgress(defaultMessage);
          }
        }
      }
    )) as BlogResearchResponse;
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

    const response = await aiApiClient.post("/api/podcast/script", {
      idea: params.idea,
      duration_minutes: params.durationMinutes,
      speakers: params.speakers,
      research: params.research,
    });

    const scenes = response.data?.scenes || [];
    const scriptScenes: Scene[] = scenes.map((scene: any) => ({
      id: scene.id || createId("scene"),
      title: scene.title || "Scene",
      duration: scene.duration || Math.max(20, params.knobs.scene_length_target || DEFAULT_KNOBS.scene_length_target),
      lines:
        Array.isArray(scene.lines) && scene.lines.length
          ? scene.lines.map((l: any) => ({
              id: createId("line"),
              speaker: l.speaker || "Host",
              text: l.text || "",
            }))
          : [
              {
                id: createId("line"),
                speaker: "Host",
                text: "Let's dive into today's topic.",
              },
            ],
      approved: false,
    }));

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

    const response = await aiApiClient.post("/api/podcast/audio", {
      scene_id: params.scene.id,
      scene_title: params.scene.title,
      text,
      voice_id: params.voiceId || "Wise_Woman",
      speed: params.speed || 1.0,
      emotion: params.emotion || "neutral",
    });

    return {
      audioUrl: response.data.audio_url,
      audioFilename: response.data.audio_filename,
      provider: response.data.provider,
      model: response.data.model,
      cost: response.data.cost,
      voiceId: response.data.voice_id,
      fileSize: response.data.file_size,
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

  // Project persistence endpoints
  async saveProject(projectId: string, state: any): Promise<void> {
    try {
      await aiApiClient.put(`/api/podcast/projects/${projectId}`, state);
    } catch (error) {
      console.error("Failed to save project to database:", error);
      // Don't throw - localStorage fallback is acceptable
    }
  },

  async loadProject(projectId: string): Promise<any> {
    const response = await aiApiClient.get(`/api/podcast/projects/${projectId}`);
    return response.data;
  },

  async listProjects(params?: {
    status?: string;
    favorites_only?: boolean;
    limit?: number;
    offset?: number;
    order_by?: "updated_at" | "created_at";
  }): Promise<{ projects: any[]; total: number; limit: number; offset: number }> {
    const response = await aiApiClient.get("/api/podcast/projects", { params });
    return response.data;
  },

  async createProjectInDb(params: {
    project_id: string;
    idea: string;
    duration: number;
    speakers: number;
    budget_cap: number;
  }): Promise<any> {
    const response = await aiApiClient.post("/api/podcast/projects", params);
    return response.data;
  },

  async deleteProject(projectId: string): Promise<void> {
    await aiApiClient.delete(`/api/podcast/projects/${projectId}`);
  },

  async toggleFavorite(projectId: string): Promise<any> {
    const response = await aiApiClient.post(`/api/podcast/projects/${projectId}/favorite`);
    return response.data;
  },

  async saveAudioToAssetLibrary(params: {
    audioUrl: string;
    filename: string;
    title: string;
    description?: string;
    projectId: string;
    sceneId?: string;
    cost?: number;
    provider?: string;
    model?: string;
    fileSize?: number;
  }): Promise<{ assetId: number }> {
    const response = await aiApiClient.post("/api/content-assets/", {
      asset_type: "audio",
      source_module: "podcast_maker",
      filename: params.filename,
      file_url: params.audioUrl,
      title: params.title,
      description: params.description || `Podcast episode audio: ${params.title}`,
      tags: ["podcast", "audio", params.projectId],
      asset_metadata: {
        project_id: params.projectId,
        scene_id: params.sceneId,
        provider: params.provider,
        model: params.model,
      },
      provider: params.provider,
      model: params.model,
      cost: params.cost || 0,
      file_size: params.fileSize,
      mime_type: "audio/mpeg",
    });
    return { assetId: response.data.id };
  },

  async generateVideo(params: {
    projectId: string;
    sceneId: string;
    sceneTitle: string;
    audioUrl: string;
    avatarImageUrl?: string;
    resolution?: string;
    prompt?: string;
  }): Promise<{ taskId: string; status: string; message: string }> {
    const response = await aiApiClient.post("/api/podcast/render/video", {
      project_id: params.projectId,
      scene_id: params.sceneId,
      scene_title: params.sceneTitle,
      audio_url: params.audioUrl,
      avatar_image_url: params.avatarImageUrl,
      resolution: params.resolution || "720p",
      prompt: params.prompt,
    });
    return response.data;
  },

  async pollTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await aiApiClient.get(`/api/podcast/task/${taskId}/status`);
    return response.data;
  },

  async cancelTask(taskId: string): Promise<void> {
    // Note: Task cancellation may not be fully supported by backend yet
    // This is a placeholder for future implementation
    try {
      await aiApiClient.post(`/api/story/task/${taskId}/cancel`);
    } catch (error) {
      console.warn("Task cancellation not supported:", error);
    }
  },
};

export type PodcastApi = typeof podcastApi;

