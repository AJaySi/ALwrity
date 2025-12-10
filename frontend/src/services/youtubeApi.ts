// YouTube Creator Studio API Client

import { apiClient } from '../api/client';

const API_BASE = '/api/youtube';

export interface VideoPlanRequest {
  user_idea: string;
  duration_type: 'shorts' | 'medium' | 'long';
  reference_image_description?: string;
  source_content_id?: string;
  source_content_type?: 'blog' | 'story';
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
};
