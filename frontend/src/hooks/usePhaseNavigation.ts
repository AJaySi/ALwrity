import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { BlogResearchResponse, BlogOutlineSection } from '../services/blogWriterApi';

export interface Phase {
  id: string;
  name: string;
  icon: string;
  description: string;
  completed: boolean;
  current: boolean;
  disabled: boolean;
}

export const usePhaseNavigation = (
  research: BlogResearchResponse | null,
  outline: BlogOutlineSection[],
  outlineConfirmed: boolean,
  hasContent: boolean,
  contentConfirmed: boolean,
  seoAnalysis: any,
  seoMetadata: any,
  seoRecommendationsApplied?: boolean
) => {
  // Initialize from localStorage if available
  // If no research exists, default to empty string to show landing page
  // Only default to 'research' if research already exists (resuming a session)
  const getInitialPhase = (): string => {
    try {
      if (typeof window !== 'undefined') {
        const stored = window.localStorage.getItem('blogwriter_current_phase');
        if (stored) {
          // If stored phase is 'research' but no research exists, show landing page instead
          if (stored === 'research' && !research) {
            return ''; // Return empty to show landing page
          }
          // For other phases, use stored value (user might be in middle of outline/content/seo/publish)
          // Even if research doesn't exist, allow other phases to be restored (edge case)
          return stored;
        }
      }
    } catch {}
    // Default to empty string to show landing page when no research exists
    // Will be set to 'research' when user clicks "Start Research"
    return research ? 'research' : '';
  };

  const [currentPhase, setCurrentPhase] = useState<string>(getInitialPhase());
  const [userSelectedPhase, setUserSelectedPhase] = useState<boolean>(() => {
    try {
      if (typeof window !== 'undefined') {
        const stored = window.localStorage.getItem('blogwriter_user_selected_phase');
        return stored === 'true';
      }
    } catch {}
    return false;
  });
  const lastClickAtRef = useRef<number>(0);

  // Determine phase states based on current data
  const phases = useMemo((): Phase[] => {
    const researchCompleted = !!research;
    const outlineCompleted = outline.length > 0;
    const contentCompleted = hasContent && contentConfirmed;
    // SEO is complete when analysis exists AND recommendations are applied
    const seoCompleted = !!seoAnalysis && (seoRecommendationsApplied === true || !!seoMetadata);

    return [
      {
        id: 'research',
        name: 'Research',
        icon: '🔍',
        description: 'Research your topic and gather data',
        completed: researchCompleted,
        current: currentPhase === 'research',
        disabled: false // Research is always accessible
      },
      {
        id: 'outline',
        name: 'Outline',
        icon: '📝',
        description: 'Create and refine your blog outline',
        completed: outlineCompleted,
        current: currentPhase === 'outline',
        disabled: !researchCompleted // Disabled only if research not completed (can always go back if completed)
      },
      {
        id: 'content',
        name: 'Content',
        icon: '✍️',
        description: 'Generate and edit your blog content',
        completed: contentCompleted,
        current: currentPhase === 'content',
        disabled: !outlineCompleted // Disabled only if outline not completed (can always go back if completed)
      },
      {
        id: 'seo',
        name: 'SEO',
        icon: '📈',
        description: 'Optimize for search engines',
        completed: seoCompleted,
        current: currentPhase === 'seo',
        disabled: !contentCompleted // Disabled only if content not completed (can always go back if completed)
      },
      {
        id: 'publish',
        name: 'Publish',
        icon: '🚀',
        description: 'Publish your blog post',
        completed: false, // This would be set when actually published
        current: currentPhase === 'publish',
        disabled: !seoCompleted // Can access if SEO done
      }
    ];
  }, [research, outline, hasContent, contentConfirmed, seoAnalysis, seoMetadata, seoRecommendationsApplied, currentPhase]);

  // Persist current phase and user selection
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('blogwriter_current_phase', currentPhase);
        window.localStorage.setItem('blogwriter_user_selected_phase', String(userSelectedPhase));
      }
    } catch {}
  }, [currentPhase, userSelectedPhase]);

  // Validate stored phase against current availability (quiet)
  useEffect(() => {
    // Allow empty string as a valid phase (landing page state)
    if (currentPhase === '') {
      return; // Don't validate empty phase - it's intentional for landing page
    }
    
    const current = phases.find(p => p.id === currentPhase);
    if (!current) {
      // If phase not found and no research exists, go to landing (empty string)
      // Otherwise, default to research
      setCurrentPhase(research ? 'research' : '');
      return;
    }
    if (current.disabled) {
      // Find the first non-disabled phase in order of progression the user qualifies for
      // If no research exists, default to landing (empty string) instead of research
      const fallback = phases.find(p => !p.disabled) || ({ id: research ? 'research' : '' } as Phase);
      if (fallback.id !== currentPhase) {
        setCurrentPhase(fallback.id);
      }
    }
  }, [phases, currentPhase, research]);

  // Auto-update current phase based on completion status (only if user hasn't manually selected a phase)
  useEffect(() => {
    if (userSelectedPhase) {
      return; // Don't auto-update if user has manually selected a phase
    }
    
    // If no research exists and phase is empty/landing, stay on landing
    if (!research && currentPhase === '') {
      return; // Keep showing landing page
    }

    // Auto-progress to the next available phase when conditions are met
    if (research && outline.length === 0) {
      // Research completed, but no outline yet - stay on research
      if (currentPhase !== 'research') {
        setCurrentPhase('research');
      }
    } else if (research && outline.length > 0 && !outlineConfirmed) {
      // Outline created but not confirmed - move to outline phase
      if (currentPhase !== 'outline') {
        setCurrentPhase('outline');
      }
    } else if (outlineConfirmed && hasContent && !contentConfirmed) {
      // Content generated but not confirmed - move to content phase
      if (currentPhase !== 'content') {
        setCurrentPhase('content');
      }
    } else if (contentConfirmed && !seoAnalysis) {
      // Content confirmed but no SEO analysis yet - move to SEO phase
      if (currentPhase !== 'seo') {
        setCurrentPhase('seo');
      }
    } else if (seoAnalysis && !seoRecommendationsApplied && !seoMetadata) {
      // SEO analysis done but recommendations not applied - stay on SEO phase
      if (currentPhase !== 'seo') {
        setCurrentPhase('seo');
      }
    } else if (seoAnalysis && (seoRecommendationsApplied || seoMetadata)) {
      // SEO recommendations applied or metadata generated
      if (currentPhase === 'seo') {
        // CRITICAL: Stay in SEO phase so user can review updated content - don't auto-progress
        // User will manually navigate to publish when ready
        // This prevents blank screen by keeping user in SEO phase where BlogEditor is visible
        // No action needed - already in SEO phase, stay here
      } else {
        // User is NOT in SEO phase - can progress to publish
        // This handles cases where user navigates away and comes back
        // Only auto-progress if user is already in a different phase (not actively in SEO)
      if (currentPhase !== 'publish') {
        setCurrentPhase('publish');
        }
      }
    }
  }, [research, outline, outlineConfirmed, hasContent, contentConfirmed, seoAnalysis, seoMetadata, seoRecommendationsApplied, currentPhase, userSelectedPhase]);

  const navigateToPhase = useCallback((phaseId: string) => {
    // Minimal debounce (200ms) to avoid race conditions on rapid clicks
    const now = Date.now();
    if (now - lastClickAtRef.current < 200) { return; }
    lastClickAtRef.current = now;

    const phase = phases.find(p => p.id === phaseId);

    if (phase && !phase.disabled) {
      setCurrentPhase(phaseId);
      setUserSelectedPhase(true); // Mark that user has manually selected a phase
    } else {
      // Quietly ignore blocked navigation
    }
  }, [phases]);

  // Reset user selection when a new phase is completed (to allow auto-progression)
  const resetUserSelection = () => {
    setUserSelectedPhase(false);
  };

  return {
    phases,
    currentPhase,
    navigateToPhase,
    setCurrentPhase,
    resetUserSelection
  };
};

export default usePhaseNavigation;
