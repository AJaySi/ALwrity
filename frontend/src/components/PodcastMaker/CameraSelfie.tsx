import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Button,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  alpha,
} from '@mui/material';
import {
  Camera as CameraIcon,
  FlipCameraAndroid as FlipCameraIcon,
  Close as CloseIcon,
  PhotoCamera as PhotoCameraIcon,
  VideocamOff as VideocamOffIcon,
} from '@mui/icons-material';

interface CameraSelfieProps {
  onCapture: (imageDataUrl: string) => void;
  onClose: () => void;
  open: boolean;
}

export const CameraSelfie: React.FC<CameraSelfieProps> = ({ onCapture, onClose, open }) => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraAvailable, setCameraAvailable] = useState(true);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const startCamera = useCallback(async () => {
    if (loading) {
      return; // Prevent multiple simultaneous camera requests
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Stop existing stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }

      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);
      
      // Function to attach stream to video element
      const attachStreamToVideo = () => {
        if (videoRef.current) {
          // Clear any existing stream
          if (videoRef.current.srcObject) {
            const oldStream = videoRef.current.srcObject as MediaStream;
            oldStream.getTracks().forEach(track => track.stop());
          }
          
          // Attach new stream
          videoRef.current.srcObject = mediaStream;
          
          // Wait for video to be ready
          videoRef.current.onloadedmetadata = () => {
            setCameraAvailable(true);
            setLoading(false);
            // Try to play the video
            videoRef.current?.play().catch(err => {
              console.error('Video play error:', err);
            });
          };
          
          // Handle video errors
          videoRef.current.onerror = (err) => {
            console.error('Video error:', err);
            setError('Failed to display camera feed.');
            setLoading(false);
          };
          
          return true; // Successfully attached
        }
        return false; // Video ref not available
      };
      
      // Try to attach immediately
      if (!attachStreamToVideo()) {
        // Retry every 100ms for up to 2 seconds
        let retryCount = 0;
        const retryInterval = setInterval(() => {
          retryCount++;
          
          if (attachStreamToVideo() || retryCount >= 20) {
            clearInterval(retryInterval);
            
            if (retryCount >= 20) {
              setCameraAvailable(true);
              setLoading(false);
            }
          }
        }, 100);
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setCameraAvailable(false);
      setLoading(false); // Set loading to false in error case
      
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('Camera access denied. Please allow camera permissions to take a selfie.');
        } else if (err.name === 'NotFoundError') {
          setError('No camera found on this device.');
        } else if (err.name === 'NotReadableError') {
          setError('Camera is already in use by another application.');
        } else {
          setError('Failed to access camera. Please try again.');
        }
      }
    }
  }, [facingMode, stream, loading]);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  }, [stream]);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw the current video frame to canvas
    const context = canvas.getContext('2d');
    if (context) {
      // Flip horizontally for selfie (mirror effect)
      context.translate(canvas.width, 0);
      context.scale(-1, 1);
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to data URL
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9);
      onCapture(imageDataUrl);
    }
  }, [onCapture]);

  const flipCamera = useCallback(() => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  }, []);

  // Start camera when dialog opens
  React.useEffect(() => {
    if (open) {
      // Small delay to ensure video element is mounted
      const timer = setTimeout(() => {
        startCamera();
      }, 100);
      
      return () => {
        clearTimeout(timer);
        stopCamera();
      };
    }
  }, [open, startCamera, stopCamera]); // Add back dependencies with proper useCallback

  // Restart camera when facing mode changes
  React.useEffect(() => {
    if (open && stream) {
      // Stop current stream before starting new one
      stopCamera();
      // Small delay to ensure proper cleanup
      setTimeout(() => {
        startCamera();
      }, 100);
    }
  }, [facingMode, open, stream, startCamera, stopCamera]); // Add back dependencies

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          overflow: 'hidden',
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          p: 2,
          bgcolor: 'primary.main',
          color: '#ffffff',
        }}
      >
        Take a Selfie
        <IconButton onClick={onClose} sx={{ color: '#ffffff' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0, minHeight: 400 }}>
        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        {loading && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 400,
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <CircularProgress size={48} />
            <Typography variant="body2" color="text.secondary">
              Accessing camera...
            </Typography>
          </Box>
        )}

        {!loading && !error && cameraAvailable && (
          <Box sx={{ position: 'relative', width: '100%', bgcolor: '#000000', minHeight: 400 }}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{
                width: '100%',
                height: '100%',
                minHeight: 400,
                objectFit: 'cover',
                display: 'block',
                transform: facingMode === 'user' ? 'scaleX(-1)' : 'none',
              }}
            />
            
            {/* Camera controls overlay */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                p: 2,
                background: 'linear-gradient(to top, rgba(0,0,0,0.7), transparent)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <Tooltip title="Flip Camera">
                <IconButton
                  onClick={flipCamera}
                  sx={{
                    bgcolor: alpha('#ffffff', 0.2),
                    color: '#ffffff',
                    '&:hover': {
                      bgcolor: alpha('#ffffff', 0.3),
                    },
                  }}
                >
                  <FlipCameraIcon />
                </IconButton>
              </Tooltip>

              <Tooltip title="Take Photo">
                <IconButton
                  onClick={capturePhoto}
                  sx={{
                    bgcolor: '#ffffff',
                    color: '#000000',
                    width: 56,
                    height: 56,
                    '&:hover': {
                      bgcolor: alpha('#ffffff', 0.9),
                    },
                  }}
                >
                  <PhotoCameraIcon sx={{ fontSize: 32 }} />
                </IconButton>
              </Tooltip>

              <Tooltip title="Close">
                <IconButton
                  onClick={onClose}
                  sx={{
                    bgcolor: alpha('#ffffff', 0.2),
                    color: '#ffffff',
                    '&:hover': {
                      bgcolor: alpha('#ffffff', 0.3),
                    },
                  }}
                >
                  <VideocamOffIcon />
                </IconButton>
              </Tooltip>
            </Box>

            {/* Face guide overlay */}
            <Box
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: 200,
                height: 250,
                border: '2px dashed rgba(255,255,255,0.3)',
                borderRadius: 2,
                pointerEvents: 'none',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  position: 'absolute',
                  top: -25,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  color: '#ffffff',
                  bgcolor: 'rgba(0,0,0,0.5)',
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  fontSize: '0.75rem',
                }}
              >
                Position face here
              </Typography>
            </Box>
          </Box>
        )}

        {!cameraAvailable && !error && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 400,
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <CameraIcon sx={{ fontSize: 64, color: 'text.secondary' }} />
            <Typography variant="h6" color="text.secondary">
              Camera Not Available
            </Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              Your device doesn't have a camera or it's not accessible.
              Please use the file upload option instead.
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button onClick={onClose} variant="outlined">
          Cancel
        </Button>
        {cameraAvailable && (
          <Button onClick={capturePhoto} variant="contained" startIcon={<PhotoCameraIcon />}>
            Take Photo
          </Button>
        )}
      </DialogActions>

      {/* Hidden canvas for image capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </Dialog>
  );
};
