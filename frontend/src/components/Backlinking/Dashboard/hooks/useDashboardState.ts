/**
 * Dashboard State Hook
 *
 * Centralized state management for the Backlinking Dashboard
 */

import { useState } from 'react';
import { Campaign, SnackbarState } from '../types/dashboard.types';

export const useDashboardState = () => {
  // Modal states
  const [showWizard, setShowWizard] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showEmailAutomation, setShowEmailAutomation] = useState(false);
  const [showAIResearch, setShowAIResearch] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [aiEnhanced, setAiEnhanced] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  // Data states
  const [aiResearchKeywords, setAiResearchKeywords] = useState<string[]>([]);

  // UI states
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Actions
  const showSnackbar = (message: string, severity: SnackbarState['severity'] = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const onToggleAI = () => {
    setAiEnhanced(prev => !prev);
  };

  const onShowAIModal = () => {
    // This could open an AI settings modal or info panel
    showSnackbar('AI Enhancement settings can be configured here', 'info');
  };

  const resetModalStates = () => {
    setSelectedCampaign(null);
    setShowAnalytics(false);
    setShowEmailAutomation(false);
    setShowAIResearch(false);
    setShowHelpModal(false);
    setConfirmDelete(null);
  };

  return {
    // Modal states
    showWizard,
    setShowWizard,
    selectedCampaign,
    setSelectedCampaign,
    showAnalytics,
    setShowAnalytics,
    showEmailAutomation,
    setShowEmailAutomation,
    showAIResearch,
    setShowAIResearch,
    showHelpModal,
    setShowHelpModal,
    confirmDelete,
    setConfirmDelete,

    // Data states
    aiEnhanced,
    aiResearchKeywords,
    setAiResearchKeywords,

    // UI states
    loadingAction,
    setLoadingAction,
    snackbar,

    // Actions
    onToggleAI,
    onShowAIModal,
    showSnackbar,
    handleCloseSnackbar,
    resetModalStates,
  };
};