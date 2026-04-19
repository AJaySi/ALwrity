import React from "react";
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  IconButton, 
  Typography, 
  Stack,
  Box,
  Divider,
  alpha,
} from "@mui/material";
import { Close as CloseIcon, Mic as MicIcon, Person as PersonIcon, AutoAwesome as AutoAwesomeIcon, Settings as SettingsIcon } from "@mui/icons-material";

export const DurationInfoModal: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
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
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              ⏱️ Episode Duration Guide
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small" sx={{ color: "rgba(255,255,255,0.7)" }}>
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
          Recommended durations based on content type and audience
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={2.5}>
          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5, color: '#4ade80' }}>
              Recommended Durations
            </Typography>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.9)" }}>1-3 minutes</Typography>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)" }}>Quick tips • Social media • Teasers</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.9)" }}>5-10 minutes</Typography>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)" }}>Standard podcast • Deep dives</Typography>
              </Stack>
            </Stack>
          </Box>

          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5, color: '#fb923c' }}>
              Cost vs Duration
            </Typography>
            <Stack spacing={1}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>1-3 min:</strong> $0.50 - $2.00 (Audio) / $3 - $6 (Video)
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>5 min:</strong> $1 - $3 (Audio) / $5 - $12 (Video)
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>10 min:</strong> $2 - $6 (Audio) / $10 - $20 (Video)
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5, color: '#a78bfa' }}>
              💡 Pro Tips
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Start short (1-3 min) for YouTube algorithm
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Deep content works best at 5-10 minutes
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Longest single call: 10 minutes max
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

export const SpeakersInfoModal: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
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
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              👥 Number of Speakers Guide
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small" sx={{ color: "rgba(255,255,255,0.7)" }}>
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
          Choose the right format for your content
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={2.5}>
          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5, color: '#4ade80' }}>
              🎤 1 Speaker (Solo)
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Best for: Tutorials, tips, personal stories
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Simpler script • Lower cost
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Full creative control
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5, color: '#fb923c' }}>
              👥 2 Speakers (Host + Guest)
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Best for: Interviews, debates, Q&A
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • More engaging • Broader perspectives
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Requires guest coordination
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5, color: '#a78bfa' }}>
              💡 Production Notes
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • 2 speakers = 2x script sections = ~2x word count
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Audio-only mode works best for interviews
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Video mode requires avatar setup for each speaker
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

export const VoiceInfoModal: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
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
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              🎤 Voice Selection Guide
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small" sx={{ color: "rgba(255,255,255,0.7)" }}>
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
          Choose the right voice for your podcast
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={2.5}>
          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
              <AutoAwesomeIcon sx={{ color: '#4ade80', fontSize: 18 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#4ade80' }}>
                Voice Clone
              </Typography>
            </Stack>
            <Stack spacing={1}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Your own voice - cloned from audio sample
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Most authentic and personalized
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Requires voice cloning setup in settings
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Best for: Brand podcasts, testimonials
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
              <MicIcon sx={{ color: '#fb923c', fontSize: 18 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#fb923c' }}>
                System Voices
              </Typography>
            </Stack>
            <Stack spacing={1}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>Female:</strong> Wise Woman, Friendly, Calm, Lively, Inspirational
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>Male:</strong> Deep Voice, Casual, Patient, Determined
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • Instant selection - no setup required
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
              <PersonIcon sx={{ color: '#a78bfa', fontSize: 18 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#a78bfa' }}>
                Voice Personalities
              </Typography>
            </Stack>
            <Stack spacing={0.5}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>Professional:</strong> Corporate, educational content
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>Happy/Energetic:</strong> Entertainment, announcements
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>Calm:</strong> Meditation, sensitive topics
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)", display: 'block' }}>
                • <strong>Storytelling:</strong> Narratives, books, experiences
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ p: 2, background: alpha("#ffffff", 0.1), borderRadius: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
              <SettingsIcon sx={{ color: '#38bdf8', fontSize: 18 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#38bdf8' }}>
                💡 Tips
              </Typography>
            </Stack>
            <Stack spacing={0.5}>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Match voice personality to your content type
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Use preview button to hear each voice
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.9)" }}>
                • Filter by gender/mood to find voices faster
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};