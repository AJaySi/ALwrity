/**
 * Video Studio API Client
 */

import { aiApiClient } from './client';

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
