import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  CameraAlt,
  FlipCameraAndroid,
  Close,
  Camera
} from '@mui/icons-material';

interface RobustCameraProps {
  onCapture: (imageDataUrl: string) => void;
  onClose: () => void;
  open: boolean;
}

export const RobustCamera: React.FC<RobustCameraProps> = ({ onCapture, onClose, open }) => {
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  
  // Single source of truth - only use state for stream, not ref
  const [stream, setStream] = useState<MediaStream | null>(null);
  
  // DOM refs only
  const videoElementRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Track initialization to prevent double-init
  const isInitializingRef = useRef(false);
  const isMountedRef = useRef(true);

  // Cleanup function - stops all tracks and clears video
  const cleanupCamera = useCallback(() => {
    console.log('[RobustCamera] Cleaning up camera');
    
    // Stop video playback
    if (videoElementRef.current) {
      videoElementRef.current.pause();
      videoElementRef.current.srcObject = null;
      videoElementRef.current.load(); // Reset video element
    }
    
    // Stop all tracks in the stream
    if (stream) {
      stream.getTracks().forEach(track => {
        console.log('[RobustCamera] Stopping track:', track.kind, track.label);
        track.stop();
      });
    }
    
    // Clear state
    setStream(null);
    setCameraReady(false);
    setError(null);
    isInitializingRef.current = false;
  }, [stream]);

  // Initialize camera - only gets the stream, doesn't attach to video
  const initializeCamera = useCallback(async () => {
    // Prevent double initialization
    if (isInitializingRef.current) {
      console.log('[RobustCamera] Already initializing, skipping');
      return;
    }
    
    if (!isMountedRef.current) {
      console.log('[RobustCamera] Component not mounted, skipping');
      return;
    }
    
    console.log('[RobustCamera] Starting camera initialization');
    isInitializingRef.current = true;
    setLoading(true);
    setError(null);
    setCameraReady(false);
    
    // Clean up any existing stream first
    if (stream) {
      console.log('[RobustCamera] Cleaning up existing stream first');
      stream.getTracks().forEach(track => track.stop());
    }

    try {
      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280, min: 640 },
          height: { ideal: 720, min: 480 },
        },
        audio: false,
      };

      console.log('[RobustCamera] Requesting camera with constraints:', constraints);
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      
      if (!isMountedRef.current) {
        // Component unmounted while awaiting, clean up
        console.log('[RobustCamera] Component unmounted, stopping stream');
        mediaStream.getTracks().forEach(track => track.stop());
        return;
      }
      
      console.log('[RobustCamera] Camera stream obtained:', mediaStream.id, 'Tracks:', mediaStream.getTracks().length);
      setStream(mediaStream);
      setLoading(false);
      
    } catch (err) {
      console.error('[RobustCamera] Camera access error:', err);
      
      if (!isMountedRef.current) return;
      
      setLoading(false);
      isInitializingRef.current = false;
      
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('Camera access denied. Please allow camera permissions in your browser settings.');
        } else if (err.name === 'NotFoundError') {
          setError('No camera found on this device.');
        } else if (err.name === 'NotReadableError') {
          setError('Camera is already in use by another application. Please close other apps using the camera.');
        } else if (err.name === 'OverconstrainedError') {
          setError('Camera does not support the requested resolution. Please try again.');
        } else {
          setError(`Failed to access camera: ${err.message}`);
        }
      } else {
        setError('Failed to access camera. Please try again.');
      }
    }
  }, [facingMode, stream]);

  // SINGLE useEffect to handle stream attachment to video
  // This runs whenever stream changes or video element becomes available
  useEffect(() => {
    const video = videoElementRef.current;
    
    if (!video || !stream) {
      console.log('[RobustCamera] Cannot attach - video:', !!video, 'stream:', !!stream);
      return;
    }
    
    if (video.srcObject === stream) {
      console.log('[RobustCamera] Stream already attached to video');
      return;
    }
    
    console.log('[RobustCamera] Attaching stream to video element');
    
    // Set up event handlers before attaching
    const handleLoadedMetadata = () => {
      console.log('[RobustCamera] Video metadata loaded, playing...');
      if (!isMountedRef.current) return;
      
      video.play()
        .then(() => {
          console.log('[RobustCamera] Video playing successfully');
          if (isMountedRef.current) {
            setCameraReady(true);
          }
        })
        .catch(err => {
          console.error('[RobustCamera] Video play error:', err);
          if (isMountedRef.current) {
            setError('Camera stream ready but video playback failed. Please try again.');
          }
        });
    };
    
    const handleError = (err: Event) => {
      console.error('[RobustCamera] Video error:', err);
      if (isMountedRef.current) {
        setError('Failed to display camera feed. Please try again.');
      }
    };
    
    // Attach event listeners
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('error', handleError);
    
    // Attach the stream
    video.srcObject = stream;
    
    // Cleanup function
    return () => {
      console.log('[RobustCamera] Cleaning up video event listeners');
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('error', handleError);
    };
  }, [stream]);

  // Initialize camera when dialog opens
  useEffect(() => {
    if (open) {
      console.log('[RobustCamera] Dialog opened');
      isMountedRef.current = true;
      
      // Small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        initializeCamera();
      }, 100);
      
      return () => {
        clearTimeout(timer);
      };
    } else {
      // Dialog closed - cleanup
      console.log('[RobustCamera] Dialog closed, cleaning up');
      cleanupCamera();
    }
  }, [open, initializeCamera, cleanupCamera]);

  // Handle facing mode changes
  useEffect(() => {
    if (!open || !stream) return;
    
    console.log('[RobustCamera] Facing mode changed, reinitializing');
    cleanupCamera();
    
    const timer = setTimeout(() => {
      isInitializingRef.current = false;
      initializeCamera();
    }, 300);
    
    return () => clearTimeout(timer);
  }, [facingMode, open]); // Only re-run when facingMode actually changes

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log('[RobustCamera] Component unmounting');
      isMountedRef.current = false;
      cleanupCamera();
    };
  }, [cleanupCamera]);

  // Capture photo
  const capturePhoto = useCallback(() => {
    if (!videoElementRef.current || !canvasRef.current || !cameraReady) {
      console.log('[RobustCamera] Cannot capture: not ready');
      return;
    }

    const video = videoElementRef.current;
    const canvas = canvasRef.current;
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    
    console.log('[RobustCamera] Capturing photo:', canvas.width, 'x', canvas.height);
    
    // Draw video frame to canvas
    const context = canvas.getContext('2d');
    if (context) {
      // Flip context if using front camera for mirror effect correction
      if (facingMode === 'user') {
        context.translate(canvas.width, 0);
        context.scale(-1, 1);
      }
      
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to data URL
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9);
      console.log('[RobustCamera] Photo captured');
      
      onCapture(imageDataUrl);
      onClose();
    }
  }, [cameraReady, facingMode, onCapture, onClose]);

  // Flip camera
  const flipCamera = useCallback(() => {
    console.log('[RobustCamera] Flipping camera');
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  }, []);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          overflow: 'hidden'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        bgcolor: 'primary.main',
        color: 'white'
      }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CameraAlt />
          Take a Selfie
        </Typography>
        <IconButton onClick={onClose} sx={{ color: 'white' }}>
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 3, minHeight: 400 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading && (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            minHeight: 300,
            gap: 2
          }}>
            <CircularProgress size={60} />
            <Typography variant="body1" color="text.secondary">
              Initializing camera...
            </Typography>
          </Box>
        )}

        <Box sx={{ 
          position: 'relative',
          width: '100%',
          maxWidth: 600,
          mx: 'auto',
          bgcolor: 'black',
          borderRadius: 2,
          overflow: 'hidden',
          minHeight: 300,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {/* Video element - always rendered but styled based on readiness */}
          <video
            ref={videoElementRef}
            autoPlay
            playsInline
            muted
            disablePictureInPicture
            controls={false}
            style={{
              width: '100%',
              height: 'auto',
              maxHeight: '60vh',
              objectFit: 'contain',
              display: cameraReady ? 'block' : 'none',
              transform: facingMode === 'user' ? 'scaleX(-1)' : 'none'
            }}
          />
          
          {/* Loading overlay - shown when stream exists but camera not ready */}
          {!cameraReady && stream && (
            <Box sx={{ 
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'rgba(0,0,0,0.9)',
              color: 'white',
              gap: 2,
              zIndex: 1
            }}>
              <CircularProgress size={40} sx={{ color: 'white' }} />
              <Typography variant="body1">
                Starting camera feed...
              </Typography>
            </Box>
          )}

          {/* Initial state - no stream yet */}
          {!cameraReady && !stream && !loading && !error && (
            <Box sx={{ 
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'rgba(0,0,0,0.8)',
              color: 'white',
              gap: 2
            }}>
              <Camera sx={{ fontSize: 60 }} />
              <Typography variant="body1" textAlign="center">
                Camera initializing...
              </Typography>
            </Box>
          )}
        </Box>

        <canvas
          ref={canvasRef}
          style={{ display: 'none' }}
        />
      </DialogContent>

      <DialogActions sx={{ p: 3, gap: 2 }}>
        {cameraReady && (
          <>
            <Tooltip title="Flip Camera">
              <IconButton onClick={flipCamera} color="primary">
                <FlipCameraAndroid />
              </IconButton>
            </Tooltip>
            <Button
              onClick={capturePhoto}
              variant="contained"
              size="large"
              startIcon={<CameraAlt />}
              sx={{ 
                borderRadius: 2,
                px: 3,
                py: 1.5
              }}
            >
              Capture Photo
            </Button>
          </>
        )}
        
        <Button onClick={onClose} variant="outlined">
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
};
