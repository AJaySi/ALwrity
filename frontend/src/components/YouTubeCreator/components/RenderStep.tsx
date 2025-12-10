/**
 * Render Step Component
 */

import React from 'react';
import {
  Paper,
  Typography,
  Stack,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Button,
  Box,
  Alert,
  LinearProgress,
  CircularProgress,
  Typography as MuiTypography,
} from '@mui/material';
import { PlayArrow, Download, Refresh } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { TaskStatus, CostEstimate } from '../../../services/youtubeApi';
import { YT_BORDER, RESOLUTIONS, type Resolution } from '../constants';

interface RenderStepProps {
  renderTaskId: string | null;
  renderStatus: TaskStatus | null;
  renderProgress: number;
  resolution: Resolution;
  combineScenes: boolean;
  enabledScenesCount: number;
  costEstimate: CostEstimate | null;
  loadingCostEstimate: boolean;
  loading: boolean;
  onResolutionChange: (resolution: Resolution) => void;
  onCombineScenesChange: (combine: boolean) => void;
  onStartRender: () => void;
  onBack: () => void;
  onReset: () => void;
  onRetryFailedScenes: (failedScenes: any[]) => void;
  getVideoUrl: () => string | null;
}

export const RenderStep: React.FC<RenderStepProps> = React.memo(({
  renderTaskId,
  renderStatus,
  renderProgress,
  resolution,
  combineScenes,
  enabledScenesCount,
  costEstimate,
  loadingCostEstimate,
  loading,
  onResolutionChange,
  onCombineScenesChange,
  onStartRender,
  onBack,
  onReset,
  onRetryFailedScenes,
  getVideoUrl,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Paper
        sx={{
          p: 4,
          backgroundColor: 'white',
          border: `1px solid ${YT_BORDER}`,
        }}
      >
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          3️⃣ Render Video
        </Typography>

        {!renderTaskId ? (
          <Stack spacing={3}>
            <Alert severity="info">
              Configure render settings and start generating your video. This may take several minutes.
            </Alert>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Video Resolution</InputLabel>
                  <Select
                    value={resolution}
                    label="Video Resolution"
                    onChange={(e) => onResolutionChange(e.target.value as Resolution)}
                  >
                    {RESOLUTIONS.map((res) => (
                      <MenuItem key={res} value={res}>
                        {res === '480p' && '480p (Lower cost, faster)'}
                        {res === '720p' && '720p (Recommended)'}
                        {res === '1080p' && '1080p (Highest quality)'}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={combineScenes}
                      onChange={(e) => onCombineScenesChange(e.target.checked)}
                    />
                  }
                  label="Combine scenes into single video"
                />
              </Grid>
            </Grid>

            <Box sx={{ p: 2, bgcolor: '#f4f4f4', borderRadius: 1, border: `1px solid ${YT_BORDER}` }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                Render Summary
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                • {enabledScenesCount} scenes will be rendered
                <br />
                • Resolution: {resolution}
                <br />
                • {combineScenes ? 'Scenes will be combined into one video' : 'Each scene will be a separate video'}
                <br />
              </Typography>

              {/* Cost Estimate */}
              {loadingCostEstimate ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    Calculating cost estimate...
                  </Typography>
                </Box>
              ) : costEstimate ? (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'primary.light', borderRadius: 1, border: '1px solid', borderColor: 'primary.main' }}>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: 'primary.dark' }}>
                    💰 Estimated Cost
                  </Typography>
                  <Typography variant="h6" sx={{ mb: 1, color: 'primary.dark' }}>
                    ${costEstimate.total_cost.toFixed(2)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Range: ${costEstimate.estimated_cost_range.min.toFixed(2)} - ${costEstimate.estimated_cost_range.max.toFixed(2)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    • {costEstimate.num_scenes} scenes × ${costEstimate.price_per_second.toFixed(2)}/second
                    <br />
                    • Total duration: ~{Math.round(costEstimate.total_duration_seconds)} seconds
                    <br />
                    • Price per second: ${costEstimate.price_per_second.toFixed(2)} ({costEstimate.resolution})
                  </Typography>
                  {costEstimate.scene_costs.length > 0 && (
                    <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
                        Per Scene Breakdown:
                      </Typography>
                      {costEstimate.scene_costs.slice(0, 5).map((sceneCost) => (
                        <Typography key={sceneCost.scene_number} variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          Scene {sceneCost.scene_number}: {sceneCost.actual_duration}s = ${sceneCost.cost.toFixed(2)}
                        </Typography>
                      ))}
                      {costEstimate.scene_costs.length > 5 && (
                        <Typography variant="caption" color="text.secondary">
                          ... and {costEstimate.scene_costs.length - 5} more scenes
                        </Typography>
                      )}
                    </Box>
                  )}
                </Box>
              ) : (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Unable to calculate cost estimate. Please check your scenes and try again.
                </Alert>
              )}
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="outlined" onClick={onBack}>
                Back to Scenes
              </Button>
              <Button
                variant="contained"
                color="error"
                size="large"
                onClick={onStartRender}
                disabled={loading || enabledScenesCount === 0}
                startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                sx={{ px: 4 }}
              >
                {loading ? 'Starting Render...' : 'Start Video Render'}
              </Button>
            </Box>
          </Stack>
        ) : (
          <Stack spacing={3}>
            {renderStatus && (
              <>
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

                {renderStatus.status === 'completed' && renderStatus.result && (
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
              </>
            )}
          </Stack>
        )}
      </Paper>
    </motion.div>
  );
});

RenderStep.displayName = 'RenderStep';

