import { useState, useCallback } from 'react';
import { aiApiClient } from '../api/client';

export interface ImageGenerationRequest {
  prompt: string;
  template_id?: string | null;
  provider?: string;
  model?: string | null;
  width?: number | null;
  height?: number | null;
  aspect_ratio?: string | null;
  style_preset?: string | null;
  quality?: 'draft' | 'standard' | 'premium';
  negative_prompt?: string;
  guidance_scale?: number | null;
  steps?: number | null;
  seed?: number | null;
  num_variations?: number;
  enhance_prompt?: boolean;
  use_persona?: boolean;
  persona_id?: string | null;
}

export interface ImageResult {
  image_base64: string;
  width: number;
  height: number;
  provider: string;
  model: string;
  seed?: number;
  variation: number;
  metadata?: any;
}

export interface GenerationResponse {
  success: boolean;
  request: any;
  results: ImageResult[];
  total_generated: number;
  total_failed: number;
}

export interface Template {
  id: string;
  name: string;
  category: string;
  platform?: string;
  aspect_ratio: {
    ratio: string;
    width: number;
    height: number;
    label: string;
  };
  description: string;
  recommended_provider: string;
  style_preset: string;
  quality: string;
  use_cases: string[];
}

export interface Provider {
  name: string;
  models: string[];
  capabilities: string[];
  max_resolution: number[];
  cost_range: string;
}

export interface CostEstimate {
  provider: string;
  model?: string;
  operation: string;
  num_images: number;
  resolution?: string;
  cost_per_image: number;
  total_cost: number;
  currency: string;
  estimated: boolean;
}

export interface CostEstimateRequest {
  provider: string;
  model?: string;
  operation: string;
  num_images: number;
  width?: number;
  height?: number;
}

export interface EditOperationMeta {
  label: string;
  description: string;
  provider: string;
  async?: boolean;
  fields?: {
    prompt?: boolean;
    mask?: boolean;
    negative_prompt?: boolean;
    search_prompt?: boolean;
    select_prompt?: boolean;
    background?: boolean;
    lighting?: boolean;
    expansion?: boolean;
  };
}

export interface EditImageRequestPayload {
  image_base64: string;
  operation: string;
  prompt?: string;
  negative_prompt?: string;
  mask_base64?: string;
  search_prompt?: string;
  select_prompt?: string;
  background_image_base64?: string;
  lighting_image_base64?: string;
  expand_left?: number;
  expand_right?: number;
  expand_up?: number;
  expand_down?: number;
  provider?: string;
  model?: string;
  style_preset?: string;
  guidance_scale?: number;
  steps?: number;
  seed?: number;
  output_format?: string;
  options?: Record<string, any>;
}

export interface EditResult {
  success: boolean;
  operation: string;
  provider: string;
  image_base64: string;
  width: number;
  height: number;
  metadata: Record<string, any>;
}

export interface UpscaleRequestPayload {
  image_base64: string;
  mode?: 'fast' | 'conservative' | 'creative' | 'auto';
  target_width?: number;
  target_height?: number;
  preset?: string;
  prompt?: string;
}

export interface UpscaleResult {
  success: boolean;
  mode: string;
  image_base64: string;
  width: number;
  height: number;
  metadata: Record<string, any>;
}

export interface ControlOperationMeta {
  label: string;
  description: string;
  provider: string;
  fields?: {
    control_image?: boolean;
    style_image?: boolean;
    control_strength?: boolean;
    fidelity?: boolean;
    style_strength?: boolean;
    aspect_ratio?: boolean;
  };
}

export interface ControlImageRequestPayload {
  control_image_base64: string;
  operation: 'sketch' | 'structure' | 'style' | 'style_transfer';
  prompt: string;
  style_image_base64?: string;
  negative_prompt?: string;
  control_strength?: number;
  fidelity?: number;
  style_strength?: number;
  composition_fidelity?: number;
  change_strength?: number;
  aspect_ratio?: string;
  style_preset?: string;
  seed?: number;
  output_format?: string;
}

export interface ControlResult {
  success: boolean;
  operation: string;
  provider: string;
  image_base64: string;
  width: number;
  height: number;
  metadata: Record<string, any>;
}

export interface SocialOptimizeResult {
  success: boolean;
  results: Array<{
    platform: string;
    format: string;
    width: number;
    height: number;
    ratio: string;
    image_base64: string;
    safe_zone: {
      top: number;
      bottom: number;
      left: number;
      right: number;
    };
  }>;
  total_optimized: number;
}

export interface PlatformFormat {
  name: string;
  width: number;
  height: number;
  ratio: string;
  safe_zone: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  file_type: string;
  max_size_mb: number;
}

export const useImageStudio = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [providers, setProviders] = useState<Record<string, Provider> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [results, setResults] = useState<ImageResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [costEstimate, setCostEstimate] = useState<CostEstimate | null>(null);
  const [editOperations, setEditOperations] = useState<Record<string, EditOperationMeta>>({});
  const [isLoadingEditOps, setIsLoadingEditOps] = useState(false);
  const [isProcessingEdit, setIsProcessingEdit] = useState(false);
  const [editResult, setEditResult] = useState<EditResult | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  const [upscaleResult, setUpscaleResult] = useState<UpscaleResult | null>(null);
  const [isUpscaling, setIsUpscaling] = useState(false);
  const [upscaleError, setUpscaleError] = useState<string | null>(null);
  const [controlOperations, setControlOperations] = useState<Record<string, ControlOperationMeta>>({});
  const [isLoadingControlOps, setIsLoadingControlOps] = useState(false);
  const [isProcessingControl, setIsProcessingControl] = useState(false);
  const [controlResult, setControlResult] = useState<ControlResult | null>(null);
  const [controlError, setControlError] = useState<string | null>(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizeResult, setOptimizeResult] = useState<SocialOptimizeResult | null>(null);
  const [optimizeError, setOptimizeError] = useState<string | null>(null);

  // Load templates
  const loadTemplates = useCallback(async (platform?: string, category?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (platform) params.append('platform', platform);
      if (category) params.append('category', category);
      
      const response = await aiApiClient.get(
        `/api/image-studio/templates?${params.toString()}`
      );
      
      setTemplates(response.data.templates || []);
    } catch (err: any) {
      console.error('Failed to load templates:', err);
      setError(err.response?.data?.detail || 'Failed to load templates');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Search templates
  const searchTemplates = useCallback(async (query: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await aiApiClient.get(
        `/api/image-studio/templates/search?query=${encodeURIComponent(query)}`
      );
      
      setTemplates(response.data.templates || []);
    } catch (err: any) {
      console.error('Failed to search templates:', err);
      setError(err.response?.data?.detail || 'Failed to search templates');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load providers
  const loadProviders = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await aiApiClient.get('/api/image-studio/providers');
      setProviders(response.data.providers || {});
    } catch (err: any) {
      console.error('Failed to load providers:', err);
      setError(err.response?.data?.detail || 'Failed to load providers');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Generate image
  const generateImage = useCallback(async (request: ImageGenerationRequest): Promise<GenerationResponse | null> => {
    setIsGenerating(true);
    setError(null);
    
    try {
      const response = await aiApiClient.post('/api/image-studio/create', request);
      
      if (response.data.success) {
        setResults(response.data.results || []);
        return response.data;
      } else {
        throw new Error('Generation failed');
      }
    } catch (err: any) {
      console.error('Failed to generate image:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to generate image';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  }, []);

  // Estimate cost
  const estimateCost = useCallback(async (request: CostEstimateRequest) => {
    try {
      const response = await aiApiClient.post('/api/image-studio/estimate-cost', request);
      setCostEstimate(response.data);
      return response.data;
    } catch (err: any) {
      console.error('Failed to estimate cost:', err);
      // Don't set error for cost estimation failures
      return null;
    }
  }, []);

  // Get platform specs
  const getPlatformSpecs = useCallback(async (platform: string) => {
    try {
      const response = await aiApiClient.get(`/api/image-studio/platform-specs/${platform}`);
      return response.data;
    } catch (err: any) {
      console.error('Failed to get platform specs:', err);
      return null;
    }
  }, []);

  // Clear results
  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load edit operations metadata
  const loadEditOperations = useCallback(async () => {
    setIsLoadingEditOps(true);
    setEditError(null);
    try {
      const response = await aiApiClient.get('/api/image-studio/edit/operations');
      setEditOperations(response.data.operations || {});
    } catch (err: any) {
      console.error('Failed to load edit operations:', err);
      setEditError(err.response?.data?.detail || 'Failed to load edit operations');
    } finally {
      setIsLoadingEditOps(false);
    }
  }, []);

  // Process edit request
  const processEdit = useCallback(async (payload: EditImageRequestPayload) => {
    setIsProcessingEdit(true);
    setEditError(null);
    try {
      const response = await aiApiClient.post('/api/image-studio/edit/process', payload);
      setEditResult(response.data);
      return response.data as EditResult;
    } catch (err: any) {
      console.error('Failed to process edit:', err);
      const message = err.response?.data?.detail || 'Failed to process edit';
      setEditError(message);
      throw new Error(message);
    } finally {
      setIsProcessingEdit(false);
    }
  }, []);

  const clearEditResult = useCallback(() => {
    setEditResult(null);
    setEditError(null);
  }, []);

  // Process upscale
  const processUpscale = useCallback(async (payload: UpscaleRequestPayload) => {
    setIsUpscaling(true);
    setUpscaleError(null);
    try {
      const response = await aiApiClient.post('/api/image-studio/upscale', payload);
      setUpscaleResult(response.data);
      return response.data as UpscaleResult;
    } catch (err: any) {
      console.error('Failed to upscale image:', err);
      const message = err.response?.data?.detail || 'Failed to upscale image';
      setUpscaleError(message);
      throw new Error(message);
    } finally {
      setIsUpscaling(false);
    }
  }, []);

  const clearUpscaleResult = useCallback(() => {
    setUpscaleResult(null);
    setUpscaleError(null);
  }, []);

  // Load control operations
  const loadControlOperations = useCallback(async () => {
    setIsLoadingControlOps(true);
    try {
      const response = await aiApiClient.get('/api/image-studio/control/operations');
      setControlOperations(response.data.operations || {});
    } catch (err: any) {
      console.error('Failed to load control operations:', err);
    } finally {
      setIsLoadingControlOps(false);
    }
  }, []);

  // Process control
  const processControl = useCallback(async (payload: ControlImageRequestPayload) => {
    setIsProcessingControl(true);
    setControlError(null);
    try {
      const response = await aiApiClient.post('/api/image-studio/control/process', payload);
      setControlResult(response.data);
      return response.data as ControlResult;
    } catch (err: any) {
      console.error('Failed to process control:', err);
      const message = err.response?.data?.detail || 'Failed to process control';
      setControlError(message);
      throw new Error(message);
    } finally {
      setIsProcessingControl(false);
    }
  }, []);

  const clearControlResult = useCallback(() => {
    setControlResult(null);
    setControlError(null);
  }, []);

  // Social Optimizer
  const optimizeForSocial = useCallback(async (payload: {
    image_base64: string;
    platforms: string[];
    format_names?: Record<string, string>;
    show_safe_zones?: boolean;
    crop_mode?: string;
    focal_point?: { x: number; y: number };
    output_format?: string;
  }) => {
    setIsOptimizing(true);
    setOptimizeError(null);
    try {
      const response = await aiApiClient.post('/api/image-studio/social/optimize', payload);
      setOptimizeResult(response.data);
      return response.data as SocialOptimizeResult;
    } catch (err: any) {
      console.error('Failed to optimize for social:', err);
      const message = err.response?.data?.detail || 'Failed to optimize for social platforms';
      setOptimizeError(message);
      throw new Error(message);
    } finally {
      setIsOptimizing(false);
    }
  }, []);

  const getPlatformFormats = useCallback(async (platform: string): Promise<PlatformFormat[]> => {
    try {
      const response = await aiApiClient.get(`/api/image-studio/social/platforms/${platform}/formats`);
      return response.data.formats || [];
    } catch (err: any) {
      console.error(`Failed to load formats for ${platform}:`, err);
      return [];
    }
  }, []);

  const clearOptimizeResult = useCallback(() => {
    setOptimizeResult(null);
    setOptimizeError(null);
  }, []);

  return {
    // State
    templates,
    providers,
    isLoading,
    isGenerating,
    results,
    error,
    costEstimate,
    editOperations,
    isLoadingEditOps,
    isProcessingEdit,
    editResult,
    editError,
    upscaleResult,
    isUpscaling,
    upscaleError,
    controlOperations,
    isLoadingControlOps,
    isProcessingControl,
    controlResult,
    controlError,
    
    // Actions
    loadTemplates,
    searchTemplates,
    loadProviders,
    generateImage,
    estimateCost,
    getPlatformSpecs,
    clearResults,
    clearError,
    loadEditOperations,
    processEdit,
    clearEditResult,
    processUpscale,
    clearUpscaleResult,
    loadControlOperations,
    processControl,
    clearControlResult,
    optimizeForSocial,
    getPlatformFormats,
    isOptimizing,
    optimizeResult,
    optimizeError,
    clearOptimizeResult,
  };
};

