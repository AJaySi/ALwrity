import React from 'react';
import Box from '@mui/material/Box';
import Tooltip from '@mui/material/Tooltip';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';

export interface Phase {
  id: string;
  name: string;
  icon: string;
  description: string;
  completed: boolean;
  current: boolean;
  disabled: boolean;
}

export interface PhaseActionHandlers {
  onResearchAction?: () => void;
  onOutlineAction?: () => void;
  onContentAction?: () => void;
  onSEOAction?: () => void;
  onApplySEORecommendations?: () => void;
  onPublishAction?: () => void;
}

interface PhaseNavigationProps {
  phases: Phase[];
  onPhaseClick: (phaseId: string) => void;
  currentPhase: string;
  copilotKitAvailable?: boolean;
  actionHandlers?: PhaseActionHandlers;
  hasResearch?: boolean;
  hasOutline?: boolean;
  outlineConfirmed?: boolean;
  hasContent?: boolean;
  contentConfirmed?: boolean;
  hasSEOAnalysis?: boolean;
  seoRecommendationsApplied?: boolean;
  hasSEOMetadata?: boolean;
}

const PHASE_TOOLTIPS: Record<string, string> = {
  research: 'Research your topic and gather data from the web to create a well-informed blog post.',
  outline: 'Create and refine your blog outline with AI-generated structure and key talking points.',
  content: 'Generate, edit, and perfect your blog content using the WYSIWYG editor and AI assistance.',
  seo: 'Optimize your blog for search engines with AI-powered SEO analysis, recommendations, and metadata.',
  publish: 'Publish your blog to WordPress, Wix, or export as HTML or Markdown.',
};

const PHASE_ACTIONS: Record<string, string> = {
  research: 'Enter keywords to research your topic',
  outline: 'Create your blog outline to structure your content',
  content: 'Generate and refine your blog content',
  seo: 'Optimize your blog for search engines',
  publish: 'Publish or export your finished blog',
};

export const PhaseNavigation: React.FC<PhaseNavigationProps> = ({
  phases,
  onPhaseClick,
  currentPhase,
  copilotKitAvailable = true,
  actionHandlers,
  hasResearch = false,
  hasOutline = false,
  outlineConfirmed = false,
  hasContent = false,
  contentConfirmed = false,
  hasSEOAnalysis = false,
  seoRecommendationsApplied = false,
  hasSEOMetadata = false,
}) => {
  const totalPhases = phases.length;
  const completedCount = phases.filter(p => p.completed).length;
  const completionPct = totalPhases > 0 ? Math.round((completedCount / totalPhases) * 100) : 0;

  const getActionForPhase = (phaseId: string): { label: string; handler: (() => void) | null } => {
    if (!actionHandlers) {
      return { label: '', handler: null };
    }

    switch (phaseId) {
      case 'research':
        if (!hasResearch) {
          return { label: 'Start Research', handler: actionHandlers.onResearchAction || null };
        }
        break;
      case 'outline':
        if (hasResearch && !outlineConfirmed) {
          return { label: 'Create Outline', handler: actionHandlers.onOutlineAction || null };
        }
        break;
      case 'content':
        if (hasOutline && !outlineConfirmed) {
          return { label: 'Confirm & Generate Content', handler: actionHandlers.onContentAction || null };
        }
        break;
      case 'seo':
        if (hasContent && !hasSEOAnalysis) {
          return { label: 'Run SEO Analysis', handler: actionHandlers.onSEOAction || null };
        }
        if (hasSEOAnalysis && !seoRecommendationsApplied) {
          return { label: 'Apply SEO Recommendations', handler: actionHandlers.onApplySEORecommendations || null };
        }
        if (hasSEOAnalysis && seoRecommendationsApplied && !hasSEOMetadata) {
          return { label: 'Generate SEO Metadata', handler: actionHandlers.onPublishAction || null };
        }
        break;
      case 'publish':
        if (hasSEOAnalysis && seoRecommendationsApplied && hasSEOMetadata) {
          return { label: 'Ready to Publish', handler: null };
        }
        break;
    }
    return { label: '', handler: null };
  };

  const activePhase = phases.find(p => p.current);

  const infoText = (() => {
    if (!activePhase || !activePhase.id) {
      if (completedCount === 0) return '📍 Start with Research to begin';
      const next = phases.find(p => !p.completed && !p.disabled);
      return next ? `👉 Next: ${next.name}` : '✅ All phases complete!';
    }
    const next = phases.find(p => !p.completed && !p.disabled);
    if (activePhase.completed && !next) return '✅ All phases complete!';
    if (activePhase.completed) return `✅ ${activePhase.name} done — Next: ${next!.name}`;
    return `📍 ${activePhase.name}: ${PHASE_ACTIONS[activePhase.id] || 'Complete this phase'}`;
  })();

  return (
    <>
      <style>{`
        @keyframes phaseActivePulse {
          0%, 100% {
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35), 0 0 0 0 rgba(37, 99, 235, 0.25);
          }
          50% {
            box-shadow: 0 2px 16px rgba(37, 99, 235, 0.55), 0 0 0 4px rgba(37, 99, 235, 0.1);
          }
        }
      `}</style>

      <Box sx={{
        display: 'flex',
        gap: 0.75,
        alignItems: 'center',
        flexWrap: 'wrap',
      }}>
        {/* Dynamic phase info text */}
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          px: 1.25,
          py: 0.4,
          borderRadius: '20px',
          background: 'rgba(37, 99, 235, 0.06)',
          border: '1px solid rgba(37, 99, 235, 0.12)',
          fontSize: '0.75rem',
          color: '#475569',
          fontWeight: 500,
          whiteSpace: 'nowrap',
          maxWidth: { xs: '180px', sm: '300px', md: '400px' },
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          flexShrink: 0,
        }}>
          {infoText}
        </Box>

        {/* Phase chips */}
        {phases.map((phase) => {
          const isCurrent = phase.current;
          const isCompleted = phase.completed;
          const isDisabled = phase.disabled;
          const action = getActionForPhase(phase.id);

          const isResearchPhase = phase.id === 'research' && action.handler;
          const isOutlinePhase = phase.id === 'outline' && hasResearch && action.handler;
          const isSEOPhase = phase.id === 'seo' && action.handler;

          /* Phase state derivation:
             - Active: phase is current AND not yet completed (user needs to work on it)
             - Done: phase is completed (show green regardless of whether it's current)
             - Pending: not current, not completed, not disabled */
          const isActive = isCurrent && !isCompleted;
          const isDone = isCompleted;
          const isPending = !isCurrent && !isCompleted && !isDisabled;

          /* Chip click: use action handler when available (same as action button),
             fall back to navigation for viewing completed/disabled phases */
          const handleChipClick = () => {
            if (isDisabled) return;
            if (action.handler) {
              action.handler();
            } else {
              onPhaseClick(phase.id);
            }
          };

          /* Show action button only when phase is NOT completed.
             Research action: only on landing page (not current), to invite start.
             Other phase actions: show when current, pending, or next-actionable. */
          const showAction = action.handler && !isDone && (
            (!isCurrent && phase.id === 'research' && !hasResearch) ||
            (isCurrent && phase.id !== 'research') ||
            (!isCurrent && !isDisabled && phase.id !== 'research') ||
            (phase.id !== 'research' && (isResearchPhase || isOutlinePhase || isSEOPhase))
          );

          const iconOnly = isDone && !isCurrent;

          const chipSx = {
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            borderRadius: '20px',
            border: 'none',
            fontWeight: 600,
            cursor: isDisabled ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'clip',

            /* Disabled phase: muted */
            ...(isDisabled && {
              px: 1.25,
              py: 0.5,
              fontSize: '0.8125rem',
              background: '#f1f5f9',
              color: '#94a3b8',
              border: '1px solid #e2e8f0',
              opacity: 0.5,
            }),

            /* Done phase: green, collapsed to icon if not current */
            ...(isDone && !isDisabled && {
              px: iconOnly ? 0.5 : 1.5,
              py: 0.5,
              fontSize: '0.8125rem',
              justifyContent: iconOnly ? 'center' : 'flex-start',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#fff',
              boxShadow: '0 2px 6px rgba(16, 185, 129, 0.25)',
              maxWidth: iconOnly ? '36px' : 'none',
              opacity: iconOnly ? 0.85 : 1,
              '&:hover': {
                maxWidth: iconOnly ? '160px' : 'none',
                px: iconOnly ? 1.5 : 1.5,
                opacity: 1,
                transform: 'translateY(-1px)',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.35)',
              },
            }),

            /* Active phase (current but not done): larger, pulse glow */
            ...(isActive && !isDisabled && {
              px: 2,
              py: 0.75,
              fontSize: '0.875rem',
              background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
              color: '#fff',
              boxShadow: '0 2px 8px rgba(37, 99, 235, 0.35), inset 0 0 0 1px rgba(255,255,255,0.15)',
              animation: 'phaseActivePulse 2s ease-in-out infinite',
              '&:hover': {
                transform: 'translateY(-1px) scale(1.03)',
                boxShadow: '0 4px 16px rgba(37, 99, 235, 0.5), inset 0 0 0 1px rgba(255,255,255,0.2)',
              },
              '&:active': {
                transform: 'translateY(0) scale(1.01)',
              },
            }),

            /* Pending phase: compact, subtle */
            ...(isPending && {
              px: 1.25,
              py: 0.5,
              fontSize: '0.8125rem',
              background: 'rgba(37, 99, 235, 0.08)',
              color: '#475569',
              border: '1px solid rgba(37, 99, 235, 0.15)',
              '&:hover': {
                transform: 'translateY(-1px)',
                background: 'rgba(37, 99, 235, 0.12)',
                boxShadow: '0 3px 8px rgba(37, 99, 235, 0.15)',
              },
            }),
          };

          const actionBtnSx = {
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            px: 1.25,
            py: 0.4,
            borderRadius: '16px',
            border: 'none',
            fontSize: '0.75rem',
            fontWeight: 700,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
            color: '#fff',
            boxShadow: '0 2px 6px rgba(37, 99, 235, 0.3)',
            textTransform: 'uppercase',
            letterSpacing: '0.03em',
            whiteSpace: 'nowrap',
            '&:hover': {
              transform: 'translateY(-1px) scale(1.03)',
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.4)',
            },
            '&:active': {
              transform: 'translateY(0) scale(1.01)',
            },
          };

          const iconSx = {
            fontSize: '14px',
            lineHeight: 1,
            flexShrink: 0,
          };

          return (
            <Box key={phase.id} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Tooltip
                title={
                  <Box>
                    <Box sx={{ fontWeight: 700, mb: 0.5, fontSize: '0.875rem' }}>{phase.name}</Box>
                    <Box sx={{ fontSize: '0.75rem', opacity: 0.9 }}>
                      {isDisabled
                        ? `Complete the previous phase first to unlock ${phase.name}.`
                        : (PHASE_TOOLTIPS[phase.id] || phase.description)}
                    </Box>
                  </Box>
                }
                arrow
                placement="top"
                enterDelay={300}
                leaveDelay={100}
              >
                <Box
                  component="button"
                  onClick={handleChipClick}
                  sx={chipSx}
                >
                  <Box component="span" sx={iconSx}>{phase.icon}</Box>
                  <Box component="span" sx={{ flexShrink: 0 }}>{phase.name}</Box>
                  {isDone && (
                    <Box component="span" sx={{ fontSize: '12px', flexShrink: 0, ml: 0.25 }}>✓</Box>
                  )}
                </Box>
              </Tooltip>

              {showAction && (
                <Tooltip
                  title={`${action.label}`}
                  arrow
                  placement="top"
                >
                  <Box
                    component="button"
                    onClick={(e: React.MouseEvent) => {
                      e.stopPropagation();
                      action.handler?.();
                    }}
                    sx={actionBtnSx}
                  >
                    <Box component="span" sx={{ fontSize: '10px' }}>▶</Box>
                    <Box component="span">{action.label}</Box>
                  </Box>
                </Tooltip>
              )}
            </Box>
          );
        })}

        {/* Circular progress indicator */}
        {totalPhases > 0 && (
          <Tooltip
            title={`${completedCount} of ${totalPhases} phases complete (${completionPct}%)`}
            arrow
            placement="top"
          >
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              ml: 0.5,
              position: 'relative',
              cursor: 'pointer',
            }}>
              <CircularProgress
                variant="determinate"
                value={completionPct}
                size={26}
                thickness={3}
                sx={{
                  color: completionPct === 100 ? '#10b981' : '#2563eb',
                }}
              />
              <Typography
                variant="caption"
                sx={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  color: '#64748b',
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                }}
              >
                {completionPct}
              </Typography>
            </Box>
          </Tooltip>
        )}
      </Box>
    </>
  );
};

export default PhaseNavigation;
