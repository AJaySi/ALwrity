import React from 'react';

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
  onResearchAction?: () => void;      // Show research form
  onOutlineAction?: () => void;       // Generate outline
  onContentAction?: () => void;       // Confirm outline + generate content
  onSEOAction?: () => void;           // Run SEO analysis
  onApplySEORecommendations?: () => void;  // Apply SEO recommendations
  onPublishAction?: () => void;       // Generate SEO metadata or publish
}

interface PhaseNavigationProps {
  phases: Phase[];
  onPhaseClick: (phaseId: string) => void;
  currentPhase: string;
  copilotKitAvailable?: boolean;
  actionHandlers?: PhaseActionHandlers;
  // State for determining which actions to show
  hasResearch?: boolean;
  hasOutline?: boolean;
  outlineConfirmed?: boolean;
  hasContent?: boolean;
  contentConfirmed?: boolean;
  hasSEOAnalysis?: boolean;
  seoRecommendationsApplied?: boolean;
  hasSEOMetadata?: boolean;
}

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
  // Determine which action to show for each phase when CopilotKit is unavailable
  const getActionForPhase = (phaseId: string): { label: string; handler: (() => void) | null } => {
    if (copilotKitAvailable || !actionHandlers) {
      return { label: '', handler: null };
    }

    switch (phaseId) {
      case 'research':
        if (!hasResearch) {
          return { label: 'Start Research', handler: actionHandlers.onResearchAction || null };
        }
        break;
      case 'outline':
        // Show "Create Outline" if research exists and outline is not yet confirmed
        // This ensures users can create/regenerate outline after research, even if cached one exists
        // Once outline is confirmed, we hide the button to avoid confusion during content generation
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
        // Priority order matching CopilotKit suggestions:
        // 1. No SEO analysis yet - Run SEO Analysis
        // Note: We check hasContent (sections exist) - contentConfirmed is checked but not strictly required
        // This allows users to run SEO analysis even if contentConfirmed hasn't been explicitly set
        if (hasContent && !hasSEOAnalysis) {
          return { label: 'Run SEO Analysis', handler: actionHandlers.onSEOAction || null };
        }
        // 2. SEO analysis exists but recommendations not applied - Apply SEO Recommendations
        if (hasSEOAnalysis && !seoRecommendationsApplied) {
          return { label: 'Apply SEO Recommendations', handler: actionHandlers.onApplySEORecommendations || null };
        }
        // 3. SEO analysis exists and recommendations applied but no metadata - Generate SEO Metadata
        if (hasSEOAnalysis && seoRecommendationsApplied && !hasSEOMetadata) {
          return { label: 'Generate SEO Metadata', handler: actionHandlers.onPublishAction || null };
        }
        break;
      case 'publish':
        // Only show if SEO metadata exists (ready to publish)
        if (hasSEOAnalysis && seoRecommendationsApplied && hasSEOMetadata) {
          return { label: 'Ready to Publish', handler: null }; // Publish handled separately
        }
        break;
    }
    return { label: '', handler: null };
  };

  return (
    <div style={{
      display: 'flex',
      gap: '8px',
      alignItems: 'center',
      padding: '8px 0',
      flexWrap: 'wrap'
    }}>
      {phases.map((phase) => {
        const isCurrent = phase.current;
        const isCompleted = phase.completed;
        const isDisabled = phase.disabled;
        const action = getActionForPhase(phase.id);
        
        // Show action button when:
        // 1. CopilotKit is unavailable
        // 2. Action handler exists
        // 3. Phase is not disabled
        // 4. Show for current phase OR next actionable phase (not completed) OR phases with available actions
        //    For research phase: always show if no research exists
        //    For outline phase: always show if research exists but no outline (like research phase)
        //    For SEO phase: always show if action handler exists (prerequisites are met)
        const isResearchPhase = phase.id === 'research' && !hasResearch;
        // Outline phase: show action whenever research exists and action handler is available
        // This allows users to create/regenerate outline after research, even if cached one exists
        const isOutlinePhase = phase.id === 'outline' && hasResearch && action.handler;
        // SEO phase: show action whenever prerequisites are met (action handler exists)
        // Similar to research/outline, show SEO actions whenever handler exists and phase is enabled
        const isSEOPhase = phase.id === 'seo' && action.handler;
        
        // Debug logging for SEO phase (temporary - for troubleshooting)
        if (phase.id === 'seo' && !copilotKitAvailable && process.env.NODE_ENV === 'development') {
          console.log('[PhaseNavigation] SEO phase debug:', {
            phaseId: phase.id,
            isCurrent,
            isCompleted,
            isDisabled,
            hasContent,
            contentConfirmed,
            hasSEOAnalysis,
            seoRecommendationsApplied,
            hasSEOMetadata,
            actionLabel: action.label,
            actionHandler: !!action.handler,
            copilotKitAvailable,
            isSEOPhase,
            showActionWillBe: !copilotKitAvailable && action.handler && !isDisabled && (
              isCurrent || 
              (!isCompleted && !isDisabled) ||
              isResearchPhase ||
              isOutlinePhase ||
              isSEOPhase
            )
          });
        }
        
        // Show action if: current phase, or phase is not completed and not disabled, or it's research/outline/SEO with available action
        // For SEO: show whenever action handler exists (prerequisites are met), even if phase is marked as disabled/completed
        // This is critical because SEO prerequisites (hasContent && contentConfirmed) are validated in getActionForPhase,
        // so if action.handler exists, we should show it regardless of phase navigation's disabled state
        const showAction = !copilotKitAvailable && action.handler && (
          isCurrent || 
          (!isCompleted && !isDisabled) ||
          isResearchPhase ||
          isOutlinePhase ||
          isSEOPhase // Show SEO actions when handler exists - handler existence means prerequisites are met, so ignore isDisabled
        );
        
        return (
          <div key={phase.id} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <button
              onClick={() => !isDisabled && onPhaseClick(phase.id)}
              disabled={isDisabled}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 12px',
                borderRadius: '20px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '500',
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                backgroundColor: isCurrent 
                  ? '#1976d2' 
                  : isCompleted 
                    ? '#4caf50' 
                    : isDisabled 
                      ? '#f5f5f5' 
                      : '#e3f2fd',
                color: isCurrent 
                  ? 'white' 
                  : isCompleted 
                    ? 'white' 
                    : isDisabled 
                      ? '#999' 
                      : '#1976d2',
                opacity: isDisabled ? 0.6 : 1,
                boxShadow: isCurrent ? '0 2px 4px rgba(25, 118, 210, 0.3)' : 'none',
                transform: isCurrent ? 'translateY(-1px)' : 'none'
              }}
              title={phase.disabled ? `Complete ${phase.name} first` : phase.description}
            >
              <span style={{ fontSize: '16px' }}>
                {phase.icon}
              </span>
              <span>{phase.name}</span>
              {isCompleted && !isCurrent && (
                <span style={{ fontSize: '12px', marginLeft: '4px' }}>
                  ✓
                </span>
              )}
            </button>
            
            {showAction && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  action.handler?.();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 12px',
                  borderRadius: '16px',
                  border: '1px solid #1976d2',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  backgroundColor: '#1976d2',
                  color: 'white',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 2px 4px rgba(25, 118, 210, 0.2)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#1565c0';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#1976d2';
                  e.currentTarget.style.transform = 'none';
                }}
                title={`${action.label} (Chat unavailable - click to proceed)`}
              >
                <span style={{ fontSize: '12px' }}>▶</span>
                <span>{action.label}</span>
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default PhaseNavigation;
