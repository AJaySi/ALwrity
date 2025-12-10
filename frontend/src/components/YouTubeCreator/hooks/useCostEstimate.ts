/**
 * Custom hook for fetching cost estimates
 */

import { useEffect, useState } from 'react';
import { youtubeApi, type Scene, type CostEstimate } from '../../../services/youtubeApi';
import { type Resolution } from '../constants';

interface UseCostEstimateParams {
  activeStep: number;
  scenes: Scene[];
  resolution: Resolution;
  renderTaskId: string | null;
}

export const useCostEstimate = ({ activeStep, scenes, resolution, renderTaskId }: UseCostEstimateParams) => {
  const [costEstimate, setCostEstimate] = useState<CostEstimate | null>(null);
  const [loadingCostEstimate, setLoadingCostEstimate] = useState(false);

  useEffect(() => {
    if (activeStep === 2 && scenes.length > 0 && !renderTaskId) {
      const fetchCostEstimate = async () => {
        setLoadingCostEstimate(true);
        try {
          const enabledScenes = scenes.filter(s => s.enabled !== false);
          const response = await youtubeApi.estimateCost({
            scenes: enabledScenes,
            resolution: resolution,
          });
          if (response.success && response.estimate) {
            setCostEstimate(response.estimate);
          }
        } catch (err: any) {
          console.error('Error estimating cost:', err);
          setCostEstimate(null);
        } finally {
          setLoadingCostEstimate(false);
        }
      };

      fetchCostEstimate();
    }
  }, [activeStep, scenes, resolution, renderTaskId]);

  return { costEstimate, loadingCostEstimate };
};

