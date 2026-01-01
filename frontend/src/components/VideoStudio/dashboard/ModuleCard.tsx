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
import LaunchIcon from '@mui/icons-material/Launch';
import LockIcon from '@mui/icons-material/Lock';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import SavingsIcon from '@mui/icons-material/Savings';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { alpha } from '@mui/material/styles';
import type { ModuleConfig } from './types';
import { statusStyles } from './modules';
import { CreateVideoPreview, AvatarVideoPreview, EnhanceVideoPreview } from './previews';

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

  return (
    <Paper
      sx={{
        height: '100%',
        borderRadius: 4,
        p: 3,
        border: '1px solid rgba(255,255,255,0.12)',
        background: 'linear-gradient(160deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92))',
        display: 'flex',
        flexDirection: 'column',
        gap: 1.75,
        position: 'relative',
        transition: 'transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease',
        boxShadow: isHovered
          ? '0 24px 50px rgba(79,70,229,0.32)'
          : '0 12px 28px rgba(15,23,42,0.35)',
        transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
        overflow: 'hidden',
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Stack direction="row" spacing={1.5} alignItems="center">
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
          <Stack spacing={0.25}>
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

      <Typography variant="body2" sx={{ color: 'rgba(241,245,249,0.95)' }}>
        {module.description}
      </Typography>

      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {module.highlights.map(item => (
          <Chip
            key={item}
            size="small"
            label={item}
            sx={{
              background: 'linear-gradient(120deg, rgba(99,102,241,0.45), rgba(14,165,233,0.38))',
              color: '#f8fafc',
              border: '1px solid rgba(255,255,255,0.35)',
              fontWeight: 600,
              letterSpacing: 0.2,
            }}
          />
        ))}
      </Stack>

      <Stack direction="row" spacing={1} alignItems="center">
        <Tooltip title={module.help || 'Guidance and intended use cases'}>
          <HelpOutlineIcon sx={{ fontSize: 18, color: 'rgba(148,163,184,0.95)' }} />
        </Tooltip>
        <Typography variant="body2" color="text.secondary">
          {module.help || 'Built for creators: pick a template and we guide duration/aspect and cost.'}
        </Typography>
      </Stack>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)' }} />

      <Stack direction="row" spacing={1} alignItems="center">
        <InfoOutlinedIcon sx={{ fontSize: 18, color: 'rgba(148,163,184,0.9)' }} />
        <Typography variant="body2" color="text.secondary">
          {module.pricingNote || 'Cost shown before run (duration, resolution, provider).'}
        </Typography>
      </Stack>

      {module.costDrivers && (
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {module.costDrivers.map(driver => (
            <Chip
              key={driver}
              size="small"
              icon={<SavingsIcon sx={{ fontSize: 16 }} />}
              label={driver}
              sx={{
                backgroundColor: 'rgba(15,118,110,0.25)',
                color: '#99f6e4',
                border: '1px solid rgba(34,197,94,0.35)',
                fontWeight: 600,
              }}
            />
          ))}
        </Stack>
      )}

      <Stack direction="row" spacing={1} alignItems="center">
        <Typography variant="caption" color="text.secondary">
          ETA: {module.eta || 'TBD'}
        </Typography>
      </Stack>

      {/* Visual Preview Component */}
      {module.status === 'live' && (
        <Box sx={{ mt: 1 }}>
          {module.key === 'create' && <CreateVideoPreview />}
          {module.key === 'avatar' && <AvatarVideoPreview />}
          {module.key === 'enhance' && <EnhanceVideoPreview />}
        </Box>
      )}

      <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 'auto' }}>
        <Button
          variant="contained"
          size="small"
          startIcon={disabled ? <LockIcon /> : <LaunchIcon />}
          disabled={disabled}
          onClick={() => onNavigate(module.route)}
          sx={{
            textTransform: 'none',
            fontWeight: 700,
            boxShadow: 'none',
            background: disabled ? 'rgba(148,163,184,0.25)' : 'linear-gradient(120deg,#6366f1,#8b5cf6)',
          }}
        >
          {disabled ? 'Preview' : 'Open'}
        </Button>
        <Tooltip title="Feature details & roadmap">
          <Button
            size="small"
            variant="text"
            color="inherit"
            onClick={() => onNavigate(module.route)}
            sx={{ textTransform: 'none', color: '#c7d2fe' }}
          >
            Learn more
          </Button>
        </Tooltip>
      </Stack>
    </Paper>
  );
};
