import React from 'react';
import { ProviderAvailability } from '../../../../api/researchConfig';

interface ProviderStatusProps {
  providerAvailability: ProviderAvailability | null;
}

export const ProviderStatus: React.FC<ProviderStatusProps> = ({ providerAvailability }) => {
  if (!providerAvailability) return null;

  return (
    <div style={{
      marginBottom: '20px',
      padding: '10px 14px',
      background: 'rgba(241, 245, 249, 0.5)',
      border: '1px solid rgba(203, 213, 225, 0.3)',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      fontSize: '11px',
      color: '#64748b',
      flexWrap: 'wrap',
    }}>
      <span style={{ fontWeight: '600', color: '#475569' }}>Provider Status:</span>
      <span style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
      }}>
        <span style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: providerAvailability.google_available ? '#10b981' : '#ef4444',
        }} />
        <span>Google: {providerAvailability.gemini_key_status}</span>
      </span>
      <span style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
      }}>
        <span style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: providerAvailability.exa_available ? '#10b981' : '#ef4444',
        }} />
        <span>Exa: {providerAvailability.exa_key_status}</span>
      </span>
      <span style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
      }}>
        <span style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: providerAvailability.tavily_available ? '#10b981' : '#ef4444',
        }} />
        <span>Tavily: {providerAvailability.tavily_key_status}</span>
      </span>
    </div>
  );
};

