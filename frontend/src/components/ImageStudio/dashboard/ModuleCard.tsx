import React from 'react';
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
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import LaunchIcon from '@mui/icons-material/Launch';
import LockIcon from '@mui/icons-material/Lock';
import { alpha } from '@mui/material/styles';
import { ModuleConfig } from './types';
import { statusStyles } from './constants';
import { ModuleInfoCard } from './ModuleInfoCard';
import {
  CreateEffectPreview,
  EditEffectPreview,
  UpscaleEffectPreview,
  TransformEffectPreview,
  SocialOptimizerEffectPreview,
  ControlEffectPreview,
} from './previews';

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
  const hasPreview =
    module.key === 'create' ||
    module.key === 'edit' ||
    module.key === 'upscale' ||
    module.key === 'transform' ||
    module.key === 'optimizer' ||
    module.key === 'control';

  const renderPreview = () => {
    switch (module.key) {
      case 'create':
        return <CreateEffectPreview />;
      case 'edit':
        return <EditEffectPreview />;
      case 'upscale':
        return <UpscaleEffectPreview />;
      case 'transform':
        return <TransformEffectPreview />;
      case 'optimizer':
        return <SocialOptimizerEffectPreview />;
      case 'control':
        return <ControlEffectPreview />;
      default:
        return null;
    }
  };

  return (
    <Paper
      sx={{
        height: '100%',
        borderRadius: 4,
        p: 3,
        border: '1px solid rgba(255,255,255,0.06)',
        background: alpha('#111827', 0.8),
        display: 'flex',
        flexDirection: 'column',
        gap: 1.5,
        position: 'relative',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        boxShadow: isHovered
          ? '0 20px 45px rgba(124,58,237,0.25)'
          : '0 10px 25px rgba(15,23,42,0.35)',
        transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
        overflow: 'hidden',
        '&::after': {
          content: '""',
          position: 'absolute',
          inset: 0,
          background:
            module.key === 'create'
              ? 'radial-gradient(circle at top, rgba(124,58,237,0.25), transparent 60%)'
              : module.key === 'edit'
              ? 'linear-gradient(120deg, rgba(8,145,178,0.25), transparent)'
              : module.key === 'upscale'
              ? 'linear-gradient(90deg, rgba(248,113,113,0.25), transparent)'
              : 'linear-gradient(120deg, rgba(59,130,246,0.15), transparent)',
          opacity: isHovered ? 1 : 0.35,
          pointerEvents: 'none',
        },
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Stack direction="row" spacing={1} alignItems="center">
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: alpha('#6366f1', 0.2),
              color: '#c7d2fe',
              fontSize: 22,
            }}
          >
            {module.icon}
          </Box>
          <Stack spacing={0.5}>
            <Typography variant="h6" fontWeight={700}>
              {module.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {module.subtitle}
            </Typography>
          </Stack>
        </Stack>
        <Chip
          label={status.label}
          size="small"
          sx={{
            backgroundColor: alpha(status.color, 0.2),
            color: status.color,
            fontWeight: 700,
          }}
        />
      </Stack>

      <Stack direction="row" spacing={1} alignItems="center">
        <Typography
          variant="body2"
          sx={{
            color: hasPreview
              ? 'rgba(248,250,252,0.92)'
              : 'rgba(148,163,184,0.95)',
          }}
        >
          {module.description}
        </Typography>
      </Stack>

      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {module.highlights.map(item => (
          <Chip
            key={item}
            size="small"
            label={item}
            sx={{
              background: 'linear-gradient(120deg, rgba(99,102,241,0.35), rgba(14,165,233,0.35))',
              color: '#f1f5f9',
              border: '1px solid rgba(255,255,255,0.3)',
              fontWeight: 600,
              letterSpacing: 0.2,
            }}
          />
        ))}
      </Stack>

      {hasPreview && (
        <>
          {renderPreview()}
          <ModuleInfoCard module={module} />
        </>
      )}

      {!hasPreview && (
        <Box
          sx={{
            position: 'absolute',
            inset: 16,
            borderRadius: 3,
            border: '1px solid rgba(255,255,255,0.1)',
            background: 'rgba(15,23,42,0.92)',
            backdropFilter: 'blur(12px)',
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
            padding: 2,
            opacity: isHovered ? 1 : 0,
            pointerEvents: 'none',
            transition: 'opacity 0.2s ease',
          }}
        >
          <Typography variant="overline" sx={{ color: '#a5b4fc', letterSpacing: 1 }}>
            Pricing & How it works
          </Typography>
          <Stack spacing={0.5}>
            <Typography variant="body2" fontWeight={700}>
              {module.pricing.estimate}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {module.pricing.notes}
            </Typography>
          </Stack>
          <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />
          <Typography variant="subtitle2" fontWeight={700}>
            {module.example.title}
          </Typography>
          <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
            {module.example.steps.map(step => (
              <Typography
                component="li"
                key={step}
                variant="body2"
                color="text.secondary"
              >
                {step}
              </Typography>
            ))}
          </Stack>
          <Typography variant="caption" color="text.secondary">
            ETA: {module.example.eta}
          </Typography>
        </Box>
      )}

      <Stack direction="row" spacing={1} alignItems="center" mt="auto">
        <Tooltip title={module.help}>
          <InfoOutlinedIcon sx={{ color: 'rgba(255,255,255,0.6)', fontSize: 20 }} />
        </Tooltip>
        <Button
          variant="contained"
          disabled={disabled}
          startIcon={disabled ? <LockIcon /> : <LaunchIcon />}
          onClick={() => {
            if (!disabled && module.route) {
              onNavigate(module.route);
            }
          }}
          sx={{
            borderRadius: 999,
            textTransform: 'none',
            fontWeight: 700,
            ml: 'auto',
            background: disabled
              ? 'rgba(148,163,184,0.2)'
              : 'linear-gradient(90deg,#7c3aed,#2563eb)',
          }}
        >
          {disabled ? 'Coming Soon' : 'Open'}
        </Button>
      </Stack>
    </Paper>
  );
};

