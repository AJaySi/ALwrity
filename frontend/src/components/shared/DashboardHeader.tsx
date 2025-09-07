import React from 'react';
import { Box, Typography, Chip, Button, CircularProgress } from '@mui/material';
import { PlayArrow, Pause, Stop } from '@mui/icons-material';
import { ShimmerHeader } from './styled';
import { DashboardHeaderProps } from './types';

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ 
  title, 
  subtitle, 
  statusChips = [],
  rightContent,
  customIcon,
  workflowControls
}) => {
  return (
    <ShimmerHeader sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {customIcon && (
            <Box
              component="img"
              src={customIcon}
              alt="Alwrity Logo"
              sx={{
                width: { xs: 40, md: 48 },
                height: { xs: 40, md: 48 },
                filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.3))',
              }}
            />
          )}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box>
              <Typography variant="h2" component="h1" sx={{ 
                fontWeight: 800, 
                color: 'white',
                textShadow: '0 4px 8px rgba(0,0,0,0.3)',
                mb: subtitle ? 1 : 0,
                fontSize: { xs: '2rem', md: '3rem' },
                background: 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                {title}
              </Typography>
              {subtitle && (
                <Typography variant="h5" sx={{ 
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontWeight: 400,
                  fontSize: { xs: '1rem', md: '1.25rem' },
                }}>
                  {subtitle}
                </Typography>
              )}
            </Box>
            
            {/* Workflow Controls */}
            {workflowControls && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {/* Workflow Control Buttons */}
                {!workflowControls.isWorkflowActive ? (
                  /* Start Button with Badge and Lightning Glow */
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<PlayArrow />}
                      onClick={workflowControls.onStartWorkflow}
                      disabled={workflowControls.isLoading}
                      sx={{
                        position: 'relative',
                        overflow: 'hidden',
                        background: 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)',
                        border: '2px solid transparent',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #388e3c 0%, #2e7d32 100%)',
                        },
                        minWidth: 'auto',
                        px: 2,
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: '-100%',
                          width: '100%',
                          height: '100%',
                          background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent)',
                          animation: 'shimmer 2.5s infinite',
                          zIndex: 1,
                        },
                        '&::after': {
                          content: '""',
                          position: 'absolute',
                          top: -2,
                          left: -2,
                          right: -2,
                          bottom: -2,
                          background: 'linear-gradient(45deg, #4caf50, #8bc34a, #4caf50, #8bc34a)',
                          backgroundSize: '400% 400%',
                          borderRadius: 'inherit',
                          zIndex: -1,
                          animation: 'borderGlow 3s ease-in-out infinite',
                        },
                        '@keyframes shimmer': {
                          '0%': { left: '-100%' },
                          '100%': { left: '100%' },
                        },
                        '@keyframes borderGlow': {
                          '0%, 100%': { backgroundPosition: '0% 50%' },
                          '50%': { backgroundPosition: '100% 50%' },
                        },
                      }}
                    >
                      Start
                    </Button>
                    <Box
                      sx={{
                        position: 'absolute',
                        top: -8,
                        right: -8,
                        backgroundColor: '#1976d2',
                        color: 'white',
                        borderRadius: '12px',
                        px: 0.75,
                        py: 0.25,
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        boxShadow: '0 2px 6px rgba(0,0,0,0.3)'
                      }}
                    >
                      {`${workflowControls.completedTasks}/${workflowControls.totalTasks}`}
                    </Box>
                  </Box>
                ) : (
                  /* In-Progress/Completed Controls with Enhanced Styling */
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {/* In-Progress/Completed Status with Lightning Glow */}
                    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                      <Button
                        variant="contained"
                        size="small"
                        onClick={workflowControls.onResumePlanModal}
                        disabled={workflowControls.isLoading}
                        sx={{
                          position: 'relative',
                          overflow: 'hidden',
                          background: workflowControls.completedTasks === workflowControls.totalTasks 
                            ? 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)'
                            : 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)',
                          color: 'white',
                          minWidth: 'auto',
                          px: 2,
                          border: '2px solid transparent',
                          boxShadow: workflowControls.completedTasks === workflowControls.totalTasks
                            ? '0 8px 25px rgba(76, 175, 80, 0.4), 0 0 0 1px rgba(255,255,255,0.2)'
                            : '0 8px 25px rgba(33, 150, 243, 0.4), 0 0 0 1px rgba(255,255,255,0.2)',
                          '&:hover': {
                            background: workflowControls.completedTasks === workflowControls.totalTasks
                              ? 'linear-gradient(135deg, #388e3c 0%, #2e7d32 100%)'
                              : 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                            transform: 'translateY(-2px)',
                            boxShadow: workflowControls.completedTasks === workflowControls.totalTasks
                              ? '0 12px 35px rgba(76, 175, 80, 0.6), 0 0 0 1px rgba(255,255,255,0.3)'
                              : '0 12px 35px rgba(33, 150, 243, 0.6), 0 0 0 1px rgba(255,255,255,0.3)',
                          },
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: '-100%',
                            width: '100%',
                            height: '100%',
                            background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent)',
                            animation: workflowControls.completedTasks === workflowControls.totalTasks 
                              ? 'none' 
                              : 'shimmer 2.5s infinite',
                            zIndex: 1,
                          },
                          '&::after': {
                            content: '""',
                            position: 'absolute',
                            top: -2,
                            left: -2,
                            right: -2,
                            bottom: -2,
                            background: workflowControls.completedTasks === workflowControls.totalTasks
                              ? 'linear-gradient(45deg, #4caf50, #8bc34a, #4caf50, #8bc34a)'
                              : 'linear-gradient(45deg, #2196f3, #64b5f6, #2196f3, #64b5f6)',
                            backgroundSize: '400% 400%',
                            borderRadius: 'inherit',
                            zIndex: -1,
                            animation: 'borderGlow 3s ease-in-out infinite',
                          },
                          '@keyframes shimmer': {
                            '0%': { left: '-100%' },
                            '100%': { left: '100%' },
                          },
                          '@keyframes borderGlow': {
                            '0%, 100%': { backgroundPosition: '0% 50%' },
                            '50%': { backgroundPosition: '100% 50%' },
                          },
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        }}
                        title={workflowControls.completedTasks === workflowControls.totalTasks 
                          ? '🎉 All tasks completed! Click to review workflow progress.' 
                          : 'Workflow in progress. Click to resume or check current tasks.'}
                      >
                        {workflowControls.completedTasks === workflowControls.totalTasks ? 'Completed' : 'In Progress'}
                      </Button>
                      <Box
                        sx={{
                          position: 'absolute',
                          top: -8,
                          right: -8,
                          backgroundColor: '#1976d2',
                          color: 'white',
                          borderRadius: '12px',
                          px: 0.75,
                          py: 0.25,
                          fontSize: '0.65rem',
                          fontWeight: 700,
                          boxShadow: '0 2px 6px rgba(0,0,0,0.3)'
                        }}
                      >
                        {`${workflowControls.completedTasks}/${workflowControls.totalTasks}`}
                      </Box>
                    </Box>
                  </Box>
                )}
              </Box>
            )}
          </Box>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {statusChips.length > 0 && (
            <Box sx={{ display: 'flex', gap: 1.5 }}>
              {statusChips.map((chip, index) => (
                <Chip 
                  key={index}
                  icon={chip.icon} 
                  label={chip.label} 
                  sx={{ 
                    background: `${chip.color}20`,
                    border: `1px solid ${chip.color}40`,
                    color: chip.color,
                    fontWeight: 700,
                  }}
                />
              ))}
            </Box>
          )}
          {rightContent}
        </Box>
      </Box>
    </ShimmerHeader>
  );
};

export default DashboardHeader; 