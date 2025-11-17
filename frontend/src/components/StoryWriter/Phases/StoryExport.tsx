import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
  Divider,
  CircularProgress,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import DownloadIcon from '@mui/icons-material/Download';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { fetchMediaBlobUrl } from '../../../utils/fetchMediaBlobUrl';
import { triggerSubscriptionError } from '../../../api/client';
import SmartDisplayIcon from '@mui/icons-material/SmartDisplay';
import SceneVideoApproval from '../components/SceneVideoApproval';

interface StoryExportProps {
  state: ReturnType<typeof useStoryWriterState>;
}

const StoryExport: React.FC<StoryExportProps> = ({ state }) => {
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [videoMessage, setVideoMessage] = useState<string>('');
  const [videoBlobUrl, setVideoBlobUrl] = useState<string | null>(null);
  const [isGeneratingHdVideo, setIsGeneratingHdVideo] = useState(false);
  const [hdVideoProgress, setHdVideoProgress] = useState(0);
  const [hdVideoMessage, setHdVideoMessage] = useState<string>('');
  const [hdVideoPrompts, setHdVideoPrompts] = useState<Map<number, string>>(new Map()); // Store prompts by scene number
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Scene-by-scene approval state
  const [approvalModal, setApprovalModal] = useState<{
    open: boolean;
    sceneNumber: number;
    sceneTitle: string;
    videoUrl: string;
    promptUsed: string;
  } | null>(null);
  const [regeneratingScene, setRegeneratingScene] = useState<number | null>(null);
  
  // Keep track of the processing function for continuation
  const processSceneRef = useRef<((sceneIndex: number) => Promise<void>) | null>(null);

  const handleCopyToClipboard = () => {
    if (state.storyContent) {
      navigator.clipboard.writeText(state.storyContent);
    }
  };

  const handleDownload = () => {
    if (state.storyContent) {
      const blob = new Blob([state.storyContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `story-${Date.now()}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleGenerateVideo = async () => {
    if (!state.enableVideoNarration) {
      setError('Story video generation is disabled in Story Setup.');
      return;
    }
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }

    if (!state.sceneImages || state.sceneImages.size === 0) {
      setError('Please generate images for scenes first');
      return;
    }

    if (!state.sceneAudio || state.sceneAudio.size === 0) {
      setError('Please generate audio for scenes first');
      return;
    }

    setIsGeneratingVideo(true);
    setError(null);
    setVideoProgress(0);

    try {
      // Prepare image and audio URLs in scene order
      const imageUrls: string[] = [];
      const audioUrls: string[] = [];
      const scenes = state.outlineScenes;

      for (const scene of scenes) {
        const sceneNumber = scene.scene_number || scenes.indexOf(scene) + 1;
        const imageUrl = state.sceneImages?.get(sceneNumber);
        const audioUrl = state.sceneAudio?.get(sceneNumber);

        if (imageUrl && audioUrl) {
          imageUrls.push(imageUrl);
          audioUrls.push(audioUrl);
        } else {
          throw new Error(`Missing image or audio for scene ${sceneNumber}`);
        }
      }

      if (imageUrls.length !== scenes.length || audioUrls.length !== scenes.length) {
        throw new Error('Number of images and audio files must match number of scenes');
      }

      // Start async video generation
      const startRes = await storyWriterApi.generateStoryVideoAsync({
        scenes: scenes,
        image_urls: imageUrls,
        audio_urls: audioUrls,
        story_title: state.storySetting || 'Story',
        fps: state.videoFps,
        transition_duration: state.videoTransitionDuration,
      });

      // Poll task status
      const taskId = startRes.task_id;
      setVideoMessage(startRes.message || 'Starting video generation...');

      let done = false;
      while (!done) {
        await new Promise((r) => setTimeout(r, 1200));
        const status = await storyWriterApi.getTaskStatus(taskId);
        setVideoProgress(Math.round(status.progress ?? 0));
        if (status.message) setVideoMessage(status.message);
        if (status.status === 'completed') {
          done = true;
          const result = await storyWriterApi.getTaskResult(taskId);
          // result.video exists under result.video
          // @ts-ignore – result typing is StoryFullGenerationResponse; our async returns a dict
          const video = result.video || (result as any).video;
          const videoUrl = video?.video_url;
          if (!videoUrl) throw new Error('Video URL missing in result');
          state.setStoryVideo(videoUrl);
          // fetch blob for authenticated preview
          const blobUrl = await fetchMediaBlobUrl(videoUrl);
          setVideoBlobUrl(blobUrl);
          setVideoProgress(100);
          setVideoMessage('Video generation complete');
        state.setError(null);
          // Autoplay and fullscreen
          setTimeout(() => {
            const v = videoRef.current;
            if (v) {
              try { v.play().catch(() => {}); } catch {}
              try { if (v.requestFullscreen) v.requestFullscreen(); } catch {}
            }
          }, 300);
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Video generation failed');
        }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate video';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const handleDownloadVideo = async () => {
    if (state.storyVideo) {
      const blobUrl = await fetchMediaBlobUrl(state.storyVideo);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `story-video-${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    }
  };

  const handleGenerateHdVideo = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }

    const scenes = state.outlineScenes;
    const totalScenes = scenes.length;
    
    // Initialize HD videos map if not exists
    if (!state.sceneHdVideos) {
      state.setSceneHdVideos(new Map());
    }
    
    // Clear previous prompts
    setHdVideoPrompts(new Map());
    
    state.setHdVideoGenerationStatus('generating');
    setIsGeneratingHdVideo(true);
    setError(null);

    // Build story context for prompt enhancement
    const storyContext = {
      persona: state.persona,
      story_setting: state.storySetting,
      characters: state.characters,
      plot_elements: state.plotElements,
      writing_style: state.writingStyle,
      story_tone: state.storyTone,
      narrative_pov: state.narrativePOV,
      audience_age_group: state.audienceAgeGroup,
      content_rating: state.contentRating,
      premise: state.premise || '',
      outline: state.outline || '',
      story_content: state.storyContent || '',
    };

    // Iterate through scenes one at a time
    const processScene = async (sceneIndex: number): Promise<void> => {
      if (sceneIndex >= totalScenes) {
        // All scenes processed
        state.setHdVideoGenerationStatus('completed');
        setIsGeneratingHdVideo(false);
        setHdVideoProgress(100);
        setHdVideoMessage(`All ${totalScenes} scenes processed`);
        
        // Show completion message
        const approvedCount = state.sceneHdVideos?.size || 0;
        setHdVideoMessage(`HD video generation complete! ${approvedCount} of ${totalScenes} scenes approved.`);
        return;
      }

      const scene = scenes[sceneIndex];
      const sceneNumber = scene.scene_number || sceneIndex + 1;
      state.setCurrentHdSceneIndex(sceneIndex);
      
      setHdVideoProgress(Math.round((sceneIndex / totalScenes) * 100));
      setHdVideoMessage(`Generating HD video for Scene ${sceneNumber}...`);

      try {
        // Generate video for current scene
        const result = await storyWriterApi.generateHdVideoScene({
          scene_number: sceneNumber,
          scene_data: scene,
          story_context: storyContext,
          all_scenes: scenes,
          provider: 'huggingface',
          model: 'tencent/HunyuanVideo',
          num_frames: 50,
          guidance_scale: 7.5,
        });

        // Store prompt for this scene
        setHdVideoPrompts((prev) => {
          const newPrompts = new Map(prev);
          newPrompts.set(sceneNumber, result.prompt_used);
          return newPrompts;
        });

        // Show approval modal
        state.setHdVideoGenerationStatus('awaiting_approval');
        setApprovalModal({
          open: true,
          sceneNumber: sceneNumber,
          sceneTitle: scene.title || `Scene ${sceneNumber}`,
          videoUrl: result.video_url,
          promptUsed: result.prompt_used,
        });

      } catch (err: any) {
        // Check if this is a subscription error (429/402) and trigger global subscription modal
        const status = err?.response?.status;
        if (status === 429 || status === 402) {
          const handled = await triggerSubscriptionError(err);
          if (handled) {
            // Subscription modal is showing, stop processing scenes
            setIsGeneratingHdVideo(false);
            state.setHdVideoGenerationStatus('idle');
            return;
          }
        }
        
        const errorMessage = err.response?.data?.detail || err.message || `Failed to generate HD video for scene ${sceneNumber}`;
        setError(errorMessage);
        
        // On subscription error, stop processing. On other errors, continue to next scene.
        if (status !== 429 && status !== 402) {
          await processScene(sceneIndex + 1);
        } else {
          setIsGeneratingHdVideo(false);
          state.setHdVideoGenerationStatus('idle');
        }
      }
    };

    // Store processScene function in ref for continuation
    processSceneRef.current = processScene;
    
    // Start processing first scene
    await processScene(0);
  };

  // Handle approval modal actions
  const handleApprove = () => {
    if (!approvalModal) return;
    
    const sceneNumber = approvalModal.sceneNumber;
    const hdVideos = state.sceneHdVideos || new Map();
    hdVideos.set(sceneNumber, approvalModal.videoUrl);
    state.setSceneHdVideos(new Map(hdVideos));
    
    setApprovalModal(null);
    
    // Continue to next scene
    const currentIndex = state.currentHdSceneIndex;
    const scenes = state.outlineScenes || [];
    if (currentIndex + 1 < scenes.length && processSceneRef.current) {
      state.setHdVideoGenerationStatus('generating');
      processSceneRef.current(currentIndex + 1);
    } else {
      state.setHdVideoGenerationStatus('completed');
      setIsGeneratingHdVideo(false);
      const approvedCount = state.sceneHdVideos?.size || 0;
      setHdVideoMessage(`HD video generation complete! ${approvedCount} of ${scenes.length} scenes approved.`);
    }
  };

  const handleReject = () => {
    if (!approvalModal) return;
    
    // Skip scene and continue to next
    setApprovalModal(null);
    
    const currentIndex = state.currentHdSceneIndex;
    const scenes = state.outlineScenes || [];
    if (currentIndex + 1 < scenes.length && processSceneRef.current) {
      state.setHdVideoGenerationStatus('generating');
      processSceneRef.current(currentIndex + 1);
    } else {
      state.setHdVideoGenerationStatus('completed');
      setIsGeneratingHdVideo(false);
      const approvedCount = state.sceneHdVideos?.size || 0;
      setHdVideoMessage(`HD video generation complete! ${approvedCount} of ${scenes.length} scenes approved.`);
    }
  };

  const handleRegenerate = async () => {
    if (!approvalModal) return;
    
    const sceneNumber = approvalModal.sceneNumber;
    const scenes = state.outlineScenes || [];
    const sceneIndex = scenes.findIndex((s: any) => (s.scene_number || 0) === sceneNumber);
    const scene = scenes[sceneIndex];
    
    if (!scene) return;
    
    setRegeneratingScene(sceneNumber);
    
    try {
      const storyContext = {
        persona: state.persona,
        story_setting: state.storySetting,
        characters: state.characters,
        plot_elements: state.plotElements,
        writing_style: state.writingStyle,
        story_tone: state.storyTone,
        narrative_pov: state.narrativePOV,
        audience_age_group: state.audienceAgeGroup,
        content_rating: state.contentRating,
        premise: state.premise || '',
        outline: state.outline || '',
        story_content: state.storyContent || '',
      };

      const result = await storyWriterApi.generateHdVideoScene({
        scene_number: sceneNumber,
        scene_data: scene,
        story_context: storyContext,
        all_scenes: scenes,
        provider: 'huggingface',
        model: 'tencent/HunyuanVideo',
        num_frames: 50,
        guidance_scale: 7.5,
      });

      // Update prompt for this scene
      setHdVideoPrompts((prev) => {
        const newPrompts = new Map(prev);
        newPrompts.set(sceneNumber, result.prompt_used);
        return newPrompts;
      });

      // Update approval modal with new video
      setApprovalModal({
        open: true,
        sceneNumber: sceneNumber,
        sceneTitle: scene.title || `Scene ${sceneNumber}`,
        videoUrl: result.video_url,
        promptUsed: result.prompt_used,
      });
    } catch (err: any) {
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          // Subscription modal is showing, stop here
          setRegeneratingScene(null);
          return;
        }
      }
      
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to regenerate video';
      setError(errorMessage);
    } finally {
      setRegeneratingScene(null);
    }
  };

  return (
    <>
    <Paper 
      sx={{ 
        p: 4, 
        mt: 2,
        backgroundColor: '#F7F3E9', // Warm cream/parchment color
        color: '#2C2416', // Dark brown text for readability
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
      }}
    >
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600, color: '#1A1611' }}>
        Export Story
      </Typography>
      <Typography variant="body2" sx={{ mb: 4, color: '#5D4037' }}>
        Your story is complete! You can copy it to clipboard or download it as a text file.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!state.storyContent ? (
        <Alert severity="info">
          No story content available. Please complete the writing phase first.
        </Alert>
      ) : (
        <>
          {/* Story Summary */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
              Story Summary
            </Typography>
            <Box 
              sx={{ 
                p: 2, 
                borderRadius: 1,
                backgroundColor: '#FAF9F6', // Slightly lighter cream for summary box
              }}
            >
              <Typography variant="body2" sx={{ mb: 1, color: '#2C2416' }}>
                <strong>Setting:</strong> {state.storySetting || 'N/A'}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1, color: '#2C2416' }}>
                <strong>Characters:</strong> {state.characters || 'N/A'}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1, color: '#2C2416' }}>
                <strong>Style:</strong> {state.writingStyle} | <strong>Tone:</strong> {state.storyTone}
              </Typography>
              <Typography variant="body2" sx={{ color: '#2C2416' }}>
                <strong>POV:</strong> {state.narrativePOV} | <strong>Audience:</strong> {state.audienceAgeGroup}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Premise */}
          {state.premise && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
                Premise
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={state.premise}
                InputProps={{ readOnly: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#FFFFFF',
                    color: '#1A1611',
                    '& fieldset': {
                      borderColor: '#8D6E63',
                      borderWidth: '1.5px',
                    },
                  },
                  '& .MuiInputBase-input': {
                    color: '#1A1611',
                  },
                }}
              />
            </Box>
          )}

          {/* Outline */}
          {state.outline && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
                Outline
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                value={state.outline}
                InputProps={{ readOnly: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#FFFFFF',
                    color: '#1A1611',
                    '& fieldset': {
                      borderColor: '#8D6E63',
                      borderWidth: '1.5px',
                    },
                  },
                  '& .MuiInputBase-input': {
                    color: '#1A1611',
                  },
                }}
              />
            </Box>
          )}

          {/* Story Content */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
              Complete Story
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={20}
              value={state.storyContent}
              InputProps={{ readOnly: true }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#FFFFFF',
                  color: '#1A1611',
                  '& fieldset': {
                    borderColor: '#8D6E63',
                    borderWidth: '1.5px',
                  },
                },
                '& .MuiInputBase-input': {
                  color: '#1A1611',
                },
              }}
            />
          </Box>

          {/* Video Generation */}
          {state.isOutlineStructured && state.outlineScenes && (
            state.enableVideoNarration ? (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
                Video Generation
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                Generate a video from your story scenes with images and audio narration.
                {(!state.sceneImages || state.sceneImages.size === 0) && ' Generate images first.'}
                {(!state.sceneAudio || state.sceneAudio.size === 0) && ' Generate audio first.'}
              </Alert>
              
              {isGeneratingVideo && (
                <Box sx={{ mb: 2 }}>
                  <LinearProgress variant="determinate" value={videoProgress} sx={{ mb: 1 }} />
                  <Typography variant="body2" sx={{ color: '#5D4037' }}>
                    {videoMessage || 'Generating video...'} {videoProgress}%
                  </Typography>
                </Box>
              )}

              {state.storyVideo && (
                <Box sx={{ mb: 2 }}>
                  <video
                    ref={videoRef}
                    controls
                    src={videoBlobUrl ?? undefined}
                    style={{ width: '100%', maxHeight: '500px' }}
                  >
                    Your browser does not support the video element.
                  </video>
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#5D4037' }}>
                    Generated story video
                  </Typography>
                  <Box sx={{ mt: 1, display: 'flex', gap: 1, flexDirection: 'column' }}>
                    <Tooltip
                      title={
                        <Box sx={{ p: 1 }}>
                          <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                            Generate HD Animation with AI
                          </Typography>
                          <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                            Upgrade this storyboard into a high‑definition AI animation using Hugging Face text‑to‑video models.
                            Your draft was generated affordably (images + narration). This premium option uses an AI model to render motion.
                          </Typography>
                          <Typography variant="caption" sx={{ display: 'block', mb: 0.5, fontWeight: 600 }}>
                            Recommended models:
                          </Typography>
                          <Typography variant="caption" component="div" sx={{ display: 'block', mb: 1 }}>
                            • tencent/HunyuanVideo<br />
                            • Lightricks/LTX-Video<br />
                            • Lightricks/LTX-Video-0.9.8-13B-distilled
                          </Typography>
                          <Typography variant="caption" sx={{ display: 'block', fontStyle: 'italic' }}>
                            This will generate HD videos for each scene one at a time. You'll review and approve each scene before the next one is generated.
                          </Typography>
                        </Box>
                      }
                      arrow
                      placement="top"
                    >
                      <Button
                        variant="contained"
                        startIcon={<SmartDisplayIcon />}
                        onClick={handleGenerateHdVideo}
                        disabled={isGeneratingHdVideo || state.hdVideoGenerationStatus === 'awaiting_approval'}
                      >
                        {isGeneratingHdVideo || state.hdVideoGenerationStatus === 'awaiting_approval' 
                          ? 'Generating HD Animation...' 
                          : 'Generate HD Animation with AI'}
                      </Button>
                    </Tooltip>
                    
                    {/* Show progress and prompts during generation */}
                    {(isGeneratingHdVideo || state.hdVideoGenerationStatus === 'generating' || state.hdVideoGenerationStatus === 'awaiting_approval') && (
                      <Box sx={{ mt: 2, p: 2, backgroundColor: '#FAF9F6', borderRadius: 1, border: '1px solid #E0DCD4' }}>
                        <LinearProgress variant="determinate" value={hdVideoProgress} sx={{ mb: 1 }} />
                        <Typography variant="body2" sx={{ color: '#5D4037', fontWeight: 500, mb: 1 }}>
                          {hdVideoMessage || 'Generating HD video...'} {hdVideoProgress}%
                        </Typography>
                        {state.hdVideoGenerationStatus === 'awaiting_approval' && (
                          <Typography variant="body2" sx={{ color: '#1976d2', display: 'block', mb: 1, fontWeight: 500 }}>
                            ⏸ Awaiting your approval for Scene {state.currentHdSceneIndex + 1} of {state.outlineScenes?.length || 0}
                          </Typography>
                        )}
                        {state.hdVideoGenerationStatus === 'generating' && (
                          <Typography variant="body2" sx={{ color: '#5D4037', display: 'block', mb: 1 }}>
                            Processing Scene {state.currentHdSceneIndex + 1} of {state.outlineScenes?.length || 0}...
                          </Typography>
                        )}
                        {state.sceneHdVideos && state.sceneHdVideos.size > 0 && (
                          <Typography variant="caption" sx={{ color: '#4caf50', display: 'block', mb: 1, fontWeight: 500 }}>
                            ✓ {state.sceneHdVideos.size} of {state.outlineScenes?.length || 0} scenes approved
                          </Typography>
                        )}
                        
                        {/* Display prompts for completed scenes */}
                        {hdVideoPrompts.size > 0 && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" sx={{ color: '#1A1611', mb: 1, fontWeight: 600 }}>
                              Generated Prompts:
                            </Typography>
                            {Array.from(hdVideoPrompts.entries())
                              .sort(([a], [b]) => a - b)
                              .map(([sceneNum, prompt]) => (
                                <Box key={sceneNum} sx={{ mb: 2, p: 1.5, backgroundColor: '#fff', borderRadius: 1, border: '1px solid #E0DCD4' }}>
                                  <Typography variant="caption" sx={{ color: '#5D4037', fontWeight: 600, display: 'block', mb: 0.5 }}>
                                    Scene {sceneNum}:
                                  </Typography>
                                  <Typography 
                                    variant="caption" 
                                    sx={{ 
                                      color: '#2C2416', 
                                      fontFamily: 'monospace',
                                      fontSize: '0.75rem',
                                      whiteSpace: 'pre-wrap',
                                      wordBreak: 'break-word',
                                      display: 'block',
                                    }}
                                  >
                                    {prompt.length > 200 ? `${prompt.substring(0, 200)}...` : prompt}
                                  </Typography>
                                </Box>
                              ))}
                          </Box>
                        )}
                      </Box>
                    )}
                    
                    {state.hdVideoGenerationStatus === 'completed' && (
                      <Alert severity="success" sx={{ mt: 2 }}>
                        HD video generation complete! {state.sceneHdVideos?.size || 0} of {state.outlineScenes?.length || 0} scenes were approved.
                      </Alert>
                    )}
                  </Box>
                </Box>
              )}

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<VideoLibraryIcon />}
                  onClick={handleGenerateVideo}
                  disabled={
                    isGeneratingVideo ||
                    !state.outlineScenes ||
                    !state.sceneImages ||
                    state.sceneImages.size === 0 ||
                    !state.sceneAudio ||
                    state.sceneAudio.size === 0
                  }
                >
                  {isGeneratingVideo ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Generating Video...
                    </>
                  ) : (
                    'Generate Video'
                  )}
                </Button>
                {state.storyVideo && (
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownloadVideo}
                  >
                    Download Video
                  </Button>
                )}
              </Box>
            </Box>
            ) : (
              <Alert severity="info" sx={{ mb: 4 }}>
                Story video generation is disabled in Story Setup. Enable it to create narrated videos.
              </Alert>
            )
          )}

          <Divider sx={{ my: 3 }} />

          {/* Export Actions */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
            <Button variant="outlined" onClick={handleCopyToClipboard}>
              Copy to Clipboard
            </Button>
            <Button variant="contained" onClick={handleDownload}>
              Download as Text File
            </Button>
          </Box>
        </>
      )}
    </Paper>
    
    {/* Scene Video Approval Modal */}
    {approvalModal && state.outlineScenes && (
      <SceneVideoApproval
        open={approvalModal.open}
        sceneNumber={approvalModal.sceneNumber}
        sceneTitle={approvalModal.sceneTitle}
        totalScenes={state.outlineScenes.length}
        videoUrl={approvalModal.videoUrl}
        promptUsed={approvalModal.promptUsed}
        onApprove={handleApprove}
        onReject={handleReject}
        onRegenerate={handleRegenerate}
        isRegenerating={regeneratingScene === approvalModal.sceneNumber}
        onClose={() => {
          if (!isGeneratingHdVideo && !regeneratingScene) {
            setApprovalModal(null);
            state.setHdVideoGenerationStatus('paused');
          }
        }}
      />
    )}
    </>
  );
};

export default StoryExport;
