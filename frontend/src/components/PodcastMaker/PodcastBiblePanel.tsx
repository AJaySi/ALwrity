import React from 'react';
import { 
  Box, 
  Typography, 
  Stack, 
  TextField, 
  Chip, 
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  ExpandMore as ExpandMoreIcon, 
  AutoFixHigh as AutoFixHighIcon,
  Psychology as PsychologyIcon,
  Groups as GroupsIcon,
  BrandingWatermark as BrandIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface PodcastBiblePanelProps {
  bible: any;
  onUpdate: (updatedBible: any) => void;
}

export const PodcastBiblePanel: React.FC<PodcastBiblePanelProps> = ({ bible, onUpdate }) => {
  if (!bible) return null;

  const handleUpdateHost = (field: string, value: any) => {
    onUpdate({
      ...bible,
      host: { ...bible.host, [field]: value }
    });
  };

  const handleUpdateAudience = (field: string, value: any) => {
    onUpdate({
      ...bible,
      audience: { ...bible.audience, [field]: value }
    });
  };

  const handleUpdateBrand = (field: string, value: any) => {
    onUpdate({
      ...bible,
      brand: { ...bible.brand, [field]: value }
    });
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
        <AutoFixHighIcon color="primary" />
        <Typography variant="h6" fontWeight="bold" color="#1e293b">
          Podcast Bible
        </Typography>
        <Tooltip title="Hyper-personalized context derived from your onboarding data. This grounds all research and script generation.">
          <IconButton size="small">
            <InfoIcon fontSize="small" sx={{ color: '#94a3b8' }} />
          </IconButton>
        </Tooltip>
      </Stack>

      <Stack spacing={2}>
        {/* Host Persona */}
        <Accordion defaultExpanded sx={{ borderRadius: 2, '&:before': { display: 'none' }, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Stack direction="row" spacing={1} alignItems="center">
              <PsychologyIcon sx={{ color: '#6366f1' }} />
              <Typography fontWeight="600">Host Persona</Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Host Background"
                size="small"
                value={bible.host?.background || ''}
                onChange={(e) => handleUpdateHost('background', e.target.value)}
                multiline
                rows={2}
              />
              <Stack direction="row" spacing={2}>
                <TextField
                  fullWidth
                  label="Expertise Level"
                  size="small"
                  value={bible.host?.expertise_level || ''}
                  onChange={(e) => handleUpdateHost('expertise_level', e.target.value)}
                />
                <TextField
                  fullWidth
                  label="Vocal Style"
                  size="small"
                  value={bible.host?.vocal_style || ''}
                  onChange={(e) => handleUpdateHost('vocal_style', e.target.value)}
                />
              </Stack>
            </Stack>
          </AccordionDetails>
        </Accordion>

        {/* Audience DNA */}
        <Accordion sx={{ borderRadius: 2, '&:before': { display: 'none' }, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Stack direction="row" spacing={1} alignItems="center">
              <GroupsIcon sx={{ color: '#ec4899' }} />
              <Typography fontWeight="600">Audience DNA</Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Audience Expertise"
                size="small"
                value={bible.audience?.expertise_level || ''}
                onChange={(e) => handleUpdateAudience('expertise_level', e.target.value)}
              />
              <Box>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                  Interests
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {bible.audience?.interests?.map((interest: string, idx: number) => (
                    <Chip key={idx} label={interest} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                  Pain Points
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {bible.audience?.pain_points?.map((point: string, idx: number) => (
                    <Chip key={idx} label={point} size="small" color="error" variant="outlined" />
                  ))}
                </Box>
              </Box>
            </Stack>
          </AccordionDetails>
        </Accordion>

        {/* Brand DNA */}
        <Accordion sx={{ borderRadius: 2, '&:before': { display: 'none' }, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Stack direction="row" spacing={1} alignItems="center">
              <BrandIcon sx={{ color: '#10b981' }} />
              <Typography fontWeight="600">Brand DNA</Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Industry"
                size="small"
                value={bible.brand?.industry || ''}
                onChange={(e) => handleUpdateBrand('industry', e.target.value)}
              />
              <Stack direction="row" spacing={2}>
                <TextField
                  fullWidth
                  label="Tone"
                  size="small"
                  value={bible.brand?.tone || ''}
                  onChange={(e) => handleUpdateBrand('tone', e.target.value)}
                />
                <TextField
                  fullWidth
                  label="Style"
                  size="small"
                  value={bible.brand?.communication_style || ''}
                  onChange={(e) => handleUpdateBrand('communication_style', e.target.value)}
                />
              </Stack>
            </Stack>
          </AccordionDetails>
        </Accordion>
      </Stack>
    </Box>
  );
};
