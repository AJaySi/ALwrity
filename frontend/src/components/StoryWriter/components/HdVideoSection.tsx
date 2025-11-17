import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import SmartDisplayIcon from '@mui/icons-material/SmartDisplay';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../api/client';
import SceneVideoApproval from './SceneVideoApproval';

// Simple logger for frontend
const logger = {
  error: (message: string, ...args: any[]) => console.error(`[HdVideoSection] ${message}`, ...args),
  warn: (message: string, ...args: any[]) => console.warn(`[HdVideoSection] ${message}`, ...args),
  info: (message: string, ...args: any[]) => console.info(`[HdVideoSection] ${message}`, ...args),
};

interface HdVideoSectionProps {
  state: ReturnType<typeof useStoryWriterState>;
  error: string | null;
  onError: (error: string | null) => void;
}

export const HdVideoSection: React.FC<HdVideoSectionProps> = ({ state, onError }) => {
  const [isGeneratingHdVideo, setIsGeneratingHdVideo] = useState(false);
  const [hdVideoProgress, setHdVideoProgress] = useState(0);
  const [hdVideoMessage, setHdVideoMessage] = useState<string>('');
  const [hdVideoPrompts, setHdVideoPrompts] = useState<Map<number, string>>(new Map());
  
  const [approvalModal, setApprovalModal] = useState<{
    open: boolean;
    sceneNumber: number;
    sceneTitle: string;
    videoUrl: string;
    promptUsed: string;
  } | null>(null);
  const [regeneratingScene, setRegeneratingScene] = useState<number | null>(null);
  
  const processSceneRef = useRef<((sceneIndex: number) => Promise<void>) | null>(null);

  const handleGenerateHdVideo = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      onError('Please generate a structured outline first');
      return;
    }

    const scenes = state.outlineScenes;
    const totalScenes = scenes.length;
    
    if (!state.sceneHdVideos) {
      state.setSceneHdVideos(new Map());
    }
    
    setHdVideoPrompts(new Map());
    state.setHdVideoGenerationStatus('generating');
    setIsGeneratingHdVideo(true);
    onError(null);

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

    const processScene = async (sceneIndex: number): Promise<void> => {
      if (sceneIndex >= totalScenes) {
        state.setHdVideoGenerationStatus('completed');
        setIsGeneratingHdVideo(false);
        setHdVideoProgress(100);
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
        const sceneImageUrl = state.sceneImages?.get(sceneNumber);

        const result = await storyWriterApi.generateHdVideoScene({
          scene_number: sceneNumber,
          scene_data: scene,
          story_context: storyContext,
          all_scenes: scenes,
          scene_image_url: sceneImageUrl,
          provider: 'huggingface',
          model: 'tencent/HunyuanVideo',
          num_frames: 50,
          guidance_scale: 7.5,
        });

        setHdVideoPrompts((prev) => {
          const newPrompts = new Map(prev);
          newPrompts.set(sceneNumber, result.prompt_used);
          return newPrompts;
        });

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
        
        // Extract error message as string (handle both string and object responses)
        let errorMessage: string;
        if (err.response?.data?.detail) {
          const detail = err.response.data.detail;
          if (typeof detail === 'string') {
            errorMessage = detail;
          } else if (typeof detail === 'object' && detail !== null) {
            // Handle object response like {error: "...", message: "..."}
            errorMessage = detail.message || detail.error || JSON.stringify(detail);
          } else {
            errorMessage = String(detail);
          }
        } else {
          errorMessage = err.message || `Failed to generate HD video for scene ${sceneNumber}`;
        }
        onError(errorMessage);
        
        // CRITICAL: Stop processing on ANY error to prevent wasting money on expensive video API calls
        // This is an expensive operation ($0.40/video) - don't continue if there's an error
        // Only retry/continue if the user explicitly requests it
        logger.error(`[HdVideoSection] Video generation failed for scene ${sceneNumber}: ${errorMessage}`);
        logger.error(`[HdVideoSection] Stopping video generation to prevent wasted API calls`);
        
        setIsGeneratingHdVideo(false);
        state.setHdVideoGenerationStatus('idle');
        
        // Don't continue to next scene - stop immediately to save money
        return;
      }
    };

    processSceneRef.current = processScene;
    await processScene(0);
  };

  const handleApprove = () => {
    if (!approvalModal) return;
    
    const sceneNumber = approvalModal.sceneNumber;
    const hdVideos = state.sceneHdVideos || new Map();
    hdVideos.set(sceneNumber, approvalModal.videoUrl);
    state.setSceneHdVideos(new Map(hdVideos));
    
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

  const handleReject = () => {
    if (!approvalModal) return;
    
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

      const sceneImageUrl = state.sceneImages?.get(sceneNumber);

      const result = await storyWriterApi.generateHdVideoScene({
        scene_number: sceneNumber,
        scene_data: scene,
        story_context: storyContext,
        all_scenes: scenes,
        scene_image_url: sceneImageUrl,
        provider: 'huggingface',
        model: 'tencent/HunyuanVideo',
        num_frames: 50,
        guidance_scale: 7.5,
      });

      setHdVideoPrompts((prev) => {
        const newPrompts = new Map(prev);
        newPrompts.set(sceneNumber, result.prompt_used);
        return newPrompts;
      });

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
      
      // Extract error message as string (handle both string and object responses)
      let errorMessage: string;
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (typeof detail === 'object' && detail !== null) {
          // Handle object response like {error: "...", message: "..."}
          errorMessage = detail.message || detail.error || JSON.stringify(detail);
        } else {
          errorMessage = String(detail);
        }
      } else {
        errorMessage = err.message || 'Failed to regenerate video';
      }
      onError(errorMessage);
    } finally {
      setRegeneratingScene(null);
    }
  };

  return (
    <>
      <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 1 }}>
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
          <span style={{ display: 'inline-flex' }}>
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
          </span>
        </Tooltip>
        
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

