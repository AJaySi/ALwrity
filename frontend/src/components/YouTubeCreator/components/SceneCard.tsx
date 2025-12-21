/**
 * Scene Card Component
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
  Box,
  FormControlLabel,
  Switch,
  IconButton,
  TextField,
  Button,
  Tooltip,
  Alert,
} from '@mui/material';
import { Edit, Check, Close, Movie, Shuffle, CallMade, ArrowForward, HelpOutline, Info, RecordVoiceOver, Videocam, AutoAwesome } from '@mui/icons-material';
import { Scene } from '../../../services/youtubeApi';
import { inputSx, labelSx } from '../styles';

interface SceneCardProps {
  scene: Scene;
  isEditing: boolean;
  editedScene: Partial<Scene> | null;
  onToggle: (sceneNumber: number) => void;
  onEdit: (scene: Scene) => void;
  onSave: () => void;
  onCancel: () => void;
  onEditChange: (updates: Partial<Scene>) => void;
  loading: boolean;
}

// Helper function to get border color based on scene emphasis
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

// Helper function to get icon for scene emphasis
const getSceneIcon = (emphasisTag: string) => {
  switch (emphasisTag) {
    case 'hook':
      return <Movie fontSize="small" />;
    case 'cta':
      return <CallMade fontSize="small" />;
    case 'transition':
      return <Shuffle fontSize="small" />;
    case 'main_content':
      return <ArrowForward fontSize="small" />;
    default:
      return <ArrowForward fontSize="small" />;
  }
};

// Helper function to get color for scene emphasis
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

export const SceneCard: React.FC<SceneCardProps> = React.memo(({
  scene,
  isEditing,
  editedScene,
  onToggle,
  onEdit,
  onSave,
  onCancel,
  onEditChange,
  loading,
}) => {
  const sceneData = isEditing && editedScene ? { ...scene, ...editedScene } : scene;
  const borderColor = getSceneBorderColor(sceneData.emphasis_tags);

  return (
    <Card
      variant="outlined"
      sx={{
        opacity: sceneData.enabled === false ? 0.6 : 1,
        border: sceneData.enabled === false ? '1px dashed #e5e7eb' : `2px solid ${borderColor}`,
        borderRadius: 2,
        bgcolor: '#ffffff',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: sceneData.enabled !== false ? '0 4px 12px rgba(0, 0, 0, 0.1)' : 'none',
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header Section */}
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
                Scene {scene.scene_number}: {sceneData.title}
              </Typography>
              <Tooltip
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Scene Type: {sceneData.emphasis_tags?.[0]?.replace('_', ' ') || 'Main Content'}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                      {sceneData.emphasis_tags?.[0] === 'hook' 
                        ? 'Hook scenes capture attention in the first few seconds with compelling visuals or statements.'
                        : sceneData.emphasis_tags?.[0] === 'cta'
                        ? 'Call-to-action scenes encourage viewers to like, subscribe, or take a specific action.'
                        : sceneData.emphasis_tags?.[0] === 'transition'
                        ? 'Transition scenes smoothly connect different topics or segments.'
                        : 'Main content scenes deliver the core message and information.'}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block' }}>
                      Duration: {sceneData.duration_estimate}s • This affects rendering cost.
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
              {sceneData.emphasis_tags?.map((tag) => (
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
                    icon={getSceneIcon(tag)}
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
                  label={`~${sceneData.duration_estimate}s`}
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
                sceneData.enabled !== false
                  ? 'Disable this scene to exclude it from rendering and reduce cost'
                  : 'Enable this scene to include it in the final video'
              }
              arrow
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={sceneData.enabled !== false}
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

        {isEditing ? (
          <Stack spacing={2}>
            <TextField
              label="Narration"
              value={sceneData.narration}
              onChange={(e) => onEditChange({ narration: e.target.value })}
              multiline
              rows={3}
              fullWidth
              sx={inputSx}
              InputLabelProps={{ sx: labelSx }}
            />
            <TextField
              label="Visual Prompt"
              value={sceneData.visual_prompt}
              onChange={(e) => onEditChange({ visual_prompt: e.target.value })}
              multiline
              rows={2}
              fullWidth
              sx={inputSx}
              InputLabelProps={{ sx: labelSx }}
            />
            <TextField
              label="Duration (seconds)"
              type="number"
              value={sceneData.duration_estimate}
              onChange={(e) => onEditChange({ duration_estimate: parseFloat(e.target.value) || 5 })}
              inputProps={{ min: 1, max: 10, step: 0.5 }}
              fullWidth
              sx={inputSx}
              InputLabelProps={{ sx: labelSx }}
            />
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                size="small"
                variant="contained"
                startIcon={<Check />}
                onClick={onSave}
                disabled={loading}
              >
                Save
              </Button>
              <Button
                size="small"
                variant="outlined"
                startIcon={<Close />}
                onClick={onCancel}
              >
                Cancel
              </Button>
            </Box>
          </Stack>
        ) : (
          <Stack spacing={2.5}>
            {/* Narration Section */}
            <Box
              sx={{
                p: 2,
                bgcolor: '#f9fafb',
                borderRadius: 1.5,
                border: '1px solid #e5e7eb',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <RecordVoiceOver sx={{ color: '#6366f1', fontSize: 18 }} />
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
                  Narration
                </Typography>
                <Tooltip
                  title="The spoken text or voiceover for this scene. This is what will be narrated in the final video."
                  arrow
                >
                  <IconButton size="small" sx={{ color: '#6b7280', p: 0.25, ml: 0.5 }}>
                    <HelpOutline fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography
                variant="body1"
                sx={{
                  fontStyle: 'italic',
                  color: '#374151',
                  fontSize: '0.9375rem',
                  lineHeight: 1.7,
                  fontWeight: 400,
                  pl: 0.5,
                }}
              >
                "{sceneData.narration}"
              </Typography>
            </Box>

            {/* Visual Prompt Section */}
            <Box
              sx={{
                p: 2,
                bgcolor: '#fef3c7',
                borderRadius: 1.5,
                border: '1px solid #fde68a',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Videocam sx={{ color: '#d97706', fontSize: 18 }} />
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    color: '#92400e',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  Visual Prompt
                </Typography>
                <Tooltip
                  title={
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                        Visual Prompt Explained
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                        This describes the visual content that will be generated for this scene. The AI uses this to create appropriate images or video clips.
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block' }}>
                        <strong>Tip:</strong> More detailed prompts lead to better visual results. Include camera angles, lighting, and composition details.
                      </Typography>
                    </Box>
                  }
                  arrow
                >
                  <IconButton size="small" sx={{ color: '#d97706', p: 0.25, ml: 0.5 }}>
                    <HelpOutline fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography
                variant="body2"
                sx={{
                  color: '#78350f',
                  fontSize: '0.875rem',
                  lineHeight: 1.7,
                  pl: 0.5,
                  fontWeight: 400,
                }}
              >
                {sceneData.visual_prompt}
              </Typography>
            </Box>

            {/* Visual Cues Section */}
            {sceneData.visual_cues && sceneData.visual_cues.length > 0 && (
              <Box
                sx={{
                  p: 2,
                  bgcolor: '#f0f9ff',
                  borderRadius: 1.5,
                  border: '1px solid #bae6fd',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                  <AutoAwesome sx={{ color: '#0284c7', fontSize: 18 }} />
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      color: '#0c4a6e',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    Visual Cues
                  </Typography>
                  <Tooltip
                    title={
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                          Visual Cues Explained
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                          These are specific visual effects, camera techniques, or stylistic elements that will be applied to enhance the scene.
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block' }}>
                          Examples: Quick Zoom, Sunlight Flare, Energetic Cut, Steady Cam Walk, etc.
                        </Typography>
                      </Box>
                    }
                    arrow
                  >
                    <IconButton size="small" sx={{ color: '#0284c7', p: 0.25, ml: 0.5 }}>
                      <HelpOutline fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap>
                  {sceneData.visual_cues.map((cue, idx) => (
                    <Tooltip
                      key={`${cue}-${idx}`}
                      title={`Visual effect: ${cue}`}
                      arrow
                    >
                      <Chip
                        label={cue}
                        size="small"
                        sx={{
                          fontSize: '0.75rem',
                          height: 28,
                          textTransform: 'capitalize',
                          borderColor: '#7dd3fc',
                          bgcolor: '#ffffff',
                          color: '#0c4a6e',
                          fontWeight: 500,
                          '&:hover': {
                            bgcolor: '#e0f2fe',
                            borderColor: '#0284c7',
                          },
                        }}
                      />
                    </Tooltip>
                  ))}
                </Stack>
              </Box>
            )}

            {/* Info Alert for Editing */}
            <Alert
              severity="info"
              icon={<Info fontSize="small" />}
              sx={{
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
                <strong>Tip:</strong> Click the edit icon above to modify narration, visual prompt, or duration. 
                Disable scenes you don't need to reduce rendering cost.
              </Typography>
            </Alert>
          </Stack>
        )}
      </CardContent>
    </Card>
  );
});

SceneCard.displayName = 'SceneCard';

