/**
 * Backlinking Feature Styles
 *
 * CSS-in-JS styles and utility classes for the Backlinking feature.
 * All styles are scoped to prevent conflicts with other ALwrity features.
 */

import { SxProps, Theme } from '@mui/material/styles';

export const BacklinkingStyles = {
  // Main container styles with AI background
  container: {
    maxWidth: 1280,
    margin: '0 auto',
    padding: '2rem',
    minHeight: '100vh',
    background: `
      radial-gradient(ellipse at top, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95))
    `,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed',
    fontFamily: '"Inter", sans-serif',
    position: 'relative',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.3)',
      zIndex: 0,
    },
  } as SxProps<Theme>,

  // Header section styling
  header: {
    textAlign: 'center',
    marginBottom: '3rem',
  } as SxProps<Theme>,

  headerTitle: {
    fontSize: '2.5rem',
    fontWeight: 800,
    background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '0.5rem',
    fontFamily: '"Inter", sans-serif',
    textShadow: '0 0 30px rgba(96, 165, 250, 0.5)',
  } as SxProps<Theme>,

  headerSubtitle: {
    fontSize: '1.2rem',
    color: 'text.secondary',
    maxWidth: 600,
    margin: '0 auto',
  } as SxProps<Theme>,

  // Modal styles for dialogs
  modal: {
    background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    boxShadow: '0 32px 128px rgba(0, 0, 0, 0.5)',
  } as SxProps<Theme>,

  modalTitle: {
    fontSize: '1.5rem',
    fontWeight: 700,
    background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '0.5rem',
  } as SxProps<Theme>,

  modalSubtitle: {
    fontSize: '1rem',
    color: 'text.secondary',
    marginBottom: '1rem',
  } as SxProps<Theme>,

  // Card grid layout
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
    gap: '2rem',
    marginBottom: '2rem',
  } as SxProps<Theme>,

  // AI-themed Campaign card styles
  campaignCard: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    cursor: 'pointer',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    borderRadius: '16px',
    overflow: 'hidden',
    background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: '0 16px 64px rgba(96, 165, 250, 0.25)',
      borderColor: 'rgba(96, 165, 250, 0.3)',
    },
  } as SxProps<Theme>,

  campaignCardHeader: {
    padding: '1.5rem',
    borderBottom: '1px solid',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
    position: 'relative',
    zIndex: 2,
  } as SxProps<Theme>,

  campaignCardContent: {
    padding: '1.5rem',
    flexGrow: 1,
    position: 'relative',
    zIndex: 2,
  } as SxProps<Theme>,

  campaignCardActions: {
    padding: '1rem 1.5rem',
    borderTop: '1px solid',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    position: 'relative',
    zIndex: 2,
  } as SxProps<Theme>,

  // Status indicators
  statusBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '20px',
    fontSize: '0.75rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  } as SxProps<Theme>,

  // Action buttons styling
  actionButton: {
    borderRadius: '12px',
    padding: '8px 16px',
    fontSize: '0.875rem',
    fontWeight: 600,
    textTransform: 'none',
    transition: 'all 0.2s ease-in-out',
    '&:hover': {
      transform: 'translateY(-1px)',
    },
  } as SxProps<Theme>,

  primaryActionButton: {
    background: 'linear-gradient(135deg, #06B6D4 0%, #60A5FA 50%, #A855F7 100%)',
    color: 'white',
    boxShadow: '0 4px 15px rgba(96, 165, 250, 0.4)',
    border: '1px solid rgba(96, 165, 250, 0.3)',
    position: 'relative',
    overflow: 'hidden',
    '&:hover': {
      background: 'linear-gradient(135deg, #0891B2 0%, #3B82F6 50%, #9333EA 100%)',
      boxShadow: '0 8px 32px rgba(96, 165, 250, 0.6)',
      borderColor: 'rgba(96, 165, 250, 0.5)',
      transform: 'translateY(-2px)',
    },
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: '-100%',
      width: '100%',
      height: '100%',
      background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
      transition: 'left 0.5s',
    },
    '&:hover::before': {
      left: '100%',
    },
  } as SxProps<Theme>,

  // Wizard dialog styles
  wizardDialog: {
    '& .MuiDialog-paper': {
      borderRadius: '20px',
      maxWidth: '600px',
      width: '100%',
    },
  } as SxProps<Theme>,

  wizardStepper: {
    padding: '2rem 2rem 1rem',
    '& .MuiStepConnector-line': {
      borderColor: 'rgba(102, 126, 234, 0.3)',
    },
  } as SxProps<Theme>,

  wizardStepContent: {
    padding: '1rem 2rem 2rem',
    minHeight: '300px',
  } as SxProps<Theme>,

  // Form field styling
  formField: {
    marginBottom: '1.5rem',
    '& .MuiInputLabel-root': {
      fontWeight: 600,
      color: 'text.primary',
    },
    '& .MuiOutlinedInput-root': {
      borderRadius: '12px',
      '&:hover .MuiOutlinedInput-notchedOutline': {
        borderColor: '#667eea',
      },
      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
        borderColor: '#667eea',
        borderWidth: 2,
      },
    },
  } as SxProps<Theme>,

  // Keyword chip styling
  keywordChip: {
    margin: '0.25rem',
    borderRadius: '8px',
    background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
    color: '#667eea',
    '&:hover': {
      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
    },
  } as SxProps<Theme>,

  // Loading and empty states
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    textAlign: 'center',
  } as SxProps<Theme>,

  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '500px',
    textAlign: 'center',
    padding: '2rem',
  } as SxProps<Theme>,

  emptyStateIcon: {
    fontSize: '4rem',
    color: 'text.secondary',
    marginBottom: '1rem',
    opacity: 0.5,
  } as SxProps<Theme>,

  emptyStateTitle: {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: 'text.primary',
    marginBottom: '0.5rem',
  } as SxProps<Theme>,

  emptyStateDescription: {
    fontSize: '1rem',
    color: 'text.secondary',
    maxWidth: '500px',
    marginBottom: '2rem',
    lineHeight: 1.6,
  } as SxProps<Theme>,

  // Analytics and stats cards
  statsCard: {
    padding: '1.5rem',
    borderRadius: '16px',
    background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
    border: '1px solid',
    borderColor: 'divider',
  } as SxProps<Theme>,

  statsValue: {
    fontSize: '2rem',
    fontWeight: 700,
    color: 'primary.main',
    marginBottom: '0.5rem',
  } as SxProps<Theme>,

  statsLabel: {
    fontSize: '0.875rem',
    color: 'text.secondary',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    fontWeight: 600,
  } as SxProps<Theme>,

  // Progress indicators
  progressContainer: {
    marginTop: '2rem',
    marginBottom: '2rem',
  } as SxProps<Theme>,

  progressBar: {
    height: '8px',
    borderRadius: '4px',
    backgroundColor: 'rgba(102, 126, 234, 0.1)',
    '& .MuiLinearProgress-bar': {
      borderRadius: '4px',
      background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
    },
  } as SxProps<Theme>,

  // AI-themed Animations
  fadeIn: {
    animation: 'fadeIn 0.5s ease-in-out',
    '@keyframes fadeIn': {
      '0%': { opacity: 0 },
      '100%': { opacity: 1 },
    },
  } as SxProps<Theme>,

  slideUp: {
    animation: 'slideUp 0.3s ease-out',
    '@keyframes slideUp': {
      '0%': {
        opacity: 0,
        transform: 'translateY(20px)',
      },
      '100%': {
        opacity: 1,
        transform: 'translateY(0)',
      },
    },
  } as SxProps<Theme>,

  // AI Neural Pulse Animation
  neuralPulse: {
    animation: 'neuralPulse 2s ease-in-out infinite',
    '@keyframes neuralPulse': {
      '0%, 100%': {
        opacity: 0.4,
        transform: 'scale(1)',
        boxShadow: '0 0 30px rgba(96, 165, 250, 0.6)',
      },
      '50%': {
        opacity: 1,
        transform: 'scale(1.05)',
        boxShadow: '0 0 30px rgba(6, 182, 212, 0.8)',
      },
    },
  } as SxProps<Theme>,

  // Quantum Pulse Animation
  quantumPulse: {
    animation: 'quantumPulse 3s ease-in-out infinite',
    '@keyframes quantumPulse': {
      '0%, 100%': {
        boxShadow: '0 0 30px rgba(6, 182, 212, 0.6)',
        transform: 'scale(1)',
      },
      '33%': {
        boxShadow: '0 0 30px rgba(96, 165, 250, 0.6)',
        transform: 'scale(1.02)',
      },
      '66%': {
        boxShadow: '0 0 30px rgba(168, 85, 247, 0.6)',
        transform: 'scale(1.02)',
      },
    },
  } as SxProps<Theme>,

  // Glow Pulse Animation
  glowPulse: {
    animation: 'glowPulse 2s ease-in-out infinite',
    '@keyframes glowPulse': {
      '0%, 100%': {
        boxShadow: '0 8px 32px rgba(96, 165, 250, 0.3)',
      },
      '50%': {
        boxShadow: '0 0 60px rgba(6, 182, 212, 0.4)',
      },
    },
  } as SxProps<Theme>,

  // AI Float Animation
  aiFloat: {
    animation: 'aiFloat 4s ease-in-out infinite',
    '@keyframes aiFloat': {
      '0%, 100%': {
        transform: 'translateY(0px) rotate(0deg)',
      },
      '25%': {
        transform: 'translateY(-10px) rotate(1deg)',
      },
      '50%': {
        transform: 'translateY(-5px) rotate(0deg)',
      },
      '75%': {
        transform: 'translateY(-15px) rotate(-1deg)',
      },
    },
  } as SxProps<Theme>,

  // Utility classes
  centerContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  } as SxProps<Theme>,

  spaceBetween: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  } as SxProps<Theme>,

  flexColumn: {
    display: 'flex',
    flexDirection: 'column',
  } as SxProps<Theme>,

  fullWidth: {
    width: '100%',
  } as SxProps<Theme>,

  // Responsive design utilities
  responsiveGrid: {
    display: 'grid',
    gridTemplateColumns: {
      xs: '1fr',
      sm: 'repeat(2, 1fr)',
      md: 'repeat(3, 1fr)',
      lg: 'repeat(4, 1fr)',
    },
    gap: '1rem',
  } as SxProps<Theme>,
};