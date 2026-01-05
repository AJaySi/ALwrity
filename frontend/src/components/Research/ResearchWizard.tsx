import React, { useEffect, useState } from 'react';
import { useResearchWizard } from './hooks/useResearchWizard';
import { useResearchExecution } from './hooks/useResearchExecution';
import { ResearchInput } from './steps/ResearchInput';
import { StepProgress } from './steps/StepProgress';
import { StepResults } from './steps/StepResults';
import { ResearchWizardProps } from './types/research.types';
import { addResearchHistory } from '../../utils/researchHistory';
import { getResearchConfig, ProviderAvailability } from '../../api/researchConfig';
import { ProviderChips } from './steps/components/ProviderChips';
import { AdvancedChip } from './steps/components/AdvancedChip';
import { SmartResearchInfo } from './steps/components/SmartResearchInfo';

export const ResearchWizard: React.FC<ResearchWizardProps> = ({ 
  onComplete,
  onCancel,
  initialKeywords,
  initialIndustry,
  initialTargetAudience,
  initialResearchMode,
  initialConfig,
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
                
                {/* Provider Status Chips */}
                <ProviderChips providerAvailability={providerAvailability} advanced={advanced} />
                
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

            {/* Research Button (Unified - enabled only after intent analysis on Step 1) */}
            <button
              onClick={() => {
                if (wizard.state.currentStep === 1) {
                  // On Step 1: If intent is analyzed with high confidence, execute directly
                  if (execution.intentAnalysis?.success && 
                      execution.intentAnalysis.intent.confidence >= 0.7) {
                    const queriesToUse = execution.intentAnalysis.suggested_queries?.slice(0, 5) || [];
                    execution.executeIntentResearch(wizard.state, queriesToUse).then(result => {
                      if (result?.success) {
                        wizard.updateState({ currentStep: 3 }); // Skip to results
                      }
                    });
                  } else {
                    // No intent or low confidence - go to progress step for traditional research
                    wizard.nextStep();
                  }
                } else {
                  wizard.nextStep();
                }
              }}
              disabled={
                wizard.state.currentStep === 1 
                  ? !wizard.canGoNext() || !execution.intentAnalysis || execution.isExecuting
                  : !wizard.canGoNext()
              }
              style={{
                padding: '10px 24px',
                background: (() => {
                  const canProceed = wizard.state.currentStep === 1 
                    ? wizard.canGoNext() && execution.intentAnalysis && !execution.isExecuting
                    : wizard.canGoNext();
                  return canProceed 
                    ? 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)'
                    : 'rgba(100, 116, 139, 0.2)';
                })(),
                color: (() => {
                  const canProceed = wizard.state.currentStep === 1 
                    ? wizard.canGoNext() && execution.intentAnalysis && !execution.isExecuting
                    : wizard.canGoNext();
                  return canProceed ? 'white' : '#94a3b8';
                })(),
                border: 'none',
                borderRadius: '10px',
                cursor: (() => {
                  const canProceed = wizard.state.currentStep === 1 
                    ? wizard.canGoNext() && execution.intentAnalysis && !execution.isExecuting
                    : wizard.canGoNext();
                  return canProceed ? 'pointer' : 'not-allowed';
                })(),
                fontSize: '13px',
                fontWeight: '600',
                transition: 'all 0.2s ease',
                boxShadow: (() => {
                  const canProceed = wizard.state.currentStep === 1 
                    ? wizard.canGoNext() && execution.intentAnalysis && !execution.isExecuting
                    : wizard.canGoNext();
                  return canProceed ? '0 2px 8px rgba(14, 165, 233, 0.3)' : 'none';
                })(),
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
              onMouseEnter={(e) => {
                const canProceed = wizard.state.currentStep === 1 
                  ? wizard.canGoNext() && execution.intentAnalysis && !execution.isExecuting
                  : wizard.canGoNext();
                if (canProceed) {
                  e.currentTarget.style.transform = 'translateX(4px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(14, 165, 233, 0.4)';
                }
              }}
              onMouseLeave={(e) => {
                const canProceed = wizard.state.currentStep === 1 
                  ? wizard.canGoNext() && execution.intentAnalysis && !execution.isExecuting
                  : wizard.canGoNext();
                if (canProceed) {
                  e.currentTarget.style.transform = 'translateX(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(14, 165, 233, 0.3)';
                }
              }}
              title={
                wizard.state.currentStep === 1 && !execution.intentAnalysis
                  ? 'Click "Intent & Options" in the text area to analyze your research first'
                  : wizard.isLastStep ? 'Complete research' : 'Start research'
              }
            >
              {execution.isExecuting ? (
                <>
                  <span style={{ animation: 'pulse 1.5s ease-in-out infinite' }}>🔍</span>
                  Researching...
                </>
              ) : wizard.isLastStep ? (
                'Finish'
              ) : (
                <>
                  🚀 Research
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchWizard;

