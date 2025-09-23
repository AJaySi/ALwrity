import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  useTheme,
  useMediaQuery,
  Chip,
  Tooltip,
  Paper,
  Modal,
  Button,
  IconButton,
  Divider,
  LinearProgress,
  Avatar,
  Stack
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Close as CloseIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as UncheckedIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import GeneratePillarChips from './components/GeneratePillarChips';
import PublishPillarChips from './components/PublishPillarChips';
import AnalyzePillarChips from './components/AnalyzePillarChips';
import EngagePillarChips from './components/EngagePillarChips';
import EnhancedTodayChip from './components/EnhancedTodayChip';
import OnboardingModal from './components/OnboardingModal';
import WorkflowHeroSection from './components/WorkflowHeroSection';
import { pillarData } from './components/PillarData';
import { useWorkflowStore } from '../../stores/workflowStore';


// Enhanced Glassomorphic Chip Component with Popping Effects
const ChipWithTooltip: React.FC<{
  chip: any;
  delay?: number;
  onOnboardingClick?: () => void;
}> = ({ chip, delay = 0, onOnboardingClick }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % chip.bubbles.length);
    }, 2000 + delay * 300);

    return () => clearInterval(interval);
  }, [chip.bubbles.length, delay]);

  const IconComponent = chip.icon;

  const handleClick = () => {
    if (chip.label === 'On-Boarding' && onOnboardingClick) {
      onOnboardingClick();
    }
  };

  return (
    <Tooltip
      title={
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
            {chip.label}
          </Typography>
          <AnimatePresence mode="wait">
            <motion.div
              key={currentIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              <Typography variant="caption" sx={{ color: 'white' }}>
                {chip.bubbles[currentIndex]}
              </Typography>
            </motion.div>
          </AnimatePresence>
        </Box>
      }
      arrow
      placement="top"
    >
      <Box
        sx={{
          position: 'relative',
          cursor: 'pointer',
          transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          '&:hover': {
            transform: 'translateY(-4px) scale(1.05)',
            '& .chip-glow': {
              opacity: 1,
              transform: 'scale(1.2)'
            },
            '& .chip-shadow': {
              opacity: 0.6,
              transform: 'translateY(8px) scale(1.1)'
            }
          }
        }}
        onClick={handleClick}
      >
        {/* Glow Effect */}
        <Box
          className="chip-glow"
          sx={{
            position: 'absolute',
            top: -8,
            left: -8,
            right: -8,
            bottom: -8,
            background: chip.gradient || chip.color,
            borderRadius: '20px',
            opacity: 0,
            transition: 'all 0.4s ease',
            filter: 'blur(12px)',
            zIndex: -2
          }}
        />
        
        {/* Shadow Effect */}
        <Box
          className="chip-shadow"
          sx={{
            position: 'absolute',
            top: 4,
            left: 2,
            right: -2,
            bottom: -4,
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '16px',
            opacity: 0.3,
            transition: 'all 0.4s ease',
            filter: 'blur(8px)',
            zIndex: -1
          }}
        />

        {/* Main Chip */}
        <Chip
          icon={<IconComponent sx={{ fontSize: 14 }} />}
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.7rem' }}>
                {chip.label}
              </Typography>
              {chip.value && (
                <Box
                  sx={{
                    backgroundColor: 'rgba(255,255,255,0.9)',
                    color: chip.color,
                    borderRadius: '50%',
                    width: 16,
                    height: 16,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.6rem',
                    fontWeight: 700,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                  }}
                >
                  {chip.value}
                </Box>
              )}
            </Box>
          }
          size="small"
          sx={{
            background: `linear-gradient(135deg, 
              rgba(255,255,255,0.25) 0%, 
              rgba(255,255,255,0.1) 50%, 
              rgba(255,255,255,0.05) 100%)`,
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.3)',
            color: 'white',
            fontSize: '0.7rem',
            fontWeight: 600,
            height: 28,
            minWidth: 100,
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '-100%',
              width: '100%',
              height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
              transition: 'left 0.6s ease',
              zIndex: 1
            },
            '&:hover::before': {
              left: '100%'
            },
            '& .MuiChip-label': {
              px: 1,
              zIndex: 2,
              position: 'relative'
            },
            '& .MuiChip-icon': {
              zIndex: 2,
              position: 'relative'
            },
            '&:hover': {
              background: `linear-gradient(135deg, 
                rgba(255,255,255,0.35) 0%, 
                rgba(255,255,255,0.2) 50%, 
                rgba(255,255,255,0.1) 100%)`,
              border: '1px solid rgba(255,255,255,0.5)',
              boxShadow: `0 8px 32px ${chip.color}40, 
                          0 4px 16px rgba(0,0,0,0.1),
                          inset 0 1px 0 rgba(255,255,255,0.3)`
            }
          }}
        />
      </Box>
    </Tooltip>
  );
};

// Enhanced Pillar Component with Progressive Disclosure
const PillarCard: React.FC<{
  pillar: typeof pillarData[0];
  index: number;
  onOnboardingClick?: () => void;
}> = ({ pillar, index, onOnboardingClick }) => {
  const IconComponent = pillar.icon;
  const [isHovered, setIsHovered] = useState(false);
  const { currentWorkflow } = useWorkflowStore();

  // Use live workflow tasks if available
  const liveTasksForPillar = (currentWorkflow?.tasks && currentWorkflow.tasks.length > 0
    ? currentWorkflow.tasks
    : pillar.todayTasks || []).filter((t: any) => t.pillarId === pillar.id);
  const totalForPillar = liveTasksForPillar.length;
  const doneForPillar = liveTasksForPillar.filter((t: any) => t.status === 'completed' || t.status === 'skipped').length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      whileHover={{ y: -5, scale: 1.02 }}
    >
      <Paper
        elevation={8}
        sx={{
          height: isHovered ? 280 : 120, // Dynamic height based on hover state
          background: pillar.gradient,
          color: 'white',
          cursor: 'pointer',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          // Large tick when pillar tasks complete (uses live store counts)
          '&::after': {
            content: doneForPillar > 0 && doneForPillar === totalForPillar ? '"✓"' : '""',
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: '64px',
            color: 'rgba(255,255,255,0.9)',
            textShadow: '0 4px 12px rgba(0,0,0,0.5)',
            pointerEvents: 'none',
            zIndex: 10, // Ensure tick is above all content
            fontWeight: 'bold'
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%)',
            opacity: isHovered ? 1 : 0,
            transition: 'opacity 0.3s ease'
          },
          '&:hover': {
            boxShadow: `0 12px 24px ${pillar.color}40`
          }
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Shooting star border animation */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            borderRadius: 'inherit',
            overflow: 'hidden',
            zIndex: 1,
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '-100%',
              width: '100%',
              height: '2px',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent)',
              animation: 'shootingStar 8s linear infinite',
            },
            '@keyframes shootingStar': {
              '0%': { left: '-100%' },
              '100%': { left: '100%' },
            },
          }}
        />
        <CardContent sx={{ p: 1.5, height: '100%', display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 2 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, position: 'relative' }}>
            <Box
              sx={{
                p: 0.6,
                borderRadius: '50%',
                backgroundColor: 'rgba(255,255,255,0.2)',
                mr: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <IconComponent sx={{ fontSize: 16, color: 'white' }} />
            </Box>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1rem' }}>
              {pillar.title}
            </Typography>
            {/* Pillar task count badge */}
            <Box sx={{ ml: 1, position: 'relative' }}>
              <Box
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.9)',
                  color: pillar.color,
                  borderRadius: '12px',
                  px: 0.75,
                  py: 0.1,
                  fontSize: '0.65rem',
                  fontWeight: 800,
                  boxShadow: '0 2px 6px rgba(0,0,0,0.2)'
                }}
              >
                {totalForPillar}
              </Box>
            </Box>
            {/* More Options Indicator */}
            {!isHovered && (
              <motion.div
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                style={{ marginLeft: 'auto' }}
              >
                <Typography variant="caption" sx={{ fontSize: '0.6rem', opacity: 0.7 }}>
                  ⋯
                </Typography>
              </motion.div>
            )}
          </Box>

          {/* Chips Layout with Progressive Disclosure */}
          {pillar.id === 'generate' ? (
            <GeneratePillarChips index={index} isHovered={isHovered} />
          ) : pillar.id === 'publish' ? (
            <PublishPillarChips isHovered={isHovered} pillarColor={pillar.color} />
          ) : pillar.id === 'analyze' ? (
            <AnalyzePillarChips isHovered={isHovered} pillarColor={pillar.color} />
          ) : pillar.id === 'engage' ? (
            <EngagePillarChips isHovered={isHovered} pillarColor={pillar.color} />
          ) : (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
                flexGrow: 1,
                justifyContent: isHovered ? 'center' : 'flex-start'
              }}
            >
              {/* Today Chip - Always Visible */}
              <EnhancedTodayChip
                pillarId={pillar.id}
                pillarTitle={pillar.title}
                pillarColor={pillar.color}
                tasks={pillar.todayTasks}
                delay={index * 5}
              />
              
              {/* Additional Chips - Progressive Disclosure */}
              <AnimatePresence>
                {isHovered && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    style={{ overflow: 'hidden' }}
                  >
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mt: 0.5 }}>
                      {pillar.id === 'plan' ? (
                        <>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.1 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.onboarding} delay={index * 5 + 1} onOnboardingClick={onOnboardingClick} />
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.2 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.strategy} delay={index * 5 + 2} />
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.3 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.calendar} delay={index * 5 + 3} />
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.4 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.review} delay={index * 5 + 4} />
                          </motion.div>
                        </>
                      ) : pillar.id === 'remarket' ? (
                        <>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.1 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.good} delay={index * 5 + 1} />
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.2 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.bad} delay={index * 5 + 2} />
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.3 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.ugly} delay={index * 5 + 3} />
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.4 }}
                          >
                            <ChipWithTooltip chip={pillar.chips.review} delay={index * 5 + 4} />
                          </motion.div>
                        </>
                      ) : null}
                    </Box>
                  </motion.div>
                )}
              </AnimatePresence>
            </Box>
          )}
        </CardContent>
      </Paper>
    </motion.div>
  );
};

// Main Content Lifecycle Pillars Component
const ContentLifecyclePillars: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [onboardingModalOpen, setOnboardingModalOpen] = useState(false);

  // Workflow store hooks
  const {
    currentWorkflow,
    workflowProgress,
    isLoading: workflowLoading,
    startWorkflow,
  } = useWorkflowStore();

  const handleOnboardingClick = () => {
    setOnboardingModalOpen(true);
  };

  const handleCloseModal = () => {
    setOnboardingModalOpen(false);
  };

  const handleStartWorkflow = async () => {
    try {
      if (currentWorkflow) {
        await startWorkflow(currentWorkflow.id);
      }
    } catch (error) {
      console.error('Failed to start workflow:', error);
    }
  };

  // Check if workflow is active (in progress or completed)
  const isWorkflowActive = currentWorkflow?.workflowStatus === 'in_progress' || 
                          currentWorkflow?.workflowStatus === 'completed';

  return (
    <>
      <Box
        sx={{
          py: 3,
          background: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
          backdropFilter: 'blur(8px)',
          borderRadius: 2,
          mb: 4,
          position: 'relative', // For hero section positioning
        }}
      >
        <Container maxWidth="xl">
          {/* Pillars Grid */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: 'repeat(2, 1fr)',
                sm: 'repeat(3, 1fr)',
                md: 'repeat(6, 1fr)'
              },
              gap: 2,
              overflow: 'visible'
            }}
          >
            {pillarData.map((pillar, index) => (
              <PillarCard
                key={pillar.id}
                pillar={pillar}
                index={index}
                onOnboardingClick={handleOnboardingClick}
              />
            ))}
          </Box>
        </Container>

        {/* Hero Section Overlay */}
        <WorkflowHeroSection
          onStartWorkflow={handleStartWorkflow}
          isWorkflowActive={isWorkflowActive}
          isLoading={workflowLoading}
        />
      </Box>

      {/* Onboarding Modal */}
      <OnboardingModal
        open={onboardingModalOpen}
        onClose={handleCloseModal}
      />
    </>
  );
};

export default ContentLifecyclePillars;