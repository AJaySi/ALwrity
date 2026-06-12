import React from 'react';
import {
  useBlogWriterResearchPolling,
  useOutlinePolling,
  useMediumGenerationPolling,
  useRewritePolling,
} from '../../../hooks/usePolling';
import { blogWriterCache } from '../../../services/blogWriterCache';
import { debug } from '../../../utils/debug';

interface UseBlogWriterPollingProps {
  onResearchComplete: (research: any) => void;
  onOutlineComplete: (outline: any) => void;
  onOutlineError: (error: any) => void;
  onSectionsUpdate: (sections: Record<string, string>) => void;
  onContentConfirmed?: () => void; // Callback when content generation completes
  onContentError?: () => void; // Callback when content generation fails
  navigateToPhase?: (phase: string) => void; // Phase navigation function
  skipContentAutoConfirmRef?: React.MutableRefObject<boolean>; // When true, skip auto-confirm & navigation after content generation
}

export const useBlogWriterPolling = ({
  onResearchComplete,
  onOutlineComplete,
  onOutlineError,
  onSectionsUpdate,
  onContentConfirmed,
  onContentError,
  navigateToPhase,
  skipContentAutoConfirmRef,
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
          
          // Skip auto-navigation when Re-Content was used
          // (user already had content and chose to regenerate — stay on content phase to review)
          const skipAutoConfirm = skipContentAutoConfirmRef?.current === true;
          if (skipContentAutoConfirmRef) skipContentAutoConfirmRef.current = false; // reset flag

          // Always confirm content so the check mark shows on the chip
          if (onContentConfirmed) {
            onContentConfirmed();
          }

          if (skipAutoConfirm) {
            debug.log('[BlogWriter] Re-Content: content confirmed, user stays on content phase to review');
          } else {
            // Auto-navigate to SEO phase when content generation completes (first time)
            if (navigateToPhase) {
              navigateToPhase('seo');
            }
          }
        }
      } catch (e) {
        console.error('Failed to apply medium generation result:', e);
      }
    },
    onError: (err: any) => {
      console.error('Medium generation failed:', err);
      onContentError?.();
      const errMsg = (typeof err === 'string' ? err : (err?.message || err?.error || '')).toLowerCase();
      if (errMsg.includes('insufficient_balance') || errMsg.includes('balance_not_enough') || (errMsg.includes('403') && errMsg.includes('balance'))) {
        setTimeout(() => alert('Your API balance is insufficient. Please top up your account or switch to a different provider.'), 100);
      } else if (errMsg.includes('no valid structured response') || errMsg.includes('parse') || errMsg.includes('json')) {
        setTimeout(() => alert('Content generation failed because the AI provider returned an unparseable response. This is usually a temporary issue — please try again.'), 100);
      }
    }
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

