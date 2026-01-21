/**
 * Active Campaigns Section Component
 *
 * Displays the grid of active campaigns with management controls
 */

import React from 'react';
import {
  Box,
  Typography,
  Button,
  Badge,
  Divider,
} from '@mui/material';
import { Campaign as CampaignIcon, Add as AddIcon } from '@mui/icons-material';
import { CampaignCard, CampaignCardHeader, CampaignCardContent, CampaignCardActions, AnimatedIconButton, SlideUpContainer, EmptyStateContainer, LoadingContainer, FadeInContainer } from '../../styles/components';
import { getStatusColor, getStatusIcon } from '../utils/dashboardUtils';
import { Campaign } from '../types/dashboard.types';

interface ActiveCampaignsSectionProps {
  campaigns: Campaign[];
  isLoadingCampaigns: boolean;
  loadingAction: string | null;
  onCreateCampaign: () => void;
  onViewCampaign: (campaign: Campaign) => void;
  onViewAnalytics: (campaign: Campaign) => void;
  onConfigureAutomation: (campaign: Campaign) => void;
  onPauseCampaign: (campaignId: string) => void;
  onResumeCampaign: (campaignId: string) => void;
  onDeleteCampaign: (campaignId: string) => void;
}

export const ActiveCampaignsSection: React.FC<ActiveCampaignsSectionProps> = ({
  campaigns,
  isLoadingCampaigns,
  loadingAction,
  onCreateCampaign,
  onViewCampaign,
  onViewAnalytics,
  onConfigureAutomation,
  onPauseCampaign,
  onResumeCampaign,
  onDeleteCampaign,
}) => {
  return (
    <Box sx={{ mb: 6 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" sx={{
            fontWeight: 700,
            color: '#F1F5F9',
            mb: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}>
            <CampaignIcon sx={{ color: '#10B981' }} />
            Active Campaigns
            <Badge
              badgeContent={campaigns.length}
              color="primary"
              sx={{
                ml: 1,
                '& .MuiBadge-badge': {
                  backgroundColor: '#10B981',
                  color: '#000',
                  fontWeight: 700,
                },
              }}
            />
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
            Manage and monitor your ongoing backlinking outreach campaigns
          </Typography>
        </Box>

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onCreateCampaign}
          sx={{
            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            borderRadius: 2,
            px: 3,
            py: 1.5,
            fontWeight: 600,
            textTransform: 'none',
            boxShadow: '0 4px 14px 0 rgba(16, 185, 129, 0.4)',
            '&:hover': {
              background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              boxShadow: '0 6px 20px 0 rgba(16, 185, 129, 0.6)',
            },
          }}
        >
          New Campaign
        </Button>
      </Box>

      {/* Loading State */}
      {isLoadingCampaigns ? (
        <LoadingContainer>
          {/* Loading skeleton would go here */}
        </LoadingContainer>
      ) : (
        <>
          {/* Campaigns Grid */}
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' },
            gap: 3,
            mb: campaigns.length === 0 ? 0 : 4,
          }}>
            {campaigns.map((campaign, index) => (
              <SlideUpContainer key={campaign.campaign_id}>
                <CampaignCard
                  role="article"
                  aria-labelledby={`campaign-title-${campaign.campaign_id}`}
                  tabIndex={0}
                  onClick={() => onViewCampaign(campaign)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      onViewCampaign(campaign);
                    }
                  }}
                >
                  <CampaignCardHeader>
                    <Box sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      mb: 2,
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <CampaignIcon sx={{ mr: 1, color: 'primary.main' }} aria-hidden="true" />
                        <Typography
                          variant="h6"
                          sx={{ flexGrow: 1 }}
                          id={`campaign-title-${campaign.campaign_id}`}
                        >
                          {campaign.name}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {getStatusColor(campaign.status)}
                        </Typography>
                        {getStatusIcon(campaign.status)}
                      </Box>
                    </Box>
                  </CampaignCardHeader>

                  <CampaignCardContent>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Keywords: {campaign.keywords.join(', ')}
                    </Typography>

                    {/* Email Stats */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Email Performance
                      </Typography>
                      <Box sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        gap: 2,
                      }}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h6" color="primary.main">
                            {campaign.email_stats.sent}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Sent
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h6" color="success.main">
                            {campaign.email_stats.replied}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Replied
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h6" color="error.main">
                            {campaign.email_stats.bounced}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Bounced
                          </Typography>
                        </Box>
                      </Box>
                    </Box>

                    <Typography variant="caption" color="text.secondary">
                      Created: {new Date(campaign.created_at).toLocaleDateString()}
                    </Typography>
                  </CampaignCardContent>

                  {/* Action Buttons */}
                  <CampaignCardActions role="toolbar" aria-label="Campaign actions">
                    <AnimatedIconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onViewCampaign(campaign);
                      }}
                      aria-label={`View details for ${campaign.name}`}
                    >
                      <span>👁️</span> {/* View icon */}
                    </AnimatedIconButton>

                    <AnimatedIconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onViewAnalytics(campaign);
                      }}
                      aria-label={`View analytics for ${campaign.name}`}
                    >
                      <span>📊</span> {/* Analytics icon */}
                    </AnimatedIconButton>

                    <AnimatedIconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onConfigureAutomation(campaign);
                      }}
                      aria-label={`Configure email automation for ${campaign.name}`}
                    >
                      <span>📧</span> {/* Email icon */}
                    </AnimatedIconButton>

                    {campaign.status === 'active' ? (
                      <AnimatedIconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onPauseCampaign(campaign.campaign_id);
                        }}
                        disabled={loadingAction === `pause-${campaign.campaign_id}`}
                        aria-label={`Pause ${campaign.name}`}
                      >
                        {loadingAction === `pause-${campaign.campaign_id}` ? (
                          <span>⏳</span>
                        ) : (
                          <span>⏸️</span>
                        )}
                      </AnimatedIconButton>
                    ) : campaign.status === 'paused' ? (
                      <AnimatedIconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onResumeCampaign(campaign.campaign_id);
                        }}
                        disabled={loadingAction === `resume-${campaign.campaign_id}`}
                        aria-label={`Resume ${campaign.name}`}
                      >
                        {loadingAction === `resume-${campaign.campaign_id}` ? (
                          <span>⏳</span>
                        ) : (
                          <span>▶️</span>
                        )}
                      </AnimatedIconButton>
                    ) : null}

                    <AnimatedIconButton
                      size="small"
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteCampaign(campaign.campaign_id);
                      }}
                      disabled={loadingAction === `delete-${campaign.campaign_id}`}
                      aria-label={`Delete ${campaign.name}`}
                    >
                      {loadingAction === `delete-${campaign.campaign_id}` ? (
                        <span>⏳</span>
                      ) : (
                        <span>🗑️</span>
                      )}
                    </AnimatedIconButton>
                  </CampaignCardActions>
                </CampaignCard>
              </SlideUpContainer>
            ))}
          </Box>

          {/* Empty State */}
          {campaigns.length === 0 && !isLoadingCampaigns && (
            <FadeInContainer>
              <EmptyStateContainer
                role="region"
                aria-labelledby="empty-state-heading"
                sx={{
                  position: 'relative',
                  zIndex: 2,
                  background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: '0 16px 64px rgba(96, 165, 250, 0.2)',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: '20%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '150px',
                    height: '150px',
                    /* backgroundImage: 'url(/images/ai-brain-icon.png)', */
                    backgroundSize: 'contain',
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'center',
                    opacity: 0.1,
                    zIndex: 0,
                  },
                }}
              >
                <Box sx={{
                  textAlign: 'center',
                  position: 'relative',
                  zIndex: 1,
                  padding: '2rem',
                }}>
                  <Typography
                    variant="h4"
                    sx={{
                      background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
                      backgroundClip: 'text',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      marginBottom: '1rem',
                    }}
                    id="empty-state-heading"
                  >
                    🧠 No AI Campaigns Yet
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: 'rgba(241, 245, 249, 0.8)',
                    }}
                  >
                    Unleash the power of AI-driven backlinking! Our neural networks will discover
                    high-quality guest posting opportunities, craft personalized outreach emails,
                    and track your link-building success.
                  </Typography>
                  <Box sx={{ mt: 3 }}>
                    <Button
                      onClick={onCreateCampaign}
                      size="large"
                      sx={{
                        background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
                        color: 'white',
                        px: 4,
                        py: 1.5,
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        '&:hover': {
                          background: 'linear-gradient(135deg, #3B82F6 0%, #9333EA 100%)',
                        },
                      }}
                    >
                      🚀 Launch Your First AI Campaign
                    </Button>
                    <Typography
                      variant="caption"
                      sx={{
                        mt: 2,
                        display: 'block',
                        color: 'rgba(203, 213, 225, 0.7)',
                        fontSize: '0.9rem',
                      }}
                    >
                      ⚡ Takes less than 2 minutes • Powered by Advanced AI
                    </Typography>
                  </Box>
                </Box>
              </EmptyStateContainer>
            </FadeInContainer>
          )}
        </>
      )}
    </Box>
  );
};