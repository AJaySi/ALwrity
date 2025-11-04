import React, { useRef, useState, useEffect } from 'react';
import { WizardStepProps } from '../types/research.types';
import { ResearchProvider } from '../../../services/blogWriterApi';

const industries = [
  'General',
  'Technology',
  'Business',
  'Marketing',
  'Finance',
  'Healthcare',
  'Education',
  'Real Estate',
  'Entertainment',
  'Food & Beverage',
  'Travel',
  'Fashion',
  'Sports',
  'Science',
  'Law',
  'Other',
];

const researchModes = [
  { value: 'basic', label: 'Basic - Quick insights' },
  { value: 'comprehensive', label: 'Comprehensive - In-depth analysis' },
  { value: 'targeted', label: 'Targeted - Specific focus' },
];

const providers = [
  { value: 'google', label: '🔍 Google Search' },
  { value: 'exa', label: '🧠 Exa Neural Search' },
];

const exaCategories = [
  { value: '', label: 'All Categories' },
  { value: 'company', label: 'Company Profiles' },
  { value: 'research paper', label: 'Research Papers' },
  { value: 'news', label: 'News Articles' },
  { value: 'linkedin profile', label: 'LinkedIn Profiles' },
  { value: 'github', label: 'GitHub Repos' },
  { value: 'tweet', label: 'Tweets' },
  { value: 'movie', label: 'Movies' },
  { value: 'song', label: 'Songs' },
  { value: 'personal site', label: 'Personal Sites' },
  { value: 'pdf', label: 'PDF Documents' },
  { value: 'financial report', label: 'Financial Reports' },
];

const exaSearchTypes = [
  { value: 'auto', label: 'Auto - Let AI decide' },
  { value: 'keyword', label: 'Keyword - Precise matching' },
  { value: 'neural', label: 'Neural - Semantic search' },
];

// Dynamic placeholder examples showcasing research capabilities
const placeholderExamples = [
  "AI-powered content marketing strategies for SaaS startups\n\nExplores:\n• Latest automation tools and platforms\n• ROI optimization techniques\n• Multi-channel campaign orchestration\n• Data-driven personalization strategies",
  "Sustainable supply chain management in manufacturing\n\nCovers:\n• Green logistics and carbon footprint reduction\n• Blockchain for transparency and traceability\n• Circular economy implementation frameworks\n• Real-time inventory optimization with AI",
  "Emerging trends in telemedicine and remote patient monitoring\n\nIncludes:\n• Wearable device integration and IoT sensors\n• HIPAA-compliant data transmission protocols\n• AI-assisted diagnostic accuracy improvements\n• Patient engagement and adherence strategies",
  "Cryptocurrency regulation and institutional adoption\n\nAnalyzes:\n• Global regulatory frameworks and compliance\n• Institutional investment trends (2024-2025)\n• DeFi integration with traditional finance\n• Risk management and security best practices",
  "Voice search optimization and conversational AI for e-commerce\n\nFeatures:\n• Natural language processing advancements\n• Smart speaker integration strategies\n• Voice-enabled checkout experiences\n• Personalization through voice analytics"
];

export const ResearchInput: React.FC<WizardStepProps> = ({ state, onUpdate }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);

  // Rotate placeholder examples every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPlaceholder((prev) => (prev + 1) % placeholderExamples.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleKeywordsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const keywords = value.split(',').map(k => k.trim()).filter(Boolean);
    onUpdate({ keywords });
  };

  const handleIndustryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onUpdate({ industry: e.target.value });
  };

  const handleAudienceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onUpdate({ targetAudience: e.target.value });
  };

  const handleModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const mode = e.target.value as any;
    onUpdate({ researchMode: mode });
  };

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provider = e.target.value as ResearchProvider;
    onUpdate({ config: { ...state.config, provider } });
  };

  const handleExaCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onUpdate({ config: { ...state.config, exa_category: value || undefined } });
  };

  const handleExaSearchTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as 'auto' | 'keyword' | 'neural';
    onUpdate({ config: { ...state.config, exa_search_type: value } });
  };

  const handleIncludeDomainsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const domains = value.split(',').map(d => d.trim()).filter(Boolean);
    onUpdate({ config: { ...state.config, exa_include_domains: domains } });
  };

  const handleExcludeDomainsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const domains = value.split(',').map(d => d.trim()).filter(Boolean);
    onUpdate({ config: { ...state.config, exa_exclude_domains: domains } });
  };

  const handleFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      console.log('File selected:', file.name);
      // TODO: Implement file upload logic
    }
  };

  return (
    <div style={{ maxWidth: '100%' }}>
      {/* Main Input Area */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.6)',
        backdropFilter: 'blur(8px)',
        border: '2px solid rgba(14, 165, 233, 0.2)',
        borderRadius: '16px',
        padding: '20px',
        marginBottom: '20px',
        transition: 'all 0.3s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
        e.currentTarget.style.boxShadow = '0 4px 20px rgba(14, 165, 233, 0.12)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
        e.currentTarget.style.boxShadow = 'none';
      }}
      >
        <label style={{
          marginBottom: '12px',
          fontSize: '15px',
          fontWeight: '600',
          color: '#0c4a6e',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <span style={{
            fontSize: '20px',
          }}>🔍</span>
          Research Topic & Keywords
        </label>
        
        <div style={{ position: 'relative' }}>
          <textarea
            value={state.keywords.join(', ')}
            onChange={handleKeywordsChange}
            placeholder={placeholderExamples[currentPlaceholder]}
            style={{
              width: '100%',
              minHeight: '160px',
              padding: '16px',
              fontSize: '14px',
              lineHeight: '1.6',
              border: '1px solid rgba(14, 165, 233, 0.15)',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              resize: 'vertical',
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
              transition: 'all 0.2s ease',
              boxShadow: 'inset 0 1px 3px rgba(14, 165, 233, 0.05)',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.5)';
              e.currentTarget.style.boxShadow = 'inset 0 1px 3px rgba(14, 165, 233, 0.05), 0 0 0 3px rgba(14, 165, 233, 0.1)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.15)';
              e.currentTarget.style.boxShadow = 'inset 0 1px 3px rgba(14, 165, 233, 0.05)';
            }}
          />
          
          {/* File Upload Button */}
          <button
            onClick={handleFileUpload}
            type="button"
            style={{
              position: 'absolute',
              bottom: '12px',
              right: '12px',
              padding: '8px 12px',
              background: 'rgba(14, 165, 233, 0.1)',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: '500',
              color: '#0369a1',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(14, 165, 233, 0.15)';
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(14, 165, 233, 0.1)';
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
            }}
          >
            📎 Upload Document
          </button>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileChange}
            accept=".txt,.doc,.docx,.pdf"
            style={{ display: 'none' }}
          />
        </div>
        
        <div style={{
          marginTop: '10px',
          fontSize: '12px',
          color: '#64748b',
          lineHeight: '1.5',
        }}>
          💡 Tip: Describe your research topic in detail. Include specific keywords, questions, or aspects you want to explore. The AI will find relevant sources and insights.
        </div>
      </div>

      {/* Configuration Options */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '20px',
      }}>
        {/* Industry */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontSize: '13px',
            fontWeight: '600',
            color: '#0c4a6e',
          }}>
            Industry
          </label>
          <select
            value={state.industry}
            onChange={handleIndustryChange}
            style={{
              width: '100%',
              padding: '10px 12px',
              fontSize: '13px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '10px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.5)';
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(14, 165, 233, 0.1)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            {industries.map(ind => (
              <option key={ind} value={ind}>{ind}</option>
            ))}
          </select>
        </div>

        {/* Research Mode */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontSize: '13px',
            fontWeight: '600',
            color: '#0c4a6e',
          }}>
            Research Depth
          </label>
          <select
            value={state.researchMode}
            onChange={handleModeChange}
            style={{
              width: '100%',
              padding: '10px 12px',
              fontSize: '13px',
              border: '1px solid rgba(14, 165, 233, 0.2)',
              borderRadius: '10px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.5)';
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(14, 165, 233, 0.1)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            {researchModes.map(mode => (
              <option key={mode.value} value={mode.value}>{mode.label}</option>
            ))}
          </select>
        </div>

        {/* Provider (only for Comprehensive/Targeted) */}
        {state.researchMode !== 'basic' && (
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontSize: '13px',
              fontWeight: '600',
              color: '#0c4a6e',
            }}>
              Search Provider
            </label>
            <select
              value={state.config.provider}
              onChange={handleProviderChange}
              style={{
                width: '100%',
                padding: '10px 12px',
                fontSize: '13px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                borderRadius: '10px',
                background: 'rgba(255, 255, 255, 0.9)',
                color: '#0f172a',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.5)';
                e.currentTarget.style.boxShadow = '0 0 0 3px rgba(14, 165, 233, 0.1)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              {providers.map(prov => (
                <option key={prov.value} value={prov.value}>{prov.label}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Exa-Specific Options */}
      {state.config.provider === 'exa' && state.researchMode !== 'basic' && (
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
                value={state.config.exa_category || ''}
                onChange={handleExaCategoryChange}
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
                value={state.config.exa_search_type || 'auto'}
                onChange={handleExaSearchTypeChange}
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
                value={state.config.exa_include_domains?.join(', ') || ''}
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
                value={state.config.exa_exclude_domains?.join(', ') || ''}
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
      )}

      {/* Target Audience (Optional) */}
      <div>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontSize: '13px',
          fontWeight: '600',
          color: '#0c4a6e',
        }}>
          Target Audience (Optional)
        </label>
        <input
          type="text"
          value={state.targetAudience}
          onChange={handleAudienceChange}
          placeholder="e.g., Marketing professionals, Tech enthusiasts, Business owners"
          style={{
            width: '100%',
            padding: '10px 12px',
            fontSize: '13px',
            border: '1px solid rgba(14, 165, 233, 0.2)',
            borderRadius: '10px',
            background: 'rgba(255, 255, 255, 0.9)',
            color: '#0f172a',
            transition: 'all 0.2s ease',
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.5)';
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(14, 165, 233, 0.1)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        />
      </div>
    </div>
  );
};
