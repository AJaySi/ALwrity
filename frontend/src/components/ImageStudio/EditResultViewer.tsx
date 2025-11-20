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
import { EditResult } from '../../hooks/useImageStudio';

interface EditResultViewerProps {
  originalImage?: string | null;
  result?: EditResult | null;
  isProcessing?: boolean;
  onReset?: () => void;
}

export const EditResultViewer: React.FC<EditResultViewerProps> = ({
  originalImage,
  result,
  isProcessing,
  onReset,
}) => {
  const handleDownload = () => {
    if (!result?.image_base64) return;
    const link = document.createElement('a');
    link.href = result.image_base64;
    link.download = `edit-${result.operation}-${Date.now()}.png`;
    link.click();
  };

  if (!originalImage) {
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
          Upload an image to preview edits.
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
                <IconButton disabled={!result && !originalImage} onClick={onReset}>
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
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Original
            </Typography>
            <Box
              sx={{
                mt: 1,
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              <img
                src={originalImage}
                alt="Original reference"
                style={{ width: '100%', display: 'block' }}
              />
            </Box>
          </Box>

          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Edited
            </Typography>
            <Box
              sx={{
                mt: 1,
                borderRadius: 2,
                minHeight: 180,
                border: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              {isProcessing && (
                <Stack alignItems="center" spacing={1} py={6}>
                  <CircularProgress />
                  <Typography variant="body2" color="text.secondary">
                    Applying edits...
                  </Typography>
                </Stack>
              )}
              {!isProcessing && result?.image_base64 && (
                <img
                  src={result.image_base64}
                  alt="Edited result"
                  style={{ width: '100%', display: 'block' }}
                />
              )}
              {!isProcessing && !result && (
                <Typography variant="body2" color="text.secondary">
                  No edits yet. Configure options and apply.
                </Typography>
              )}
            </Box>
          </Box>
        </Stack>

        {result && (
          <>
            <Divider sx={{ my: 2 }} />
            <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
              <ChipLabel label="Operation" value={result.operation} />
              <ChipLabel label="Provider" value={result.provider} />
              <ChipLabel label="Resolution" value={`${result.width}×${result.height}`} />
              {result.metadata?.style_preset && (
                <ChipLabel label="Style" value={result.metadata.style_preset} />
              )}
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


