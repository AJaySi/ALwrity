import React from 'react';
import PhaseNavigation from '../PhaseNavigation';

interface HeaderBarProps {
  phases: any[];
  currentPhase: string;
  onPhaseClick: (phaseId: string) => void;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ phases, currentPhase, onPhaseClick }) => {
  return (
    <div style={{ padding: 16, borderBottom: '1px solid #eee' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>AI Blog Writer</h2>
        <div style={{ 
          width: '40px', 
          height: '40px', 
          backgroundColor: '#f0f0f0', 
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px',
          fontWeight: 'bold',
          color: '#666'
        }}>
          A
        </div>
      </div>
      <PhaseNavigation
        phases={phases}
        currentPhase={currentPhase}
        onPhaseClick={onPhaseClick}
      />
    </div>
  );
};

export default HeaderBar;


