import { useState, useCallback } from 'react';
import {
  createCampaign as apiCreateCampaign,
  getCampaigns as apiGetCampaigns,
  getCampaign as apiGetCampaign,
  pauseCampaign as apiPauseCampaign,
  resumeCampaign as apiResumeCampaign,
  deleteCampaign as apiDeleteCampaign,
  discoverOpportunities as apiDiscoverOpportunities,
  getCampaignOpportunities as apiGetCampaignOpportunities,
  generateOutreachEmails as apiGenerateOutreachEmails,
  sendOutreachEmails as apiSendOutreachEmails,
  checkEmailResponses as apiCheckEmailResponses,
  getCampaignAnalytics as apiGetCampaignAnalytics,
  Campaign,
  CreateCampaignRequest,
  Opportunity,
  EmailGenerationResponse,
  CampaignAnalytics,
  EmailConfig
} from '../api/backlinkingApi';

export const useBacklinking = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [currentCampaign, setCurrentCampaign] = useState<Campaign | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [analytics, setAnalytics] = useState<CampaignAnalytics | null>(null);
  const [isLoadingCampaigns, setIsLoadingCampaigns] = useState(false);
  const [isLoadingOpportunities, setIsLoadingOpportunities] = useState(false);
  const [isGeneratingEmails, setIsGeneratingEmails] = useState(false);
  const [isSendingEmails, setIsSendingEmails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCampaign = useCallback(async (data: CreateCampaignRequest): Promise<void> => {
    try {
      setError(null);
      const newCampaign = await apiCreateCampaign(data);
      setCampaigns(prev => [newCampaign, ...prev]);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to create campaign';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const getCampaigns = useCallback(async (): Promise<void> => {
    try {
      setIsLoadingCampaigns(true);
      setError(null);
      const campaignsData = await apiGetCampaigns();
      setCampaigns(campaignsData);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to load campaigns';
      setError(errorMessage);
    } finally {
      setIsLoadingCampaigns(false);
    }
  }, []);

  const getCampaign = useCallback(async (campaignId: string): Promise<Campaign | null> => {
    try {
      setError(null);
      const campaign = await apiGetCampaign(campaignId);
      setCurrentCampaign(campaign);
      return campaign;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to load campaign';
      setError(errorMessage);
      return null;
    }
  }, []);

  const pauseCampaign = useCallback(async (campaignId: string): Promise<void> => {
    try {
      setError(null);
      await apiPauseCampaign(campaignId);
      // Update local state
      setCampaigns(prev => prev.map(campaign =>
        campaign.campaign_id === campaignId
          ? { ...campaign, status: 'paused' }
          : campaign
      ));
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to pause campaign';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const resumeCampaign = useCallback(async (campaignId: string): Promise<void> => {
    try {
      setError(null);
      await apiResumeCampaign(campaignId);
      // Update local state
      setCampaigns(prev => prev.map(campaign =>
        campaign.campaign_id === campaignId
          ? { ...campaign, status: 'active' }
          : campaign
      ));
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to resume campaign';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const deleteCampaign = useCallback(async (campaignId: string): Promise<void> => {
    try {
      setError(null);
      await apiDeleteCampaign(campaignId);
      // Remove from local state
      setCampaigns(prev => prev.filter(campaign => campaign.campaign_id !== campaignId));
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to delete campaign';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const discoverOpportunities = useCallback(async (
    campaignId: string,
    keywords: string[]
  ): Promise<Opportunity[]> => {
    try {
      setIsLoadingOpportunities(true);
      setError(null);
      const discoveredOpportunities = await apiDiscoverOpportunities(campaignId, keywords);
      setOpportunities(discoveredOpportunities);
      return discoveredOpportunities;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to discover opportunities';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoadingOpportunities(false);
    }
  }, []);

  const getCampaignOpportunities = useCallback(async (campaignId: string): Promise<Opportunity[]> => {
    try {
      setIsLoadingOpportunities(true);
      setError(null);
      const opportunitiesData = await apiGetCampaignOpportunities(campaignId);
      setOpportunities(opportunitiesData);
      return opportunitiesData;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to load opportunities';
      setError(errorMessage);
      return [];
    } finally {
      setIsLoadingOpportunities(false);
    }
  }, []);

  const generateOutreachEmails = useCallback(async (
    campaignId: string,
    userProposal: any
  ): Promise<EmailGenerationResponse[]> => {
    try {
      setIsGeneratingEmails(true);
      setError(null);
      const emails = await apiGenerateOutreachEmails(campaignId, userProposal);
      return emails;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to generate emails';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsGeneratingEmails(false);
    }
  }, []);

  const sendOutreachEmails = useCallback(async (
    campaignId: string,
    emailRecords: any[],
    smtpConfig: EmailConfig
  ): Promise<any> => {
    try {
      setIsSendingEmails(true);
      setError(null);
      const result = await apiSendOutreachEmails(campaignId, emailRecords, smtpConfig);
      return result;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to send emails';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSendingEmails(false);
    }
  }, []);

  const checkEmailResponses = useCallback(async (
    campaignId: string,
    imapConfig: EmailConfig
  ): Promise<any> => {
    try {
      setError(null);
      const result = await apiCheckEmailResponses(campaignId, imapConfig);
      return result;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to check responses';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const getCampaignAnalytics = useCallback(async (campaignId: string): Promise<CampaignAnalytics | null> => {
    try {
      setError(null);
      const analyticsData = await apiGetCampaignAnalytics(campaignId);
      setAnalytics(analyticsData);
      return analyticsData;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to load analytics';
      setError(errorMessage);
      return null;
    }
  }, []);

  return {
    // State
    campaigns,
    currentCampaign,
    opportunities,
    analytics,
    isLoadingCampaigns,
    isLoadingOpportunities,
    isGeneratingEmails,
    isSendingEmails,
    error,

    // Actions
    createCampaign,
    getCampaigns,
    getCampaign,
    pauseCampaign,
    resumeCampaign,
    deleteCampaign,
    discoverOpportunities,
    getCampaignOpportunities,
    generateOutreachEmails,
    sendOutreachEmails,
    checkEmailResponses,
    getCampaignAnalytics,
  };
};