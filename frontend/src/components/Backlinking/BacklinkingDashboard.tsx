/**
 * Backlinking Dashboard - Main Component
 *
 * Orchestrates all dashboard components and manages global state
 * Refactored for better maintainability and modularity
 */

import React, { useEffect } from 'react';
import {
  Box,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Snackbar,
  Typography,
  Grid,
  Card,
  CardContent,
  Skeleton,
  Stack,
  Divider,
  Fade,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  Assessment as AssessmentIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';

import { useBacklinking } from '../../hooks/useBacklinking';
import { CampaignWizard } from './CampaignWizard';
import { CampaignAnalytics } from './CampaignAnalytics';
import { EmailAutomationDialog } from './EmailAutomationDialog';
import { AIResearchModal } from './AIResearchModal';
import { AnalyticsSummary } from './AnalyticsSummary';
import BacklinkingHelpModal from './BacklinkingHelpModal';
import { BacklinkingStyles } from './styles/backlinkingStyles';

// Dashboard components
import { DashboardHeader } from './Dashboard/components/DashboardHeader';
import { QuickStatsGrid } from './Dashboard/components/QuickStatsGrid';
import { ResearchAndAnalysisSection } from './Dashboard/components/ResearchAndAnalysisSection';
import { EmailCampaignsSection } from './Dashboard/components/EmailCampaignsSection';
import { ActiveCampaignsSection } from './Dashboard/components/ActiveCampaignsSection';
import { AIInsightsFooter } from './Dashboard/components/AIInsightsFooter';

// Dashboard hooks and utilities
import { useDashboardState } from './Dashboard/hooks/useDashboardState';
import { useCampaignActions } from './Dashboard/hooks/useCampaignActions';
import { calculateQuickStats } from './Dashboard/utils/dashboardUtils';
import { Campaign } from './Dashboard/types/dashboard.types';

export const BacklinkingDashboard: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Backend data and API calls
  const {
    campaigns,
    isLoadingCampaigns,
    error,
    getCampaigns,
    createCampaign,
    pauseCampaign,
    resumeCampaign,
    deleteCampaign,
  } = useBacklinking();

  // Dashboard state management
  const dashboardState = useDashboardState();
  const {
    showWizard,
    selectedCampaign,
    showAnalytics,
    showEmailAutomation,
    showAIResearch,
    showHelpModal,
    confirmDelete,
    snackbar,
    loadingAction,
    aiEnhanced,
    aiResearchKeywords,
    setShowWizard,
    setSelectedCampaign,
    setShowAnalytics,
    setShowEmailAutomation,
    setShowAIResearch,
    setShowHelpModal,
    setConfirmDelete,
    setAiResearchKeywords,
    setLoadingAction,
    onToggleAI,
    onShowAIModal,
    showSnackbar,
    handleCloseSnackbar,
    resetModalStates,
  } = dashboardState;

  // Campaign action handlers
  const campaignActions = useCampaignActions({
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
  });

  // Initialize data on component mount
  useEffect(() => {
    getCampaigns();
  }, [getCampaigns]);

  // Calculate stats for quick stats grid
  const quickStats = calculateQuickStats(campaigns);

  const handleAIResearchComplete = async (results: any) => {
    try {
      // Create a new campaign with the research results
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

      await campaignActions.handleCreateCampaign(campaignData);
      setShowAIResearch(false);
      showSnackbar(`AI Research Complete! Created campaign with ${results.prospectsFound} prospects.`, 'success');
    } catch (error: any) {
      showSnackbar('Failed to create campaign from AI research results', 'error');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'paused':
        return 'warning';
      case 'completed':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <PlayIcon />;
      case 'paused':
        return <PauseIcon />;
      case 'completed':
        return <CheckCircleIcon />;
      default:
        return <ScheduleIcon />;
    }
  };

  // Loading skeleton component
  const CampaignSkeleton = () => (
    <Grid item xs={12} md={6} lg={4}>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Skeleton variant="text" width="60%" height={32} sx={{ mb: 2 }} />
          <Skeleton variant="text" width="80%" height={20} sx={{ mb: 2 }} />
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Skeleton variant="rectangular" width={60} height={24} />
          </Box>
          <Divider sx={{ my: 2 }} />
          <Box sx={{ mb: 2 }}>
            <Skeleton variant="text" width="40%" height={20} sx={{ mb: 1 }} />
            <Stack direction="row" spacing={2}>
              <Box sx={{ textAlign: 'center' }}>
                <Skeleton variant="text" width={30} height={28} />
                <Skeleton variant="text" width={30} height={16} />
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Skeleton variant="text" width={30} height={28} />
                <Skeleton variant="text" width={40} height={16} />
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Skeleton variant="text" width={30} height={28} />
                <Skeleton variant="text" width={35} height={16} />
              </Box>
            </Stack>
          </Box>
          <Skeleton variant="text" width="50%" height={16} />
        </CardContent>
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} variant="circular" width={40} height={40} />
          ))}
        </Box>
      </Card>
    </Grid>
  );

  if (isLoadingCampaigns) {
    return (
      <Fade in={true} timeout={500}>
        <Box sx={BacklinkingStyles.container}>
          <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
            <Skeleton variant="rectangular" width={200} height={40} />
            <Skeleton variant="rectangular" width={150} height={40} />
          </Box>

          <Box sx={BacklinkingStyles.cardGrid}>
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <CampaignSkeleton key={i} />
            ))}
          </Box>
        </Box>
      </Fade>
    );
  }

  return (
    <Box sx={{
      ...BacklinkingStyles.container,
      position: 'relative',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: '20%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '300px',
        height: '300px',
        /* backgroundImage: 'url(/images/ai-brain-icon.png)', */
        backgroundSize: 'contain',
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'center',
        opacity: 0.08,
        zIndex: 0,
        filter: 'blur(1px)',
      },
    }}>
      {/* Dashboard Header */}
      <DashboardHeader
        onCreateCampaign={() => setShowWizard(true)}
        onStartAIResearch={campaignActions.handleStartAIResearch}
        onShowHelp={() => setShowHelpModal(true)}
        aiEnhanced={aiEnhanced}
        onToggleAI={onToggleAI}
        onShowAIModal={onShowAIModal}
      />

      {/* Quick Performance Stats */}
      <QuickStatsGrid stats={quickStats} />

      {/* Analytics Summary */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" sx={{
            fontWeight: 700,
            color: '#F1F5F9',
            mb: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}>
            <AssessmentIcon sx={{ color: '#60A5FA' }} />
            Campaign Analytics Overview
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
            Comprehensive performance metrics and AI-powered insights for your backlinking campaigns
          </Typography>
        </Box>
        <AnalyticsSummary />
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Research & Analysis Tools */}
      <ResearchAndAnalysisSection
        onKeywordSelect={(keywords) => setAiResearchKeywords(keywords)}
        onProspectSelect={() => {}}
        onProspectViewDetails={() => {}}
        onProspectContact={() => {}}
      />

      {/* Email Campaigns Management */}
      <EmailCampaignsSection
        onCampaignSelect={(campaign) => setSelectedCampaign(campaign)}
      />

      {/* Visual Divider */}
      <Divider sx={{
        my: 4,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        height: '1px',
        borderRadius: '1px',
      }} />

      {/* Campaign Management */}
      <ActiveCampaignsSection
        campaigns={campaigns}
        isLoadingCampaigns={isLoadingCampaigns}
        loadingAction={loadingAction}
        onCreateCampaign={() => setShowWizard(true)}
        onViewCampaign={campaignActions.handleViewCampaignDetails}
        onViewAnalytics={(campaign) => {
          setSelectedCampaign(campaign);
          setShowAnalytics(true);
        }}
        onConfigureAutomation={(campaign) => {
          setSelectedCampaign(campaign);
          setShowEmailAutomation(true);
        }}
        onPauseCampaign={campaignActions.handlePauseCampaign}
        onResumeCampaign={campaignActions.handleResumeCampaign}
        onDeleteCampaign={setConfirmDelete}
      />

      {/* AI Insights Footer */}
      <AIInsightsFooter />

      {/* Campaign Wizard Dialog */}
      <CampaignWizard
        open={showWizard}
        onClose={() => setShowWizard(false)}
        onSubmit={async (data) => {
          const success = await campaignActions.handleCreateCampaign(data);
          if (success) {
            setShowWizard(false);
          }
        }}
      />

      {/* Analytics Dialog */}
      {selectedCampaign && (
        <CampaignAnalytics
          open={showAnalytics}
          onClose={() => {
            setShowAnalytics(false);
            resetModalStates();
          }}
          campaign={selectedCampaign}
        />
      )}

      {/* Email Automation Dialog */}
      {selectedCampaign && (
        <EmailAutomationDialog
          open={showEmailAutomation}
          onClose={() => {
            setShowEmailAutomation(false);
            resetModalStates();
          }}
          campaign={selectedCampaign}
        />
      )}

      {/* AI Research Modal */}
      <AIResearchModal
        open={showAIResearch}
        onClose={() => setShowAIResearch(false)}
        keywords={aiResearchKeywords}
        onComplete={campaignActions.handleAIResearchComplete}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!confirmDelete} onClose={() => setConfirmDelete(null)}>
        <DialogTitle>Delete Campaign</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this campaign? This action cannot be undone and will remove all associated data.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDelete(null)}>Cancel</Button>
          <Button
            onClick={async () => {
              if (confirmDelete) {
                await campaignActions.handleDeleteCampaign(confirmDelete);
                setConfirmDelete(null);
              }
            }}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        sx={{
          '& .MuiSnackbarContent-root': {
            borderRadius: 2,
            boxShadow: (theme) => theme.shadows[4],
          }
        }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Backlinking Help Modal */}
      <BacklinkingHelpModal
        open={showHelpModal}
        onClose={() => setShowHelpModal(false)}
      />
    </Box>
  );
};