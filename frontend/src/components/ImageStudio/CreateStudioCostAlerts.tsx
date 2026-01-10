/**
 * Image Studio Cost Alerts Integration
 * 
 * Example integration of Priority 2 alerts (cost estimation, OSS recommendations)
 * into the Image Studio Create Studio component.
 */

import React, { useEffect, useState } from 'react';
import { Box, Alert, AlertTitle, Button, Collapse, Chip, Stack, Typography } from '@mui/material';
import { usePriority2Alerts, useCostEstimationAlert } from '../../hooks/usePriority2Alerts';
import Priority2AlertBanner from '../shared/Priority2AlertBanner';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { checkPreflight, PreflightOperation } from '../../services/billingService';
import { showToastNotification } from '../../utils/toastNotifications';
import { AttachMoney, Lightbulb, TrendingUp } from '@mui/icons-material';

interface CreateStudioCostAlertsProps {
  userId?: string;
  provider?: string;
  model?: string;
  numVariations?: number;
  onGenerate?: () => void;
}

/**
 * Image Studio Cost Alerts Component
 * 
 * Displays Priority 2 alerts and provides cost estimation before image generation.
 * Shows OSS model recommendations and cost comparisons.
 */
export const CreateStudioCostAlerts: React.FC<CreateStudioCostAlertsProps> = ({
  userId,
  provider = 'auto',
  model,
  numVariations = 1,
  onGenerate,
}) => {
  const { subscription } = useSubscription();
  const { alerts, refreshAlerts, dismissAlert } = usePriority2Alerts({
    userId,
    enabled: !!userId && subscription?.active,
    checkInterval: 120000,
  });

  const { showEstimationAlert } = useCostEstimationAlert();
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null);
  const [ossRecommendation, setOssRecommendation] = useState<{
    model: string;
    savings: number;
    currentCost: number;
  } | null>(null);

  // Estimate cost for image generation
  useEffect(() => {
    const estimateCost = async () => {
      if (!userId || provider === 'auto') return;

      try {
        // Determine actual provider (default to wavespeed for OSS)
        const actualProvider = provider === 'wavespeed' ? 'stability' : provider;
        const actualModel = model || (provider === 'wavespeed' ? 'qwen-image' : 'stable-diffusion');

        const operations: PreflightOperation[] = Array(numVariations).fill(null).map(() => ({
          provider: actualProvider,
          model: actualModel,
          operation_type: 'image_generation',
          tokens_requested: 0,
        }));

        if (operations.length > 0) {
          const preflightResult = await checkPreflight(operations[0]);
          const cost = (preflightResult.estimated_cost || 0) * numVariations;
          setEstimatedCost(cost);

          // Check if OSS alternative would be cheaper
          if (provider !== 'wavespeed' && actualProvider === 'stability') {
            // Compare with OSS model
            const ossOperation: PreflightOperation = {
              provider: 'stability',
              model: 'qwen-image',
              operation_type: 'image_generation',
              tokens_requested: 0,
            };
            const ossResult = await checkPreflight(ossOperation);
            const ossCost = (ossResult.estimated_cost || 0) * numVariations;

            if (ossCost < cost) {
              setOssRecommendation({
                model: 'Qwen Image (OSS)',
                savings: cost - ossCost,
                currentCost: cost,
              });
            }
          }
        }
      } catch (error) {
        console.error('[CreateStudioCostAlerts] Error estimating cost:', error);
      }
    };

    estimateCost();
  }, [userId, provider, model, numVariations]);

  const handleGenerateWithEstimation = async () => {
    if (!estimatedCost || estimatedCost < 0.01) {
      // Low cost - proceed directly
      if (onGenerate) onGenerate();
      return;
    }

    showEstimationAlert(
      estimatedCost,
      `image generation (${numVariations} image${numVariations > 1 ? 's' : ''})`,
      () => {
        if (onGenerate) onGenerate();
      },
      () => {
        showToastNotification('Image generation cancelled', 'info');
      }
    );
  };

  // Filter alerts relevant to Image Studio
  const imageStudioAlerts = alerts.filter(alert => 
    alert.type === 'oss_recommendation' ||
    alert.type === 'cost_trend' ||
    (alert.type === 'cost_estimation' && alert.message.includes('image'))
  );

  // Get OSS model cost info
  const getModelCost = (modelName: string): number => {
    const costs: Record<string, number> = {
      'qwen-image': 0.03,
      'ideogram-v3-turbo': 0.05,
      'stable-diffusion': 0.04,
      'stability-ultra': 0.08,
      'stability-core': 0.03,
    };
    return costs[modelName] || 0.04;
  };

  const currentModelCost = model ? getModelCost(model) : 0.03; // Default to OSS
  const totalEstimatedCost = currentModelCost * numVariations;

  return (
    <Box sx={{ mb: 2 }}>
      {/* Priority 2 Alert Banner */}
      {imageStudioAlerts.length > 0 && (
        <Priority2AlertBanner
          alerts={imageStudioAlerts}
          onDismiss={dismissAlert}
          maxAlerts={2}
        />
      )}

      {/* Cost Estimation Display */}
      <Collapse in={true}>
        <Alert 
          severity="info" 
          icon={<AttachMoney />}
          sx={{ 
            mb: 2,
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
          }}
        >
          <AlertTitle sx={{ fontWeight: 'bold', mb: 0.5, display: 'flex', alignItems: 'center', gap: 1 }}>
            <AttachMoney sx={{ fontSize: 18 }} />
            Estimated Cost
          </AlertTitle>
          <Stack spacing={1}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Typography variant="body2">
                <strong>{numVariations} image{numVariations > 1 ? 's' : ''}</strong> using{' '}
                <strong>{model || (provider === 'wavespeed' ? 'Qwen Image (OSS)' : 'Default')}</strong>:
              </Typography>
              <Chip 
                label={`$${totalEstimatedCost.toFixed(4)}`}
                color="primary"
                size="small"
                sx={{ fontWeight: 'bold' }}
              />
            </Box>

            {/* OSS Recommendation */}
            {ossRecommendation && (
              <Box sx={{ 
                mt: 1, 
                p: 1.5, 
                backgroundColor: 'rgba(251, 191, 36, 0.1)',
                borderRadius: 1,
                border: '1px solid rgba(251, 191, 36, 0.3)',
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Lightbulb sx={{ fontSize: 18, color: '#f59e0b' }} />
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    💡 Cost Savings Opportunity
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Switch to <strong>{ossRecommendation.model}</strong> to save{' '}
                  <strong>${ossRecommendation.savings.toFixed(4)}</strong> per generation
                  ({((ossRecommendation.savings / ossRecommendation.currentCost) * 100).toFixed(0)}% savings).
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    showToastNotification(
                      'OSS models are automatically used as defaults in Basic tier',
                      'info'
                    );
                  }}
                  sx={{ textTransform: 'none' }}
                >
                  Learn More About OSS Models
                </Button>
              </Box>
            )}

            {/* Cost Breakdown */}
            <Box sx={{ mt: 1, fontSize: '0.75rem', color: 'text.secondary' }}>
              <Typography variant="caption">
                Cost per image: ${currentModelCost.toFixed(4)} • Total: ${totalEstimatedCost.toFixed(4)}
                {subscription?.tier === 'basic' && ' (Basic tier uses OSS models by default)'}
              </Typography>
            </Box>
          </Stack>
        </Alert>
      </Collapse>

      {/* Generate Button with Cost Awareness */}
      {onGenerate && (
        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={handleGenerateWithEstimation}
          startIcon={<AttachMoney />}
          sx={{ mt: 1 }}
        >
          Generate {numVariations} Image{numVariations > 1 ? 's' : ''} 
          {estimatedCost && estimatedCost > 0 && (
            <Chip 
              label={`$${estimatedCost.toFixed(4)}`}
              size="small"
              sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
            />
          )}
        </Button>
      )}
    </Box>
  );
};

/**
 * Hook for Image Studio cost estimation
 * Use this in Image Studio components before triggering image generation
 */
export const useImageStudioCostEstimation = () => {
  const { showEstimationAlert } = useCostEstimationAlert();

  const estimateAndGenerate = async (
    provider: string,
    model: string,
    numVariations: number,
    onGenerate: () => void,
    userId?: string
  ) => {
    if (!userId) {
      onGenerate();
      return;
    }

    try {
      const actualProvider = provider === 'wavespeed' ? 'stability' : provider;
      const operations: PreflightOperation[] = Array(numVariations).fill(null).map(() => ({
        provider: actualProvider,
        model: model || (provider === 'wavespeed' ? 'qwen-image' : 'stable-diffusion'),
        operation_type: 'image_generation',
        tokens_requested: 0,
      }));

      if (operations.length > 0) {
        const preflightResult = await checkPreflight(operations[0]);
        const estimatedCost = (preflightResult.estimated_cost || 0) * numVariations;

        if (estimatedCost > 0.01) {
          showEstimationAlert(
            estimatedCost,
            `image generation (${numVariations} image${numVariations > 1 ? 's' : ''})`,
            onGenerate,
            () => showToastNotification('Image generation cancelled', 'info')
          );
        } else {
          onGenerate();
        }
      } else {
        onGenerate();
      }
    } catch (error) {
      console.error('[ImageStudioCostEstimation] Error:', error);
      onGenerate();
    }
  };

  return { estimateAndGenerate };
};

export default CreateStudioCostAlerts;
