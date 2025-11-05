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
  // Phase Navigation: Default interface for blog writing workflow
  // - Phase buttons are always clickable and functional (for both CopilotKit and manual flows)
  // - Action buttons (▶) only appear when CopilotKit is unavailable (manual fallback)
  // - When CopilotKit is available, users can use either phase buttons or CopilotKit suggestions
  
  // Determine which action to show for each phase when CopilotKit is unavailable
  const getActionForPhase = (phaseId: string): { label: string; handler: (() => void) | null } => {
    // Show action buttons for both CopilotKit and manual flows (dual mode)
    // Users can use either CopilotKit suggestions or phase navigation buttons
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
    <>
      <style>{`
        /* Enterprise Phase Navigation Styles */
        .phase-nav-container {
          display: flex;
          gap: 10px;
          alignItems: center;
          padding: 12px 0;
          flexWrap: wrap;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 250, 251, 0.98) 100%);
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        .phase-chip {
          position: relative;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 18px;
          border-radius: 24px;
          border: none;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          letter-spacing: 0.01em;
        }
        
        .phase-chip::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
          transition: left 0.5s ease;
        }
        
        .phase-chip:hover::before {
          left: 100%;
        }
        
        /* Current Phase - Active Gradient */
        .phase-chip.current {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
          transform: translateY(-2px) scale(1.02);
        }
        
        .phase-chip.current:hover {
          transform: translateY(-3px) scale(1.03);
          box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.2) inset;
        }
        
        .phase-chip.current:active {
          transform: translateY(-1px) scale(1.01);
          box-shadow: 0 3px 12px rgba(102, 126, 234, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
        }
        
        /* Completed Phase - Success Gradient */
        .phase-chip.completed {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          box-shadow: 0 3px 12px rgba(16, 185, 129, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        }
        
        .phase-chip.completed:hover {
          transform: translateY(-2px) scale(1.02);
          box-shadow: 0 5px 16px rgba(16, 185, 129, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
        }
        
        /* Pending Phase - Subtle Gradient */
        .phase-chip.pending {
          background: linear-gradient(135deg, #e0e7ff 0%, #dbeafe 100%);
          color: #4b5563;
          border: 1px solid rgba(99, 102, 241, 0.2);
          box-shadow: 0 2px 6px rgba(99, 102, 241, 0.1);
        }
        
        .phase-chip.pending:hover {
          background: linear-gradient(135deg, #c7d2fe 0%, #bfdbfe 100%);
          transform: translateY(-2px) scale(1.02);
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
          border-color: rgba(99, 102, 241, 0.3);
        }
        
        /* Disabled Phase */
        .phase-chip.disabled {
          background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
          color: #9ca3af;
          cursor: not-allowed;
          opacity: 0.6;
          box-shadow: none;
          border: 1px solid #e5e7eb;
        }
        
        .phase-chip.disabled:hover {
          transform: none;
          box-shadow: none;
        }
        
        /* Phase Icon */
        .phase-icon {
          font-size: 18px;
          filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
          transition: transform 0.3s ease;
        }
        
        .phase-chip.current .phase-icon,
        .phase-chip.completed .phase-icon {
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
        }
        
        .phase-chip:hover:not(.disabled) .phase-icon {
          transform: scale(1.1) rotate(5deg);
        }
        
        /* Checkmark for completed */
        .phase-checkmark {
          font-size: 14px;
          margin-left: 4px;
          animation: checkmarkPop 0.3s ease;
        }
        
        @keyframes checkmarkPop {
          0% { transform: scale(0); }
          50% { transform: scale(1.2); }
          100% { transform: scale(1); }
        }
        
        /* Action Button - Enterprise Style */
        .phase-action-btn {
          position: relative;
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          border-radius: 20px;
          border: none;
          font-size: 13px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          overflow: hidden;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35), 
                      0 0 0 1px rgba(255, 255, 255, 0.1) inset,
                      0 1px 2px rgba(0, 0, 0, 0.1) inset;
        }
        
        .phase-action-btn::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
          transition: left 0.5s ease;
        }
        
        .phase-action-btn:hover::before {
          left: 100%;
        }
        
        .phase-action-btn:hover {
          transform: translateY(-2px) scale(1.05);
          box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5), 
                      0 0 0 1px rgba(255, 255, 255, 0.2) inset,
                      0 2px 4px rgba(0, 0, 0, 0.15) inset;
        }
        
        .phase-action-btn:active {
          transform: translateY(0) scale(1.02);
          box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4), 
                      0 0 0 1px rgba(255, 255, 255, 0.15) inset;
        }
        
        .phase-action-btn:focus-visible {
          outline: none;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3), 
                      0 4px 12px rgba(102, 126, 234, 0.35),
                      0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        }
        
        .phase-action-icon {
          font-size: 12px;
          transition: transform 0.3s ease;
        }
        
        .phase-action-btn:hover .phase-action-icon {
          transform: translateX(2px);
        }
      `}</style>
      
      <div className="phase-nav-container">
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
          // DUAL MODE: Show action buttons even when CopilotKit is available (users can use either method)
          const showAction = action.handler && (
            isCurrent || 
            (!isCompleted && !isDisabled) ||
            isResearchPhase ||
            isOutlinePhase ||
            isSEOPhase // Show SEO actions when handler exists - handler existence means prerequisites are met, so ignore isDisabled
          );
          
          // Determine chip class
          const chipClass = [
            'phase-chip',
            isCurrent ? 'current' : '',
            isCompleted && !isCurrent ? 'completed' : '',
            !isCurrent && !isCompleted && !isDisabled ? 'pending' : '',
            isDisabled ? 'disabled' : ''
          ].filter(Boolean).join(' ');
          
          return (
            <div key={phase.id} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                onClick={() => !isDisabled && onPhaseClick(phase.id)}
                disabled={isDisabled}
                className={chipClass}
                title={phase.disabled ? `Complete ${phase.name} first` : phase.description}
              >
                <span className="phase-icon">
                  {phase.icon}
                </span>
                <span>{phase.name}</span>
                {isCompleted && !isCurrent && (
                  <span className="phase-checkmark">
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
                  className="phase-action-btn"
                  title={`${action.label}`}
                >
                  <span className="phase-action-icon">▶</span>
                  <span>{action.label}</span>
                </button>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
};

export default PhaseNavigation;
