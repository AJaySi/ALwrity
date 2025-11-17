import React, { useState, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  CircularProgress,
  Paper,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import RefreshIcon from '@mui/icons-material/Refresh';
import { fetchMediaBlobUrl } from '../../../utils/fetchMediaBlobUrl';

interface SceneVideoApprovalProps {
  open: boolean;
  sceneNumber: number;
  sceneTitle: string;
  totalScenes: number;
  videoUrl: string;
  promptUsed: string;
  onApprove: () => void;
  onReject: () => void;
  onRegenerate: () => void;
  isRegenerating?: boolean;
  onClose?: () => void;
}

const SceneVideoApproval: React.FC<SceneVideoApprovalProps> = ({
  open,
  sceneNumber,
  sceneTitle,
  totalScenes,
  videoUrl,
  promptUsed,
  onApprove,
  onReject,
  onRegenerate,
  isRegenerating = false,
  onClose,
}) => {
  const [videoBlobUrl, setVideoBlobUrl] = useState<string | null>(null);
  const [loadingVideo, setLoadingVideo] = useState(true);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  // Load video when modal opens
  React.useEffect(() => {
    if (open && videoUrl) {
      setLoadingVideo(true);
      fetchMediaBlobUrl(videoUrl)
        .then((blobUrl) => {
          setVideoBlobUrl(blobUrl);
          setLoadingVideo(false);
        })
        .catch((err) => {
          console.error('Failed to load video:', err);
          setLoadingVideo(false);
        });
    }

    // Cleanup blob URL when modal closes
    return () => {
      if (videoBlobUrl) {
        URL.revokeObjectURL(videoBlobUrl);
        setVideoBlobUrl(null);
      }
    };
  }, [open, videoUrl]);

  const handleClose = () => {
    if (onClose && !isRegenerating) {
      onClose();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: '#fff',
          borderRadius: 2,
          boxShadow: '0 24px 64px rgba(0,0,0,0.18)',
          border: '1px solid rgba(0,0,0,0.06)',
        },
      }}
    >
      <DialogTitle sx={{ color: '#1A1611', pb: 1 }}>
        <Typography variant="h6" component="div">
          Scene {sceneNumber} of {totalScenes}: {sceneTitle}
        </Typography>
        <Typography variant="caption" sx={{ color: '#5D4037', mt: 0.5, display: 'block' }}>
          Review the generated HD video and choose an action
        </Typography>
      </DialogTitle>

      <DialogContent dividers sx={{ color: '#2C2416' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Video Player */}
          <Box
            sx={{
              position: 'relative',
              width: '100%',
              backgroundColor: '#000',
              borderRadius: 1,
              overflow: 'hidden',
              minHeight: '300px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {loadingVideo ? (
              <CircularProgress sx={{ color: '#fff' }} />
            ) : videoBlobUrl ? (
              <video
                ref={videoRef}
                controls
                src={videoBlobUrl}
                style={{
                  width: '100%',
                  height: 'auto',
                  maxHeight: '500px',
                }}
              >
                Your browser does not support the video element.
              </video>
            ) : (
              <Typography sx={{ color: '#fff' }}>Failed to load video</Typography>
            )}
          </Box>

          {/* Prompt Used */}
          {promptUsed && (
            <Paper
              elevation={0}
              sx={{
                p: 2,
                backgroundColor: '#FAF9F6',
                borderRadius: 1,
                border: '1px solid #E0DCD4',
              }}
            >
              <Typography variant="subtitle2" sx={{ color: '#1A1611', mb: 1, fontWeight: 600 }}>
                Generated Prompt (for transparency):
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: '#2C2416',
                  fontFamily: 'monospace',
                  fontSize: '0.85rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {promptUsed}
              </Typography>
            </Paper>
          )}

          {isRegenerating && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, backgroundColor: '#FFF3E0', borderRadius: 1 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" sx={{ color: '#5D4037' }}>
                Regenerating video for this scene...
              </Typography>
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, gap: 1 }}>
        <Button
          onClick={onReject}
          disabled={isRegenerating}
          startIcon={<CancelIcon />}
          sx={{ color: '#5D4037' }}
        >
          Reject & Skip
        </Button>
        <Button
          onClick={onRegenerate}
          disabled={isRegenerating}
          startIcon={isRegenerating ? <CircularProgress size={16} /> : <RefreshIcon />}
          sx={{ color: '#5D4037' }}
        >
          {isRegenerating ? 'Regenerating...' : 'Regenerate This Scene'}
        </Button>
        <Button
          variant="contained"
          onClick={onApprove}
          disabled={isRegenerating || loadingVideo || !videoBlobUrl}
          startIcon={<CheckCircleIcon />}
          sx={{
            backgroundColor: '#5D4037',
            '&:hover': {
              backgroundColor: '#4E342E',
            },
          }}
        >
          Approve & Continue
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SceneVideoApproval;

