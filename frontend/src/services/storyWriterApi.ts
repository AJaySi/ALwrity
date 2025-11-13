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
  image_urls: string[];
  audio_urls: string[];
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
   * Get image URL for a scene image
   */
  getImageUrl(imageUrl: string): string {
    // If imageUrl is already a full URL, return it as-is
    if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
      return imageUrl;
    }
    // Otherwise, prepend the base URL
    const baseURL = aiApiClient.defaults.baseURL || '';
    // Remove trailing slash from baseURL if present, and leading slash from imageUrl if present
    const cleanBaseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL;
    const cleanImageUrl = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
    return `${cleanBaseURL}${cleanImageUrl}`;
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
