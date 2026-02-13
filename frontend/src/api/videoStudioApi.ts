/**
 * Video Studio API Client
 */

import { aiApiClient } from './client';
// Import TaskStatusResponse from blogWriterApi to ensure compatibility with usePolling
import type { TaskStatusResponse } from '../services/blogWriterApi';

const API_BASE = '/api/video-studio';

export interface PromptOptimizeRequest {
  text: string;
  mode?: 'image' | 'video';
  style?: 'default' | 'artistic' | 'photographic' | 'technical' | 'anime' | 'realistic';
  image?: string;
}

export interface PromptOptimizeResponse {
  optimized_prompt: string;
  success: boolean;
}

export interface CreateAvatarVideoResponse {
  task_id: string;
  status: string;
  message: string;
  error?: string;
  result?: {
      video_url: string;
      [key: string]: any;
  };
}

/**
 * Optimize a prompt using WaveSpeed prompt optimizer
 */
export async function optimizePrompt(
  request: PromptOptimizeRequest
): Promise<PromptOptimizeResponse> {
  const response = await aiApiClient.post<PromptOptimizeResponse>(
    `${API_BASE}/optimize-prompt`,
    request
  );
  return response.data;
}

/**
 * Create a talking avatar video asynchronously
 * Uses dedicated Video Studio endpoint for generic avatar generation
 */
export async function createAvatarVideoAsync(
  imageFile: File,
  audioFile: File,
  resolution: '480p' | '720p' = '720p',
  model: 'infinitetalk' | 'hunyuan-avatar' = 'infinitetalk'
): Promise<CreateAvatarVideoResponse> {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('audio', audioFile);
  formData.append('resolution', resolution);
  formData.append('model', model);

  try {
    const response = await aiApiClient.post<CreateAvatarVideoResponse>(
      `${API_BASE}/avatar/create-async`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error: any) {
    console.error('Error creating avatar video:', error);
    throw new Error(error.response?.data?.detail || 'Failed to create avatar video');
  }
}

/**
 * Get the status of a video generation task
 */
export async function getVideoTaskStatus(taskId: string): Promise<CreateAvatarVideoResponse> {
    try {
        const response = await aiApiClient.get<CreateAvatarVideoResponse>(
            `${API_BASE}/task/${taskId}`
        );
        return response.data;
    } catch (error: any) {
        console.error('Error fetching video task status:', error);
        throw new Error(error.response?.data?.detail || 'Failed to fetch task status');
    }
}

/**
 * Poll video task status compatible with usePolling hook
 */
export async function pollVideoTaskStatus(taskId: string): Promise<TaskStatusResponse<{ video_url: string; [key: string]: any }>> {
  const data = await getVideoTaskStatus(taskId);
  
  // Map CreateAvatarVideoResponse to TaskStatusResponse
  // Ensure we map 'processing' to 'running' for frontend consistency
  let status: 'pending' | 'running' | 'completed' | 'failed' = 'pending';
  
  if (data.status === 'completed') status = 'completed';
  else if (data.status === 'failed') status = 'failed';
  else if (data.status === 'running' || data.status === 'processing') status = 'running';
  else status = 'pending';

  return {
    task_id: data.task_id,
    status: status,
    progress_messages: [], // Video Studio currently doesn't return progress messages
    result: data.result,
    error: data.error,
    // Add default values for missing fields
    created_at: new Date().toISOString(),
  };
}
