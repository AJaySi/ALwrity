import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, DialogActions, 
  Button, Box, Typography, CircularProgress, Alert,
  Stack, Avatar, FormControl, FormLabel, RadioGroup, 
  FormControlLabel, Radio, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, Paper, IconButton,
  Tooltip, Chip
} from '@mui/material';
import { createAvatarVideoAsync } from '../../../../api/videoStudioApi';
import { useVideoGenerationPolling } from '../../../../hooks/usePolling';
import { fetchMediaBlobUrl } from '../../../../utils/fetchMediaBlobUrl';
import { VideoCameraFront, SkipNext, PlayArrow, InfoOutlined, Close as CloseIcon, HelpOutline, Refresh, RestartAlt, Undo } from '@mui/icons-material';
import { VideoGenerationLoader } from '../../../shared/VideoGenerationLoader';
import { OperationButton } from '../../../shared/OperationButton';

interface TestPersonaModalProps {
  open: boolean;
  onClose: () => void;
  avatarUrl: string;
  voiceUrl: string;
  onVideoGenerated?: (url: string | null) => void;
}

export const TestPersonaModal: React.FC<TestPersonaModalProps> = ({ 
  open, onClose, avatarUrl, voiceUrl, onVideoGenerated
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [model, setModel] = useState<'infinitetalk' | 'hunyuan-avatar'>('infinitetalk');
  const [showCapabilities, setShowCapabilities] = useState(false);
  const [avatarBlobUrl, setAvatarBlobUrl] = useState<string | null>(null);
  const STORAGE_KEY = 'test_persona_video_url';
  const STORAGE_BACKUP_KEY = 'test_persona_video_url_backup';
  
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      // Ensure we don't restore invalid string values
      return saved && saved !== 'undefined' && saved !== 'null' && saved.length > 0 ? saved : null;
    } catch (e) {
      console.warn('Failed to read video URL from localStorage', e);
      return null;
    }
  });

  const [archivedVideoUrl, setArchivedVideoUrl] = useState<string | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_BACKUP_KEY);
      return saved && saved !== 'undefined' && saved !== 'null' && saved.length > 0 ? saved : null;
    } catch { return null; }
  });

  // Persist generated video URL
  useEffect(() => {
    try {
      if (generatedVideoUrl) {
        localStorage.setItem(STORAGE_KEY, generatedVideoUrl);
      }
      if (onVideoGenerated) {
        onVideoGenerated(generatedVideoUrl);
      }
    } catch (e) {
      console.warn('Failed to save video URL to localStorage', e);
    }
  }, [generatedVideoUrl, onVideoGenerated]);

  // Persist archived video URL
  useEffect(() => {
    try {
      if (archivedVideoUrl) {
        localStorage.setItem(STORAGE_BACKUP_KEY, archivedVideoUrl);
      } else {
        localStorage.removeItem(STORAGE_BACKUP_KEY);
      }
    } catch (e) {
      console.warn('Failed to save archived video URL to localStorage', e);
    }
  }, [archivedVideoUrl]);

  const handleComplete = useCallback((res: any) => {
    setSuccess('Video generated successfully!');
    if (res?.video_url) {
      setGeneratedVideoUrl(res.video_url);
      setArchivedVideoUrl(null); // Clear archive on new generation
    }
    setLoading(false);
  }, []);

  const handleReDo = () => {
    if (generatedVideoUrl) {
      setArchivedVideoUrl(generatedVideoUrl);
    }
    setGeneratedVideoUrl(null);
    setSuccess(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const handleRestore = () => {
    if (archivedVideoUrl) {
      setGeneratedVideoUrl(archivedVideoUrl);
      setArchivedVideoUrl(null);
      setSuccess('Restored previous video');
    }
  };

  const handleError = useCallback((err: string) => {
    setError(`Generation failed: ${err}`);
    setLoading(false);
  }, []);

  const { 
    startPolling, 
    stopPolling, 
    isPolling 
  } = useVideoGenerationPolling({
    onComplete: handleComplete,
    onError: handleError
  });

  // Cleanup polling on unmount is handled by usePolling hook
  // The previous manual useEffect cleanup here was causing a race condition
  // where stopPolling was called immediately after startPolling due to dependency changes

  const operation = useMemo(() => ({
    provider: 'video',
    operation_type: 'avatar_video',
    actual_provider_name: 'alwrity',
    model: model,
  }), [model]);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setGeneratedVideoUrl(null);

    try {
      let avatarBlob: Blob;
      try {
        const avatarBlobUrl = await fetchMediaBlobUrl(avatarUrl);
        if (avatarBlobUrl) {
          avatarBlob = await fetch(avatarBlobUrl).then(r => r.blob());
        } else {
          avatarBlob = await fetch(avatarUrl).then(r => r.blob());
        }
      } catch {
        avatarBlob = await fetch(avatarUrl).then(r => r.blob());
      }

      let voiceBlob: Blob;
      try {
        const voiceBlobUrl = await fetchMediaBlobUrl(voiceUrl);
        if (voiceBlobUrl) {
          voiceBlob = await fetch(voiceBlobUrl).then(r => r.blob());
        } else {
          voiceBlob = await fetch(voiceUrl).then(r => r.blob());
        }
      } catch {
        voiceBlob = await fetch(voiceUrl).then(r => r.blob());
      }

      // 2. Create Files
      const avatarFile = new File([avatarBlob], "avatar.png", { type: avatarBlob.type });
      const voiceFile = new File([voiceBlob], "voice_sample.wav", { type: voiceBlob.type });

      // 3. Call API
      const resp = await createAvatarVideoAsync(avatarFile, voiceFile, '720p', model);
      
      // 4. Start polling
      if (resp.task_id) {
        startPolling(resp.task_id);
      } else {
        throw new Error("No task ID received from service");
      }
      
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Failed to start video generation");
      setLoading(false);
    }
  };

  const handleSkip = () => {
    onClose();
    // Attempt to focus the wizard continue button after modal closes
    setTimeout(() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const continueBtn = buttons.find(b => 
            b.textContent?.toLowerCase().includes('continue') || 
            b.textContent?.toLowerCase().includes('next')
        );
        if (continueBtn) {
            (continueBtn as HTMLElement).focus();
        }
    }, 100);
  };

  useEffect(() => {
    if (!avatarUrl) {
      setAvatarBlobUrl(null);
      return;
    }

    if (avatarUrl.startsWith('data:') || avatarUrl.startsWith('blob:')) {
      setAvatarBlobUrl(null);
      return;
    }

    const isInternal =
      avatarUrl.includes('/api/podcast/') ||
      avatarUrl.includes('/api/youtube/') ||
      avatarUrl.includes('/api/story/') ||
      (avatarUrl.startsWith('/') && !avatarUrl.startsWith('//'));

    if (!isInternal) {
      setAvatarBlobUrl(null);
      return;
    }

    let isMounted = true;
    const currentAvatarUrl = avatarUrl;

    const loadAvatarBlob = async () => {
      try {
        const blobUrl = await fetchMediaBlobUrl(currentAvatarUrl);

        if (!isMounted || avatarUrl !== currentAvatarUrl) {
          if (blobUrl && blobUrl.startsWith('blob:')) {
            URL.revokeObjectURL(blobUrl);
          }
          return;
        }

        setAvatarBlobUrl(prev => {
          if (prev && prev !== blobUrl && prev.startsWith('blob:')) {
            URL.revokeObjectURL(prev);
          }
          return blobUrl;
        });
      } catch {
        if (isMounted && avatarUrl === currentAvatarUrl) {
          setAvatarBlobUrl(null);
        }
      }
    };

    loadAvatarBlob();

    return () => {
      isMounted = false;
      setAvatarBlobUrl(prev => {
        if (prev && prev.startsWith('blob:')) {
          URL.revokeObjectURL(prev);
        }
        return null;
      });
    };
  }, [avatarUrl]);

  const CapabilitiesModal = () => (
    <Dialog 
        open={showCapabilities} 
        onClose={() => setShowCapabilities(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{ 
            sx: { 
                borderRadius: 3,
                bgcolor: '#ffffff !important', // Force light theme with !important
                color: '#1e293b !important',    // Force dark text
                backgroundImage: 'none !important', // Remove dark mode gradient
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
            } 
        }}
        sx={{
            '& .MuiBackdrop-root': {
                backgroundColor: 'rgba(15, 23, 42, 0.7)' // Darker backdrop for better contrast
            }
        }}
    >
       <DialogTitle sx={{ 
           display: 'flex', 
           justifyContent: 'space-between', 
           alignItems: 'center', 
           borderBottom: '1px solid #e2e8f0', 
           bgcolor: '#ffffff',
           color: '#0f172a',
           py: 2.5,
           px: 3
       }}>
          <Stack direction="row" alignItems="center" gap={1.5}>
             <Box sx={{ 
                 p: 1, 
                 borderRadius: 2, 
                 bgcolor: '#eff6ff',
                 color: '#2563eb',
                 display: 'flex' 
             }}>
                <VideoCameraFront fontSize="small" />
             </Box>
             <Typography variant="h6" fontWeight={700} sx={{ color: '#0f172a' }}>
                Alwrity Video Capabilities
             </Typography>
          </Stack>
          <IconButton 
            onClick={() => setShowCapabilities(false)} 
            sx={{ 
                color: '#64748b',
                '&:hover': { bgcolor: '#f1f5f9', color: '#0f172a' }
            }}
          >
            <CloseIcon />
          </IconButton>
       </DialogTitle>
       <DialogContent sx={{ pt: 4, px: 3, pb: 4, bgcolor: '#ffffff' }}>
          <Alert 
            severity="info" 
            icon={<InfoOutlined fontSize="small" />} 
            sx={{ 
                mb: 4, 
                bgcolor: '#eff6ff', 
                color: '#1e3a8a',
                border: '1px solid #dbeafe',
                '& .MuiAlert-icon': { color: '#2563eb' }
            }}
          >
             <Typography variant="body2" fontWeight={500}>
                These advanced models are available in the <strong>Creative Scenes</strong> studio. 
                The "Test Your Persona" feature currently uses specialized avatar models.
             </Typography>
          </Alert>
          
          <TableContainer 
            component={Paper} 
            variant="outlined" 
            sx={{ 
                borderRadius: 3, 
                overflow: 'hidden', 
                boxShadow: 'none', 
                border: '1px solid #e2e8f0',
                bgcolor: '#ffffff' 
            }}
          >
             <Table sx={{ minWidth: 650 }}>
                <TableHead>
                   <TableRow sx={{ bgcolor: '#f8fafc' }}>
                      <TableCell sx={{ color: '#475569', fontWeight: 700, py: 2 }}>Model</TableCell>
                      <TableCell sx={{ color: '#475569', fontWeight: 700, py: 2 }}>Type</TableCell>
                      <TableCell sx={{ color: '#475569', fontWeight: 700, py: 2 }}>Resolution</TableCell>
                      <TableCell sx={{ color: '#475569', fontWeight: 700, py: 2 }}>Duration</TableCell>
                   </TableRow>
                </TableHead>
                <TableBody>
                   <TableRow hover sx={{ '&:hover': { bgcolor: '#f8fafc' }, transition: 'background-color 0.2s' }}>
                      <TableCell sx={{ color: '#0f172a', py: 2.5 }}>
                          <Stack>
                              <Typography variant="subtitle2" fontWeight={700}>HunyuanVideo-1.5</Typography>
                              <Typography variant="caption" color="text.secondary">Tencent</Typography>
                          </Stack>
                      </TableCell>
                      <TableCell sx={{ color: '#334155' }}><Chip label="Text-to-Video" size="small" sx={{ bgcolor: '#eff6ff', color: '#2563eb', fontWeight: 600, borderRadius: 1.5 }} /></TableCell>
                      <TableCell sx={{ color: '#334155' }}>480p, 720p</TableCell>
                      <TableCell sx={{ color: '#334155' }}>5s, 8s, 10s</TableCell>
                   </TableRow>
                   <TableRow hover sx={{ '&:hover': { bgcolor: '#f8fafc' }, transition: 'background-color 0.2s' }}>
                      <TableCell sx={{ color: '#0f172a', py: 2.5 }}>
                          <Stack>
                              <Typography variant="subtitle2" fontWeight={700}>LTX-2 Pro</Typography>
                              <Typography variant="caption" color="text.secondary">Lightricks</Typography>
                          </Stack>
                      </TableCell>
                      <TableCell sx={{ color: '#334155' }}><Chip label="Text-to-Video" size="small" sx={{ bgcolor: '#eff6ff', color: '#2563eb', fontWeight: 600, borderRadius: 1.5 }} /></TableCell>
                      <TableCell sx={{ color: '#334155' }}>Fixed 1080p</TableCell>
                      <TableCell sx={{ color: '#334155' }}>6s, 8s, 10s</TableCell>
                   </TableRow>
                   <TableRow hover sx={{ '&:hover': { bgcolor: '#f8fafc' }, transition: 'background-color 0.2s' }}>
                      <TableCell sx={{ color: '#0f172a', py: 2.5 }}>
                          <Stack>
                              <Typography variant="subtitle2" fontWeight={700}>WAN 2.5</Typography>
                              <Typography variant="caption" color="text.secondary">Alibaba</Typography>
                          </Stack>
                      </TableCell>
                      <TableCell sx={{ color: '#334155' }}><Chip label="Image-to-Video" size="small" sx={{ bgcolor: '#f0fdf4', color: '#16a34a', fontWeight: 600, borderRadius: 1.5 }} /></TableCell>
                      <TableCell sx={{ color: '#334155' }}>480p, 720p, 1080p</TableCell>
                      <TableCell sx={{ color: '#334155' }}>5s</TableCell>
                   </TableRow>
                   <TableRow hover sx={{ '&:hover': { bgcolor: '#f8fafc' }, transition: 'background-color 0.2s' }}>
                      <TableCell sx={{ color: '#0f172a', py: 2.5 }}>
                          <Stack>
                              <Typography variant="subtitle2" fontWeight={700}>Kandinsky 5 Pro</Typography>
                              <Typography variant="caption" color="text.secondary">FusionBrain</Typography>
                          </Stack>
                      </TableCell>
                      <TableCell sx={{ color: '#334155' }}><Chip label="Image-to-Video" size="small" sx={{ bgcolor: '#f0fdf4', color: '#16a34a', fontWeight: 600, borderRadius: 1.5 }} /></TableCell>
                      <TableCell colSpan={2} sx={{ color: '#64748b', fontStyle: 'italic' }}>
                           Powered by WAN 2.5 architecture
                      </TableCell>
                   </TableRow>
                </TableBody>
             </Table>
          </TableContainer>
       </DialogContent>
       <DialogActions sx={{ p: 3, borderTop: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
          <Button 
            onClick={() => setShowCapabilities(false)} 
            variant="contained" 
            sx={{ 
                bgcolor: '#0f172a', 
                color: 'white',
                px: 4,
                py: 1,
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                '&:hover': { bgcolor: '#1e293b' }
            }}
          >
            Close
          </Button>
       </DialogActions>
    </Dialog>
  );

  return (
    <>
    <Dialog 
        open={open} 
        onClose={loading ? undefined : handleSkip} 
        maxWidth={false} // Disable default maxWidth to allow custom width
        PaperProps={{
            sx: { 
                borderRadius: 3,
                width: '70%',        // 70% screen width
                maxWidth: 'none',    // Override constraint
                bgcolor: '#ffffff',  // Force light theme
                color: '#1e293b',    // Force dark text
                backgroundImage: 'none'
            }
        }}
    >
      <DialogTitle sx={{ borderBottom: '1px solid #f1f5f9', bgcolor: '#ffffff', color: '#0f172a' }}>
        <Stack direction="row" alignItems="center" gap={1}>
            <VideoCameraFront color="primary" />
            <Typography variant="h6" fontWeight="bold">Test Your Persona</Typography>
        </Stack>
      </DialogTitle>
      <DialogContent sx={{ bgcolor: '#ffffff', color: '#334155', py: 4 }}>
         <Typography variant="body1" color="text.secondary" sx={{ mb: 4, textAlign: 'center', fontSize: '1.1rem' }}>
            Combine your new <strong>Brand Avatar</strong> and <strong>Voice Clone</strong> to generate a test intro video.
            <br />See how your persona comes to life before you start creating content!
         </Typography>

         {loading ? (
             <VideoGenerationLoader />
         ) : generatedVideoUrl ? (
             <Box sx={{ width: '100%', mt: 2 }}>
                 <Box sx={{ 
                     width: '100%', 
                     borderRadius: 3, 
                     overflow: 'hidden', 
                     boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
                     border: '1px solid #e2e8f0',
                     position: 'relative',
                     bgcolor: '#000'
                 }}>
                     <video controls src={generatedVideoUrl} style={{ width: '100%', display: 'block', maxHeight: '60vh' }} autoPlay />
                     
                     <Box sx={{ 
                         position: 'absolute', 
                         top: 16, 
                         right: 16, 
                         zIndex: 10 
                     }}>
                        <Button
                            variant="contained"
                            onClick={handleReDo}
                            startIcon={<RestartAlt />}
                            sx={{
                                background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                                color: 'white',
                                borderRadius: '50px',
                                px: 3,
                                py: 1,
                                textTransform: 'none',
                                fontWeight: 700,
                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                                '&:hover': {
                                    background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                                }
                            }}
                        >
                            ReDo
                        </Button>
                     </Box>
                 </Box>
                 
                 <Box sx={{ p: 2, mt: 2, bgcolor: '#f0fdf4', borderRadius: 2, border: '1px solid #dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                     <Typography variant="body2" color="#166534" fontWeight={600} align="center">
                         Video generated successfully! 
                     </Typography>
                     <Typography variant="body2" color="#166534">
                         Click "ReDo" to change settings or "Close" to finish.
                     </Typography>
                 </Box>
             </Box>
         ) : (
             <Stack direction={{ xs: 'column', md: 'row' }} spacing={4} alignItems="stretch" justifyContent="center">
                {/* Left Column: Previews */}
                <Stack spacing={3} flex={1} alignItems="center" sx={{ p: 3, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                    {/* Avatar Preview */}
                    <Box sx={{ position: 'relative' }}>
                        <Avatar 
                            src={avatarBlobUrl || avatarUrl} 
                            sx={{ width: 140, height: 140, border: '4px solid #ffffff', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} 
                        />
                        <Box sx={{ position: 'absolute', bottom: 0, right: 0, bgcolor: '#10b981', color: 'white', p: 0.5, borderRadius: '50%', border: '2px solid white' }}>
                            <VideoCameraFront fontSize="small" />
                        </Box>
                    </Box>
                    <Typography variant="subtitle2" fontWeight="bold" color="text.primary">Your Brand Avatar</Typography>
    
                    {/* Audio Preview */}
                    <Box sx={{ width: '100%', bgcolor: '#ffffff', p: 2, borderRadius: 2, border: '1px solid #e2e8f0' }}>
                        <Typography variant="caption" fontWeight="bold" sx={{ mb: 1, display: 'block', color: '#64748b' }}>
                            Voice Preview
                        </Typography>
                        <audio controls src={voiceUrl} style={{ width: '100%', height: 36 }} />
                    </Box>
                </Stack>
    
                {/* Right Column: Configuration */}
                <Stack spacing={3} flex={1}>
                    {/* Restore Option */}
                    {archivedVideoUrl && (
                        <Button
                            fullWidth
                            variant="outlined"
                            startIcon={<Undo />}
                            onClick={handleRestore}
                            sx={{ 
                                textTransform: 'none', 
                                fontWeight: 600,
                                borderStyle: 'dashed',
                                borderColor: '#3b82f6',
                                color: '#2563eb',
                                bgcolor: '#eff6ff',
                                '&:hover': { 
                                    borderStyle: 'solid',
                                    bgcolor: '#dbeafe'
                                }
                            }}
                        >
                            Restore Last Generated Video
                        </Button>
                    )}

                    {/* Model Selection */}
                    <Box sx={{ width: '100%', p: 3, border: '1px solid #e2e8f0', borderRadius: 2, bgcolor: '#ffffff' }}>
                        <FormControl component="fieldset" fullWidth>
                            <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 2 }}>
                                <FormLabel component="legend" sx={{ fontWeight: 'bold', fontSize: '1rem', color: '#0f172a' }}>
                                    Select Avatar Model
                                </FormLabel>
                                <Tooltip title="Choose the AI model that best fits your video duration needs. InfiniteTalk is recommended for most use cases.">
                                    <HelpOutline fontSize="small" color="action" sx={{ cursor: 'help' }} />
                                </Tooltip>
                            </Stack>
                            
                            <RadioGroup
                                aria-label="avatar-model"
                                name="avatar-model"
                                value={model}
                                onChange={(e) => setModel(e.target.value as any)}
                            >
                                <Tooltip title="Best for long-form content. Features natural head movements and lip-sync." placement="left" arrow>
                                    <FormControlLabel 
                                        value="infinitetalk" 
                                        control={<Radio size="small" />} 
                                        label={
                                            <Box>
                                                <Typography variant="body2" fontWeight={600} color="#0f172a">InfiniteTalk (Default)</Typography>
                                                <Typography variant="caption" color="text.secondary" display="block">Specialized for talking heads, up to 10 mins</Typography>
                                            </Box>
                                        } 
                                        sx={{ mb: 2, alignItems: 'flex-start', '&:hover': { bgcolor: '#f8fafc' }, p: 1, borderRadius: 1, ml: -1, width: '100%' }}
                                    />
                                </Tooltip>
                                
                                <Tooltip title="Alternative high-quality model, optimized for shorter clips." placement="left" arrow>
                                    <FormControlLabel 
                                        value="hunyuan-avatar" 
                                        control={<Radio size="small" />} 
                                        label={
                                            <Box>
                                                <Typography variant="body2" fontWeight={600} color="#0f172a">Hunyuan Avatar</Typography>
                                                <Typography variant="caption" color="text.secondary" display="block">Alternative model, supports up to 2 minutes</Typography>
                                            </Box>
                                        }
                                        sx={{ alignItems: 'flex-start', '&:hover': { bgcolor: '#f8fafc' }, p: 1, borderRadius: 1, ml: -1, width: '100%' }}
                                    />
                                </Tooltip>
                            </RadioGroup>
                        </FormControl>
                        
                        <Box sx={{ mt: 2, pt: 2, borderTop: '1px dashed #e2e8f0', display: 'flex', justifyContent: 'center' }}>
                            <Button 
                                size="small" 
                                startIcon={<InfoOutlined />} 
                                onClick={() => setShowCapabilities(true)}
                                sx={{ textTransform: 'none', color: 'primary.main', fontWeight: 500 }}
                            >
                                Know Alwrity Video Capabilities
                            </Button>
                        </Box>
                    </Box>
                </Stack>
              </Stack>
          )}

         {error && <Alert severity="error" sx={{ width: '100%', mt: 3 }}>{error}</Alert>}
         {success && !generatedVideoUrl && <Alert severity="success" sx={{ width: '100%', mt: 3 }}>{success}</Alert>}
      </DialogContent>
      <DialogActions sx={{ px: 4, pb: 4, pt: 2, bgcolor: '#ffffff', borderTop: '1px solid #f1f5f9' }}>
        <Button 
            onClick={handleSkip} 
            disabled={loading} 
            startIcon={generatedVideoUrl ? <CloseIcon /> : <SkipNext />}
            color="inherit"
            sx={{ textTransform: 'none', color: '#64748b' }}
        >
            {generatedVideoUrl ? "Close" : "Skip"}
        </Button>
        {!generatedVideoUrl && (
        <OperationButton 
            operation={operation}
            label={loading ? "Generating..." : "Generate Intro Video"}
            onClick={handleGenerate}
            disabled={loading || !!success}
            loading={loading}
            startIcon={<PlayArrow />}
            checkOnMount={true}
            sx={{ 
                background: 'linear-gradient(45deg, #7C3AED 0%, #EC4899 100%)',
                color: 'white',
                px: 4,
                py: 1,
                textTransform: 'none',
                fontWeight: 'bold',
                boxShadow: '0 4px 12px rgba(124, 58, 237, 0.3)',
                '&:hover': {
                    boxShadow: '0 6px 16px rgba(124, 58, 237, 0.4)',
                },
                // Override disabled style to keep it readable if just loading
                '&.Mui-disabled': {
                    color: 'rgba(255, 255, 255, 0.7)',
                    background: 'linear-gradient(45deg, #7C3AED 0%, #EC4899 100%)',
                    opacity: 0.7
                }
            }}
        />
        )}
      </DialogActions>
    </Dialog>
    <CapabilitiesModal />
    </>
  );
};
