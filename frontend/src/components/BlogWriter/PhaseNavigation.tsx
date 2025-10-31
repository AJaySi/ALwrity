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

interface PhaseNavigationProps {
  phases: Phase[];
  onPhaseClick: (phaseId: string) => void;
  currentPhase: string;
}

export const PhaseNavigation: React.FC<PhaseNavigationProps> = ({
  phases,
  onPhaseClick,
  currentPhase
}) => {
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
        
        return (
          <button
            key={phase.id}
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
        );
      })}
    </div>
  );
};

export default PhaseNavigation;
