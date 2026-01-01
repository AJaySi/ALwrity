import React, { useState } from 'react';
import {
  Box,
  Paper,
  Stack,
  Typography,
  FormControl,
  Select,
  MenuItem,
  Chip,
  Tooltip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import { VIDEO_MODELS, type VideoModelInfo } from '../models/videoModels';

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (modelId: string) => void;
  duration: number;
  resolution: string;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  selectedModel,
  onModelChange,
  duration,
  resolution,
}) => {
  const [expandedModel, setExpandedModel] = useState<string | false>(false);
  const selectedModelInfo = VIDEO_MODELS.find(m => m.id === selectedModel);

  const handleAccordionChange = (modelId: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedModel(isExpanded ? modelId : false);
  };

  const calculateCost = (model: VideoModelInfo): string => {
    const costPerSecond = model.costPerSecond[resolution] || model.costPerSecond[Object.keys(model.costPerSecond)[0]];
    const totalCost = costPerSecond * duration;
    return `$${totalCost.toFixed(2)}`;
  };

  const isModelCompatible = (model: VideoModelInfo): { compatible: boolean; reason?: string } => {
    if (!model.durations.includes(duration)) {
      return { compatible: false, reason: `Duration ${duration}s not supported. Available: ${model.durations.join(', ')}s` };
    }
    if (!model.resolutions.includes(resolution)) {
      return { compatible: false, reason: `Resolution ${resolution} not supported. Available: ${model.resolutions.join(', ')}` };
    }
    return { compatible: true };
  };

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#0f172a' }}>
          AI Model
        </Typography>
        <Tooltip
          title="Choose the AI model that best fits your content needs. Each model has different strengths, pricing, and capabilities."
          arrow
        >
          <IconButton size="small" sx={{ color: '#64748b' }}>
            <HelpOutlineIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <Select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          sx={{
            borderRadius: 2,
            backgroundColor: '#fff',
            '& fieldset': { borderColor: '#e2e8f0' },
            '&:hover fieldset': { borderColor: '#cbd5f5' },
            '&.Mui-focused fieldset': {
              borderColor: '#7c3aed',
            },
          }}
        >
          {VIDEO_MODELS.map((model) => {
            const compatibility = isModelCompatible(model);
            return (
              <MenuItem
                key={model.id}
                value={model.id}
                disabled={!compatibility.compatible}
              >
                <Stack direction="row" spacing={1} alignItems="center" sx={{ width: '100%' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography sx={{ color: compatibility.compatible ? '#0f172a' : '#94a3b8', fontWeight: 600 }}>
                      {model.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#64748b', display: 'block' }}>
                      {model.tagline}
                    </Typography>
                    {!compatibility.compatible && (
                      <Typography variant="caption" sx={{ color: '#ef4444', display: 'block', mt: 0.5 }}>
                        {compatibility.reason}
                      </Typography>
                    )}
                  </Box>
                  {compatibility.compatible && (
                    <Chip
                      label={calculateCost(model)}
                      size="small"
                      sx={{
                        backgroundColor: '#f0f9ff',
                        color: '#0369a1',
                        fontWeight: 600,
                        fontSize: '0.75rem',
                      }}
                    />
                  )}
                </Stack>
              </MenuItem>
            );
          })}
        </Select>
      </FormControl>

      {/* Selected Model Details */}
      {selectedModelInfo && (
        <Paper
          elevation={0}
          sx={{
            border: '1px solid #e2e8f0',
            borderRadius: 2,
            p: 2,
            backgroundColor: '#f8fafc',
          }}
        >
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a', mb: 1 }}>
                {selectedModelInfo.name}
              </Typography>
              <Typography variant="body2" sx={{ color: '#475569' }}>
                {selectedModelInfo.description}
              </Typography>
            </Box>

            <Divider />

            {/* Best For */}
            <Box>
              <Typography variant="caption" sx={{ fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                Best For
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 1 }}>
                {selectedModelInfo.bestFor.slice(0, 3).map((useCase) => (
                  <Chip
                    key={useCase}
                    label={useCase}
                    size="small"
                    sx={{
                      backgroundColor: '#e0e7ff',
                      color: '#4338ca',
                      fontSize: '0.7rem',
                    }}
                  />
                ))}
              </Stack>
            </Box>

            {/* Cost & Duration Info */}
            <Box>
              <Stack direction="row" spacing={2}>
                <Box>
                  <Typography variant="caption" sx={{ color: '#64748b', display: 'block' }}>
                    Estimated Cost
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                    {calculateCost(selectedModelInfo)}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" sx={{ color: '#64748b', display: 'block' }}>
                    Audio Support
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: selectedModelInfo.audioSupport ? '#059669' : '#dc2626' }}>
                    {selectedModelInfo.audioSupport ? 'Yes' : 'No'}
                  </Typography>
                </Box>
              </Stack>
            </Box>

            {/* Expandable Details */}
            <Accordion
              expanded={expandedModel === selectedModel}
              onChange={handleAccordionChange(selectedModel)}
              sx={{
                boxShadow: 'none',
                border: '1px solid #e2e8f0',
                borderRadius: 2,
                '&:before': { display: 'none' },
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon sx={{ color: '#64748b' }} />}
                sx={{ minHeight: 40 }}
              >
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#64748b' }}>
                  View Full Details & Tips
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  {/* Strengths */}
                  <Box>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: '#64748b', textTransform: 'uppercase', display: 'block', mb: 1 }}>
                      Strengths
                    </Typography>
                    <List dense sx={{ py: 0 }}>
                      {selectedModelInfo.strengths.map((strength, idx) => (
                        <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CheckCircleIcon sx={{ fontSize: 16, color: '#059669' }} />
                          </ListItemIcon>
                          <ListItemText
                            primary={strength}
                            primaryTypographyProps={{
                              variant: 'body2',
                              sx: { color: '#475569' },
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>

                  {/* Tips */}
                  <Box>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: '#64748b', textTransform: 'uppercase', display: 'block', mb: 1 }}>
                      Pro Tips
                    </Typography>
                    <List dense sx={{ py: 0 }}>
                      {selectedModelInfo.tips.map((tip, idx) => (
                        <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <InfoIcon sx={{ fontSize: 16, color: '#0369a1' }} />
                          </ListItemIcon>
                          <ListItemText
                            primary={tip}
                            primaryTypographyProps={{
                              variant: 'body2',
                              sx: { color: '#475569' },
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                </Stack>
              </AccordionDetails>
            </Accordion>
          </Stack>
        </Paper>
      )}

      {/* Model Comparison Link */}
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Tooltip title="Compare all models side-by-side to find the best fit for your needs">
          <Typography
            variant="caption"
            sx={{
              color: '#667eea',
              cursor: 'pointer',
              textDecoration: 'underline',
              '&:hover': { color: '#5568d3' },
            }}
          >
            Compare all models →
          </Typography>
        </Tooltip>
      </Box>
    </Box>
  );
};
