import React from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Fade
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Assessment as AssessmentIcon,
  LinkedIn as LinkedInIcon,
  Facebook as FacebookIcon,
  Twitter as TwitterIcon,
  Article as ArticleIcon,
  Instagram as InstagramIcon
} from '@mui/icons-material';
import { CorePersonaDisplay } from './sections/CorePersonaDisplay';
import { PlatformPersonaDisplay } from './sections/PlatformPersonaDisplay';
import { QualityMetricsDisplay } from './QualityMetricsDisplay';

interface PersonaPreviewSectionProps {
  showPreview: boolean;
  corePersona: any;
  platformPersonas: Record<string, any>;
  qualityMetrics: any;
  selectedPlatforms: string[];
  expandedAccordion: string | false;
  setExpandedAccordion: (accordion: string | false) => void;
  setCorePersona: (persona: any) => void;
  setPlatformPersonas: (personas: Record<string, any>) => void;
  handleRegenerate: () => void;
}

const availablePlatforms = [
  { id: 'linkedin', name: 'LinkedIn', icon: <LinkedInIcon />, color: '#0077B5' },
  { id: 'facebook', name: 'Facebook', icon: <FacebookIcon />, color: '#1877F2' },
  { id: 'twitter', name: 'Twitter', icon: <TwitterIcon />, color: '#1DA1F2' },
  { id: 'blog', name: 'Blog', icon: <ArticleIcon />, color: '#FF6B35' },
  { id: 'instagram', name: 'Instagram', icon: <InstagramIcon />, color: '#E4405F' }
];

export const PersonaPreviewSection: React.FC<PersonaPreviewSectionProps> = ({
  showPreview,
  corePersona,
  platformPersonas,
  qualityMetrics,
  selectedPlatforms,
  expandedAccordion,
  setExpandedAccordion,
  setCorePersona,
  setPlatformPersonas,
  handleRegenerate
}) => {
  if (!showPreview || !corePersona) {
    return null;
  }

  return (
    <Fade in={true}>
      <Box>
        <Box sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
          p: 3,
          background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
          border: '1px solid #e2e8f0',
          borderRadius: 3,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)'
        }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#1e293b', mb: 0.5 }}>
              Your AI Writing Persona
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Comprehensive analysis of your unique writing style and brand voice
            </Typography>
          </Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRegenerate}
            size="small"
            sx={{
              borderColor: '#e2e8f0',
              color: '#475569',
              '&:hover': {
                borderColor: '#3b82f6',
                backgroundColor: '#f8fafc'
              }
            }}
          >
            Regenerate
          </Button>
        </Box>

        {/* Core Persona */}
        <Accordion
          expanded={expandedAccordion === 'core'}
          onChange={() => setExpandedAccordion(expandedAccordion === 'core' ? false : 'core')}
          sx={{
            mb: 3,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: '1px solid #e2e8f0',
            borderRadius: 3,
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
            '&:before': {
              display: 'none'
            },
            '&.Mui-expanded': {
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon sx={{ color: '#64748b' }} />}
            sx={{
              px: 4,
              py: 3,
              '&:hover': {
                backgroundColor: '#f8fafc'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, width: '100%' }}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <PsychologyIcon sx={{ fontSize: 24 }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 0.5 }}>
                  Core Writing Style
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Your unique voice and writing characteristics
                </Typography>
              </Box>
              {qualityMetrics && (
                <Chip
                  label={`${qualityMetrics.overall_score}% Quality`}
                  sx={{
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: 'white',
                    fontWeight: 600,
                    '& .MuiChip-label': {
                      px: 2
                    }
                  }}
                  size="small"
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ px: 4, pb: 4 }}>
            <CorePersonaDisplay
              persona={corePersona}
              onChange={(updatedPersona) => {
                setCorePersona(updatedPersona);
                // TODO: Add debounced auto-save
              }}
            />
          </AccordionDetails>
        </Accordion>

        {/* Platform Adaptations */}
        <Accordion
          expanded={expandedAccordion === 'platforms'}
          onChange={() => setExpandedAccordion(expandedAccordion === 'platforms' ? false : 'platforms')}
          sx={{
            mb: 3,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: '1px solid #e2e8f0',
            borderRadius: 3,
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
            '&:before': {
              display: 'none'
            },
            '&.Mui-expanded': {
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon sx={{ color: '#64748b' }} />}
            sx={{
              px: 4,
              py: 3,
              '&:hover': {
                backgroundColor: '#f8fafc'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, width: '100%' }}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <AutoAwesomeIcon sx={{ fontSize: 24 }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 0.5 }}>
                  Platform Adaptations
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Optimized for different content platforms
                </Typography>
              </Box>
              <Chip
                label={`${selectedPlatforms.length} Platforms`}
                sx={{
                  background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                  color: 'white',
                  fontWeight: 600,
                  '& .MuiChip-label': {
                    px: 2
                  }
                }}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ px: 4, pb: 4 }}>
            <Box>
              {selectedPlatforms.map((platformId, index) => {
                const platformInfo = availablePlatforms.find(p => p.id === platformId);
                return (
                  <Box key={platformId} sx={{ mb: index < selectedPlatforms.length - 1 ? 4 : 0 }}>
                    <Divider sx={{ mb: 3 }}>
                      <Chip
                        icon={platformInfo?.icon}
                        label={platformInfo?.name || platformId}
                        sx={{
                          background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                          color: 'white',
                          fontWeight: 600
                        }}
                      />
                    </Divider>
                    <PlatformPersonaDisplay
                      platformPersona={platformPersonas[platformId] || {}}
                      platformName={platformId}
                      onChange={(updatedPersona) => {
                        setPlatformPersonas({
                          ...platformPersonas,
                          [platformId]: updatedPersona
                        });
                        // TODO: Add debounced auto-save
                      }}
                    />
                  </Box>
                );
              })}
              {selectedPlatforms.length === 0 && (
                <Alert severity="info" sx={{
                  background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                  border: '1px solid #0ea5e9',
                  color: '#0c4a6e'
                }}>
                  No platforms selected. Please select at least one platform to see optimized personas.
                </Alert>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Quality Metrics */}
        {qualityMetrics && (
          <Accordion
            expanded={expandedAccordion === 'quality'}
            onChange={() => setExpandedAccordion(expandedAccordion === 'quality' ? false : 'quality')}
            sx={{
              mb: 4,
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              border: '1px solid #e2e8f0',
              borderRadius: 3,
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
              '&:before': {
                display: 'none'
              },
              '&.Mui-expanded': {
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#64748b' }} />}
              sx={{
                px: 4,
                py: 3,
                '&:hover': {
                  backgroundColor: '#f8fafc'
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, width: '100%' }}>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <AssessmentIcon sx={{ fontSize: 24 }} />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 0.5 }}>
                    Quality Assessment
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    Performance metrics and recommendations
                  </Typography>
                </Box>
                <Chip
                  label={`${qualityMetrics.overall_score}% Quality`}
                  sx={{
                    background: qualityMetrics.overall_score >= 85
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                      : qualityMetrics.overall_score >= 70
                      ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                      : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    color: 'white',
                    fontWeight: 600,
                    '& .MuiChip-label': {
                      px: 2
                    }
                  }}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ px: 4, pb: 4 }}>
              <QualityMetricsDisplay metrics={qualityMetrics} />
            </AccordionDetails>
          </Accordion>
        )}
      </Box>
    </Fade>
  );
};
