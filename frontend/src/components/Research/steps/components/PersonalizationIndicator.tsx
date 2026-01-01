import React from 'react';
import { Tooltip } from '@mui/material';
import { InfoOutlined, AutoAwesome } from '@mui/icons-material';

interface PersonalizationIndicatorProps {
  type: 'placeholder' | 'keywords' | 'presets' | 'angles' | 'provider' | 'mode';
  hasPersona: boolean;
  source?: string; // e.g., "from your website content", "from your writing style"
}

const PERSONALIZATION_TOOLTIPS = {
  placeholder: {
    title: 'Personalized Placeholders',
    description: 'These placeholders are customized based on your research persona, including research angles and recommended presets from your website analysis.',
    source: 'from your research persona'
  },
  keywords: {
    title: 'Personalized Keywords',
    description: 'Keywords are extracted from your actual website content and matched to your industry and audience preferences.',
    source: 'from your website content'
  },
  presets: {
    title: 'Personalized Presets',
    description: 'Research presets are generated based on your content types, writing patterns, and website topics for maximum relevance.',
    source: 'from your content strategy'
  },
  angles: {
    title: 'Personalized Research Angles',
    description: 'Research angles are derived from your writing patterns and style guidelines to match your content approach.',
    source: 'from your writing patterns'
  },
  provider: {
    title: 'Smart Provider Selection',
    description: 'Research provider is automatically selected based on your writing style complexity and content type preferences.',
    source: 'from your writing style'
  },
  mode: {
    title: 'Optimized Research Depth',
    description: 'Research depth is matched to your writing complexity level - high complexity gets comprehensive research, simple gets basic.',
    source: 'from your writing complexity'
  }
};

export const PersonalizationIndicator: React.FC<PersonalizationIndicatorProps> = ({
  type,
  hasPersona,
  source
}) => {
  if (!hasPersona) {
    return null; // Don't show indicator if no persona
  }

  const tooltip = PERSONALIZATION_TOOLTIPS[type];
  const displaySource = source || tooltip.source;

  return (
    <Tooltip
      title={
        <div style={{ padding: '4px 0' }}>
          <div style={{ fontWeight: 600, marginBottom: '4px', fontSize: '13px' }}>
            {tooltip.title}
          </div>
          <div style={{ fontSize: '12px', lineHeight: '1.5', marginBottom: '4px' }}>
            {tooltip.description}
          </div>
          <div style={{ fontSize: '11px', color: 'rgba(255, 255, 255, 0.7)', fontStyle: 'italic' }}>
            ✨ Personalized {displaySource}
          </div>
        </div>
      }
      arrow
      placement="top"
    >
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          cursor: 'help',
          marginLeft: '6px',
          color: '#0ea5e9',
        }}
      >
        <AutoAwesome sx={{ fontSize: 14, color: '#0ea5e9' }} />
      </span>
    </Tooltip>
  );
};

interface PersonalizationBadgeProps {
  label: string;
  source: string;
  compact?: boolean;
}

export const PersonalizationBadge: React.FC<PersonalizationBadgeProps> = ({
  label,
  source,
  compact = false
}) => {
  return (
    <Tooltip
      title={`Personalized ${source} - This is customized based on your research persona and website analysis`}
      arrow
      placement="top"
    >
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          padding: compact ? '2px 6px' : '4px 8px',
          background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
          border: '1px solid rgba(14, 165, 233, 0.2)',
          borderRadius: '6px',
          fontSize: compact ? '10px' : '11px',
          color: '#0369a1',
          fontWeight: 500,
          cursor: 'help',
        }}
      >
        <AutoAwesome sx={{ fontSize: compact ? 12 : 14, color: '#0ea5e9' }} />
        <span>{label}</span>
      </div>
    </Tooltip>
  );
};
