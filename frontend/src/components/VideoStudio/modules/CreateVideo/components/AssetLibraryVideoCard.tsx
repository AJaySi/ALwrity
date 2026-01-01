import React from 'react';
import { Box, Card, CardContent, Stack, Typography, Chip } from '@mui/material';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import { motion as framerMotion } from 'framer-motion';
import { OptimizedVideo } from '../../../../ImageStudio/dashboard/utils/OptimizedVideo';
import type { ContentAsset } from '../../../../../hooks/useContentAssets';

interface AssetLibraryVideoCardProps {
  asset: ContentAsset;
  isSelected: boolean;
  onClick: () => void;
}

export const AssetLibraryVideoCard: React.FC<AssetLibraryVideoCardProps> = ({
  asset,
  isSelected,
  onClick,
}) => {
  return (
    <framerMotion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        sx={{
          cursor: 'pointer',
          border: isSelected ? '2px solid #667eea' : '1px solid #e2e8f0',
          borderRadius: 2,
          overflow: 'hidden',
          transition: 'all 0.2s',
          '&:hover': {
            boxShadow: '0 8px 24px rgba(102, 126, 234, 0.2)',
          },
        }}
        onClick={onClick}
      >
        <Box
          sx={{
            position: 'relative',
            width: '100%',
            paddingTop: '56.25%', // 16:9 aspect ratio
            backgroundColor: '#0f172a',
            overflow: 'hidden',
          }}
        >
          <OptimizedVideo
            src={asset.file_url}
            alt={asset.title || asset.filename}
            controls
            muted
            loop
            playsInline
            preload="metadata"
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
          {isSelected && (
            <Box
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                background: '#667eea',
                borderRadius: '50%',
                p: 0.5,
              }}
            >
              <PlayCircleOutlineIcon sx={{ color: '#fff', fontSize: 20 }} />
            </Box>
          )}
        </Box>
        <CardContent sx={{ p: 2 }}>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 700,
                  color: '#0f172a',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  flex: 1,
                }}
                title={asset.title || asset.filename}
              >
                {asset.title || asset.filename}
              </Typography>
              {asset.source_module && (
                <Chip
                  label={asset.source_module}
                  size="small"
                  sx={{
                    background: 'rgba(102, 126, 234, 0.1)',
                    color: '#667eea',
                    fontWeight: 600,
                    fontSize: 10,
                    ml: 1,
                  }}
                />
              )}
            </Stack>
            {asset.description && (
              <Typography
                variant="caption"
                sx={{ color: '#475569', fontSize: 11 }}
                title={asset.description}
              >
                {asset.description.length > 60
                  ? `${asset.description.substring(0, 60)}...`
                  : asset.description}
              </Typography>
            )}
            {asset.prompt && (
              <Typography
                variant="caption"
                sx={{
                  color: '#6366f1',
                  fontSize: 10,
                  fontStyle: 'italic',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
                title={asset.prompt}
              >
                "{asset.prompt.length > 50 ? `${asset.prompt.substring(0, 50)}...` : asset.prompt}"
              </Typography>
            )}
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {asset.cost > 0 && (
                <Chip
                  label={`$${asset.cost.toFixed(2)}`}
                  size="small"
                  sx={{
                    background: 'rgba(16, 185, 129, 0.1)',
                    color: '#047857',
                    fontWeight: 600,
                    fontSize: 10,
                  }}
                />
              )}
              {asset.asset_metadata?.resolution && (
                <Chip
                  label={asset.asset_metadata.resolution}
                  size="small"
                  sx={{
                    background: 'rgba(59, 130, 246, 0.1)',
                    color: '#1e40af',
                    fontWeight: 600,
                    fontSize: 10,
                  }}
                />
              )}
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </framerMotion.div>
  );
};