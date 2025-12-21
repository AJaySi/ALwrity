/**
 * Scene Timeline Component
 *
 * Displays a horizontal timeline/flow view of all scenes showing
 * sequence, duration, and scene types in a visual format.
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Stack,
  Chip,
  Tooltip,
} from '@mui/material';
import { AccessTime } from '@mui/icons-material';
import { Scene } from '../../../services/youtubeApi';
import { getSceneIcon, getSceneColor, getSceneTypeLabel, formatDuration } from '../utils/sceneHelpers';

interface SceneTimelineProps {
  scenes: Scene[];
}

export const SceneTimeline: React.FC<SceneTimelineProps> = React.memo(({
  scenes,
}) => {
  const enabledScenes = scenes.filter(s => s.enabled !== false);

  if (enabledScenes.length === 0) {
    return null;
  }

  // Calculate total duration
  const totalDuration = enabledScenes.reduce((sum, scene) => sum + scene.duration_estimate, 0);

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
          <AccessTime sx={{ color: 'primary.main', fontSize: 20 }} />
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              fontSize: '1.125rem',
              letterSpacing: '-0.01em',
            }}
          >
            Scene Sequence
          </Typography>
        </Box>

        {/* Timeline Visualization */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            {enabledScenes.map((scene, index) => (
              <React.Fragment key={scene.scene_number}>
                {/* Scene Node */}
                <Tooltip
                  title={
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        Scene {scene.scene_number}: {scene.title}
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block' }}>
                        {scene.narration?.substring(0, 100)}...
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                        Duration: {scene.duration_estimate}s
                      </Typography>
                    </Box>
                  }
                  arrow
                  placement="top"
                >
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      minWidth: 80,
                      p: 1,
                      borderRadius: 1,
                      border: `2px solid ${getSceneColor(scene.emphasis_tags?.[0] || 'main_content')}`,
                      bgcolor: 'white',
                      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                        transform: 'translateY(-1px)',
                      },
                    }}
                  >
                    {getSceneIcon(scene.emphasis_tags?.[0] || 'main_content', 'medium')}
                    <Typography
                      variant="caption"
                      sx={{
                        fontWeight: 600,
                        fontSize: '0.7rem',
                        mt: 0.5,
                        color: 'text.primary',
                      }}
                    >
                      {scene.scene_number}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        fontSize: '0.65rem',
                        color: 'text.secondary',
                        textAlign: 'center',
                      }}
                    >
                      {scene.duration_estimate}s
                    </Typography>
                  </Box>
                </Tooltip>

                {/* Arrow between scenes */}
                {index < enabledScenes.length - 1 && (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      px: 1,
                    }}
                  >
                    <Box
                      sx={{
                        width: 20,
                        height: 1,
                        bgcolor: '#d1d5db',
                        position: 'relative',
                        '&::after': {
                          content: '""',
                          position: 'absolute',
                          right: -4,
                          top: -2,
                          width: 0,
                          height: 0,
                          borderLeft: '4px solid #d1d5db',
                          borderTop: '2px solid transparent',
                          borderBottom: '2px solid transparent',
                        },
                      }}
                    />
                  </Box>
                )}
              </React.Fragment>
            ))}
          </Box>

          {/* Timeline Summary */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Chip
                label={`Total: ${formatDuration(totalDuration)}`}
                size="small"
                sx={{ fontWeight: 500 }}
              />
              <Chip
                label={`${enabledScenes.length} scenes`}
                size="small"
                variant="outlined"
              />
              <Chip
                label={`Avg: ${Math.round((totalDuration / enabledScenes.length) * 10) / 10}s`}
                size="small"
                variant="outlined"
              />
            </Stack>

            <Stack direction="row" spacing={1}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#3b82f6' }} />
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Hook
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#6b7280' }} />
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Content
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#8b5cf6' }} />
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  CTA
                </Typography>
              </Box>
            </Stack>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
});

SceneTimeline.displayName = 'SceneTimeline';

