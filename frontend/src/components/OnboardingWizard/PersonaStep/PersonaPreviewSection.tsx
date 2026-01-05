import React, { useCallback, useRef } from 'react';
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
  Instagram as InstagramIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { CorePersonaDisplay } from './sections/CorePersonaDisplay';
import { PlatformPersonaDisplay } from './sections/PlatformPersonaDisplay';
import { QualityMetricsDisplay } from './QualityMetricsDisplay';
import { apiClient } from '../../../api/client';

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
  setQualityMetrics: (metrics: any) => void;
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
  setQualityMetrics,
  handleRegenerate
}) => {
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isSaving, setIsSaving] = React.useState(false);

  // Debounced auto-save function
  const debouncedSave = useCallback(async (updatedCorePersona: any, updatedPlatformPersonas: any) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(async () => {
      try {
        setIsSaving(true);
        console.log('Auto-saving persona changes...');

        const saveData = {
          core_persona: updatedCorePersona,
          platform_personas: updatedPlatformPersonas,
          quality_metrics: qualityMetrics,
          selected_platforms: selectedPlatforms
        };

        console.log('📤 Sending save data:', JSON.stringify(saveData, null, 2));

        const response = await apiClient.post('/api/onboarding/step4/persona-save', saveData);

        if (response.data.success) {
          console.log('✅ Persona changes saved successfully');

          // Clear sessionStorage flag to force re-check server cache on next refresh
          sessionStorage.removeItem('persona_server_cache_checked');
          console.log('🧹 Cleared server cache check flag - will re-check on refresh');

          // Reload the latest data from server to ensure UI shows the saved changes
          try {
            console.log('🔄 Reloading latest persona data from server after save...');
            const latestResponse = await apiClient.get('/api/onboarding/step4/persona-latest');
            console.log('📥 Reload response:', latestResponse.data);

            if (latestResponse.data && latestResponse.data.success && latestResponse.data.persona) {
              const latestData = latestResponse.data.persona;
              console.log('✅ Latest persona data received:', {
                core_persona_keys: Object.keys(latestData.core_persona || {}),
                platform_personas_keys: Object.keys(latestData.platform_personas || {}),
                persona_name: latestData.core_persona?.identity?.persona_name
              });

              // Update local state with fresh server data
              setCorePersona(latestData.core_persona);
              setPlatformPersonas(latestData.platform_personas || {});
              setQualityMetrics(latestData.quality_metrics || null);

              console.log('✅ UI state updated with latest server data');
            } else {
              console.warn('⚠️ Reload response missing expected data:', latestResponse.data);
            }
          } catch (reloadError) {
            console.warn('⚠️ Failed to reload latest data after save:', reloadError);
            // Don't fail the save operation if reload fails
          }
        } else {
          console.error('❌ Failed to save persona changes:', response.data);
        }
      } catch (error: any) {
        console.error('❌ Error auto-saving persona changes:', error);
        // Don't show user error for auto-save failures to avoid interrupting their editing
      } finally {
        setIsSaving(false);
      }
    }, 2000); // 2 second debounce
  }, [qualityMetrics, selectedPlatforms]);

  // Handle core persona changes with auto-save
  const handleCorePersonaChange = useCallback((updatedPersona: any) => {
    console.log('🔄 Core persona changed:', updatedPersona);
    setCorePersona(updatedPersona);
    debouncedSave(updatedPersona, platformPersonas);
  }, [setCorePersona, debouncedSave, platformPersonas]);

  // Handle platform persona changes with auto-save
  const handlePlatformPersonaChange = useCallback((platformId: string, updatedPersona: any) => {
    console.log('🔄 Platform persona changed:', platformId, updatedPersona);
    const updatedPlatformPersonas = {
      ...platformPersonas,
      [platformId]: updatedPersona
    };
    setPlatformPersonas(updatedPlatformPersonas);
    debouncedSave(corePersona, updatedPlatformPersonas);
  }, [setPlatformPersonas, debouncedSave, corePersona, platformPersonas]);
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isSaving && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SaveIcon sx={{ fontSize: 16, color: '#64748b' }} />
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  Saving...
                </Typography>
              </Box>
            )}
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
              onChange={handleCorePersonaChange}
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
                      onChange={(updatedPersona) => handlePlatformPersonaChange(platformId, updatedPersona)}
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
