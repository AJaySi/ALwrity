import { useState, useEffect, useCallback, useRef } from 'react';
import { readLSString, readLSBool } from '../utils/persistence';

export interface PhaseBase {
  id: string;
  disabled: boolean;
}

export interface PhaseNavigationConfig {
  /** localStorage key for the current phase */
  phaseKey: string;
  /** localStorage key for the user-selected flag */
  userSelectedKey: string;
  /**
   * Default phase shown when no progress exists.
   * BlogWriter uses `''` (landing page), StoryWriter uses `'setup'`.
   */
  emptyPhaseId?: string;
  /**
   * Override the initial phase instead of reading from localStorage.
   * Used when the stored phase is stale (e.g., 'research' stored but no
   * research data exists yet on a different origin).
   */
  initialPhase?: string;
}

interface OscillationState {
  from: string;
  to: string;
  count: number;
  lastTime: number;
}

export interface UsePhaseNavigationCoreReturn {
  currentPhase: string;
  setCurrentPhase: (phase: string) => void;
  userSelectedPhase: boolean;
  navigateToPhase: (phaseId: string, phases: PhaseBase[]) => void;
  resetUserSelection: () => void;
  oscillationGuardRef: React.MutableRefObject<OscillationState>;
  lastClickAtRef: React.MutableRefObject<number>;
}

/**
 * Core phase navigation state management shared across BlogWriter,
 * StoryWriter, etc.
 *
 * Handles:
 * - Initializing phase + user-selected state from localStorage
 * - Persisting state back to localStorage on changes
 * - User-tracking flag (auto-progression vs. manual selection)
 * - Click debouncing (200ms)
 *
 * Does NOT handle:
 * - Phase definitions (phases array) — product-specific
 * - Phase validation effect — use usePhaseValidation() separately
 * - Auto-update / auto-progression effect — product-specific
 */
export const usePhaseNavigationCore = (
  config: PhaseNavigationConfig,
): UsePhaseNavigationCoreReturn => {
  const { phaseKey, userSelectedKey, emptyPhaseId = '' } = config;

  const [currentPhase, setCurrentPhase] = useState<string>(() => {
    if (config.initialPhase !== undefined) return config.initialPhase;
    try {
      if (typeof window === 'undefined') return emptyPhaseId;
      return readLSString(phaseKey, emptyPhaseId);
    } catch {
      return emptyPhaseId;
    }
  });

  const [userSelectedPhase, setUserSelectedPhase] = useState<boolean>(() => {
    try {
      if (typeof window !== 'undefined') {
        return readLSBool(userSelectedKey, false);
      }
    } catch { /* noop */ }
    return false;
  });

  const lastClickAtRef = useRef<number>(0);
  const oscillationGuardRef = useRef<OscillationState>({
    from: '', to: '', count: 0, lastTime: 0,
  });

  // Persist to localStorage on change
  useEffect(() => {
    try { localStorage.setItem(phaseKey, currentPhase); } catch { /* noop */ }
  }, [currentPhase, phaseKey]);

  useEffect(() => {
    try { localStorage.setItem(userSelectedKey, String(userSelectedPhase)); } catch { /* noop */ }
  }, [userSelectedPhase, userSelectedKey]);

  const navigateToPhase = useCallback((phaseId: string, phases: PhaseBase[]) => {
    const now = Date.now();
    if (now - lastClickAtRef.current < 200) return;
    lastClickAtRef.current = now;

    const phase = phases.find(p => p.id === phaseId);
    if (phase && !phase.disabled) {
      setCurrentPhase(phaseId);
      setUserSelectedPhase(true);
    }
  }, []);

  const resetUserSelection = useCallback(() => {
    setUserSelectedPhase(false);
  }, []);

  return {
    currentPhase,
    setCurrentPhase,
    userSelectedPhase,
    navigateToPhase,
    resetUserSelection,
    oscillationGuardRef,
    lastClickAtRef,
  };
};

/**
 * Shared phase validation effect.
 *
 * Checks that the current phase is still valid (not disabled) given the
 * latest data. If the phase is disabled, redirects to the first
 * non-disabled phase with oscillation detection to prevent bouncing.
 */
export function usePhaseValidation(
  phases: PhaseBase[],
  currentPhase: string,
  userSelectedPhase: boolean,
  setCurrentPhase: (phase: string) => void,
  oscillationGuardRef: React.MutableRefObject<OscillationState>,
  emptyPhaseId: string,
  research?: any,
): void {
  useEffect(() => {
    if (currentPhase === emptyPhaseId) return;
    if (userSelectedPhase) return;

    const current = phases.find(p => p.id === currentPhase);
    if (!current) {
      setCurrentPhase(research ? 'research' : emptyPhaseId);
      return;
    }
    if (current.disabled) {
      const guard = oscillationGuardRef.current;
      const now = Date.now();

      // Oscillation guard: detect rapid bouncing between two phases
      if (guard.from === currentPhase && guard.count >= 3 && (now - guard.lastTime) < 1000) {
        return;
      }
      if (guard.to !== currentPhase) {
        oscillationGuardRef.current = { from: currentPhase, to: '', count: 1, lastTime: now };
      }

      const fallback = phases.find(p => !p.disabled);
      if (fallback && fallback.id !== currentPhase) {
        oscillationGuardRef.current = {
          ...oscillationGuardRef.current,
          to: fallback.id,
          count: guard.from === currentPhase ? guard.count + 1 : 1,
          lastTime: now,
        };
        setCurrentPhase(fallback.id);
      }
    }
  }, [
    phases,
    currentPhase,
    userSelectedPhase,
    setCurrentPhase,
    emptyPhaseId,
    research,
  ]);
}

export default usePhaseNavigationCore;
