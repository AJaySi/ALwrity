import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Divider,
  IconButton,
  Stack,
  Typography,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { FaceSwapResult } from '../../hooks/useImageStudio';

interface FaceSwapResultViewerProps {
  baseImage?: string | null;
  faceImage?: string | null;
  result?: FaceSwapResult | null;
  isProcessing?: boolean;
  onReset?: () => void;
}

export const FaceSwapResultViewer: React.FC<FaceSwapResultViewerProps> = ({
  baseImage,
  faceImage,
  result,
  isProcessing,
  onReset,
}) => {
  const handleDownload = () => {
    if (!result?.image_base64) return;
    const link = document.createElement('a');
    link.href = result.image_base64;
    link.download = `face-swap-${result.model}-${Date.now()}.png`;
    link.click();
  };

  if (!baseImage || !faceImage) {
    return (
      <Card
        sx={{
          borderRadius: 3,
          borderStyle: 'dashed',
          borderColor: 'rgba(255,255,255,0.1)',
          minHeight: 280,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(255,255,255,0.02)',
        }}
      >
        <Typography variant="body1" color="text.secondary">
          Upload both images to preview face swap.
        </Typography>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        borderRadius: 3,
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight={700}>
            Results
          </Typography>
          <Stack direction="row" spacing={1}>
            <Tooltip title="Reset">
              <span>
                <IconButton disabled={!result && !baseImage} onClick={onReset}>
                  <RestartAltIcon />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="Download result">
              <span>
                <IconButton disabled={!result} onClick={handleDownload}>
                  <DownloadIcon />
                </IconButton>
              </span>
            </Tooltip>
          </Stack>
        </Stack>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          {/* Base Image */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block" mb={1}>
              Base Image
            </Typography>
            <Box
              sx={{
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              <img
                src={baseImage}
                alt="Base image"
                style={{ width: '100%', display: 'block', maxHeight: 300, objectFit: 'contain' }}
              />
            </Box>
          </Box>

          {/* Face Image */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block" mb={1}>
              Face Image
            </Typography>
            <Box
              sx={{
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              <img
                src={faceImage}
                alt="Face image"
                style={{ width: '100%', display: 'block', maxHeight: 300, objectFit: 'contain' }}
              />
            </Box>
          </Box>

          {/* Result */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block" mb={1}>
              Swapped Result
            </Typography>
            <Box
              sx={{
                borderRadius: 2,
                minHeight: 180,
                border: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
                position: 'relative',
                background: 'rgba(255,255,255,0.02)',
              }}
            >
              {isProcessing && (
                <Stack alignItems="center" spacing={1} py={6}>
                  <CircularProgress />
                  <Typography variant="body2" color="text.secondary">
                    Swapping faces...
                  </Typography>
                </Stack>
              )}
              {!isProcessing && result?.image_base64 && (
                <img
                  src={result.image_base64}
                  alt="Face swap result"
                  style={{ width: '100%', display: 'block', maxHeight: 300, objectFit: 'contain' }}
                />
              )}
              {!isProcessing && !result && (
                <Typography variant="body2" color="text.secondary">
                  No result yet. Select a model and swap.
                </Typography>
              )}
            </Box>
          </Box>
        </Stack>

        {result && (
          <>
            <Divider sx={{ my: 2 }} />
            <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
              <ChipLabel label="Model" value={result.model} />
              <ChipLabel label="Provider" value={result.provider} />
              <ChipLabel label="Resolution" value={`${result.width}×${result.height}`} />
            </Stack>
          </>
        )}
      </CardContent>
    </Card>
  );
};

const ChipLabel: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <Box
    sx={{
      borderRadius: 2,
      background: 'rgba(255,255,255,0.08)',
      px: 2,
      py: 1,
      minWidth: 140,
    }}
  >
    <Typography variant="caption" color="text.secondary">
      {label}
    </Typography>
    <Typography variant="body2" fontWeight={600}>
      {value}
    </Typography>
  </Box>
);
