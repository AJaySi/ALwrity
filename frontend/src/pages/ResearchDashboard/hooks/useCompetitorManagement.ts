import { useState } from 'react';
import { getCompetitorAnalysis, CompetitorAnalysisResponse } from '../../../api/researchConfig';

/**
 * Hook to manage competitor analysis modal state and operations
 */
export const useCompetitorManagement = () => {
  const [showCompetitorModal, setShowCompetitorModal] = useState(false);
  const [competitorData, setCompetitorData] = useState<CompetitorAnalysisResponse | null>(null);
  const [loadingCompetitors, setLoadingCompetitors] = useState(false);
  const [competitorError, setCompetitorError] = useState<string | null>(null);

  const handleOpenCompetitorModal = async () => {
    console.log('[useCompetitorManagement] ===== START: Opening competitor analysis modal =====');
    setShowCompetitorModal(true);
    setLoadingCompetitors(true);
    setCompetitorError(null);
    
    try {
      console.log('[useCompetitorManagement] Calling getCompetitorAnalysis()...');
      const data = await getCompetitorAnalysis();
      console.log('[useCompetitorManagement] Received data:', {
        success: data.success,
        competitorsCount: data.competitors?.length || 0,
        error: data.error,
        hasCompetitors: !!data.competitors && data.competitors.length > 0
      });
      
      setCompetitorData(data);
      if (!data.success) {
        const errorMsg = data.error || 'Failed to load competitor data';
        console.error('[useCompetitorManagement] ❌ Failed to load competitor data:', errorMsg);
        setCompetitorError(errorMsg);
      } else {
        console.log('[useCompetitorManagement] ✅ Successfully loaded competitor data');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to load competitor data';
      console.error('[useCompetitorManagement] ❌ EXCEPTION:', error);
      setCompetitorError(errorMsg);
      setCompetitorData(null);
    } finally {
      setLoadingCompetitors(false);
      console.log('[useCompetitorManagement] ===== END: Opening competitor analysis modal =====');
    }
  };

  const handleRefreshCompetitors = (newData: CompetitorAnalysisResponse) => {
    setCompetitorData(newData);
    setCompetitorError(null);
  };

  return {
    showCompetitorModal,
    competitorData,
    loadingCompetitors,
    competitorError,
    handleOpenCompetitorModal,
    handleRefreshCompetitors,
    setShowCompetitorModal,
  };
};
