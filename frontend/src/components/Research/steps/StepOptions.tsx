import React from 'react';
import { WizardStepProps, ModeCardInfo } from '../types/research.types';
import { ResearchProvider } from '../../../services/researchApi';

const modeCards: ModeCardInfo[] = [
  {
    mode: 'basic',
    title: 'Basic Research',
    description: 'Quick keyword-focused analysis for fast results',
    features: [
      'Primary & secondary keywords',
      'Current trends overview',
      'Top 5 content angles',
      'Key statistics',
    ],
    icon: '⚡',
  },
  {
    mode: 'comprehensive',
    title: 'Comprehensive Research',
    description: 'Deep analysis with full competitive intelligence',
    features: [
      'All basic features',
      'Expert quotes & opinions',
      'Competitor analysis',
      'Market forecasts',
      'Best practices & case studies',
      'Content gaps identification',
    ],
    icon: '📊',
  },
  {
    mode: 'targeted',
    title: 'Targeted Research',
    description: 'Customize what you need most',
    features: [
      'Select specific components',
      'Choose date ranges',
      'Filter source types',
      'Control depth & scope',
    ],
    icon: '🎯',
  },
];

export const StepOptions: React.FC<WizardStepProps> = ({ state, onUpdate }) => {
  const handleModeChange = (mode: any) => {
    onUpdate({ researchMode: mode });
  };

  const handleProviderChange = (provider: ResearchProvider) => {
    onUpdate({ config: { ...state.config, provider } });
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '8px', color: '#333' }}>Choose Research Mode</h2>
      <p style={{ marginBottom: '24px', color: '#666', fontSize: '15px' }}>
        Select the type of research that best fits your needs.
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px',
        marginBottom: '24px',
      }}>
        {modeCards.map(card => (
          <div
            key={card.mode}
            onClick={() => handleModeChange(card.mode)}
            style={{
              border: state.researchMode === card.mode ? '2px solid #1976d2' : '2px solid #e0e0e0',
              borderRadius: '12px',
              padding: '24px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              backgroundColor: state.researchMode === card.mode ? '#f0f7ff' : 'white',
            }}
            onMouseEnter={(e) => {
              if (state.researchMode !== card.mode) {
                e.currentTarget.style.borderColor = '#90caf9';
                e.currentTarget.style.backgroundColor = '#fafafa';
              }
            }}
            onMouseLeave={(e) => {
              if (state.researchMode !== card.mode) {
                e.currentTarget.style.borderColor = '#e0e0e0';
                e.currentTarget.style.backgroundColor = 'white';
              }
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ fontSize: '32px', marginRight: '12px' }}>{card.icon}</span>
              <h3 style={{ margin: 0, color: '#333', fontSize: '18px' }}>{card.title}</h3>
            </div>
            <p style={{ marginBottom: '16px', color: '#666', fontSize: '14px' }}>
              {card.description}
            </p>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#555' }}>
              {card.features.map((feature, idx) => (
                <li key={idx} style={{ marginBottom: '4px' }}>{feature}</li>
              ))}
            </ul>
            {state.researchMode === card.mode && (
              <div style={{
                marginTop: '16px',
                padding: '8px',
                backgroundColor: '#1976d2',
                color: 'white',
                borderRadius: '6px',
                textAlign: 'center',
                fontSize: '13px',
                fontWeight: '600',
              }}>
                ✓ Selected
              </div>
            )}
          </div>
        ))}
      </div>

      {state.researchMode !== 'basic' && (
        <div style={{ marginBottom: '24px', border: '1px solid #e0e0e0', borderRadius: '8px', padding: '15px', backgroundColor: '#f9f9f9' }}>
          <h3 style={{ marginTop: 0, marginBottom: '12px', color: '#555', fontSize: '16px' }}>
            🔍 Research Provider
          </h3>
          <div style={{ display: 'flex', gap: '12px' }}>
            <div
              onClick={() => handleProviderChange('google')}
              style={{
                flex: 1,
                padding: '12px',
                border: '2px solid',
                borderColor: (state.config.provider === 'google' || !state.config.provider) ? '#1976d2' : '#ddd',
                backgroundColor: (state.config.provider === 'google' || !state.config.provider) ? '#e3f2fd' : 'white',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ fontWeight: '600', marginBottom: '4px' }}>Google Search</div>
              <div style={{ fontSize: '11px', color: '#666' }}>
                Fast, broad coverage, trending topics
              </div>
            </div>
            <div
              onClick={() => handleProviderChange('exa')}
              style={{
                flex: 1,
                padding: '12px',
                border: '2px solid',
                borderColor: state.config.provider === 'exa' ? '#7c3aed' : '#ddd',
                backgroundColor: state.config.provider === 'exa' ? '#f3e8ff' : 'white',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ fontWeight: '600', marginBottom: '4px' }}>Exa Neural</div>
              <div style={{ fontSize: '11px', color: '#666' }}>
                Deep research, rich citations, semantic search
              </div>
            </div>
          </div>
        </div>
      )}

      <div style={{
        padding: '12px',
        backgroundColor: '#fff3e0',
        borderRadius: '8px',
        border: '1px solid #ffb74d',
        fontSize: '13px',
        color: '#e65100',
      }}>
        ℹ️ <strong>Note:</strong> You can always run additional research if you need more information later.
      </div>
    </div>
  );
};

