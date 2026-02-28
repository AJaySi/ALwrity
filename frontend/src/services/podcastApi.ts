import { ResearchProvider, ResearchConfig } from "./blogWriterApi";
import {
  storyWriterApi,
  StorySetupGenerationResponse,
} from "./storyWriterApi";
import { getResearchConfig, ResearchPersona } from "../api/researchConfig";
import { aiApiClient } from "../api/client";
import {
  CreateProjectPayload,
  CreateProjectResult,
  Fact,
  Knobs,
  PodcastAnalysis,
  PodcastEstimate,
  Query,
  RenderJobResult,
  Research,
  Scene,
  Script,
} from "../components/PodcastMaker/types";
import { checkPreflight, PreflightOperation } from "./billingService";
import { TaskStatus } from "./storyWriterApi";

const DEFAULT_KNOBS: Knobs = {
  voice_emotion: "neutral",
  voice_speed: 1,
  resolution: "720p",
  scene_length_target: 45,
  sample_rate: 24000,
  bitrate: "standard",
};

// const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

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

const mapSourcesToFacts = (sources: ExaSource[]): Fact[] => {
  if (!sources || !sources.length) return [];
  return sources.slice(0, 12).map((source: ExaSource, idx: number) => ({
    id: source.url || createId("fact"),
    quote: source.excerpt || source.title || "Insight",
    url: source.url || "",
    date: source.published_at || "Unknown",
    confidence: typeof (source as any).credibility_score === "number" ? (source as any).credibility_score : Math.max(0.5, 0.85 - idx * 0.02),
    image: source.image,
    author: source.author,
    highlights: source.highlights,
  }));
};

type ExaSource = {
  title?: string;
  url?: string;
  excerpt?: string;
  published_at?: string;
  highlights?: string[];
  summary?: string;
  source_type?: string;
  index?: number;
  image?: string;
  author?: string;
};

type ExaResearchResult = {
  sources: ExaSource[];
  search_queries?: string[];
  cost?: { total?: number };
  search_type?: string;
  provider?: string;
  content?: string;
};

const mapExaResearchResponse = (response: any): Research => {
  const factCards = mapSourcesToFacts(response.sources);
  // Use backend summary if available, otherwise use full content (no truncation) or fallback text
  const summary = response.summary || response.content || "Research completed.";
  
  const keyInsights = (response.key_insights || []).map((insight: any) => ({
    title: insight.title || "Insight",
    content: insight.content || "",
    source_indices: insight.source_indices || []
  }));

  return {
    summary,
    keyInsights,
    factCards,
    mappedAngles: [],
    searchQueries: response.search_queries,
    searchType: response.search_type,
    provider: response.provider || "exa",
    cost: response.cost?.total,
    sourceCount: response.sources?.length || 0,
  };
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
  async createProject(payload: CreateProjectPayload, bible?: any, feedback?: string): Promise<CreateProjectResult> {
    const storyIdea = payload.ideaOrUrl || "AI marketing for small businesses";

    await ensurePreflight({
      provider: "gemini",
      operation_type: "podcast_analysis",
      tokens_requested: 1500,
      actual_provider_name: "gemini",
    });

    // Podcast-specific analysis (not story setup)
    const analysisResp = await aiApiClient.post("/api/podcast/analyze", {
      idea: storyIdea,
      duration: payload.duration,
      speakers: payload.speakers,
      bible: bible,
      avatar_url: payload.avatarUrl,
      feedback: feedback, // Pass feedback to backend
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
      research_queries: analysisResp.data?.research_queries || [],
      exaSuggestedConfig: analysisResp.data?.exa_suggested_config || undefined,
    };

    const researchConfig = await getResearchConfig().catch(() => null);
    
    // Use AI-generated queries if available, fallback to legacy mapping
    let queries: Query[] = [];
    if (analysis.research_queries && analysis.research_queries.length > 0) {
      queries = analysis.research_queries.map(rq => ({
        id: createId("q"),
        query: rq.query,
        rationale: rq.rationale,
        needsRecentStats: /202[45]|latest|trend/i.test(rq.query)
      }));
    } else {
      queries = mapPersonaQueries(researchConfig?.research_persona, storyIdea);
    }

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
      bible: analysisResp.data?.bible || undefined,
      avatar_url: analysisResp.data?.avatar_url || null,
      avatar_prompt: analysisResp.data?.avatar_prompt || null,
    };
  },

  async enhanceIdea(params: { idea: string; bible?: any }): Promise<{ enhanced_idea: string; rationale: string }> {
    const response = await aiApiClient.post("/api/podcast/idea/enhance", params);
    return response.data;
  },

  async runResearch(params: {
    projectId: string;
    topic: string;
    approvedQueries: Query[];
    provider?: ResearchProvider;
    exaConfig?: ResearchConfig;
    bible?: any;
    analysis?: PodcastAnalysis | null;
    onProgress?: (message: string) => void;
  }): Promise<{ research: Research; raw: any }> {
    const keywords = params.approvedQueries.map((q) => q.query).filter(Boolean);
    if (!keywords.length) {
      throw new Error("At least one query must be approved for research.");
    }

    // Ensure Exa payload respects API constraint: when requesting contents, only one of includeDomains or excludeDomains.
    let sanitizedExaConfig: ResearchConfig | undefined = params.exaConfig;
    if (sanitizedExaConfig && sanitizedExaConfig.exa_include_domains?.length) {
      sanitizedExaConfig = {
        ...sanitizedExaConfig,
        exa_exclude_domains: undefined,
      };
    } else if (sanitizedExaConfig && sanitizedExaConfig.exa_exclude_domains?.length) {
      sanitizedExaConfig = {
        ...sanitizedExaConfig,
        exa_include_domains: undefined,
      };
    }

    await ensurePreflight({
      provider: "exa",
      operation_type: "exa_neural_search",
      tokens_requested: 0,
      actual_provider_name: "exa",
    });

    const response = await aiApiClient.post("/api/podcast/research/exa", {
      topic: params.topic || keywords[0],
      queries: keywords,
      exa_config: sanitizedExaConfig,
      bible: params.bible,
      analysis: params.analysis,
    });

    const exaResult = response.data as ExaResearchResult;
    if (params.onProgress) {
      params.onProgress("Deep research completed with Exa.");
    }
    const mapped = mapExaResearchResponse(exaResult);
    return { research: mapped, raw: exaResult };
  },

  async generateScript(params: {
    projectId: string;
    idea: string;
    research?: ExaResearchResult | null;
    knobs: Knobs;
    speakers: number;
    durationMinutes: number;
    bible?: any;
    outline?: any;
    analysis?: PodcastAnalysis | null;
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
      bible: params.bible,
      outline: params.outline,
      analysis: params.analysis,
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

  async renderSceneAudio(params: {
    scene: Scene;
    voiceId?: string;
    emotion?: string; // Fallback if scene doesn't have emotion
    speed?: number;
    volume?: number;
    pitch?: number;
    englishNormalization?: boolean;
    sampleRate?: number;
    bitrate?: number;
    channel?: "1" | "2";
    format?: "mp3" | "wav" | "pcm" | "flac";
    languageBoost?: string;
  }): Promise<RenderJobResult> {
    // Use scene-specific emotion if available, otherwise fallback to provided/default
    const sceneEmotion = params.scene.emotion || params.emotion || "neutral";

    // Optimize text for Minimax Speech-02-HD TTS
    // - Strip markdown formatting (bold, italic, etc.) - TTS reads it literally
    // - Use pause markers <#x#> for natural speech rhythm
    // - Add longer pauses for speaker changes
    // - Preserve punctuation for natural breathing
    // - Add emphasis pauses for important points
    const text = params.scene.lines
      .map((line, idx) => {
        let lineText = line.text.trim();

        // Strip markdown formatting - TTS reads asterisks and other markdown literally
        // Remove bold (**text** or __text__)
        lineText = lineText.replace(/\*\*([^*]+)\*\*/g, '$1'); // **bold**
        lineText = lineText.replace(/\*([^*]+)\*/g, '$1'); // *bold* (single asterisk)
        lineText = lineText.replace(/__([^_]+)__/g, '$1'); // __bold__
        lineText = lineText.replace(/_([^_]+)_/g, '$1'); // _italic_ (single underscore)
        // Remove any remaining stray asterisks or underscores
        lineText = lineText.replace(/\*+/g, ''); // Remove any remaining asterisks
        lineText = lineText.replace(/_+/g, ''); // Remove any remaining underscores
        // Clean up extra spaces
        lineText = lineText.replace(/\s+/g, ' ').trim();

        // Preserve punctuation (Minimax uses it for natural breathing)
        // Don't strip punctuation - it helps TTS understand natural pauses

        // Add emphasis pause after lines marked with emphasis
        if (line.emphasis) {
          // Minimal pause after emphasized content (0.15s for subtle emphasis)
          lineText = `${lineText}<#0.15#>`;
        }

        // Check for speaker change (longer pause for natural conversation flow)
        const prevLine = idx > 0 ? params.scene.lines[idx - 1] : null;
        const isSpeakerChange = prevLine && prevLine.speaker !== line.speaker;

        if (isSpeakerChange) {
          // Short pause for speaker changes (0.2s - enough for natural transition)
          lineText = `<#0.2#>${lineText}`;
        }

        // Add minimal pause between lines (only between regular lines, very short)
        if (idx < params.scene.lines.length - 1) {
          if (!line.emphasis && !isSpeakerChange) {
            // Very short pause between lines (0.08s - barely noticeable but helps flow)
            lineText = `${lineText}<#0.08#>`;
          }
          // If emphasis or speaker change, the pause is already added above
        }

        return lineText;
      })
      .join(" ");

    // Validate character limit (Minimax max: 10,000 characters)
    const MAX_CHARS = 10000;
    let textToUse = text;
    if (text.length > MAX_CHARS) {
      console.warn(
        `[Podcast] Scene "${params.scene.title}" exceeds ${MAX_CHARS} character limit (${text.length} chars). Truncating...`
      );
      // Truncate at word boundary to avoid cutting mid-word
      const truncated = text.substring(0, MAX_CHARS);
      const lastSpace = truncated.lastIndexOf(" ");
      textToUse = lastSpace > 0 ? truncated.substring(0, lastSpace) : truncated;
    }

    await ensurePreflight({
      provider: "audio",
      operation_type: "tts_full_render",
      tokens_requested: textToUse.length,
      actual_provider_name: "wavespeed",
    });

    const response = await aiApiClient.post("/api/podcast/audio", {
      scene_id: params.scene.id,
      scene_title: params.scene.title,
      text: textToUse,
      voice_id: params.voiceId || "Wise_Woman",
      speed: params.speed ?? 1.0, // Normal speed (was 0.9, but too slow - causing duration issues)
      volume: params.volume ?? 1.0,
      pitch: params.pitch ?? 0.0,
      emotion: sceneEmotion,
      english_normalization: params.englishNormalization ?? true, // Better number reading for statistics
      sample_rate: params.sampleRate || null,
      bitrate: params.bitrate || null,
      channel: params.channel || null,
      format: params.format || null,
      language_boost: params.languageBoost || null,
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
    avatar_url?: string | null;
  }): Promise<any> {
    const response = await aiApiClient.post("/api/podcast/projects", params);
    return response.data;
  },

  async updateProject(projectId: string, updates: any): Promise<any> {
    const response = await aiApiClient.put(`/api/podcast/projects/${projectId}`, updates);
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
    bible?: any;
    resolution?: string;
    prompt?: string;
    seed?: number;
    maskImageUrl?: string;
  }): Promise<{ taskId: string; status: string; message: string }> {
    const response = await aiApiClient.post("/api/podcast/render/video", {
      project_id: params.projectId,
      scene_id: params.sceneId,
      scene_title: params.sceneTitle,
      audio_url: params.audioUrl,
      avatar_image_url: params.avatarImageUrl,
      bible: params.bible,
      resolution: params.resolution || "720p",
      prompt: params.prompt,
      seed: params.seed ?? -1,
      mask_image_url: params.maskImageUrl,
    });

    // Backend returns snake_case (task_id); normalize to camelCase for callers
    const { task_id, status, message } = response.data || {};
    return {
      taskId: task_id,
      status,
      message,
    };
  },

  async pollTaskStatus(taskId: string): Promise<TaskStatus | null> {
    const response = await aiApiClient.get(`/api/podcast/task/${taskId}/status`);
    // Backend returns null if task not found
    return response.data || null;
  },

  async listVideos(projectId?: string): Promise<{
    videos: Array<{
      scene_number: number;
      filename: string;
      video_url: string;
      file_size: number;
    }>;
  }> {
    const params = projectId ? { project_id: projectId } : {};
    const response = await aiApiClient.get("/api/podcast/videos", { params });
    return response.data;
  },

  async combineVideos(params: {
    projectId: string;
    sceneVideoUrls: string[];
    podcastTitle?: string;
  }): Promise<{
    taskId: string;
    status: string;
    message: string;
  }> {
    const response = await aiApiClient.post("/api/podcast/render/combine-videos", {
      project_id: params.projectId,
      scene_video_urls: params.sceneVideoUrls,
      podcast_title: params.podcastTitle || "Podcast",
    });

    const { task_id, status, message } = response.data || {};
    return {
      taskId: task_id,
      status,
      message,
    };
  },

  async generateSceneImage(params: {
    sceneId: string;
    sceneTitle: string;
    sceneContent?: string;
    baseAvatarUrl?: string;
    bible?: any;
    idea?: string;
    width?: number;
    height?: number;
    customPrompt?: string;
    style?: "Auto" | "Fiction" | "Realistic";
    renderingSpeed?: "Default" | "Turbo" | "Quality";
    aspectRatio?: "1:1" | "16:9" | "9:16" | "4:3" | "3:4";
  }): Promise<{
    scene_id: string;
    scene_title: string;
    image_filename: string;
    image_url: string;
    width: number;
    height: number;
    provider: string;
    model?: string;
    cost: number;
  }> {
    const response = await aiApiClient.post("/api/podcast/image", {
      scene_id: params.sceneId,
      scene_title: params.sceneTitle,
      scene_content: params.sceneContent,
      base_avatar_url: params.baseAvatarUrl || null,
      bible: params.bible,
      idea: params.idea || null,
      width: params.width || 1024,
      height: params.height || 1024,
      custom_prompt: params.customPrompt || null,
      style: params.style || null,
      rendering_speed: params.renderingSpeed || null,
      aspect_ratio: params.aspectRatio || null,
    });
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

  async combineAudio(params: {
    projectId: string;
    sceneIds: string[];
    sceneAudioUrls: string[];
  }): Promise<{
    combined_audio_url: string;
    combined_audio_filename: string;
    total_duration: number;
    file_size: number;
    scene_count: number;
  }> {
    const response = await aiApiClient.post("/api/podcast/combine-audio", {
      project_id: params.projectId,
      scene_ids: params.sceneIds,
      scene_audio_urls: params.sceneAudioUrls,
    });
    return response.data;
  },

  async uploadAvatar(file: File, projectId?: string): Promise<{ avatar_url: string; avatar_filename: string }> {
    const formData = new FormData();
    formData.append('file', file);
    if (projectId) {
      formData.append('project_id', projectId);
    }
    const response = await aiApiClient.post('/api/podcast/avatar/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async generatePresenters(
    speakers: number,
    projectId?: string,
    audience?: string,
    contentType?: string,
    topKeywords?: string[]
  ): Promise<{
    avatars: Array<{ avatar_url: string; speaker_number: number; prompt?: string; persona_id?: string; seed?: number }>;
    persona_id?: string;
  }> {
    const formData = new FormData();
    formData.append('speakers', speakers.toString());
    if (projectId) {
      formData.append('project_id', projectId);
    }
    if (audience) {
      formData.append('audience', audience);
    }
    if (contentType) {
      formData.append('content_type', contentType);
    }
    if (topKeywords && Array.isArray(topKeywords) && topKeywords.length > 0) {
      formData.append('top_keywords', JSON.stringify(topKeywords));
    }
    const response = await aiApiClient.post('/api/podcast/avatar/generate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async makeAvatarPresentable(avatarUrl: string, projectId?: string): Promise<{ avatar_url: string; avatar_filename: string }> {
    const formData = new FormData();
    formData.append('avatar_url', avatarUrl);
    if (projectId) {
      formData.append('project_id', projectId);
    }
    const response = await aiApiClient.post('/api/podcast/avatar/make-presentable', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

export type PodcastApi = typeof podcastApi;

