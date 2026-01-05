import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
  Box,
  Button,
  Divider,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { alpha } from '@mui/material/styles';
import { EditingModel } from '../../hooks/useImageStudio';

interface ModelInfoCardProps {
  model: EditingModel;
  isSelected: boolean;
  isRecommended: boolean;
  onSelect: () => void;
  onLearnMore?: () => void;
}

export const ModelInfoCard: React.FC<ModelInfoCardProps> = ({
  model,
  isSelected,
  isRecommended,
  onSelect,
  onLearnMore,
}) => {
  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'budget':
        return '#10b981';
      case 'mid':
        return '#3b82f6';
      case 'premium':
        return '#8b5cf6';
      default:
        return '#6b7280';
    }
  };

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'budget':
        return 'Budget';
      case 'mid':
        return 'Mid';
      case 'premium':
        return 'Premium';
      default:
        return tier;
    }
  };

  return (
    <Card
      sx={{
        borderRadius: 3,
        borderWidth: 2,
        borderStyle: 'solid',
        borderColor: isSelected
          ? alpha('#667eea', 0.8)
          : isRecommended
          ? alpha('#f59e0b', 0.4)
          : 'transparent',
        background: isSelected
          ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15))'
          : 'rgba(255,255,255,0.05)',
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: alpha('#667eea', 0.6),
          background: 'rgba(255,255,255,0.08)',
        },
      }}
    >
      <CardContent>
        <Stack spacing={2}>
          {/* Header */}
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" mb={0.5}>
                <Typography variant="subtitle1" fontWeight={700}>
                  {model.name}
                </Typography>
                {isSelected && (
                  <CheckCircleIcon sx={{ fontSize: 18, color: '#667eea' }} />
                )}
                {isRecommended && (
                  <Chip
                    size="small"
                    label="Recommended"
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      bgcolor: alpha('#f59e0b', 0.2),
                      color: '#f59e0b',
                      fontWeight: 600,
                    }}
                  />
                )}
              </Stack>
              <Chip
                size="small"
                label={getTierLabel(model.tier)}
                sx={{
                  bgcolor: alpha(getTierColor(model.tier), 0.2),
                  color: getTierColor(model.tier),
                  fontWeight: 600,
                  fontSize: '0.7rem',
                }}
              />
            </Box>
            <Typography
              variant="h6"
              fontWeight={700}
              sx={{
                color: '#667eea',
              }}
            >
              ${model.cost.toFixed(3)}
            </Typography>
          </Stack>

          {/* Description */}
          <Typography variant="body2" color="text.secondary">
            {model.description}
          </Typography>

          <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

          {/* Details */}
          <Stack spacing={1}>
            <Stack direction="row" spacing={2}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Max Resolution
                </Typography>
                <Typography variant="body2" fontWeight={600}>
                  {model.max_resolution[0]}×{model.max_resolution[1]}
                </Typography>
              </Box>
              {model.cost_8k && (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    8K Cost
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    ${model.cost_8k.toFixed(3)}
                  </Typography>
                </Box>
              )}
            </Stack>

            {/* Features */}
            {model.features.length > 0 && (
              <Box>
                <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                  Features
                </Typography>
                <Stack direction="row" spacing={0.5} flexWrap="wrap" gap={0.5}>
                  {model.features.map((feature, idx) => (
                    <Chip
                      key={idx}
                      size="small"
                      label={feature}
                      sx={{
                        height: 22,
                        fontSize: '0.7rem',
                        bgcolor: alpha('#667eea', 0.1),
                        color: '#667eea',
                      }}
                    />
                  ))}
                </Stack>
              </Box>
            )}

            {/* Use Cases */}
            {model.use_cases.length > 0 && (
              <Box>
                <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                  Best For
                </Typography>
                <Stack spacing={0.5}>
                  {model.use_cases.slice(0, 3).map((useCase, idx) => (
                    <Typography key={idx} variant="caption" color="text.secondary">
                      • {useCase}
                    </Typography>
                  ))}
                </Stack>
              </Box>
            )}
          </Stack>

          {/* Actions */}
          <Stack direction="row" spacing={1}>
            <Button
              variant={isSelected ? 'contained' : 'outlined'}
              onClick={onSelect}
              fullWidth
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                ...(isSelected
                  ? {
                      background: 'linear-gradient(90deg, #667eea, #764ba2)',
                      '&:hover': {
                        background: 'linear-gradient(90deg, #5568d3, #65408b)',
                      },
                    }
                  : {}),
              }}
            >
              {isSelected ? 'Selected' : 'Select Model'}
            </Button>
            {onLearnMore && (
              <Button
                variant="outlined"
                onClick={onLearnMore}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  minWidth: 100,
                }}
              >
                Learn More
              </Button>
            )}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
};
