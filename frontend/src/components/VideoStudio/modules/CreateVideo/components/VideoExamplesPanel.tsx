import React from 'react';
import {
  Box,
  Paper,
  Stack,
  Typography,
  Divider,
  Grid,
  Chip,
} from '@mui/material';
import MovieCreationIcon from '@mui/icons-material/MovieCreation';
import type { ExampleVideo } from '../types';
import type { ContentAsset } from '../../../../../hooks/useContentAssets';
import { ExampleVideoCard } from './ExampleVideoCard';
import { AssetLibraryVideoCard } from './AssetLibraryVideoCard';

interface VideoExamplesPanelProps {
  examples: ExampleVideo[];
  libraryVideos: ContentAsset[];
  loadingLibraryVideos: boolean;
  selectedExample: number | null;
  selectedAssetId: number | null;
  prompt: string;
  onExampleClick: (index: number) => void;
  onAssetClick: (asset: ContentAsset) => void;
}

export const VideoExamplesPanel: React.FC<VideoExamplesPanelProps> = ({
  examples,
  libraryVideos,
  loadingLibraryVideos,
  selectedExample,
  selectedAssetId,
  prompt,
  onExampleClick,
  onAssetClick,
}) => {
  return (
    <Paper
      elevation={0}
      sx={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        borderRadius: 3,
        p: 3,
        minHeight: 600,
      }}
    >
      <Typography
        variant="h6"
        sx={{
          fontWeight: 700,
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          color: '#0f172a',
        }}
      >
        <MovieCreationIcon sx={{ color: '#667eea' }} />
        Video Examples & Preview
      </Typography>

      {/* Example Videos */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#0f172a' }}>
          Example Videos
        </Typography>
        <Grid container spacing={2}>
          {examples.map((example, index) => (
            <Grid item xs={12} sm={6} key={example.id}>
              <ExampleVideoCard
                example={example}
                index={index}
                isSelected={selectedExample === index}
                onClick={() => onExampleClick(index)}
              />
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Asset Library Videos */}
      {libraryVideos.length > 0 && (
        <>
          <Divider sx={{ my: 3, borderColor: 'rgba(0,0,0,0.1)' }} />
          <Box sx={{ mb: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#0f172a' }}>
                Your Videos from Asset Library
              </Typography>
              <Chip
                label={`${libraryVideos.length} video${libraryVideos.length !== 1 ? 's' : ''}`}
                size="small"
                sx={{
                  background: 'rgba(102, 126, 234, 0.1)',
                  color: '#667eea',
                  fontWeight: 600,
                }}
              />
            </Stack>
            {loadingLibraryVideos ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" sx={{ color: '#475569' }}>
                  Loading your videos...
                </Typography>
              </Box>
            ) : (
              <Grid container spacing={2}>
                {libraryVideos.map((asset) => (
                  <Grid item xs={12} sm={6} key={asset.id}>
                    <AssetLibraryVideoCard
                      asset={asset}
                      isSelected={selectedAssetId === asset.id}
                      onClick={() => onAssetClick(asset)}
                    />
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        </>
      )}

      <Divider sx={{ my: 3, borderColor: 'rgba(0,0,0,0.1)' }} />

      {/* Empty State / Preview Area */}
      {!prompt && (
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
            px: 3,
          }}
        >
          <Box
            sx={{
              width: 120,
              height: 120,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea20, #764ba220)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 3,
            }}
          >
            <MovieCreationIcon sx={{ fontSize: 60, color: '#667eea' }} />
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, color: '#0f172a' }}>
            No Video Yet
          </Typography>
          <Typography variant="body2" sx={{ color: '#475569', mb: 3 }}>
            Enter a prompt and click "Create Video" to generate your video, or click an example above to see what's possible
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
            {['Instagram Reel', 'TikTok Video', 'YouTube Short', 'LinkedIn Post'].map((tag) => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                sx={{
                  background: 'rgba(102, 126, 234, 0.1)',
                  color: '#667eea',
                  fontWeight: 600,
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Generated Video Preview (when available) */}
      {prompt && (
        <Box
          sx={{
            textAlign: 'center',
            py: 4,
            px: 3,
            background: 'rgba(102, 126, 234, 0.05)',
            borderRadius: 2,
            border: '2px dashed rgba(102, 126, 234, 0.3)',
          }}
        >
          <Typography variant="body1" sx={{ fontWeight: 600, mb: 2, color: '#0f172a' }}>
            Your video will appear here
          </Typography>
          <Typography variant="body2" sx={{ color: '#475569' }}>
            Click "Create Video" to generate your video based on your prompt and settings
          </Typography>
        </Box>
      )}
    </Paper>
  );
};
