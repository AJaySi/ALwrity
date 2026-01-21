/**
 * Dashboard Header Component
 *
 * Header section with title, subtitle, and action buttons
 */

import React from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Analytics as AnalyticsIcon,
  Psychology as BrainIcon,
  HelpOutline as HelpIcon,
  ToggleOn as ToggleOnIcon,
  ToggleOff as ToggleOffIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { GradientButton } from '../../styles/components';
import { BacklinkingStyles } from '../../styles/backlinkingStyles';
import { alpha } from '@mui/material/styles';

interface DashboardHeaderProps {
  onCreateCampaign: () => void;
  onStartAIResearch: () => void;
  onShowHelp: () => void;
  aiEnhanced: boolean;
  onToggleAI: () => void;
  onShowAIModal: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  onCreateCampaign,
  onStartAIResearch,
  onShowHelp,
  aiEnhanced,
  onToggleAI,
  onShowAIModal,
}) => {
  const navigate = useNavigate();

  return (
    <>
      {/* Hero Header */}
      <Box sx={{
        ...BacklinkingStyles.header,
        position: 'relative',
        zIndex: 2,
        textAlign: 'center',
        marginBottom: '3rem',
        padding: '2rem',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
        backdropFilter: 'blur(20px)',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 8px 32px rgba(96, 165, 250, 0.15)',
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
        <Typography variant="h2" sx={{
          ...BacklinkingStyles.headerTitle,
          fontSize: '3rem',
          textShadow: '0 0 40px rgba(96, 165, 250, 0.5)',
        }}>
          🤖 AI Backlinking
        </Typography>
        <Typography variant="h5" sx={{
          ...BacklinkingStyles.headerSubtitle,
          fontSize: '1.3rem',
          opacity: 0.9,
        }}>
          Automate your guest posting outreach and build high-quality backlinks
        </Typography>
      </Box>

      {/* Action Bar */}
      <Box sx={{
        mb: 3,
        display: 'flex',
        gap: 2,
        alignItems: 'center',
        position: 'relative',
        zIndex: 2,
        padding: '1.5rem',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%)',
        backdropFilter: 'blur(20px)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 8px 32px rgba(96, 165, 250, 0.15)',
      }}>
        <GradientButton
          startIcon={<AddIcon />}
          onClick={onCreateCampaign}
          sx={{
            minWidth: 200,
            position: 'relative',
            zIndex: 1,
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '-100%',
              width: '100%',
              height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
              transition: 'left 0.5s',
            },
            '&:hover::before': {
              left: '100%',
            },
          }}
        >
          ⚡ Create Campaign
        </GradientButton>

        <Button
          variant="outlined"
          startIcon={<AnalyticsIcon />}
          onClick={() => navigate('/backlinking/analytics')}
          sx={{
            ...BacklinkingStyles.actionButton,
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(96, 165, 250, 0.3)',
            color: '#60A5FA',
            '&:hover': {
              background: 'rgba(96, 165, 250, 0.1)',
              borderColor: '#60A5FA',
              boxShadow: '0 0 20px rgba(96, 165, 250, 0.3)',
            },
          }}
        >
          📊 View All Analytics
        </Button>

        {/* AI Enhancement Toggle */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2 }}>
          <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.875rem' }}>
            AI Enhanced
          </Typography>
          <Tooltip title={aiEnhanced ? "Disable AI enhancements (cost-effective)" : "Enable AI enhancements (better results)"}>
            <IconButton
              onClick={onToggleAI}
              sx={{
                color: aiEnhanced ? '#10B981' : '#6B7280',
                '&:hover': {
                  color: aiEnhanced ? '#059669' : '#4B5563',
                  transform: 'scale(1.1)',
                },
                transition: 'all 0.2s ease',
              }}
            >
              {aiEnhanced ? <ToggleOnIcon /> : <ToggleOffIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Learn about AI enhancements">
            <IconButton
              onClick={onShowAIModal}
              sx={{
                color: '#60A5FA',
                '&:hover': {
                  color: '#3B82F6',
                  transform: 'scale(1.1)',
                },
                transition: 'all 0.2s ease',
              }}
            >
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        <Tooltip title="AI Backlinking Help & Guide">
          <IconButton
            onClick={onShowHelp}
            sx={{
              bgcolor: alpha('#60A5FA', 0.1),
              border: `1px solid ${alpha('#60A5FA', 0.3)}`,
              mr: 1,
              '&:hover': {
                bgcolor: alpha('#60A5FA', 0.2),
                borderColor: alpha('#60A5FA', 0.5),
                transform: 'scale(1.05)',
              },
              transition: 'all 0.2s ease',
            }}
          >
            <HelpIcon sx={{ color: '#60A5FA' }} />
          </IconButton>
        </Tooltip>

        <Button
          variant="contained"
          startIcon={<BrainIcon />}
          onClick={onStartAIResearch}
          sx={{
            background: 'linear-gradient(135deg, #A855F7 0%, #60A5FA 100%)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            boxShadow: '0 4px 15px rgba(168, 85, 247, 0.4)',
            color: 'white',
            '&:hover': {
              background: 'linear-gradient(135deg, #9333EA 0%, #3B82F6 100%)',
              boxShadow: '0 6px 20px rgba(168, 85, 247, 0.6)',
              transform: 'translateY(-2px)',
            },
          }}
        >
          🤖 AI Research
        </Button>
      </Box>
    </>
  );
};