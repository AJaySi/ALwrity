import React, { useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  Tooltip,
  Modal,
  Paper,
  Button,
  IconButton,
  Avatar,
  Stack,
  LinearProgress,
  CircularProgress,
  Card,
  CardContent
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  Today as TodayIcon,
  Close as CloseIcon,
  AutoAwesome as AlwrityIcon,
  CheckCircle as CheckIcon,
  PlayArrow as PlayIcon,
  SkipNext as SkipIcon,
  NavigateNext
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../../../stores/workflowStore';
import { TodayTask } from '../../../types/workflow';

interface EnhancedTodayModalProps {
  open: boolean;
  onClose: () => void;
  pillarId: string;
  pillarTitle: string;
  pillarColor: string;
  tasks: TodayTask[];
  // When navigating away (Next), prevent the previous pillar modal from auto-reopening
  onPreventAutoReopen?: () => void;
}

// Enhanced Today Modal with Workflow Integration
const EnhancedTodayModal: React.FC<EnhancedTodayModalProps> = ({ 
  open, 
  onClose, 
  pillarId, 
  pillarTitle, 
  pillarColor, 
  tasks, 
  onPreventAutoReopen 
}) => {
  const navigate = useNavigate();
  const {
    currentWorkflow,
    workflowProgress,
    navigationState,
    completeTask,
    skipTask,
    moveToNextTask,
    isLoading,
    isWorkflowComplete
  } = useWorkflowStore();

  const [selectedTask, setSelectedTask] = useState<TodayTask | null>(null);

  // Prefer live workflow tasks (to reflect updated statuses), fallback to props
  const liveTasks = currentWorkflow?.tasks && Array.isArray(currentWorkflow.tasks) && currentWorkflow.tasks.length > 0
    ? currentWorkflow.tasks
    : tasks;

  // Filter tasks for this pillar
  const pillarTasks = liveTasks.filter(task => task.pillarId === pillarId);
  const currentTask = navigationState?.currentTask;
  const isComplete = isWorkflowComplete();

  const handleTaskAction = async (task: TodayTask) => {
    if (!task.enabled) return;

    try {
      // Execute the task action
      if (task.action) {
        task.action();
      } else if (task.actionUrl) {
        navigate(task.actionUrl);
      }

      // Mark task as completed in workflow
      if (currentWorkflow) {
        await completeTask(task.id);
      }
    } catch (error) {
      console.error('Error executing task:', error);
    }
  };

  const handleSkipTask = async (task: TodayTask) => {
    if (currentWorkflow) {
      await skipTask(task.id);
    }
  };

  const handleStartWorkflow = async () => {
    if (currentWorkflow) {
      await moveToNextTask();
    }
  };

  const handleNextPillar = async () => {
    // Close current modal
    onClose();
    
    // Prevent auto-reopen of current modal during navigation
    if (onPreventAutoReopen) {
      onPreventAutoReopen();
    }
    
    // Navigate to next pillar
    if (nextPillarId) {
      setTimeout(() => {
        // Trigger next pillar modal opening
        const nextChip = document.querySelector(`[data-pillar-id="${nextPillarId}"]`);
        if (nextChip) {
          (nextChip as HTMLElement).click();
        }
      }, 300);
    }
  };

  const handleWorkflowComplete = async () => {
    console.log('Workflow Complete clicked for pillar:', pillarId);
    console.log('Current pillar tasks:', pillarTasks);
    
    // Mark all remaining tasks in this pillar as completed
    const incompleteTasks = pillarTasks.filter(task => 
      task.status !== 'completed' && task.status !== 'skipped'
    );
    
    console.log('Incomplete tasks to complete:', incompleteTasks);
    
    for (const task of incompleteTasks) {
      try {
        console.log('Completing task:', task.id);
        await completeTask(task.id);
        console.log('Task completed successfully:', task.id);
      } catch (error) {
        console.error(`Failed to complete task ${task.id}:`, error);
      }
    }
    
    console.log('All tasks completed, closing modal');
    // Close the modal
    onClose();
  };

  // Check if all tasks in this pillar are completed or skipped
  const areAllTasksCompleted = pillarTasks.every(task => 
    task.status === 'completed' || task.status === 'skipped'
  );

  // Check if this is the Plan pillar
  const isPlanPillar = pillarId === 'plan';
  
  // Define pillar order for navigation
  const pillarOrder = ['plan', 'generate', 'publish', 'analyze', 'engage', 'remarket'];
  const currentPillarIndex = pillarOrder.indexOf(pillarId);
  const isLastPillar = currentPillarIndex === pillarOrder.length - 1;
  const nextPillarId = !isLastPillar ? pillarOrder[currentPillarIndex + 1] : null;

  const getTaskStatus = (task: TodayTask) => {
    if (task.status === 'completed') return 'completed';
    if (task.status === 'in_progress') return 'active';
    if (task.status === 'skipped') return 'skipped';
    return 'pending';
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'active': return '#2196F3';
      case 'skipped': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: { xs: 1.5, md: 3 }
      }}
    >
      <Paper
        sx={{
          width: { xs: '96vw', sm: '94vw', md: '90vw' },
          maxWidth: 1200,
          maxHeight: '92vh',
          overflow: 'auto',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(250,250,252,0.92) 100%)',
          backdropFilter: 'blur(24px)',
          borderRadius: 4,
          boxShadow: '0 30px 60px rgba(0,0,0,0.35)',
          border: '1px solid rgba(0,0,0,0.06)'
        }}
      >
        {/* Header */}
        <Box sx={{ p: { xs: 2, md: 3 }, borderBottom: '1px solid rgba(0,0,0,0.08)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar
                sx={{
                  background: pillarColor,
                  width: 48,
                  height: 48
                }}
              >
                <TodayIcon sx={{ fontSize: 24, color: 'white' }} />
              </Avatar>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#23252F', letterSpacing: 0.2 }}>
                  Today's {pillarTitle} Tasks
                </Typography>
                <Typography variant="body2" sx={{ color: '#5A5F6A' }}>
                  Complete your daily marketing workflow
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={onClose} sx={{ color: '#6B7280' }}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Workflow Progress - Circular in Header */}
        {workflowProgress && (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            p: { xs: 2, md: 3 }, 
            borderBottom: '1px solid rgba(0,0,0,0.08)' 
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2" sx={{ color: '#5A5F6A', fontWeight: 600 }}>
                Overall Progress
              </Typography>
              <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                <CircularProgress
                  variant="determinate"
                  value={workflowProgress.completionPercentage}
                  size={40}
                  thickness={4}
                  sx={{
                    color: pillarColor,
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    }
                  }}
                />
                <Box
                  sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography
                    variant="caption"
                    component="div"
                    sx={{ 
                      color: '#5A5F6A', 
                      fontWeight: 700,
                      fontSize: '0.7rem'
                    }}
                  >
                    {`${Math.round(workflowProgress.completionPercentage)}%`}
                  </Typography>
                </Box>
              </Box>
            </Box>
            <Typography variant="body2" sx={{ color: '#5A5F6A', fontWeight: 600 }}>
              {workflowProgress.completedTasks} of {workflowProgress.totalTasks} tasks
            </Typography>
          </Box>
        )}

        {/* Tasks List */}
        <Box sx={{ p: { xs: 2, md: 3 } }}>
          <Typography variant="h6" sx={{ mb: 2, color: '#23252F', fontWeight: 800 }}>
            {pillarTitle} Tasks
          </Typography>
          
          <Stack spacing={2}>
            {pillarTasks.map((task, index) => {
              const status = getTaskStatus(task);
              const statusColor = getTaskStatusColor(status);
              const isCurrentTask = currentTask?.id === task.id;
              const IconComponent = (typeof task.icon === 'function' ? task.icon : undefined) as any;

              return (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Card
                    sx={{
                      border: isCurrentTask ? `2px solid ${pillarColor}` : '1px solid rgba(0,0,0,0.08)',
                      background: isCurrentTask ? `${pillarColor}12` : 'white',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 20px rgba(0,0,0,0.08)'
                      }
                    }}
                  >
                    <CardContent sx={{ p: { xs: 2, md: 2.5 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                        {IconComponent && (
                          <Avatar
                            sx={{
                              background: statusColor,
                              width: 36,
                              height: 36
                            }}
                          >
                            <IconComponent sx={{ fontSize: 18, color: 'white' }} />
                          </Avatar>
                        )}
                        
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#23252F' }}>
                            {task.title}
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#5A5F6A' }}>
                            {task.description}
                          </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={status}
                            size="small"
                            sx={{
                              background: `${statusColor}18`,
                              color: statusColor,
                              border: `1px solid ${statusColor}40`,
                              textTransform: 'capitalize'
                            }}
                          />
                          
                          <Typography variant="caption" sx={{ color: '#999' }}>
                            {task.estimatedTime} min
                          </Typography>
                        </Box>
                      </Box>

                      {/* Task Actions */}
                      <Box sx={{ display: 'flex', gap: 1.25, mt: 2 }}>
                        {status === 'pending' && task.enabled && (
                          <Button
                            variant="contained"
                            size="small"
                            startIcon={<AlwrityIcon />}
                            onClick={() => handleTaskAction(task)}
                            disabled={isLoading}
                            sx={{
                              background: pillarColor,
                              '&:hover': {
                                background: pillarColor,
                                opacity: 0.9
                              }
                            }}
                          >
                            ALwrity it
                          </Button>
                        )}

                        {status === 'active' && (
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<PlayIcon />}
                            onClick={() => handleTaskAction(task)}
                            disabled={isLoading}
                            sx={{ borderColor: pillarColor, color: pillarColor }}
                          >
                            Continue
                          </Button>
                        )}

                        {status === 'completed' && (
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<CheckIcon />}
                            disabled
                            sx={{ borderColor: '#4CAF50', color: '#4CAF50' }}
                          >
                            Completed
                          </Button>
                        )}

                        {status === 'pending' && (
                          <Button
                            variant="text"
                            size="small"
                            startIcon={<SkipIcon />}
                            onClick={() => handleSkipTask(task)}
                            disabled={isLoading}
                            sx={{ color: '#FF9800' }}
                          >
                            Skip
                          </Button>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </Stack>
        </Box>

        {/* Footer Actions */}
        <Box sx={{ p: { xs: 2, md: 3 }, borderTop: '1px solid rgba(0,0,0,0.08)' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ color: '#5A5F6A' }}>
              {isComplete ? '🎉 All tasks completed!' : `${pillarTasks.length} tasks in this pillar`}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              {/* Next button for all pillars except the last one */}
              {!isLastPillar && (
                <>
                  <Button variant="outlined" onClick={onClose}>
                    Close
                  </Button>
                  <Tooltip 
                    title={areAllTasksCompleted 
                      ? `All tasks completed! Click to proceed to ${nextPillarId ? nextPillarId.charAt(0).toUpperCase() + nextPillarId.slice(1) : 'next'} pillar` 
                      : "Complete or skip all tasks in this pillar to proceed"
                    }
                    arrow
                  >
                    <span>
                      <Button
                        variant="contained"
                        startIcon={<NavigateNext />}
                        onClick={handleNextPillar}
                        disabled={!areAllTasksCompleted || isLoading}
                        sx={{
                          background: pillarColor,
                          '&:hover': {
                            background: pillarColor,
                            opacity: 0.9
                          },
                          '&:disabled': {
                            background: '#ccc',
                            color: '#666'
                          }
                        }}
                      >
                        Next
                      </Button>
                    </span>
                  </Tooltip>
                </>
              )}
              
              {/* Last pillar (Remarket) - Workflow Complete button acts as close */}
              {isLastPillar && (
                <Button
                  variant="contained"
                  startIcon={<CheckIcon />}
                  onClick={handleWorkflowComplete}
                  sx={{
                    background: '#4CAF50',
                    '&:hover': {
                      background: '#45a049',
                      opacity: 0.9
                    }
                  }}
                >
                  Workflow Complete!
                </Button>
              )}
            </Box>
          </Box>
        </Box>
      </Paper>
    </Modal>
  );
};

export default EnhancedTodayModal;
