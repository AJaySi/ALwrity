import React, { useEffect } from 'react';
import { useResearchWizard } from './hooks/useResearchWizard';
import { useResearchExecution } from './hooks/useResearchExecution';
import { StepKeyword } from './steps/StepKeyword';
import { StepOptions } from './steps/StepOptions';
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
      wizard.updateState({ results: execution.result });
      if (wizard.state.currentStep === 3) {
        wizard.nextStep();
      }
    }
  }, [execution.result, execution.isExecuting]);

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
        return <StepKeyword {...stepProps} />;
      case 2:
        return <StepOptions {...stepProps} />;
      case 3:
        return <StepProgress {...stepProps} />;
      case 4:
        return <StepResults {...stepProps} />;
      default:
        return <StepKeyword {...stepProps} />;
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f5f5f5',
      padding: '20px',
    }}>
      {/* Wizard Container */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          backgroundColor: '#1976d2',
          color: 'white',
          padding: '24px',
          borderBottom: '1px solid #e0e0e0',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ margin: 0, fontSize: '24px' }}>Research Wizard</h1>
              <p style={{ margin: '8px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
                Step {wizard.state.currentStep} of {wizard.maxSteps}
              </p>
            </div>
            {onCancel && (
              <button
                onClick={onCancel}
                style={{
                  padding: '8px 16px',
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{
          backgroundColor: '#f0f0f0',
          height: '4px',
          position: 'relative',
        }}>
          <div
            style={{
              backgroundColor: '#1976d2',
              height: '100%',
              width: `${(wizard.state.currentStep / wizard.maxSteps) * 100}%`,
              transition: 'width 0.3s ease',
            }}
          />
        </div>

        {/* Step Indicators */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-around',
          padding: '20px 40px',
          borderBottom: '1px solid #e0e0e0',
        }}>
          {[1, 2, 3, 4].map(step => (
            <div key={step} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: step <= wizard.state.currentStep ? '#1976d2' : '#e0e0e0',
                color: step <= wizard.state.currentStep ? 'white' : '#999',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold',
                fontSize: '16px',
                marginBottom: '8px',
                transition: 'all 0.3s ease',
              }}>
                {step < wizard.state.currentStep ? '✓' : step}
              </div>
              <span style={{
                fontSize: '12px',
                color: step <= wizard.state.currentStep ? '#1976d2' : '#999',
                fontWeight: step === wizard.state.currentStep ? '600' : 'normal',
              }}>
                {step === 1 && 'Setup'}
                {step === 2 && 'Options'}
                {step === 3 && 'Research'}
                {step === 4 && 'Results'}
              </span>
            </div>
          ))}
        </div>

        {/* Content */}
        <div style={{ padding: '24px' }}>
          {renderStep()}
        </div>

        {/* Navigation Footer */}
        {wizard.state.currentStep <= 2 && (
          <div style={{
            padding: '20px 24px',
            borderTop: '1px solid #e0e0e0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: '#fafafa',
          }}>
            <button
              onClick={wizard.prevStep}
              disabled={wizard.isFirstStep}
              style={{
                padding: '10px 20px',
                backgroundColor: wizard.isFirstStep ? '#f0f0f0' : 'white',
                color: wizard.isFirstStep ? '#999' : '#333',
                border: wizard.isFirstStep ? '1px solid #e0e0e0' : '1px solid #ddd',
                borderRadius: '6px',
                cursor: wizard.isFirstStep ? 'not-allowed' : 'pointer',
                fontSize: '14px',
              }}
            >
              ← Back
            </button>

            <button
              onClick={wizard.nextStep}
              disabled={!wizard.canGoNext()}
              style={{
                padding: '10px 24px',
                backgroundColor: wizard.canGoNext() ? '#1976d2' : '#e0e0e0',
                color: wizard.canGoNext() ? 'white' : '#999',
                border: 'none',
                borderRadius: '6px',
                cursor: wizard.canGoNext() ? 'pointer' : 'not-allowed',
                fontSize: '14px',
                fontWeight: '600',
              }}
            >
              {wizard.isLastStep ? 'Finish' : 'Next →'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchWizard;

