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
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  
  // Use multiple refs for different purposes
  const videoElementRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const cameraInitRef = useRef<boolean>(false);
  const retryCountRef = useRef<number>(0);

  // Clean up stream
  const cleanupStream = useCallback(() => {
    console.log('[RobustCamera] Cleaning up stream');
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoElementRef.current && videoElementRef.current.srcObject) {
      videoElementRef.current.srcObject = null;
    }
    setStream(null);
    setCameraReady(false);
    cameraInitRef.current = false;
    retryCountRef.current = 0;
  }, []);

  // Initialize camera
  const initializeCamera = useCallback(async () => {
    if (cameraInitRef.current || loading) {
      console.log('[RobustCamera] Camera already initializing or loading');
      return;
    }

    console.log('[RobustCamera] Starting camera initialization');
    cameraInitRef.current = true;
    setLoading(true);
    setError(null);
    cleanupStream();

    try {
      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      };

      console.log('[RobustCamera] Requesting camera with constraints:', constraints);
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('[RobustCamera] Camera stream obtained successfully');
      
      streamRef.current = mediaStream;
      setStream(mediaStream);

      // Attach to video element
      if (videoElementRef.current) {
        console.log('[RobustCamera] Video element found, attaching stream');
        videoElementRef.current.srcObject = mediaStream;
        
        videoElementRef.current.onloadedmetadata = () => {
          console.log('[RobustCamera] Video metadata loaded');
          setCameraReady(true);
          setLoading(false);
          videoElementRef.current?.play().catch(err => {
            console.error('[RobustCamera] Video play error:', err);
            setError('Camera stream obtained but video display failed. Please try again.');
          });
        };

        videoElementRef.current.onerror = (err) => {
          console.error('[RobustCamera] Video error:', err);
          setError('Failed to display camera feed.');
          setLoading(false);
        };
      } else {
        console.log('[RobustCamera] Video element not found, will attach when ready');
        setCameraReady(false);
        setLoading(false);
        // Stream will be attached when video element mounts
      }

    } catch (err) {
      console.error('[RobustCamera] Camera access error:', err);
      cleanupStream();
      setLoading(false);
      
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
  }, [facingMode, loading, cleanupStream]);

  // Attach stream when video element is available
  const attachStreamToVideo = useCallback(() => {
    if (videoElementRef.current && streamRef.current && !cameraReady) {
      console.log('[RobustCamera] Attaching stream to video element');
      const video = videoElementRef.current;
      const stream = streamRef.current;
      
      // Clear any existing stream
      if (video.srcObject) {
        const oldStream = video.srcObject as MediaStream;
        oldStream.getTracks().forEach(track => track.stop());
      }
      
      // Attach new stream
      video.srcObject = stream;
      
      video.onloadedmetadata = () => {
        console.log('[RobustCamera] Video metadata loaded after attachment');
        setCameraReady(true);
        setLoading(false);
        video.play().catch(err => {
          console.error('[RobustCamera] Video play error after attachment:', err);
          setError('Camera stream obtained but video display failed. Please try again.');
        });
      };

      video.onerror = (err) => {
        console.error('[RobustCamera] Video error after attachment:', err);
        setError('Failed to display camera feed.');
        setLoading(false);
      };
    } else {
      console.log('[RobustCamera] Cannot attach stream:', {
        videoExists: !!videoElementRef.current,
        streamExists: !!streamRef.current,
        cameraReady
      });
    }
  }, [cameraReady]);

  // Capture photo
  const capturePhoto = useCallback(() => {
    if (!videoElementRef.current || !canvasRef.current || !cameraReady) {
      console.log('[RobustCamera] Cannot capture: video or canvas not ready');
      return;
    }

    const video = videoElementRef.current;
    const canvas = canvasRef.current;
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    const context = canvas.getContext('2d');
    if (context) {
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to data URL
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9);
      console.log('[RobustCamera] Photo captured successfully');
      onCapture(imageDataUrl);
      onClose();
    }
  }, [cameraReady, onCapture, onClose]);

  // Flip camera
  const flipCamera = useCallback(() => {
    console.log('[RobustCamera] Flipping camera');
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  }, []);

  // Initialize camera when dialog opens
  useEffect(() => {
    if (open) {
      console.log('[RobustCamera] Dialog opened, initializing camera');
      // Small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        initializeCamera();
      }, 300);
      
      return () => {
        clearTimeout(timer);
        cleanupStream();
      };
    }
  }, [open]); // Remove initializeCamera and cleanupStream from dependencies

  // Re-initialize when facing mode changes
  useEffect(() => {
    if (open && cameraReady) {
      console.log('[RobustCamera] Facing mode changed, re-initializing camera');
      cleanupStream();
      const timer = setTimeout(() => {
        initializeCamera();
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [facingMode]); // Remove other dependencies to prevent loops

  // Attach stream when video element is available
  useEffect(() => {
    if (videoElementRef.current && streamRef.current && !cameraReady) {
      console.log('[RobustCamera] Video element available, attaching stream');
      attachStreamToVideo();
    }
  }, [stream, cameraReady]); // Trigger when stream changes

  // Attach stream when component mounts or stream changes
  useEffect(() => {
    if (open && stream && !cameraReady && videoElementRef.current) {
      console.log('[RobustCamera] Stream available, attaching to video element');
      attachStreamToVideo();
    }
  }, [open, stream]); // Remove cameraReady and attachStreamToVideo to prevent loops

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

        {!loading && !error && (
          <Box sx={{ 
            position: 'relative',
            width: '100%',
            maxWidth: 600,
            mx: 'auto',
            bgcolor: 'black',
            borderRadius: 2,
            overflow: 'hidden'
          }}>
            <video
              ref={videoElementRef}
              autoPlay
              playsInline
              muted
              style={{
                width: '100%',
                height: 'auto',
                display: cameraReady ? 'block' : 'none',
                transform: facingMode === 'user' ? 'scaleX(-1)' : 'none'
              }}
            />
            
            {!cameraReady && stream && (
              <Box sx={{ 
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'rgba(0,0,0,0.8)',
                color: 'white'
              }}>
                <Typography variant="body1">
                  Camera stream ready, attaching to display...
                </Typography>
              </Box>
            )}

            {!cameraReady && !stream && !loading && (
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
                  Camera not ready
                </Typography>
              </Box>
            )}
          </Box>
        )}

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
