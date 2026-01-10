import React from 'react';
import {
  useBlogWriterResearchPolling,
  useOutlinePolling,
  useMediumGenerationPolling,
  useRewritePolling,
} from '../../../hooks/usePolling';
import { blogWriterCache } from '../../../services/blogWriterCache';

interface UseBlogWriterPollingProps {
  onResearchComplete: (research: any) => void;
  onOutlineComplete: (outline: any) => void;
  onOutlineError: (error: any) => void;
  onSectionsUpdate: (sections: Record<string, string>) => void;
  onContentConfirmed?: () => void; // Callback when content generation completes
  navigateToPhase?: (phase: string) => void; // Phase navigation function
}

export const useBlogWriterPolling = ({
  onResearchComplete,
  onOutlineComplete,
  onOutlineError,
  onSectionsUpdate,
  onContentConfirmed,
  navigateToPhase,
}: UseBlogWriterPollingProps) => {
  // Research polling hook (for context awareness) - uses blog writer endpoint
  const researchPolling = useBlogWriterResearchPolling({
    onComplete: onResearchComplete,
    onError: (error) => console.error('Research polling error:', error)
  });

  // Outline polling hook
  const outlinePolling = useOutlinePolling({
    onComplete: onOutlineComplete,
    onError: onOutlineError
  });

  // Medium generation polling (used after confirm if short blog)
  const mediumPolling = useMediumGenerationPolling({
    onComplete: (result: any) => {
      try {
        if (result && result.sections) {
          const newSections: Record<string, string> = {};
          result.sections.forEach((s: any) => {
            newSections[String(s.id)] = s.content || '';
          });
          onSectionsUpdate(newSections);
          
          // Cache the generated content (shared utility)
          if (Object.keys(newSections).length > 0) {
            const sectionIds = Object.keys(newSections);
            blogWriterCache.cacheContent(newSections, sectionIds);
            
            // Auto-confirm content and navigate to SEO phase when content generation completes
            // This happens when user clicks "Next:Confirm and generate content"
            if (onContentConfirmed) {
              onContentConfirmed();
            }
            if (navigateToPhase) {
              navigateToPhase('seo');
            }
          }
        }
      } catch (e) {
        console.error('Failed to apply medium generation result:', e);
      }
    },
    onError: (err) => console.error('Medium generation failed:', err)
  });

  // Rewrite polling hook (used for blog rewrite operations)
  const rewritePolling = useRewritePolling({
    onComplete: (result: any) => {
      try {
        if (result && result.sections) {
          const newSections: Record<string, string> = {};
          result.sections.forEach((s: any) => {
            newSections[String(s.id)] = s.content || '';
          });
          onSectionsUpdate(newSections);
        }
      } catch (e) {
        console.error('Failed to apply rewrite result:', e);
      }
    },
    onError: (err) => console.error('Rewrite failed:', err)
  });

  // Memoize polling state objects to prevent unnecessary recalculations
  const researchPollingState = React.useMemo(
    () => ({ isPolling: researchPolling.isPolling, currentStatus: researchPolling.currentStatus }),
    [researchPolling.isPolling, researchPolling.currentStatus]
  );
  const outlinePollingState = React.useMemo(
    () => ({ isPolling: outlinePolling.isPolling, currentStatus: outlinePolling.currentStatus }),
    [outlinePolling.isPolling, outlinePolling.currentStatus]
  );
  const mediumPollingState = React.useMemo(
    () => ({ isPolling: mediumPolling.isPolling, currentStatus: mediumPolling.currentStatus }),
    [mediumPolling.isPolling, mediumPolling.currentStatus]
  );

  return {
    researchPolling,
    outlinePolling,
    mediumPolling,
    rewritePolling,
    researchPollingState,
    outlinePollingState,
    mediumPollingState,
  };
};

