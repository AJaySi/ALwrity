/**
 * Target Audience Analysis Section Component
 * Displays target audience analysis in a reusable format
 */

import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper
} from '@mui/material';
import {
  Group as GroupIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon,
  Psychology as PsychologyIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

import { renderKeyInsight } from '../utils/renderUtils';
import { useOnboardingStyles } from '../../common/useOnboardingStyles';

interface TargetAudience {
  demographics?: string[];
  expertise_level?: string;
  industry_focus?: string;
  geographic_focus?: string;
  psychographic_profile?: string;
  pain_points?: string[];
  motivations?: string[];
}

interface TargetAudienceAnalysisSectionProps {
  targetAudience?: TargetAudience;
}

const TargetAudienceAnalysisSection: React.FC<TargetAudienceAnalysisSectionProps> = ({
  targetAudience
}) => {
  const styles = useOnboardingStyles();

  if (!targetAudience) {
    return null;
  }

  return (
  <Box sx={{ 
    ...styles.analysisSection, 
    mt: 4,
    '& .MuiTypography-root': { color: '#111827 !important', WebkitTextFillColor: '#111827' },
    '& .MuiPaper-root': { backgroundColor: '#ffffff !important', backgroundImage: 'none !important' }
  }}>
      <Typography 
        variant="h5" 
        sx={{
          ...styles.analysisSectionHeader,
          color: '#1a202c !important', // Force dark text
          fontWeight: '700 !important'
        }}
      >
        <GroupIcon sx={{ color: '#667eea !important' }} />
        Target Audience Analysis
      </Typography>
      
      <Grid container spacing={2}>
        {targetAudience.demographics && targetAudience.demographics.length > 0 && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            {renderKeyInsight(
              'Demographics',
              targetAudience.demographics,
              <GroupIcon />,
              'info'
            )}
          </Grid>
        )}
        
        {targetAudience.industry_focus && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            {renderKeyInsight(
              'Industry Focus',
              targetAudience.industry_focus,
              <BusinessIcon />,
              'primary'
            )}
          </Grid>
        )}
        
        {targetAudience.geographic_focus && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            {renderKeyInsight(
              'Geographic Focus',
              targetAudience.geographic_focus,
              <AnalyticsIcon />,
              'secondary'
            )}
          </Grid>
        )}
        
        {targetAudience.psychographic_profile && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Paper elevation={2} sx={styles.analysisAccentPaperSuccess}>
              <Box display="flex" alignItems="center" gap={2}>
                <Box sx={styles.analysisAccentIconSuccess}>
                  <PsychologyIcon />
                </Box>
                <Box flex={1}>
                  <Typography variant="subtitle2" sx={{ color: '#1a202c !important', fontWeight: 600 }} gutterBottom>
                    Psychographic Profile
                  </Typography>
                  <Box component="ul" sx={styles.analysisList}>
                    {Array.isArray(targetAudience.psychographic_profile)
                      ? targetAudience.psychographic_profile.map((item: string, index: number) => (
                          <Typography component="li" variant="body2" key={index} sx={{ ...styles.analysisListItem, color: '#1a202c !important' }}>
                            {item}
                          </Typography>
                        ))
                      : (
                          <Typography component="li" variant="body2" sx={{ ...styles.analysisListItem, color: '#1a202c !important' }}>
                            {targetAudience.psychographic_profile}
                          </Typography>
                        )}
                  </Box>
                </Box>
              </Box>
            </Paper>
          </Grid>
        )}
        
        {targetAudience.pain_points && targetAudience.pain_points.length > 0 && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Paper elevation={2} sx={styles.analysisAccentPaperError}>
              <Box display="flex" alignItems="center" gap={2}>
                <Box sx={styles.analysisAccentIconError}>
                  <WarningIcon />
                </Box>
                <Box flex={1}>
                  <Typography variant="subtitle2" sx={{ color: '#1a202c !important', fontWeight: 600 }} gutterBottom>
                    Pain Points
                  </Typography>
                  <Box component="ul" sx={styles.analysisList}>
                    {targetAudience.pain_points.map((painPoint: string, index: number) => (
                      <Typography component="li" variant="body2" key={index} sx={{ ...styles.analysisListItem, color: '#1a202c !important' }}>
                        {painPoint}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              </Box>
            </Paper>
          </Grid>
        )}
        
        {targetAudience.motivations && targetAudience.motivations.length > 0 && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Paper elevation={2} sx={styles.analysisAccentPaperSuccess}>
              <Box display="flex" alignItems="center" gap={2}>
                <Box sx={styles.analysisAccentIconSuccess}>
                  <TrendingUpIcon />
                </Box>
                <Box flex={1}>
                  <Typography variant="subtitle2" sx={{ color: '#1a202c !important', fontWeight: 600 }} gutterBottom>
                    Motivations
                  </Typography>
                  <Box component="ul" sx={styles.analysisList}>
                    {targetAudience.motivations.map((motivation: string, index: number) => (
                      <Typography component="li" variant="body2" key={index} sx={{ ...styles.analysisListItem, color: '#1a202c !important' }}>
                        {motivation}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default TargetAudienceAnalysisSection;
