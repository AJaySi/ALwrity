import { useState, useCallback } from 'react';
import { aiApiClient } from '../api/client';

export interface CampaignCreateRequest {
  campaign_name: string;
  goal: string;
  kpi?: string;
  channels: string[];
  product_context?: {
    product_description?: string;
    product_name?: string;
    marketing_goal?: string;
    [key: string]: any;
  };
}

export interface CampaignBlueprint {
  campaign_id: string;
  campaign_name: string;
  goal: string;
  kpi?: string;
  phases: Array<{
    name: string;
    duration_days: number;
    purpose: string;
  }>;
  asset_nodes: Array<{
    asset_id: string;
    asset_type: string;
    channel: string;
    status: string;
  }>;
  channels: string[];
  status: string;
}

export interface AssetProposal {
  asset_id: string;
  asset_type: string;
  channel: string;
  campaign_id?: string;
  proposed_prompt?: string;
  recommended_template?: string;
  recommended_provider?: string;
  cost_estimate: number;
  concept_summary: string;
  video_subtype?: string;
  video_type?: string;
  animation_type?: string;
  duration?: number;
  resolution?: string;
}

export interface AssetProposalsResponse {
  proposals: Record<string, AssetProposal>;
  total_assets: number;
}

export interface BrandDNATokens {
  writing_style: {
    tone: string;
    voice: string;
    complexity: string;
    engagement_level: string;
  };
  target_audience: {
    demographics: string[];
    industry_focus: string;
    expertise_level: string;
  };
  visual_identity: {
    color_palette?: string[];
    brand_values?: string[];
    positioning?: string;
    style_guidelines?: any;
  };
  persona: {
    persona_name?: string;
    archetype?: string;
    core_belief?: string;
    linguistic_fingerprint?: any;
    platform_personas?: any;
  };
  competitive_positioning: {
    differentiators: string[];
    unique_value_props: string[];
  };
}

export interface ChannelPack {
  channel: string;
  platform: string;
  asset_type: string;
  templates: Array<{
    id: string;
    name: string;
    dimensions: string;
    aspect_ratio: string;
    recommended_provider: string;
    quality: string;
  }>;
  formats: Array<{
    name: string;
    width: number;
    height: number;
    ratio: string;
    safe_zone?: any;
  }>;
  copy_framework: Record<string, any>;
  optimization_tips: string[];
}

export interface AssetAuditResult {
  asset_info: {
    width: number;
    height: number;
    format: string;
    mode: string;
    quality_score: number;
  };
  recommendations: Array<{
    operation: string;
    priority: string;
    reason: string;
    suggested_mode?: string;
    suggested_format?: string;
    suggested_operations?: string[];
  }>;
  status: 'usable' | 'needs_enhancement' | 'error';
  error?: string;
}

export interface PreflightValidationResult {
  can_proceed: boolean;
  message?: string;
  error_details?: Record<string, any>;
  summary: {
    total_assets: number;
    image_count: number;
    text_count: number;
    estimated_cost: number;
  };
}

export const useCampaignCreator = () => {
  const [isLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Campaign Blueprint
  const [blueprint, setBlueprint] = useState<CampaignBlueprint | null>(null);
  const [isCreatingBlueprint, setIsCreatingBlueprint] = useState(false);

  // Asset Proposals
  const [proposals, setProposals] = useState<AssetProposalsResponse | null>(null);
  const [isGeneratingProposals, setIsGeneratingProposals] = useState(false);

  // Brand DNA
  const [brandDNA, setBrandDNA] = useState<BrandDNATokens | null>(null);
  const [isLoadingBrandDNA, setIsLoadingBrandDNA] = useState(false);

  // Channel Packs
  const [channelPack, setChannelPack] = useState<ChannelPack | null>(null);
  const [isLoadingChannelPack, setIsLoadingChannelPack] = useState(false);

  // Asset Audit
  const [auditResult, setAuditResult] = useState<AssetAuditResult | null>(null);
  const [isAuditing, setIsAuditing] = useState(false);

  // Asset Generation
  const [isGeneratingAsset, setIsGeneratingAsset] = useState(false);
  const [generatedAsset, setGeneratedAsset] = useState<any>(null);

  // Pre-flight Validation
  const [preflightResult, setPreflightResult] = useState<PreflightValidationResult | null>(null);
  const [isValidatingPreflight, setIsValidatingPreflight] = useState(false);

  // Campaign listing
  const [campaigns, setCampaigns] = useState<CampaignBlueprint[]>([]);
  const [isLoadingCampaigns, setIsLoadingCampaigns] = useState(false);

  const createCampaignBlueprint = useCallback(
    async (request: CampaignCreateRequest): Promise<CampaignBlueprint> => {
      setIsCreatingBlueprint(true);
      setError(null);
      try {
        const response = await aiApiClient.post<CampaignBlueprint>(
          '/api/campaign-creator/campaigns/create-blueprint',
          request
        );
        setBlueprint(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to create campaign blueprint';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsCreatingBlueprint(false);
      }
    },
    []
  );

  const generateAssetProposals = useCallback(
    async (campaignId: string, productContext?: any): Promise<AssetProposalsResponse> => {
      setIsGeneratingProposals(true);
      setError(null);
      try {
        const response = await aiApiClient.post<AssetProposalsResponse>(
          `/api/campaign-creator/campaigns/${campaignId}/generate-proposals`,
          {
            campaign_id: campaignId,
            product_context: productContext,
          }
        );
        setProposals(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate asset proposals';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGeneratingProposals(false);
      }
    },
    []
  );

  const generateAsset = useCallback(
    async (assetProposal: AssetProposal, productContext?: any): Promise<any> => {
      setIsGeneratingAsset(true);
      setError(null);
      try {
        const response = await aiApiClient.post('/api/campaign-creator/assets/generate', {
          asset_proposal: assetProposal,
          product_context: productContext,
        });
        setGeneratedAsset(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate asset';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsGeneratingAsset(false);
      }
    },
    []
  );

  const getBrandDNA = useCallback(async (): Promise<BrandDNATokens> => {
    setIsLoadingBrandDNA(true);
    setError(null);
    try {
      const response = await aiApiClient.get<{ brand_dna: BrandDNATokens }>('/api/campaign-creator/brand-dna');
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

  const getChannelBrandDNA = useCallback(
    async (channel: string): Promise<BrandDNATokens> => {
      setIsLoadingBrandDNA(true);
      setError(null);
      try {
        const response = await aiApiClient.get<{ channel: string; brand_dna: BrandDNATokens }>(
          `/api/campaign-creator/brand-dna/channel/${channel}`
        );
        return response.data.brand_dna;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to get channel brand DNA';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsLoadingBrandDNA(false);
      }
    },
    []
  );

  const getChannelPack = useCallback(
    async (channel: string, assetType: string = 'social_post'): Promise<ChannelPack> => {
      setIsLoadingChannelPack(true);
      setError(null);
      try {
        const response = await aiApiClient.get<ChannelPack>(
          `/api/campaign-creator/channels/${channel}/pack?asset_type=${assetType}`
        );
        setChannelPack(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to get channel pack';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsLoadingChannelPack(false);
      }
    },
    []
  );

  const auditAsset = useCallback(
    async (imageBase64: string, assetMetadata?: any): Promise<AssetAuditResult> => {
      setIsAuditing(true);
      setError(null);
      try {
        const response = await aiApiClient.post<AssetAuditResult>('/api/campaign-creator/assets/audit', {
          image_base64: imageBase64,
          asset_metadata: assetMetadata,
        });
        setAuditResult(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to audit asset';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsAuditing(false);
      }
    },
    []
  );

  const listCampaigns = useCallback(async (status?: string): Promise<CampaignBlueprint[]> => {
    setIsLoadingCampaigns(true);
    setError(null);
    try {
      const url = status ? `/api/campaign-creator/campaigns?status=${status}` : '/api/campaign-creator/campaigns';
      const response = await aiApiClient.get<{ campaigns: CampaignBlueprint[]; total: number }>(url);
      setCampaigns(response.data.campaigns);
      return response.data.campaigns;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to list campaigns';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoadingCampaigns(false);
    }
  }, []);

  const getCampaign = useCallback(async (campaignId: string): Promise<CampaignBlueprint> => {
    setError(null);
    try {
      const response = await aiApiClient.get<CampaignBlueprint>(`/api/campaign-creator/campaigns/${campaignId}`);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get campaign';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const getCampaignProposals = useCallback(async (campaignId: string): Promise<AssetProposalsResponse> => {
    setError(null);
    try {
      const response = await aiApiClient.get<AssetProposalsResponse>(`/api/campaign-creator/campaigns/${campaignId}/proposals`);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get proposals';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const validateCampaignPreflight = useCallback(
    async (request: CampaignCreateRequest): Promise<PreflightValidationResult> => {
      setIsValidatingPreflight(true);
      setError(null);
      try {
        const response = await aiApiClient.post<PreflightValidationResult>(
          '/api/campaign-creator/campaigns/validate-preflight',
          request
        );
        setPreflightResult(response.data);
        return response.data;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to validate campaign pre-flight';
        setError(errorMessage);
        const errorResult: PreflightValidationResult = {
          can_proceed: false,
          message: errorMessage,
          summary: {
            total_assets: 0,
            image_count: 0,
            text_count: 0,
            estimated_cost: 0,
          },
        };
        setPreflightResult(errorResult);
        return errorResult;
      } finally {
        setIsValidatingPreflight(false);
      }
    },
    []
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearBlueprint = useCallback(() => {
    setBlueprint(null);
  }, []);

  const clearProposals = useCallback(() => {
    setProposals(null);
  }, []);

  const clearAuditResult = useCallback(() => {
    setAuditResult(null);
  }, []);

  // Personalization
  const [userPreferences] = useState<any>(null);
  const [isLoadingPreferences] = useState(false);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);

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

  return {
    // State
    isLoading,
    error,
    blueprint,
    isCreatingBlueprint,
    proposals,
    isGeneratingProposals,
    brandDNA,
    isLoadingBrandDNA,
    channelPack,
    isLoadingChannelPack,
    auditResult,
    isAuditing,
    isGeneratingAsset,
    generatedAsset,
    preflightResult,
    isValidatingPreflight,
    campaigns,
    isLoadingCampaigns,

    // Actions
    createCampaignBlueprint,
    generateAssetProposals,
    generateAsset,
    getBrandDNA,
    getChannelBrandDNA,
    getChannelPack,
    auditAsset,
    clearError,
    clearBlueprint,
    clearProposals,
    clearAuditResult,
    listCampaigns,
    getCampaign,
    getCampaignProposals,
    validateCampaignPreflight,

    // Personalization
    getPersonalizedDefaults,
    getRecommendations,
    userPreferences,
    isLoadingPreferences,
    recommendations,
    isLoadingRecommendations,
  };
};
