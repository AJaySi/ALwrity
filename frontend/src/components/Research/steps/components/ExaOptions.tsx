import React from 'react';
import { ResearchConfig } from '../../../../services/blogWriterApi';
import { exaCategories, exaSearchTypes } from '../utils/constants';

interface ExaOptionsProps {
  config: ResearchConfig;
  onConfigUpdate: (updates: Partial<ResearchConfig>) => void;
}

export const ExaOptions: React.FC<ExaOptionsProps> = ({ config, onConfigUpdate }) => {
  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onConfigUpdate({ exa_category: value || undefined });
  };

  const handleSearchTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as 'auto' | 'keyword' | 'neural';
    onConfigUpdate({ exa_search_type: value });
  };

  const handleIncludeDomainsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const domains = value.split(',').map(d => d.trim()).filter(Boolean);
    onConfigUpdate({ exa_include_domains: domains });
  };

  const handleExcludeDomainsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const domains = value.split(',').map(d => d.trim()).filter(Boolean);
    onConfigUpdate({ exa_exclude_domains: domains });
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(99, 102, 241, 0.05) 100%)',
      border: '1px solid rgba(139, 92, 246, 0.2)',
      borderRadius: '14px',
      padding: '16px',
      marginBottom: '20px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '14px',
      }}>
        <span style={{ fontSize: '18px' }}>🧠</span>
        <strong style={{ color: '#6b21a8', fontSize: '13px' }}>Exa Neural Search Options</strong>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
        marginBottom: '12px',
      }}>
        {/* Exa Category */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Content Category
          </label>
          <select
            value={config.exa_category || ''}
            onChange={handleCategoryChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
            }}
          >
            {exaCategories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        {/* Exa Search Type */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Search Algorithm
          </label>
          <select
            value={config.exa_search_type || 'auto'}
            onChange={handleSearchTypeChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
            }}
          >
            {exaSearchTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Domain Filters */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
      }}>
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Include Domains (optional)
          </label>
          <input
            type="text"
            value={config.exa_include_domains?.join(', ') || ''}
            onChange={handleIncludeDomainsChange}
            placeholder="e.g., nature.com, arxiv.org"
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
            }}
          />
        </div>

        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Exclude Domains (optional)
          </label>
          <input
            type="text"
            value={config.exa_exclude_domains?.join(', ') || ''}
            onChange={handleExcludeDomainsChange}
            placeholder="e.g., spam.com, ads.com"
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
            }}
          />
        </div>
      </div>
    </div>
  );
};

