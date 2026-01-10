import { useState, useCallback } from 'react';
import { aiApiClient } from '../api/client';

/**
 * useProductMarketing Hook
 * 
 * Hook for Product Marketing Suite - Product asset generation only.
 * For campaign management, use useCampaignCreator hook instead.
 */
export const useProductMarketing = () => {
  const [error, setError] = useState<string | null>(null);

  // Product Image Generation (Product Marketing Suite - Product Assets)
  const [isGeneratingProductImage, setIsGeneratingProductImage] = useState(false);
  const [generatedProductImage, setGeneratedProductImage] = useState<any>(null);
  const [productImageError, setProductImageError] = useState<string | null>(null);

  const generateProductImage = useCallback(
    async (request: {
      product_name: string;
      product_description: string;
      environment?: string;
      background_style?: string;
      lighting?: string;
      product_variant?: string;
      angle?: string;
      style?: string;
      resolution?: string;
      num_variations?: number;
      brand_colors?: string[];
      additional_context?: string;
    }): Promise<any> => {
      setIsGeneratingProductImage(true);
      setProductImageError(null);
      try {
        const response = await aiApiClient.post('/api/product-marketing/products/photoshoot', request);
        setGeneratedProductImage(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate product image';
        setProductImageError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGeneratingProductImage(false);
      }
    },
    []
  );

  // Product Animation Generation (Image-to-Video)
  const [isGeneratingAnimation, setIsGeneratingAnimation] = useState(false);
  const [generatedAnimation, setGeneratedAnimation] = useState<any>(null);
  const [animationError, setAnimationError] = useState<string | null>(null);

  const generateProductAnimation = useCallback(
    async (request: {
      product_image_base64: string;
      animation_type: string;
      product_name: string;
      product_description?: string;
      resolution?: string;
      duration?: number;
      audio_base64?: string;
      additional_context?: string;
    }): Promise<any> => {
      setIsGeneratingAnimation(true);
      setAnimationError(null);
      try {
        const response = await aiApiClient.post('/api/product-marketing/products/animate', request);
        setGeneratedAnimation(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate product animation';
        setAnimationError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGeneratingAnimation(false);
      }
    },
    []
  );

  // Product Video Generation (Text-to-Video)
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [generatedVideo, setGeneratedVideo] = useState<any>(null);
  const [videoError, setVideoError] = useState<string | null>(null);

  const generateProductVideo = useCallback(
    async (request: {
      product_name: string;
      product_description: string;
      video_type: string;
      resolution?: string;
      duration?: number;
      audio_base64?: string;
      additional_context?: string;
    }): Promise<any> => {
      setIsGeneratingVideo(true);
      setVideoError(null);
      try {
        const response = await aiApiClient.post('/api/product-marketing/products/video/demo', request);
        setGeneratedVideo(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate product video';
        setVideoError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGeneratingVideo(false);
      }
    },
    []
  );

  // Product Avatar Generation (Talking Avatar)
  const [isGeneratingAvatar, setIsGeneratingAvatar] = useState(false);
  const [generatedAvatar, setGeneratedAvatar] = useState<any>(null);
  const [avatarError, setAvatarError] = useState<string | null>(null);

  const generateProductAvatar = useCallback(
    async (request: {
      avatar_image_base64: string;
      script_text?: string;
      audio_base64?: string;
      product_name: string;
      product_description?: string;
      explainer_type?: string;
      resolution?: string;
      prompt?: string;
      mask_image_base64?: string;
      additional_context?: string;
    }): Promise<any> => {
      setIsGeneratingAvatar(true);
      setAvatarError(null);
      try {
        const response = await aiApiClient.post('/api/product-marketing/products/avatar/explainer', request);
        setGeneratedAvatar(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate product avatar';
        setAvatarError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGeneratingAvatar(false);
      }
    },
    []
  );

  // Intelligent Prompt Inference
  const [isInferringPrompt, setIsInferringPrompt] = useState(false);
  const [inferredConfig, setInferredConfig] = useState<any>(null);
  const [inferenceError, setInferenceError] = useState<string | null>(null);

  // Brand DNA
  const [brandDNA, setBrandDNA] = useState<any>(null);
  const [isLoadingBrandDNA, setIsLoadingBrandDNA] = useState(false);

  // Personalization
  const [userPreferences, setUserPreferences] = useState<any>(null);
  const [isLoadingPreferences, setIsLoadingPreferences] = useState(false);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);

  const inferRequirements = useCallback(
    async (userInput: string, assetType?: string): Promise<any> => {
      setIsInferringPrompt(true);
      setInferenceError(null);
      try {
        const response = await aiApiClient.post('/api/product-marketing/intelligent-prompt', {
          user_input: userInput,
          asset_type: assetType,
        });
        setInferredConfig(response.data.configuration);
        return response.data.configuration;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to infer requirements';
        setInferenceError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsInferringPrompt(false);
      }
    },
    []
  );

  const getBrandDNA = useCallback(async (): Promise<any> => {
    setIsLoadingBrandDNA(true);
    setError(null);
    try {
      // Brand DNA is shared between campaign creator and product marketing
      // Using campaign-creator endpoint since it's the same data
      const response = await aiApiClient.get('/api/campaign-creator/brand-dna');
      setBrandDNA(response.data.brand_dna);
      return response.data.brand_dna;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get brand DNA';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoadingBrandDNA(false);
    }
  }, []);

  const getUserPreferences = useCallback(async (): Promise<any> => {
    setIsLoadingPreferences(true);
    setError(null);
    try {
      const response = await aiApiClient.get('/api/product-marketing/personalization/preferences');
      setUserPreferences(response.data.preferences);
      return response.data.preferences;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get user preferences';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoadingPreferences(false);
    }
  }, []);

  const getPersonalizedDefaults = useCallback(
    async (formType: string): Promise<any> => {
      setError(null);
      try {
        const response = await aiApiClient.get(`/api/product-marketing/personalization/defaults/${formType}`);
        return response.data.defaults;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to get personalized defaults';
        setError(errorMessage);
        throw new Error(errorMessage);
      }
    },
    []
  );

  const getRecommendations = useCallback(async (): Promise<any> => {
    setIsLoadingRecommendations(true);
    setError(null);
    try {
      const response = await aiApiClient.get('/api/product-marketing/personalization/recommendations');
      setRecommendations(response.data.recommendations);
      return response.data.recommendations;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get recommendations';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoadingRecommendations(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    setInferenceError(null);
  }, []);

  return {
    // State
    error,

    // Actions
    clearError,

    // Product Image Generation
    generateProductImage,
    isGeneratingProductImage,
    generatedProductImage,
    productImageError,

    // Product Animation Generation (Image-to-Video)
    generateProductAnimation,
    isGeneratingAnimation,
    generatedAnimation,
    animationError,

    // Product Video Generation (Text-to-Video)
    generateProductVideo,
    isGeneratingVideo,
    generatedVideo,
    videoError,

    // Product Avatar Generation (Talking Avatar)
    generateProductAvatar,
    isGeneratingAvatar,
    generatedAvatar,
    avatarError,

    // Intelligent Prompt Inference
    inferRequirements,
    isInferringPrompt,
    inferredConfig,
    inferenceError,

    // Brand DNA
    brandDNA,
    getBrandDNA,
    isLoadingBrandDNA,

    // Personalization
    getUserPreferences,
    userPreferences,
    isLoadingPreferences,
    getPersonalizedDefaults,
    getRecommendations,
    recommendations,
    isLoadingRecommendations,
  };
};
