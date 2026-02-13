/**
 * Campaign Performance Dashboard - Advanced Analytics
 *
 * Comprehensive campaign analytics with AI-powered insights,
 * performance tracking, and optimization recommendations.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Grid,
  Button,
  Chip,
  Avatar,
  Divider,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Alert,
  AlertTitle,
  IconButton,
  Tooltip,
  Badge,
  useTheme,
  useMediaQuery,
  alpha,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  People as PeopleIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  ShowChart as ShowChartIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  FilterList as FilterIcon,
  DateRange as DateRangeIcon,
  Insights as InsightsIcon,
  Lightbulb as LightbulbIcon,
  Warning as WarningIcon,
  ThumbUp as ThumbUpIcon,
  Campaign as CampaignIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { BacklinkingStyles } from './styles/backlinkingStyles';

interface CampaignMetrics {
  campaignId: string;
  campaignName: string;
  status: 'active' | 'paused' | 'completed' | 'draft';
  totalProspects: number;
  emailsSent: number;
  emailsOpened: number;
  emailsClicked: number;
  replies: number;
  bounces: number;
  unsubscribes: number;
  openRate: number;
  clickRate: number;
  replyRate: number;
  bounceRate: number;
  avgResponseTime: number;
  backlinksSecured: number;
  domainAuthority: number;
  startDate: string;
  endDate?: string;
}

interface TimeSeriesData {
  date: string;
  sent: number;
  opened: number;
  clicked: number;
  replied: number;
  backlinks: number;
}

interface CampaignInsight {
  type: 'success' | 'warning' | 'info' | 'opportunity';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  recommendation?: string;
  icon: React.ComponentType<any>;
}

const generateSampleMetrics = (): CampaignMetrics => ({
  campaignId: 'camp-001',
  campaignName: 'AI Tools Guest Posts Q1 2024',
  status: 'active',
  totalProspects: 150,
  emailsSent: 120,
  emailsOpened: 84,
  emailsClicked: 25,
  replies: 18,
  bounces: 3,
  unsubscribes: 2,
  openRate: 70.0,
  clickRate: 20.8,
  replyRate: 15.0,
  bounceRate: 2.5,
  avgResponseTime: 2.3,
  backlinksSecured: 8,
  domainAuthority: 72.5,
  startDate: '2024-01-15',
  endDate: undefined,
});

const generateTimeSeriesData = (): TimeSeriesData[] => [
  { date: '2024-01-15', sent: 15, opened: 12, clicked: 4, replied: 2, backlinks: 0 },
  { date: '2024-01-16', sent: 20, opened: 16, clicked: 5, replied: 3, backlinks: 1 },
  { date: '2024-01-17', sent: 18, opened: 14, clicked: 4, replied: 2, backlinks: 0 },
  { date: '2024-01-18', sent: 25, opened: 19, clicked: 6, replied: 4, backlinks: 2 },
  { date: '2024-01-19', sent: 22, opened: 17, clicked: 5, replied: 3, backlinks: 1 },
  { date: '2024-01-20', sent: 20, opened: 16, clicked: 4, replied: 4, backlinks: 2 },
  { date: '2024-01-21', sent: 0, opened: 0, clicked: 0, replied: 0, backlinks: 2 },
];

const generateInsights = (): CampaignInsight[] => [
  {
    type: 'success',
    title: 'Exceptional Open Rate',
    description: 'Your 70% open rate is 40% above industry average for outreach emails.',
    impact: 'high',
    recommendation: 'Consider A/B testing subject lines to further improve engagement.',
    icon: TrendingUpIcon,
  },
  {
    type: 'opportunity',
    title: 'Reply Rate Optimization',
    description: '15% reply rate shows strong engagement. Focus on high-DA prospects (70+) for better conversion.',
    impact: 'high',
    recommendation: 'Prioritize prospects with DA > 70 and recent content updates.',
    icon: LightbulbIcon,
  },
  {
    type: 'warning',
    title: 'Response Time Analysis',
    description: 'Average 2.3 days response time could be improved with follow-up sequences.',
    impact: 'medium',
    recommendation: 'Implement automated follow-up emails 3-5 days after initial outreach.',
    icon: ScheduleIcon,
  },
  {
    type: 'info',
    title: 'Backlink Conversion',
    description: '8 backlinks secured represents 6.7% conversion rate from sent emails.',
    impact: 'medium',
    recommendation: 'Excellent performance! Continue targeting similar prospect profiles.',
    icon: CheckCircleIcon,
  },
];

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
  </div>
);

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ComponentType<any>;
  color: string;
  subtitle?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  color,
  subtitle,
}) => {
  const getChangeColor = (type: string) => {
    switch (type) {
      case 'positive':
        return '#10B981';
      case 'negative':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{
        height: '100%',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 2,
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `radial-gradient(circle at 30% 30%, ${alpha(color, 0.08)} 0%, transparent 70%)`,
          pointerEvents: 'none',
        },
      }}>
        <CardContent sx={{ p: 2.5, position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Avatar sx={{
              bgcolor: alpha(color, 0.1),
              border: `1px solid ${alpha(color, 0.3)}`,
              width: 40,
              height: 40,
            }}>
              <Icon sx={{ color, fontSize: 20 }} />
            </Avatar>
            {change && (
              <Chip
                label={change}
                size="small"
                sx={{
                  bgcolor: alpha(getChangeColor(changeType), 0.1),
                  color: getChangeColor(changeType),
                  border: `1px solid ${alpha(getChangeColor(changeType), 0.3)}`,
                  fontSize: '0.7rem',
                  height: 20,
                }}
              />
            )}
          </Box>

          <Typography variant="h4" sx={{
            fontWeight: 800,
            color: '#F1F5F9',
            fontSize: '1.75rem',
            mb: 0.5,
          }}>
            {typeof value === 'number' && value % 1 !== 0 ? value.toFixed(1) : value}
            {typeof value === 'number' && title.toLowerCase().includes('rate') && '%'}
          </Typography>

          <Typography variant="subtitle2" sx={{
            color: 'rgba(203, 213, 225, 0.8)',
            fontSize: '0.8rem',
            fontWeight: 600,
            mb: subtitle ? 0.5 : 0,
          }}>
            {title}
          </Typography>

          {subtitle && (
            <Typography variant="caption" sx={{
              color: 'rgba(203, 213, 225, 0.6)',
              fontSize: '0.7rem',
            }}>
              {subtitle}
            </Typography>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

interface InsightCardProps {
  insight: CampaignInsight;
  index: number;
}

const InsightCard: React.FC<InsightCardProps> = ({ insight, index }) => {
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'success':
        return '#10B981';
      case 'warning':
        return '#F59E0B';
      case 'opportunity':
        return '#3B82F6';
      default:
        return '#6B7280';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return '#EF4444';
      case 'medium':
        return '#F59E0B';
      default:
        return '#10B981';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
    >
      <Alert
        severity={insight.type === 'success' ? 'success' : insight.type === 'warning' ? 'warning' : 'info'}
        icon={<insight.icon sx={{ color: getTypeColor(insight.type) }} />}
        sx={{
          mb: 2,
          background: alpha(getTypeColor(insight.type), 0.1),
          border: `1px solid ${alpha(getTypeColor(insight.type), 0.3)}`,
          borderRadius: 2,
          '& .MuiAlert-icon': {
            alignItems: 'flex-start',
            mt: 0.5,
          },
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <AlertTitle sx={{ fontWeight: 700, mb: 0.5 }}>
            {insight.title}
          </AlertTitle>
          <Chip
            label={insight.impact.toUpperCase()}
            size="small"
            sx={{
              bgcolor: alpha(getImpactColor(insight.impact), 0.2),
              color: getImpactColor(insight.impact),
              fontSize: '0.65rem',
              fontWeight: 700,
              height: 18,
            }}
          />
        </Box>
        <Typography variant="body2" sx={{ mb: insight.recommendation ? 1.5 : 0 }}>
          {insight.description}
        </Typography>
        {insight.recommendation && (
          <Typography variant="body2" sx={{
            fontStyle: 'italic',
            color: 'rgba(203, 213, 225, 0.8)',
            fontSize: '0.875rem',
          }}>
            💡 {insight.recommendation}
          </Typography>
        )}
      </Alert>
    </motion.div>
  );
};

interface CampaignPerformanceDashboardProps {
  campaignId?: string;
  campaignData?: CampaignMetrics;
  timeRange?: '7d' | '30d' | '90d' | 'all';
  showExport?: boolean;
}

export const CampaignPerformanceDashboard: React.FC<CampaignPerformanceDashboardProps> = ({
  campaignId,
  campaignData: propCampaignData,
  timeRange = '30d',
  showExport = true,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [campaignData, setCampaignData] = useState<CampaignMetrics>(generateSampleMetrics());
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>(generateTimeSeriesData());
  const [insights, setInsights] = useState<CampaignInsight[]>(generateInsights());
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    if (propCampaignData) {
      setCampaignData(propCampaignData);
    }
  }, [propCampaignData]);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      // Simulate data refresh
      setLastUpdated(new Date());
      setLoading(false);
    }, 1500);
  };

  const handleExport = () => {
    // Export functionality
  };

  const COLORS = ['#60A5FA', '#A855F7', '#10B981', '#F59E0B', '#EF4444', '#06B6D4'];

  const engagementData = [
    { name: 'Opened', value: campaignData.emailsOpened, color: '#60A5FA' },
    { name: 'Clicked', value: campaignData.emailsClicked, color: '#A855F7' },
    { name: 'Replied', value: campaignData.replies, color: '#10B981' },
    { name: 'Bounced', value: campaignData.bounces, color: '#EF4444' },
  ];

  const performanceMetrics = [
    {
      title: 'Open Rate',
      value: campaignData.openRate,
      change: '+5.2%',
      changeType: 'positive' as const,
      icon: EmailIcon,
      color: '#60A5FA',
      subtitle: `${campaignData.emailsOpened} of ${campaignData.emailsSent} emails`,
    },
    {
      title: 'Click Rate',
      value: campaignData.clickRate,
      change: '+2.1%',
      changeType: 'positive' as const,
      icon: TrendingUpIcon,
      color: '#A855F7',
      subtitle: `${campaignData.emailsClicked} clicks recorded`,
    },
    {
      title: 'Reply Rate',
      value: campaignData.replyRate,
      change: '+3.7%',
      changeType: 'positive' as const,
      icon: CheckCircleIcon,
      color: '#10B981',
      subtitle: `${campaignData.replies} responses received`,
    },
    {
      title: 'Bounce Rate',
      value: campaignData.bounceRate,
      change: '-1.2%',
      changeType: 'positive' as const,
      icon: WarningIcon,
      color: '#EF4444',
      subtitle: `${campaignData.bounces} emails bounced`,
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Box sx={{ minHeight: '100vh', background: 'transparent' }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <Box>
              <Typography variant="h4" sx={{
                fontWeight: 800,
                color: '#F1F5F9',
                mb: 1,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}>
                <AnalyticsIcon sx={{ color: '#60A5FA' }} />
                Campaign Performance Dashboard
              </Typography>
              <Typography variant="h6" sx={{
                color: 'rgba(203, 213, 225, 0.9)',
                fontWeight: 600,
                mb: 1,
              }}>
                {campaignData.campaignName}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                Advanced analytics and AI-powered insights for campaign optimization
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Chip
                label={`Last updated: ${lastUpdated.toLocaleTimeString()}`}
                size="small"
                sx={{
                  bgcolor: alpha('#60A5FA', 0.1),
                  color: '#60A5FA',
                  border: `1px solid ${alpha('#60A5FA', 0.3)}`,
                  fontSize: '0.7rem',
                }}
              />
              <Tooltip title="Refresh Data">
                <IconButton
                  onClick={handleRefresh}
                  disabled={loading}
                  sx={{
                    bgcolor: alpha('#F1F5F9', 0.1),
                    '&:hover': {
                      bgcolor: alpha('#F1F5F9', 0.2),
                    },
                  }}
                >
                  <RefreshIcon sx={{ color: '#F1F5F9' }} />
                </IconButton>
              </Tooltip>
              {showExport && (
                <Tooltip title="Export Report">
                  <IconButton
                    onClick={handleExport}
                    sx={{
                      bgcolor: alpha('#F1F5F9', 0.1),
                      '&:hover': {
                        bgcolor: alpha('#F1F5F9', 0.2),
                      },
                    }}
                  >
                    <DownloadIcon sx={{ color: '#F1F5F9' }} />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>

          {/* Campaign Status Banner */}
          <Box sx={{
            p: 2,
            background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
            border: '1px solid rgba(96, 165, 250, 0.3)',
            borderRadius: 2,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Badge
                variant="dot"
                color={campaignData.status === 'active' ? 'success' : 'warning'}
                sx={{
                  '& .MuiBadge-badge': {
                    backgroundColor: campaignData.status === 'active' ? '#10B981' : '#F59E0B',
                  },
                }}
              >
                <Avatar sx={{
                  bgcolor: alpha(campaignData.status === 'active' ? '#10B981' : '#F59E0B', 0.1),
                  border: `1px solid ${campaignData.status === 'active' ? '#10B981' : '#F59E0B'}`,
                }}>
                  <CampaignIcon sx={{
                    color: campaignData.status === 'active' ? '#10B981' : '#F59E0B'
                  }} />
                </Avatar>
              </Badge>
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9' }}>
                  Status: {campaignData.status.charAt(0).toUpperCase() + campaignData.status.slice(1)}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
                  Started {new Date(campaignData.startDate).toLocaleDateString()}
                  {campaignData.endDate && ` • Ended ${new Date(campaignData.endDate).toLocaleDateString()}`}
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#10B981' }}>
                  {campaignData.backlinksSecured}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                  Backlinks Secured
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#F59E0B' }}>
                  {campaignData.domainAuthority}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                  Avg Domain Authority
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* Loading Indicator */}
        {loading && (
          <Box sx={{ mb: 4 }}>
            <LinearProgress sx={{
              backgroundColor: alpha('#60A5FA', 0.2),
              '& .MuiLinearProgress-bar': {
                backgroundColor: '#60A5FA',
              },
            }} />
          </Box>
        )}

        {/* Performance Metrics Grid */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{
            fontWeight: 700,
            color: '#F1F5F9',
            mb: 3,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}>
            <BarChartIcon sx={{ color: '#A855F7' }} />
            Key Performance Metrics
          </Typography>

          <Grid container spacing={2}>
            {performanceMetrics.map((metric, index) => (
              <Grid item xs={12} sm={6} lg={3} key={metric.title}>
                <MetricCard {...metric} />
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Tabs for different views */}
        <Box sx={{ width: '100%' }}>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue)}
            sx={{
              mb: 3,
              '& .MuiTab-root': {
                color: 'rgba(203, 213, 225, 0.7)',
                fontWeight: 600,
                textTransform: 'none',
                minHeight: 48,
                '&.Mui-selected': {
                  color: '#60A5FA',
                },
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#60A5FA',
                height: 3,
              },
            }}
          >
            <Tab icon={<ShowChartIcon />} label="Performance Trends" />
            <Tab icon={<PieChartIcon />} label="Engagement Breakdown" />
            <Tab icon={<InsightsIcon />} label="AI Insights" />
            <Tab icon={<AssessmentIcon />} label="Detailed Analytics" />
          </Tabs>

          {/* Performance Trends Tab */}
          <TabPanel value={activeTab} index={0}>
            <Card sx={BacklinkingStyles.campaignCard}>
              <CardHeader
                title={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TimelineIcon sx={{ color: '#60A5FA' }} />
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
                      Email Performance Over Time
                    </Typography>
                  </Box>
                }
                sx={BacklinkingStyles.campaignCardHeader}
              />
              <CardContent sx={BacklinkingStyles.campaignCardContent}>
                <Box sx={{ width: '100%', height: 400 }}>
                  <ResponsiveContainer>
                    <AreaChart data={timeSeriesData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(203, 213, 225, 0.2)" />
                      <XAxis
                        dataKey="date"
                        stroke="rgba(203, 213, 225, 0.7)"
                        fontSize={12}
                        tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      />
                      <YAxis stroke="rgba(203, 213, 225, 0.7)" fontSize={12} />
                      <RechartsTooltip
                        contentStyle={{
                          backgroundColor: 'rgba(30, 41, 59, 0.95)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: 8,
                          color: '#F1F5F9',
                        }}
                        labelFormatter={(value) => new Date(value).toLocaleDateString()}
                      />
                      <Area
                        type="monotone"
                        dataKey="sent"
                        stackId="1"
                        stroke="#60A5FA"
                        fill="#60A5FA"
                        fillOpacity={0.3}
                        name="Sent"
                      />
                      <Area
                        type="monotone"
                        dataKey="opened"
                        stackId="2"
                        stroke="#A855F7"
                        fill="#A855F7"
                        fillOpacity={0.3}
                        name="Opened"
                      />
                      <Area
                        type="monotone"
                        dataKey="replied"
                        stackId="3"
                        stroke="#10B981"
                        fill="#10B981"
                        fillOpacity={0.3}
                        name="Replied"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </TabPanel>

          {/* Engagement Breakdown Tab */}
          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={BacklinkingStyles.campaignCard}>
                  <CardHeader
                    title={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PieChartIcon sx={{ color: '#A855F7' }} />
                        <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
                          Email Engagement Distribution
                        </Typography>
                      </Box>
                    }
                    sx={BacklinkingStyles.campaignCardHeader}
                  />
                  <CardContent sx={BacklinkingStyles.campaignCardContent}>
                    <Box sx={{ width: '100%', height: 300 }}>
                      <ResponsiveContainer>
                        <PieChart>
                          <Pie
                            data={engagementData}
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            dataKey="value"
                            label={({ name }) => name}
                          >
                            {engagementData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <RechartsTooltip
                            contentStyle={{
                              backgroundColor: 'rgba(30, 41, 59, 0.95)',
                              border: '1px solid rgba(255, 255, 255, 0.1)',
                              borderRadius: 8,
                              color: '#F1F5F9',
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card sx={BacklinkingStyles.campaignCard}>
                  <CardHeader
                    title={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <BarChartIcon sx={{ color: '#10B981' }} />
                        <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
                          Conversion Funnel
                        </Typography>
                      </Box>
                    }
                    sx={BacklinkingStyles.campaignCardHeader}
                  />
                  <CardContent sx={BacklinkingStyles.campaignCardContent}>
                    <Box sx={{ width: '100%', height: 300 }}>
                      <ResponsiveContainer>
                        <BarChart data={engagementData} layout="horizontal">
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(203, 213, 225, 0.2)" />
                          <XAxis type="number" stroke="rgba(203, 213, 225, 0.7)" />
                          <YAxis dataKey="name" type="category" stroke="rgba(203, 213, 225, 0.7)" width={80} />
                          <RechartsTooltip
                            contentStyle={{
                              backgroundColor: 'rgba(30, 41, 59, 0.95)',
                              border: '1px solid rgba(255, 255, 255, 0.1)',
                              borderRadius: 8,
                              color: '#F1F5F9',
                            }}
                          />
                          <Bar dataKey="value" fill="#60A5FA" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* AI Insights Tab */}
          <TabPanel value={activeTab} index={2}>
            <Box>
              <Typography variant="h6" sx={{
                fontWeight: 700,
                color: '#F1F5F9',
                mb: 3,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}>
                <InsightsIcon sx={{ color: '#A855F7' }} />
                AI-Powered Campaign Insights & Recommendations
              </Typography>

              <AnimatePresence>
                {insights.map((insight, index) => (
                  <InsightCard key={insight.title} insight={insight} index={index} />
                ))}
              </AnimatePresence>
            </Box>
          </TabPanel>

          {/* Detailed Analytics Tab */}
          <TabPanel value={activeTab} index={3}>
            <Card sx={BacklinkingStyles.campaignCard}>
              <CardHeader
                title={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AssessmentIcon sx={{ color: '#F59E0B' }} />
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
                      Detailed Performance Metrics
                    </Typography>
                  </Box>
                }
                sx={BacklinkingStyles.campaignCardHeader}
              />
              <CardContent sx={BacklinkingStyles.campaignCardContent}>
                <TableContainer component={Paper} sx={{
                  backgroundColor: 'transparent',
                  boxShadow: 'none',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: 2,
                }}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{
                        '& th': {
                          backgroundColor: alpha('#1E293B', 0.5),
                          color: '#F1F5F9',
                          fontWeight: 700,
                          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                        },
                      }}>
                        <TableCell>Metric</TableCell>
                        <TableCell align="right">Value</TableCell>
                        <TableCell align="right">Target</TableCell>
                        <TableCell align="right">Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {[
                        { metric: 'Total Prospects', value: campaignData.totalProspects, target: 200, status: 'On Track' },
                        { metric: 'Emails Sent', value: campaignData.emailsSent, target: 150, status: 'On Track' },
                        { metric: 'Open Rate', value: `${campaignData.openRate}%`, target: '65%', status: 'Excellent' },
                        { metric: 'Reply Rate', value: `${campaignData.replyRate}%`, target: '12%', status: 'Excellent' },
                        { metric: 'Backlinks Secured', value: campaignData.backlinksSecured, target: 10, status: 'On Track' },
                        { metric: 'Avg Response Time', value: `${campaignData.avgResponseTime} days`, target: '3 days', status: 'Good' },
                      ].map((row) => (
                        <TableRow key={row.metric} sx={{
                          '& td': {
                            color: '#F1F5F9',
                            borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                          },
                        }}>
                          <TableCell component="th" scope="row">
                            {row.metric}
                          </TableCell>
                          <TableCell align="right">{row.value}</TableCell>
                          <TableCell align="right">{row.target}</TableCell>
                          <TableCell align="right">
                            <Chip
                              label={row.status}
                              size="small"
                              sx={{
                                bgcolor: row.status === 'Excellent' ? alpha('#10B981', 0.2) :
                                       row.status === 'Good' ? alpha('#F59E0B', 0.2) :
                                       alpha('#60A5FA', 0.2),
                                color: row.status === 'Excellent' ? '#10B981' :
                                       row.status === 'Good' ? '#F59E0B' :
                                       '#60A5FA',
                                fontWeight: 600,
                              }}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </TabPanel>
        </Box>
      </Box>
    </motion.div>
  );
};