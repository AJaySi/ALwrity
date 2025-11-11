import React, { useState } from 'react';
import { ProviderAvailability } from '../../../../api/researchConfig';

interface ProviderChipsProps {
  providerAvailability: ProviderAvailability | null;
  advanced?: boolean;
}

export const ProviderChips: React.FC<ProviderChipsProps> = ({ providerAvailability, advanced = false }) => {
  const [hoveredChip, setHoveredChip] = useState<string | null>(null);

  if (!providerAvailability) return null;

  const providers = [
    {
      id: 'google',
      name: 'Google',
      available: providerAvailability.google_available,
      status: providerAvailability.gemini_key_status,
      icon: '🔍',
      tooltip: 'Google Search powered by Gemini AI. Provides comprehensive web search results with semantic understanding and real-time information from across the web.',
      color: providerAvailability.google_available 
        ? 'linear-gradient(135deg, rgba(66, 133, 244, 0.15) 0%, rgba(52, 168, 83, 0.15) 100%)'
        : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%)',
      borderColor: providerAvailability.google_available 
        ? 'rgba(66, 133, 244, 0.3)'
        : 'rgba(239, 68, 68, 0.2)',
      textColor: providerAvailability.google_available ? '#4285f4' : '#ef4444',
    },
    {
      id: 'exa',
      name: 'Exa',
      available: providerAvailability.exa_available,
      status: providerAvailability.exa_key_status,
      icon: '🧠',
      tooltip: 'Exa Neural Search. Advanced semantic search engine that understands context and meaning, providing highly relevant results through neural network-powered query understanding.',
      // Show green when advanced is ON and available, red when advanced is OFF or not available
      isAdvanced: true,
      color: (advanced && providerAvailability.exa_available)
        ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)'
        : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%)',
      borderColor: (advanced && providerAvailability.exa_available)
        ? 'rgba(16, 185, 129, 0.3)'
        : 'rgba(239, 68, 68, 0.2)',
      textColor: (advanced && providerAvailability.exa_available) ? '#10b981' : '#ef4444',
      chipStatus: (advanced && providerAvailability.exa_available) ? '#10b981' : '#ef4444',
    },
    {
      id: 'tavily',
      name: 'Tavily',
      available: providerAvailability.tavily_available,
      status: providerAvailability.tavily_key_status,
      icon: '🤖',
      tooltip: 'Tavily AI Research Engine. Specialized AI-powered research tool designed for comprehensive content discovery, providing deep insights and structured research data from multiple sources.',
      // Show green when advanced is ON and available, red when advanced is OFF or not available
      isAdvanced: true,
      color: (advanced && providerAvailability.tavily_available)
        ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)'
        : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%)',
      borderColor: (advanced && providerAvailability.tavily_available)
        ? 'rgba(16, 185, 129, 0.3)'
        : 'rgba(239, 68, 68, 0.2)',
      textColor: (advanced && providerAvailability.tavily_available) ? '#10b981' : '#ef4444',
      chipStatus: (advanced && providerAvailability.tavily_available) ? '#10b981' : '#ef4444',
    },
  ];

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginLeft: '16px',
    }}>
      {providers.map((provider) => {
        const isHovered = hoveredChip === provider.id;
        return (
          <div
            key={provider.id}
            style={{
              position: 'relative',
            }}
            onMouseEnter={() => setHoveredChip(provider.id)}
            onMouseLeave={() => setHoveredChip(null)}
          >
            {/* Chip */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                background: provider.color,
                border: `1px solid ${provider.borderColor}`,
                borderRadius: '12px',
                fontSize: '11px',
                fontWeight: '600',
                color: provider.textColor,
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                cursor: 'default',
                boxShadow: isHovered 
                  ? '0 2px 8px rgba(0, 0, 0, 0.12)' 
                  : '0 1px 3px rgba(0, 0, 0, 0.08)',
                transform: isHovered ? 'translateY(-1px)' : 'translateY(0)',
                letterSpacing: '-0.01em',
              }}
            >
              <span style={{ fontSize: '13px' }}>{provider.icon}</span>
              <span>{provider.name}</span>
              <span style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: (provider as any).chipStatus || (provider.available ? '#10b981' : '#ef4444'),
                boxShadow: ((provider as any).chipStatus === '#10b981') || (provider.available && !(provider as any).isAdvanced)
                  ? '0 0 4px rgba(16, 185, 129, 0.4)' 
                  : '0 0 4px rgba(239, 68, 68, 0.4)',
              }} />
            </div>

            {/* Tooltip */}
            {isHovered && (
              <div
                style={{
                  position: 'absolute',
                  top: '100%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  marginTop: '8px',
                  padding: '10px 12px',
                  background: 'rgba(15, 23, 42, 0.95)',
                  color: '#f8fafc',
                  fontSize: '11px',
                  lineHeight: '1.5',
                  borderRadius: '8px',
                  maxWidth: '280px',
                  zIndex: 1000,
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.25)',
                  pointerEvents: 'none',
                  whiteSpace: 'normal',
                  wordWrap: 'break-word',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                }}
              >
                {provider.tooltip}
                <div
                  style={{
                    position: 'absolute',
                    top: '-4px',
                    left: '50%',
                    transform: 'translateX(-50%) rotate(45deg)',
                    width: '8px',
                    height: '8px',
                    background: 'rgba(15, 23, 42, 0.95)',
                    borderLeft: '1px solid rgba(255, 255, 255, 0.1)',
                    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                  }}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

