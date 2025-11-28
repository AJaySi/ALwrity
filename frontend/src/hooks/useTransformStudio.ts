import { useState, useCallback } from 'react';
import { aiApiClient } from '../api/client';

export interface TransformImageToVideoRequest {
  image_base64: string;
  prompt: string;
  audio_base64?: string;
  resolution?: '480p' | '720p' | '1080p';
  duration?: 5 | 10;
  negative_prompt?: string;
  seed?: number;
  enable_prompt_expansion?: boolean;
}

export interface TalkingAvatarRequest {
  image_base64: string;
  audio_base64: string;
  resolution?: '480p' | '720p';
  prompt?: string;
  mask_image_base64?: string;
  seed?: number;
}

export interface TransformVideoResponse {
  success: boolean;
  video_url: string;
  video_base64?: string;
  duration: number;
  resolution: string;
  width: number;
  height: number;
  file_size: number;
  cost: number;
  provider: string;
  model: string;
  metadata: Record<string, any>;
}

export interface CostEstimateRequest {
  operation: 'image-to-video' | 'talking-avatar';
  resolution: string;
  duration?: number;
}

export interface CostEstimateResponse {
  estimated_cost: number;
  breakdown: {
    base_cost: number;
    per_second: number;
    duration: number;
    total: number;
  };
  currency: string;
  provider: string;
  model: string;
}

export const useTransformStudio = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TransformVideoResponse | null>(null);
  const [costEstimate, setCostEstimate] = useState<CostEstimateResponse | null>(null);

  const transformImageToVideo = useCallback(
    async (request: TransformImageToVideoRequest): Promise<TransformVideoResponse> => {
      setIsGenerating(true);
      setError(null);
      setResult(null);

      try {
        const response = await aiApiClient.post<TransformVideoResponse>(
          '/api/image-studio/transform/image-to-video',
          request
        );
        setResult(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.detail || err.message || 'Failed to generate video';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGenerating(false);
      }
    },
    []
  );

  const createTalkingAvatar = useCallback(
    async (request: TalkingAvatarRequest): Promise<TransformVideoResponse> => {
      setIsGenerating(true);
      setError(null);
      setResult(null);

      try {
        const response = await aiApiClient.post<TransformVideoResponse>(
          '/api/image-studio/transform/talking-avatar',
          request
        );
        setResult(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.detail || err.message || 'Failed to create talking avatar';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGenerating(false);
      }
    },
    []
  );

  const estimateCost = useCallback(
    async (request: CostEstimateRequest): Promise<CostEstimateResponse> => {
      try {
        const response = await aiApiClient.post<CostEstimateResponse>(
          '/api/image-studio/transform/estimate-cost',
          request
        );
        setCostEstimate(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.detail || err.message || 'Failed to estimate cost';
        setError(errorMessage);
        throw new Error(errorMessage);
      }
    },
    []
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
  }, []);

  return {
    isGenerating,
    error,
    result,
    costEstimate,
    transformImageToVideo,
    createTalkingAvatar,
    estimateCost,
    clearError,
    clearResult,
  };
};

