import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Stack,
  Chip,
  Divider,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Campaign,
  AutoAwesome,
  PhotoLibrary,
  Assessment,
  TrendingUp,
  CheckCircle,
  RadioButtonUnchecked,
  PhotoCamera,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { ImageStudioLayout } from '../ImageStudio/ImageStudioLayout';
import { GlassyCard } from '../ImageStudio/ui/GlassyCard';
import { SectionHeader } from '../ImageStudio/ui/SectionHeader';
import { useProductMarketing } from '../../hooks/useProductMarketing';
import { CampaignWizard } from './CampaignWizard';
import { AssetAuditPanel } from './AssetAuditPanel';
import { ProposalReview } from './ProposalReview';
import { useNavigate } from 'react-router-dom';

const MotionCard = motion(Card);

interface CampaignSummary {
  campaign_id: string;
  campaign_name: string;
  goal: string;
  status: string;
  total_assets: number;
  completed_assets: number;
  channels: string[];
}

export const ProductMarketingDashboard: React.FC = () => {
  const {
    getBrandDNA,
    brandDNA,
    isLoadingBrandDNA,
    listCampaigns,
    campaigns: apiCampaigns,
    isLoadingCampaigns,
  } = useProductMarketing();
  const [showWizard, setShowWizard] = useState(false);
  const [showAssetAudit, setShowAssetAudit] = useState(false);
  const [reviewCampaignId, setReviewCampaignId] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Load brand DNA on mount
    if (!brandDNA) {
      getBrandDNA();
    }
    // Load campaigns on mount
    listCampaigns();
  }, [brandDNA, getBrandDNA, listCampaigns]);

  const handleCreateCampaign = () => {
    setShowWizard(true);
  };

  const handleJourneySelect = (journey: string) => {
    if (journey === 'launch') {
      setShowWizard(true);
    } else if (journey === 'photoshoot') {
      navigate('/campaign-creator/photoshoot');
    } else if (journey === 'optimize') {
      // TODO: Show optimization insights
      alert('Optimization insights coming soon!');
    }
  };

  const handleWizardComplete = (blueprint: any) => {
    setShowWizard(false);
    // Reload campaigns from API
    listCampaigns();
    // Navigate to proposal review
    setReviewCampaignId(blueprint.campaign_id);
  };

  if (showWizard) {
    return <CampaignWizard onComplete={handleWizardComplete} onCancel={() => setShowWizard(false)} />;
  }

  if (showAssetAudit) {
    return <AssetAuditPanel onClose={() => setShowAssetAudit(false)} />;
  }

  if (reviewCampaignId) {
    return (
      <ProposalReview
        campaignId={reviewCampaignId}
        onBack={() => {
          setReviewCampaignId(null);
          listCampaigns();
        }}
        onComplete={() => {
          setReviewCampaignId(null);
          listCampaigns();
        }}
      />
    );
  }

  return (
    <ImageStudioLayout
      headerProps={{
        title: 'AI Campaign Creator',
        subtitle:
          'Create consistent, personalized marketing campaigns across all digital platforms. AI handles the heavy lifting—you just approve.',
      }}
    >
      <GlassyCard
        sx={{
          maxWidth: 1400,
          mx: 'auto',
          p: { xs: 3, md: 5 },
        }}
      >
        {/* Brand DNA Status */}
        {isLoadingBrandDNA ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : brandDNA ? (
          <Alert severity="success" sx={{ mb: 3 }}>
            Brand DNA loaded: {brandDNA.persona?.persona_name || 'Default Persona'} •{' '}
            {brandDNA.writing_style?.tone || 'professional'} tone • {brandDNA.target_audience?.industry_focus || 'general'} industry
          </Alert>
        ) : (
          <Alert severity="info" sx={{ mb: 3 }}>
            Brand DNA not available. Complete onboarding to enable personalized campaigns.
          </Alert>
        )}

        {/* User Journey Selection */}
        <SectionHeader
          title="Choose Your Journey"
          subtitle="Select how you want to create marketing assets"
          sx={{ mb: 3 }}
        />

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <MotionCard
              whileHover={{ scale: 1.02 }}
              sx={{
                height: '100%',
                cursor: 'pointer',
                background: 'rgba(124, 58, 237, 0.1)',
                border: '1px solid rgba(124, 58, 237, 0.3)',
              }}
              onClick={() => handleJourneySelect('launch')}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Campaign sx={{ color: '#c4b5fd', fontSize: 32 }} />
                    <Typography variant="h6" fontWeight={700}>
                      Journey A: Launch Campaign
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Create a new marketing campaign from scratch. AI generates personalized assets based on your brand DNA.
                  </Typography>
                  <Button variant="contained" startIcon={<AutoAwesome />} fullWidth>
                    Start Campaign Wizard
                  </Button>
                </Stack>
              </CardContent>
            </MotionCard>
          </Grid>

          <Grid item xs={12} md={4}>
            <MotionCard
              whileHover={{ scale: 1.02 }}
              sx={{
                height: '100%',
                cursor: 'pointer',
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
              }}
              onClick={() => setShowAssetAudit(true)}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PhotoLibrary sx={{ color: '#93c5fd', fontSize: 32 }} />
                    <Typography variant="h6" fontWeight={700}>
                      Journey B: Enhance Assets
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Upload existing assets for AI-powered quality assessment and enhancement recommendations.
                  </Typography>
                  <Button variant="contained" startIcon={<PhotoLibrary />} fullWidth>
                    Upload & Audit
                  </Button>
                </Stack>
              </CardContent>
            </MotionCard>
          </Grid>

          <Grid item xs={12} md={4}>
            <MotionCard
              whileHover={{ scale: 1.02 }}
              sx={{
                height: '100%',
                cursor: 'pointer',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
              onClick={() => handleJourneySelect('photoshoot')}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PhotoCamera sx={{ color: '#6ee7b7', fontSize: 32 }} />
                    <Typography variant="h6" fontWeight={700}>
                      Journey C: Product Photoshoot
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Generate professional product images for e-commerce listings and marketing campaigns.
                  </Typography>
                  <Button variant="contained" startIcon={<PhotoCamera />} fullWidth>
                    Launch Photoshoot Studio
                  </Button>
                </Stack>
              </CardContent>
            </MotionCard>
          </Grid>

          <Grid item xs={12} md={4}>
            <MotionCard
              whileHover={{ scale: 1.02 }}
              sx={{
                height: '100%',
                cursor: 'pointer',
                background: 'rgba(191, 219, 254, 0.1)',
                border: '1px solid rgba(191, 219, 254, 0.3)',
              }}
              onClick={() => handleJourneySelect('optimize')}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <TrendingUp sx={{ color: '#bfdbfe', fontSize: 32 }} />
                    <Typography variant="h6" fontWeight={700}>
                      Journey D: Optimize
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Get AI-powered insights and suggestions to optimize your existing campaigns and assets.
                  </Typography>
                  <Button variant="contained" startIcon={<TrendingUp />} fullWidth>
                    View Insights
                  </Button>
                </Stack>
              </CardContent>
            </MotionCard>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4, borderColor: 'rgba(255,255,255,0.08)' }} />

        {/* Quick Actions */}
        <SectionHeader
          title="Quick Actions"
          subtitle="Start a new campaign or enhance existing assets"
          sx={{ mb: 3 }}
        />

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <MotionCard
              whileHover={{ scale: 1.02 }}
              sx={{
                height: '100%',
                cursor: 'pointer',
                background: 'rgba(124, 58, 237, 0.1)',
                border: '1px solid rgba(124, 58, 237, 0.3)',
              }}
              onClick={handleCreateCampaign}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Campaign sx={{ color: '#c4b5fd', fontSize: 32 }} />
                    <Typography variant="h6" fontWeight={700}>
                      Create Campaign
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Launch a new marketing campaign with AI-generated assets personalized to your brand.
                  </Typography>
                  <Button variant="contained" startIcon={<AutoAwesome />} fullWidth>
                    Start Campaign Wizard
                  </Button>
                </Stack>
              </CardContent>
            </MotionCard>
          </Grid>

          <Grid item xs={12} md={6}>
            <MotionCard
              whileHover={{ scale: 1.02 }}
              sx={{
                height: '100%',
                cursor: 'pointer',
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
              }}
              onClick={() => setShowAssetAudit(true)}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PhotoLibrary sx={{ color: '#93c5fd', fontSize: 32 }} />
                    <Typography variant="h6" fontWeight={700}>
                      Audit Assets
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Upload existing assets for AI-powered quality assessment and enhancement recommendations.
                  </Typography>
                  <Button variant="contained" startIcon={<PhotoLibrary />} fullWidth>
                    Upload & Audit
                  </Button>
                </Stack>
              </CardContent>
            </MotionCard>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4, borderColor: 'rgba(255,255,255,0.08)' }} />

        {/* Active Campaigns */}
        <SectionHeader
          title="Active Campaigns"
          subtitle={
            isLoadingCampaigns
              ? 'Loading campaigns...'
              : apiCampaigns.length === 0
              ? 'No active campaigns. Create your first campaign to get started.'
              : `${apiCampaigns.length} campaign(s) in progress`
          }
          sx={{ mb: 3 }}
        />

        {isLoadingCampaigns ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : apiCampaigns.length === 0 ? (
          <Paper
            sx={{
              p: 4,
              textAlign: 'center',
              background: 'rgba(255,255,255,0.02)',
              border: '1px dashed rgba(255,255,255,0.1)',
            }}
          >
            <Campaign sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No campaigns yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Create your first campaign to start generating personalized marketing assets
            </Typography>
            <Button variant="contained" startIcon={<AutoAwesome />} onClick={handleCreateCampaign}>
              Create Campaign
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={2}>
            {apiCampaigns.map((campaign) => (
              <Grid item xs={12} md={6} key={campaign.campaign_id}>
                <GlassyCard sx={{ p: 3 }}>
                  <Stack spacing={2}>
                    <Box display="flex" justifyContent="space-between" alignItems="start">
                      <Box>
                        <Typography variant="h6" fontWeight={700} gutterBottom>
                          {campaign.campaign_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {campaign.goal}
                        </Typography>
                      </Box>
                      <Chip
                        label={campaign.status}
                        size="small"
                        color={campaign.status === 'ready' ? 'success' : 'default'}
                      />
                    </Box>

                    <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Progress
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Box flex={1}>
                          <Box
                            sx={{
                              height: 8,
                              borderRadius: 1,
                              background: 'rgba(255,255,255,0.1)',
                              overflow: 'hidden',
                            }}
                          >
                            <Box
                              sx={{
                                height: '100%',
                                width: `${((campaign.asset_nodes?.filter((n: any) => n.status === 'ready' || n.status === 'approved').length || 0) / (campaign.asset_nodes?.length || 1)) * 100}%`,
                                background: 'linear-gradient(90deg, #7c3aed, #a78bfa)',
                                transition: 'width 0.3s ease',
                              }}
                            />
                          </Box>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {campaign.asset_nodes?.filter((n: any) => n.status === 'ready' || n.status === 'approved').length || 0}/{campaign.asset_nodes?.length || 0}
                        </Typography>
                      </Box>
                    </Box>

                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Channels
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {campaign.channels.map((channel) => (
                          <Chip key={channel} label={channel} size="small" />
                        ))}
                      </Box>
                    </Box>

                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => {
                        // Check if proposals exist, if so show review, otherwise show campaign
                        setReviewCampaignId(campaign.campaign_id);
                      }}
                    >
                      {campaign.asset_nodes?.some((n: any) => n.status === 'proposed') ? 'Review Proposals' : 'View Campaign'}
                    </Button>
                  </Stack>
                </GlassyCard>
              </Grid>
            ))}
          </Grid>
        )}
      </GlassyCard>
    </ImageStudioLayout>
  );
};

