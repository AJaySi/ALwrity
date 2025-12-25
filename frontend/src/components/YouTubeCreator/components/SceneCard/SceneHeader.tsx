import React from 'react';
import {
  Typography,
  Stack,
  Chip,
  Box,
  FormControlLabel,
  Switch,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Edit, HelpOutline } from '@mui/icons-material';
import { Scene } from '../../../../services/youtubeApi';

// Helper functions
const getSceneBorderColor = (emphasisTags?: string[]): string => {
  if (!emphasisTags || emphasisTags.length === 0) return '#e5e7eb'; // Default gray

  const primaryTag = emphasisTags[0];
  switch (primaryTag) {
    case 'hook':
      return '#3b82f6'; // Blue for hook
    case 'cta':
      return '#8b5cf6'; // Purple for CTA
    case 'transition':
      return '#10b981'; // Green for transition
    case 'main_content':
    default:
      return '#e5e7eb'; // Gray for main content
  }
};

const getSceneIcon = (emphasisTag: string) => {
  switch (emphasisTag) {
    case 'hook':
      return '🎬'; // Movie icon
    case 'cta':
      return '📣'; // Call made icon
    case 'transition':
      return '🔄'; // Shuffle icon
    case 'main_content':
    default:
      return '➡️'; // Arrow forward icon
  }
};

const getSceneChipColor = (emphasisTag: string): 'primary' | 'secondary' | 'default' => {
  switch (emphasisTag) {
    case 'hook':
      return 'primary';
    case 'cta':
      return 'secondary';
    default:
      return 'default';
  }
};

interface SceneHeaderProps {
  scene: Scene;
  isEditing: boolean;
  onToggle: (sceneNumber: number) => void;
  onEdit: (scene: Scene) => void;
}

export const SceneHeader: React.FC<SceneHeaderProps> = ({
  scene,
  isEditing,
  onToggle,
  onEdit,
}) => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2.5 }}>
      <Box sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
          <Typography
            variant="h6"
            sx={{
              mb: 0,
              fontWeight: 700,
              fontSize: '1.125rem',
              color: '#111827',
              letterSpacing: '-0.01em',
            }}
          >
            Scene {scene.scene_number}: {scene.title}
          </Typography>
          <Tooltip
            title={
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                  Scene Type: {scene.emphasis_tags?.[0]?.replace('_', ' ') || 'Main Content'}
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                  {scene.emphasis_tags?.[0] === 'hook'
                    ? 'Hook scenes capture attention in the first few seconds with compelling visuals or statements.'
                    : scene.emphasis_tags?.[0] === 'cta'
                    ? 'Call-to-action scenes encourage viewers to like, subscribe, or take a specific action.'
                    : scene.emphasis_tags?.[0] === 'transition'
                    ? 'Transition scenes smoothly connect different topics or segments.'
                    : 'Main content scenes deliver the core message and information.'}
                </Typography>
                <Typography variant="caption" sx={{ display: 'block' }}>
                  Duration: {scene.duration_estimate}s • This affects rendering cost.
                </Typography>
              </Box>
            }
            arrow
            placement="top"
          >
            <IconButton size="small" sx={{ color: '#6b7280', p: 0.5 }}>
              <HelpOutline fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Stack direction="row" spacing={1} sx={{ mb: 0 }} flexWrap="wrap" useFlexGap>
          {scene.emphasis_tags?.map((tag) => (
            <Tooltip
              key={tag}
              title={
                tag === 'hook'
                  ? 'Hook: Grabs viewer attention immediately'
                  : tag === 'cta'
                  ? 'CTA: Encourages viewer action'
                  : tag === 'transition'
                  ? 'Transition: Connects segments smoothly'
                  : 'Main Content: Core message delivery'
              }
              arrow
            >
              <Chip
                label={tag.replace('_', ' ')}
                size="small"
                color={getSceneChipColor(tag)}
                icon={<span>{getSceneIcon(tag)}</span>}
                sx={{
                  textTransform: 'capitalize',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                }}
              />
            </Tooltip>
          ))}
          <Tooltip
            title="Estimated duration in seconds. Longer scenes cost more to render but provide more detail."
            arrow
          >
            <Chip
              label={`~${scene.duration_estimate}s`}
              size="small"
              variant="outlined"
              sx={{
                ml: 'auto',
                fontWeight: 600,
                fontSize: '0.75rem',
                borderColor: '#d1d5db',
                color: '#374151',
              }}
            />
          </Tooltip>
        </Stack>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip
          title={
            scene.enabled !== false
              ? 'Disable this scene to exclude it from rendering and reduce cost'
              : 'Enable this scene to include it in the final video'
          }
          arrow
        >
          <FormControlLabel
            control={
              <Switch
                checked={scene.enabled !== false}
                onChange={() => onToggle(scene.scene_number)}
                size="small"
              />
            }
            label="Enable"
            sx={{ mr: 0 }}
          />
        </Tooltip>
        {!isEditing && (
          <Tooltip title="Edit scene narration, visual prompt, or duration" arrow>
            <IconButton
              size="small"
              onClick={() => onEdit(scene)}
              color="primary"
              sx={{
                border: '1px solid #e5e7eb',
                '&:hover': {
                  bgcolor: '#f9fafb',
                },
              }}
            >
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    </Box>
  );
};
