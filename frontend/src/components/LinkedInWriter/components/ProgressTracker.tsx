import React from 'react';

type ProgressStatus = 'pending' | 'active' | 'completed' | 'error';

export interface ProgressStep {
  id: string;
  label: string;
  status: ProgressStatus;
  message?: string;
  details?: Record<string, any>;
  timestamp?: string;
}

interface ProgressTrackerProps {
  steps: ProgressStep[];
  active: boolean;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({ steps, active }) => {
  if (!steps || steps.length === 0) return null;
  
  const completedSteps = steps.filter(step => step.status === 'completed').length;
  const progressPercentage = Math.round((completedSteps / steps.length) * 100);
  
  return (
    <div style={{
      marginBottom: '24px',
      padding: '20px',
      borderRadius: '16px',
      border: '1px solid rgba(10,102,194,0.15)',
      background: 'linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,253,255,0.98))',
      boxShadow: '0 8px 32px rgba(10,102,194,0.12)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Header with progress percentage */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        paddingBottom: '16px',
        borderBottom: '1px solid rgba(10,102,194,0.1)'
      }}>
        <div style={{
          fontSize: '16px',
          fontWeight: '600',
          color: '#0f172a'
        }}>
          LinkedIn Content Generation
        </div>
        <div style={{
          fontSize: '14px',
          fontWeight: '500',
          color: '#0a66c2',
          padding: '6px 12px',
          background: 'rgba(10,102,194,0.1)',
          borderRadius: '20px'
        }}>
          {progressPercentage}% Complete
        </div>
      </div>
      
      {/* Progress bar */}
      <div style={{
        width: '100%',
        height: '6px',
        background: '#e2e8f0',
        borderRadius: '3px',
        marginBottom: '20px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${progressPercentage}%`,
          height: '100%',
          background: 'linear-gradient(90deg, #0a66c2, #3b82f6)',
          borderRadius: '3px',
          transition: 'width 0.5s ease',
          boxShadow: '0 0 8px rgba(10,102,194,0.3)'
        }} />
      </div>
      
      {/* Steps */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {steps.map((step, idx) => (
          <div key={step.id} style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '16px',
            padding: '16px',
            borderRadius: '12px',
            background: step.status === 'active' ? 'rgba(10,102,194,0.05)' : 'transparent',
            border: step.status === 'active' ? '1px solid rgba(10,102,194,0.2)' : '1px solid transparent',
            transition: 'all 300ms ease',
            position: 'relative'
          }}>
            {/* Step indicator */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: step.status === 'completed' ? '#10b981' : 
                         step.status === 'active' ? '#0a66c2' : 
                         step.status === 'error' ? '#ef4444' : '#cbd5e1',
              color: 'white',
              fontSize: '14px',
              fontWeight: '600',
              flexShrink: 0,
              position: 'relative'
            }}>
              {step.status === 'completed' ? '✓' : 
               step.status === 'active' ? '●' : 
               step.status === 'error' ? '✕' : (idx + 1)}
              
              {/* Active step glow effect */}
              {step.status === 'active' && (
                <div style={{
                  position: 'absolute',
                  top: '-4px',
                  left: '-4px',
                  right: '-4px',
                  bottom: '-4px',
                  borderRadius: '50%',
                  background: 'radial-gradient(circle, rgba(10,102,194,0.3) 0%, transparent 70%)',
                  animation: 'pulse 2s ease-in-out infinite alternate',
                  zIndex: -1
                }} />
              )}
            </div>
            
            {/* Step content */}
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: '14px',
                fontWeight: '600',
                color: step.status === 'active' ? '#0a66c2' : 
                       step.status === 'completed' ? '#10b981' : 
                       step.status === 'error' ? '#ef4444' : '#64748b',
                marginBottom: '4px',
                transition: 'color 200ms ease'
              }}>
                {step.label}
              </div>
              
              {/* Step message */}
              {step.message && (
                <div style={{
                  fontSize: '13px',
                  color: step.status === 'active' ? '#475569' : '#94a3b8',
                  lineHeight: '1.4',
                  fontStyle: step.status === 'active' ? 'normal' : 'italic'
                }}>
                  {step.message}
                </div>
              )}
              
              {/* Step details */}
              {step.details && step.status === 'completed' && (
                <div style={{
                  marginTop: '8px',
                  padding: '8px 12px',
                  background: 'rgba(16,185,129,0.1)',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#065f46'
                }}>
                  {Object.entries(step.details).map(([key, value]) => (
                    <div key={key} style={{ marginBottom: '4px' }}>
                      <strong>{key}:</strong> {String(value)}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Status indicator */}
            <div style={{
              padding: '4px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: '500',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              background: step.status === 'completed' ? 'rgba(16,185,129,0.1)' :
                         step.status === 'active' ? 'rgba(10,102,194,0.1)' :
                         step.status === 'error' ? 'rgba(239,68,68,0.1)' : 'rgba(203,213,225,0.1)',
              color: step.status === 'completed' ? '#065f46' :
                     step.status === 'active' ? '#0a66c2' :
                     step.status === 'error' ? '#991b1b' : '#64748b',
              flexShrink: 0
            }}>
              {step.status}
            </div>
          </div>
        ))}
      </div>
      
      {/* Active status indicator */}
      {active && (
        <div style={{
          marginTop: '20px',
          padding: '12px 16px',
          background: 'rgba(10,102,194,0.05)',
          borderRadius: '12px',
          border: '1px solid rgba(10,102,194,0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: '#0a66c2',
            animation: 'pulse 1.5s ease-in-out infinite'
          }} />
          <div style={{
            fontSize: '14px',
            color: '#0a66c2',
            fontWeight: '500'
          }}>
            Content generation in progress...
          </div>
        </div>
      )}
      
      {/* CSS Animations */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse {
            0% { opacity: 0.6; transform: scale(1); }
            100% { opacity: 1; transform: scale(1.1); }
          }
        `
      }} />
    </div>
  );
};


