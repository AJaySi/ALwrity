import { useState, useEffect, useMemo, useCallback, useRef } from 'react';

export interface StoryPhase {
  id: 'setup' | 'outline' | 'writing' | 'export';
  name: string;
  icon: string;
  description: string;
  completed: boolean;
  current: boolean;
  disabled: boolean;
}

interface UseStoryWriterPhaseNavigationParams {
  hasPremise: boolean;
  hasOutline: boolean;
  hasStoryContent: boolean;
  isComplete: boolean;
}

export const useStoryWriterPhaseNavigation = ({
  hasPremise,
  hasOutline,
  hasStoryContent,
  isComplete,
}: UseStoryWriterPhaseNavigationParams) => {
  // Initialize from localStorage if available
  const getInitialPhase = (): string => {
    try {
      if (typeof window !== 'undefined') {
        const stored = window.localStorage.getItem('storywriter_current_phase');
        if (stored) return stored;
      }
    } catch {}
    return 'setup';
  };

  const [currentPhase, setCurrentPhase] = useState<string>(getInitialPhase());
  const [userSelectedPhase, setUserSelectedPhase] = useState<boolean>(() => {
    try {
      if (typeof window !== 'undefined') {
        const stored = window.localStorage.getItem('storywriter_user_selected_phase');
        return stored === 'true';
      }
    } catch {}
    return false;
  });
  const lastClickAtRef = useRef<number>(0);

  // Determine phase states based on current data
  const phases = useMemo((): StoryPhase[] => {
    const setupCompleted = hasPremise; // Setup is complete when premise exists
    const outlineCompleted = hasOutline;
    const writingCompleted = hasStoryContent && isComplete;
    const exportCompleted = isComplete;

    return [
      {
        id: 'setup',
        name: 'Setup',
        icon: '⚙️',
        description: 'Configure your story parameters and premise',
        completed: setupCompleted,
        current: currentPhase === 'setup',
        disabled: false, // Always accessible
      },
      {
        id: 'outline',
        name: 'Outline',
        icon: '📝',
        description: 'Generate and refine story outline',
        completed: outlineCompleted,
        current: currentPhase === 'outline',
        disabled: !hasPremise, // Need premise first
      },
      {
        id: 'writing',
        name: 'Writing',
        icon: '✍️',
        description: 'Generate and edit your story',
        completed: writingCompleted,
        current: currentPhase === 'writing',
        disabled: !hasOutline, // Need outline first
      },
      {
        id: 'export',
        name: 'Export',
        icon: '📤',
        description: 'Export your completed story',
        completed: exportCompleted,
        current: currentPhase === 'export',
        disabled: !hasStoryContent, // Need story content first
      },
    ];
  }, [hasPremise, hasOutline, hasStoryContent, isComplete, currentPhase]);

  // Persist current phase and user selection
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('storywriter_current_phase', currentPhase);
        window.localStorage.setItem('storywriter_user_selected_phase', String(userSelectedPhase));
      }
    } catch {}
  }, [currentPhase, userSelectedPhase]);

  // Validate stored phase against current availability (quiet)
  // Also migrate old 'premise' phase to 'outline' if needed
  useEffect(() => {
    // Migrate old 'premise' phase to 'outline' if stored
    if (currentPhase === 'premise') {
      if (hasPremise) {
        setCurrentPhase('outline');
      } else {
        setCurrentPhase('setup');
      }
      return;
    }
    
    const current = phases.find((p) => p.id === currentPhase);
    if (!current) {
      setCurrentPhase('setup');
      return;
    }
    if (current.disabled) {
      // Find the first non-disabled phase in order of progression
      const fallback = phases.find((p) => !p.disabled) || ({ id: 'setup' } as StoryPhase);
      if (fallback.id !== currentPhase) {
        setCurrentPhase(fallback.id);
      }
    }
  }, [phases, currentPhase, hasPremise]);

  // Auto-update current phase based on completion status (only if user hasn't manually selected)
  useEffect(() => {
    if (userSelectedPhase) {
      return; // Don't auto-update if user has manually selected a phase
    }

    // Auto-progress to the next available phase when conditions are met
    if (!hasPremise && currentPhase !== 'setup') {
      setCurrentPhase('setup');
    } else if (hasPremise && !hasOutline && currentPhase !== 'outline') {
      setCurrentPhase('outline');
    } else if (hasOutline && !hasStoryContent && currentPhase !== 'writing') {
      setCurrentPhase('writing');
    } else if (hasStoryContent && !isComplete && currentPhase !== 'export') {
      setCurrentPhase('export');
    }
  }, [hasPremise, hasOutline, hasStoryContent, isComplete, currentPhase, userSelectedPhase]);

  const navigateToPhase = useCallback(
    (phaseId: string) => {
      // Minimal debounce (200ms) to avoid race conditions on rapid clicks
      const now = Date.now();
      if (now - lastClickAtRef.current < 200) {
        return;
      }
      lastClickAtRef.current = now;

      const phase = phases.find((p) => p.id === phaseId);

      if (phase && !phase.disabled) {
        setCurrentPhase(phaseId);
        setUserSelectedPhase(true); // Mark that user has manually selected a phase
      }
    },
    [phases]
  );

  // Reset user selection when a new phase is completed (to allow auto-progression)
  const resetUserSelection = useCallback(() => {
    setUserSelectedPhase(false);
  }, []);

  return {
    phases,
    currentPhase,
    navigateToPhase,
    setCurrentPhase,
    resetUserSelection,
  };
};

export default useStoryWriterPhaseNavigation;
