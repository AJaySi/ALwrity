// YouTube Creator Studio API Client

import { apiClient, aiApiClient } from '../api/client';

const API_BASE = '/api/youtube';

export interface VideoPlanRequest {
  user_idea: string;
  duration_type: 'shorts' | 'medium' | 'long';
  video_type?: 'tutorial' | 'review' | 'educational' | 'entertainment' | 'vlog' | 'product_demo' | 'reaction' | 'storytelling';
  target_audience?: string;
  video_goal?: string;
  brand_style?: string;
  reference_image_description?: string;
  source_content_id?: string;
  source_content_type?: 'blog' | 'story';
  avatar_url?: string;
}

export interface VideoPlan {
  video_summary: string;
  target_audience: string;
  video_goal?: string;
  key_message?: string;
  content_outline: Array<{
    section: string;
    description: string;
    duration_estimate: number;
  }>;
  hook_strategy: string;
  call_to_action?: string;
  cta_ideas?: string[];
  visual_style: string;
  tone?: string;
  seo_keywords: string[];
  duration_type: string;
  estimated_duration?: string;
  auto_generated_avatar_url?: string;
  avatar_reused?: boolean; // Flag indicating if avatar was reused from asset library
  avatar_recommendations?: {
    description?: string;
    style?: string;
    energy?: string;
  };
  avatar_prompt?: string; // AI prompt used to generate the avatar
}

export interface Scene {
  scene_number: number;
  title: string;
  narration: string;
  visual_prompt: string;
  enhanced_visual_prompt?: string;
  duration_estimate: number;
  visual_cues: string[];
  emphasis_tags: string[];
  enabled?: boolean;
}

export interface VideoRenderRequest {
  scenes: Scene[];
  video_plan: VideoPlan;
  resolution?: '480p' | '720p' | '1080p';
  combine_scenes?: boolean;
  voice_id?: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: any;
  error?: string;
}

export interface CostEstimateRequest {
  scenes: Scene[];
  resolution: '480p' | '720p' | '1080p';
}

export interface CostEstimate {
  resolution: string;
  price_per_second: number;
  num_scenes: number;
  total_duration_seconds: number;
  scene_costs: Array<{
    scene_number: number;
    duration_estimate: number;
    actual_duration: number;
    cost: number;
  }>;
  total_cost: number;
  estimated_cost_range: {
    min: number;
    max: number;
  };
}

export interface CostEstimateResponse {
  success: boolean;
  estimate?: CostEstimate;
  message: string;
}

export interface AvatarUploadResponse {
  avatar_url: string;
  avatar_filename: string;
  message: string;
}

export interface AvatarTransformResponse {
  avatar_url: string;
  avatar_filename: string;
  avatar_prompt?: string;
  message: string;
}

export interface SceneImageRequest {
  sceneId: string;
  sceneTitle?: string;
  sceneContent?: string;
  baseAvatarUrl?: string;
  idea?: string;
  width?: number;
  height?: number;
  customPrompt?: string;
  style?: string;
  renderingSpeed?: string;
  aspectRatio?: string;
}

export interface SceneImageResponse {
  scene_id: string;
  scene_title?: string;
  image_filename: string;
  image_url: string;
  width: number;
  height: number;
}

export const youtubeApi = {
  /**
   * Generate a video plan from user input.
   */
  async createPlan(request: VideoPlanRequest): Promise<{ success: boolean; plan?: VideoPlan; message: string }> {
    try {
      const response = await apiClient.post(`${API_BASE}/plan`, request);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to create video plan';
      throw new Error(errorMessage);
    }
  },

  /**
   * Build scenes from a video plan.
   */
  async buildScenes(videoPlan: VideoPlan, customScript?: string): Promise<{ success: boolean; scenes?: Scene[]; message: string }> {
    try {
      const response = await apiClient.post(`${API_BASE}/scenes`, {
        video_plan: videoPlan,
        custom_script: customScript || undefined,
      });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to build scenes';
      throw new Error(errorMessage);
    }
  },

  /**
   * Update a single scene.
   */
  async updateScene(
    sceneId: number,
    updates: {
      narration?: string;
      visual_description?: string;
      duration_estimate?: number;
      enabled?: boolean;
    }
  ): Promise<{ success: boolean; scene?: Scene; message: string }> {
    try {
      const response = await apiClient.post(`${API_BASE}/scenes/${sceneId}/update`, updates);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to update scene';
      throw new Error(errorMessage);
    }
  },

  /**
   * Start rendering a video.
   */
  async startRender(request: VideoRenderRequest): Promise<{ success: boolean; task_id?: string; message: string }> {
    try {
      const response = await apiClient.post(`${API_BASE}/render`, request);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to start render';
      throw new Error(errorMessage);
    }
  },

  /**
   * Get render task status.
   */
  async getRenderStatus(taskId: string): Promise<TaskStatus> {
    try {
      const response = await apiClient.get(`${API_BASE}/render/${taskId}`);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to get render status';
      throw new Error(errorMessage);
    }
  },

  /**
   * Estimate the cost of rendering a video before rendering.
   */
  async estimateCost(request: CostEstimateRequest): Promise<CostEstimateResponse> {
    try {
      const response = await apiClient.post(`${API_BASE}/estimate-cost`, request);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to estimate cost';
      throw new Error(errorMessage);
    }
  },

  /**
   * Get video URL for a generated video.
   */
  getVideoUrl(filename: string): string {
    return `${API_BASE}/videos/${filename}`;
  },

  /**
   * Upload a YouTube avatar image.
   */
  async uploadAvatar(file: File): Promise<AvatarUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiClient.post(`${API_BASE}/avatar/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to upload avatar';
      throw new Error(errorMessage);
    }
  },

  /**
   * Make an uploaded avatar presentable for YouTube.
   */
  async makeAvatarPresentable(
    avatarUrl: string, 
    projectId?: string,
    videoType?: string,
    targetAudience?: string,
    videoGoal?: string,
    brandStyle?: string
  ): Promise<AvatarTransformResponse> {
    try {
      const formData = new FormData();
      formData.append('avatar_url', avatarUrl);
      if (projectId) formData.append('project_id', projectId);
      if (videoType) formData.append('video_type', videoType);
      if (targetAudience) formData.append('target_audience', targetAudience);
      if (videoGoal) formData.append('video_goal', videoGoal);
      if (brandStyle) formData.append('brand_style', brandStyle);
      // Use aiApiClient for longer timeout (image editing takes ~30 seconds)
      const response = await aiApiClient.post(`${API_BASE}/avatar/make-presentable`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to optimize avatar';
      throw new Error(errorMessage);
    }
  },

  /**
   * Auto-generate a YouTube creator avatar.
   */
  async generateCreatorAvatar(params: { projectId?: string; audience?: string; contentType?: string }): Promise<AvatarTransformResponse> {
    try {
      const formData = new FormData();
      if (params.projectId) formData.append('project_id', params.projectId);
      if (params.audience) formData.append('audience', params.audience);
      if (params.contentType) formData.append('content_type', params.contentType);
      const response = await apiClient.post(`${API_BASE}/avatar/generate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to generate avatar';
      throw new Error(errorMessage);
    }
  },

  /**
   * Regenerate a YouTube creator avatar using video plan context.
   */
  async regenerateCreatorAvatar(videoPlan: VideoPlan, projectId?: string): Promise<AvatarTransformResponse> {
    try {
      const formData = new FormData();
      formData.append('video_plan_json', JSON.stringify(videoPlan));
      if (projectId) formData.append('project_id', projectId);

      const response = await aiApiClient.post(`${API_BASE}/avatar/regenerate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to regenerate avatar';
      throw new Error(errorMessage);
    }
  },

  /**
   * Generate a YouTube scene image (with optional avatar consistency).
   */
  async generateSceneImage(params: SceneImageRequest): Promise<SceneImageResponse> {
    try {
      const response = await apiClient.post(`${API_BASE}/image`, {
        scene_id: params.sceneId,
        scene_title: params.sceneTitle,
        scene_content: params.sceneContent,
        base_avatar_url: params.baseAvatarUrl || null,
        idea: params.idea || null,
        width: params.width || 1024,
        height: params.height || 576,
        custom_prompt: params.customPrompt || null,
        style: params.style || null,
        rendering_speed: params.renderingSpeed || null,
        aspect_ratio: params.aspectRatio || null,
      });
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to generate scene image';
      throw new Error(errorMessage);
    }
  },

  /**
   * Get avatar URL for display.
   */
  getAvatarUrl(filename: string): string {
    return `${API_BASE}/images/avatars/${filename}`;
  },

  /**
   * Get scene image URL for display.
   */
  getSceneImageUrl(filename: string): string {
    return `${API_BASE}/images/scenes/${filename}`;
  },
};
