/**
 * Analytics Summary - Ported from Legacy Backlinker
 *
 * Comprehensive KPI dashboard showing backlinking campaign performance
 * with AI-powered insights and trend analysis.
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Grid,
  Avatar,
  Chip,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  People as PeopleIcon,
  CheckCircle as CheckCircleIcon,
  Public as PublicIcon,
  Visibility as VisibilityIcon,
  Chat as ChatIcon,
  TrackChanges as TargetIcon,
  Analytics as AnalyticsIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { BacklinkingStyles } from './styles/backlinkingStyles';

interface KPIMetric {
  id: string;
  title: string;
  value: string | number;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: React.ComponentType<any>;
  color: string;
  bgColor: string;
  description?: string;
  trend?: 'up' | 'down' | 'stable';
}

const generateKPIData = (): KPIMetric[] => [
  {
    id: 'total-prospects',
    title: 'Total Prospects',
    value: '1,247',
    change: '+12.5%',
    changeType: 'positive',
    icon: PeopleIcon,
    color: '#60A5FA',
    bgColor: alpha('#60A5FA', 0.1),
    description: 'AI-discovered potential link partners',
    trend: 'up',
  },
  {
    id: 'emails-sent',
    title: 'Emails Sent',
    value: '856',
    change: '+8.3%',
    changeType: 'positive',
    icon: EmailIcon,
    color: '#A855F7',
    bgColor: alpha('#A855F7', 0.1),
    description: 'Personalized outreach messages',
    trend: 'up',
  },
  {
    id: 'response-rate',
    title: 'Response Rate',
    value: '24.8%',
    change: '+3.2%',
    changeType: 'positive',
    icon: ChatIcon,
    color: '#06B6D4',
    bgColor: alpha('#06B6D4', 0.1),
    description: 'Prospects who replied to outreach',
    trend: 'up',
  },
  {
    id: 'backlinks-secured',
    title: 'Backlinks Secured',
    value: '187',
    change: '+15.7%',
    changeType: 'positive',
    icon: CheckCircleIcon,
    color: '#10B981',
    bgColor: alpha('#10B981', 0.1),
    description: 'Successfully published guest posts',
    trend: 'up',
  },
  {
    id: 'domain-authority',
    title: 'Domain Authority Avg',
    value: '68.5',
    change: '+2.1%',
    changeType: 'positive',
    icon: PublicIcon,
    color: '#F59E0B',
    bgColor: alpha('#F59E0B', 0.1),
    description: 'Average DA of target domains',
    trend: 'up',
  },
  {
    id: 'open-rate',
    title: 'Open Rate',
    value: '42.3%',
    change: '+5.4%',
    changeType: 'positive',
    icon: VisibilityIcon,
    color: '#EC4899',
    bgColor: alpha('#EC4899', 0.1),
    description: 'Emails opened by recipients',
    trend: 'up',
  },
  {
    id: 'active-campaigns',
    title: 'Active Campaigns',
    value: '12',
    change: '+2',
    changeType: 'positive',
    icon: TargetIcon,
    color: '#8B5CF6',
    bgColor: alpha('#8B5CF6', 0.1),
    description: 'Currently running outreach campaigns',
    trend: 'up',
  },
  {
    id: 'conversion-rate',
    title: 'Conversion Rate',
    value: '18.6%',
    change: '+4.1%',
    changeType: 'positive',
    icon: TrendingUpIcon,
    color: '#EF4444',
    bgColor: alpha('#EF4444', 0.1),
    description: 'Emails that resulted in backlinks',
    trend: 'up',
  },
];

interface KPICardProps {
  metric: KPIMetric;
  index: number;
}

const KPICard: React.FC<KPICardProps> = ({ metric, index }) => {
  const theme = useTheme();

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon sx={{ fontSize: 14, color: '#10B981' }} />;
      case 'down':
        return <TrendingUpIcon sx={{ fontSize: 14, color: '#EF4444', transform: 'rotate(180deg)' }} />;
      default:
        return <TimelineIcon sx={{ fontSize: 14, color: '#6B7280' }} />;
    }
  };

  const getChangeColor = (changeType: string) => {
    switch (changeType) {
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
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.5,
        delay: index * 0.1,
        ease: [0.4, 0, 0.2, 1],
      }}
      whileHover={{
        scale: 1.05,
        y: -4,
        transition: { duration: 0.2 },
      }}
    >
      <Card
        sx={{
          height: '100%',
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 3,
          cursor: 'pointer',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `radial-gradient(circle at 30% 30%, ${alpha(metric.color, 0.08)} 0%, transparent 70%)`,
            pointerEvents: 'none',
          },
          '&:hover': {
            boxShadow: `0 8px 25px ${alpha(metric.color, 0.2)}`,
            borderColor: alpha(metric.color, 0.3),
            transform: 'translateY(-2px)',
          },
        }}
      >
        <CardContent sx={{ p: 2, position: 'relative', zIndex: 1, textAlign: 'center' }}>
          {/* Icon */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              mb: 1.5,
            }}
          >
            <Avatar
              sx={{
                bgcolor: metric.bgColor,
                width: 48,
                height: 48,
                border: `2px solid ${alpha(metric.color, 0.3)}`,
              }}
            >
              <metric.icon sx={{ color: metric.color, fontSize: 24 }} />
            </Avatar>
          </Box>

          {/* Value */}
          <Typography
            variant="h4"
            sx={{
              fontWeight: 800,
              fontSize: '1.75rem',
              color: '#F1F5F9',
              mb: 0.5,
              textShadow: `0 0 10px ${alpha(metric.color, 0.5)}`,
            }}
          >
            {metric.value}
          </Typography>

          {/* Title */}
          <Typography
            variant="body2"
            sx={{
              color: 'rgba(203, 213, 225, 0.8)',
              fontSize: '0.75rem',
              fontWeight: 600,
              mb: 1,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            {metric.title}
          </Typography>

          {/* Change Indicator */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 0.5,
            }}
          >
            {getTrendIcon(metric.trend || 'stable')}
            <Typography
              variant="caption"
              sx={{
                color: getChangeColor(metric.changeType),
                fontWeight: 700,
                fontSize: '0.7rem',
              }}
            >
              {metric.change}
            </Typography>
          </Box>

          {/* Description */}
          {metric.description && (
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 1,
                color: 'rgba(203, 213, 225, 0.6)',
                fontSize: '0.65rem',
                lineHeight: 1.2,
              }}
            >
              {metric.description}
            </Typography>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

interface AnalyticsSummaryProps {
  campaignId?: string;
  showHeader?: boolean;
  refreshInterval?: number; // in milliseconds
}

export const AnalyticsSummary: React.FC<AnalyticsSummaryProps> = ({
  campaignId,
  showHeader = true,
  refreshInterval = 30000, // 30 seconds
}) => {
  const theme = useTheme();
  const [kpiData, setKpiData] = useState<KPIMetric[]>(generateKPIData());
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setIsRefreshing(true);

      // Simulate slight data changes
      setTimeout(() => {
        setKpiData(prevData =>
          prevData.map(metric => ({
            ...metric,
            value: typeof metric.value === 'string' && metric.value.includes(',')
              ? (parseInt(metric.value.replace(',', '')) + Math.floor(Math.random() * 10 - 5)).toLocaleString()
              : typeof metric.value === 'string' && metric.value.includes('%')
              ? `${(parseFloat(metric.value) + (Math.random() - 0.5) * 2).toFixed(1)}%`
              : typeof metric.value === 'string' && !isNaN(parseFloat(metric.value))
              ? (parseFloat(metric.value) + Math.floor(Math.random() * 4 - 2)).toString()
              : metric.value,
          }))
        );
        setLastUpdated(new Date());
        setIsRefreshing(false);
      }, 1000);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Calculate summary stats
  const summaryStats = {
    totalProspects: kpiData.find(k => k.id === 'total-prospects')?.value || '0',
    emailsSent: kpiData.find(k => k.id === 'emails-sent')?.value || '0',
    responseRate: kpiData.find(k => k.id === 'response-rate')?.value || '0%',
    backlinksSecured: kpiData.find(k => k.id === 'backlinks-secured')?.value || '0',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1, duration: 0.5 }}
    >
      <Card sx={{
        ...BacklinkingStyles.campaignCard,
        minHeight: 300,
        position: 'relative',
      }}>
        {showHeader && (
          <CardHeader sx={BacklinkingStyles.campaignCardHeader}>
            <Box sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              width: '100%',
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{
                  bgcolor: 'rgba(96, 165, 250, 0.1)',
                  border: '1px solid rgba(96, 165, 250, 0.3)',
                }}>
                  <AnalyticsIcon sx={{ color: '#60A5FA' }} />
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
                    Campaign Analytics Overview
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Real-time performance metrics and AI insights
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Chip
                  label={`Last updated: ${lastUpdated.toLocaleTimeString()}`}
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(96, 165, 250, 0.1)',
                    color: '#60A5FA',
                    border: '1px solid rgba(96, 165, 250, 0.3)',
                    fontSize: '0.7rem',
                  }}
                />
                {isRefreshing && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <AnalyticsIcon sx={{ color: '#60A5FA', fontSize: 16 }} />
                  </motion.div>
                )}
              </Box>
            </Box>
          </CardHeader>
        )}

        <CardContent sx={{ ...BacklinkingStyles.campaignCardContent, p: 3 }}>
          {/* Summary Overview */}
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6" sx={{ color: '#F1F5F9', fontWeight: 600, mb: 0.5 }}>
                AI-Powered Backlinking Performance
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
                Tracking {summaryStats.totalProspects} prospects • {summaryStats.emailsSent} emails sent • {summaryStats.responseRate} response rate
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="h4" sx={{ color: '#10B981', fontWeight: 800 }}>
                {summaryStats.backlinksSecured}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                Backlinks Secured
              </Typography>
            </Box>
          </Box>

          {/* KPI Grid */}
          <Grid container spacing={2}>
            <AnimatePresence>
              {kpiData.map((metric, index) => (
                <Grid item xs={6} sm={4} md={3} key={metric.id}>
                  <KPICard metric={metric} index={index} />
                </Grid>
              ))}
            </AnimatePresence>
          </Grid>

          {/* AI Insights */}
          <Box sx={{
            mt: 3,
            p: 2,
            background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)',
            border: '1px solid rgba(96, 165, 250, 0.2)',
            borderRadius: 2,
          }}>
            <Typography variant="subtitle2" sx={{ color: '#60A5FA', fontWeight: 600, mb: 1 }}>
              🤖 AI Insights
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)', fontSize: '0.875rem' }}>
              Your response rate is 24.8%, which is 45% above industry average. Consider increasing outreach volume to qualified prospects
              with DA scores above 70 for optimal results.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};