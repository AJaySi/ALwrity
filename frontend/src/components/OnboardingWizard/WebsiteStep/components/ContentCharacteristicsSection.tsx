/**
 * Content Characteristics Section Component
 * Displays content characteristics analysis in a reusable format
 */

import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Tooltip
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Language as LanguageIcon,
  Speed as SpeedIcon,
  Palette as PaletteIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

import { renderKeyInsight } from '../utils/renderUtils';
import { useOnboardingStyles } from '../../common/useOnboardingStyles';

interface ContentCharacteristics {
  sentence_structure?: string;
  vocabulary_level?: string;
  paragraph_organization?: string;
  content_flow?: string;
  readability_score?: string;
  content_density?: string;
  visual_elements_usage?: string;
}

interface ContentCharacteristicsSectionProps {
  contentCharacteristics?: ContentCharacteristics;
}

const ContentCharacteristicsSection: React.FC<ContentCharacteristicsSectionProps> = ({
  contentCharacteristics
}) => {
  const styles = useOnboardingStyles();

  if (!contentCharacteristics) {
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
        <AnalyticsIcon sx={{ color: '#667eea !important' }} />
        Content Characteristics
      </Typography>
      
      <Grid container spacing={2}>
        {contentCharacteristics.vocabulary_level && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Tooltip title="The complexity and sophistication of words used in the content. Higher levels use more advanced vocabulary while accessible levels use simpler, everyday words." arrow>
              <Box>
                {renderKeyInsight(
                  'Vocabulary Level',
                  contentCharacteristics.vocabulary_level,
                  <LanguageIcon />,
                  'info'
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
        
        {contentCharacteristics.readability_score && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Tooltip title="How easy it is for readers to understand the content. Higher scores mean the content is easier to read and comprehend." arrow>
              <Box>
                {renderKeyInsight(
                  'Readability Score',
                  contentCharacteristics.readability_score,
                  <SpeedIcon />,
                  'success'
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
        
        {contentCharacteristics.content_density && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Tooltip title="How much information is packed into each section. Moderate density balances information with readability." arrow>
              <Box>
                {renderKeyInsight(
                  'Content Density',
                  contentCharacteristics.content_density,
                  <PaletteIcon />,
                  'warning'
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
        
        {contentCharacteristics.sentence_structure && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Tooltip title="The variety and complexity of sentence patterns used. Varied structures keep readers engaged." arrow>
              <Box>
                {renderKeyInsight(
                  'Sentence Structure',
                  contentCharacteristics.sentence_structure,
                  <AnalyticsIcon />,
                  'secondary'
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
        
        {contentCharacteristics.paragraph_organization && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Tooltip title="How paragraphs are structured and organized. Clear organization helps readers follow the content easily." arrow>
              <Box>
                {renderKeyInsight(
                  'Paragraph Organization',
                  contentCharacteristics.paragraph_organization,
                  <AnalyticsIcon />,
                  'primary'
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
        
        {contentCharacteristics.content_flow && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Tooltip title="How smoothly the content moves from one idea to the next. Good flow keeps readers engaged throughout." arrow>
              <Box>
                {renderKeyInsight(
                  'Content Flow',
                  contentCharacteristics.content_flow,
                  <TrendingUpIcon />,
                  'success'
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
        
        {contentCharacteristics.visual_elements_usage && (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
            <Tooltip title="How often images, charts, and other visual elements are used to support the text content." arrow>
              <Box>
                {renderKeyInsight(
                  'Visual Elements Usage',
                  contentCharacteristics.visual_elements_usage,
                  <PaletteIcon />,
                  'warning'
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default ContentCharacteristicsSection;
