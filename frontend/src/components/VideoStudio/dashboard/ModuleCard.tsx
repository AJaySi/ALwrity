import React, { useState } from 'react';
import {
  Box,
  Paper,
  Stack,
  Typography,
  Chip,
  Button,
  Tooltip,
  Divider,
} from '@mui/material';
import LaunchIcon from '@mui/icons-material/Launch';
import LockIcon from '@mui/icons-material/Lock';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import SavingsIcon from '@mui/icons-material/Savings';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import PeopleIcon from '@mui/icons-material/People';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { alpha } from '@mui/material/styles';
import type { ModuleConfig } from './types';
import { statusStyles } from './modules';
import { CreateVideoPreview, AvatarVideoPreview, EnhanceVideoPreview, VideoTranslatePreview, VideoBackgroundRemoverPreview } from './previews';
import { InfoModal } from './InfoModal';

interface ModuleCardProps {
  module: ModuleConfig;
  isHovered: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  onNavigate: (route: string) => void;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({
  module,
  isHovered,
  onMouseEnter,
  onMouseLeave,
  onNavigate,
}) => {
  const status = statusStyles[module.status];
  const disabled = module.status !== 'live';
  const [openModal, setOpenModal] = useState<'perfect-for' | 'cost' | 'ai-models' | null>(null);

  return (
    <Paper
      sx={{
        height: '100%',
        borderRadius: 4,
        p: 3.5,
        border: isHovered 
          ? '2px solid rgba(139,92,246,0.6)' 
          : '1px solid rgba(255,255,255,0.18)',
        background: isHovered
          ? 'linear-gradient(160deg, rgba(30,41,59,0.98), rgba(51,65,85,0.95))'
          : 'linear-gradient(160deg, rgba(15,23,42,0.98), rgba(30,41,59,0.95))',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        position: 'relative',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: isHovered
          ? '0 32px 64px rgba(79,70,229,0.4), 0 0 0 1px rgba(139,92,246,0.2), inset 0 1px 0 rgba(255,255,255,0.1)'
          : '0 8px 32px rgba(15,23,42,0.5), 0 0 0 1px rgba(255,255,255,0.05), inset 0 1px 0 rgba(255,255,255,0.05)',
        transform: isHovered ? 'translateY(-6px) scale(1.01)' : 'translateY(0) scale(1)',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: isHovered
            ? 'linear-gradient(90deg, #8b5cf6, #6366f1, #3b82f6, #8b5cf6)'
            : 'linear-gradient(90deg, rgba(139,92,246,0.3), rgba(99,102,241,0.2))',
          backgroundSize: '200% 100%',
          animation: isHovered ? 'shimmer 2s linear infinite' : 'none',
          '@keyframes shimmer': {
            '0%': { backgroundPosition: '200% 0' },
            '100%': { backgroundPosition: '-200% 0' },
          },
        },
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Box
            sx={{
              width: 52,
              height: 52,
              borderRadius: 2.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: isHovered
                ? 'linear-gradient(135deg, rgba(139,92,246,0.35), rgba(99,102,241,0.3))'
                : 'linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.2))',
              color: '#c7d2fe',
              fontSize: 26,
              border: '1px solid rgba(139,92,246,0.3)',
              boxShadow: isHovered 
                ? '0 8px 16px rgba(139,92,246,0.3), inset 0 1px 0 rgba(255,255,255,0.1)'
                : '0 4px 12px rgba(99,102,241,0.2)',
              transition: 'all 0.3s ease',
            }}
          >
            {module.icon}
          </Box>
          <Stack spacing={0.25}>
            <Typography 
              variant="h6" 
              fontWeight={800}
              sx={{
                color: '#f1f5f9',
                fontSize: '1.25rem',
                letterSpacing: '-0.02em',
              }}
            >
              {module.title}
            </Typography>
            <Typography 
              variant="body2" 
              sx={{
                color: 'rgba(203,213,225,0.9)',
                fontWeight: 500,
              }}
            >
              {module.subtitle}
            </Typography>
          </Stack>
        </Stack>
        <Chip
          label={status.label}
          size="small"
          sx={{
            backgroundColor: alpha(status.color, 0.25),
            color: status.color,
            fontWeight: 700,
            border: `1px solid ${alpha(status.color, 0.4)}`,
            boxShadow: `0 2px 8px ${alpha(status.color, 0.2)}`,
            fontSize: '0.7rem',
            height: 26,
          }}
        />
      </Stack>

      <Typography 
        variant="body2" 
        sx={{ 
          color: 'rgba(241,245,249,0.92)',
          lineHeight: 1.7,
          fontSize: '0.95rem',
        }}
      >
        {module.description}
      </Typography>

      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {module.highlights.map(item => (
          <Chip
            key={item}
            size="small"
            label={item}
            sx={{
              background: isHovered
                ? 'linear-gradient(120deg, rgba(139,92,246,0.5), rgba(99,102,241,0.45))'
                : 'linear-gradient(120deg, rgba(99,102,241,0.4), rgba(14,165,233,0.35))',
              color: '#f8fafc',
              border: '1px solid rgba(255,255,255,0.4)',
              fontWeight: 600,
              letterSpacing: 0.3,
              fontSize: '0.75rem',
              height: 28,
              boxShadow: '0 2px 8px rgba(99,102,241,0.2)',
              transition: 'all 0.3s ease',
            }}
          />
        ))}
      </Stack>

      {/* Info Chips */}
      <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap>
        {module.perfectFor && (
          <Chip
            icon={<PeopleIcon sx={{ fontSize: 18 }} />}
            label="Perfect for"
            onClick={() => setOpenModal(openModal === 'perfect-for' ? null : 'perfect-for')}
            sx={{
              background: openModal === 'perfect-for'
                ? 'linear-gradient(120deg, rgba(139,92,246,0.5), rgba(99,102,241,0.45))'
                : 'linear-gradient(120deg, rgba(139,92,246,0.3), rgba(99,102,241,0.25))',
              color: '#c7d2fe',
              border: '2px solid rgba(139,92,246,0.6)',
              fontWeight: 700,
              fontSize: '0.8rem',
              height: 36,
              cursor: 'pointer',
              px: 2,
              py: 1,
              boxShadow: openModal === 'perfect-for'
                ? '0 4px 12px rgba(139,92,246,0.4)'
                : '0 2px 8px rgba(139,92,246,0.2)',
              '&:hover': {
                background: 'linear-gradient(120deg, rgba(139,92,246,0.4), rgba(99,102,241,0.35))',
                border: '2px solid rgba(139,92,246,0.8)',
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 16px rgba(139,92,246,0.4)',
              },
              transition: 'all 0.2s ease',
            }}
          />
        )}
        {module.costDetails && (
          <Chip
            icon={<AttachMoneyIcon sx={{ fontSize: 18 }} />}
            label="Cost depends on"
            onClick={() => setOpenModal(openModal === 'cost' ? null : 'cost')}
            sx={{
              background: openModal === 'cost'
                ? 'linear-gradient(120deg, rgba(14,165,233,0.5), rgba(56,189,248,0.45))'
                : 'linear-gradient(120deg, rgba(14,165,233,0.3), rgba(56,189,248,0.25))',
              color: '#7dd3fc',
              border: '2px solid rgba(56,189,248,0.6)',
              fontWeight: 700,
              fontSize: '0.8rem',
              height: 36,
              cursor: 'pointer',
              px: 2,
              py: 1,
              boxShadow: openModal === 'cost'
                ? '0 4px 12px rgba(56,189,248,0.4)'
                : '0 2px 8px rgba(56,189,248,0.2)',
              '&:hover': {
                background: 'linear-gradient(120deg, rgba(14,165,233,0.4), rgba(56,189,248,0.35))',
                border: '2px solid rgba(56,189,248,0.8)',
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 16px rgba(56,189,248,0.4)',
              },
              transition: 'all 0.2s ease',
            }}
          />
        )}
        {module.aiModels && (
          <Chip
            icon={<SmartToyIcon sx={{ fontSize: 18 }} />}
            label="AI Models"
            onClick={() => setOpenModal(openModal === 'ai-models' ? null : 'ai-models')}
            sx={{
              background: openModal === 'ai-models'
                ? 'linear-gradient(120deg, rgba(16,185,129,0.5), rgba(34,197,94,0.45))'
                : 'linear-gradient(120deg, rgba(16,185,129,0.3), rgba(34,197,94,0.25))',
              color: '#99f6e4',
              border: '2px solid rgba(34,197,94,0.6)',
              fontWeight: 700,
              fontSize: '0.8rem',
              height: 36,
              cursor: 'pointer',
              px: 2,
              py: 1,
              boxShadow: openModal === 'ai-models'
                ? '0 4px 12px rgba(34,197,94,0.4)'
                : '0 2px 8px rgba(34,197,94,0.2)',
              '&:hover': {
                background: 'linear-gradient(120deg, rgba(16,185,129,0.4), rgba(34,197,94,0.35))',
                border: '2px solid rgba(34,197,94,0.8)',
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 16px rgba(34,197,94,0.4)',
              },
              transition: 'all 0.2s ease',
            }}
          />
        )}
      </Stack>

      {/* Visual Preview Component */}
      {(module.status === 'live' || module.status === 'beta') && (
        <Box sx={{ mt: 1.5 }}>
          {module.key === 'create' && <CreateVideoPreview />}
          {module.key === 'avatar' && <AvatarVideoPreview />}
          {module.key === 'enhance' && <EnhanceVideoPreview />}
          {module.key === 'video-translate' && <VideoTranslatePreview />}
          {module.key === 'video-background-remover' && <VideoBackgroundRemoverPreview />}
        </Box>
      )}

      <Stack 
        direction="row" 
        spacing={1.5} 
        alignItems="center" 
        sx={{ 
          mt: 'auto',
          pt: 2,
          borderTop: '1px solid rgba(255,255,255,0.1)',
        }}
      >
        <Button
          variant="contained"
          size="medium"
          startIcon={disabled ? <LockIcon /> : <LaunchIcon />}
          disabled={disabled}
          onClick={() => onNavigate(module.route)}
          sx={{
            textTransform: 'none',
            fontWeight: 700,
            fontSize: '0.95rem',
            px: 3,
            py: 1.25,
            background: disabled 
              ? 'rgba(148,163,184,0.25)' 
              : isHovered
                ? 'linear-gradient(120deg, #8b5cf6, #6366f1)'
                : 'linear-gradient(120deg, #6366f1, #8b5cf6)',
            boxShadow: disabled
              ? 'none'
              : isHovered
                ? '0 8px 24px rgba(139,92,246,0.5), 0 0 0 1px rgba(255,255,255,0.1)'
                : '0 4px 16px rgba(99,102,241,0.4)',
            '&:hover': {
              background: 'linear-gradient(120deg, #8b5cf6, #6366f1)',
              boxShadow: '0 12px 32px rgba(139,92,246,0.6), 0 0 0 1px rgba(255,255,255,0.15)',
              transform: 'translateY(-2px)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          {disabled ? 'Preview' : 'Open Studio'}
        </Button>
        <Tooltip 
          title="View detailed feature documentation and use cases"
          arrow
          placement="top"
        >
          <Button
            size="medium"
            variant="text"
            color="inherit"
            onClick={() => onNavigate(module.route)}
            sx={{ 
              textTransform: 'none', 
              color: 'rgba(199,210,254,0.9)',
              fontWeight: 600,
              fontSize: '0.9rem',
              '&:hover': {
                color: '#c7d2fe',
                background: 'rgba(139,92,246,0.1)',
              },
            }}
          >
            Learn more
          </Button>
        </Tooltip>
      </Stack>

      {/* Info Modals - Open on Click */}
      {module.perfectFor && (
        <InfoModal
          open={openModal === 'perfect-for'}
          onClose={() => setOpenModal(null)}
          title={`Perfect for - ${module.title}`}
          type="perfect-for"
          perfectFor={module.perfectFor}
        />
      )}
      {module.costDetails && (
        <InfoModal
          open={openModal === 'cost'}
          onClose={() => setOpenModal(null)}
          title={`Cost Information - ${module.title}`}
          type="cost"
          costDetails={module.costDetails}
        />
      )}
      {module.aiModels && (
        <InfoModal
          open={openModal === 'ai-models'}
          onClose={() => setOpenModal(null)}
          title={`AI Models & Capabilities - ${module.title}`}
          type="ai-models"
          aiModels={module.aiModels}
        />
      )}
    </Paper>
  );
};
