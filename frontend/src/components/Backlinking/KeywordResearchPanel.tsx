/**
 * Keyword Research Panel - Ported from Legacy Backlinker
 *
 * AI-powered keyword research interface with volume analysis,
 * difficulty assessment, and opportunity discovery.
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  TextField,
  Chip,
  IconButton,
  Grid,
  Badge,
  Avatar,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Search as SearchIcon,
  SmartToy as BrainIcon,
  TrendingUp as TrendingUpIcon,
  Add as AddIcon,
  Bolt as FlashIcon,
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  Insights as InsightsIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { BacklinkingStyles } from './styles/backlinkingStyles';
import { useBacklinking } from '../../hooks/useBacklinking';

interface KeywordData {
  term: string;
  volume: number;
  difficulty: 'Low' | 'Medium' | 'High';
  opportunities: number;
  trend?: 'up' | 'down' | 'stable';
  relevanceScore?: number;
}

interface KeywordResearchPanelProps {
  campaignId?: string;
  onKeywordSelect?: (keywords: string[]) => void;
  maxKeywords?: number;
  showHeader?: boolean;
}

const sampleKeywords: KeywordData[] = [
  { term: "AI content marketing", volume: 12500, difficulty: "Medium", opportunities: 45, trend: "up", relevanceScore: 0.92 },
  { term: "SEO automation tools", volume: 8900, difficulty: "High", opportunities: 23, trend: "up", relevanceScore: 0.85 },
  { term: "Content optimization", volume: 15600, difficulty: "Low", opportunities: 67, trend: "stable", relevanceScore: 0.88 },
  { term: "Digital marketing AI", volume: 9800, difficulty: "Medium", opportunities: 34, trend: "up", relevanceScore: 0.79 },
  { term: "Automated link building", volume: 7200, difficulty: "High", opportunities: 18, trend: "up", relevanceScore: 0.81 },
  { term: "Neural content creation", volume: 5400, difficulty: "Medium", opportunities: 29, trend: "up", relevanceScore: 0.76 },
];

const getDifficultyColor = (difficulty: string) => {
  switch (difficulty) {
    case 'Low': return '#10B981'; // green
    case 'Medium': return '#F59E0B'; // amber
    case 'High': return '#EF4444'; // red
    default: return '#6B7280'; // gray
  }
};

const getDifficultyBgColor = (difficulty: string) => {
  switch (difficulty) {
    case 'Low': return alpha('#10B981', 0.1);
    case 'Medium': return alpha('#F59E0B', 0.1);
    case 'High': return alpha('#EF4444', 0.1);
    default: return alpha('#6B7280', 0.1);
  }
};

const KeywordCard: React.FC<{ keyword: KeywordData; onClick?: () => void }> = ({ keyword, onClick }) => {
  const theme = useTheme();

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        sx={{
          cursor: onClick ? 'pointer' : 'default',
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 8px 25px rgba(96, 165, 250, 0.2)',
            borderColor: 'rgba(96, 165, 250, 0.3)',
          },
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `radial-gradient(circle at 30% 30%, ${alpha('#60A5FA', 0.05)} 0%, transparent 70%)`,
            pointerEvents: 'none',
          },
        }}
        onClick={onClick}
      >
        <CardContent sx={{ p: 2, position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9', fontSize: '0.9rem' }}>
              {keyword.term}
            </Typography>
            <Chip
              label={keyword.difficulty}
              size="small"
              sx={{
                backgroundColor: getDifficultyBgColor(keyword.difficulty),
                color: getDifficultyColor(keyword.difficulty),
                border: `1px solid ${alpha(getDifficultyColor(keyword.difficulty), 0.3)}`,
                fontSize: '0.7rem',
                height: 20,
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AnalyticsIcon sx={{ fontSize: 14, color: 'rgba(203, 213, 225, 0.7)' }} />
              <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                {keyword.volume.toLocaleString()} vol
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUpIcon sx={{
                fontSize: 14,
                color: keyword.trend === 'up' ? '#10B981' : keyword.trend === 'down' ? '#EF4444' : '#F59E0B'
              }} />
              <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                {keyword.opportunities} ops
              </Typography>
            </Box>
          </Box>

          {keyword.relevanceScore && (
            <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PsychologyIcon sx={{ fontSize: 12, color: '#60A5FA' }} />
              <Typography variant="caption" sx={{ color: '#60A5FA', fontSize: '0.7rem' }}>
                {Math.round(keyword.relevanceScore * 100)}% relevant
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export const KeywordResearchPanel: React.FC<KeywordResearchPanelProps> = ({
  campaignId,
  onKeywordSelect,
  maxKeywords = 10,
  showHeader = true,
}) => {
  const navigate = useNavigate();
  const theme = useTheme();

  const [keywords, setKeywords] = useState<KeywordData[]>(sampleKeywords);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [expanded, setExpanded] = useState<string | false>('research');
  const [researchResults, setResearchResults] = useState<KeywordData[]>([]);

  // AI keyword research with backlinking integration
  const handleAIResearch = async () => {
    if (!searchQuery.trim()) return;

    setIsResearching(true);

    try {
      // Simulate AI research process (in production, this would call the actual research service)
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Generate AI-powered keyword suggestions
      const newKeywords: KeywordData[] = [
        {
          term: `${searchQuery} automation`,
          volume: Math.floor(Math.random() * 10000) + 5000,
          difficulty: 'Medium' as const,
          opportunities: Math.floor(Math.random() * 50) + 20,
          trend: 'up' as const,
          relevanceScore: 0.85 + Math.random() * 0.1,
        },
        {
          term: `AI-powered ${searchQuery}`,
          volume: Math.floor(Math.random() * 8000) + 3000,
          difficulty: 'High' as const,
          opportunities: Math.floor(Math.random() * 30) + 10,
          trend: 'up' as const,
          relevanceScore: 0.75 + Math.random() * 0.15,
        },
        {
          term: `${searchQuery} optimization`,
          volume: Math.floor(Math.random() * 6000) + 2000,
          difficulty: 'Low' as const,
          opportunities: Math.floor(Math.random() * 40) + 15,
          trend: 'stable' as const,
          relevanceScore: 0.80 + Math.random() * 0.1,
        },
      ];

      setResearchResults(newKeywords);
      setKeywords(prev => [...newKeywords, ...prev.slice(0, 3)]);

    } catch (error) {
    } finally {
      setIsResearching(false);
    }
  };

  const handleKeywordToggle = (keyword: string) => {
    setSelectedKeywords(prev => {
      const newSelected = prev.includes(keyword)
        ? prev.filter(k => k !== keyword)
        : [...prev, keyword].slice(0, maxKeywords);

      onKeywordSelect?.(newSelected);
      return newSelected;
    });
  };

  const filteredKeywords = keywords.filter(keyword =>
    keyword.term.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.5 }}
    >
      <Card sx={{
        ...BacklinkingStyles.campaignCard,
        minHeight: 500,
        position: 'relative',
      }}>
        {showHeader && (
          <CardHeader sx={BacklinkingStyles.campaignCardHeader}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{
                  bgcolor: 'rgba(96, 165, 250, 0.1)',
                  border: '1px solid rgba(96, 165, 250, 0.3)',
                }}>
                  <SearchIcon sx={{ color: '#60A5FA' }} />
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
                    AI Keyword Research
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Discover high-value keywords with AI-powered analysis
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Badge
                  badgeContent={selectedKeywords.length}
                  color="primary"
                  sx={{
                    '& .MuiBadge-badge': {
                      background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
                    },
                  }}
                >
                  <Chip
                    label={`${filteredKeywords.length} Available`}
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(96, 165, 250, 0.1)',
                      color: '#60A5FA',
                      border: '1px solid rgba(96, 165, 250, 0.3)',
                    }}
                  />
                </Badge>

                <Chip
                  icon={<InsightsIcon />}
                  label={`${filteredKeywords.reduce((sum, k) => sum + k.opportunities, 0)} Opportunities`}
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    color: '#06B6D4',
                    border: '1px solid rgba(6, 182, 212, 0.3)',
                  }}
                />
              </Box>
            </Box>
          </CardHeader>
        )}

        <CardContent sx={{ ...BacklinkingStyles.campaignCardContent, p: 0 }}>
          <Accordion
            expanded={expanded === 'research'}
            onChange={() => setExpanded(expanded === 'research' ? false : 'research')}
            sx={{
              background: 'transparent',
              boxShadow: 'none',
              '&:before': { display: 'none' },
              '& .MuiAccordionSummary-root': {
                background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)',
                borderRadius: 2,
                mx: 2,
                mt: 2,
                minHeight: 64,
              },
              '& .MuiAccordionSummary-content': {
                alignItems: 'center',
              },
              '& .MuiAccordionDetails-root': {
                px: 2,
                pb: 2,
              },
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#60A5FA' }} />}
              sx={{
                '&:hover': {
                  background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Avatar sx={{
                  bgcolor: 'rgba(96, 165, 250, 0.1)',
                  border: '1px solid rgba(96, 165, 250, 0.3)',
                }}>
                  <BrainIcon sx={{ color: '#60A5FA' }} />
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9' }}>
                    AI Research & Suggestions
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Live AI-powered keyword discovery and analysis
                  </Typography>
                </Box>
                <Chip
                  label="Live"
                  size="small"
                  sx={{
                    background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                    color: 'white',
                    fontSize: '0.7rem',
                    animation: 'pulse 2s ease-in-out infinite',
                  }}
                />
              </Box>
            </AccordionSummary>

            <AccordionDetails>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Search Input */}
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    placeholder="Enter keywords or domain for AI research..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        background: 'rgba(30, 41, 59, 0.6)',
                        borderRadius: 2,
                        '& fieldset': { borderColor: 'rgba(96, 165, 250, 0.3)' },
                        '&:hover fieldset': { borderColor: 'rgba(96, 165, 250, 0.5)' },
                        '&.Mui-focused fieldset': { borderColor: '#60A5FA' },
                      },
                      '& .MuiInputBase-input': {
                        color: '#F1F5F9',
                        '&::placeholder': { color: 'rgba(203, 213, 225, 0.5)' },
                      },
                    }}
                  />
                  <IconButton
                    onClick={handleAIResearch}
                    disabled={isResearching || !searchQuery.trim()}
                    sx={{
                      background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
                      color: 'white',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #3B82F6 0%, #9333EA 100%)',
                        transform: 'scale(1.05)',
                      },
                      '&:disabled': {
                        background: 'rgba(107, 114, 128, 0.5)',
                        color: 'rgba(255, 255, 255, 0.5)',
                      },
                    }}
                  >
                    {isResearching ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      >
                        <BrainIcon />
                      </motion.div>
                    ) : (
                      <BrainIcon />
                    )}
                  </IconButton>
                </Box>

                {/* Selected Keywords */}
                {selectedKeywords.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ mb: 1, color: '#F1F5F9', fontWeight: 600 }}>
                      Selected Keywords ({selectedKeywords.length}/{maxKeywords})
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {selectedKeywords.map(keyword => (
                        <Chip
                          key={keyword}
                          label={keyword}
                          onDelete={() => handleKeywordToggle(keyword)}
                          sx={{
                            background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)',
                            color: '#60A5FA',
                            border: '1px solid rgba(96, 165, 250, 0.3)',
                            '&:hover': {
                              background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.3) 0%, rgba(168, 85, 247, 0.3) 100%)',
                            },
                            '& .MuiChip-deleteIcon': {
                              color: '#60A5FA',
                              '&:hover': {
                                color: '#3B82F6',
                              },
                            },
                          }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Research Results Indicator */}
                {researchResults.length > 0 && (
                  <Box sx={{
                    mb: 3,
                    p: 2,
                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: 2,
                  }}>
                    <Typography variant="subtitle2" sx={{ color: '#10B981', fontWeight: 600, mb: 1 }}>
                      🎯 AI Research Complete!
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
                      Found {researchResults.length} high-potential keywords for "{searchQuery}"
                    </Typography>
                  </Box>
                )}

                {/* Keywords Grid */}
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ color: '#F1F5F9', fontWeight: 600 }}>
                      Keyword Analysis Results
                    </Typography>
                    <Button
                      size="small"
                      startIcon={<AddIcon />}
                      sx={{
                        color: '#60A5FA',
                        '&:hover': {
                          backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        },
                      }}
                    >
                      Add Custom
                    </Button>
                  </Box>

                  <Grid container spacing={2}>
                    <AnimatePresence>
                      {filteredKeywords.map((keyword, index) => (
                        <Grid item xs={12} sm={6} key={keyword.term}>
                          <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1, duration: 0.3 }}
                          >
                            <KeywordCard
                              keyword={keyword}
                              onClick={() => handleKeywordToggle(keyword.term)}
                            />
                          </motion.div>
                        </Grid>
                      ))}
                    </AnimatePresence>
                  </Grid>
                </Box>

                {/* Action Button */}
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<FlashIcon />}
                  onClick={() => navigate('/backlinking/new-campaign')}
                  sx={{
                    mt: 2,
                    background: 'linear-gradient(135deg, #06B6D4 0%, #60A5FA 50%, #A855F7 100%)',
                    boxShadow: '0 4px 15px rgba(6, 182, 212, 0.4)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #0891B2 0%, #3B82F6 50%, #9333EA 100%)',
                      boxShadow: '0 6px 20px rgba(6, 182, 212, 0.6)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                >
                  Start New Research Campaign
                </Button>
              </Box>
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>
  );
};