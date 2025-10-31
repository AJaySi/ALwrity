import { useCallback, useState } from 'react';
import { apiClient } from '../../api/client';

export interface ImageGenerationRequest {
  prompt: string;
  negative_prompt?: string;
  provider?: 'gemini' | 'huggingface' | 'stability';
  model?: string;
  width?: number;
  height?: number;
  guidance_scale?: number;
  steps?: number;
  seed?: number;
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
    try {
      const { data } = await apiClient.post<ImageGenerationResponse>('/api/images/generate', req);
      setResult(data);
      return data;
    } catch (e: any) {
      const message = e?.response?.data?.detail || e?.message || 'Image generation failed';
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

export async function fetchPromptSuggestions(payload: any): Promise<PromptSuggestion[]> {
  const res = await fetch('/api/images/suggest-prompts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to fetch prompt suggestions');
  }
  const data = await res.json();
  return data.suggestions || [];
}


