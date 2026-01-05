import React from 'react';
import { Box, Typography, Paper, Stack, Chip, Divider } from '@mui/material';
import ContentCutIcon from '@mui/icons-material/ContentCut';
import SpeedIcon from '@mui/icons-material/Speed';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import TuneIcon from '@mui/icons-material/Tune';
import NoiseAwareIcon from '@mui/icons-material/NoiseAware';
import type { EditOperation } from '../hooks/useEditVideo';

interface OperationSelectorProps {
  selectedOperation: EditOperation;
  onOperationChange: (operation: EditOperation) => void;
}

interface OperationInfo {
  key: EditOperation;
  label: string;
  description: string;
  icon: React.ReactNode;
  phase: 1 | 2;
}

const operations: OperationInfo[] = [
  // Phase 1 - Video Operations
  {
    key: 'trim',
    label: 'Trim & Cut',
    description: 'Cut video to specific time range or max duration',
    icon: <ContentCutIcon />,
    phase: 1,
  },
  {
    key: 'speed',
    label: 'Speed Control',
    description: 'Slow motion (0.25x-0.5x) or fast forward (1.5x-4x)',
    icon: <SpeedIcon />,
    phase: 1,
  },
  {
    key: 'stabilize',
    label: 'Stabilize',
    description: 'Reduce camera shake with FFmpeg vidstab',
    icon: <CameraAltIcon />,
    phase: 1,
  },
  // Phase 2 - Text & Audio Operations
  {
    key: 'text',
    label: 'Text Overlay',
    description: 'Add text captions, titles, or watermarks',
    icon: <TextFieldsIcon />,
    phase: 2,
  },
  {
    key: 'volume',
    label: 'Volume Control',
    description: 'Adjust audio volume (mute, reduce, boost)',
    icon: <VolumeUpIcon />,
    phase: 2,
  },
  {
    key: 'normalize',
    label: 'Normalize Audio',
    description: 'EBU R128 loudness normalization for streaming',
    icon: <TuneIcon />,
    phase: 2,
  },
  {
    key: 'denoise',
    label: 'Noise Reduction',
    description: 'Remove background noise (AC, hum, hiss)',
    icon: <NoiseAwareIcon />,
    phase: 2,
  },
];

export const OperationSelector: React.FC<OperationSelectorProps> = ({
  selectedOperation,
  onOperationChange,
}) => {
  const phase1Ops = operations.filter((op) => op.phase === 1);
  const phase2Ops = operations.filter((op) => op.phase === 2);

  const renderOperation = (op: OperationInfo) => (
    <Box
      key={op.key}
      onClick={() => onOperationChange(op.key)}
      sx={{
        p: 1.5,
        borderRadius: 2,
        border: '2px solid',
        borderColor: selectedOperation === op.key ? '#3b82f6' : '#e2e8f0',
        backgroundColor: selectedOperation === op.key ? '#eff6ff' : '#ffffff',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: '#3b82f6',
          backgroundColor: selectedOperation === op.key ? '#eff6ff' : '#f8fafc',
        },
      }}
    >
      <Stack direction="row" spacing={1.5} alignItems="center">
        <Box
          sx={{
            p: 0.75,
            borderRadius: 1,
            backgroundColor: selectedOperation === op.key ? '#3b82f6' : '#f1f5f9',
            color: selectedOperation === op.key ? '#fff' : '#64748b',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {op.icon}
        </Box>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="body2" fontWeight={600} color="#0f172a" noWrap>
              {op.label}
            </Typography>
            <Chip
              label="Free"
              size="small"
              sx={{
                height: 16,
                fontSize: '0.6rem',
                backgroundColor: '#10b981',
                color: '#fff',
              }}
            />
          </Stack>
          <Typography variant="caption" color="text.secondary" noWrap>
            {op.description}
          </Typography>
        </Box>
      </Stack>
    </Box>
  );

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        borderRadius: 2,
        border: '1px solid #e2e8f0',
        backgroundColor: '#ffffff',
      }}
    >
      <Typography
        variant="subtitle2"
        sx={{
          mb: 1.5,
          color: '#0f172a',
          fontWeight: 700,
        }}
      >
        Edit Operation
      </Typography>

      {/* Phase 1: Video */}
      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
        Video Processing
      </Typography>
      <Stack spacing={0.75} sx={{ mb: 2 }}>
        {phase1Ops.map(renderOperation)}
      </Stack>

      <Divider sx={{ my: 1.5 }} />

      {/* Phase 2: Audio */}
      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
        Text & Audio
      </Typography>
      <Stack spacing={0.75}>
        {phase2Ops.map(renderOperation)}
      </Stack>
    </Paper>
  );
};
