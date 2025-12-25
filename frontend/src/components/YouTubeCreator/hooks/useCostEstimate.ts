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
  imageModel?: 'ideogram-v3-turbo' | 'qwen-image';
}

export const useCostEstimate = ({ activeStep, scenes, resolution, renderTaskId, imageModel = 'ideogram-v3-turbo' }: UseCostEstimateParams) => {
  const [costEstimate, setCostEstimate] = useState<CostEstimate | null>(null);
  const [loadingCostEstimate, setLoadingCostEstimate] = useState(false);

  useEffect(() => {
    // Fetch cost estimate on both "Generate Assets" (step 2) and "Render Video" (step 3) steps
    if ((activeStep === 2 || activeStep === 3) && scenes.length > 0 && !renderTaskId) {
      const fetchCostEstimate = async () => {
        setLoadingCostEstimate(true);
        try {
          const enabledScenes = scenes.filter(s => s.enabled !== false);
          
          // Only fetch if all enabled scenes have images and audio
          const allScenesReady = enabledScenes.every(s => s.imageUrl && s.audioUrl);
          
          if (!allScenesReady && activeStep === 3) {
            // On render step, require all scenes to be ready
            setCostEstimate(null);
            setLoadingCostEstimate(false);
            return;
          }
          
          const response = await youtubeApi.estimateCost({
            scenes: enabledScenes,
            resolution: resolution,
            imageModel: imageModel,
          });
          if (response.success && response.estimate) {
            setCostEstimate(response.estimate);
          } else {
            setCostEstimate(null);
          }
        } catch (err: any) {
          console.error('Error estimating cost:', err);
          setCostEstimate(null);
        } finally {
          setLoadingCostEstimate(false);
        }
      };

      fetchCostEstimate();
    } else {
      // Reset cost estimate when not on relevant steps
      setCostEstimate(null);
      setLoadingCostEstimate(false);
    }
  }, [activeStep, scenes, resolution, renderTaskId, imageModel]);

  return { costEstimate, loadingCostEstimate };
};

