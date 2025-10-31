import React, { useState } from 'react';
import PhaseNavigation from './PhaseNavigation';
import { Phase } from './PhaseNavigation';

// Test component to verify phase navigation functionality
export const PhaseNavigationTest: React.FC = () => {
  const [currentPhase, setCurrentPhase] = useState<string>('research');
  
  const testPhases: Phase[] = [
    {
      id: 'research',
      name: 'Research',
      icon: '🔍',
      description: 'Research your topic and gather data',
      completed: true,
      current: currentPhase === 'research',
      disabled: false
    },
    {
      id: 'outline',
      name: 'Outline',
      icon: '📝',
      description: 'Create and refine your blog outline',
      completed: true,
      current: currentPhase === 'outline',
      disabled: false
    },
    {
      id: 'content',
      name: 'Content',
      icon: '✍️',
      description: 'Generate and edit your blog content',
      completed: false,
      current: currentPhase === 'content',
      disabled: false
    },
    {
      id: 'seo',
      name: 'SEO',
      icon: '📈',
      description: 'Optimize for search engines',
      completed: false,
      current: currentPhase === 'seo',
      disabled: true
    },
    {
      id: 'publish',
      name: 'Publish',
      icon: '🚀',
      description: 'Publish your blog post',
      completed: false,
      current: currentPhase === 'publish',
      disabled: true
    }
  ];

  const handlePhaseClick = (phaseId: string) => {
    setCurrentPhase(phaseId);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Phase Navigation Test</h2>
      <p>Current Phase: <strong>{currentPhase}</strong></p>
      
      <PhaseNavigation
        phases={testPhases}
        currentPhase={currentPhase}
        onPhaseClick={handlePhaseClick}
      />
      
      <div style={{ marginTop: '20px', padding: '16px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Phase Status:</h3>
        <ul>
          {testPhases.map(phase => (
            <li key={phase.id}>
              <strong>{phase.name}</strong>: 
              {phase.completed ? ' ✅ Completed' : ' ⏳ Pending'} | 
              {phase.current ? ' 🎯 Current' : ''} | 
              {phase.disabled ? ' 🚫 Disabled' : ' ✅ Enabled'}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default PhaseNavigationTest;
