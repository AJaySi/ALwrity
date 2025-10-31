import React, { useState } from 'react';
import { Container, Grid, Card, CardContent, Typography, Box, Stack, Chip } from '@mui/material';
import { CheckCircle, AutoAwesome } from '@mui/icons-material';

interface PhaseFeature {
  title: string;
  description: string;
  details: string[];
  imagePlaceholder: string;
}

interface BlogPhase {
  id: string;
  name: string;
  icon: string;
  shortDescription: string;
  features: PhaseFeature[];
  technicalDetails: {
    aiModel: string;
    promptType: string;
    outputFormat: string;
    integration: string;
  };
  videoPlaceholder: string;
}

const BlogWriterPhasesSection: React.FC = () => {
  const [activePhase, setActivePhase] = useState<number | null>(null);

  const phases: BlogPhase[] = [
    {
      id: 'research',
      name: 'Research & Strategy',
      icon: '🔍',
      shortDescription: 'AI-powered comprehensive research with Google Search grounding, competitor analysis, and content gap identification',
      features: [
        {
          title: 'Google Search Grounding',
          description: 'Real-time web research using Gemini\'s native Google Search integration',
          details: [
            'Single API call for comprehensive research',
            'Live web data from credible sources',
            'Automatic source extraction and citation',
            'Current trends and 2024-2025 insights',
            'Market analysis and forecasts'
          ],
          imagePlaceholder: '/images/research-google-grounding.jpg'
        },
        {
          title: 'Competitor Analysis',
          description: 'Identify top players and content opportunities in your niche',
          details: [
            'Top competitor content analysis',
            'Content gap identification',
            'Unique angle discovery',
            'Market positioning insights',
            'Competitive advantage opportunities'
          ],
          imagePlaceholder: '/images/research-competitor.jpg'
        },
        {
          title: 'Keyword Intelligence',
          description: 'Comprehensive keyword analysis with SEO opportunities',
          details: [
            'Primary, secondary, and long-tail keyword identification',
            'Search volume and competition analysis',
            'Keyword clustering and grouping',
            'Content optimization suggestions',
            'Target audience keyword mapping'
          ],
          imagePlaceholder: '/images/research-keywords.jpg'
        },
        {
          title: 'Content Angle Generation',
          description: 'AI-generated compelling content angles for maximum engagement',
          details: [
            '5 unique content angle suggestions',
            'Trending topic identification',
            'Audience pain point mapping',
            'Viral potential assessment',
            'Expert opinion synthesis'
          ],
          imagePlaceholder: '/images/research-angles.jpg'
        }
      ],
      technicalDetails: {
        aiModel: 'Gemini Pro with Google Search Grounding',
        promptType: 'Comprehensive research prompt',
        outputFormat: 'Structured JSON with sources, keywords, trends, competitors',
        integration: 'GeminiGroundedProvider via research_service.py'
      },
      videoPlaceholder: '/videos/phase1-research.mp4'
    },
    {
      id: 'outline',
      name: 'Intelligent Outline',
      icon: '📝',
      shortDescription: 'AI-generated outlines with source mapping, grounding insights, and optimization recommendations',
      features: [
        {
          title: 'AI Outline Generation',
          description: 'Comprehensive outline based on research with SEO optimization',
          details: [
            'Section-by-section breakdown',
            'Subheadings and key points',
            'Target word counts per section',
            'Logical flow and progression',
            'SEO-optimized structure'
          ],
          imagePlaceholder: '/images/outline-generation.jpg'
        },
        {
          title: 'Source Mapping & Grounding',
          description: 'Connect each section to research sources with citations',
          details: [
            'Automatic source-to-section mapping',
            'Grounding support scores',
            'Citation suggestions',
            'Source credibility ratings',
            'Reference verification'
          ],
          imagePlaceholder: '/images/outline-grounding.jpg'
        },
        {
          title: 'Interactive Refinement',
          description: 'Human-in-the-loop editing with AI assistance',
          details: [
            'Add, remove, merge sections',
            'Reorder and restructure',
            'AI enhancement suggestions',
            'Custom instructions support',
            'Multiple outline versions'
          ],
          imagePlaceholder: '/images/outline-refine.jpg'
        },
        {
          title: 'Title Generation',
          description: 'Multiple SEO-optimized title options',
          details: [
            'AI-generated title variations',
            'SEO score per title',
            'Engagement potential analysis',
            'Keyword integration',
            'Click-through optimization'
          ],
          imagePlaceholder: '/images/outline-titles.jpg'
        }
      ],
      technicalDetails: {
        aiModel: 'Gemini Pro (provider-agnostic via llm_text_gen)',
        promptType: 'Structured outline prompt with research context',
        outputFormat: 'JSON outline with sections, headings, key_points, references',
        integration: 'OutlineService via parallel_processor.py'
      },
      videoPlaceholder: '/videos/phase2-outline.mp4'
    },
    {
      id: 'content',
      name: 'Content Generation',
      icon: '✨',
      shortDescription: 'Section-by-section content generation with SEO optimization, context memory, and engagement improvements',
      features: [
        {
          title: 'Smart Content Generation',
          description: 'AI-powered section writing with context awareness',
          details: [
            'Section-by-section generation',
            'Context memory across sections',
            'Smooth transitions between sections',
            'Consistent tone and style',
            'Natural keyword integration'
          ],
          imagePlaceholder: '/images/content-generation.jpg'
        },
        {
          title: 'Continuity Analysis',
          description: 'Real-time flow and coherence monitoring',
          details: [
            'Narrative flow assessment',
            'Coherence scoring',
            'Transition quality analysis',
            'Tone consistency tracking',
            'Content quality metrics'
          ],
          imagePlaceholder: '/images/content-continuity.jpg'
        },
        {
          title: 'Source Integration',
          description: 'Automatic citation and source reference',
          details: [
            'Relevant URL selection',
            'Natural citation insertion',
            'Source attribution',
            'Evidence-backed content',
            'Reference management'
          ],
          imagePlaceholder: '/images/content-sources.jpg'
        },
        {
          title: 'Medium Blog Mode',
          description: 'Quick generation for Medium-style articles',
          details: [
            'Single-call full blog generation',
            'Medium-optimized formatting',
            'Engagement-focused structure',
            'SEO-ready output',
            'Fast turnaround option'
          ],
          imagePlaceholder: '/images/content-medium.jpg'
        }
      ],
      technicalDetails: {
        aiModel: 'Provider-agnostic (Gemini/HF via main_text_generation)',
        promptType: 'Context-aware section prompt with research',
        outputFormat: 'Markdown content with transitions and metrics',
        integration: 'EnhancedContentGenerator with ContextMemory'
      },
      videoPlaceholder: '/videos/phase3-content.mp4'
    },
    {
      id: 'seo',
      name: 'SEO Analysis',
      icon: '📈',
      shortDescription: 'Advanced SEO analysis with actionable recommendations and AI-powered optimization',
      features: [
        {
          title: 'Comprehensive SEO Scoring',
          description: 'Multi-dimensional SEO analysis across key factors',
          details: [
            'Overall SEO score (0-100)',
            'Structure optimization score',
            'Keyword optimization rating',
            'Readability assessment',
            'Quality metrics evaluation'
          ],
          imagePlaceholder: '/images/seo-scoring.jpg'
        },
        {
          title: 'Actionable Recommendations',
          description: 'AI-powered improvement suggestions',
          details: [
            'Priority-ranked fixes',
            'Specific text improvements',
            'Keyword density optimization',
            'Heading structure suggestions',
            'Content enhancement ideas'
          ],
          imagePlaceholder: '/images/seo-recommendations.jpg'
        },
        {
          title: 'AI-Powered Content Refinement',
          description: 'Automatically apply SEO recommendations',
          details: [
            'Smart content rewriting',
            'Preserves original intent',
            'Natural keyword integration',
            'Readability improvement',
            'Structure optimization'
          ],
          imagePlaceholder: '/images/seo-apply.jpg'
        },
        {
          title: 'Keyword Analysis',
          description: 'Deep dive into keyword performance',
          details: [
            'Primary keyword density',
            'Semantic keyword usage',
            'Long-tail keyword opportunities',
            'Keyword distribution heatmap',
            'Optimization recommendations'
          ],
          imagePlaceholder: '/images/seo-keywords.jpg'
        }
      ],
      technicalDetails: {
        aiModel: 'Parallel non-AI analyzers + single AI call',
        promptType: 'Structured SEO analysis prompt',
        outputFormat: 'Comprehensive SEO report with scores and recommendations',
        integration: 'BlogContentSEOAnalyzer with parallel processing'
      },
      videoPlaceholder: '/videos/phase4-seo.mp4'
    },
    {
      id: 'metadata',
      name: 'SEO Metadata',
      icon: '🎯',
      shortDescription: 'Optimized metadata generation for titles, descriptions, Open Graph, Twitter cards, and structured data',
      features: [
        {
          title: 'Comprehensive Metadata',
          description: 'All-in-one SEO metadata generation',
          details: [
            'SEO-optimized title (50-60 chars)',
            'Meta description with CTA',
            'URL slug optimization',
            'Blog tags and categories',
            'Social hashtags'
          ],
          imagePlaceholder: '/images/metadata-comprehensive.jpg'
        },
        {
          title: 'Open Graph & Twitter Cards',
          description: 'Rich social media previews',
          details: [
            'OG title and description',
            'Twitter card optimization',
            'Image preview settings',
            'Social engagement boost',
            'Click-through optimization'
          ],
          imagePlaceholder: '/images/metadata-social.jpg'
        },
        {
          title: 'Structured Data',
          description: 'Schema.org markup for rich snippets',
          details: [
            'Article schema',
            'Organization markup',
            'Breadcrumb schema',
            'FAQ schema support',
            'Enhanced search results'
          ],
          imagePlaceholder: '/images/metadata-schema.jpg'
        },
        {
          title: 'Multi-Format Output',
          description: 'Ready-to-use metadata in all formats',
          details: [
            'HTML meta tags',
            'JSON-LD structured data',
            'WordPress export format',
            'Wix integration format',
            'One-click copy options'
          ],
          imagePlaceholder: '/images/metadata-export.jpg'
        }
      ],
      technicalDetails: {
        aiModel: 'Maximum 2 AI calls for comprehensive metadata',
        promptType: 'Personalized metadata prompt with context',
        outputFormat: 'Complete metadata package (title, desc, tags, schema)',
        integration: 'BlogSEOMetadataGenerator with optimization'
      },
      videoPlaceholder: '/videos/phase5-metadata.mp4'
    },
    {
      id: 'publish',
      name: 'Publish & Distribute',
      icon: '🚀',
      shortDescription: 'Direct publishing to WordPress, Wix, Medium, and other platforms with scheduling',
      features: [
        {
          title: 'Multi-Platform Publishing',
          description: 'Publish to multiple platforms simultaneously',
          details: [
            'WordPress direct publishing',
            'Wix blog integration',
            'Medium publishing',
            'Custom blog platforms',
            'API integrations'
          ],
          imagePlaceholder: '/images/publish-platforms.jpg'
        },
        {
          title: 'Content Scheduling',
          description: 'Schedule posts for optimal timing',
          details: [
            'Time-based scheduling',
            'Timezone management',
            'Bulk scheduling support',
            'Calendar integration',
            'Reminder notifications'
          ],
          imagePlaceholder: '/images/publish-schedule.jpg'
        },
        {
          title: 'Revision Management',
          description: 'Track and manage content versions',
          details: [
            'Version history',
            'Change tracking',
            'Rollback capabilities',
            'A/B testing support',
            'Performance comparison'
          ],
          imagePlaceholder: '/images/publish-versions.jpg'
        },
        {
          title: 'Analytics Integration',
          description: 'Post-publish performance tracking',
          details: [
            'View count tracking',
            'Engagement metrics',
            'SEO performance',
            'Traffic analysis',
            'Conversion tracking'
          ],
          imagePlaceholder: '/images/publish-analytics.jpg'
        }
      ],
      technicalDetails: {
        aiModel: 'Platform-specific API integrations',
        promptType: 'N/A - publishing only',
        outputFormat: 'Published content with URL',
        integration: 'Platform APIs via Publisher component'
      },
      videoPlaceholder: '/videos/phase6-publish.mp4'
    }
  ];

  return (
    <Box sx={{ py: 8, bgcolor: 'background.paper' }}>
      <Container maxWidth="lg">
        {/* Section Title */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography 
            variant="h2" 
            component="h2" 
            sx={{ 
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 700,
              background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2
            }}
          >
            Complete AI Blog Writing Workflow
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: '800px', mx: 'auto' }}>
            Six powerful phases that transform your ideas into SEO-optimized, engaging blog content
          </Typography>
        </Box>

        {/* Phase Cards */}
        <Grid container spacing={4}>
          {phases.map((phase, index) => (
            <Grid item xs={12} md={6} key={phase.id}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: activePhase === index ? 2 : 1,
                  borderColor: activePhase === index ? 'primary.main' : 'divider',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: 6,
                  }
                }}
                onClick={() => setActivePhase(activePhase === index ? null : index)}
              >
                <CardContent sx={{ p: 3 }}>
                  <Stack direction="row" spacing={2} alignItems="flex-start" mb={2}>
                    <Typography variant="h2" sx={{ fontSize: '3rem' }}>
                      {phase.icon}
                    </Typography>
                    <Box flex={1}>
                      <Typography variant="h5" fontWeight={600} gutterBottom>
                        {phase.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {phase.shortDescription}
                      </Typography>
                    </Box>
                    <Chip 
                      label={`Phase ${index + 1}`} 
                      size="small" 
                      color="primary"
                      variant="outlined"
                    />
                  </Stack>

                  {activePhase === index && (
                    <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
                      {/* Video Placeholder */}
                      <Box 
                        sx={{ 
                          width: '100%', 
                          aspectRatio: '16/9',
                          bgcolor: 'grey.200',
                          borderRadius: 2,
                          mb: 3,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        <Typography variant="body2" color="text.secondary">
                          🎥 Video: {phase.videoPlaceholder}
                        </Typography>
                      </Box>

                      {/* Features Grid */}
                      <Grid container spacing={2} mb={3}>
                        {phase.features.map((feature, idx) => (
                          <Grid item xs={12} sm={6} key={idx}>
                            <Card variant="outlined" sx={{ p: 2, height: '100%' }}>
                              <Box 
                                sx={{ 
                                  width: '100%', 
                                  aspectRatio: '4/3',
                                  bgcolor: 'grey.100',
                                  borderRadius: 1,
                                  mb: 2,
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center'
                                }}
                              >
                                <Typography variant="caption" color="text.secondary">
                                  📷 Image
                                </Typography>
                              </Box>
                              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                {feature.title}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" mb={1}>
                                {feature.description}
                              </Typography>
                              <Stack spacing={0.5}>
                                {feature.details.slice(0, 3).map((detail, i) => (
                                  <Stack key={i} direction="row" spacing={1} alignItems="flex-start">
                                    <CheckCircle sx={{ fontSize: 16, color: 'success.main', mt: 0.5 }} />
                                    <Typography variant="caption" color="text.secondary">
                                      {detail}
                                    </Typography>
                                  </Stack>
                                ))}
                              </Stack>
                            </Card>
                          </Grid>
                        ))}
                      </Grid>

                      {/* Technical Details */}
                      <Card variant="outlined" sx={{ bgcolor: 'grey.50', p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={600} mb={1} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <AutoAwesome sx={{ fontSize: 18 }} />
                          Technical Implementation
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" fontWeight={600}>AI Model</Typography>
                            <Typography variant="body2">{phase.technicalDetails.aiModel}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" fontWeight={600}>Output Format</Typography>
                            <Typography variant="body2">{phase.technicalDetails.outputFormat}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" fontWeight={600}>Prompt Type</Typography>
                            <Typography variant="body2">{phase.technicalDetails.promptType}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" fontWeight={600}>Integration</Typography>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                              {phase.technicalDetails.integration}
                            </Typography>
                          </Grid>
                        </Grid>
                      </Card>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default BlogWriterPhasesSection;

