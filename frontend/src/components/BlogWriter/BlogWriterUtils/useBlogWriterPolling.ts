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
          
          // Auto-confirm content and navigate to SEO phase when content generation completes
          // This happens when user clicks "Next:Confirm and generate content"
          if (onContentConfirmed) {
            onContentConfirmed();
          }
          if (navigateToPhase) {
            navigateToPhase('seo');
          }

          // Save to asset library (dedup by title is handled inside saveBlogToAssetLibrary)
          // Backend also saves via save_and_track_text_content; this is a safety net / metadata update
          (async () => {
            try {
              const { saveBlogToAssetLibrary } = await import('../../../services/blogWriterApi');
              const totalWords = result.sections.reduce(
                (sum: number, s: any) => sum + (s.wordCount || (s.content || '').split(/\s+/).length),
                0
              );
              await saveBlogToAssetLibrary({
                title: result.title || 'Untitled Blog',
                blogType: 'medium',
                wordCount: totalWords,
                sectionCount: result.sections?.length,
                model: result.model,
                generationTimeMs: result.generation_time_ms,
              });
            } catch (assetError) {
              console.error('[BlogWriter] Failed to save blog to asset library:', assetError);
            }
          })();
        }
      } catch (e) {
        console.error('Failed to apply medium generation result:', e);
      }
    },
    onError: (err: any) => {
      console.error('Medium generation failed:', err);
      const errMsg = (typeof err === 'string' ? err : (err?.message || err?.error || '')).toLowerCase();
      if (errMsg.includes('insufficient_balance') || errMsg.includes('balance_not_enough') || (errMsg.includes('403') && errMsg.includes('balance'))) {
        setTimeout(() => alert('Your API balance is insufficient. Please top up your account or switch to a different provider.'), 100);
      } else if (errMsg.includes('no valid structured response')) {
        setTimeout(() => alert('Content generation failed due to a provider error. This might be a temporary issue — please try again or switch providers.'), 100);
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

