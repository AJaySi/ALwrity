/**
 * Scheduler Jobs Tree Component
 * Displays scheduled jobs in tree structure matching log format.
 */

import React from 'react';
import { Box } from '@mui/material';
import {
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
  Event as EventIcon,
  Person as PersonIcon,
  Storage as StorageIcon
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
          label={`${jobs.length} total`} 
          size="small"
        />
      </Box>

      <Box sx={{ fontFamily: 'monospace', fontSize: '0.875rem', color: terminalColors.text, flex: 1, overflow: 'auto', minHeight: 0 }}>
        {/* Header */}
        <Box mb={2} sx={{ flexShrink: 0 }}>
          <TerminalTypography variant="body2" sx={{ mb: 1, color: terminalColors.textSecondary }}>
            Recurring Jobs: {recurringJobs} | One-Time Jobs: {oneTimeJobs}
          </TerminalTypography>
        </Box>

        {/* Jobs Tree */}
        {jobs.length > 0 ? (
          <Box sx={{ flex: 1 }}>
            {jobs.map((job, index) => {
              const isLast = index === jobs.length - 1;
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

