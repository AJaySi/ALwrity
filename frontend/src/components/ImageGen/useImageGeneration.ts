import { useCallback, useState } from 'react';
import { apiClient, aiApiClient } from '../../api/client';

export interface ImageGenerationRequest {
  prompt: string;
  negative_prompt?: string;
  provider?: 'gemini' | 'huggingface' | 'stability' | 'wavespeed';
  model?: string;
  width?: number;
  height?: number;
  guidance_scale?: number;
  steps?: number;
  seed?: number;
  overlay_text?: string;
}

export interface ImageGenerationResponse {
  success: boolean;
  image_base64: string;
  width: number;
  height: number;
  provider: string;
  model?: string;
  seed?: number;
}

export function useImageGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ImageGenerationResponse | null>(null);

  const generate = useCallback(async (req: ImageGenerationRequest) => {
    setIsGenerating(true);
    setError(null);
    setResult(null);
    try {
      const response = await apiClient.post<ImageGenerationResponse>('/api/images/generate', req);
      const data = response.data;
      
      // Check if response has success field and image data
      if (data && (data.success !== false) && data.image_base64) {
        setResult(data);
        setError(null);
        return data;
      } else {
        // Response received but missing required data
        const message = 'Image generation completed but response is incomplete';
        setError(message);
        throw new Error(message);
      }
    } catch (e: any) {
      // Check if error response contains image data (partial success)
      if (e?.response?.data?.image_base64) {
        // Image was generated but there was an error in post-processing
        const data = e.response.data;
        console.warn('Image generation succeeded but post-processing had issues', data);
        setResult(data);
        setError(null);
        return data;
      }
      
      const message = e?.response?.data?.detail || e?.response?.data?.message || e?.message || 'Image generation failed';
      setError(message);
      throw new Error(message);
    } finally {
      setIsGenerating(false);
    }
  }, []);

  return { isGenerating, error, result, generate };
}

export interface PromptSuggestion {
  prompt: string;
  negative_prompt?: string;
  width?: number;
  height?: number;
  overlay_text?: string;
}

export async function fetchPromptSuggestions(payload: {
  provider?: string;
  model?: string;
  image_type?: string;
  title?: string;
  section?: any;
  research?: any;
  persona?: any;
}): Promise<PromptSuggestion[]> {
  // Use aiApiClient (3-minute timeout) because suggest-prompts calls an LLM
  // which can take 30-60+ seconds to respond via WaveSpeed
  const response = await aiApiClient.post('/api/images/suggest-prompts', payload);
  return response.data.suggestions || [];
}


