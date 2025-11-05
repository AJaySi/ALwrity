import React, { useRef, useState, useEffect } from 'react';
import { WizardStepProps } from '../types/research.types';
import { ResearchProvider, ResearchMode } from '../../../services/blogWriterApi';
import { getResearchConfig, ProviderAvailability } from '../../../api/researchConfig';
import { 
  getResearchHistory, 
  clearResearchHistory, 
  formatHistoryTimestamp, 
  getHistorySummary,
  ResearchHistoryEntry 
} from '../../../utils/researchHistory';
import { 
  expandKeywords, 
  formatKeyword, 
  isOriginalKeyword 
} from '../../../utils/keywordExpansion';
import { 
  generateResearchAngles, 
  formatAngle 
} from '../../../utils/researchAngles';

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

// Intelligent input parser - handles sentences, keywords, URLs
const parseIntelligentInput = (value: string): string[] => {
  // If empty, return empty array
  if (!value.trim()) return [];
  
  // Detect if input contains URLs
  const urlPattern = /(https?:\/\/[^\s,]+)/g;
  const urls = value.match(urlPattern) || [];
  
  // Check if input looks like a sentence/paragraph (contains multiple words without commas)
  const hasCommas = value.includes(',');
  const wordCount = value.trim().split(/\s+/).length;
  
  if (urls.length > 0) {
    // User provided URLs - extract them as separate keywords
    const textWithoutUrls = value.replace(urlPattern, '').trim();
    const textKeywords = textWithoutUrls ? [textWithoutUrls] : [];
    return [...urls, ...textKeywords];
  } else if (!hasCommas && wordCount > 5) {
    // Looks like a sentence/paragraph - treat entire input as single research topic
    return [value.trim()];
  } else if (hasCommas) {
    // Traditional comma-separated keywords
    return value.split(',').map(k => k.trim()).filter(Boolean);
  } else {
    // Short phrase or single keyword
    return [value.trim()];
  }
};

// Industry-specific placeholder examples for personalized experience
const getIndustryPlaceholders = (industry: string): string[] => {
  const industryExamples: Record<string, string[]> = {
    Healthcare: [
      "Research: AI-powered diagnostic tools in clinical practice\n\n💡 What you'll get:\n• FDA-approved AI medical devices\n• Clinical accuracy and patient outcomes\n• Implementation costs and ROI",
      "Analyze: Telemedicine adoption trends and patient satisfaction\n\n💡 Research includes:\n• Post-pandemic telehealth growth\n• Remote patient monitoring technologies\n• Insurance coverage and reimbursement",
      "Investigate: Personalized medicine and genomic testing advances\n\n💡 You'll discover:\n• Latest genomic sequencing technologies\n• Precision therapy success rates\n• Ethical considerations and regulations"
    ],
    Technology: [
      "Investigate: Latest developments in edge computing and IoT\n\n💡 What you'll get:\n• Edge AI deployment strategies\n• 5G integration and performance\n• Industry use cases and benchmarks",
      "Compare: Cloud providers for enterprise SaaS applications\n\n💡 Research includes:\n• AWS vs Azure vs GCP feature comparison\n• Cost optimization strategies\n• Security and compliance certifications",
      "Analyze: Quantum computing breakthroughs and commercial applications\n\n💡 You'll discover:\n• Latest quantum hardware developments\n• Real-world problem solving examples\n• Investment landscape and timeline"
    ],
    Finance: [
      "Research: DeFi regulatory landscape and compliance challenges\n\n💡 What you'll get:\n• Global regulatory frameworks\n• Compliance best practices\n• Risk management strategies",
      "Analyze: Digital banking customer retention strategies\n\n💡 Research includes:\n• Neobank growth and market share\n• Customer acquisition costs and LTV\n• Personalization and UX innovations",
      "Investigate: ESG investing trends and impact measurement\n\n💡 You'll discover:\n• ESG rating methodologies\n• Fund performance and returns\n• Regulatory requirements and reporting"
    ],
    Marketing: [
      "Research: AI-powered marketing automation and personalization\n\n💡 What you'll get:\n• Top marketing AI platforms and features\n• ROI and conversion rate improvements\n• Implementation case studies",
      "Analyze: Influencer marketing ROI and authenticity trends\n\n💡 Research includes:\n• Micro vs macro influencer effectiveness\n• Platform-specific engagement rates\n• Brand partnership best practices",
      "Investigate: Privacy-first marketing in a cookieless world\n\n💡 You'll discover:\n• First-party data strategies\n• Contextual targeting innovations\n• Compliance with privacy regulations"
    ],
    Business: [
      "Research: Remote work policies and hybrid workplace models\n\n💡 What you'll get:\n• Productivity metrics and employee satisfaction\n• Technology infrastructure requirements\n• Cultural impact and change management",
      "Analyze: Supply chain resilience and diversification strategies\n\n💡 Research includes:\n• Nearshoring and reshoring trends\n• Technology solutions for visibility\n• Risk mitigation frameworks",
      "Investigate: Sustainability initiatives and corporate ESG programs\n\n💡 You'll discover:\n• Industry-specific sustainability benchmarks\n• Cost-benefit analysis of green initiatives\n• Stakeholder communication strategies"
    ],
    Education: [
      "Research: EdTech tools for personalized learning experiences\n\n💡 What you'll get:\n• Adaptive learning platform comparisons\n• Student engagement and outcomes data\n• Implementation costs and training needs",
      "Analyze: Microlearning and skill-based education trends\n\n💡 Research includes:\n• Corporate training effectiveness\n• Platform and content recommendations\n• ROI and completion rates",
      "Investigate: AI tutoring systems and student support tools\n\n💡 You'll discover:\n• Natural language processing advances\n• Student performance improvements\n• Accessibility and inclusion features"
    ],
    'Real Estate': [
      "Research: PropTech innovations transforming property management\n\n💡 What you'll get:\n• Smart building technologies and IoT\n• Tenant experience platforms\n• Operational efficiency gains",
      "Analyze: Virtual staging and 3D property tours adoption\n\n💡 Research includes:\n• Technology provider comparisons\n• Impact on sales velocity and pricing\n• Cost vs traditional staging",
      "Investigate: Real estate tokenization and fractional ownership\n\n💡 You'll discover:\n• Blockchain platforms and regulations\n• Investor demographics and demand\n• Liquidity and exit strategies"
    ],
    Travel: [
      "Research: Sustainable tourism trends and eco-travel preferences\n\n💡 What you'll get:\n• Green certification programs\n• Traveler willingness to pay premium\n• Destination best practices",
      "Analyze: AI-powered travel personalization and recommendations\n\n💡 Research includes:\n• Recommendation engine technologies\n• Booking conversion rate improvements\n• Customer lifetime value impact",
      "Investigate: Bleisure travel and workation destination trends\n\n💡 You'll discover:\n• Remote work-friendly destinations\n• Co-working and accommodation options\n• Digital nomad demographics"
    ]
  };

  return industryExamples[industry] || [
    "Research: Latest AI advancements in your industry\n\n💡 What you'll get:\n• Recent breakthroughs and innovations\n• Key companies and technologies\n• Expert insights and market trends",
    
    "Write a blog on: Emerging trends shaping your industry in 2025\n\n💡 This will research:\n• Technology disruptions and innovations\n• Regulatory changes and compliance\n• Consumer behavior shifts",
    
    "Analyze: Best practices and success stories in your field\n\n💡 Research includes:\n• Industry leader strategies\n• Implementation case studies\n• ROI and performance metrics",
    
    "https://example.com/article\n\n💡 URL detected! Research will:\n• Extract key insights from the article\n• Find related sources and updates\n• Provide comprehensive context"
  ];
};

export const ResearchInput: React.FC<WizardStepProps> = ({ state, onUpdate }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);
  const [providerAvailability, setProviderAvailability] = useState<ProviderAvailability | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [suggestedMode, setSuggestedMode] = useState<ResearchMode | null>(null);
  const [researchHistory, setResearchHistory] = useState<ResearchHistoryEntry[]>([]);
  const [keywordExpansion, setKeywordExpansion] = useState<{
    original: string[];
    expanded: string[];
    suggestions: string[];
  } | null>(null);
  const [researchAngles, setResearchAngles] = useState<string[]>([]);

  // Load research history on mount and when component updates
  useEffect(() => {
    const history = getResearchHistory();
    setResearchHistory(history);
  }, []); // Load once on mount

  // Reload history when keywords change (after research completes)
  useEffect(() => {
    const history = getResearchHistory();
    setResearchHistory(history);
  }, [state.keywords]);

  // Load research configuration on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await getResearchConfig();
        
        // Set provider availability with fallback
        setProviderAvailability(config?.provider_availability || {
          google_available: true, // Default to available, will be corrected by actual key status
          exa_available: false,
          gemini_key_status: 'missing',
          exa_key_status: 'missing'
        });
        
        // Apply persona defaults if not already set (with null checks)
        if (config?.persona_defaults) {
          if (config.persona_defaults.industry && state.industry === 'General') {
            onUpdate({ industry: config.persona_defaults.industry });
          }
          if (config.persona_defaults.target_audience && state.targetAudience === 'General') {
            onUpdate({ targetAudience: config.persona_defaults.target_audience });
          }
          
          // Apply suggested Exa domains if Exa is available and not already set
          if (config.provider_availability?.exa_available && config.persona_defaults.suggested_domains?.length > 0) {
            if (!state.config.exa_include_domains || state.config.exa_include_domains.length === 0) {
              onUpdate({ 
                config: { 
                  ...state.config, 
                  exa_include_domains: config.persona_defaults.suggested_domains 
                } 
              });
            }
          }
          
          // Apply suggested Exa category if available
          if (config.persona_defaults.suggested_exa_category && !state.config.exa_category) {
            onUpdate({
              config: {
                ...state.config,
                exa_category: config.persona_defaults.suggested_exa_category
              }
            });
          }
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error('[ResearchInput] Failed to load research config:', errorMessage);
        
        // Set default provider availability on error
        setProviderAvailability({
          google_available: true, // Optimistically assume available
          exa_available: false,
          gemini_key_status: 'missing',
          exa_key_status: 'missing'
        });
        
        // Continue with defaults - don't block the UI
      } finally {
        setLoadingConfig(false);
      }
    };
    
    loadConfig();
  }, []); // Only run once on mount

  // Get industry-specific placeholders
  const placeholderExamples = getIndustryPlaceholders(state.industry);
  
  // Rotate placeholder examples every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPlaceholder((prev) => (prev + 1) % placeholderExamples.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [placeholderExamples.length]);
  
  // Reset placeholder index when industry changes
  useEffect(() => {
    setCurrentPlaceholder(0);
  }, [state.industry]);
  
  // Auto-set provider based on research mode
  useEffect(() => {
    if (!providerAvailability) return;
    
    let newProvider: ResearchProvider = 'google';
    
    switch (state.researchMode) {
      case 'basic':
        // Basic: Google only (fast, simple)
        newProvider = 'google';
        break;
      case 'comprehensive':
        // Comprehensive: Prefer Exa if available, fallback to Google
        newProvider = providerAvailability.exa_available ? 'exa' : 'google';
        break;
      case 'targeted':
        // Targeted: Prefer Exa if available, fallback to Google
        newProvider = providerAvailability.exa_available ? 'exa' : 'google';
        break;
    }
    
    // Only update if provider changed
    if (state.config.provider !== newProvider) {
      onUpdate({ config: { ...state.config, provider: newProvider } });
    }
  }, [state.researchMode, providerAvailability]);
  
  // Dynamic domain suggestions when industry changes
  useEffect(() => {
    if (!providerAvailability || state.industry === 'General') return;
    
    // Get industry-specific domain suggestions (from backend logic)
    const domainMap: Record<string, string[]> = {
      'Healthcare': ['pubmed.gov', 'nejm.org', 'thelancet.com', 'nih.gov'],
      'Technology': ['techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com'],
      'Finance': ['wsj.com', 'bloomberg.com', 'ft.com', 'reuters.com'],
      'Science': ['nature.com', 'sciencemag.org', 'cell.com', 'pnas.org'],
      'Business': ['hbr.org', 'forbes.com', 'businessinsider.com', 'mckinsey.com'],
      'Marketing': ['marketingland.com', 'adweek.com', 'hubspot.com', 'moz.com'],
      'Education': ['edutopia.org', 'chronicle.com', 'insidehighered.com'],
      'Real Estate': ['realtor.com', 'zillow.com', 'forbes.com'],
      'Entertainment': ['variety.com', 'hollywoodreporter.com', 'deadline.com'],
      'Travel': ['lonelyplanet.com', 'nationalgeographic.com', 'travelandleisure.com'],
      'Fashion': ['vogue.com', 'elle.com', 'wwd.com'],
      'Sports': ['espn.com', 'si.com', 'bleacherreport.com'],
      'Law': ['law.com', 'abajournal.com', 'scotusblog.com'],
    };
    
    const newDomains = domainMap[state.industry] || [];
    
    // Get industry-specific Exa category
    const categoryMap: Record<string, string> = {
      'Healthcare': 'research paper',
      'Science': 'research paper',
      'Finance': 'financial report',
      'Technology': 'company',
      'Business': 'company',
      'Marketing': 'company',
      'Education': 'research paper',
      'Law': 'pdf',
    };
    
    const newCategory = categoryMap[state.industry];
    
    // Only update if Exa is available and domains/category should change
    if (providerAvailability.exa_available && newDomains.length > 0) {
      const configUpdates: any = {};
      
      // Update domains if different
      const currentDomains = state.config.exa_include_domains || [];
      if (JSON.stringify(currentDomains) !== JSON.stringify(newDomains)) {
        configUpdates.exa_include_domains = newDomains;
      }
      
      // Update category if available and different
      if (newCategory && state.config.exa_category !== newCategory) {
        configUpdates.exa_category = newCategory;
      }
      
      // Apply updates if any
      if (Object.keys(configUpdates).length > 0) {
        onUpdate({ 
          config: { 
            ...state.config, 
            ...configUpdates 
          } 
        });
      }
    }
  }, [state.industry, providerAvailability]);

  // Smart mode suggestion based on query complexity
  const suggestResearchMode = (keywords: string[]): ResearchMode => {
    if (keywords.length === 0) return 'basic';
    
    const totalText = keywords.join(' ');
    const totalWords = totalText.split(/\s+/).length;
    const hasURL = keywords.some(k => k.startsWith('http'));
    
    // URL detected → comprehensive research
    if (hasURL) return 'comprehensive';
    
    // Long detailed query → comprehensive
    if (totalWords > 20) return 'comprehensive';
    
    // Medium complexity → targeted
    if (totalWords > 10 || keywords.length > 3) return 'targeted';
    
    // Simple query → basic
    return 'basic';
  };

  // Expand keywords when keywords or industry changes
  useEffect(() => {
    if (state.keywords.length > 0 && state.industry !== 'General') {
      const expansion = expandKeywords(state.keywords, state.industry);
      setKeywordExpansion(expansion);
    } else {
      setKeywordExpansion(null);
    }
  }, [state.keywords, state.industry]);

  // Generate research angles when keywords change
  useEffect(() => {
    if (state.keywords.length > 0) {
      // Use the first keyword (or joined keywords) as the query
      const query = state.keywords.join(' ');
      const angles = generateResearchAngles(query, state.industry);
      setResearchAngles(angles);
    } else {
      setResearchAngles([]);
    }
  }, [state.keywords, state.industry]);

  const handleKeywordsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const keywords = parseIntelligentInput(value);
    onUpdate({ keywords });
    
    // Update suggested mode
    const suggested = suggestResearchMode(keywords);
    setSuggestedMode(suggested);
  };

  // Handle clicking a keyword suggestion to add it
  const handleAddSuggestion = (suggestion: string) => {
    const currentKeywords = [...state.keywords];
    // Check if suggestion already exists (case-insensitive)
    const exists = currentKeywords.some(k => k.toLowerCase() === suggestion.toLowerCase());
    if (!exists) {
      currentKeywords.push(suggestion);
      onUpdate({ keywords: currentKeywords });
    }
  };

  // Handle removing a keyword
  const handleRemoveKeyword = (keywordToRemove: string) => {
    const currentKeywords = state.keywords.filter(k => k.toLowerCase() !== keywordToRemove.toLowerCase());
    onUpdate({ keywords: currentKeywords });
  };

  // Handle clicking a research angle to use it
  const handleUseAngle = (angle: string) => {
    // Parse the angle as a new research query
    const keywords = parseIntelligentInput(angle);
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
        
        {/* Research History */}
        {researchHistory.length > 0 && (
          <div style={{
            marginBottom: '12px',
            padding: '12px',
            background: 'rgba(14, 165, 233, 0.03)',
            border: '1px solid rgba(14, 165, 233, 0.1)',
            borderRadius: '10px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '10px',
            }}>
              <span style={{
                fontSize: '12px',
                fontWeight: '600',
                color: '#0369a1',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}>
                <span>🕐</span>
                Recently Researched
              </span>
              <button
                onClick={() => {
                  clearResearchHistory();
                  setResearchHistory([]);
                }}
                style={{
                  padding: '4px 10px',
                  fontSize: '11px',
                  color: '#64748b',
                  background: 'transparent',
                  border: '1px solid rgba(100, 116, 139, 0.2)',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)';
                  e.currentTarget.style.color = '#dc2626';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'rgba(100, 116, 139, 0.2)';
                  e.currentTarget.style.color = '#64748b';
                }}
              >
                Clear
              </button>
            </div>
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
            }}>
              {researchHistory.map((entry) => (
                <button
                  key={entry.timestamp}
                  onClick={() => {
                    // Populate all fields from history entry
                    onUpdate({
                      keywords: entry.keywords,
                      industry: entry.industry,
                      targetAudience: entry.targetAudience,
                      researchMode: entry.researchMode,
                    });
                  }}
                  title={`Industry: ${entry.industry} | Audience: ${entry.targetAudience} | Mode: ${entry.researchMode} | ${formatHistoryTimestamp(entry.timestamp)}`}
                  style={{
                    padding: '8px 14px',
                    fontSize: '12px',
                    color: '#0369a1',
                    background: 'rgba(255, 255, 255, 0.9)',
                    border: '1px solid rgba(14, 165, 233, 0.2)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    maxWidth: '100%',
                    textAlign: 'left',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(14, 165, 233, 0.1)';
                    e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(14, 165, 233, 0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.9)';
                    e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <span style={{ fontSize: '14px' }}>🔍</span>
                  <span style={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    maxWidth: '200px',
                  }}>
                    {getHistorySummary(entry)}
                  </span>
                  <span style={{
                    fontSize: '10px',
                    color: '#64748b',
                    marginLeft: '4px',
                  }}>
                    {formatHistoryTimestamp(entry.timestamp)}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
        
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
        
                {/* Smart Input Detection Indicator */}
        {state.keywords.length > 0 && (
          <div style={{
            marginTop: '10px',
            padding: '8px 12px',
            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)',                                                     
            border: '1px solid rgba(34, 197, 94, 0.2)',
            borderRadius: '8px',
            fontSize: '12px',
            color: '#059669',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}>
            <span>✓</span>
            {state.keywords[0]?.startsWith('http') ? (
              <span>URL detected - will extract and analyze content</span>      
            ) : state.keywords.length === 1 && state.keywords[0]?.split(/\s+/).length > 5 ? (                                                                   
              <span>Research topic detected - will conduct comprehensive analysis</span>                                                                        
            ) : (
              <span>{state.keywords.length} keyword{state.keywords.length > 1 ? 's' : ''} identified</span>                                                     
            )}
          </div>
        )}

        {/* Keyword Expansion Suggestions */}
        {keywordExpansion && keywordExpansion.suggestions.length > 0 && state.industry !== 'General' && (
          <div style={{
            marginTop: '12px',
            padding: '12px',
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 197, 253, 0.05) 100%)',
            border: '1px solid rgba(59, 130, 246, 0.15)',
            borderRadius: '8px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '10px',
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '13px',
                fontWeight: '600',
                color: '#1e40af',
              }}>
                <span>💡</span>
                <span>Suggested Keywords for {state.industry}</span>
              </div>
            </div>
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
            }}>
              {keywordExpansion.suggestions.map((suggestion, idx) => {
                const isAlreadyAdded = state.keywords.some(k => k.toLowerCase() === suggestion.toLowerCase());
                return (
                  <button
                    key={idx}
                    onClick={() => !isAlreadyAdded && handleAddSuggestion(suggestion)}
                    disabled={isAlreadyAdded}
                    style={{
                      padding: '6px 12px',
                      background: isAlreadyAdded 
                        ? 'rgba(203, 213, 225, 0.3)' 
                        : 'rgba(59, 130, 246, 0.1)',
                      border: `1px solid ${isAlreadyAdded ? 'rgba(148, 163, 184, 0.3)' : 'rgba(59, 130, 246, 0.2)'}`,
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: '500',
                      color: isAlreadyAdded ? '#64748b' : '#1e40af',
                      cursor: isAlreadyAdded ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s ease',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                    onMouseEnter={(e) => {
                      if (!isAlreadyAdded) {
                        e.currentTarget.style.background = 'rgba(59, 130, 246, 0.15)';
                        e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.3)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isAlreadyAdded) {
                        e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                        e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.2)';
                      }
                    }}
                  >
                    {isAlreadyAdded ? (
                      <>
                        <span>✓</span>
                        <span>{formatKeyword(suggestion)}</span>
                      </>
                    ) : (
                      <>
                        <span>+</span>
                        <span>{formatKeyword(suggestion)}</span>
                      </>
                    )}
                  </button>
                );
              })}
            </div>
            <div style={{
              marginTop: '8px',
              fontSize: '11px',
              color: '#64748b',
              fontStyle: 'italic',
            }}>
              Click to add suggested keywords to your research query
            </div>
          </div>
        )}

         {/* Current Keywords Display (for removal) */}
         {state.keywords.length > 0 && (
           <div style={{
             marginTop: '12px',
             padding: '10px',
             background: 'rgba(241, 245, 249, 0.5)',
             border: '1px solid rgba(203, 213, 225, 0.3)',
             borderRadius: '8px',
           }}>
             <div style={{
               fontSize: '12px',
               fontWeight: '600',
               color: '#475569',
               marginBottom: '8px',
             }}>
               Current Keywords ({state.keywords.length})
             </div>
             <div style={{
               display: 'flex',
               flexWrap: 'wrap',
               gap: '6px',
             }}>
               {state.keywords.map((keyword, idx) => (
                 <div
                   key={idx}
                   style={{
                     padding: '5px 10px',
                     background: 'white',
                     border: '1px solid rgba(203, 213, 225, 0.5)',
                     borderRadius: '6px',
                     fontSize: '12px',
                     color: '#334155',
                     display: 'flex',
                     alignItems: 'center',
                     gap: '6px',
                   }}
                 >
                   <span>{formatKeyword(keyword)}</span>
                   <button
                     onClick={() => handleRemoveKeyword(keyword)}
                     style={{
                       background: 'none',
                       border: 'none',
                       color: '#ef4444',
                       cursor: 'pointer',
                       fontSize: '14px',
                       padding: '0',
                       width: '16px',
                       height: '16px',
                       display: 'flex',
                       alignItems: 'center',
                       justifyContent: 'center',
                       borderRadius: '50%',
                       transition: 'all 0.2s ease',
                     }}
                     onMouseEnter={(e) => {
                       e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                     }}
                     onMouseLeave={(e) => {
                       e.currentTarget.style.background = 'none';
                     }}
                     title="Remove keyword"
                   >
                     ×
                   </button>
                 </div>
               ))}
             </div>
           </div>
         )}

         {/* Alternative Research Angles */}
         {researchAngles.length > 0 && (
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
             </div>
             <div style={{
               display: 'grid',
               gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
               gap: '10px',
             }}>
               {researchAngles.map((angle, idx) => (
                 <button
                   key={idx}
                   onClick={() => handleUseAngle(angle)}
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
         )}

        <div style={{
          marginTop: '10px',
          fontSize: '12px',
          color: '#64748b',
          lineHeight: '1.5',
        }}>
          💡 Tip: Enter sentences, keywords, or URLs. The AI will intelligently parse your input and conduct comprehensive research.                            
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

        {/* Research Mode with Status Indicator */}
        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '8px',
            fontSize: '13px',
            fontWeight: '600',
            color: '#0c4a6e',
          }}>
            <span>Research Depth</span>
            {providerAvailability && (
              <span style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '11px',
                color: '#64748b',
                background: 'rgba(255, 255, 255, 0.8)',
                padding: '4px 10px',
                borderRadius: '20px',
                border: '1px solid rgba(14, 165, 233, 0.15)',
              }}>
                <span style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: providerAvailability.google_available ? '#10b981' : '#ef4444',
                  boxShadow: providerAvailability.google_available 
                    ? '0 0 6px rgba(16, 185, 129, 0.5)' 
                    : '0 0 6px rgba(239, 68, 68, 0.5)',
                }} title={`Google: ${providerAvailability.gemini_key_status}`} />
                <span>Google</span>
                <span style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: providerAvailability.exa_available ? '#10b981' : '#ef4444',
                  boxShadow: providerAvailability.exa_available 
                    ? '0 0 6px rgba(16, 185, 129, 0.5)' 
                    : '0 0 6px rgba(239, 68, 68, 0.5)',
                  marginLeft: '6px',
                }} title={`Exa: ${providerAvailability.exa_key_status}`} />
                <span>Exa</span>
              </span>
            )}
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
              <option key={mode.value} value={mode.value}>
                {mode.label}
                {mode.value === 'basic' && ' • Google Search'}
                {mode.value === 'comprehensive' && providerAvailability?.exa_available && ' • Exa Neural'}
                {mode.value === 'comprehensive' && !providerAvailability?.exa_available && ' • Google Search'}
                {mode.value === 'targeted' && providerAvailability?.exa_available && ' • Exa Neural'}
                {mode.value === 'targeted' && !providerAvailability?.exa_available && ' • Google Search'}
              </option>
            ))}
          </select>
          <div style={{
            marginTop: '6px',
            fontSize: '11px',
            color: '#64748b',
            fontStyle: 'italic',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
          }}>
            <span>
              {state.researchMode === 'basic' && '🔍 Fast research using Google Search'}
              {state.researchMode === 'comprehensive' && providerAvailability?.exa_available && '🧠 Deep research using Exa Neural Search'}
              {state.researchMode === 'comprehensive' && !providerAvailability?.exa_available && '🔍 In-depth research using Google Search'}
              {state.researchMode === 'targeted' && providerAvailability?.exa_available && '🎯 Focused research using Exa Neural Search'}
              {state.researchMode === 'targeted' && !providerAvailability?.exa_available && '🎯 Focused research using Google Search'}
            </span>
            {suggestedMode && suggestedMode !== state.researchMode && state.keywords.length > 0 && (
              <button
                onClick={() => onUpdate({ researchMode: suggestedMode })}
                style={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '4px 10px',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 2px 8px rgba(16, 185, 129, 0.3)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(16, 185, 129, 0.3)';
                }}
                title={`Switch to ${suggestedMode} mode for better results`}
              >
                <span>💡</span>
                <span>Try {suggestedMode}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Exa-Specific Options - Show when Exa is selected */}
      {state.config.provider === 'exa' && (
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
