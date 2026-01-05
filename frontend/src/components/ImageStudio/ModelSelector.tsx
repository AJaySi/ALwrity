import React, { useState, useMemo } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Typography,
  Stack,
  TextField,
  InputAdornment,
  CircularProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import InfoIcon from '@mui/icons-material/Info';
import { alpha } from '@mui/material/styles';
import { EditingModel, FaceSwapModel } from '../../hooks/useImageStudio';

type ModelType = EditingModel | FaceSwapModel;

interface ModelSelectorProps {
  models: ModelType[];
  selectedModel?: string;
  recommendedModel?: string;
  recommendationReason?: string;
  onModelSelect: (modelId: string) => void;
  loading?: boolean;
  operation?: string;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModel,
  recommendedModel,
  recommendationReason,
  onModelSelect,
  loading = false,
  operation,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [tierFilter, setTierFilter] = useState<string>('all');

  const filteredModels = useMemo(() => {
    let filtered = models;

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (model) =>
          model.name.toLowerCase().includes(query) ||
          model.description.toLowerCase().includes(query) ||
          model.id.toLowerCase().includes(query)
      );
    }

    // Filter by tier
    if (tierFilter !== 'all') {
      filtered = filtered.filter((model) => model.tier === tierFilter);
    }

    return filtered;
  }, [models, searchQuery, tierFilter]);

  const groupedModels = useMemo(() => {
    const groups: Record<string, ModelType[]> = {
      budget: [],
      mid: [],
      premium: [],
    };

    filteredModels.forEach((model) => {
      groups[model.tier].push(model);
    });

    return groups;
  }, [filteredModels]);

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

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  return (
    <Stack spacing={2}>
      {/* Search and Filter */}
      <Stack direction="row" spacing={2}>
        <TextField
          size="small"
          placeholder="Search models..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{ flex: 1 }}
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Tier</InputLabel>
          <Select
            value={tierFilter}
            label="Tier"
            onChange={(e) => setTierFilter(e.target.value)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="budget">Budget</MenuItem>
            <MenuItem value="mid">Mid</MenuItem>
            <MenuItem value="premium">Premium</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      {/* Model Selector */}
      <FormControl fullWidth>
        <InputLabel>AI Model</InputLabel>
        <Select
          value={selectedModel || ''}
          label="AI Model"
          onChange={(e) => onModelSelect(e.target.value)}
          renderValue={(value) => {
            const model = models.find((m) => m.id === value);
            if (!model) return value;
            return (
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="body2">{model.name}</Typography>
                <Chip
                  size="small"
                  label={getTierLabel(model.tier)}
                  sx={{
                    height: 20,
                    fontSize: '0.7rem',
                    bgcolor: alpha(getTierColor(model.tier), 0.2),
                    color: getTierColor(model.tier),
                    fontWeight: 600,
                  }}
                />
                {value === recommendedModel && (
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
            );
          }}
        >
          {Object.entries(groupedModels).map(([tier, tierModels]) => {
            if (tierModels.length === 0) return null;
            return [
              <MenuItem key={`header-${tier}`} disabled>
                <Typography variant="overline" sx={{ fontWeight: 700 }}>
                  {getTierLabel(tier)} ({tierModels.length})
                </Typography>
              </MenuItem>,
              ...tierModels.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ width: '100%' }}>
                    <Box sx={{ flex: 1 }}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Typography variant="body2" fontWeight={500}>
                          {model.name}
                        </Typography>
                        {model.id === recommendedModel && (
                          <Chip
                            size="small"
                            label="Recommended"
                            sx={{
                              height: 18,
                              fontSize: '0.65rem',
                              bgcolor: alpha('#f59e0b', 0.2),
                              color: '#f59e0b',
                              fontWeight: 600,
                            }}
                          />
                        )}
                      </Stack>
                      <Stack direction="row" spacing={1} alignItems="center" mt={0.5}>
                        <Typography variant="caption" color="text.secondary">
                          ${model.cost.toFixed(3)} {('max_resolution' in model) ? 'per edit' : 'per swap'}
                        </Typography>
                        {'max_resolution' in model && model.max_resolution && (
                          <>
                            <Typography variant="caption" color="text.secondary">
                              •
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {model.max_resolution[0]}×{model.max_resolution[1]}
                            </Typography>
                          </>
                        )}
                        {'max_faces' in model && model.max_faces && model.max_faces > 1 && (
                          <>
                            <Typography variant="caption" color="text.secondary">
                              •
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Up to {model.max_faces} faces
                            </Typography>
                          </>
                        )}
                      </Stack>
                    </Box>
                    <Chip
                      size="small"
                      label={getTierLabel(model.tier)}
                      sx={{
                        height: 20,
                        fontSize: '0.7rem',
                        bgcolor: alpha(getTierColor(model.tier), 0.2),
                        color: getTierColor(model.tier),
                        fontWeight: 600,
                      }}
                    />
                  </Stack>
                </MenuItem>
              )),
            ];
          })}
        </Select>
      </FormControl>

      {/* Recommendation Badge */}
      {recommendedModel && recommendationReason && selectedModel === recommendedModel && (
        <Box
          sx={{
            p: 1.5,
            borderRadius: 2,
            bgcolor: alpha('#f59e0b', 0.1),
            border: `1px solid ${alpha('#f59e0b', 0.3)}`,
          }}
        >
          <Stack direction="row" spacing={1} alignItems="flex-start">
            <InfoIcon sx={{ fontSize: 18, color: '#f59e0b', mt: 0.25 }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" fontWeight={600} color="#f59e0b">
                Recommended for you
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                {recommendationReason}
              </Typography>
            </Box>
          </Stack>
        </Box>
      )}

      {/* Selected Model Info */}
      {selectedModel && (
        <Box
          sx={{
            p: 1.5,
            borderRadius: 2,
            bgcolor: alpha('#667eea', 0.08),
            border: `1px solid ${alpha('#667eea', 0.2)}`,
          }}
        >
          {(() => {
            const model = models.find((m) => m.id === selectedModel);
            if (!model) return null;
            return (
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="subtitle2" fontWeight={600}>
                    {model.name}
                  </Typography>
                  <Chip
                    size="small"
                    label={`$${model.cost.toFixed(3)}`}
                    sx={{
                      bgcolor: alpha('#667eea', 0.2),
                      color: '#667eea',
                      fontWeight: 600,
                    }}
                  />
                </Stack>
                <Typography variant="caption" color="text.secondary">
                  {model.description}
                </Typography>
                {model.features.length > 0 && (
                  <Stack direction="row" spacing={0.5} flexWrap="wrap" gap={0.5}>
                    {model.features.slice(0, 3).map((feature, idx) => (
                      <Chip
                        key={idx}
                        size="small"
                        label={feature}
                        sx={{
                          height: 20,
                          fontSize: '0.65rem',
                          bgcolor: alpha('#667eea', 0.1),
                          color: '#667eea',
                        }}
                      />
                    ))}
                  </Stack>
                )}
              </Stack>
            );
          })()}
        </Box>
      )}
    </Stack>
  );
};
