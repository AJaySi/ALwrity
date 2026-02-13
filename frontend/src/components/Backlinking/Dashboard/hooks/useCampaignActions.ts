/**
 * Campaign Actions Hook
 *
 * Handles all campaign-related actions and API calls
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBacklinking } from '../../../../hooks/useBacklinking';
import { Campaign } from '../types/dashboard.types';

interface UseCampaignActionsProps {
  setLoadingAction: (action: string | null) => void;
  showSnackbar: (message: string, severity?: 'success' | 'error' | 'info' | 'warning') => void;
  setShowAIResearch: (show: boolean) => void;
  setAiResearchKeywords: (keywords: string[]) => void;
  aiResearchKeywords: string[];
  getCampaigns: () => void;
  createCampaign: (data: any) => Promise<any>;
  pauseCampaign: (id: string) => Promise<any>;
  resumeCampaign: (id: string) => Promise<any>;
  deleteCampaign: (id: string) => Promise<any>;
}

export const useCampaignActions = ({
  setLoadingAction,
  showSnackbar,
  setShowAIResearch,
  setAiResearchKeywords,
  aiResearchKeywords,
  getCampaigns,
  createCampaign,
  pauseCampaign,
  resumeCampaign,
  deleteCampaign,
}: UseCampaignActionsProps & { aiResearchKeywords: string[] }) => {
  const navigate = useNavigate();

  const [lastCreatedCampaignId, setLastCreatedCampaignId] = useState<string | null>(null);

  const handleCreateCampaign = async (campaignData: any) => {
    setLoadingAction('create');
    try {
      const result = await createCampaign(campaignData);
      setLastCreatedCampaignId(result?.campaign_id || null);
      getCampaigns();
      showSnackbar('Campaign created successfully!', 'success');
      return result;
    } catch (error: any) {
      showSnackbar(error?.response?.data?.detail || 'Failed to create campaign', 'error');
      throw error;
    } finally {
      setLoadingAction(null);
    }
  };

  const handlePauseCampaign = async (campaignId: string) => {
    setLoadingAction(`pause-${campaignId}`);
    try {
      await pauseCampaign(campaignId);
      getCampaigns();
      showSnackbar('Campaign paused successfully', 'info');
    } catch (error: any) {
      showSnackbar(error?.response?.data?.detail || 'Failed to pause campaign', 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleResumeCampaign = async (campaignId: string) => {
    setLoadingAction(`resume-${campaignId}`);
    try {
      await resumeCampaign(campaignId);
      getCampaigns();
      showSnackbar('Campaign resumed successfully', 'success');
    } catch (error: any) {
      showSnackbar(error?.response?.data?.detail || 'Failed to resume campaign', 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleDeleteCampaign = async (campaignId: string) => {
    setLoadingAction(`delete-${campaignId}`);
    try {
      await deleteCampaign(campaignId);
      getCampaigns();
      showSnackbar('Campaign deleted successfully', 'success');
    } catch (error: any) {
      showSnackbar(error?.response?.data?.detail || 'Failed to delete campaign', 'error');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleStartAIResearch = (keywords: string[] = []) => {
    setAiResearchKeywords(keywords);
    setShowAIResearch(true);
  };

  const handleAIResearchComplete = async (results: any) => {
    try {
      const campaignData = {
        name: `AI Research Campaign - ${new Date().toLocaleDateString()}`,
        keywords: aiResearchKeywords,
        target_audience: 'general',
        industry: 'general',
        user_proposal: {
          user_name: 'AI Researcher',
          user_email: 'research@alwrity.ai',
          topic: aiResearchKeywords.join(', '),
          description: `AI-discovered campaign with ${results.prospectsFound} prospects and ${results.emailsReady} email addresses ready.`,
        },
      };

      await handleCreateCampaign(campaignData);
      setShowAIResearch(false);
      showSnackbar(`AI Research Complete! Created campaign with ${results.prospectsFound} prospects.`, 'success');
    } catch (error: any) {
      showSnackbar('Failed to create campaign from AI research results', 'error');
    }
  };

  const handleViewCampaignDetails = (campaign: Campaign) => {
    navigate(`/backlinking/campaign/${campaign.campaign_id}`);
  };

  const handleViewCampaignAnalytics = (campaign: Campaign) => {
    navigate(`/backlinking/campaign/${campaign.campaign_id}/analytics`);
  };

  return {
    lastCreatedCampaignId,
    handleCreateCampaign,
    handlePauseCampaign,
    handleResumeCampaign,
    handleDeleteCampaign,
    handleStartAIResearch,
    handleAIResearchComplete,
    handleViewCampaignDetails,
    handleViewCampaignAnalytics,
  };
};