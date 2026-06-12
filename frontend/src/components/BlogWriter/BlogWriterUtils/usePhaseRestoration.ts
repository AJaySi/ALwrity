import { useEffect, useRef } from 'react';
import { debug } from '../../../utils/debug';

interface UsePhaseRestorationProps {
  copilotKitAvailable: boolean;
  research: any;
  phases: any[];
  currentPhase: string;
  navigateToPhase: (phase: string) => void;
  setCurrentPhase: (phase: string) => void;
  resetUserSelection?: () => void;
}

export const usePhaseRestoration = ({
  copilotKitAvailable,
  research,
  phases,
  currentPhase,
  navigateToPhase,
  setCurrentPhase,
  resetUserSelection,
}: UsePhaseRestorationProps) => {
  const hasRestoredRef = useRef(false);

  useEffect(() => {
    if (!copilotKitAvailable && !research && phases.length > 0 && currentPhase !== 'research' && !hasRestoredRef.current) {
      navigateToPhase('research');
      hasRestoredRef.current = true;
      debug.log('[BlogWriter] Auto-navigating to research phase (CopilotKit unavailable)');
    }
  }, [copilotKitAvailable, research, phases.length, currentPhase, navigateToPhase]);

  // Restore phase from navigation state on mount (after subscription renewal)
  // Note: The PricingPage restores the phase to localStorage before redirecting
  // This effect ensures the phase is applied when BlogWriter loads
  useEffect(() => {
    try {
      // Wait for phases to be initialized
      if (phases.length === 0) {
        return;
      }
      
      // Check if we just returned from pricing page (has restored phase in localStorage)
      const restoredPhase = localStorage.getItem('blogwriter_current_phase');
      const userSelectedPhase = localStorage.getItem('blogwriter_user_selected_phase') === 'true';
      
      // Determine if we should restore based on user selection OR publish completion
      const publishCompleted = localStorage.getItem('blog_publish_completed') === 'true';
      const shouldRestore = restoredPhase && restoredPhase !== currentPhase && (userSelectedPhase || publishCompleted);

      // Only restore if:
      // 1. A phase was saved (restoredPhase exists)
      // 2. User had manually selected a phase OR publish was completed (indicates they were actively working)
      // 3. The phase is different from current (to avoid unnecessary updates)
      if (shouldRestore) {
        const targetPhase = phases.find(p => p.id === restoredPhase);
        if (targetPhase && !targetPhase.disabled) {
          console.log('[BlogWriter] Restoring phase from navigation state:', restoredPhase);
          setCurrentPhase(restoredPhase);
          // Reset user selection so auto-progression can correct stale phases
          if (resetUserSelection) {
            resetUserSelection();
          }
        } else {
          console.log('[BlogWriter] Restored phase is disabled or not found, keeping current phase:', {
            restoredPhase,
            currentPhase,
            targetPhaseExists: !!targetPhase,
            targetPhaseDisabled: targetPhase?.disabled
          });
        }
      }
    } catch (error) {
      console.error('[BlogWriter] Failed to restore phase from navigation state:', error);
    }
  }, [phases, currentPhase, setCurrentPhase]);
};

