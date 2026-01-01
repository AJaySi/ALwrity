import React from 'react';
import { formatAngle } from '../../../../utils/researchAngles';
import { PersonalizationIndicator } from './PersonalizationIndicator';

interface ResearchAnglesProps {
  angles: string[];
  onUseAngle: (angle: string) => void;
  hasPersona?: boolean;
}

export const ResearchAngles: React.FC<ResearchAnglesProps> = ({ angles, onUseAngle, hasPersona = false }) => {
  if (angles.length === 0) return null;

  return (
    <div style={{
      marginTop: '12px',
      padding: '12px',
      background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)',
      border: '1px solid rgba(168, 85, 247, 0.15)',
      borderRadius: '8px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        marginBottom: '10px',
      }}>
        <span style={{
          fontSize: '16px',
        }}>💡</span>
        <span style={{
          fontSize: '13px',
          fontWeight: '600',
          color: '#7c3aed',
        }}>
          Explore Alternative Research Angles
        </span>
        {hasPersona && (
          <PersonalizationIndicator 
            type="angles" 
            hasPersona={hasPersona}
            source="from your writing patterns"
          />
        )}
      </div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '10px',
      }}>
        {angles.map((angle, idx) => (
          <button
            key={idx}
            onClick={() => onUseAngle(angle)}
            style={{
              padding: '10px 14px',
              background: 'rgba(255, 255, 255, 0.9)',
              border: '1px solid rgba(168, 85, 247, 0.2)',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: '500',
              color: '#6b21a8',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
              boxShadow: '0 1px 3px rgba(168, 85, 247, 0.1)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(168, 85, 247, 0.1)';
              e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.4)';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(168, 85, 247, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.9)';
              e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.2)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 1px 3px rgba(168, 85, 247, 0.1)';
            }}
            title={`Click to research: ${angle}`}
          >
            <span style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}>
              <span style={{ fontSize: '14px' }}>🔍</span>
              <span>{formatAngle(angle)}</span>
            </span>
          </button>
        ))}
      </div>
      <div style={{
        marginTop: '8px',
        fontSize: '11px',
        color: '#64748b',
        fontStyle: 'italic',
      }}>
        Click any angle to explore a different research focus
      </div>
    </div>
  );
};

