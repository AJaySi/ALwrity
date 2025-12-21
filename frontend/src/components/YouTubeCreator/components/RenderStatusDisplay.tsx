/**
 * Render Status Display Component
 * 
 * Displays render progress, completion status, errors, and video preview.
 */

import React from 'react';
import {
  Stack,
  Box,
  Typography,
  Alert,
  LinearProgress,
  Button,
} from '@mui/material';
import { Download, Refresh } from '@mui/icons-material';
import { TaskStatus } from '../../../services/youtubeApi';

interface RenderStatusDisplayProps {
  renderStatus: TaskStatus | null;
  renderProgress: number;
  getVideoUrl: () => string | null;
  onReset: () => void;
  onRetryFailedScenes: (failedScenes: any[]) => void;
}

export const RenderStatusDisplay: React.FC<RenderStatusDisplayProps> = React.memo(({
  renderStatus,
  renderProgress,
  getVideoUrl,
  onReset,
  onRetryFailedScenes,
}) => {
  if (!renderStatus) {
    return null;
  }

  return (
    <Stack spacing={3}>
      {/* Progress Bar */}
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {renderStatus.message || 'Processing...'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {Math.round(renderProgress)}%
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={renderProgress} sx={{ height: 8, borderRadius: 1 }} />
      </Box>

      {/* Success Status */}
      {renderStatus.status === 'completed' && renderStatus.result && !renderStatus.result.partial_success && (
        <Alert severity="success">
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            Video Rendered Successfully!
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Total cost: ${renderStatus.result.total_cost?.toFixed(2) || '0.00'}
            <br />
            Scenes rendered: {renderStatus.result.num_scenes || 0}
          </Typography>
          {getVideoUrl() && (
            <Box sx={{ mt: 2 }}>
              <video
                controls
                src={getVideoUrl()!}
                style={{ width: '100%', maxHeight: '500px', borderRadius: 8 }}
              />
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Download />}
                  href={getVideoUrl()!}
                  download
                >
                  Download Video
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={onReset}
                >
                  Render Another
                </Button>
              </Box>
            </Box>
          )}
        </Alert>
      )}

      {/* Failed Status */}
      {renderStatus.status === 'failed' && (
        <Alert severity="error">
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            Render Failed
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {renderStatus.error || 'An error occurred during rendering'}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              size="small"
              startIcon={<Refresh />}
              onClick={onReset}
            >
              Retry Render
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={onReset}
            >
              Start Over
            </Button>
          </Box>
        </Alert>
      )}

      {/* Partial Success Status */}
      {renderStatus.status === 'completed' && renderStatus.result?.partial_success && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            Partial Success
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {renderStatus.result.num_scenes} scenes rendered successfully, but{' '}
            {renderStatus.result.num_failed} scene(s) failed.
            {renderStatus.result.failed_scenes && renderStatus.result.failed_scenes.length > 0 && (
              <>
                <br />
                <br />
                <strong>Failed Scenes:</strong>
                {renderStatus.result.failed_scenes.map((failed: any, idx: number) => (
                  <Box key={idx} sx={{ mt: 1, p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
                    <Typography variant="caption">
                      Scene {failed.scene_number}: {failed.error || 'Unknown error'}
                    </Typography>
                  </Box>
                ))}
              </>
            )}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              size="small"
              startIcon={<Refresh />}
              onClick={() => {
                const failedScenes = renderStatus.result?.failed_scenes || [];
                onRetryFailedScenes(failedScenes);
              }}
            >
              Retry Failed Scenes
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={onReset}
            >
              View Successful Scenes
            </Button>
          </Box>
        </Alert>
      )}
    </Stack>
  );
});

RenderStatusDisplay.displayName = 'RenderStatusDisplay';

