/**
 * Email Campaigns Panel - Ported from Legacy Backlinker
 *
 * Comprehensive email campaign management interface with AI-powered
 * outreach tracking, performance analytics, and campaign creation.
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Grid,
  Button,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
  Badge,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  alpha,
  Divider,
} from '@mui/material';
import {
  Email as EmailIcon,
  Send as SendIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  ExpandMore as ExpandMoreIcon,
  SmartToy as BrainIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  Campaign as CampaignIcon,
  PlayArrow as ActivityIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Reply as ReplyIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { BacklinkingStyles } from './styles/backlinkingStyles';

interface EmailCampaign {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'draft' | 'completed';
  sent: number;
  opened: number;
  replied: number;
  prospects: number;
  lastActivity: string;
  openRate: number;
  replyRate: number;
  createdAt: string;
  aiGenerated: boolean;
  template?: string;
}

const generateSampleCampaigns = (): EmailCampaign[] => [
  {
    id: '1',
    name: 'AI Tools Guest Posts',
    status: 'active',
    sent: 45,
    opened: 28,
    replied: 12,
    prospects: 67,
    lastActivity: '2 hours ago',
    openRate: 62.2,
    replyRate: 26.7,
    createdAt: '2024-01-15',
    aiGenerated: true,
    template: 'Guest Post Outreach',
  },
  {
    id: '2',
    name: 'Content Marketing Outreach',
    status: 'paused',
    sent: 32,
    opened: 18,
    replied: 8,
    prospects: 89,
    lastActivity: '1 day ago',
    openRate: 56.3,
    replyRate: 25.0,
    createdAt: '2024-01-12',
    aiGenerated: false,
    template: 'Content Collaboration',
  },
  {
    id: '3',
    name: 'SEO Expert Quotes',
    status: 'draft',
    sent: 0,
    opened: 0,
    replied: 0,
    prospects: 23,
    lastActivity: '3 hours ago',
    openRate: 0,
    replyRate: 0,
    createdAt: '2024-01-20',
    aiGenerated: true,
    template: 'Expert Quote Request',
  },
  {
    id: '4',
    name: 'Industry Partnership Outreach',
    status: 'completed',
    sent: 78,
    opened: 52,
    replied: 23,
    prospects: 95,
    lastActivity: '1 week ago',
    openRate: 66.7,
    replyRate: 29.5,
    createdAt: '2024-01-01',
    aiGenerated: true,
    template: 'Partnership Proposal',
  },
];

interface CampaignCardProps {
  campaign: EmailCampaign;
  index: number;
  onView: (campaign: EmailCampaign) => void;
  onEdit: (campaign: EmailCampaign) => void;
  onLaunch: (campaign: EmailCampaign) => void;
}

const CampaignCard: React.FC<CampaignCardProps> = ({
  campaign,
  index,
  onView,
  onEdit,
  onLaunch,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10B981';
      case 'paused':
        return '#F59E0B';
      case 'draft':
        return '#60A5FA';
      case 'completed':
        return '#8B5CF6';
      default:
        return '#6B7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <PlayIcon sx={{ fontSize: 12 }} />;
      case 'paused':
        return <PauseIcon sx={{ fontSize: 12 }} />;
      case 'draft':
        return <EditIcon sx={{ fontSize: 12 }} />;
      case 'completed':
        return <CheckCircleIcon sx={{ fontSize: 12 }} />;
      default:
        return <ScheduleIcon sx={{ fontSize: 12 }} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.5,
        delay: index * 0.1,
        ease: [0.4, 0, 0.2, 1],
      }}
      whileHover={{
        scale: 1.02,
        y: -2,
        transition: { duration: 0.2 },
      }}
    >
      <Card
        sx={{
          height: '100%',
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          cursor: 'pointer',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `radial-gradient(circle at 30% 30%, ${alpha(getStatusColor(campaign.status), 0.08)} 0%, transparent 70%)`,
            pointerEvents: 'none',
          },
          '&:hover': {
            boxShadow: `0 8px 25px ${alpha(getStatusColor(campaign.status), 0.2)}`,
            borderColor: alpha(getStatusColor(campaign.status), 0.3),
            transform: 'translateY(-2px)',
          },
        }}
        onClick={() => onView(campaign)}
      >
        <CardContent sx={{ p: 2.5, position: 'relative', zIndex: 1 }}>
          {/* Header with status and AI badge */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flex: 1, minWidth: 0 }}>
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: getStatusColor(campaign.status),
                  boxShadow: `0 0 8px ${alpha(getStatusColor(campaign.status), 0.6)}`,
                }}
              />
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: '#F1F5F9',
                  fontSize: '0.95rem',
                  lineHeight: 1.3,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {campaign.name}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 0.5, flexShrink: 0 }}>
              {campaign.aiGenerated && (
                <Tooltip title="AI Generated Campaign">
                  <Avatar sx={{
                    width: 20,
                    height: 20,
                    bgcolor: alpha('#A855F7', 0.1),
                    border: `1px solid ${alpha('#A855F7', 0.3)}`,
                  }}>
                    <BrainIcon sx={{ fontSize: 12, color: '#A855F7' }} />
                  </Avatar>
                </Tooltip>
              )}
              <Chip
                label={campaign.status}
                size="small"
                icon={getStatusIcon(campaign.status)}
                sx={{
                  height: 20,
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  bgcolor: alpha(getStatusColor(campaign.status), 0.1),
                  color: getStatusColor(campaign.status),
                  border: `1px solid ${alpha(getStatusColor(campaign.status), 0.3)}`,
                  textTransform: 'capitalize',
                  '& .MuiChip-icon': {
                    color: getStatusColor(campaign.status),
                  },
                }}
              />
            </Box>
          </Box>

          {/* Stats Grid */}
          <Grid container spacing={1.5} sx={{ mb: 2 }}>
            <Grid item xs={6}>
              <Box sx={{
                textAlign: 'center',
                p: 1.5,
                bgcolor: alpha('#1E293B', 0.5),
                borderRadius: 1.5,
                border: '1px solid rgba(255, 255, 255, 0.05)',
              }}>
                <Typography variant="h5" sx={{
                  fontWeight: 800,
                  color: '#F1F5F9',
                  fontSize: '1.25rem',
                  lineHeight: 1,
                }}>
                  {campaign.sent}
                </Typography>
                <Typography variant="caption" sx={{
                  color: 'rgba(203, 213, 225, 0.7)',
                  fontSize: '0.7rem',
                  fontWeight: 500,
                }}>
                  Sent
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{
                textAlign: 'center',
                p: 1.5,
                bgcolor: alpha('#10B981', 0.1),
                borderRadius: 1.5,
                border: '1px solid rgba(16, 185, 129, 0.2)',
              }}>
                <Typography variant="h5" sx={{
                  fontWeight: 800,
                  color: '#10B981',
                  fontSize: '1.25rem',
                  lineHeight: 1,
                }}>
                  {campaign.replied}
                </Typography>
                <Typography variant="caption" sx={{
                  color: 'rgba(203, 213, 225, 0.7)',
                  fontSize: '0.7rem',
                  fontWeight: 500,
                }}>
                  Replies
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Additional Stats */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <PeopleIcon sx={{ fontSize: 14, color: 'rgba(203, 213, 225, 0.6)' }} />
              <Typography variant="caption" sx={{
                color: 'rgba(203, 213, 225, 0.8)',
                fontSize: '0.75rem',
              }}>
                {campaign.prospects} prospects
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <TrendingUpIcon sx={{ fontSize: 14, color: 'rgba(203, 213, 225, 0.6)' }} />
              <Typography variant="caption" sx={{
                color: 'rgba(203, 213, 225, 0.8)',
                fontSize: '0.75rem',
              }}>
                {campaign.openRate.toFixed(1)}% open
              </Typography>
            </Box>
          </Box>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<VisibilityIcon />}
              onClick={(e) => {
                e.stopPropagation();
                onView(campaign);
              }}
              sx={{
                flex: 1,
                borderColor: 'rgba(255, 255, 255, 0.2)',
                color: '#F1F5F9',
                fontSize: '0.75rem',
                py: 0.75,
                '&:hover': {
                  borderColor: '#60A5FA',
                  bgcolor: alpha('#60A5FA', 0.1),
                },
              }}
            >
              <VisibilityIcon sx={{ fontSize: 14, mr: 0.5 }} />
              View Analytics
            </Button>
            {campaign.status === 'draft' ? (
              <Button
                variant="contained"
                size="small"
                startIcon={<SendIcon />}
                onClick={(e) => {
                  e.stopPropagation();
                  onLaunch(campaign);
                }}
                sx={{
                  flex: 1,
                  bgcolor: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                  fontSize: '0.75rem',
                  py: 0.75,
                  '&:hover': {
                    bgcolor: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  },
                }}
              >
                Launch
              </Button>
            ) : (
              <Button
                variant="contained"
                size="small"
                startIcon={<EditIcon />}
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(campaign);
                }}
                sx={{
                  flex: 1,
                  bgcolor: 'linear-gradient(135deg, #A855F7 0%, #9333EA 100%)',
                  fontSize: '0.75rem',
                  py: 0.75,
                  '&:hover': {
                    bgcolor: 'linear-gradient(135deg, #9333EA 0%, #7C3AED 100%)',
                  },
                }}
              >
                Edit
              </Button>
            )}
          </Box>

          {/* Last Activity */}
          <Typography variant="caption" sx={{
            color: 'rgba(203, 213, 225, 0.6)',
            fontSize: '0.7rem',
            mt: 1.5,
            display: 'block',
            textAlign: 'center',
          }}>
            Last activity: {campaign.lastActivity}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );
};

interface EmailCampaignsPanelProps {
  onCampaignSelect?: (campaign: EmailCampaign) => void;
  maxHeight?: string | number;
  showCreateButtons?: boolean;
}

export const EmailCampaignsPanel: React.FC<EmailCampaignsPanelProps> = ({
  onCampaignSelect,
  maxHeight,
  showCreateButtons = true,
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState<EmailCampaign[]>([]);
  const [expanded, setExpanded] = useState<string | false>('campaigns');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Simulate loading campaigns
    setLoading(true);
    setTimeout(() => {
      setCampaigns(generateSampleCampaigns());
      setLoading(false);
    }, 1000);
  }, []);

  const handleViewCampaign = (campaign: EmailCampaign) => {
    onCampaignSelect?.(campaign);
    // Navigate to campaign details
    navigate(`/backlinking/campaign/${campaign.id}/emails`);
  };

  const handleEditCampaign = (campaign: EmailCampaign) => {
    onCampaignSelect?.(campaign);
    navigate(`/backlinking/campaign/${campaign.id}/edit`);
  };

  const handleLaunchCampaign = (campaign: EmailCampaign) => {
    onCampaignSelect?.(campaign);
    // Launch campaign logic
  };

  const handleCreateAICampaign = () => {
    navigate('/backlinking/new-campaign?type=ai');
  };

  const handleCreateCustomCampaign = () => {
    navigate('/backlinking/new-campaign?type=custom');
  };

  // Calculate summary stats
  const totalCampaigns = campaigns.length;
  const activeCampaigns = campaigns.filter(c => c.status === 'active').length;
  const totalReplies = campaigns.reduce((sum, c) => sum + c.replied, 0);
  const totalSent = campaigns.reduce((sum, c) => sum + c.sent, 0);
  const avgReplyRate = totalSent > 0 ? (totalReplies / totalSent) * 100 : 0;

  const handleAccordionChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4, duration: 0.5 }}
    >
      <Card sx={{
        ...BacklinkingStyles.campaignCard,
        minHeight: 400,
        maxHeight: maxHeight || 'auto',
        overflow: 'auto',
      }}>
        <CardHeader sx={BacklinkingStyles.campaignCardHeader}>
          <Box sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            width: '100%',
            flexWrap: 'wrap',
            gap: 2,
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{
                bgcolor: 'rgba(6, 182, 212, 0.1)',
                border: '1px solid rgba(6, 182, 212, 0.3)',
              }}>
                <EmailIcon sx={{ color: '#06B6D4' }} />
              </Avatar>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 0.5 }}>
                  AI Email Campaigns
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
                  Automated outreach with intelligent personalization and performance tracking
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Badge
                badgeContent={totalCampaigns}
                color="primary"
                sx={{
                  '& .MuiBadge-badge': {
                    backgroundColor: '#06B6D4',
                    color: '#000',
                    fontWeight: 700,
                  },
                }}
              >
                <Chip
                  icon={<ActivityIcon />}
                  label={`${activeCampaigns} Active`}
                  size="small"
                  sx={{
                    bgcolor: alpha('#10B981', 0.1),
                    color: '#10B981',
                    border: `1px solid ${alpha('#10B981', 0.3)}`,
                    fontWeight: 600,
                  }}
                />
              </Badge>

              <Chip
                icon={<ReplyIcon />}
                label={`${avgReplyRate.toFixed(1)}% Reply Rate`}
                size="small"
                sx={{
                  bgcolor: alpha('#A855F7', 0.1),
                  color: '#A855F7',
                  border: `1px solid ${alpha('#A855F7', 0.3)}`,
                  fontWeight: 600,
                }}
              />
            </Box>
          </Box>
        </CardHeader>

        <CardContent sx={{ ...BacklinkingStyles.campaignCardContent, p: 0 }}>
          <Accordion
            expanded={expanded === 'campaigns'}
            onChange={handleAccordionChange('campaigns')}
            sx={{
              bgcolor: 'transparent',
              boxShadow: 'none',
              '&:before': { display: 'none' },
              '& .MuiAccordionSummary-root': {
                bgcolor: alpha('#1E293B', 0.5),
                borderRadius: 2,
                mx: 3,
                mt: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                minHeight: 64,
              },
              '& .MuiAccordionSummary-expandIconWrapper': {
                color: '#60A5FA',
              },
              '& .MuiAccordionDetails-root': {
                p: 3,
                pt: 2,
              },
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="campaigns-content"
              id="campaigns-header"
              sx={{
                '& .MuiAccordionSummary-content': {
                  alignItems: 'center',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                <Avatar sx={{
                  bgcolor: alpha('#F59E0B', 0.1),
                  border: `1px solid ${alpha('#F59E0B', 0.3)}`,
                  width: 32,
                  height: 32,
                }}>
                  <CampaignIcon sx={{ color: '#F59E0B', fontSize: 16 }} />
                </Avatar>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9' }}>
                    Active Email Campaigns
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Manage and monitor your outreach campaigns
                  </Typography>
                </Box>
                <Chip
                  label="AI Powered"
                  size="small"
                  sx={{
                    bgcolor: alpha('#A855F7', 0.1),
                    color: '#A855F7',
                    border: `1px solid ${alpha('#A855F7', 0.3)}`,
                    fontWeight: 600,
                    ml: 'auto',
                    mr: 2,
                  }}
                />
              </Box>
            </AccordionSummary>

            <AccordionDetails>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <BrainIcon sx={{ fontSize: 32, color: '#60A5FA' }} />
                  </motion.div>
                </Box>
              ) : (
                <>
                  {/* Campaign Grid */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <AnimatePresence>
                      {campaigns.map((campaign, index) => (
                        <Grid item xs={12} sm={6} lg={4} key={campaign.id}>
                          <CampaignCard
                            campaign={campaign}
                            index={index}
                            onView={handleViewCampaign}
                            onEdit={handleEditCampaign}
                            onLaunch={handleLaunchCampaign}
                          />
                        </Grid>
                      ))}
                    </AnimatePresence>
                  </Grid>

                  {/* Create Campaign Buttons */}
                  {showCreateButtons && (
                    <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
                      <Button
                        variant="contained"
                        startIcon={<BrainIcon />}
                        onClick={handleCreateAICampaign}
                        sx={{
                          flex: 1,
                          py: 1.5,
                          background: 'linear-gradient(135deg, #A855F7 0%, #9333EA 100%)',
                          fontWeight: 600,
                          textTransform: 'none',
                          borderRadius: 2,
                          boxShadow: '0 4px 14px 0 rgba(168, 85, 247, 0.4)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #9333EA 0%, #7C3AED 100%)',
                            boxShadow: '0 6px 20px 0 rgba(168, 85, 247, 0.6)',
                          },
                        }}
                      >
                        Generate AI Campaign
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<EmailIcon />}
                        onClick={handleCreateCustomCampaign}
                        sx={{
                          flex: 1,
                          py: 1.5,
                          borderColor: 'rgba(255, 255, 255, 0.3)',
                          color: '#F1F5F9',
                          fontWeight: 600,
                          textTransform: 'none',
                          borderRadius: 2,
                          '&:hover': {
                            borderColor: '#60A5FA',
                            bgcolor: alpha('#60A5FA', 0.1),
                          },
                        }}
                      >
                        Create Custom Campaign
                      </Button>
                    </Box>
                  )}
                </>
              )}
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>
  );
};