import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { 
  Info,
  DollarSign,
  Activity,
  Zap,
  Search,
  Image,
  Code,
  Database,
  Globe,
  FileText,
  BarChart3
} from 'lucide-react';

// Types
import { ProviderBreakdown } from '../../types/billing';

interface ComprehensiveAPIBreakdownProps {
  providerBreakdown: ProviderBreakdown;
  totalCost: number;
}

// Comprehensive API categories and their descriptions
const API_CATEGORIES = {
  llm_models: {
    title: 'Large Language Models',
    description: 'AI models for text generation, analysis, and processing',
    icon: <Code size={20} />,
    apis: [
      {
        name: 'Gemini',
        description: 'Google\'s advanced AI model for complex reasoning and coding',
        models: ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash'],
        pricing: 'From $0.10/1M tokens (Flash-Lite) to $15.00/1M tokens (Pro)',
        use_cases: ['Content generation', 'Code analysis', 'Complex reasoning']
      },
      {
        name: 'OpenAI',
        description: 'GPT models for natural language processing and generation',
        models: ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
        pricing: 'From $0.15/1M tokens (GPT-4o Mini) to $10.00/1M tokens (GPT-4o)',
        use_cases: ['Chat completion', 'Text analysis', 'Creative writing']
      },
      {
        name: 'Anthropic',
        description: 'Claude models for safe and helpful AI assistance',
        models: ['claude-3.5-sonnet', 'claude-3-haiku', 'claude-3-opus'],
        pricing: 'From $3.00/1M tokens (Sonnet) to $15.00/1M tokens (Opus)',
        use_cases: ['Safe AI assistance', 'Long-form content', 'Analysis tasks']
      },
      {
        name: 'Mistral',
        description: 'European AI models for efficient text processing',
        models: ['mistral-large', 'mistral-medium', 'mistral-small'],
        pricing: 'From $2.00/1M tokens (Small) to $8.00/1M tokens (Large)',
        use_cases: ['Multilingual support', 'Efficient processing', 'European compliance']
      }
    ]
  },
  search_apis: {
    title: 'Search & Research APIs',
    description: 'APIs for web search, content discovery, and research',
    icon: <Search size={20} />,
    apis: [
      {
        name: 'Tavily',
        description: 'AI-powered search for real-time information',
        models: ['tavily-search'],
        pricing: '$0.001 per search request',
        use_cases: ['Real-time search', 'Fact checking', 'Research assistance']
      },
      {
        name: 'Serper',
        description: 'Google Search API for web results',
        models: ['serper-search'],
        pricing: '$0.001 per search request',
        use_cases: ['Web search', 'SEO analysis', 'Content research']
      },
      {
        name: 'Metaphor',
        description: 'Advanced search and content discovery',
        models: ['metaphor-search'],
        pricing: '$0.003 per search request',
        use_cases: ['Content discovery', 'Link analysis', 'Research automation']
      }
    ]
  },
  content_processing: {
    title: 'Content Processing APIs',
    description: 'APIs for web scraping, content extraction, and processing',
    icon: <FileText size={20} />,
    apis: [
      {
        name: 'Firecrawl',
        description: 'Web scraping and content extraction service',
        models: ['firecrawl-extract', 'firecrawl-scrape'],
        pricing: '$0.002 per page crawled',
        use_cases: ['Web scraping', 'Content extraction', 'Data collection']
      }
    ]
  },
  image_generation: {
    title: 'Image Generation APIs',
    description: 'APIs for creating and processing images',
    icon: <Image size={20} />,
    apis: [
      {
        name: 'Stability AI',
        description: 'AI-powered image generation and editing',
        models: ['stable-diffusion-xl', 'stable-diffusion-3'],
        pricing: '$0.04 per image generated',
        use_cases: ['Image generation', 'Art creation', 'Visual content']
      }
    ]
  },
  embeddings: {
    title: 'Embeddings & Vector APIs',
    description: 'APIs for text embeddings and vector operations',
    icon: <Database size={20} />,
    apis: [
      {
        name: 'Gemini Embeddings',
        description: 'Text embeddings for semantic search and analysis',
        models: ['gemini-embedding'],
        pricing: '$0.15 per 1M input tokens',
        use_cases: ['Semantic search', 'Text similarity', 'Vector databases']
      }
    ]
  }
};

const ComprehensiveAPIBreakdown: React.FC<ComprehensiveAPIBreakdownProps> = ({ 
  providerBreakdown, 
  totalCost 
}) => {
  // Get active providers from breakdown
  const activeProviders = Object.entries(providerBreakdown)
    .filter(([_, data]) => data.cost > 0)
    .map(([provider, data]) => ({ provider, ...data }));

  const getProviderCategory = (providerName: string) => {
    const provider = providerName.toLowerCase();
    if (['gemini', 'openai', 'anthropic', 'mistral'].includes(provider)) {
      return 'llm_models';
    }
    if (['tavily', 'serper', 'metaphor'].includes(provider)) {
      return 'search_apis';
    }
    if (['firecrawl'].includes(provider)) {
      return 'content_processing';
    }
    if (['stability'].includes(provider)) {
      return 'image_generation';
    }
    return 'llm_models'; // default
  };

  const getCategoryStats = (categoryKey: string) => {
    const categoryProviders = activeProviders.filter(p => 
      getProviderCategory(p.provider) === categoryKey
    );
    
    return {
      count: categoryProviders.length,
      totalCost: categoryProviders.reduce((sum, p) => sum + p.cost, 0),
      totalCalls: categoryProviders.reduce((sum, p) => sum + p.calls, 0),
      totalTokens: categoryProviders.reduce((sum, p) => sum + p.tokens, 0)
    };
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <CardContent sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 'bold', color: '#ffffff' }}>
              <BarChart3 size={20} />
              Comprehensive API Breakdown
            </Typography>
            <Tooltip title="Detailed breakdown of all API usage across categories">
              <Info size={16} color="rgba(255,255,255,0.7)" />
            </Tooltip>
          </Box>
        </CardContent>

        <CardContent sx={{ pt: 0 }}>
          {/* Summary Stats */}
          <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                    {Object.keys(API_CATEGORIES).length}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                    API Categories
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                    {activeProviders.length}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                    Active Providers
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                    ${totalCost.toFixed(4)}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                    Total Cost
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                    {activeProviders.reduce((sum, p) => sum + p.calls, 0)}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                    Total Calls
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>

          {/* API Categories */}
          {Object.entries(API_CATEGORIES).map(([categoryKey, category]) => {
            const stats = getCategoryStats(categoryKey);
            const hasUsage = stats.count > 0;

            return (
              <Accordion 
                key={categoryKey}
                sx={{ 
                  mb: 1,
                  backgroundColor: 'rgba(255,255,255,0.05)',
                  '&:before': { display: 'none' },
                  '&.Mui-expanded': { margin: '0 0 8px 0' }
                }}
              >
                <AccordionSummary
                  expandIcon={<ExpandMore sx={{ color: 'rgba(255,255,255,0.7)' }} />}
                  sx={{ 
                    minHeight: 48,
                    '&.Mui-expanded': { minHeight: 48 }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    <Box sx={{ color: hasUsage ? '#4ade80' : 'rgba(255,255,255,0.5)' }}>
                      {category.icon}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                        {category.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        {category.description}
                      </Typography>
                    </Box>
                    {hasUsage && (
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <Chip 
                          label={`${stats.count} active`} 
                          size="small" 
                          sx={{ 
                            backgroundColor: 'rgba(74, 222, 128, 0.2)',
                            color: '#4ade80',
                            border: '1px solid rgba(74, 222, 128, 0.3)'
                          }} 
                        />
                        <Typography variant="caption" sx={{ color: '#4ade80', fontWeight: 'bold' }}>
                          ${stats.totalCost.toFixed(4)}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <Grid container spacing={2}>
                    {category.apis.map((api) => {
                      const providerData = activeProviders.find(p => 
                        p.provider.toLowerCase() === api.name.toLowerCase()
                      );

                      return (
                        <Grid item xs={12} md={6} key={api.name}>
                          <Box 
                            sx={{ 
                              p: 2, 
                              backgroundColor: providerData ? 'rgba(74, 222, 128, 0.1)' : 'rgba(255,255,255,0.05)',
                              borderRadius: 2,
                              border: providerData ? '1px solid rgba(74, 222, 128, 0.2)' : '1px solid rgba(255,255,255,0.1)'
                            }}
                          >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                                {api.name}
                              </Typography>
                              {providerData && (
                                <Chip 
                                  label="Active" 
                                  size="small" 
                                  sx={{ 
                                    backgroundColor: 'rgba(74, 222, 128, 0.2)',
                                    color: '#4ade80'
                                  }} 
                                />
                              )}
                            </Box>
                            
                            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', display: 'block', mb: 1 }}>
                              {api.description}
                            </Typography>
                            
                            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)', display: 'block', mb: 1 }}>
                              Pricing: {api.pricing}
                            </Typography>

                            {providerData && (
                              <Box sx={{ mt: 2, p: 1, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 1 }}>
                                <Grid container spacing={1}>
                                  <Grid item xs={4}>
                                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                                      Cost
                                    </Typography>
                                    <Typography variant="caption" sx={{ display: 'block', color: '#4ade80', fontWeight: 'bold' }}>
                                      ${providerData.cost.toFixed(4)}
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={4}>
                                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                                      Calls
                                    </Typography>
                                    <Typography variant="caption" sx={{ display: 'block', color: '#ffffff', fontWeight: 'bold' }}>
                                      {providerData.calls}
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={4}>
                                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                                      Tokens
                                    </Typography>
                                    <Typography variant="caption" sx={{ display: 'block', color: '#ffffff', fontWeight: 'bold' }}>
                                      {providerData.tokens.toLocaleString()}
                                    </Typography>
                                  </Grid>
                                </Grid>
                              </Box>
                            )}

                            <Box sx={{ mt: 1 }}>
                              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                                Use cases: {api.use_cases.join(', ')}
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>
                      );
                    })}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ComprehensiveAPIBreakdown;
