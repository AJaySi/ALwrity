/**
 * Backlinking Feature Theme
 *
 * Custom theme overrides specifically for the Backlinking feature.
 * This theme is feature-contained and doesn't affect global ALwrity styling.
 */

import { ThemeOptions } from '@mui/material/styles';

export const BacklinkingTheme: ThemeOptions = {
  // Futuristic AI Color Palette
  palette: {
    mode: 'dark' as const,
    primary: {
      main: '#60A5FA', // Electric blue
      dark: '#3B82F6',
      light: '#93C5FD',
    },
    secondary: {
      main: '#A855F7', // Neural purple
      dark: '#9333EA',
      light: '#C084FC',
    },
    background: {
      default: '#0F172A', // Dark background
      paper: '#1E293B',   // Card background
    },
    text: {
      primary: '#F1F5F9',
      secondary: '#CBD5E1',
    },
  },

  // Typography with Inter font
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 800,
      background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h2: {
      fontWeight: 700,
      background: 'linear-gradient(135deg, #06B6D4 0%, #60A5FA 100%)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h3: {
      fontWeight: 600,
      color: '#F1F5F9',
    },
  },

  // Component-specific overrides with AI theme
  components: {
    // Enhanced Card styling with glass morphism
    MuiCard: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 12,
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 8px 32px rgba(96, 165, 250, 0.15)',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 16px 64px rgba(96, 165, 250, 0.25)',
            transform: 'translateY(-4px)',
            borderColor: 'rgba(96, 165, 250, 0.3)',
          },
        }),
      },
    },

    // Futuristic AI Button styling
    MuiButton: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 12,
          textTransform: 'none' as const,
          fontWeight: 600,
          padding: '12px 24px',
          fontFamily: '"Inter", sans-serif',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&:hover': {
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
        }),
        contained: {
          background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
          boxShadow: '0 4px 15px rgba(96, 165, 250, 0.4)',
          border: '1px solid rgba(96, 165, 250, 0.3)',
          '&:hover': {
            background: 'linear-gradient(135deg, #3B82F6 0%, #9333EA 100%)',
            boxShadow: '0 8px 32px rgba(96, 165, 250, 0.6)',
            borderColor: 'rgba(96, 165, 250, 0.5)',
          },
        },
        outlined: {
          borderWidth: 2,
          borderColor: 'rgba(96, 165, 250, 0.5)',
          color: '#60A5FA',
          '&:hover': {
            borderWidth: 2,
            backgroundColor: 'rgba(96, 165, 250, 0.1)',
            borderColor: '#60A5FA',
            boxShadow: '0 0 20px rgba(96, 165, 250, 0.3)',
          },
        },
      },
    },

    // AI-themed Chip styling
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
          fontFamily: '"Inter", sans-serif',
          backdropFilter: 'blur(10px)',
        },
        colorSuccess: {
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          color: '#10B981',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          boxShadow: '0 0 10px rgba(16, 185, 129, 0.2)',
          '& .MuiChip-icon': {
            color: '#10B981',
          },
        },
        colorWarning: {
          backgroundColor: 'rgba(245, 158, 11, 0.15)',
          color: '#F59E0B',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          boxShadow: '0 0 10px rgba(245, 158, 11, 0.2)',
          '& .MuiChip-icon': {
            color: '#F59E0B',
          },
        },
        colorError: {
          backgroundColor: 'rgba(239, 68, 68, 0.15)',
          color: '#EF4444',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          boxShadow: '0 0 10px rgba(239, 68, 68, 0.2)',
          '& .MuiChip-icon': {
            color: '#EF4444',
          },
        },
      },
    },

    // AI-themed TextField styling
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(96, 165, 250, 0.2)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              borderColor: 'rgba(96, 165, 250, 0.4)',
              boxShadow: '0 0 20px rgba(96, 165, 250, 0.2)',
            },
            '&.Mui-focused': {
              borderColor: '#60A5FA',
              borderWidth: 2,
              boxShadow: '0 0 30px rgba(96, 165, 250, 0.4)',
            },
            '& .MuiOutlinedInput-notchedOutline': {
              border: 'none',
            },
          },
          '& .MuiInputLabel-root': {
            color: '#CBD5E1',
            fontWeight: 600,
            fontFamily: '"Inter", sans-serif',
            '&.Mui-focused': {
              color: '#60A5FA',
            },
          },
        },
      },
    },

    // AI-themed Dialog styling
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%)',
          backdropFilter: 'blur(30px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 25px 50px rgba(96, 165, 250, 0.15)',
        },
      },
    },

    // AI-themed Stepper styling
    MuiStepper: {
      styleOverrides: {
        root: {
          padding: '24px 0',
        },
      },
    },

    MuiStepIcon: {
      styleOverrides: {
        root: {
          '&.Mui-active': {
            color: '#60A5FA',
            filter: 'drop-shadow(0 0 10px rgba(96, 165, 250, 0.5))',
          },
          '&.Mui-completed': {
            color: '#10B981',
            filter: 'drop-shadow(0 0 10px rgba(16, 185, 129, 0.5))',
          },
        },
      },
    },

    // AI-themed IconButton
    MuiIconButton: {
      styleOverrides: {
        root: {
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          borderRadius: 12,
          '&:hover': {
            transform: 'scale(1.05)',
            backgroundColor: 'rgba(96, 165, 250, 0.1)',
            boxShadow: '0 0 15px rgba(96, 165, 250, 0.3)',
          },
        },
      },
    },

    // AI-themed LinearProgress
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 10,
          backgroundColor: 'rgba(96, 165, 250, 0.1)',
        },
        bar: {
          borderRadius: 8,
          background: 'linear-gradient(90deg, #60A5FA 0%, #06B6D4 50%, #A855F7 100%)',
          boxShadow: '0 0 20px rgba(96, 165, 250, 0.4)',
        },
      },
    },
  },
};