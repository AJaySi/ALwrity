import { aiApiClient, pollingApiClient } from "../api/client";

/**
 * Story Writer API Service
 * 
 * Provides TypeScript-typed API calls for story generation endpoints.
 */

export interface StoryGenerationRequest {
  persona: string;
  story_setting: string;
  character_input: string;
  plot_elements: string;
  writing_style: string;
  story_tone: string;
  narrative_pov: string;
  audience_age_group: string;
  content_rating: string;
  ending_preference: string;
  story_length?: string;
  enable_explainer?: boolean;
  enable_illustration?: boolean;
  enable_narration?: boolean;
  enable_video_narration?: boolean;
  // Image generation settings
  image_provider?: string;
  image_width?: number;
  image_height?: number;
  image_model?: string;
  // Video generation settings
  video_fps?: number;
  video_transition_duration?: number;
  // Audio generation settings
  audio_provider?: string;
  audio_lang?: string;
  audio_slow?: boolean;
  audio_rate?: number;
}

export interface StorySetupGenerationRequest {
  story_idea: string;
}

export interface StorySetupOption {
  persona: string;
  story_setting: string;
  character_input: string;
  plot_elements: string;
  writing_style: string;
  story_tone: string;
  narrative_pov: string;
  audience_age_group: string;
  content_rating: string;
  ending_preference: string;
  story_length?: string;
  premise: string;
  reasoning: string;
  // Image generation settings
  image_provider?: string;
  image_width?: number;
  image_height?: number;
  image_model?: string;
  // Video generation settings
  video_fps?: number;
  video_transition_duration?: number;
  // Audio generation settings
  audio_provider?: string;
  audio_lang?: string;
  audio_slow?: boolean;
  audio_rate?: number;
}

export interface StorySetupGenerationResponse {
  options: StorySetupOption[];
  success: boolean;
}

export interface StoryPremiseResponse {
  premise: string;
  success: boolean;
  task_id?: string;
}

export interface StoryScene {
  scene_number: number;
  title: string;
  description: string;
  image_prompt: string;
  audio_narration: string;
  character_descriptions?: string[];
  key_events?: string[];
}

export interface StoryOutlineResponse {
  outline: string | StoryScene[];
  success: boolean;
  task_id?: string;
  is_structured?: boolean;
}

export interface StoryContentResponse {
  story: string;
  premise?: string;
  outline?: string;
  is_complete: boolean;
  iterations: number;
  success: boolean;
  task_id?: string;
}

export interface StoryFullGenerationResponse {
  premise: string;
  outline: string;
  story: string;
  is_complete: boolean;
  iterations: number;
  success: boolean;
  task_id?: string;
}

export interface StoryStartRequest extends StoryGenerationRequest {
  premise: string;
  outline: string | StoryScene[];
}

export interface StoryContinueRequest extends StoryGenerationRequest {
  premise: string;
  outline: string | StoryScene[];
  story_text: string;
}

export interface StoryContinueResponse {
  continuation: string;
  is_complete: boolean;
  success: boolean;
}

export interface TaskStatus {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress?: number;
  message?: string;
  result?: any;
  error?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CacheStats {
  total_entries: number;
  cache_keys: string[];
}

export interface StoryImageGenerationRequest {
  scenes: StoryScene[];
  provider?: string;
  width?: number;
  height?: number;
  model?: string;
}

export interface StoryImageResult {
  scene_number: number;
  scene_title: string;
  image_filename: string;
  image_url: string;
  width: number;
  height: number;
  provider: string;
  model?: string;
  seed?: number;
  error?: string;
}

export interface StoryImageGenerationResponse {
  images: StoryImageResult[];
  success: boolean;
  task_id?: string;
}

export interface StoryAudioGenerationRequest {
  scenes: StoryScene[];
  provider?: string;
  lang?: string;
  slow?: boolean;
  rate?: number;
}

export interface StoryAudioResult {
  scene_number: number;
  scene_title: string;
  audio_filename: string;
  audio_url: string;
  provider: string;
  file_size: number;
  error?: string;
}

export interface StoryAudioGenerationResponse {
  audio_files: StoryAudioResult[];
  success: boolean;
  task_id?: string;
}

export interface StoryVideoGenerationRequest {
  scenes: StoryScene[];
  image_urls: (string | null)[];
  audio_urls: string[];
  video_urls?: (string | null)[] | null;
  ai_audio_urls?: (string | null)[] | null;
  story_title?: string;
  fps?: number;
  transition_duration?: number;
}

export interface StoryVideoResult {
  video_filename: string;
  video_url: string;
  duration: number;
  fps: number;
  file_size: number;
  num_scenes: number;
  error?: string;
}

export interface StoryVideoGenerationResponse {
  video: StoryVideoResult;
  success: boolean;
  task_id?: string;
}

export interface AnimateSceneRequest {
  scene_number: number;
  scene_data: StoryScene;
  story_context: Record<string, any>;
  image_url: string;
  duration?: 5 | 10;
}

export interface AnimateSceneVoiceoverRequest extends AnimateSceneRequest {
  audio_url: string;
  resolution?: '480p' | '720p';
  prompt?: string;
}

export interface AnimateSceneResponse {
  success: boolean;
  scene_number: number;
  video_filename: string;
  video_url: string;
  duration: number;
  cost: number;
  prompt_used: string;
  provider: string;
  prediction_id?: string;
}

export interface ResumeAnimateSceneRequest {
  prediction_id: string;
  scene_number: number;
  duration?: 5 | 10;
}

class StoryWriterApi {
  /**
   * Generate 3 story setup options from a user's story idea
   */
  async generateStorySetup(
    request: StorySetupGenerationRequest
  ): Promise<StorySetupGenerationResponse> {
    const response = await aiApiClient.post<StorySetupGenerationResponse>(
      "/api/story/generate-setup",
      request
    );
    return response.data;
  }

  /**
   * Generate a story premise
   */
  async generatePremise(request: StoryGenerationRequest): Promise<StoryPremiseResponse> {
    const response = await aiApiClient.post<StoryPremiseResponse>(
      "/api/story/generate-premise",
      request
    );
    return response.data;
  }

  /**
   * Generate a story outline from a premise
   */
  async generateOutline(
    premise: string,
    request: StoryGenerationRequest
  ): Promise<StoryOutlineResponse> {
    // Create StoryStartRequest with premise included
    const outlineRequest: StoryStartRequest = {
      ...request,
      premise: premise,
      outline: [], // Empty outline for outline generation
    };
    const response = await aiApiClient.post<StoryOutlineResponse>(
      `/api/story/generate-outline`,
      outlineRequest
    );
    return response.data;
  }

  /**
   * Generate the starting section of a story
   */
  async generateStoryStart(
    premise: string,
    outline: string | StoryScene[],
    request: StoryGenerationRequest
  ): Promise<StoryContentResponse> {
    // Create request body with premise and outline
    const requestBody = {
      ...request,
      premise,
      outline,
    };
    const response = await aiApiClient.post<StoryContentResponse>(
      `/api/story/generate-start`,
      requestBody
    );
    return response.data;
  }

  /**
   * Continue writing a story
   */
  async continueStory(request: StoryContinueRequest): Promise<StoryContinueResponse> {
    const response = await aiApiClient.post<StoryContinueResponse>(
      "/api/story/continue",
      request
    );
    return response.data;
  }

  /**
   * Generate a complete story asynchronously
   * Returns a task_id for polling
   */
  async generateFullStory(
    request: StoryGenerationRequest,
    maxIterations: number = 10
  ): Promise<{ task_id: string; status: string; message: string }> {
    const response = await aiApiClient.post<{ task_id: string; status: string; message: string }>(
      "/api/story/generate-full",
      request,
      {
        params: { max_iterations: maxIterations },
      }
    );
    return response.data;
  }

  /**
   * Get the status of a story generation task
   */
  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await pollingApiClient.get<TaskStatus>(
      `/api/story/task/${taskId}/status`
    );
    return response.data;
  }

  /**
   * Get the result of a completed story generation task
   */
  async getTaskResult(taskId: string): Promise<StoryFullGenerationResponse> {
    const response = await aiApiClient.get<StoryFullGenerationResponse>(
      `/api/story/task/${taskId}/result`
    );
    return response.data;
  }

  /**
   * Get cache statistics
   */
  async getCacheStats(): Promise<{ success: boolean; stats: CacheStats }> {
    const response = await pollingApiClient.get<{ success: boolean; stats: CacheStats }>(
      "/api/story/cache/stats"
    );
    return response.data;
  }

  /**
   * Clear the story generation cache
   */
  async clearCache(): Promise<{ success: boolean; status: string; message: string }> {
    const response = await pollingApiClient.post<{ success: boolean; status: string; message: string }>(
      "/api/story/cache/clear"
    );
    return response.data;
  }

  /**
   * Generate images for story scenes
   */
  async generateSceneImages(request: StoryImageGenerationRequest): Promise<StoryImageGenerationResponse> {
    const response = await aiApiClient.post<StoryImageGenerationResponse>(
      "/api/story/generate-images",
      request
    );
    return response.data;
  }

  /**
   * Animate a single scene image into a short video preview
   */
  async animateScene(request: AnimateSceneRequest): Promise<AnimateSceneResponse> {
    const response = await aiApiClient.post<AnimateSceneResponse>(
      "/api/story/animate-scene-preview",
      request
    );
    return response.data;
  }

  /**
   * Animate a scene image using WaveSpeed InfiniteTalk with voiceover (async)
   * Returns task_id for polling since InfiniteTalk can take up to 10 minutes.
   */
  async animateSceneVoiceover(request: AnimateSceneVoiceoverRequest): Promise<{ task_id: string; status: string; message: string }> {
    const response = await aiApiClient.post<{ task_id: string; status: string; message: string }>(
      "/api/story/animate-scene-voiceover",
      request
    );
    return response.data;
  }

  /**
   * Resume a timed-out scene animation download using the prediction id
   */
  async resumeAnimateScene(request: ResumeAnimateSceneRequest): Promise<AnimateSceneResponse> {
    const response = await aiApiClient.post<AnimateSceneResponse>(
      "/api/story/animate-scene-resume",
      request
    );
    return response.data;
  }

  private buildAbsoluteUrl(path: string): string {
    if (!path) return path;
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    const baseURL = aiApiClient.defaults.baseURL || '';
    const cleanBaseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${cleanBaseURL}${cleanPath}`;
  }

  /**
   * Get image URL for a scene image
   */
  getImageUrl(imageUrl: string): string {
    return this.buildAbsoluteUrl(imageUrl);
    }

  /**
   * Convert any relative media URL to absolute
   */
  getMediaUrl(path: string): string {
    return this.buildAbsoluteUrl(path);
  }

  /**
   * Generate audio narration for story scenes
   */
  async generateSceneAudio(request: StoryAudioGenerationRequest): Promise<StoryAudioGenerationResponse> {
    const response = await aiApiClient.post<StoryAudioGenerationResponse>(
      "/api/story/generate-audio",
      request
    );
    return response.data;
  }

  /**
   * Optimize an image prompt using WaveSpeed prompt optimizer
   */
  async optimizePrompt(request: {
    text: string;
    mode?: 'image' | 'video';
    style?: 'default' | 'artistic' | 'photographic' | 'technical' | 'anime' | 'realistic';
    image?: string;
  }): Promise<{ optimized_prompt: string; success: boolean }> {
    const response = await aiApiClient.post<{ optimized_prompt: string; success: boolean }>(
      "/api/story/optimize-prompt",
      request
    );
    return response.data;
  }

  /**
   * Regenerate a scene image using a direct prompt (no AI prompt generation)
   */
  async regenerateSceneImage(request: {
    scene_number: number;
    scene_title: string;
    prompt: string;
    provider?: string;
    width?: number;
    height?: number;
    model?: string;
  }): Promise<{
    scene_number: number;
    scene_title: string;
    image_filename: string;
    image_url: string;
    width: number;
    height: number;
    provider: string;
    model?: string;
    seed?: number;
    success: boolean;
    error?: string;
  }> {
    const response = await aiApiClient.post<{
      scene_number: number;
      scene_title: string;
      image_filename: string;
      image_url: string;
      width: number;
      height: number;
      provider: string;
      model?: string;
      seed?: number;
      success: boolean;
      error?: string;
    }>(
      "/api/story/regenerate-images",
      request
    );
    return response.data;
  }

  /**
   * Generate AI audio for a single scene using WaveSpeed Minimax Speech 02 HD
   */
  async generateAIAudio(request: {
    scene_number: number;
    scene_title: string;
    text: string;
    voice_id?: string;
    speed?: number;
    volume?: number;
    pitch?: number;
    emotion?: string;
  }): Promise<{
    scene_number: number;
    scene_title: string;
    audio_filename: string;
    audio_url: string;
    provider: string;
    model: string;
    voice_id: string;
    text_length: number;
    file_size: number;
    cost: number;
    success: boolean;
    error?: string;
  }> {
    const response = await aiApiClient.post<{
      scene_number: number;
      scene_title: string;
      audio_filename: string;
      audio_url: string;
      provider: string;
      model: string;
      voice_id: string;
      text_length: number;
      file_size: number;
      cost: number;
      success: boolean;
      error?: string;
    }>(
      "/api/story/generate-ai-audio",
      request
    );
    return response.data;
  }

  /**
   * Generate free audio for a single scene using gTTS
   */
  async generateFreeAudio(request: {
    scene_number: number;
    scene_title: string;
    text: string;
    provider?: string;
    lang?: string;
    slow?: boolean;
    rate?: number;
  }): Promise<{
    scene_number: number;
    scene_title: string;
    audio_filename: string;
    audio_url: string;
    provider: string;
    file_size: number;
    success: boolean;
    error?: string;
  }> {
    // Use existing generateSceneAudio endpoint but for a single scene
    const response = await aiApiClient.post<StoryAudioGenerationResponse>(
      "/api/story/generate-audio",
      {
        scenes: [{
          scene_number: request.scene_number,
          title: request.scene_title,
          audio_narration: request.text,
        }],
        provider: request.provider || 'gtts',
        lang: request.lang || 'en',
        slow: request.slow || false,
        rate: request.rate || 150,
      }
    );
    const result = response.data;
    if (result.success && result.audio_files && result.audio_files.length > 0) {
      const audio = result.audio_files[0];
      return {
        scene_number: audio.scene_number,
        scene_title: audio.scene_title,
        audio_filename: audio.audio_filename,
        audio_url: audio.audio_url,
        provider: audio.provider,
        file_size: audio.file_size,
        success: true,
        error: audio.error,
      };
    } else {
      throw new Error(result.audio_files?.[0]?.error || 'Failed to generate audio');
    }
  }

  /**
   * Get audio URL for a scene audio file
   */
  getAudioUrl(audioUrl: string): string {
    // If audioUrl is already a full URL, return it as-is
    if (audioUrl.startsWith('http://') || audioUrl.startsWith('https://')) {
      return audioUrl;
    }
    // Otherwise, prepend the base URL
    const baseURL = aiApiClient.defaults.baseURL || '';
    // Remove trailing slash from baseURL if present, and leading slash from audioUrl if present
    const cleanBaseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL;
    const cleanAudioUrl = audioUrl.startsWith('/') ? audioUrl : `/${audioUrl}`;
    return `${cleanBaseURL}${cleanAudioUrl}`;
  }

  /**
   * Generate video from story scenes, images, and audio
   */
  async generateStoryVideo(request: StoryVideoGenerationRequest): Promise<StoryVideoGenerationResponse> {
    const response = await aiApiClient.post<StoryVideoGenerationResponse>(
      "/api/story/generate-video",
      request
    );
    return response.data;
  }

  /**
   * Generate video asynchronously (returns task_id for polling)
   */
  async generateStoryVideoAsync(
    request: StoryVideoGenerationRequest
  ): Promise<{ task_id: string; status: string; message: string }> {
    const response = await aiApiClient.post<{ task_id: string; status: string; message: string }>(
      "/api/story/generate-video-async",
      request
    );
    return response.data;
  }

  /**
   * Generate HD AI animation via Hugging Face text-to-video (server saves and returns url)
   */
  async generateHdVideo(payload: {
    prompt: string;
    provider?: string;
    model?: string;
    num_frames?: number;
    guidance_scale?: number;
    num_inference_steps?: number;
    negative_prompt?: string;
    seed?: number;
  }): Promise<{ success: boolean; video_filename: string; video_url: string; provider: string; model: string }> {
    // Long-running request - use longRunningApiClient to allow more time
    const { longRunningApiClient } = await import("../api/client");
    const response = await longRunningApiClient.post(
      "/api/story/hd-video",
      {
        provider: "huggingface",
        ...payload,
      }
    );
    return response.data;
  }

  /**
   * Generate HD AI animation asynchronously (returns task_id for polling)
   */
  async generateHdVideoAsync(payload: {
    prompt: string;
    provider?: string;
    model?: string;
    num_frames?: number;
    guidance_scale?: number;
    num_inference_steps?: number;
    negative_prompt?: string;
    seed?: number;
  }): Promise<{ task_id: string; status: string; message: string }> {
    const response = await aiApiClient.post<{ task_id: string; status: string; message: string }>(
      "/api/story/hd-video-async",
      {
        provider: "huggingface",
        ...payload,
      }
    );
    return response.data;
  }

  /**
   * Generate HD AI video for a single scene with AI-enhanced prompt
   */
  async generateHdVideoScene(payload: {
    scene_number: number;
    scene_data: StoryScene;
    story_context: Record<string, any>;
    all_scenes: StoryScene[];
    provider?: string;
    model?: string;
    num_frames?: number;
    guidance_scale?: number;
    num_inference_steps?: number;
    negative_prompt?: string;
    seed?: number;
  }): Promise<{
    success: boolean;
    scene_number: number;
    video_filename: string;
    video_url: string;
    prompt_used: string;
    provider: string;
    model: string;
  }> {
    // Long-running request - use longRunningApiClient to allow more time
    const { longRunningApiClient } = await import("../api/client");
    const response = await longRunningApiClient.post(
      "/api/story/hd-video-scene",
      {
        provider: "huggingface",
        ...payload,
      }
    );
    return response.data;
  }

  /**
   * Get video URL for a story video file
   */
  getVideoUrl(videoUrl: string): string {
    // If videoUrl is already a full URL, return it as-is
    if (videoUrl.startsWith('http://') || videoUrl.startsWith('https://')) {
      return videoUrl;
    }
    // Otherwise, prepend the base URL
    const baseURL = aiApiClient.defaults.baseURL || '';
    // Remove trailing slash from baseURL if present, and leading slash from videoUrl if present
    const cleanBaseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL;
    const cleanVideoUrl = videoUrl.startsWith('/') ? videoUrl : `/${videoUrl}`;
    return `${cleanBaseURL}${cleanVideoUrl}`;
  }
}

export const storyWriterApi = new StoryWriterApi();
