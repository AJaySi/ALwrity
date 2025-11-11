import React from 'react';
import { ProviderAvailability } from '../../../../api/researchConfig';
import { industries } from '../utils/constants';

interface ResearchControlsBarProps {
  industry: string;
  providerAvailability: ProviderAvailability | null;
  onIndustryChange: (industry: string) => void;
}

export const ResearchControlsBar: React.FC<ResearchControlsBarProps> = ({
  industry,
  providerAvailability,
  onIndustryChange,
}) => {
  const dropdownStyle = {
    minWidth: '130px',
    padding: '7px 28px 7px 10px',
    fontSize: '12px',
    border: '1px solid rgba(15, 23, 42, 0.1)',
    borderRadius: '8px',
    background: '#ffffff',
    color: '#0f172a',
    cursor: 'pointer',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif',
    fontWeight: '500',
    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)',
    appearance: 'none' as const,
    WebkitAppearance: 'none' as const,
    MozAppearance: 'none' as const,
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'%3E%3Cpath fill='%23475569' d='M5 7L1 3h8z'/%3E%3C/svg%3E")`,
    backgroundRepeat: 'no-repeat' as const,
    backgroundPosition: 'right 9px center',
    backgroundSize: '10px 10px',
  };

  const handleFocus = (e: React.FocusEvent<HTMLSelectElement>) => {
    e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
    e.currentTarget.style.boxShadow = '0 0 0 2px rgba(14, 165, 233, 0.08), 0 1px 3px rgba(0, 0, 0, 0.08)';
    e.currentTarget.style.background = '#ffffff';
    e.currentTarget.style.backgroundImage = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'%3E%3Cpath fill='%230ea5e9' d='M5 7L1 3h8z'/%3E%3C/svg%3E")`;
    e.currentTarget.style.backgroundSize = '10px 10px';
  };

  const handleBlur = (e: React.FocusEvent<HTMLSelectElement>) => {
    e.currentTarget.style.borderColor = 'rgba(15, 23, 42, 0.1)';
    e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.04)';
    e.currentTarget.style.background = '#ffffff';
    e.currentTarget.style.backgroundImage = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'%3E%3Cpath fill='%23475569' d='M5 7L1 3h8z'/%3E%3C/svg%3E")`;
    e.currentTarget.style.backgroundSize = '10px 10px';
  };

  const handleMouseEnter = (e: React.MouseEvent<HTMLSelectElement>) => {
    e.currentTarget.style.borderColor = 'rgba(15, 23, 42, 0.15)';
    e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.06)';
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLSelectElement>) => {
    if (document.activeElement !== e.currentTarget) {
      e.currentTarget.style.borderColor = 'rgba(15, 23, 42, 0.1)';
      e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.04)';
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-end',
      gap: '10px',
      paddingTop: '16px',
      marginTop: '16px',
      borderTop: '1px solid rgba(14, 165, 233, 0.15)',
      flexWrap: 'wrap',
    }}>
      {/* Compact Dropdowns - Stacked Horizontally */}
      <div style={{
        display: 'flex',
        flexDirection: 'row',
        gap: '10px',
        alignItems: 'center',
        flexWrap: 'wrap',
      }}>
        {/* Industry Dropdown */}
        <select
          value={industry}
          onChange={(e) => onIndustryChange(e.target.value)}
          title="Select industry for targeted research"
          style={dropdownStyle}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {industries.map(ind => (
            <option key={ind} value={ind}>{ind}</option>
          ))}
        </select>

      </div>
    </div>
  );
};

