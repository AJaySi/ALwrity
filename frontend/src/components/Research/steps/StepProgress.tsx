import React, { useEffect } from 'react';
import { WizardStepProps } from '../types/research.types';
import { useResearchExecution } from '../hooks/useResearchExecution';

export const StepProgress: React.FC<WizardStepProps> = ({ state, onNext, onUpdate }) => {
  const { executeResearch, stopExecution, isExecuting, error, progressMessages, currentStatus } = useResearchExecution();

  useEffect(() => {
    // Start research when this step is reached
    const startResearch = async () => {
      const taskId = await executeResearch(state);
      if (taskId === 'cached') {
        // If cached, move to results immediately
        // The parent will handle this
      }
    };

    startResearch();

    return () => {
      if (isExecuting) {
        stopExecution();
      }
    };
  }, []); // Run once on mount

  // Move to next step when research completes
  useEffect(() => {
    if (!isExecuting && progressMessages.length > 0) {
      // Small delay to show final message
      const timer = setTimeout(() => {
        onNext();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [isExecuting, progressMessages.length, onNext]);

  const getStatusIcon = () => {
    if (error) return '❌';
    if (!isExecuting && progressMessages.length > 0) return '✅';
    if (currentStatus === 'completed') return '✅';
    return '🔄';
  };

  const getStatusColor = () => {
    if (error) return '#f44336';
    if (!isExecuting && progressMessages.length > 0) return '#4caf50';
    return '#1976d2';
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '8px', color: '#333' }}>Researching...</h2>
      <p style={{ marginBottom: '24px', color: '#666', fontSize: '15px' }}>
        Gathering insights from Google Search grounding
      </p>

      {/* Status Display */}
      <div style={{
        backgroundColor: '#f5f5f5',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>{getStatusIcon()}</div>
        
        {error ? (
          <>
            <h3 style={{ color: getStatusColor(), marginBottom: '8px' }}>Error</h3>
            <p style={{ color: '#666', fontSize: '14px' }}>{error}</p>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: '16px',
                padding: '8px 16px',
                backgroundColor: '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
              }}
            >
              Retry
            </button>
          </>
        ) : (
          <>
            <h3 style={{ color: getStatusColor(), marginBottom: '8px' }}>
              {currentStatus === 'completed' ? 'Complete!' : 'In Progress'}
            </h3>
            <p style={{ color: '#666', fontSize: '14px' }}>
              {isExecuting ? 'Analyzing sources and generating insights...' : 'Finalizing results...'}
            </p>
          </>
        )}
      </div>

      {/* Progress Messages */}
      {progressMessages.length > 0 && (
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          maxHeight: '300px',
          overflow: 'auto',
        }}>
          <div style={{ padding: '16px', borderBottom: '1px solid #e0e0e0' }}>
            <strong style={{ fontSize: '14px', color: '#333' }}>Progress Updates</strong>
          </div>
          {progressMessages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                padding: '12px 16px',
                borderBottom: idx < progressMessages.length - 1 ? '1px solid #f0f0f0' : 'none',
                fontSize: '13px',
                color: '#555',
              }}
            >
              {idx === progressMessages.length - 1 && isExecuting && (
                <span style={{ marginRight: '8px' }}>🔄</span>
              )}
              {msg.message}
            </div>
          ))}
        </div>
      )}

      {/* Cancel Button */}
      {isExecuting && (
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <button
            onClick={stopExecution}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Cancel Research
          </button>
        </div>
      )}
    </div>
  );
};

