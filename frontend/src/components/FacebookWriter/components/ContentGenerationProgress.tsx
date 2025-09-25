import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Collapse,
  Fade,
  Zoom,
  Alert,
  AlertTitle,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  CheckCircle,
  RadioButtonUnchecked,
  Error,
  Warning,
  Info,
  ExpandMore,
  ExpandLess,
  Refresh,
  Close,
  PlayArrow,
  Pause,
  Stop
} from '@mui/icons-material';

interface GenerationStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'warning';
  progress: number;
  message?: string;
  timestamp?: Date;
  duration?: number;
  details?: string[];
}

interface ContentGenerationProgressProps {
  isVisible: boolean;
  onClose: () => void;
  onComplete?: (result: any) => void;
  onError?: (error: any) => void;
  generationType?: 'post' | 'hashtags' | 'ad_copy' | 'story' | 'reel' | 'carousel' | 'event' | 'page_about';
  initialSteps?: GenerationStep[];
}

const ContentGenerationProgress: React.FC<ContentGenerationProgressProps> = ({
  isVisible,
  onClose,
  onComplete,
  onError,
  generationType = 'post',
  initialSteps = []
}) => {
  const [steps, setSteps] = useState<GenerationStep[]>(initialSteps);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [overallProgress, setOverallProgress] = useState<number>(0);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Default steps based on generation type
  const getDefaultSteps = (type: string): GenerationStep[] => {
    const baseSteps: Record<string, GenerationStep[]> = {
      post: [
        {
          id: 'analyze',
          title: 'Analyzing Requirements',
          description: 'Understanding your content goals and target audience',
          status: 'pending',
          progress: 0
        },
        {
          id: 'persona',
          title: 'Applying Persona',
          description: 'Optimizing content for your writing style and brand voice',
          status: 'pending',
          progress: 0
        },
        {
          id: 'generate',
          title: 'Generating Content',
          description: 'Creating engaging Facebook post content',
          status: 'pending',
          progress: 0
        },
        {
          id: 'optimize',
          title: 'Optimizing for Engagement',
          description: 'Enhancing content for maximum reach and engagement',
          status: 'pending',
          progress: 0
        },
        {
          id: 'finalize',
          title: 'Finalizing Content',
          description: 'Reviewing and polishing the final content',
          status: 'pending',
          progress: 0
        }
      ],
      hashtags: [
        {
          id: 'analyze',
          title: 'Analyzing Content',
          description: 'Understanding your post content and context',
          status: 'pending',
          progress: 0
        },
        {
          id: 'research',
          title: 'Researching Trends',
          description: 'Finding relevant and trending hashtags',
          status: 'pending',
          progress: 0
        },
        {
          id: 'generate',
          title: 'Generating Hashtags',
          description: 'Creating optimized hashtag combinations',
          status: 'pending',
          progress: 0
        },
        {
          id: 'validate',
          title: 'Validating Hashtags',
          description: 'Ensuring hashtags are relevant and effective',
          status: 'pending',
          progress: 0
        }
      ],
      ad_copy: [
        {
          id: 'analyze',
          title: 'Analyzing Campaign Goals',
          description: 'Understanding your advertising objectives',
          status: 'pending',
          progress: 0
        },
        {
          id: 'research',
          title: 'Researching Audience',
          description: 'Analyzing target audience preferences',
          status: 'pending',
          progress: 0
        },
        {
          id: 'generate',
          title: 'Creating Ad Copy',
          description: 'Writing compelling ad content',
          status: 'pending',
          progress: 0
        },
        {
          id: 'optimize',
          title: 'Optimizing for Conversions',
          description: 'Enhancing copy for maximum conversion rates',
          status: 'pending',
          progress: 0
        }
      ]
    };

    return baseSteps[type] || baseSteps.post;
  };

  // Initialize steps when component mounts
  useEffect(() => {
    if (isVisible && steps.length === 0) {
      const defaultSteps = getDefaultSteps(generationType);
      setSteps(defaultSteps);
      setStartTime(new Date());
    }
  }, [isVisible, generationType]);

  // Simulate generation process
  useEffect(() => {
    if (!isVisible || isPaused) return;

    const simulateGeneration = async () => {
      for (let i = 0; i < steps.length; i++) {
        if (isPaused) break;

        // Update current step to running
        setSteps(prev => prev.map((step, index) => 
          index === i 
            ? { ...step, status: 'running', timestamp: new Date() }
            : step
        ));
        setCurrentStep(i);

        // Simulate step progress
        for (let progress = 0; progress <= 100; progress += 10) {
          if (isPaused) break;
          
          setSteps(prev => prev.map((step, index) => 
            index === i 
              ? { ...step, progress, message: getStepMessage(i, progress) }
              : step
          ));

          // Update overall progress
          const overallProgress = ((i * 100) + progress) / steps.length;
          setOverallProgress(overallProgress);

          await new Promise(resolve => setTimeout(resolve, 200));
        }

        // Mark step as completed
        setSteps(prev => prev.map((step, index) => 
          index === i 
            ? { 
                ...step, 
                status: 'completed', 
                progress: 100,
                duration: Date.now() - (step.timestamp?.getTime() || Date.now())
              }
            : step
        ));

        // Small delay between steps
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Generation complete
      if (!isPaused) {
        onComplete?.({ success: true, content: 'Generated content here' });
      }
    };

    if (isVisible && !isPaused) {
      simulateGeneration();
    }
  }, [isVisible, isPaused]);

  // Update elapsed time
  useEffect(() => {
    if (!startTime) return;

    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const getStepMessage = (stepIndex: number, progress: number): string => {
    const messages = {
      analyze: [
        'Reading your requirements...',
        'Understanding your goals...',
        'Analyzing target audience...',
        'Processing context...',
        'Preparing for generation...'
      ],
      persona: [
        'Loading your persona...',
        'Applying writing style...',
        'Optimizing for brand voice...',
        'Customizing tone...',
        'Personalizing content...'
      ],
      generate: [
        'Generating content...',
        'Creating engaging copy...',
        'Crafting your message...',
        'Building the post...',
        'Finalizing content...'
      ],
      optimize: [
        'Analyzing engagement potential...',
        'Optimizing for reach...',
        'Enhancing call-to-action...',
        'Improving readability...',
        'Finalizing optimizations...'
      ],
      finalize: [
        'Reviewing content...',
        'Checking quality...',
        'Polishing details...',
        'Preparing final version...',
        'Content ready!'
      ]
    };

    const stepMessages = messages[steps[stepIndex]?.id as keyof typeof messages] || messages.generate;
    const messageIndex = Math.floor((progress / 100) * (stepMessages.length - 1));
    return stepMessages[messageIndex] || stepMessages[0];
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle sx={{ color: '#4caf50' }} />;
      case 'running':
        return <CircularProgress size={20} sx={{ color: '#1877f2' }} />;
      case 'error':
        return <Error sx={{ color: '#f44336' }} />;
      case 'warning':
        return <Warning sx={{ color: '#ff9800' }} />;
      default:
        return <RadioButtonUnchecked sx={{ color: 'rgba(255,255,255,0.5)' }} />;
    }
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#4caf50';
      case 'running':
        return '#1877f2';
      case 'error':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      default:
        return 'rgba(255,255,255,0.5)';
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isVisible) return null;

  return (
    <Fade in={isVisible} timeout={300}>
      <Paper
        sx={{
          position: 'fixed',
          top: 20,
          right: 20,
          width: 400,
          maxHeight: '80vh',
          zIndex: 2000,
          background: 'linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(20,20,30,0.98) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
          boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <Box sx={{ 
          p: 3, 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          background: 'linear-gradient(135deg, rgba(24,119,242,0.1) 0%, rgba(11,88,195,0.05) 100%)'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" sx={{ 
              color: 'rgba(255,255,255,0.95)', 
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}>
              <Box sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: '#1877f2',
                animation: 'pulse 1.5s ease-in-out infinite'
              }} />
              AI Content Generation
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title={isPaused ? 'Resume' : 'Pause'}>
                <IconButton 
                  size="small" 
                  onClick={() => setIsPaused(!isPaused)}
                  sx={{ color: 'rgba(255,255,255,0.7)' }}
                >
                  {isPaused ? <PlayArrow /> : <Pause />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Close">
                <IconButton 
                  size="small" 
                  onClick={onClose}
                  sx={{ color: 'rgba(255,255,255,0.7)' }}
                >
                  <Close />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              {generationType.charAt(0).toUpperCase() + generationType.slice(1).replace('_', ' ')} Generation
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              {formatTime(elapsedTime)}
            </Typography>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={overallProgress}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'rgba(255,255,255,0.1)',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(90deg, #1877f2 0%, #42a5f5 100%)',
                borderRadius: 3
              }
            }}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              {Math.round(overallProgress)}% Complete
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              Step {currentStep + 1} of {steps.length}
            </Typography>
          </Box>
        </Box>

        {/* Content */}
        <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
          <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.9)', fontWeight: 600 }}>
                Generation Steps
              </Typography>
              <IconButton 
                size="small" 
                onClick={() => setIsExpanded(!isExpanded)}
                sx={{ color: 'rgba(255,255,255,0.7)' }}
              >
                {isExpanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>
            
            <Collapse in={isExpanded}>
              <List dense>
                {steps.map((step, index) => (
                  <Zoom key={step.id} in={true} timeout={300 + (index * 100)}>
                    <ListItem
                      sx={{
                        py: 1.5,
                        px: 2,
                        borderRadius: 2,
                        mb: 1,
                        background: step.status === 'running' 
                          ? 'rgba(24,119,242,0.1)' 
                          : step.status === 'completed'
                          ? 'rgba(76,175,80,0.1)'
                          : 'transparent',
                        border: step.status === 'running' 
                          ? '1px solid rgba(24,119,242,0.2)' 
                          : '1px solid transparent',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        {getStepIcon(step.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ 
                            color: 'rgba(255,255,255,0.9)', 
                            fontWeight: step.status === 'running' ? 600 : 500 
                          }}>
                            {step.title}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" sx={{ 
                              color: 'rgba(255,255,255,0.7)',
                              display: 'block',
                              mb: 0.5
                            }}>
                              {step.description}
                            </Typography>
                            {step.message && (
                              <Typography variant="caption" sx={{ 
                                color: getStepColor(step.status),
                                fontStyle: 'italic'
                              }}>
                                {step.message}
                              </Typography>
                            )}
                            {step.status === 'running' && (
                              <LinearProgress
                                variant="determinate"
                                value={step.progress}
                                sx={{
                                  height: 2,
                                  borderRadius: 1,
                                  backgroundColor: 'rgba(255,255,255,0.1)',
                                  mt: 0.5,
                                  '& .MuiLinearProgress-bar': {
                                    background: 'linear-gradient(90deg, #1877f2 0%, #42a5f5 100%)',
                                    borderRadius: 1
                                  }
                                }}
                              />
                            )}
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {step.duration && (
                            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                              {step.duration}ms
                            </Typography>
                          )}
                          <Chip
                            size="small"
                            label={step.status}
                            sx={{
                              backgroundColor: getStepColor(step.status),
                              color: 'white',
                              fontSize: '0.7rem',
                              height: 20
                            }}
                          />
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                  </Zoom>
                ))}
              </List>
            </Collapse>
          </Box>
        </Box>

        {/* Footer */}
        <Box sx={{ 
          p: 2, 
          borderTop: '1px solid rgba(255,255,255,0.1)',
          background: 'rgba(0,0,0,0.2)'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              {isPaused ? 'Generation paused' : 'Generating content...'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Refresh">
                <IconButton size="small" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Box>

        {/* CSS Animations */}
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </Paper>
    </Fade>
  );
};

export default ContentGenerationProgress;
