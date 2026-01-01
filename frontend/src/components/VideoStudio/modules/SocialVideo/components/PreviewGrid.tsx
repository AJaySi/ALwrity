import React from 'react';
import { Grid, Box, Typography, Button, Stack, Chip, Paper, CircularProgress } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { PlatformResult } from '../hooks/useSocialVideo';

interface PreviewGridProps {
  results: PlatformResult[];
  optimizing: boolean;
  onDownload: (result: PlatformResult) => void;
  onDownloadAll: () => void;
}

const platformColors: Record<string, string> = {
  instagram: '#E4405F',
  tiktok: '#000000',
  youtube: '#FF0000',
  linkedin: '#0077B5',
  facebook: '#1877F2',
  twitter: '#1DA1F2',
};

export const PreviewGrid: React.FC<PreviewGridProps> = ({
  results,
  optimizing,
  onDownload,
  onDownloadAll,
}) => {
  if (optimizing) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <CircularProgress size={48} sx={{ mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          Optimizing videos for selected platforms...
        </Typography>
      </Box>
    );
  }

  if (results.length === 0) {
    return (
      <Box
        sx={{
          border: '2px dashed #cbd5e1',
          borderRadius: 2,
          p: 6,
          textAlign: 'center',
          backgroundColor: '#f8fafc',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Optimized videos will appear here
        </Typography>
      </Box>
    );
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
          Optimized Videos ({results.length})
        </Typography>
        {results.length > 1 && (
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={onDownloadAll}
            sx={{
              backgroundColor: '#3b82f6',
              '&:hover': {
                backgroundColor: '#2563eb',
              },
            }}
          >
            Download All
          </Button>
        )}
      </Stack>

      <Grid container spacing={3}>
        {results.map((result, index) => {
          const color = platformColors[result.platform] || '#3b82f6';
          const videoUrl = result.video_url.startsWith('http')
            ? result.video_url
            : `${window.location.origin}${result.video_url}`;

          return (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  border: `2px solid ${color}`,
                  backgroundColor: '#ffffff',
                }}
              >
                <Stack spacing={2}>
                  <Box>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, color }}>
                        {result.name}
                      </Typography>
                    </Stack>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      <Chip
                        label={result.aspect_ratio}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                      <Chip
                        label={`${result.width}x${result.height}`}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                      <Chip
                        label={formatFileSize(result.file_size)}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    </Stack>
                  </Box>

                  <Box
                    sx={{
                      borderRadius: 1,
                      overflow: 'hidden',
                      border: '1px solid #e2e8f0',
                      backgroundColor: '#000',
                      aspectRatio: result.aspect_ratio === '9:16' ? '9/16' : '16/9',
                    }}
                  >
                    <video
                      src={videoUrl}
                      controls
                      style={{
                        width: '100%',
                        height: '100%',
                        display: 'block',
                      }}
                    />
                  </Box>

                  {result.thumbnail_url && (
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
                        Thumbnail:
                      </Typography>
                      <Box
                        component="img"
                        src={
                          result.thumbnail_url.startsWith('http')
                            ? result.thumbnail_url
                            : `${window.location.origin}${result.thumbnail_url}`
                        }
                        alt={`${result.name} thumbnail`}
                        sx={{
                          width: '100%',
                          borderRadius: 1,
                          border: '1px solid #e2e8f0',
                        }}
                      />
                    </Box>
                  )}

                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<DownloadIcon />}
                    onClick={() => onDownload(result)}
                    href={videoUrl}
                    download
                    sx={{
                      borderColor: color,
                      color: color,
                      '&:hover': {
                        borderColor: color,
                        backgroundColor: `${color}08`,
                      },
                    }}
                  >
                    Download
                  </Button>
                </Stack>
              </Paper>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};
