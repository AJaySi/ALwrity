/**
 * Scheduler Jobs Tree Component
 * Displays scheduled jobs in tree structure matching log format.
 */

import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  FormControl,
  Select,
  MenuItem,
  Chip,
  InputLabel,
  Stack,
  Tooltip,
  Typography
} from '@mui/material';
import {
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
  Event as EventIcon,
  Person as PersonIcon,
  Storage as StorageIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Create as CreateIcon,
  Analytics as AnalyticsIcon,
  Assessment as AssessmentIcon,
  IntegrationInstructions as IntegrationIcon,
  Image as ImageIcon,
  SearchOutlined as SeoIcon,
  Share as SocialIcon,
  Settings as SettingsIcon,
  MoreHoriz as MoreIcon
} from '@mui/icons-material';
import { SchedulerJob } from '../../api/schedulerDashboard';
import { TerminalPaper, TerminalTypography, TerminalChip, terminalColors } from './terminalTheme';

interface SchedulerJobsTreeProps {
  jobs: SchedulerJob[];
  recurringJobs: number;
  oneTimeJobs: number;
}

const SchedulerJobsTree: React.FC<SchedulerJobsTreeProps> = ({
  jobs,
  recurringJobs,
  oneTimeJobs
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [jobTypeFilter, setJobTypeFilter] = useState('all');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [alwrityToolFilter, setAlwrityToolFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const DEFAULT_DISPLAY_COUNT = 3; // Show only 3 jobs by default
  const COLLAPSE_DELAY = 2000; // 2 seconds delay before collapsing

  const handleMouseEnter = () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
    setIsExpanded(true);
  };

  const handleMouseLeave = () => {
    hoverTimeoutRef.current = setTimeout(() => {
      setIsExpanded(false);
    }, COLLAPSE_DELAY);
  };

  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

  // Helper functions for categorization and icons
  const getAlwrityToolIcon = (toolCategory: string) => {
    const iconProps = { fontSize: 'small' as const, sx: { mr: 1 } };
    switch (toolCategory) {
      case 'content_creation': return <CreateIcon {...iconProps} />;
      case 'content_strategy': return <AssessmentIcon {...iconProps} />;
      case 'website_analysis': return <AnalyticsIcon {...iconProps} />;
      case 'analytics': return <AnalyticsIcon {...iconProps} />;
      case 'platform_integration': return <IntegrationIcon {...iconProps} />;
      case 'image_studio': return <ImageIcon {...iconProps} />;
      case 'seo_tools': return <SeoIcon {...iconProps} />;
      case 'social_media': return <SocialIcon {...iconProps} />;
      case 'scheduler': return <SettingsIcon {...iconProps} />;
      default: return <MoreIcon {...iconProps} />;
    }
  };

  const getAlwrityToolCategory = (jobId: string, job?: SchedulerJob): string => {
    // Categorize jobs by Alwrity tools/services
    if (jobId === 'check_due_tasks') {
      return 'scheduler';
    }
    if (jobId.includes('research_persona') || jobId.includes('facebook_persona')) {
      return 'content_creation';
    }
    if (jobId.includes('oauth_token_monitoring')) {
      return 'platform_integration';
    }
    if (jobId.includes('website_analysis')) {
      return 'website_analysis';
    }
    if (jobId.includes('platform_insights')) {
      return 'analytics';
    }
    if (jobId.includes('content_strategy') || jobId.includes('content_planning')) {
      return 'content_strategy';
    }
    if (jobId.includes('image') || jobId.includes('studio')) {
      return 'image_studio';
    }
    if (jobId.includes('seo') || jobId.includes('dashboard')) {
      return 'seo_tools';
    }
    if (jobId.includes('linkedin') || jobId.includes('youtube') || jobId.includes('podcast')) {
      return 'social_media';
    }
    return 'other';
  };

  // Filter and search jobs
  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const searchableText = `${job.id} ${job.function_name || ''} ${job.platform || ''} ${job.user_id || ''}`.toLowerCase();
        if (!searchableText.includes(query)) {
          return false;
        }
      }

      // Job type filter
      if (jobTypeFilter !== 'all') {
        if (jobTypeFilter === 'recurring' && job.id !== 'check_due_tasks') {
          return false;
        }
        if (jobTypeFilter === 'oauth' && !job.id.includes('oauth_token_monitoring')) {
          return false;
        }
        if (jobTypeFilter === 'website' && !job.id.includes('website_analysis')) {
          return false;
        }
        if (jobTypeFilter === 'platform' && !job.id.includes('platform_insights')) {
          return false;
        }
        if (jobTypeFilter === 'persona' && !(job.id.includes('research_persona') || job.id.includes('facebook_persona'))) {
          return false;
        }
      }

      // Platform filter
      if (platformFilter !== 'all') {
        const jobPlatform = job.platform || '';
        if (jobPlatform !== platformFilter) {
          return false;
        }
      }

      // Alwrity tool filter
      if (alwrityToolFilter !== 'all') {
        const toolCategory = getAlwrityToolCategory(job.id, job);
        if (toolCategory !== alwrityToolFilter) {
          return false;
        }
      }

      return true;
    });
  }, [jobs, searchQuery, jobTypeFilter, platformFilter, alwrityToolFilter]);

  const displayedJobs = isExpanded ? filteredJobs : filteredJobs.slice(0, DEFAULT_DISPLAY_COUNT);
  const hasMoreJobs = filteredJobs.length > DEFAULT_DISPLAY_COUNT;
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not scheduled';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  const getJobTypeIcon = (jobId: string) => {
    if (jobId === 'check_due_tasks') {
      return <RefreshIcon fontSize="small" />;
    }
    return <EventIcon fontSize="small" />;
  };

  const getJobTypeLabel = (jobId: string, job?: SchedulerJob) => {
    if (jobId === 'check_due_tasks') {
      return 'Recurring';
    }
    if (jobId.includes('research_persona')) {
      return 'Research Persona';
    }
    if (jobId.includes('facebook_persona')) {
      return 'Facebook Persona';
    }
    if (jobId.includes('oauth_token_monitoring')) {
      // Extract platform from job ID or use platform field
      const platform = job?.platform || 
                      jobId.split('_')[2] || 
                      'OAuth';
      const platformNames: { [key: string]: string } = {
        'gsc': 'GSC',
        'bing': 'Bing',
        'wordpress': 'WordPress',
        'wix': 'Wix'
      };
      return `OAuth ${platformNames[platform] || platform.toUpperCase()}`;
    }
    if (jobId.includes('website_analysis')) {
      // Extract task type from job
      const taskType = job?.task_type || 'Website';
      const taskTypeNames: { [key: string]: string } = {
        'user_website': 'User Website',
        'competitor': 'Competitor'
      };
      return `Website Analysis - ${taskTypeNames[taskType] || taskType}`;
    }
    if (jobId.includes('platform_insights')) {
      // Extract platform from job ID or use platform field
      const platform = job?.platform || 
                      jobId.split('_')[2] || 
                      'Platform';
      const platformNames: { [key: string]: string } = {
        'gsc': 'GSC Insights',
        'bing': 'Bing Insights'
      };
      return platformNames[platform] || `${platform.toUpperCase()} Insights`;
    }
    return 'One-Time';
  };

  const getJobTypeColor = (jobId: string) => {
    if (jobId === 'check_due_tasks') {
      return 'primary';
    }
    return 'secondary';
  };

  // Separate recurring and one-time jobs
  const recurringJob = jobs.find(j => j.id === 'check_due_tasks');
  const oneTimeJobsList = jobs.filter(j => j.id !== 'check_due_tasks');

  return (
    <TerminalPaper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <ScheduleIcon sx={{ color: terminalColors.primary }} />
        <TerminalTypography variant="h6" component="h2" sx={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
          Scheduled Jobs
        </TerminalTypography>
        <TerminalChip
          label={`${filteredJobs.length} of ${jobs.length} shown`}
          size="small"
        />
      </Box>

      {/* Search and Filter Controls */}
      <Box mb={2}>
        <Stack direction="row" spacing={1} alignItems="center" mb={1}>
          <TextField
            size="small"
            placeholder="Search jobs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: terminalColors.primary, fontSize: '18px' }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiInputBase-root': {
                backgroundColor: 'rgba(0, 255, 0, 0.05)',
                border: '1px solid rgba(0, 255, 0, 0.3)',
                color: terminalColors.text,
                fontFamily: 'monospace',
                fontSize: '0.8rem',
              },
              '& .MuiInputBase-input::placeholder': {
                color: terminalColors.textSecondary,
                opacity: 0.7,
              },
              '& .MuiOutlinedInput-notchedOutline': {
                border: 'none',
              },
              flex: 1,
            }}
          />
          <FilterListIcon
            sx={{
              color: showFilters ? terminalColors.primary : terminalColors.textSecondary,
              cursor: 'pointer',
              fontSize: '20px',
              '&:hover': { color: terminalColors.primary }
            }}
            onClick={() => setShowFilters(!showFilters)}
          />
        </Stack>

        {showFilters && (
          <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel sx={{
                color: terminalColors.textSecondary,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                '&.Mui-focused': { color: terminalColors.primary }
              }}>
                Job Type
              </InputLabel>
              <Select
                value={jobTypeFilter}
                label="Job Type"
                onChange={(e) => setJobTypeFilter(e.target.value)}
                sx={{
                  backgroundColor: 'rgba(0, 255, 0, 0.05)',
                  border: '1px solid rgba(0, 255, 0, 0.3)',
                  color: terminalColors.text,
                  fontFamily: 'monospace',
                  fontSize: '0.8rem',
                  '& .MuiOutlinedInput-notchedOutline': {
                    border: 'none',
                  },
                  '& .MuiSelect-icon': {
                    color: terminalColors.primary,
                  }
                }}
              >
                <MenuItem value="all" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>All Types</MenuItem>
                <MenuItem value="recurring" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>Recurring</MenuItem>
                <MenuItem value="oauth" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>OAuth</MenuItem>
                <MenuItem value="website" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>Website</MenuItem>
                <MenuItem value="platform" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>Platform</MenuItem>
                <MenuItem value="persona" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>Persona</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel sx={{
                color: terminalColors.textSecondary,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                '&.Mui-focused': { color: terminalColors.primary }
              }}>
                Platform
              </InputLabel>
              <Select
                value={platformFilter}
                label="Platform"
                onChange={(e) => setPlatformFilter(e.target.value)}
                sx={{
                  backgroundColor: 'rgba(0, 255, 0, 0.05)',
                  border: '1px solid rgba(0, 255, 0, 0.3)',
                  color: terminalColors.text,
                  fontFamily: 'monospace',
                  fontSize: '0.8rem',
                  '& .MuiOutlinedInput-notchedOutline': {
                    border: 'none',
                  },
                  '& .MuiSelect-icon': {
                    color: terminalColors.primary,
                  }
                }}
              >
                <MenuItem value="all" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>All Platforms</MenuItem>
                <MenuItem value="gsc" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>GSC</MenuItem>
                <MenuItem value="bing" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>Bing</MenuItem>
                <MenuItem value="wordpress" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>WordPress</MenuItem>
                <MenuItem value="wix" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>Wix</MenuItem>
              </Select>
            </FormControl>

            <Tooltip title={
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>Filter by Alwrity Tool/Service:</Typography>
                <Typography variant="caption" component="div">• Content Creation: Research & writing personas</Typography>
                <Typography variant="caption" component="div">• Content Strategy: Strategy planning & management</Typography>
                <Typography variant="caption" component="div">• Website Analysis: Site performance monitoring</Typography>
                <Typography variant="caption" component="div">• Platform Analytics: GSC & Bing insights</Typography>
                <Typography variant="caption" component="div">• Platform Integration: OAuth token monitoring</Typography>
                <Typography variant="caption" component="div">• Image Studio: AI image generation tasks</Typography>
                <Typography variant="caption" component="div">• SEO Tools: Search optimization tasks</Typography>
                <Typography variant="caption" component="div">• Social Media: LinkedIn, YouTube, Podcast tasks</Typography>
                <Typography variant="caption" component="div">• Scheduler Core: System maintenance tasks</Typography>
              </Box>
            } arrow>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel sx={{
                  color: terminalColors.textSecondary,
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                  '&.Mui-focused': { color: terminalColors.primary }
                }}>
                  Alwrity Tool
                </InputLabel>
                <Select
                value={alwrityToolFilter}
                label="Alwrity Tool"
                onChange={(e) => setAlwrityToolFilter(e.target.value)}
                sx={{
                  backgroundColor: 'rgba(0, 255, 0, 0.05)',
                  border: '1px solid rgba(0, 255, 0, 0.3)',
                  color: terminalColors.text,
                  fontFamily: 'monospace',
                  fontSize: '0.8rem',
                  '& .MuiOutlinedInput-notchedOutline': {
                    border: 'none',
                  },
                  '& .MuiSelect-icon': {
                    color: terminalColors.primary,
                  }
                }}
              >
                <MenuItem value="all" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  <MoreIcon sx={{ mr: 1, fontSize: 'small' }} />
                  All Tools
                </MenuItem>
                <MenuItem value="content_creation" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('content_creation')}
                  Content Creation
                </MenuItem>
                <MenuItem value="content_strategy" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('content_strategy')}
                  Content Strategy
                </MenuItem>
                <MenuItem value="website_analysis" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('website_analysis')}
                  Website Analysis
                </MenuItem>
                <MenuItem value="analytics" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('analytics')}
                  Platform Analytics
                </MenuItem>
                <MenuItem value="platform_integration" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('platform_integration')}
                  Platform Integration
                </MenuItem>
                <MenuItem value="image_studio" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('image_studio')}
                  Image Studio
                </MenuItem>
                <MenuItem value="seo_tools" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('seo_tools')}
                  SEO Tools
                </MenuItem>
                <MenuItem value="social_media" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('social_media')}
                  Social Media
                </MenuItem>
                <MenuItem value="scheduler" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('scheduler')}
                  Scheduler Core
                </MenuItem>
                <MenuItem value="other" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
                  {getAlwrityToolIcon('other')}
                  Other
                </MenuItem>
                </Select>
              </FormControl>
            </Tooltip>

            {(searchQuery || jobTypeFilter !== 'all' || platformFilter !== 'all' || alwrityToolFilter !== 'all') && (
              <Chip
                label="Clear Filters"
                size="small"
                onClick={() => {
                  setSearchQuery('');
                  setJobTypeFilter('all');
                  setPlatformFilter('all');
                  setAlwrityToolFilter('all');
                }}
                sx={{
                  backgroundColor: 'rgba(244, 67, 54, 0.2)',
                  color: '#f44336',
                  border: '1px solid #f44336',
                  fontFamily: 'monospace',
                  fontSize: '0.7rem',
                  '&:hover': {
                    backgroundColor: 'rgba(244, 67, 54, 0.3)',
                  }
                }}
              />
            )}
          </Stack>
        )}
      </Box>

      <Box 
        sx={{ 
          fontFamily: 'monospace', 
          fontSize: '0.875rem', 
          color: terminalColors.text, 
          flex: 1, 
          overflow: 'auto', 
          minHeight: 0 
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {/* Header */}
        <Box mb={2} sx={{ flexShrink: 0 }}>
          <TerminalTypography variant="body2" sx={{ mb: 1, color: terminalColors.textSecondary }}>
            Recurring Jobs: {recurringJobs} | One-Time Jobs: {oneTimeJobs}
            {hasMoreJobs && !isExpanded && (
              <TerminalTypography 
                component="span" 
                sx={{ ml: 1, color: terminalColors.primary, fontStyle: 'italic', fontSize: '0.75rem' }}
              >
                (Hover to see all {jobs.length} jobs)
              </TerminalTypography>
            )}
          </TerminalTypography>
        </Box>

        {/* Jobs Tree */}
        {displayedJobs.length > 0 ? (
          <Box sx={{ flex: 1 }}>
            {displayedJobs.map((job, index) => {
              const isLast = index === displayedJobs.length - 1 && (!hasMoreJobs || isExpanded);
              const prefix = isLast ? '└─' : '├─';
              const isRecurring = job.id === 'check_due_tasks';

              return (
                <Box 
                  key={job.id} 
                  sx={{ 
                    mb: 2, 
                    display: 'block',
                    borderLeft: `2px solid ${terminalColors.border}`,
                    pl: 2,
                    py: 1
                  }}
                >
                  <Box 
                    display="flex" 
                    alignItems="flex-start" 
                    gap={1.5} 
                    flexWrap="wrap"
                    sx={{ 
                      width: '100%',
                      minHeight: '50px',
                    }}
                  >
                    {/* Tree prefix and chip */}
                    <Box display="flex" alignItems="center" gap={1} sx={{ flexShrink: 0 }}>
                      <TerminalTypography component="span" sx={{ fontFamily: 'monospace', color: terminalColors.primary, fontSize: '1.2rem' }}>
                        {prefix}
                      </TerminalTypography>
                      <TerminalChip
                        icon={getJobTypeIcon(job.id)}
                        label={getJobTypeLabel(job.id, job)}
                        size="small"
                        sx={{ flexShrink: 0 }}
                      />
                    </Box>
                    
                    {/* Job details */}
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center', mb: 0.5 }}>
                        <TerminalTypography 
                          component="span" 
                          sx={{ 
                            fontFamily: 'monospace', 
                            color: terminalColors.primary, 
                            wordBreak: 'break-word',
                            wordWrap: 'break-word',
                            overflowWrap: 'break-word',
                            whiteSpace: 'normal',
                            fontSize: '0.875rem',
                            fontWeight: 'bold',
                            maxWidth: '100%'
                          }}
                        >
                          {job.id}
                        </TerminalTypography>
                      </Box>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, alignItems: 'center', mt: 0.5 }}>
                        <TerminalTypography 
                          component="span" 
                          sx={{ 
                            fontFamily: 'monospace', 
                            color: terminalColors.textSecondary, 
                            fontSize: '0.8rem',
                            wordBreak: 'break-word',
                            wordWrap: 'break-word',
                            overflowWrap: 'break-word',
                            whiteSpace: 'normal'
                          }}
                        >
                          Trigger: {job.trigger_type}
                        </TerminalTypography>
                        {job.next_run_time && (
                          <TerminalTypography 
                            component="span" 
                            sx={{ 
                              fontFamily: 'monospace', 
                              color: terminalColors.textSecondary, 
                              fontSize: '0.8rem',
                              wordBreak: 'break-word',
                              wordWrap: 'break-word',
                              overflowWrap: 'break-word',
                              whiteSpace: 'normal'
                            }}
                          >
                            Next Run: {formatDate(job.next_run_time)}
                          </TerminalTypography>
                        )}
                        {job.user_id && (
                          <Box display="flex" alignItems="center" gap={0.5}>
                            <PersonIcon fontSize="small" sx={{ color: terminalColors.textSecondary, fontSize: '0.875rem' }} />
                            <TerminalTypography 
                              component="span" 
                              sx={{ 
                                fontFamily: 'monospace', 
                                color: terminalColors.textSecondary, 
                                fontSize: '0.8rem',
                                wordBreak: 'break-word',
                                wordWrap: 'break-word',
                                overflowWrap: 'break-word',
                                whiteSpace: 'normal'
                              }}
                            >
                              User: {String(job.user_id)}
                            </TerminalTypography>
                          </Box>
                        )}
                        {job.platform && (
                          <Box display="flex" alignItems="center" gap={0.5}>
                            <TerminalTypography 
                              component="span" 
                              sx={{ 
                                fontFamily: 'monospace', 
                                color: terminalColors.primary, 
                                fontSize: '0.8rem',
                                fontWeight: 'bold',
                                wordBreak: 'break-word',
                                wordWrap: 'break-word',
                                overflowWrap: 'break-word',
                                whiteSpace: 'normal'
                              }}
                            >
                              Platform: {job.platform.toUpperCase()}
                            </TerminalTypography>
                          </Box>
                        )}
                        {job.user_job_store && job.user_job_store !== 'default' && (
                          <Box display="flex" alignItems="center" gap={0.5}>
                            <StorageIcon fontSize="small" sx={{ color: terminalColors.textSecondary, fontSize: '0.875rem' }} />
                            <TerminalTypography 
                              component="span" 
                              sx={{ 
                                fontFamily: 'monospace', 
                                color: terminalColors.textSecondary, 
                                fontSize: '0.8rem',
                                wordBreak: 'break-word',
                                wordWrap: 'break-word',
                                overflowWrap: 'break-word',
                                whiteSpace: 'normal'
                              }}
                            >
                              Store: {job.user_job_store}
                            </TerminalTypography>
                          </Box>
                        )}
                      </Box>
                    </Box>
                  </Box>
                </Box>
              );
            })}
          </Box>
        ) : (
          <TerminalTypography variant="body2" sx={{ fontStyle: 'italic', color: terminalColors.textSecondary }}>
            No jobs scheduled
          </TerminalTypography>
        )}
      </Box>
    </TerminalPaper>
  );
};

export default SchedulerJobsTree;

