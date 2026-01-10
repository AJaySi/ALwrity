import React from 'react';
import { Tooltip } from '@mui/material';
import { AutoAwesome } from '@mui/icons-material';
import { ResearchPreset } from '../types';

interface PresetsCardProps {
  presets: ResearchPreset[];
  personaExists: boolean;
  onPresetClick: (preset: ResearchPreset) => void;
  onReset: () => void;
}

export const PresetsCard: React.FC<PresetsCardProps> = ({
  presets,
  personaExists,
  onPresetClick,
  onReset,
}) => {
  return (
    <div className="card-hover" style={{
      background: 'rgba(255, 255, 255, 0.8)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(14, 165, 233, 0.2)',
      borderRadius: '16px',
      padding: '20px',
      marginBottom: '20px',
      boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
      animation: 'fadeInUp 0.6s ease-out',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '18px',
        }}>
          🎯
        </div>
        <h3 style={{ margin: 0, color: '#0c4a6e', fontSize: '18px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          Quick Start Presets
          {personaExists && (
            <Tooltip
              title={
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, marginBottom: '4px', fontSize: '13px' }}>
                    Personalized Presets
                  </div>
                  <div style={{ fontSize: '12px', lineHeight: '1.5' }}>
                    These presets are customized based on your content types, writing patterns, and website topics from your research persona.
                  </div>
                </div>
              }
              arrow
              placement="top"
            >
              <span style={{ display: 'inline-flex', alignItems: 'center', cursor: 'help', color: '#0ea5e9' }}>
                <AutoAwesome sx={{ fontSize: 16 }} />
              </span>
            </Tooltip>
          )}
        </h3>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {presets.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => onPresetClick(preset)}
            className="card-hover"
            style={{
              padding: '14px',
              background: 'rgba(255, 255, 255, 0.9)',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '12px',
              cursor: 'pointer',
              textAlign: 'left',
              fontSize: '14px',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
              overflow: 'hidden',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateX(4px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(14, 165, 233, 0.2)';
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateX(0)';
              e.currentTarget.style.boxShadow = 'none';
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <span style={{ fontSize: '20px' }}>{preset.icon}</span>
              <div style={{ fontWeight: '600', color: '#0c4a6e', fontSize: '14px' }}>
                {preset.name}
              </div>
            </div>
            <div style={{ fontSize: '11px', color: '#64748b', lineHeight: '1.5' }}>
              {preset.keywords}
            </div>
            <div style={{
              marginTop: '6px',
              display: 'inline-block',
              padding: '3px 10px',
              background: 'rgba(14, 165, 233, 0.1)',
              borderRadius: '10px',
              fontSize: '10px',
              color: '#0369a1',
              fontWeight: '600',
            }}>
              {preset.industry}
            </div>
          </button>
        ))}
      </div>
      
      <button
        onClick={onReset}
        style={{
          marginTop: '12px',
          padding: '10px 16px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: '10px',
          cursor: 'pointer',
          fontSize: '13px',
          width: '100%',
          color: '#dc2626',
          fontWeight: '500',
          transition: 'all 0.2s ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
          e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.4)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
          e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.25)';
        }}
      >
        ↻ Reset Research
      </button>
    </div>
  );
};
