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

export interface TransformJobResponse {
  success: boolean;
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  operation: 'image-to-video' | 'talking-avatar';
  message: string;
}

export interface TransformJobStatusResponse {
  success: boolean;
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  operation: 'image-to-video' | 'talking-avatar';
  progress: number;
  message?: string;
  result?: TransformVideoResponse;
  error?: string;
  created_at: string;
  updated_at: string;
}

const mapTransformError = (err: any): string => {
  const detail = err?.response?.data?.detail || err?.message || 'Operation failed';
  const raw = String(detail).toLowerCase();

  if (raw.includes('timeout') || raw.includes('timed out')) {
    return 'The generation timed out. Try a shorter duration or lower resolution and retry.';
  }
  if (raw.includes('insufficient') || raw.includes('credit') || raw.includes('limit')) {
    return 'You may have reached a plan limit. Check credits/usage and try with a lower-cost option.';
  }
  if (raw.includes('audio')) {
    return 'Audio validation failed. Upload a valid WAV/MP3 file and retry.';
  }
  if (raw.includes('image')) {
    return 'Image validation failed. Try a clearer source image under the size limit.';
  }

  return detail;
};

export const useTransformStudio = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TransformVideoResponse | null>(null);
  const [costEstimate, setCostEstimate] = useState<CostEstimateResponse | null>(null);
  const [job, setJob] = useState<TransformJobStatusResponse | null>(null);

  const pollTransformJob = useCallback(async (jobId: string): Promise<TransformJobStatusResponse> => {
    while (true) {
      const response = await aiApiClient.get<TransformJobStatusResponse>(`/api/image-studio/transform/jobs/${jobId}`);
      const status = response.data;
      setJob(status);

      if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
        return status;
      }

      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  }, []);

  const transformImageToVideo = useCallback(
    async (request: TransformImageToVideoRequest): Promise<TransformVideoResponse> => {
      setIsGenerating(true);
      setError(null);
      setResult(null);

      try {
        const queued = await aiApiClient.post<TransformJobResponse>('/api/image-studio/transform/image-to-video/async', request);
        const status = await pollTransformJob(queued.data.job_id);

        if (status.status !== 'completed' || !status.result) {
          throw new Error(status.error || status.message || 'Failed to generate video');
        }

        setResult(status.result);
        return status.result;
      } catch (err: any) {
        const errorMessage = mapTransformError(err);
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGenerating(false);
      }
    },
    [pollTransformJob]
  );

  const createTalkingAvatar = useCallback(
    async (request: TalkingAvatarRequest): Promise<TransformVideoResponse> => {
      setIsGenerating(true);
      setError(null);
      setResult(null);

      try {
        const queued = await aiApiClient.post<TransformJobResponse>('/api/image-studio/transform/talking-avatar/async', request);
        const status = await pollTransformJob(queued.data.job_id);

        if (status.status !== 'completed' || !status.result) {
          throw new Error(status.error || status.message || 'Failed to create talking avatar');
        }

        setResult(status.result);
        return status.result;
      } catch (err: any) {
        const errorMessage = mapTransformError(err);
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGenerating(false);
      }
    },
    [pollTransformJob]
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
        const errorMessage = mapTransformError(err);
        setError(errorMessage);
        throw new Error(errorMessage);
      }
    },
    []
  );

  const cancelJob = useCallback(async (jobId: string): Promise<void> => {
    await aiApiClient.post(`/api/image-studio/transform/jobs/${jobId}/cancel`);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
    setJob(null);
  }, []);

  return {
    isGenerating,
    error,
    result,
    costEstimate,
    job,
    transformImageToVideo,
    createTalkingAvatar,
    estimateCost,
    cancelJob,
    clearError,
    clearResult,
  };
};
