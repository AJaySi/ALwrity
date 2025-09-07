import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Tooltip,
  Modal,
  IconButton,
  Chip,
  Stack,
  Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { keyframes } from '@mui/system';
import {
  CheckCircle as CheckIcon,
  WarningAmber as WarningIcon,
  Error as ErrorIcon,
  Close as CloseIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface Insight {
  id: string;
  title: string;
  description: string;
  metric: string;
  value: string;
  trend: 'up' | 'down' | 'stable';
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: 'engagement' | 'reach' | 'conversion' | 'seo' | 'content';
  platform: 'facebook' | 'linkedin' | 'twitter' | 'instagram' | 'website';
  detailedAnalysis: string;
  recommendations: string[];
  impact: string;
  timeframe: string;
}

interface AnalyticsData {
  theGood: Insight[];
  theBad: Insight[];
  theUgly: Insight[];
}

interface AnalyticsInsightsProps {
  data?: AnalyticsData; // optional - falls back to mock
  onActionClick?: (action: 'alwrity' | 'ignore', insight: Insight) => void;
}

const ColumnCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(180deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0.08) 100%)',
  border: '1px solid rgba(255,255,255,0.16)',
  backdropFilter: 'blur(18px)',
  WebkitBackdropFilter: 'blur(18px)',
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
  boxShadow: '0 8px 20px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.22)',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-3px)',
    boxShadow: '0 12px 28px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.28)'
  }
}));

const Pill = styled('div')<{ color: string }>(() => ({
  width: 10,
  height: 10,
  borderRadius: 6,
}));

const GradientHeader = styled(Box)<{ gradient: string }>(({ gradient }) => ({
  background: gradient,
  padding: '8px 12px',
  color: 'white',
  display: 'flex',
  alignItems: 'center',
  gap: 6,
}));

const Badge = styled('span')(({ theme }) => ({
  background: 'rgba(255,255,255,0.15)',
  border: '1px solid rgba(255,255,255,0.35)',
  color: 'white',
  borderRadius: 999,
  padding: '1px 6px',
  fontWeight: 700,
  fontSize: '0.65rem'
}));


const mockData: AnalyticsData = {
  theGood: [
    {
      id: 'good-1',
      title: 'LinkedIn Engagement Surge',
      description: 'LinkedIn engagement is up significantly this week.',
      metric: 'Engagement Rate',
      value: '+45%',
      trend: 'up',
      priority: 'high',
      category: 'engagement',
      platform: 'linkedin',
      detailedAnalysis: 'Recent posts on AI topics resonated strongly with your B2B audience.',
      recommendations: ['Post 3x/week on AI trends', 'Engage with comments within 2 hours'],
      impact: 'High lead-gen potential',
      timeframe: 'Last 7 days'
    },
    {
      id: 'good-2',
      title: 'Website Traffic Growth',
      description: 'Organic traffic increased due to improved SEO.',
      metric: 'Organic Traffic',
      value: '+23%',
      trend: 'up',
      priority: 'medium',
      category: 'seo',
      platform: 'website',
      detailedAnalysis: 'Technical fixes and content refresh improved rankings.',
      recommendations: ['Create 2 pillar pages', 'Refresh 5 top posts'],
      impact: 'Improved visibility',
      timeframe: 'Last 30 days'
    },
    {
      id: 'good-3',
      title: 'Top-Performing Post',
      description: 'A recent LinkedIn post outperformed baseline by 2.1x',
      metric: 'Engagement Index',
      value: '2.1x',
      trend: 'up',
      priority: 'medium',
      category: 'engagement',
      platform: 'linkedin',
      detailedAnalysis: 'Carousel format and thought leadership angle worked well.',
      recommendations: ['Use carousel weekly', 'Add CTA to subscribe'],
      impact: 'Audience growth',
      timeframe: 'This week'
    }
  ],
  theBad: [
    {
      id: 'bad-1',
      title: 'Facebook Reach Decline',
      description: 'Facebook post reach dropped this month.',
      metric: 'Reach',
      value: '-18%',
      trend: 'down',
      priority: 'medium',
      category: 'reach',
      platform: 'facebook',
      detailedAnalysis: 'Algorithm change likely impacting page distribution.',
      recommendations: ['Test short video posts', 'Boost first-hour engagement'],
      impact: 'Lower awareness',
      timeframe: 'Last 30 days'
    },
    {
      id: 'bad-2',
      title: 'Email CTR Stagnant',
      description: 'Content CTR plateaued across campaigns.',
      metric: 'CTR',
      value: '0.9%',
      trend: 'stable',
      priority: 'low',
      category: 'content',
      platform: 'website',
      detailedAnalysis: 'Subject lines lack urgency; preview text uninspiring.',
      recommendations: ['A/B test subject lines', 'Add curiosity hook'],
      impact: 'Reduced visits',
      timeframe: 'Last 14 days'
    }
  ],
  theUgly: [
    {
      id: 'ugly-1',
      title: 'Critical SEO Issues',
      description: '15 pages have broken internal links.',
      metric: 'Broken Links',
      value: '15 pages',
      trend: 'down',
      priority: 'critical',
      category: 'seo',
      platform: 'website',
      detailedAnalysis: 'Broken links hurt crawlability and user experience.',
      recommendations: ['Fix links immediately', 'Add automated link checks'],
      impact: 'Severe ranking risk',
      timeframe: 'Ongoing'
    },
    {
      id: 'ugly-2',
      title: 'Declining Conversions',
      description: 'Checkout conversion dropped vs prior month.',
      metric: 'CVR',
      value: '-12%',
      trend: 'down',
      priority: 'high',
      category: 'conversion',
      platform: 'website',
      detailedAnalysis: 'Funnel analysis shows friction on payment step.',
      recommendations: ['Simplify checkout', 'Add alternate payment'],
      impact: 'Direct revenue impact',
      timeframe: 'Last 30 days'
    }
  ]
};

const getGradient = (type: 'good' | 'bad' | 'ugly') => {
  switch (type) {
    case 'good':
      return 'linear-gradient(135deg, rgba(76,175,80,0.55) 0%, rgba(139,195,74,0.55) 100%)';
    case 'bad':
      return 'linear-gradient(135deg, rgba(255,152,0,0.55) 0%, rgba(245,124,0,0.55) 100%)';
    default:
      return 'linear-gradient(135deg, rgba(244,67,54,0.55) 0%, rgba(233,30,99,0.55) 100%)';
  }
};

const getIcon = (type: 'good' | 'bad' | 'ugly') => {
  switch (type) {
    case 'good':
      return <CheckIcon />;
    case 'bad':
      return <WarningIcon />;
    default:
      return <ErrorIcon />;
  }
};

const TrendChip: React.FC<{ trend: Insight['trend'] }> = ({ trend }) => {
  if (trend === 'up') return <Chip size="small" icon={<TrendingUpIcon />} label="Up" sx={{ color: '#4CAF50', background: '#4CAF5022', border: '1px solid #4CAF5044', fontWeight: 700, fontSize: '0.6rem', height: 18 }} />;
  if (trend === 'down') return <Chip size="small" icon={<TrendingDownIcon />} label="Down" sx={{ color: '#F44336', background: '#F4433622', border: '1px solid #F4433644', fontWeight: 700, fontSize: '0.6rem', height: 18 }} />;
  return <Chip size="small" icon={<InfoIcon />} label="Stable" sx={{ color: '#90CAF9', background: '#90CAF922', border: '1px solid #90CAF944', fontWeight: 700, fontSize: '0.6rem', height: 18 }} />;
};

const AnalyticsInsights: React.FC<AnalyticsInsightsProps> = ({ data, onActionClick }) => {
  const [hovered, setHovered] = React.useState<'good' | 'bad' | 'ugly' | null>(null);
  const [open, setOpen] = React.useState(false);
  const [selected, setSelected] = React.useState<Insight | null>(null);

  const insights = data || mockData;

  const columns: Array<{ key: 'good' | 'bad' | 'ugly'; title: string; items: Insight[] }> = [
    { key: 'good', title: 'The Good', items: insights.theGood },
    { key: 'bad', title: 'The Bad', items: insights.theBad },
    { key: 'ugly', title: 'The Ugly', items: insights.theUgly },
  ];

  const handleKnowMore = (insight: Insight) => {
    setSelected(insight);
    setOpen(true);
  };

  const handleClose = () => setOpen(false);

  const handleAction = (action: 'alwrity' | 'ignore') => {
    if (selected && onActionClick) {
      onActionClick(action, selected);
    }
    setOpen(false);
  };

  return (
    <Box sx={{ mt: 2, mb: 2.9 }}>
      <Box sx={{ position: 'relative', overflow: 'hidden' }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 800,
            mb: 1.5,
            fontSize: '1.1rem',
            color: 'rgba(255,255,255,0.95)',
          }}
        >
          Today's Analytics Insights
        </Typography>
      </Box>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
        {columns.map((col) => {
          const isHovered = hovered === col.key;
          const visibleItems = isHovered ? col.items : col.items.slice(0, 1);
          const gradient = getGradient(col.key);
          return (
            <motion.div key={col.key} style={{ flex: 1 }} onMouseEnter={() => setHovered(col.key)} onMouseLeave={() => setHovered(null)}>
              <ColumnCard>
                <GradientHeader gradient={gradient}>
                  {getIcon(col.key)}
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, fontSize: '0.9rem' }}>{col.title}</Typography>
                  <Badge>{col.items.length}</Badge>
                </GradientHeader>

                <CardContent sx={{ p: 1.5 }}>
                  <Stack spacing={1}>
                    {visibleItems.map((insight) => (
                      <Box key={insight.id} sx={{
                        background: 'rgba(255,255,255,0.08)',
                        border: '1px solid rgba(255,255,255,0.18)',
                        borderRadius: 1.5,
                        p: 1
                      }}>
                        <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mb: 0.25 }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.95)', fontWeight: 700, fontSize: '0.8rem' }}>
                            {insight.title}
                          </Typography>
                          <TrendChip trend={insight.trend} />
                        </Stack>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.7rem', lineHeight: 1.2 }}>
                          {insight.description}
                        </Typography>
                        <Stack direction="row" spacing={0.5} sx={{ mt: 0.5 }}>
                          <Chip size="small" label={`${insight.metric}: ${insight.value}`} sx={{ color: 'rgba(255,255,255,0.95)', background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.24)', fontWeight: 700, fontSize: '0.65rem', height: 20 }} />
                          <Chip size="small" label={insight.platform} sx={{ color: 'rgba(255,255,255,0.85)', background: 'rgba(255,255,255,0.08)', fontSize: '0.65rem', height: 20 }} />
                        </Stack>
                      </Box>
                    ))}
                  </Stack>

                  {isHovered && (
                    <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
                      <Tooltip title={`Open detailed insights for ${col.title.toLowerCase()}.`}>
                        <span>
                          <Button
                            variant="contained"
                            onClick={() => handleKnowMore(col.items[0])}
                            size="small"
                            sx={{
                              textTransform: 'none',
                              fontWeight: 800,
                              background: gradient,
                              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                              fontSize: '0.75rem',
                              px: 2,
                              py: 0.5
                            }}
                          >
                            Know More
                          </Button>
                        </span>
                      </Tooltip>
                    </Box>
                  )}
                </CardContent>
              </ColumnCard>
            </motion.div>
          );
        })}
      </Stack>

      <Modal open={open} onClose={handleClose}>
        <Box sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: { xs: '92%', md: 900 },
          maxHeight: '80vh',
          overflowY: 'auto',
          background: 'linear-gradient(180deg, rgba(16,24,39,0.92) 0%, rgba(26,33,56,0.92) 100%)',
          border: '1px solid rgba(255,255,255,0.18)',
          borderRadius: 3,
          boxShadow: '0 26px 80px rgba(0,0,0,0.5)'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 2.5, borderBottom: '1px solid rgba(255,255,255,0.15)' }}>
            <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.95)', fontWeight: 800 }}>
              {selected?.title}
            </Typography>
            <IconButton onClick={handleClose} sx={{ color: 'rgba(255,255,255,0.85)' }}>
              <CloseIcon />
            </IconButton>
          </Box>

          <CardContent>
            <Stack spacing={1.5}>
              <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                {selected?.detailedAnalysis}
              </Typography>
              <Stack direction="row" spacing={1}>
                <Chip size="small" label={`${selected?.metric}: ${selected?.value}`} sx={{ color: 'rgba(255,255,255,0.95)', background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.24)', fontWeight: 700 }} />
                {selected?.platform && (
                  <Chip size="small" label={selected.platform} sx={{ color: 'rgba(255,255,255,0.85)', background: 'rgba(255,255,255,0.08)' }} />
                )}
                {selected?.impact && (
                  <Chip size="small" label={`Impact: ${selected.impact}`} sx={{ color: 'rgba(255,255,255,0.85)', background: 'rgba(255,255,255,0.08)' }} />
                )}
              </Stack>

              <Divider sx={{ my: 1.5, borderColor: 'rgba(255,255,255,0.15)' }} />
              <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.9)', fontWeight: 800 }}>
                Recommendations
              </Typography>
              <Stack spacing={0.75}>
                {selected?.recommendations.map((rec, idx) => (
                  <Typography key={idx} variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>• {rec}</Typography>
                ))}
              </Stack>

              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1.5, mt: 2 }}>
                <Tooltip title="Save this as a memory for ALwrity AI to take action automatically.">
                  <span>
                    <Button variant="contained" color="success" onClick={() => handleAction('alwrity')} sx={{ textTransform: 'none', fontWeight: 800 }}>
                      ALwrity it
                    </Button>
                  </span>
                </Tooltip>
                <Tooltip title="Dismiss for now. You can revisit later in analytics.">
                  <span>
                    <Button variant="outlined" color="inherit" onClick={() => handleAction('ignore')} sx={{ textTransform: 'none', fontWeight: 800 }}>
                      Ignore it
                    </Button>
                  </span>
                </Tooltip>
              </Box>
            </Stack>
          </CardContent>
        </Box>
      </Modal>
    </Box>
  );
};

export default AnalyticsInsights;


