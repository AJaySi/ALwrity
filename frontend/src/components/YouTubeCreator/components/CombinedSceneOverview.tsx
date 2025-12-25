/**
 * Combined Scene Overview Component
 * 
 * Displays scene statistics and timeline in a compact, combined view.
 */

import React, { useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Box,
  Grid,
  Chip,
  Divider,
  Tooltip,
  IconButton,
  Alert,
} from '@mui/material';
import { HelpOutline, Timeline, BarChart, AccessTime, Movie, Info, Image as ImageIcon, VolumeUp, CheckCircle } from '@mui/icons-material';
import { Scene } from '../../../services/youtubeApi';
import { getSceneIcon, getSceneColor, getSceneTypeLabel, formatDuration } from '../utils/sceneHelpers';

interface CombinedSceneOverviewProps {
  scenes: Scene[];
}

export const CombinedSceneOverview: React.FC<CombinedSceneOverviewProps> = React.memo(({ scenes }) => {
  const stats = useMemo(() => {
    const enabledScenes = scenes.filter(s => s.enabled !== false);
    const totalDuration = enabledScenes.reduce((sum, scene) => sum + scene.duration_estimate, 0);
    const averageDuration = enabledScenes.length > 0
      ? Math.round((totalDuration / enabledScenes.length) * 10) / 10
      : 0;

    const sceneBreakdown = enabledScenes.reduce((acc, scene) => {
      const type = scene.emphasis_tags?.[0] || 'main_content';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Asset readiness stats
    const scenesWithImages = enabledScenes.filter(s => s.imageUrl).length;
    const scenesWithAudio = enabledScenes.filter(s => s.audioUrl).length;
    const scenesWithBoth = enabledScenes.filter(s => s.imageUrl && s.audioUrl).length;
    const allReady = enabledScenes.length > 0 && scenesWithBoth === enabledScenes.length;

    return {
      totalScenes: scenes.length,
      enabledScenes: enabledScenes.length,
      totalDuration,
      averageDuration,
      sceneBreakdown,
      enabledScenesList: enabledScenes,
      scenesWithImages,
      scenesWithAudio,
      scenesWithBoth,
      allReady,
    };
  }, [scenes]);

  return (
    <Card
      elevation={0}
      sx={{
        border: '2px solid #e5e7eb',
        borderRadius: 2,
        bgcolor: '#ffffff',
        mb: 3,
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        {/* Header with Help Icon */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Timeline sx={{ color: '#6366f1', fontSize: 20 }} />
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                fontSize: '1rem',
                color: '#111827',
                letterSpacing: '-0.01em',
              }}
            >
              Scene Overview
            </Typography>
          </Box>
          <Tooltip
            title={
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                  Scene Overview Explained
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                  <strong>Statistics:</strong> Shows total scenes, duration, and breakdown by type (Hook, Content, CTA).
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                  <strong>Sequence:</strong> Visual timeline showing scene order and flow. Hover over scenes for details.
                </Typography>
                <Typography variant="caption" sx={{ display: 'block' }}>
                  <strong>Tip:</strong> Disable scenes you don't want to render to reduce cost and processing time.
                </Typography>
              </Box>
            }
            arrow
            placement="left"
          >
            <IconButton size="small" sx={{ color: '#6b7280' }}>
              <HelpOutline fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        <Grid container spacing={2}>
          {/* Left Column: Statistics */}
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                p: 2,
                bgcolor: '#f9fafb',
                borderRadius: 1.5,
                border: '1px solid #e5e7eb',
                height: '100%',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                <BarChart sx={{ color: '#6366f1', fontSize: 18 }} />
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    color: '#111827',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  Statistics
                </Typography>
              </Box>

              <Stack spacing={1.5}>
                {/* Main Stats Row */}
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Tooltip
                    title="Total number of scenes generated. You can enable/disable individual scenes below."
                    arrow
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                      <Movie sx={{ color: '#6b7280', fontSize: 16 }} />
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color: '#111827',
                          fontSize: '0.875rem',
                        }}
                      >
                        <strong>{stats.enabledScenes}</strong>/{stats.totalScenes} scenes
                      </Typography>
                    </Box>
                  </Tooltip>

                  <Tooltip
                    title="Total video duration when all enabled scenes are rendered. This affects rendering cost."
                    arrow
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                      <AccessTime sx={{ color: '#6b7280', fontSize: 16 }} />
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color: '#111827',
                          fontSize: '0.875rem',
                        }}
                      >
                        <strong>{formatDuration(stats.totalDuration)}</strong> total
                      </Typography>
                    </Box>
                  </Tooltip>

                  <Tooltip
                    title="Average duration per scene. Helps estimate pacing and engagement."
                    arrow
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#6b7280',
                        fontSize: '0.875rem',
                      }}
                    >
                      Avg: <strong>{stats.averageDuration}s</strong>
                    </Typography>
                  </Tooltip>
                </Box>

                <Divider sx={{ my: 0.5 }} />

                {/* Asset Readiness */}
                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      color: '#6b7280',
                      fontSize: '0.75rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      display: 'block',
                      mb: 1,
                    }}
                  >
                    Asset Status
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    <Tooltip
                      title="Number of scenes with AI-generated images ready"
                      arrow
                    >
                      <Chip
                        icon={<ImageIcon sx={{ fontSize: 14 }} />}
                        label={`${stats.scenesWithImages}/${stats.enabledScenes} Images`}
                        size="small"
                        sx={{
                          fontWeight: 500,
                          fontSize: '0.75rem',
                          bgcolor: stats.scenesWithImages === stats.enabledScenes ? '#d1fae5' : '#fef3c7',
                          color: stats.scenesWithImages === stats.enabledScenes ? '#065f46' : '#92400e',
                          border: `1px solid ${stats.scenesWithImages === stats.enabledScenes ? '#10b981' : '#f59e0b'}`,
                        }}
                      />
                    </Tooltip>
                    <Tooltip
                      title="Number of scenes with audio narration ready"
                      arrow
                    >
                      <Chip
                        icon={<VolumeUp sx={{ fontSize: 14 }} />}
                        label={`${stats.scenesWithAudio}/${stats.enabledScenes} Audio`}
                        size="small"
                        sx={{
                          fontWeight: 500,
                          fontSize: '0.75rem',
                          bgcolor: stats.scenesWithAudio === stats.enabledScenes ? '#d1fae5' : '#fef3c7',
                          color: stats.scenesWithAudio === stats.enabledScenes ? '#065f46' : '#92400e',
                          border: `1px solid ${stats.scenesWithAudio === stats.enabledScenes ? '#10b981' : '#f59e0b'}`,
                        }}
                      />
                    </Tooltip>
                    {stats.allReady && (
                      <Tooltip
                        title="All scenes are ready for video generation!"
                        arrow
                      >
                        <Chip
                          icon={<CheckCircle sx={{ fontSize: 14 }} />}
                          label="All Ready"
                          size="small"
                          color="success"
                          sx={{
                            fontWeight: 600,
                            fontSize: '0.75rem',
                          }}
                        />
                      </Tooltip>
                    )}
                  </Stack>
                </Box>

                <Divider sx={{ my: 0.5 }} />

                {/* Scene Type Breakdown */}
                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      color: '#6b7280',
                      fontSize: '0.75rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      display: 'block',
                      mb: 1,
                    }}
                  >
                    Breakdown by Type
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {Object.entries(stats.sceneBreakdown).map(([type, count]) => (
                      <Tooltip
                        key={type}
                        title={
                          type === 'hook'
                            ? 'Hook scenes grab attention in the first few seconds'
                            : type === 'cta'
                            ? 'Call-to-action scenes encourage viewer engagement'
                            : type === 'transition'
                            ? 'Transition scenes connect different topics smoothly'
                            : 'Main content scenes deliver the core message'
                        }
                        arrow
                      >
                        <Chip
                          label={`${getSceneTypeLabel(type)}: ${count}`}
                          size="small"
                          sx={{
                            fontWeight: 500,
                            fontSize: '0.75rem',
                            bgcolor: type === 'hook' ? '#eff6ff' : type === 'cta' ? '#f5f3ff' : '#f9fafb',
                            color: type === 'hook' ? '#1e40af' : type === 'cta' ? '#6b21a8' : '#374151',
                            border: `1px solid ${getSceneColor(type)}`,
                            '& .MuiChip-label': {
                              px: 1,
                            },
                          }}
                        />
                      </Tooltip>
                    ))}
                  </Stack>
                </Box>
              </Stack>
            </Box>
          </Grid>

          {/* Right Column: Timeline */}
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                p: 2,
                bgcolor: '#f9fafb',
                borderRadius: 1.5,
                border: '1px solid #e5e7eb',
                height: '100%',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                <AccessTime sx={{ color: '#6366f1', fontSize: 18 }} />
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    color: '#111827',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  Sequence
                </Typography>
              </Box>

              {/* Compact Timeline */}
              <Box sx={{ mb: 1.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap' }}>
                  {stats.enabledScenesList.map((scene, index) => (
                    <React.Fragment key={scene.scene_number}>
                      <Tooltip
                        title={
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                              Scene {scene.scene_number}: {scene.title}
                            </Typography>
                            <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                              {scene.narration?.substring(0, 80)}...
                            </Typography>
                            <Typography variant="caption" sx={{ display: 'block' }}>
                              Duration: {scene.duration_estimate}s • Type: {getSceneTypeLabel(scene.emphasis_tags?.[0] || 'main_content')}
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
                            minWidth: 60,
                            p: 0.75,
                            borderRadius: 1,
                            border: `2px solid ${getSceneColor(scene.emphasis_tags?.[0] || 'main_content')}`,
                            bgcolor: 'white',
                            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
                            transition: 'all 0.2s ease-in-out',
                            cursor: 'pointer',
                            '&:hover': {
                              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
                              transform: 'translateY(-1px)',
                            },
                          }}
                        >
                          {getSceneIcon(scene.emphasis_tags?.[0] || 'main_content')}
                          <Typography
                            variant="caption"
                            sx={{
                              fontWeight: 700,
                              fontSize: '0.7rem',
                              mt: 0.25,
                              color: '#111827',
                            }}
                          >
                            {scene.scene_number}
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              fontSize: '0.65rem',
                              color: '#6b7280',
                            }}
                          >
                            {scene.duration_estimate}s
                          </Typography>
                        </Box>
                      </Tooltip>

                      {index < stats.enabledScenesList.length - 1 && (
                        <Box
                          sx={{
                            width: 16,
                            height: 1,
                            bgcolor: '#d1d5db',
                            position: 'relative',
                            mx: 0.25,
                            '&::after': {
                              content: '""',
                              position: 'absolute',
                              right: -3,
                              top: -1.5,
                              width: 0,
                              height: 0,
                              borderLeft: '3px solid #d1d5db',
                              borderTop: '2px solid transparent',
                              borderBottom: '2px solid transparent',
                            },
                          }}
                        />
                      )}
                    </React.Fragment>
                  ))}
                </Box>
              </Box>

              {/* Legend */}
              <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap', mt: 1.5, pt: 1.5, borderTop: '1px solid #e5e7eb' }}>
                <Typography
                  variant="caption"
                  sx={{
                    color: '#6b7280',
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    mr: 0.5,
                  }}
                >
                  Legend:
                </Typography>
                {['hook', 'main_content', 'cta'].map((type) => (
                  <Tooltip
                    key={type}
                    title={
                      type === 'hook'
                        ? 'Hook scenes capture attention immediately'
                        : type === 'cta'
                        ? 'CTA scenes drive viewer action'
                        : 'Main content delivers your message'
                    }
                    arrow
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: getSceneColor(type),
                        }}
                      />
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#6b7280',
                          fontSize: '0.75rem',
                        }}
                      >
                        {getSceneTypeLabel(type)}
                      </Typography>
                    </Box>
                  </Tooltip>
                ))}
              </Box>
            </Box>
          </Grid>
        </Grid>

        {/* Info Alert */}
        <Alert
          severity="info"
          icon={<Info fontSize="small" />}
          sx={{
            mt: 2,
            bgcolor: '#eff6ff',
            border: '1px solid #bfdbfe',
            '& .MuiAlert-icon': {
              color: '#3b82f6',
            },
            '& .MuiAlert-message': {
              color: '#1e40af',
            },
          }}
        >
          <Typography variant="caption" sx={{ fontSize: '0.75rem', lineHeight: 1.5 }}>
            <strong>Tip:</strong> Review scene details below to edit narration, visual prompts, or disable scenes you don't need. 
            This helps optimize cost and video quality.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
});

CombinedSceneOverview.displayName = 'CombinedSceneOverview';

