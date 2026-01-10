import React from 'react';
import { ResearchConfig } from '../../../../services/researchApi';
import { exaCategories, exaSearchTypes } from '../utils/constants';
import { OptimizedConfig } from '../../types/intent.types';
import { Tooltip } from '@mui/material';
import { exaOptionTooltips } from './utils/exaTooltips';

interface ExaOptionsProps {
  config: ResearchConfig;
  onConfigUpdate: (updates: Partial<ResearchConfig>) => void;
  optimizedConfig?: OptimizedConfig; // AI-optimized config with justifications
}

export const ExaOptions: React.FC<ExaOptionsProps> = ({ config, onConfigUpdate, optimizedConfig }) => {
  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onConfigUpdate({ exa_category: value || undefined });
  };

  const handleSearchTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as 'auto' | 'keyword' | 'neural' | 'fast' | 'deep';
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

  const handleNumResultsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1 && value <= 100) {
      onConfigUpdate({ exa_num_results: value });
    }
  };

  const handleDateFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Convert YYYY-MM-DD to ISO format if needed
    const isoDate = value ? `${value}T00:00:00.000Z` : undefined;
    onConfigUpdate({ exa_date_filter: isoDate || undefined });
  };

  const handleEndPublishedDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const isoDate = value ? `${value}T23:59:59.999Z` : undefined;
    onConfigUpdate({ exa_end_published_date: isoDate || undefined });
  };

  const handleStartCrawlDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const isoDate = value ? `${value}T00:00:00.000Z` : undefined;
    onConfigUpdate({ exa_start_crawl_date: isoDate || undefined });
  };

  const handleEndCrawlDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const isoDate = value ? `${value}T23:59:59.999Z` : undefined;
    onConfigUpdate({ exa_end_crawl_date: isoDate || undefined });
  };

  const handleIncludeTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Only one string supported, up to 5 words
    const words = value.trim().split(/\s+/).filter(Boolean).slice(0, 5);
    onConfigUpdate({ exa_include_text: words.length > 0 ? [words.join(' ')] : undefined });
  };

  const handleExcludeTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Only one string supported, up to 5 words
    const words = value.trim().split(/\s+/).filter(Boolean).slice(0, 5);
    onConfigUpdate({ exa_exclude_text: words.length > 0 ? [words.join(' ')] : undefined });
  };

  const handleHighlightsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ exa_highlights: e.target.checked });
  };

  const handleHighlightsNumSentencesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1) {
      onConfigUpdate({ exa_highlights_num_sentences: value });
    }
  };

  const handleHighlightsPerUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1) {
      onConfigUpdate({ exa_highlights_per_url: value });
    }
  };

  const handleContextMaxCharactersChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value > 0) {
      onConfigUpdate({ 
        exa_context: true,
        exa_context_max_characters: value 
      });
    } else if (value === 0 || e.target.value === '') {
      onConfigUpdate({ 
        exa_context: false,
        exa_context_max_characters: undefined 
      });
    }
  };

  const handleTextMaxCharactersChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value > 0) {
      onConfigUpdate({ exa_text_max_characters: value });
    } else if (e.target.value === '') {
      onConfigUpdate({ exa_text_max_characters: undefined });
    }
  };

  const handleSummaryQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.trim();
    onConfigUpdate({ exa_summary_query: value || undefined });
  };

  const handleContextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ exa_context: e.target.checked });
  };

  const handleAdditionalQueriesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    // Parse comma or newline-separated queries
    const queries = value
      .split(/[,\n]/)
      .map(q => q.trim())
      .filter(Boolean);
    onConfigUpdate({ exa_additional_queries: queries.length > 0 ? queries : undefined });
  };

  // Get AI justification for a field
  const getJustification = (field: string): string | undefined => {
    if (!optimizedConfig) return undefined;
    const justificationKey = `exa_${field}_justification` as keyof OptimizedConfig;
    return optimizedConfig[justificationKey] as string | undefined;
  };

  // Get detailed tooltip content for a field
  const getTooltipContent = (field: string): string => {
    const aiJustification = getJustification(field);
    const tooltipKey = field as keyof typeof exaOptionTooltips;
    const baseTooltip = exaOptionTooltips[tooltipKey];
    
    if (!baseTooltip) {
      // Fallback to AI justification if no base tooltip
      return aiJustification || '';
    }
    
    let tooltip = '';
    
    switch (field) {
      case 'category':
        const categoryTooltip = baseTooltip as any;
        tooltip = `${baseTooltip.description}\n\nExamples:\n${Object.entries(categoryTooltip.examples || {}).map(([key, val]) => `• ${key}: ${val}`).join('\n')}`;
        break;
      case 'searchType':
        const selectedType = config.exa_search_type || 'auto';
        const searchTypeTooltip = baseTooltip as any;
        const types = searchTypeTooltip.types;
        const typeInfo = types?.[selectedType];
        if (typeInfo) {
          tooltip = `${typeInfo.description}\n\nWhen to use: ${typeInfo.whenToUse}`;
          if (typeInfo.latency) tooltip += `\n\nLatency: ${typeInfo.latency}`;
          if (typeInfo.quality) tooltip += `\n\nQuality: ${typeInfo.quality}`;
          if (typeInfo.limits) tooltip += `\n\nLimits: ${typeInfo.limits}`;
          if (typeInfo.note) tooltip += `\n\nNote: ${typeInfo.note}`;
        } else {
          tooltip = baseTooltip.description || '';
        }
        break;
      case 'numResults':
        tooltip = `${baseTooltip.description}\n\n${(baseTooltip as any).limits || ''}\n\nRecommendations:\n${Object.entries((baseTooltip as any).recommendations || {}).map(([key, val]) => `• ${key} results: ${val}`).join('\n')}`;
        break;
      case 'dateFilter':
      case 'endPublishedDate':
      case 'startCrawlDate':
      case 'endCrawlDate':
      case 'includeText':
      case 'excludeText':
      case 'highlightsNumSentences':
      case 'highlightsPerUrl':
      case 'contextMaxCharacters':
      case 'textMaxCharacters':
      case 'summaryQuery':
        tooltip = `${baseTooltip.description}\n\nWhen to use:\n${((baseTooltip as any).whenToUse || []).map((u: string) => `• ${u}`).join('\n')}\n\n${(baseTooltip as any).format || ''}\n\nExample: ${(baseTooltip as any).example || ''}\n\n${(baseTooltip as any).recommendation || ''}\n\n${(baseTooltip as any).limit || ''}\n\n${(baseTooltip as any).note || ''}`;
        break;
      case 'highlights':
        tooltip = `${baseTooltip.description}\n\nBenefits:\n${((baseTooltip as any).benefits || []).map((b: string) => `• ${b}`).join('\n')}\n\n${(baseTooltip as any).whenToUse || ''}`;
        break;
      case 'context':
        tooltip = `${baseTooltip.description}\n\nBenefits:\n${((baseTooltip as any).benefits || []).map((b: string) => `• ${b}`).join('\n')}\n\n${(baseTooltip as any).whenToUse || ''}\n\n${(baseTooltip as any).recommendation || ''}`;
        break;
      case 'includeDomains':
        tooltip = `${baseTooltip.description}\n\nWhen to use:\n${((baseTooltip as any).whenToUse || []).map((u: string) => `• ${u}`).join('\n')}\n\n${(baseTooltip as any).format || ''}\n\nExample: ${(baseTooltip as any).example || ''}\n\n${(baseTooltip as any).limit || ''}`;
        break;
      case 'excludeDomains':
        tooltip = `${baseTooltip.description}\n\nWhen to use:\n${((baseTooltip as any).whenToUse || []).map((u: string) => `• ${u}`).join('\n')}\n\n${(baseTooltip as any).format || ''}\n\nExample: ${(baseTooltip as any).example || ''}\n\n${(baseTooltip as any).limit || ''}`;
        break;
      case 'dateFilter':
      case 'endPublishedDate':
      case 'startCrawlDate':
      case 'endCrawlDate':
        tooltip = `${baseTooltip.description}\n\nWhen to use:\n${((baseTooltip as any).whenToUse || []).map((u: string) => `• ${u}`).join('\n')}\n\n${(baseTooltip as any).format || ''}\n\nExample: ${(baseTooltip as any).example || ''}\n\n${(baseTooltip as any).note || ''}`;
        break;
      default:
        tooltip = (baseTooltip as any).description || '';
    }
    
    // Append AI justification if available
    if (aiJustification) {
      tooltip += `\n\n🤖 AI Recommendation: ${aiJustification}`;
    }
    
    return tooltip;
  };

  // Format date for input (YYYY-MM-DD from ISO string)
  const formatDateForInput = (isoDate?: string): string => {
    if (!isoDate) return '';
    try {
      const date = new Date(isoDate);
      return date.toISOString().split('T')[0];
    } catch {
      return '';
    }
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
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Content Category
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('category')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
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
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Search Algorithm
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('searchType')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
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

        {/* Number of Results */}
        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Number of Results
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('numResults')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="number"
            min="1"
            max="100"
            value={config.exa_num_results || optimizedConfig?.exa_num_results || 10}
            onChange={handleNumResultsChange}
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

        {/* Date Filters - Published Dates */}
        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Start Published Date (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('dateFilter')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="date"
            value={formatDateForInput(config.exa_date_filter || optimizedConfig?.exa_date_filter)}
            onChange={handleDateFilterChange}
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
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            End Published Date (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('endPublishedDate')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="date"
            value={formatDateForInput(config.exa_end_published_date)}
            onChange={handleEndPublishedDateChange}
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

      {/* Crawl Date Filters */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginTop: '12px',
      }}>
        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Start Crawl Date (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('startCrawlDate')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="date"
            value={formatDateForInput(config.exa_start_crawl_date)}
            onChange={handleStartCrawlDateChange}
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
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            End Crawl Date (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('endCrawlDate')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="date"
            value={formatDateForInput(config.exa_end_crawl_date)}
            onChange={handleEndCrawlDateChange}
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

      {/* Text Filters */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginTop: '12px',
      }}>
        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Include Text (optional, max 5 words)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('includeText')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="text"
            value={config.exa_include_text?.[0] || ''}
            onChange={handleIncludeTextChange}
            placeholder="e.g., large language model"
            maxLength={50}
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
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Exclude Text (optional, max 5 words)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('excludeText')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="text"
            value={config.exa_exclude_text?.[0] || ''}
            onChange={handleExcludeTextChange}
            placeholder="e.g., course tutorial"
            maxLength={50}
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

      {/* Boolean Options Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginTop: '12px',
        marginBottom: '12px',
      }}>
        {/* Highlights */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          borderRadius: '8px',
          background: 'rgba(255, 255, 255, 0.9)',
        }}>
          <input
            type="checkbox"
            checked={config.exa_highlights ?? optimizedConfig?.exa_highlights ?? true}
            onChange={handleHighlightsChange}
            style={{
              cursor: 'pointer',
            }}
          />
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
            cursor: 'pointer',
            flex: 1,
          }}>
            Extract Highlights
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('highlights')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
        </div>

        {/* Context */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          borderRadius: '8px',
          background: 'rgba(255, 255, 255, 0.9)',
        }}>
          <input
            type="checkbox"
            checked={typeof config.exa_context === 'object' ? true : (config.exa_context ?? (typeof optimizedConfig?.exa_context === 'object' ? true : optimizedConfig?.exa_context ?? true))}
            onChange={handleContextChange}
            style={{
              cursor: 'pointer',
            }}
          />
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
            cursor: 'pointer',
            flex: 1,
          }}>
            Return Context String
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('context')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
        </div>
      </div>

      {/* Configurable Contents Options */}
      {config.exa_highlights && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          marginTop: '12px',
        }}>
          <div>
            <label style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              marginBottom: '6px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b21a8',
            }}>
              Highlights: Sentences Per Snippet
              <Tooltip 
                title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('highlightsNumSentences')}</div>} 
                arrow
                placement="top"
              >
                <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
              </Tooltip>
            </label>
            <input
              type="number"
              min="1"
              value={config.exa_highlights_num_sentences || 2}
              onChange={handleHighlightsNumSentencesChange}
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
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              marginBottom: '6px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b21a8',
            }}>
              Highlights: Snippets Per URL
              <Tooltip 
                title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('highlightsPerUrl')}</div>} 
                arrow
                placement="top"
              >
                <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
              </Tooltip>
            </label>
            <input
              type="number"
              min="1"
              value={config.exa_highlights_per_url || 3}
              onChange={handleHighlightsPerUrlChange}
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
      )}

      {config.exa_context && (
        <div style={{
          marginTop: '12px',
        }}>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Context: Max Characters (optional, recommended 10,000+)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('contextMaxCharacters')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="number"
            min="0"
            value={config.exa_context_max_characters || ''}
            onChange={handleContextMaxCharactersChange}
            placeholder="Leave empty for no limit (recommended)"
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
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginTop: '12px',
      }}>
        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Text: Max Characters (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('textMaxCharacters')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="number"
            min="0"
            value={config.exa_text_max_characters || 1000}
            onChange={handleTextMaxCharactersChange}
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
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Summary: Custom Query (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('summaryQuery')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <input
            type="text"
            value={config.exa_summary_query || ''}
            onChange={handleSummaryQueryChange}
            placeholder="e.g., Key insights about..."
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

      {/* Additional Queries for Deep Search */}
      {config.exa_search_type === 'deep' && (
        <div style={{ marginBottom: '12px' }}>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Additional Query Variations (Deep Search Only)
            <Tooltip 
              title={
                <div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>
                  Provide 2-3 query variations to expand your Deep search. These queries are used alongside the main query for comprehensive results. Deep search will auto-generate variations if not provided.
                  {'\n\n'}
                  Example:
                  {'\n'}• LLM advancements
                  {'\n'}• large language model progress
                  {'\n'}• recent AI breakthroughs
                  {optimizedConfig?.exa_additional_queries_justification && `\n\n🤖 AI Recommendation: ${optimizedConfig.exa_additional_queries_justification}`}
                </div>
              } 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
          </label>
          <textarea
            value={config.exa_additional_queries?.join(', ') || ''}
            onChange={handleAdditionalQueriesChange}
            placeholder="Enter query variations separated by commas or new lines (e.g., LLM advancements, large language model progress)"
            rows={3}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              fontFamily: 'inherit',
              resize: 'vertical',
            }}
          />
          {optimizedConfig?.exa_additional_queries && optimizedConfig.exa_additional_queries.length > 0 && (
            <div style={{
              marginTop: '6px',
              padding: '6px 8px',
              backgroundColor: '#f0fdf4',
              border: '1px solid #86efac',
              borderRadius: '6px',
              fontSize: '11px',
              color: '#166534',
            }}>
              <strong>AI Suggested:</strong> {optimizedConfig.exa_additional_queries.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Domain Filters */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
      }}>
        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Include Domains (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('includeDomains')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
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
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b21a8',
          }}>
            Exclude Domains (optional)
            <Tooltip 
              title={<div style={{ whiteSpace: 'pre-line', fontSize: '12px', lineHeight: '1.5' }}>{getTooltipContent('excludeDomains')}</div>} 
              arrow
              placement="top"
            >
              <span style={{ fontSize: '10px', color: '#0ea5e9', cursor: 'help' }}>ℹ️</span>
            </Tooltip>
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

