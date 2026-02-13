/**
 * Backlinking Styled Components
 *
 * Reusable styled components specifically for the Backlinking feature.
 */

import { styled, Box, Card, Button, Chip, TextField, IconButton } from '@mui/material';
import { motion } from 'framer-motion';

// Animated containers
export const AnimatedContainer = styled(motion.div)(() => ({
  width: '100%',
}));

export const FadeInContainer = styled(AnimatedContainer)(() => ({
  animation: 'fadeIn 0.5s ease-in-out',
  '@keyframes fadeIn': {
    '0%': { opacity: 0 },
    '100%': { opacity: 1 },
  },
}));

export const SlideUpContainer = styled(AnimatedContainer)(() => ({
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
}));

// AI-themed styled card for campaigns with glass morphism and neural patterns
export const CampaignCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  cursor: 'pointer',
  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
  borderRadius: '16px',
  overflow: 'hidden',
  background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: '0 8px 32px rgba(96, 165, 250, 0.15)',
  position: 'relative',
  '&:hover': {
    boxShadow: '0 16px 64px rgba(96, 165, 250, 0.25)',
    transform: 'translateY(-4px)',
    borderColor: 'rgba(96, 165, 250, 0.3)',
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `
      radial-gradient(circle at 20% 20%, rgba(96, 165, 250, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 40% 70%, rgba(6, 182, 212, 0.05) 0%, transparent 50%)
    `,
    pointerEvents: 'none',
    zIndex: 1,
  },
}));

export const CampaignCardHeader = styled(Box)(() => ({
  padding: '1.5rem',
  borderBottom: '1px solid',
  borderColor: 'divider',
  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
}));

export const CampaignCardContent = styled(Box)(() => ({
  padding: '1.5rem',
  flexGrow: 1,
}));

export const CampaignCardActions = styled(Box)(() => ({
  padding: '1rem 1.5rem',
  borderTop: '1px solid',
  borderColor: 'divider',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
}));

// AI Quantum Gradient buttons with shimmer effect
export const GradientButton = styled(Button)(() => ({
  background: 'linear-gradient(135deg, #06B6D4 0%, #60A5FA 50%, #A855F7 100%)',
  color: 'white',
  borderRadius: '12px',
  padding: '12px 24px',
  fontWeight: 600,
  fontFamily: '"Inter", sans-serif',
  textTransform: 'none',
  boxShadow: '0 4px 15px rgba(96, 165, 250, 0.4)',
  border: '1px solid rgba(96, 165, 250, 0.3)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
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
}));

// Status chips with custom styling
export const StatusChip = styled(Chip)(() => ({
  borderRadius: '8px',
  fontWeight: 500,
  '&.status-active': {
    backgroundColor: 'rgba(46, 125, 50, 0.1)',
    color: '#2e7d32',
  },
  '&.status-paused': {
    backgroundColor: 'rgba(237, 108, 2, 0.1)',
    color: '#ed6c02',
  },
  '&.status-completed': {
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
    color: '#2196f3',
  },
}));

// AI-themed text field with glass morphism
export const BacklinkingTextField = styled(TextField)(() => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: '12px',
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
}));

// Animated icon button
export const AnimatedIconButton = styled(IconButton)(() => ({
  transition: 'all 0.2s ease-in-out',
  borderRadius: '12px',
  padding: '12px',
  '&:hover': {
    transform: 'scale(1.05)',
    backgroundColor: 'rgba(102, 126, 234, 0.1)',
  },
}));

// Stats display component
export const StatsCard = styled(Box)(() => ({
  padding: '1.5rem',
  borderRadius: '16px',
  background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  border: '1px solid #e0e0e0',
  textAlign: 'center',
}));

export const StatsValue = styled(Box)(() => ({
  fontSize: '2rem',
  fontWeight: 700,
  color: '#667eea',
  marginBottom: '0.5rem',
}));

export const StatsLabel = styled(Box)(() => ({
  fontSize: '0.875rem',
  color: '#666',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  fontWeight: 600,
}));

// Empty state container
export const EmptyStateContainer = styled(Box)(() => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '500px',
  textAlign: 'center',
  padding: '2rem',
}));

// Loading skeleton with custom styling
export const LoadingContainer = styled(Box)(() => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '400px',
  textAlign: 'center',
}));

// AI-themed keyword display chip
export const KeywordChip = styled(Chip)(() => ({
  margin: '0.25rem',
  borderRadius: '8px',
  background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
  color: '#60A5FA',
  border: '1px solid rgba(96, 165, 250, 0.2)',
  backdropFilter: 'blur(5px)',
  fontFamily: '"Inter", sans-serif',
  '&:hover': {
    background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)',
    borderColor: 'rgba(96, 165, 250, 0.4)',
    boxShadow: '0 0 10px rgba(96, 165, 250, 0.3)',
  },
}));