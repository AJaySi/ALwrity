import React from 'react';
import { ResearchConfig } from '../../../../services/blogWriterApi';
import { 
  tavilyTopics, 
  tavilySearchDepths, 
  tavilyTimeRanges, 
  tavilyAnswerOptions, 
  tavilyRawContentOptions 
} from '../utils/constants';

interface TavilyOptionsProps {
  config: ResearchConfig;
  onConfigUpdate: (updates: Partial<ResearchConfig>) => void;
}

export const TavilyOptions: React.FC<TavilyOptionsProps> = ({ config, onConfigUpdate }) => {
  const handleTopicChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as 'general' | 'news' | 'finance';
    onConfigUpdate({ tavily_topic: value || 'general' });
  };

  const handleSearchDepthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as 'basic' | 'advanced';
    onConfigUpdate({ tavily_search_depth: value });
  };

  const handleIncludeDomainsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const domains = value.split(',').map(d => d.trim()).filter(Boolean);
    onConfigUpdate({ tavily_include_domains: domains });
  };

  const handleExcludeDomainsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const domains = value.split(',').map(d => d.trim()).filter(Boolean);
    onConfigUpdate({ tavily_exclude_domains: domains });
  };

  const handleIncludeAnswerChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    let answerValue: boolean | 'basic' | 'advanced';
    if (value === 'true') {
      answerValue = true;
    } else if (value === 'false') {
      answerValue = false;
    } else {
      answerValue = value as 'basic' | 'advanced';
    }
    onConfigUpdate({ tavily_include_answer: answerValue });
  };

  const handleTimeRangeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const timeRangeValue = value ? (value as 'day' | 'week' | 'month' | 'year' | 'd' | 'w' | 'm' | 'y') : undefined;
    onConfigUpdate({ tavily_time_range: timeRangeValue });
  };

  const handleIncludeRawContentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    let rawContentValue: boolean | 'markdown' | 'text';
    if (value === 'true') {
      rawContentValue = true;
    } else if (value === 'false') {
      rawContentValue = false;
    } else {
      rawContentValue = value as 'markdown' | 'text';
    }
    onConfigUpdate({ tavily_include_raw_content: rawContentValue });
  };

  const handleIncludeImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ tavily_include_images: e.target.checked });
  };

  const handleIncludeImageDescriptionsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ tavily_include_image_descriptions: e.target.checked });
  };

  const handleIncludeFaviconChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ tavily_include_favicon: e.target.checked });
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ tavily_start_date: e.target.value || undefined });
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ tavily_end_date: e.target.value || undefined });
  };

  const handleCountryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ tavily_country: e.target.value || undefined });
  };

  const handleChunksPerSourceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1 && value <= 3) {
      onConfigUpdate({ tavily_chunks_per_source: value });
    }
  };

  const handleAutoParametersChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onConfigUpdate({ tavily_auto_parameters: e.target.checked });
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
      border: '2px solid rgba(14, 165, 233, 0.3)',
      borderRadius: '12px',
      padding: '16px',
      marginBottom: '14px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '14px',
      }}>
        <span style={{ fontSize: '18px' }}>🤖</span>
        <strong style={{ color: '#0ea5e9', fontSize: '13px' }}>Tavily AI Search Options</strong>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
        marginBottom: '12px',
      }}>
        {/* Tavily Topic */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#0ea5e9',
          }}>
            Search Topic
          </label>
          <select
            value={config.tavily_topic || 'general'}
            onChange={handleTopicChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
            }}
          >
            {tavilyTopics.map(topic => (
              <option key={topic.value} value={topic.value}>{topic.label}</option>
            ))}
          </select>
        </div>

        {/* Tavily Search Depth */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#0ea5e9',
          }}>
            Search Depth
          </label>
          <select
            value={config.tavily_search_depth || 'basic'}
            onChange={handleSearchDepthChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
            }}
          >
            {tavilySearchDepths.map(depth => (
              <option key={depth.value} value={depth.value}>{depth.label}</option>
            ))}
          </select>
        </div>

        {/* Tavily Include Answer */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#0ea5e9',
          }}>
            AI Answer
          </label>
          <select
            value={config.tavily_include_answer === true ? 'true' : typeof config.tavily_include_answer === 'string' ? config.tavily_include_answer : 'false'}
            onChange={handleIncludeAnswerChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
            }}
          >
            {tavilyAnswerOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Tavily Time Range */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#0ea5e9',
          }}>
            Time Range
          </label>
          <select
            value={config.tavily_time_range || ''}
            onChange={handleTimeRangeChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
            }}
          >
            {tavilyTimeRanges.map(range => (
              <option key={range.value} value={range.value}>{range.label}</option>
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
            color: '#0ea5e9',
          }}>
            Include Domains (optional)
          </label>
          <input
            type="text"
            value={config.tavily_include_domains?.join(', ') || ''}
            onChange={handleIncludeDomainsChange}
            placeholder="e.g., nature.com, arxiv.org"
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
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
            color: '#0ea5e9',
          }}>
            Exclude Domains (optional)
          </label>
          <input
            type="text"
            value={config.tavily_exclude_domains?.join(', ') || ''}
            onChange={handleExcludeDomainsChange}
            placeholder="e.g., spam.com, ads.com"
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
            }}
          />
        </div>
      </div>

      {/* Additional Tavily Options */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px',
        marginTop: '12px',
      }}>
        {/* Include Raw Content */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#0ea5e9',
          }}>
            Raw Content Format
          </label>
          <select
            value={config.tavily_include_raw_content === true ? 'true' : typeof config.tavily_include_raw_content === 'string' ? config.tavily_include_raw_content : 'false'}
            onChange={handleIncludeRawContentChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
            }}
          >
            {tavilyRawContentOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Country */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#0ea5e9',
          }}>
            Country Code (optional)
          </label>
          <input
            type="text"
            value={config.tavily_country || ''}
            onChange={handleCountryChange}
            placeholder="e.g., US, GB, IN"
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
            }}
          />
        </div>

        {/* Chunks Per Source (only for advanced) */}
        {config.tavily_search_depth === 'advanced' && (
          <div>
            <label style={{
              display: 'block',
              marginBottom: '6px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#0ea5e9',
            }}>
              Chunks Per Source (1-3)
            </label>
            <input
              type="number"
              min="1"
              max="3"
              value={config.tavily_chunks_per_source || 3}
              onChange={handleChunksPerSourceChange}
              style={{
                width: '100%',
                padding: '8px 10px',
                fontSize: '12px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.9)',
                color: '#0f172a',
              }}
            />
          </div>
        )}
      </div>

      {/* Date Range */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginTop: '12px',
      }}>
        <div>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#0ea5e9',
          }}>
            Start Date (YYYY-MM-DD)
          </label>
          <input
            type="date"
            value={config.tavily_start_date || ''}
            onChange={handleStartDateChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
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
            color: '#0ea5e9',
          }}>
            End Date (YYYY-MM-DD)
          </label>
          <input
            type="date"
            value={config.tavily_end_date || ''}
            onChange={handleEndDateChange}
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
            }}
          />
        </div>
      </div>

      {/* Checkboxes */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px',
        marginTop: '12px',
      }}>
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: '#0ea5e9',
          cursor: 'pointer',
        }}>
          <input
            type="checkbox"
            checked={config.tavily_include_images || false}
            onChange={handleIncludeImagesChange}
            style={{
              width: '16px',
              height: '16px',
              cursor: 'pointer',
            }}
          />
          <span>Include Images</span>
        </label>

        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: '#0ea5e9',
          cursor: 'pointer',
        }}>
          <input
            type="checkbox"
            checked={config.tavily_include_image_descriptions || false}
            onChange={handleIncludeImageDescriptionsChange}
            disabled={!config.tavily_include_images}
            style={{
              width: '16px',
              height: '16px',
              cursor: config.tavily_include_images ? 'pointer' : 'not-allowed',
              opacity: config.tavily_include_images ? 1 : 0.5,
            }}
          />
          <span>Include Image Descriptions</span>
        </label>

        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: '#0ea5e9',
          cursor: 'pointer',
        }}>
          <input
            type="checkbox"
            checked={config.tavily_include_favicon || false}
            onChange={handleIncludeFaviconChange}
            style={{
              width: '16px',
              height: '16px',
              cursor: 'pointer',
            }}
          />
          <span>Include Favicon URLs</span>
        </label>

        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: '#0ea5e9',
          cursor: 'pointer',
        }}>
          <input
            type="checkbox"
            checked={config.tavily_auto_parameters || false}
            onChange={handleAutoParametersChange}
            style={{
              width: '16px',
              height: '16px',
              cursor: 'pointer',
            }}
          />
          <span>Auto-Configure Parameters</span>
        </label>
      </div>
    </div>
  );
};

