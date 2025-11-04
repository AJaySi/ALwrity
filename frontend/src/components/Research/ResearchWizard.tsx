import React, { useEffect } from 'react';
import { useResearchWizard } from './hooks/useResearchWizard';
import { useResearchExecution } from './hooks/useResearchExecution';
import { ResearchInput } from './steps/ResearchInput';
import { StepProgress } from './steps/StepProgress';
import { StepResults } from './steps/StepResults';
import { ResearchWizardProps } from './types/research.types';

export const ResearchWizard: React.FC<ResearchWizardProps> = ({ 
  onComplete,
  onCancel,
  initialKeywords,
  initialIndustry,
}) => {
  const wizard = useResearchWizard(initialKeywords, initialIndustry);
  const execution = useResearchExecution();

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

  // Handle completion callback
  useEffect(() => {
    if (wizard.state.results && onComplete) {
      onComplete(wizard.state.results);
    }
  }, [wizard.state.results, onComplete]);

  const renderStep = () => {
    const stepProps = {
      state: wizard.state,
      onUpdate: wizard.updateState,
      onNext: wizard.nextStep,
      onBack: wizard.prevStep,
    };

    switch (wizard.state.currentStep) {
      case 1:
        return <ResearchInput {...stepProps} />;
      case 2:
        return <StepProgress {...stepProps} execution={execution} />;
      case 3:
        return <StepResults {...stepProps} />;
      default:
        return <ResearchInput {...stepProps} />;
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
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.08) 0%, rgba(56, 189, 248, 0.08) 100%)',
          borderBottom: '1px solid rgba(14, 165, 233, 0.15)',
          padding: '20px 28px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ 
                margin: 0, 
                fontSize: '24px',
                fontWeight: '700',
                color: '#0c4a6e',
              }}>
                Research Wizard
              </h1>
              <p style={{ 
                margin: '4px 0 0 0', 
                fontSize: '13px', 
                color: '#0369a1',
                fontWeight: '400',
              }}>
                Phase {wizard.state.currentStep} of {wizard.maxSteps} • AI-Powered Intelligence
              </p>
            </div>
            {onCancel && (
              <button
                onClick={() => {
                  wizard.reset();
                  onCancel();
                }}
                style={{
                  padding: '8px 16px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  color: '#dc2626',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '13px',
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
          height: '5px',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div
            style={{
              background: 'linear-gradient(90deg, #0ea5e9 0%, #38bdf8 100%)',
              height: '100%',
              width: `${(wizard.state.currentStep / wizard.maxSteps) * 100}%`,
              transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 0 8px rgba(14, 165, 233, 0.4)',
            }}
          />
        </div>

        {/* Step Indicators */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-around',
          padding: '24px 40px',
          borderBottom: '1px solid rgba(14, 165, 233, 0.15)',
          background: 'rgba(14, 165, 233, 0.03)',
        }}>
          {[1, 2, 3].map(step => {
            const isActive = step === wizard.state.currentStep;
            const isCompleted = step < wizard.state.currentStep;
            const isClickable = step <= wizard.state.currentStep;
            
            return (
              <div 
                key={step} 
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  position: 'relative',
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
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <div style={{
                  width: '48px',
                  height: '48px',
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
                  fontSize: '18px',
                  marginBottom: '10px',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  border: isActive ? '2px solid rgba(14, 165, 233, 0.3)' : '2px solid rgba(14, 165, 233, 0.1)',
                  boxShadow: isActive 
                    ? '0 4px 16px rgba(14, 165, 233, 0.3)' 
                    : isCompleted 
                    ? '0 2px 8px rgba(34, 197, 94, 0.2)'
                    : 'none',
                }}>
                  {isCompleted ? '✓' : step}
                </div>
                <span style={{
                  fontSize: '13px',
                  color: (isActive || isCompleted) ? '#0c4a6e' : '#64748b',
                  fontWeight: isActive ? '600' : '400',
                  letterSpacing: '0.01em',
                }}>
                  {step === 1 && 'Configure'}
                  {step === 2 && 'Execute'}
                  {step === 3 && 'Analyze'}
                </span>
              </div>
            );
          })}
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

            <button
              onClick={wizard.nextStep}
              disabled={!wizard.canGoNext()}
              style={{
                padding: '10px 24px',
                background: wizard.canGoNext() 
                  ? 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)'
                  : 'rgba(100, 116, 139, 0.2)',
                color: wizard.canGoNext() ? 'white' : '#94a3b8',
                border: wizard.canGoNext() ? 'none' : '1px solid rgba(100, 116, 139, 0.2)',
                borderRadius: '10px',
                cursor: wizard.canGoNext() ? 'pointer' : 'not-allowed',
                fontSize: '13px',
                fontWeight: '600',
                transition: 'all 0.2s ease',
                boxShadow: wizard.canGoNext() ? '0 2px 8px rgba(14, 165, 233, 0.3)' : 'none',
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
            >
              {wizard.isLastStep ? 'Finish' : 'Continue →'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchWizard;

