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

export interface EditingModel {
  id: string;
  name: string;
  description: string;
  cost: number;
  cost_8k?: number;
  tier: 'budget' | 'mid' | 'premium';
  max_resolution: [number, number];
  capabilities: string[];
  use_cases: string[];
  features: string[];
  supports_multi_image: boolean;
  supports_controlnet: boolean;
  languages: string[];
  api_params?: {
    uses_size?: boolean;
    uses_aspect_ratio?: boolean;
    uses_resolution?: boolean;
    supports_guidance_scale?: boolean;
    supports_seed?: boolean;
  };
}

export interface ModelRecommendation {
  recommended_model: string;
  reason: string;
  alternatives: Array<{
    model_id: string;
    name: string;
    cost: number;
    reason: string;
  }>;
}

export interface FaceSwapModel {
  id: string;
  name: string;
  description: string;
  cost: number;
  tier: 'budget' | 'mid' | 'premium';
  capabilities: string[];
  use_cases: string[];
  features: string[];
  max_faces: number;
}

export interface FaceSwapModelRecommendation {
  recommended_model: string;
  reason: string;
  alternatives: Array<{
    model_id: string;
    name: string;
    cost: number;
    reason: string;
  }>;
}

export interface FaceSwapRequestPayload {
  base_image_base64: string;
  face_image_base64: string;
  model?: string;
  target_face_index?: number;
  target_gender?: string;
  options?: Record<string, any>;
}

export interface FaceSwapResult {
  success: boolean;
  image_base64: string;
  width: number;
  height: number;
  provider: string;
  model: string;
  metadata: Record<string, any>;
}

// Compression types
export interface CompressionRequest {
  image_base64: string;
  quality: number;
  format: string;
  target_size_kb?: number;
  strip_metadata: boolean;
  progressive: boolean;
  optimize: boolean;
}

export interface CompressionResult {
  success: boolean;
  image_base64: string;
  original_size_kb: number;
  compressed_size_kb: number;
  compression_ratio: number;
  format: string;
  width: number;
  height: number;
  quality_used: number;
  metadata_stripped: boolean;
}

export interface CompressionFormat {
  id: string;
  name: string;
  extension: string;
  description: string;
  supports_transparency: boolean;
  quality_range: [number, number];
  recommended_quality: number;
  use_cases: string[];
}

export interface CompressionPreset {
  id: string;
  name: string;
  description: string;
  format: string;
  quality: number;
  target_size_kb?: number;
  strip_metadata: boolean;
}

export interface CompressionEstimate {
  original_size_kb: number;
  estimated_size_kb: number;
  estimated_reduction_percent: number;
  width: number;
  height: number;
  format: string;
}

// Format Converter types
export interface FormatConversionRequest {
  image_base64: string;
  target_format: string;
  preserve_transparency: boolean;
  quality?: number;
  color_space?: string;
  strip_metadata: boolean;
  optimize: boolean;
  progressive: boolean;
}

export interface FormatConversionResult {
  success: boolean;
  image_base64: string;
  original_format: string;
  target_format: string;
  original_size_kb: number;
  converted_size_kb: number;
  width: number;
  height: number;
  transparency_preserved: boolean;
  metadata_preserved: boolean;
  color_space?: string;
}

export interface SupportedFormat {
  id: string;
  name: string;
  description: string;
  supports_transparency: boolean;
  supports_lossy: boolean;
  mime_type: string;
}

export interface FormatRecommendation {
  format: string;
  reason: string;
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

  // Edit model selection state
  const [editModels, setEditModels] = useState<EditingModel[]>([]);
  const [isLoadingEditModels, setIsLoadingEditModels] = useState(false);
  const [modelRecommendation, setModelRecommendation] = useState<ModelRecommendation | null>(null);
  const [isLoadingRecommendation, setIsLoadingRecommendation] = useState(false);

  // Face swap state
  const [faceSwapModels, setFaceSwapModels] = useState<FaceSwapModel[]>([]);
  const [isLoadingFaceSwapModels, setIsLoadingFaceSwapModels] = useState(false);
  const [faceSwapModelRecommendation, setFaceSwapModelRecommendation] = useState<FaceSwapModelRecommendation | null>(null);
  const [isLoadingFaceSwapRecommendation, setIsLoadingFaceSwapRecommendation] = useState(false);
  const [isProcessingFaceSwap, setIsProcessingFaceSwap] = useState(false);
  const [faceSwapResult, setFaceSwapResult] = useState<FaceSwapResult | null>(null);
  const [faceSwapError, setFaceSwapError] = useState<string | null>(null);

  // Compression state
  const [compressionFormats, setCompressionFormats] = useState<CompressionFormat[]>([]);
  const [compressionPresets, setCompressionPresets] = useState<CompressionPreset[]>([]);
  const [isCompressing, setIsCompressing] = useState(false);
  const [compressionResult, setCompressionResult] = useState<CompressionResult | null>(null);
  const [compressionError, setCompressionError] = useState<string | null>(null);
  const [compressionEstimate, setCompressionEstimate] = useState<CompressionEstimate | null>(null);

  // Format Converter state
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormat[]>([]);
  const [isConvertingFormat, setIsConvertingFormat] = useState(false);
  const [formatConversionResult, setFormatConversionResult] = useState<FormatConversionResult | null>(null);
  const [formatConversionError, setFormatConversionError] = useState<string | null>(null);
  const [formatRecommendations, setFormatRecommendations] = useState<FormatRecommendation[]>([]);

  // Load available editing models
  const loadEditModels = useCallback(async (operation?: string, tier?: string) => {
    setIsLoadingEditModels(true);
    try {
      const params = new URLSearchParams();
      if (operation) params.append('operation', operation);
      if (tier) params.append('tier', tier);
      
      const response = await aiApiClient.get(`/api/image-studio/edit/models?${params.toString()}`);
      setEditModels(response.data.models || []);
      return response.data.models || [];
    } catch (err: any) {
      console.error('Failed to load edit models:', err);
      return [];
    } finally {
      setIsLoadingEditModels(false);
    }
  }, []);

  // Get model recommendation
  const getModelRecommendation = useCallback(async (
    operation: string,
    imageResolution?: { width: number; height: number },
    userTier?: string,
    preferences?: { prioritize_cost?: boolean; prioritize_quality?: boolean }
  ) => {
    setIsLoadingRecommendation(true);
    try {
      const response = await aiApiClient.post('/api/image-studio/edit/recommend', {
        operation,
        image_resolution: imageResolution,
        user_tier: userTier,
        preferences,
      });
      setModelRecommendation(response.data);
      return response.data;
    } catch (err: any) {
      console.error('Failed to get model recommendation:', err);
      return null;
    } finally {
      setIsLoadingRecommendation(false);
    }
  }, []);

  // Load face swap models
  const loadFaceSwapModels = useCallback(async (tier?: string) => {
    setIsLoadingFaceSwapModels(true);
    try {
      const params = new URLSearchParams();
      if (tier) params.append('tier', tier);
      
      const response = await aiApiClient.get(`/api/image-studio/face-swap/models?${params.toString()}`);
      setFaceSwapModels(response.data.models || []);
      return response.data.models || [];
    } catch (err: any) {
      console.error('Failed to load face swap models:', err);
      return [];
    } finally {
      setIsLoadingFaceSwapModels(false);
    }
  }, []);

  // Get face swap model recommendation
  const getFaceSwapModelRecommendation = useCallback(async (
    baseImageResolution?: { width: number; height: number },
    faceImageResolution?: { width: number; height: number },
    userTier?: string,
    preferences?: { prioritize_cost?: boolean; prioritize_quality?: boolean }
  ) => {
    setIsLoadingFaceSwapRecommendation(true);
    try {
      const response = await aiApiClient.post('/api/image-studio/face-swap/recommend', {
        base_image_resolution: baseImageResolution,
        face_image_resolution: faceImageResolution,
        user_tier: userTier,
        preferences,
      });
      setFaceSwapModelRecommendation(response.data);
      return response.data;
    } catch (err: any) {
      console.error('Failed to get face swap model recommendation:', err);
      return null;
    } finally {
      setIsLoadingFaceSwapRecommendation(false);
    }
  }, []);

  // Process face swap
  const processFaceSwap = useCallback(async (payload: FaceSwapRequestPayload) => {
    setIsProcessingFaceSwap(true);
    setFaceSwapError(null);
    try {
      const response = await aiApiClient.post('/api/image-studio/face-swap/process', payload);
      setFaceSwapResult(response.data);
      return response.data as FaceSwapResult;
    } catch (err: any) {
      console.error('Failed to process face swap:', err);
      const message = err.response?.data?.detail || 'Failed to process face swap';
      setFaceSwapError(message);
      throw new Error(message);
    } finally {
      setIsProcessingFaceSwap(false);
    }
  }, []);

  const clearFaceSwapResult = useCallback(() => {
    setFaceSwapResult(null);
    setFaceSwapError(null);
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

  // Load compression formats
  const loadCompressionFormats = useCallback(async () => {
    try {
      const response = await aiApiClient.get('/api/image-studio/compress/formats');
      setCompressionFormats(response.data.formats || []);
      return response.data.formats || [];
    } catch (err: any) {
      console.error('Failed to load compression formats:', err);
      return [];
    }
  }, []);

  // Load compression presets
  const loadCompressionPresets = useCallback(async () => {
    try {
      const response = await aiApiClient.get('/api/image-studio/compress/presets');
      setCompressionPresets(response.data.presets || []);
      return response.data.presets || [];
    } catch (err: any) {
      console.error('Failed to load compression presets:', err);
      return [];
    }
  }, []);

  // Estimate compression
  const estimateCompression = useCallback(async (
    image_base64: string,
    format: string = 'jpeg',
    quality: number = 85,
  ): Promise<CompressionEstimate | null> => {
    try {
      const response = await aiApiClient.post('/api/image-studio/compress/estimate', {
        image_base64,
        format,
        quality,
      });
      setCompressionEstimate(response.data);
      return response.data;
    } catch (err: any) {
      console.error('Failed to estimate compression:', err);
      return null;
    }
  }, []);

  // Process compression
  const processCompression = useCallback(async (request: CompressionRequest): Promise<CompressionResult> => {
    setIsCompressing(true);
    setCompressionError(null);
    try {
      const response = await aiApiClient.post('/api/image-studio/compress', request);
      setCompressionResult(response.data);
      return response.data;
    } catch (err: any) {
      console.error('Failed to compress image:', err);
      const message = err.response?.data?.detail || 'Failed to compress image';
      setCompressionError(message);
      throw new Error(message);
    } finally {
      setIsCompressing(false);
    }
  }, []);

  const clearCompressionResult = useCallback(() => {
    setCompressionResult(null);
    setCompressionError(null);
    setCompressionEstimate(null);
  }, []);

  // Load supported formats
  const loadSupportedFormats = useCallback(async () => {
    try {
      const response = await aiApiClient.get('/api/image-studio/convert-format/supported');
      setSupportedFormats(response.data.formats || []);
      return response.data.formats || [];
    } catch (err: any) {
      console.error('Failed to load supported formats:', err);
      return [];
    }
  }, []);

  // Get format recommendations
  const getFormatRecommendations = useCallback(async (sourceFormat: string): Promise<FormatRecommendation[]> => {
    try {
      const response = await aiApiClient.get(`/api/image-studio/convert-format/recommendations?source_format=${sourceFormat}`);
      setFormatRecommendations(response.data.recommendations || []);
      return response.data.recommendations || [];
    } catch (err: any) {
      console.error('Failed to get format recommendations:', err);
      return [];
    }
  }, []);

  // Process format conversion
  const processFormatConversion = useCallback(async (request: FormatConversionRequest): Promise<FormatConversionResult> => {
    setIsConvertingFormat(true);
    setFormatConversionError(null);
    try {
      const response = await aiApiClient.post('/api/image-studio/convert-format', request);
      setFormatConversionResult(response.data);
      return response.data;
    } catch (err: any) {
      console.error('Failed to convert format:', err);
      const message = err.response?.data?.detail || 'Failed to convert image format';
      setFormatConversionError(message);
      throw new Error(message);
    } finally {
      setIsConvertingFormat(false);
    }
  }, []);

  const clearFormatConversionResult = useCallback(() => {
    setFormatConversionResult(null);
    setFormatConversionError(null);
    setFormatRecommendations([]);
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
    // Edit model selection
    editModels,
    isLoadingEditModels,
    loadEditModels,
    modelRecommendation,
    isLoadingRecommendation,
    getModelRecommendation,
    // Face swap
    faceSwapModels,
    isLoadingFaceSwapModels,
    loadFaceSwapModels,
    faceSwapModelRecommendation,
    isLoadingFaceSwapRecommendation,
    getFaceSwapModelRecommendation,
    processFaceSwap,
    isProcessingFaceSwap,
    faceSwapResult,
    faceSwapError,
    clearFaceSwapResult,
    // Compression
    compressionFormats,
    compressionPresets,
    loadCompressionFormats,
    loadCompressionPresets,
    estimateCompression,
    processCompression,
    isCompressing,
    compressionResult,
    compressionError,
    compressionEstimate,
    clearCompressionResult,
    // Format Converter
    supportedFormats,
    loadSupportedFormats,
    getFormatRecommendations,
    processFormatConversion,
    isConvertingFormat,
    formatConversionResult,
    formatConversionError,
    formatRecommendations,
    clearFormatConversionResult,
  };
};

