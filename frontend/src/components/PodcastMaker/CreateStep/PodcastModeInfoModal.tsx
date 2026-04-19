import React from "react";
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  IconButton, 
  Box, 
  Typography, 
  Stack, 
  Chip,
  Divider,
  alpha,
} from "@mui/material";
import { Close as CloseIcon, HelpOutline as HelpOutlineIcon } from "@mui/icons-material";

export const PodcastModeInfoModal: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ 
        sx: { 
          borderRadius: 3,
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
        } 
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              Choosing Your Podcast Mode
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Understand cost, duration, and best use cases for each mode
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small" sx={{ color: "rgba(255,255,255,0.7)" }}>
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ opacity: 0.7, mt: 1 }}>
          Select the right podcast mode based on your content type, target audience, and budget.
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          {/* Mode Overview */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                🎙️ Podcast Modes Explained
              </Typography>
              <Box sx={{ color: "rgba(255,255,255,0.5)" }}>
                <HelpOutlineIcon fontSize="small" />
              </Box>
            </Stack>
            <Stack spacing={1.5}>
              {[
                { mode: 'audio_only', icon: '🎧', label: 'Audio Only', desc: 'AI voice podcast. No video. Best for audio platforms.',
                  bg: '#f0fdf4', borderColor: '#10b981', textColor: '#166534' },
                { mode: 'video_only', icon: '🎬', label: 'Video Only', desc: 'AI avatar video. Best for YouTube and social media.',
                  bg: '#fff7ed', borderColor: '#f97316', textColor: '#9a3412' },
                { mode: 'audio_video', icon: '🎧+🎬', label: 'Both (Audio + Video)', desc: 'Generates both versions. Best for multi-platform distribution.',
                  bg: '#f5f3ff', borderColor: '#8b5cf6', textColor: '#6b21a8' },
              ].map((item) => (
                <Box 
                  key={item.mode}
                  sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    border: `1px solid ${item.borderColor}`,
                    background: alpha(item.bg, 0.95),
                    opacity: 0.95
                  }}
                >
                  <Stack direction="row" alignItems="center" spacing={1.5}>
                    <Typography sx={{ fontSize: '1.5rem' }}>{item.icon}</Typography>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, color: item.textColor }}>
                        {item.label}
                      </Typography>
                      <Typography variant="body2" sx={{ color: item.textColor, fontSize: '0.875rem', opacity: 0.9 }}>
                        {item.desc}
                      </Typography>
                    </Box>
                  </Stack>
                </Box>
              ))}
            </Stack>
          </Box>

          <Divider sx={{ borderColor: "rgba(255,255,255,0.2)" }} />

          {/* AI API Costs */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                💰 AI API Costs (Estimated per 5-min episode)
              </Typography>
            </Stack>
            <Box sx={{ 
              p: 2, 
              background: alpha("#ffffff", 0.1), 
              borderRadius: 2,
              border: '1px solid rgba(255,255,255,0.1)'
            }}>
              <Stack spacing={1.5}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ py: 0.5, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'white' }}>Audio Only</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)" }}>TTS API (voice generation)</Typography>
                  </Box>
                  <Chip label="$0.50 - $1.50" size="small" sx={{ background: '#10b981', color: '#fff', fontWeight: 600 }} />
                </Stack>
                
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ py: 0.5, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'white' }}>Video Only</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)" }}>TTS + Image Generation APIs</Typography>
                  </Box>
                  <Chip label="$3.00 - $8.00" size="small" sx={{ background: '#f97316', color: '#fff', fontWeight: 600 }} />
                </Stack>
                
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ py: 0.5 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'white' }}>Both</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)" }}>TTS + Image + Video combination</Typography>
                  </Box>
                  <Chip label="$4.00 - $12.00" size="small" sx={{ background: '#8b5cf6', color: '#fff', fontWeight: 600 }} />
                </Stack>
              </Stack>
            </Box>
            <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block', fontStyle: 'italic' }}>
              * Actual costs vary based on scene count, image resolution, and API provider
            </Typography>
          </Box>

          <Divider sx={{ borderColor: "rgba(255,255,255,0.2)" }} />

          {/* Max Duration & Optimization */}
          <Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>
              ⏱️ Maximum Duration & AI Optimization
            </Typography>
            <Stack spacing={1.5}>
              <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2, border: '1px solid rgba(255,255,255,0.1)' }}>
                <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
                  <Chip label="Audio Only" size="small" sx={{ background: '#10b981', color: '#fff' }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#4ade80' }}>
                    Max 3-4 scenes per episode • Optimized with fewer API calls
                  </Typography>
                </Stack>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block', mb: 0.5 }}>
                  • Each scene: 800-1200 words (~1.5 min audio)
                </Typography>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block', mb: 0.5 }}>
                  • Fewer API calls = lower cost
                </Typography>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                  • Rich, content-dense script for audio-only listening
                </Typography>
              </Box>
              
              <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2, border: '1px solid rgba(255,255,255,0.1)' }}>
                <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
                  <Chip label="Video Only" size="small" sx={{ background: '#f97316', color: '#fff' }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#fb923c' }}>
                    Max 5-6 scenes per episode • More visuals = more image costs
                  </Typography>
                </Stack>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block', mb: 0.5 }}>
                  • Each scene: 300-500 words (~30-45 sec)
                </Typography>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block', mb: 0.5 }}>
                  • Shorter scripts for visual pacing + image rendering time
                </Typography>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                  • More scenes = more image generation API calls
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Divider sx={{ borderColor: "rgba(255,255,255,0.2)" }} />

          {/* When to Use */}
          <Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>
              🎯 When to Choose Each Mode
            </Typography>
            <Stack spacing={1.5}>
              <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2, border: '1px solid rgba(255,255,255,0.1)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#4ade80', mb: 1 }}>
                  🎧 Choose Audio Only For:
                </Typography>
                <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ gap: 0.5 }}>
                  {['Spotify & Podcasts', 'Low budget', 'Evergreen content', 'Commute listeners', 'Deep content'].map((item) => (
                    <Chip key={item} label={item} size="small" variant="outlined" sx={{ borderColor: '#4ade80', color: '#4ade80' }} />
                  ))}
                </Stack>
              </Box>
              
              <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2, border: '1px solid rgba(255,255,255,0.1)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#fb923c', mb: 1 }}>
                  🎬 Choose Video Only For:
                </Typography>
                <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ gap: 0.5 }}>
                  {['YouTube', 'Social Media', 'Personal Brand', 'Visual Content', 'Tutorials'].map((item) => (
                    <Chip key={item} label={item} size="small" variant="outlined" sx={{ borderColor: '#fb923c', color: '#fb923c' }} />
                  ))}
                </Stack>
              </Box>
              
              <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2, border: '1px solid rgba(255,255,255,0.1)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#a78bfa', mb: 1 }}>
                  🎧+🎬 Choose Both For:
                </Typography>
                <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ gap: 0.5 }}>
                  {['Multi-platform', 'Max Reach', 'Content Repurpose', 'Premium Podcast'].map((item) => (
                    <Chip key={item} label={item} size="small" variant="outlined" sx={{ borderColor: '#a78bfa', color: '#a78bfa' }} />
                  ))}
                </Stack>
              </Box>
            </Stack>
          </Box>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};