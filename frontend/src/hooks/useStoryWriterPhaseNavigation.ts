import { useEffect, useMemo, useCallback } from 'react';
import { usePhaseNavigationCore, usePhaseValidation } from './usePhaseNavigationCore';
import type { PhaseBase } from './usePhaseNavigationCore';

export interface StoryPhase extends PhaseBase {
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
  const core = usePhaseNavigationCore({
    phaseKey: 'storywriter_current_phase',
    userSelectedKey: 'storywriter_user_selected_phase',
    emptyPhaseId: 'setup',
  });

  // Determine phase states based on current data
  const phases = useMemo((): StoryPhase[] => {
    const setupCompleted = hasPremise;
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
        current: core.currentPhase === 'setup',
        disabled: false,
      },
      {
        id: 'outline',
        name: 'Outline',
        icon: '📝',
        description: 'Generate and refine story outline',
        completed: outlineCompleted,
        current: core.currentPhase === 'outline',
        disabled: !hasPremise,
      },
      {
        id: 'writing',
        name: 'Writing',
        icon: '✍️',
        description: 'Generate and edit your story',
        completed: writingCompleted,
        current: core.currentPhase === 'writing',
        disabled: !hasOutline,
      },
      {
        id: 'export',
        name: 'Export',
        icon: '📤',
        description: 'Export your completed story',
        completed: exportCompleted,
        current: core.currentPhase === 'export',
        disabled: !hasStoryContent,
      },
    ];
  }, [hasPremise, hasOutline, hasStoryContent, isComplete, core.currentPhase]);

  // Shared validation: redirect if current phase is disabled
  usePhaseValidation(
    phases,
    core.currentPhase,
    core.userSelectedPhase,
    core.setCurrentPhase,
    core.oscillationGuardRef,
    'setup',
  );

  // Migration: old 'premise' phase → 'outline' or 'setup'
  // Runs after usePhaseValidation so it overrides the redirect to 'setup'.
  useEffect(() => {
    if (core.currentPhase === 'premise') {
      core.setCurrentPhase(hasPremise ? 'outline' : 'setup');
    }
  }, [core.currentPhase, core.setCurrentPhase, hasPremise]);

  // Auto-update current phase based on completion status
  useEffect(() => {
    if (core.userSelectedPhase) {
      return;
    }

    if (!hasPremise && core.currentPhase !== 'setup') {
      core.setCurrentPhase('setup');
    } else if (hasPremise && !hasOutline && core.currentPhase !== 'outline') {
      core.setCurrentPhase('outline');
    } else if (hasOutline && !hasStoryContent && core.currentPhase !== 'writing') {
      core.setCurrentPhase('writing');
    } else if (hasStoryContent && !isComplete && core.currentPhase !== 'export') {
      core.setCurrentPhase('export');
    }
  }, [hasPremise, hasOutline, hasStoryContent, isComplete, core.currentPhase, core.userSelectedPhase]);

  const navigateToPhase = useCallback(
    (phaseId: string) => core.navigateToPhase(phaseId, phases),
    [core.navigateToPhase, phases],
  );

  return {
    phases,
    currentPhase: core.currentPhase,
    navigateToPhase,
    setCurrentPhase: core.setCurrentPhase,
    resetUserSelection: core.resetUserSelection,
  };
};

export default useStoryWriterPhaseNavigation;
