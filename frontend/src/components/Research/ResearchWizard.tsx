import React, { useEffect, useState, useRef } from 'react';
import { useResearchWizard } from './hooks/useResearchWizard';
import { useResearchExecution } from './hooks/useResearchExecution';
import { ResearchInput } from './steps/ResearchInput';
import { StepProgress } from './steps/StepProgress';
import { StepResults } from './steps/StepResults';
import { ResearchWizardProps } from './types/research.types';
import { addResearchHistory } from '../../utils/researchHistory';
import { getResearchConfig, ProviderAvailability } from '../../api/researchConfig';
import { AdvancedChip } from './steps/components/AdvancedChip';
import { SmartResearchInfo } from './steps/components/SmartResearchInfo';
import { intentResearchApi } from '../../api/intentResearchApi';
import { clearDraftFromStorage } from '../../utils/researchDraftManager';

export interface ResearchWizardHeaderActions {
  onOpenPersona?: () => void;
  onOpenCompetitors?: () => void;
  personaExists?: boolean;
}

export const ResearchWizard: React.FC<ResearchWizardProps & { headerActions?: ResearchWizardHeaderActions }> = ({ 
  onComplete,
  onCancel,
  initialKeywords,
  initialIndustry,
  initialTargetAudience,
  initialResearchMode,
  initialConfig,
  initialResults,
  headerActions,
}) => {
  const wizard = useResearchWizard(
    initialKeywords, 
    initialIndustry,
    initialTargetAudience,
    initialResearchMode,
    initialConfig
  );
  const execution = useResearchExecution();
  const [providerAvailability, setProviderAvailability] = useState<ProviderAvailability | null>(null);
  const [advanced, setAdvanced] = useState<boolean>(false);
  const hasSavedProject = useRef(false); // Track if we've already saved this project
  
  // Restore initial results if provided (e.g., from saved project)
  useEffect(() => {
    if (initialResults && !wizard.state.results) {
      wizard.updateState({ results: initialResults });
      // Navigate to results step if results are available
      if (wizard.state.currentStep < 3) {
        wizard.updateState({ currentStep: 3 });
      }
    }
  }, [initialResults]); // Only run once on mount
  
  // Restore intent analysis and confirmed intent from draft
  useEffect(() => {
    if (execution.intentAnalysis && wizard.state.keywords.length > 0) {
      // Intent analysis already restored by useResearchExecution hook
      console.log('[ResearchWizard] ✅ Intent analysis restored from draft');
    }
    if (execution.confirmedIntent && wizard.state.keywords.length > 0) {
      // Confirmed intent already restored by useResearchExecution hook
      console.log('[ResearchWizard] ✅ Confirmed intent restored from draft');
    }
  }, [execution.intentAnalysis, execution.confirmedIntent, wizard.state.keywords]);

  // Load provider availability on mount
  useEffect(() => {
    const loadProviderAvailability = async () => {
      try {
        const config = await getResearchConfig();
        setProviderAvailability(config?.provider_availability || null);
      } catch (error) {
        console.error('[ResearchWizard] Failed to load provider availability:', error);
        // Set default availability on error
        setProviderAvailability({
          google_available: true,
          exa_available: false,
          tavily_available: false,
          gemini_key_status: 'missing',
          exa_key_status: 'missing',
          tavily_key_status: 'missing',
        });
      }
    };
    loadProviderAvailability();
  }, []);

  // Handle results from execution
  useEffect(() => {
    if (execution.result && !execution.isExecuting) {
      console.log('[ResearchWizard] Results received, updating state and navigating:', {
        hasResults: !!execution.result,
        currentStep: wizard.state.currentStep,
        shouldNavigate: wizard.state.currentStep === 2
      });
      wizard.updateState({ results: execution.result });
      if (wizard.state.currentStep === 2) {
        wizard.nextStep();
      }
    }
  }, [execution.result, execution.isExecuting]); // Don't depend on currentStep to avoid loops

  // Auto-save research project when research completes
  useEffect(() => {
    // Save when intent-driven research completes
    if (execution.intentResult?.success && !hasSavedProject.current && wizard.state.keywords.length > 0) {
      hasSavedProject.current = true;
      
      // Generate project title from keywords
      const projectTitle = `Research: ${wizard.state.keywords.slice(0, 3).join(', ')}`;
      
      // Save project to Asset Library
      intentResearchApi.saveResearchProject(wizard.state, {
        intentAnalysis: execution.intentAnalysis,
        confirmedIntent: execution.confirmedIntent,
        intentResult: execution.intentResult,
        title: projectTitle,
        description: `Research project on ${wizard.state.keywords.join(', ')}. ` +
          `Industry: ${wizard.state.industry}, Target Audience: ${wizard.state.targetAudience}`,
      }).then((response) => {
        if (response.success) {
          console.log('[ResearchWizard] ✅ Final research project saved to Asset Library:', response.asset_id);
          // Clear draft after successful final save
          clearDraftFromStorage();
        } else {
          console.warn('[ResearchWizard] ⚠️ Failed to save final research project:', response.message);
        }
      }).catch((error) => {
        console.error('[ResearchWizard] ❌ Error saving final research project:', error);
      });
    }
    
    // Save when legacy research completes (fallback)
    if (wizard.state.results && !hasSavedProject.current && wizard.state.keywords.length > 0 && !execution.intentResult) {
      hasSavedProject.current = true;
      
      const projectTitle = `Research: ${wizard.state.keywords.slice(0, 3).join(', ')}`;
      
      intentResearchApi.saveResearchProject(wizard.state, {
        legacyResult: wizard.state.results,
        title: projectTitle,
        description: `Completed research project on ${wizard.state.keywords.join(', ')}. ` +
          `Industry: ${wizard.state.industry}, Target Audience: ${wizard.state.targetAudience}`,
      }).then((response) => {
        if (response.success) {
          console.log('[ResearchWizard] ✅ Final research project saved to Asset Library:', response.asset_id);
          // Clear draft after successful final save
          clearDraftFromStorage();
        } else {
          console.warn('[ResearchWizard] ⚠️ Failed to save final research project:', response.message);
        }
      }).catch((error) => {
        console.error('[ResearchWizard] ❌ Error saving final research project:', error);
      });
    }
  }, [execution.intentResult, wizard.state.results, wizard.state.keywords, wizard.state.industry, wizard.state.targetAudience, execution.intentAnalysis, execution.confirmedIntent]);

  // Handle completion callback and track history
  useEffect(() => {
    if (wizard.state.results && onComplete) {
      // Track in research history when results are available
      if (wizard.state.keywords.length > 0) {
        // Extract a summary from results if available
        const resultSummary = wizard.state.results.suggested_angles?.[0] || 
                             wizard.state.results.keyword_analysis?.primary_keywords?.[0] ||
                             wizard.state.results.sources?.[0]?.title;
        
        addResearchHistory({
          keywords: wizard.state.keywords,
          industry: wizard.state.industry,
          targetAudience: wizard.state.targetAudience,
          researchMode: wizard.state.researchMode,
          resultSummary,
        });
      }
      
      onComplete(wizard.state.results);
    }
  }, [wizard.state.results, wizard.state.keywords, wizard.state.industry, wizard.state.targetAudience, wizard.state.researchMode, onComplete]);

  const renderStep = () => {
    const stepProps = {
      state: wizard.state,
      onUpdate: wizard.updateState,
      onNext: wizard.nextStep,
      onBack: wizard.prevStep,
    };

    switch (wizard.state.currentStep) {
      case 1:
        return <ResearchInput {...stepProps} advanced={advanced} onAdvancedChange={setAdvanced} execution={execution} />;
      case 2:
        return <StepProgress {...stepProps} execution={execution} />;
      case 3:
        return <StepResults {...stepProps} execution={execution} />;
      default:
        return <ResearchInput {...stepProps} advanced={advanced} onAdvancedChange={setAdvanced} execution={execution} />;
    }
  };

  return (
    <div>
      {/* Wizard Container */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(14, 165, 233, 0.2)',
        borderRadius: '20px',
        boxShadow: '0 4px 16px rgba(14, 165, 233, 0.1)',
        overflow: 'hidden',
      }}>
        {/* Header with Compact Steps */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.08) 0%, rgba(56, 189, 248, 0.08) 100%)',
          borderBottom: '1px solid rgba(14, 165, 233, 0.15)',
          padding: '14px 24px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '24px' }}>
            {/* Title Section */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: '1', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <h1 style={{ 
                  margin: 0, 
                  fontSize: '20px',
                  fontWeight: '700',
                  color: '#0c4a6e',
                  letterSpacing: '-0.01em',
                }}>
                  Research Wizard
                </h1>
                
                {/* Persona Button */}
                {headerActions?.onOpenPersona && (
                  <button
                    onClick={headerActions.onOpenPersona}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: headerActions.personaExists ? '#22c55e' : '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: '500',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      boxShadow: headerActions.personaExists 
                        ? '0 0 12px rgba(34, 197, 94, 0.4), 0 1px 4px rgba(34, 197, 94, 0.2)'
                        : '0 0 12px rgba(239, 68, 68, 0.4), 0 1px 4px rgba(239, 68, 68, 0.2)',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-1px)';
                      if (headerActions.personaExists) {
                        e.currentTarget.style.boxShadow = '0 0 16px rgba(34, 197, 94, 0.5), 0 2px 6px rgba(34, 197, 94, 0.3)';
                      } else {
                        e.currentTarget.style.boxShadow = '0 0 16px rgba(239, 68, 68, 0.5), 0 2px 6px rgba(239, 68, 68, 0.3)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      if (headerActions.personaExists) {
                        e.currentTarget.style.boxShadow = '0 0 12px rgba(34, 197, 94, 0.4), 0 1px 4px rgba(34, 197, 94, 0.2)';
                      } else {
                        e.currentTarget.style.boxShadow = '0 0 12px rgba(239, 68, 68, 0.4), 0 1px 4px rgba(239, 68, 68, 0.2)';
                      }
                    }}
                    title={headerActions.personaExists ? 'View Research Persona' : 'Create Research Persona'}
                  >
                    <span style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      background: 'white',
                      boxShadow: '0 0 4px rgba(255, 255, 255, 0.8)',
                    }} />
                    <span>Persona</span>
                  </button>
                )}
                
                {/* Competitors Button */}
                {headerActions?.onOpenCompetitors && (
                  <button
                    onClick={headerActions.onOpenCompetitors}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: '#0284c7',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: '500',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      boxShadow: '0 2px 6px rgba(2, 132, 199, 0.2)',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#0369a1';
                      e.currentTarget.style.transform = 'translateY(-1px)';
                      e.currentTarget.style.boxShadow = '0 4px 10px rgba(2, 132, 199, 0.3)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#0284c7';
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 6px rgba(2, 132, 199, 0.2)';
                    }}
                    title="View Competitor Analysis"
                  >
                    <span>📊</span>
                    <span>Competitors</span>
                  </button>
                )}
                
                {/* Advanced Chip */}
                <AdvancedChip advanced={advanced} />
              </div>
              
              {/* Compact Step Indicators */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginLeft: '8px',
              }}>
                {[1, 2, 3].map((step, index) => {
                  const isActive = step === wizard.state.currentStep;
                  const isCompleted = step < wizard.state.currentStep;
                  const isClickable = step <= wizard.state.currentStep;
                  
                  return (
                    <React.Fragment key={step}>
                      {index > 0 && (
                        <div style={{
                          width: '20px',
                          height: '2px',
                          background: isCompleted || (step === wizard.state.currentStep)
                            ? 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)'
                            : 'rgba(14, 165, 233, 0.2)',
                          transition: 'all 0.3s ease',
                        }} />
                      )}
                      <div 
                        style={{ 
                          display: 'flex', 
                          flexDirection: 'column', 
                          alignItems: 'center', 
                          gap: '4px',
                          cursor: isClickable ? 'pointer' : 'default',
                          transition: 'all 0.2s ease',
                        }}
                        onClick={() => {
                          if (isClickable) {
                            wizard.updateState({ currentStep: step });
                          }
                        }}
                        onMouseEnter={(e) => {
                          if (isClickable) {
                            e.currentTarget.style.transform = 'translateY(-1px)';
                          }
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'translateY(0)';
                        }}
                      >
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: isActive 
                            ? 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)'
                            : isCompleted
                            ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                            : 'rgba(14, 165, 233, 0.1)',
                          color: (isActive || isCompleted) ? 'white' : '#64748b',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: '700',
                          fontSize: '13px',
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          border: isActive ? '2px solid rgba(14, 165, 233, 0.3)' : '2px solid rgba(14, 165, 233, 0.1)',
                          boxShadow: isActive 
                            ? '0 2px 8px rgba(14, 165, 233, 0.25)' 
                            : isCompleted 
                            ? '0 1px 4px rgba(34, 197, 94, 0.2)'
                            : 'none',
                        }}>
                          {isCompleted ? '✓' : step}
                        </div>
                        <span style={{
                          fontSize: '11px',
                          color: (isActive || isCompleted) ? '#0c4a6e' : '#64748b',
                          fontWeight: isActive ? '600' : '400',
                          letterSpacing: '0.01em',
                          whiteSpace: 'nowrap',
                        }}>
                          {step === 1 && 'Configure'}
                          {step === 2 && 'Execute'}
                          {step === 3 && 'Analyze'}
                        </span>
                      </div>
                    </React.Fragment>
                  );
                })}
              </div>
            </div>

            {/* Cancel Button */}
            {onCancel && (
              <button
                onClick={() => {
                  wizard.reset();
                  onCancel();
                }}
                style={{
                  padding: '6px 12px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  color: '#dc2626',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                }}
              >
                ✕ Cancel
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{
          background: 'rgba(14, 165, 233, 0.1)',
          height: '3px',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div
            style={{
              background: 'linear-gradient(90deg, #0ea5e9 0%, #38bdf8 100%)',
              height: '100%',
              width: `${(wizard.state.currentStep / wizard.maxSteps) * 100}%`,
              transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 0 6px rgba(14, 165, 233, 0.4)',
            }}
          />
        </div>

        {/* Content */}
        <div style={{ padding: '20px' }}>
          {renderStep()}
        </div>

        {/* Navigation Footer */}
        {wizard.state.currentStep < 3 && (
          <div style={{
            padding: '20px 28px',
            borderTop: '1px solid rgba(14, 165, 233, 0.15)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'rgba(14, 165, 233, 0.03)',
          }}>
            <button
              onClick={wizard.prevStep}
              disabled={wizard.isFirstStep}
              style={{
                padding: '10px 24px',
                background: wizard.isFirstStep ? 'rgba(100, 116, 139, 0.1)' : 'rgba(255, 255, 255, 0.8)',
                color: wizard.isFirstStep ? '#94a3b8' : '#0c4a6e',
                border: `1px solid ${wizard.isFirstStep ? 'rgba(100, 116, 139, 0.2)' : 'rgba(14, 165, 233, 0.2)'}`,
                borderRadius: '10px',
                cursor: wizard.isFirstStep ? 'not-allowed' : 'pointer',
                fontSize: '13px',
                fontWeight: '500',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                if (!wizard.isFirstStep) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 1)';
                  e.currentTarget.style.transform = 'translateX(-4px)';
                  e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
                }
              }}
              onMouseLeave={(e) => {
                if (!wizard.isFirstStep) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.8)';
                  e.currentTarget.style.transform = 'translateX(0)';
                  e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
                }
              }}
            >
              ← Back
            </button>

            {/* Research Button - Hidden on Step 1 when IntentConfirmationPanel is visible (has its own "Start Research" button) */}
            {!(wizard.state.currentStep === 1 && execution.intentAnalysis) && (
              <button
                onClick={() => {
                  if (wizard.state.currentStep === 1) {
                    // On Step 1: No intent analysis - go to progress step for traditional research
                    wizard.nextStep();
                  } else {
                    wizard.nextStep();
                  }
                }}
                disabled={!wizard.canGoNext()}
                style={{
                  padding: '10px 24px',
                  background: wizard.canGoNext()
                    ? 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)'
                    : 'rgba(100, 116, 139, 0.2)',
                  color: wizard.canGoNext() ? 'white' : '#94a3b8',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: wizard.canGoNext() ? 'pointer' : 'not-allowed',
                  fontSize: '13px',
                  fontWeight: '600',
                  transition: 'all 0.2s ease',
                  boxShadow: wizard.canGoNext() ? '0 2px 8px rgba(14, 165, 233, 0.3)' : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
                onMouseEnter={(e) => {
                  if (wizard.canGoNext()) {
                    e.currentTarget.style.transform = 'translateX(4px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(14, 165, 233, 0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (wizard.canGoNext()) {
                    e.currentTarget.style.transform = 'translateX(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(14, 165, 233, 0.3)';
                  }
                }}
                title={
                  wizard.isLastStep ? 'Complete research' : 'Continue to next step'
                }
              >
                {wizard.isLastStep ? (
                  'Finish'
                ) : (
                  <>
                    → Next
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchWizard;

