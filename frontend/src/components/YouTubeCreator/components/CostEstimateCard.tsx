/**
 * Cost Estimate Card Component
 * 
 * Displays professional cost estimate with breakdown and per-scene costs.
 */

import React from 'react';
import {
  Box,
  Typography,
  Stack,
  CircularProgress,
  Alert,
} from '@mui/material';
import { CostEstimate } from '../../../services/youtubeApi';

interface CostEstimateCardProps {
  costEstimate: CostEstimate | null;
  loadingCostEstimate: boolean;
}

export const CostEstimateCard: React.FC<CostEstimateCardProps> = React.memo(({
  costEstimate,
  loadingCostEstimate,
}) => {
  if (loadingCostEstimate) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
        <CircularProgress size={16} />
        <Typography variant="body2" color="text.secondary">
          Calculating cost estimate...
        </Typography>
      </Box>
    );
  }

  if (!costEstimate) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Unable to calculate cost estimate. Please check your scenes and try again.
      </Alert>
    );
  }

  return (
    <Box
      sx={{
        mt: 3,
        p: 3,
        bgcolor: '#ffffff',
        borderRadius: 2,
        border: '2px solid #e5e7eb',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 700,
            fontSize: '1rem',
            color: '#111827',
            letterSpacing: '-0.01em',
          }}
        >
          Estimated Cost
        </Typography>
      </Box>
      
      <Box sx={{ mb: 2.5 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            fontSize: '2rem',
            color: '#111827',
            lineHeight: 1.2,
            mb: 0.5,
          }}
        >
          ${costEstimate.total_cost.toFixed(2)}
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#6b7280',
            fontSize: '0.875rem',
            fontWeight: 500,
          }}
        >
          Range: ${costEstimate.estimated_cost_range.min.toFixed(2)} - ${costEstimate.estimated_cost_range.max.toFixed(2)}
        </Typography>
      </Box>

      <Box
        sx={{
          p: 2,
          bgcolor: '#f9fafb',
          borderRadius: 1.5,
          border: '1px solid #e5e7eb',
          mb: 2,
        }}
      >
        <Typography
          variant="body2"
          sx={{
            color: '#374151',
            fontSize: '0.875rem',
            lineHeight: 1.6,
            mb: 0.5,
          }}
        >
          <strong>{costEstimate.num_scenes} scenes</strong> × <strong>${costEstimate.price_per_second.toFixed(2)}/second</strong>
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#374151',
            fontSize: '0.875rem',
            lineHeight: 1.6,
            mb: 0.5,
          }}
        >
          Total duration: <strong>~{Math.round(costEstimate.total_duration_seconds)} seconds</strong>
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#374151',
            fontSize: '0.875rem',
            lineHeight: 1.6,
          }}
        >
          Price per second: <strong>${costEstimate.price_per_second.toFixed(2)}</strong> ({costEstimate.resolution})
        </Typography>
      </Box>

      {costEstimate.scene_costs.length > 0 && (
        <Box
          sx={{
            pt: 2,
            borderTop: '2px solid #e5e7eb',
          }}
        >
          <Typography
            variant="subtitle2"
            sx={{
              fontWeight: 600,
              fontSize: '0.875rem',
              color: '#111827',
              mb: 1.5,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            Per Scene Breakdown
          </Typography>
          <Stack spacing={0.75}>
            {costEstimate.scene_costs.slice(0, 5).map((sceneCost) => (
              <Box
                key={sceneCost.scene_number}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  py: 0.75,
                  px: 1.5,
                  bgcolor: '#ffffff',
                  borderRadius: 1,
                  border: '1px solid #e5e7eb',
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    color: '#374151',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                  }}
                >
                  Scene {sceneCost.scene_number}: {sceneCost.actual_duration}s
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: '#111827',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                  }}
                >
                  ${sceneCost.cost.toFixed(2)}
                </Typography>
              </Box>
            ))}
            {costEstimate.scene_costs.length > 5 && (
              <Typography
                variant="body2"
                sx={{
                  color: '#6b7280',
                  fontSize: '0.875rem',
                  textAlign: 'center',
                  py: 0.5,
                }}
              >
                ... and {costEstimate.scene_costs.length - 5} more scenes
              </Typography>
            )}
          </Stack>
        </Box>
      )}
    </Box>
  );
});

CostEstimateCard.displayName = 'CostEstimateCard';

