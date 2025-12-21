/**
 * Scene Statistics Card Component
 *
 * Displays summary statistics about generated scenes including
 * total count, duration, and breakdown by scene type.
 */

import React, { useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Box,
  Chip,
  Divider,
} from '@mui/material';
import { AccessTime, Movie, Timeline } from '@mui/icons-material';
import { Scene } from '../../../services/youtubeApi';

interface SceneStatisticsCardProps {
  scenes: Scene[];
}

export const SceneStatisticsCard: React.FC<SceneStatisticsCardProps> = React.memo(({
  scenes,
}) => {
  const stats = useMemo(() => {
    const totalScenes = scenes.length;
    const enabledScenes = scenes.filter(s => s.enabled !== false);
    const totalDuration = enabledScenes.reduce((sum, scene) => sum + scene.duration_estimate, 0);

    // Group scenes by emphasis type
    const sceneBreakdown = scenes.reduce((acc, scene) => {
      const type = scene.emphasis_tags?.[0] || 'main_content';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Calculate enabled scene breakdown
    const enabledBreakdown = enabledScenes.reduce((acc, scene) => {
      const type = scene.emphasis_tags?.[0] || 'main_content';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const averageDuration = enabledScenes.length > 0
      ? Math.round((totalDuration / enabledScenes.length) * 10) / 10
      : 0;

    return {
      totalScenes,
      enabledScenes: enabledScenes.length,
      totalDuration,
      sceneBreakdown,
      enabledBreakdown,
      averageDuration,
    };
  }, [scenes]);

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getSceneTypeLabel = (type: string): string => {
    switch (type) {
      case 'hook': return 'Hook';
      case 'cta': return 'CTA';
      case 'transition': return 'Transition';
      case 'main_content': return 'Main Content';
      default: return type.charAt(0).toUpperCase() + type.slice(1);
    }
  };

  const getSceneTypeColor = (type: string): 'primary' | 'secondary' | 'default' => {
    switch (type) {
      case 'hook': return 'primary';
      case 'cta': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <Card
      elevation={0}
      sx={{
        border: '1px solid #e5e7eb',
        borderRadius: 2,
        bgcolor: '#ffffff',
        mb: 3,
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        },
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Timeline sx={{ color: 'primary.main', fontSize: 20 }} />
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              fontSize: '1.125rem',
              letterSpacing: '-0.01em',
            }}
          >
            Scene Statistics
          </Typography>
        </Box>

        <Stack spacing={2}>
          {/* Main Statistics Row */}
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Movie sx={{ color: 'text.secondary', fontSize: 18 }} />
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                {stats.enabledScenes} of {stats.totalScenes} scenes enabled
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AccessTime sx={{ color: 'text.secondary', fontSize: 18 }} />
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                Total: {formatDuration(stats.totalDuration)}
              </Typography>
            </Box>

            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Average: {stats.averageDuration}s per scene
            </Typography>
          </Box>

          {/* Scene Type Breakdown */}
          <Divider sx={{ my: 1 }} />

          <Box>
            <Typography
              variant="body2"
              sx={{
                fontWeight: 600,
                color: 'text.primary',
                mb: 1.5,
                fontSize: '0.875rem',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Scene Breakdown
            </Typography>

            <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap>
              {Object.entries(stats.enabledBreakdown).map(([type, count]) => (
                <Chip
                  key={type}
                  label={`${getSceneTypeLabel(type)}: ${count}`}
                  size="small"
                  color={getSceneTypeColor(type)}
                  variant="outlined"
                  sx={{
                    fontWeight: 500,
                    '& .MuiChip-label': {
                      px: 1.5,
                    },
                  }}
                />
              ))}
            </Stack>

            {stats.enabledScenes !== stats.totalScenes && (
              <Typography
                variant="caption"
                sx={{
                  color: 'text.secondary',
                  mt: 1,
                  display: 'block',
                }}
              >
                {stats.totalScenes - stats.enabledScenes} scene{stats.totalScenes - stats.enabledScenes !== 1 ? 's' : ''} disabled
              </Typography>
            )}
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
});

SceneStatisticsCard.displayName = 'SceneStatisticsCard';

