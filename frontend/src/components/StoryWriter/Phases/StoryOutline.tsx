import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Snackbar,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import GlobalStyles from '@mui/material/GlobalStyles';
import ImageIcon from '@mui/icons-material/Image';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { motion, AnimatePresence } from 'framer-motion';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { aiApiClient } from '../../../api/client';
import OutlineHoverActions from './StoryOutlineParts/OutlineHoverActions';
import EditSectionModal from './StoryOutlineParts/EditSectionModal';
import { leftPageVariants, rightPageVariants } from './StoryOutlineParts/pageVariants';
import { outlineActionButtonSx, primaryButtonSx } from './StoryOutlineParts/buttonStyles';
import BookPages from './StoryOutlineParts/BookPages';
import OutlineActionsBar from './StoryOutlineParts/OutlineActionsBar';
import ImageEditModal from './StoryOutlineParts/ImageEditModal';
import AudioScriptModal from './StoryOutlineParts/AudioScriptModal';
import CharactersModal from './StoryOutlineParts/CharactersModal';
import KeyEventsModal from './StoryOutlineParts/KeyEventsModal';
import TitleEditModal from './StoryOutlineParts/TitleEditModal';

const MotionBox = motion(Box);

// styles imported

interface StoryOutlineProps {
  state: ReturnType<typeof useStoryWriterState>;
  onNext: () => void;
}

const StoryOutline: React.FC<StoryOutlineProps> = ({ state, onNext }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGeneratingImages, setIsGeneratingImages] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentSceneIndex, setCurrentSceneIndex] = useState(0);
  const [pageDirection, setPageDirection] = useState(0);
  const [imageLoadError, setImageLoadError] = useState<Set<number>>(new Set());
  const [imageBlobUrls, setImageBlobUrls] = useState<Map<number, string>>(new Map());
  const [audioBlobUrls, setAudioBlobUrls] = useState<Map<number, string>>(new Map());
  const [audioLoadError, setAudioLoadError] = useState<Set<number>>(new Set());
  const [outlineToastOpen, setOutlineToastOpen] = useState(false);
  const lastToastSceneCount = useRef<number | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editText, setEditText] = useState<string>('');
  const [aiFeedback, setAiFeedback] = useState<string>('');
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [isRegeneratingSceneImage, setIsRegeneratingSceneImage] = useState<boolean>(false);
  const [isRegeneratingSceneAudio, setIsRegeneratingSceneAudio] = useState<boolean>(false);
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);
  const [imagePromptDraft, setImagePromptDraft] = useState('');
  const [isAudioModalOpen, setIsAudioModalOpen] = useState(false);
  const [audioScriptDraft, setAudioScriptDraft] = useState('');
  const [isCharactersModalOpen, setIsCharactersModalOpen] = useState(false);
  const [isKeyEventsModalOpen, setIsKeyEventsModalOpen] = useState(false);
  const [isTitleModalOpen, setIsTitleModalOpen] = useState(false);
  const [titleDraft, setTitleDraft] = useState('');
  
  // Use state from hook instead of local state
  const sceneImages = state.sceneImages || new Map<number, string>();
  const sceneAudio = state.sceneAudio || new Map<number, string>();

  const scenes = state.outlineScenes || [];
  const sceneCount = scenes.length;
  const hasScenes = state.isOutlineStructured && scenes.length > 0;
  const hasOutlineScenes = Boolean(state.outlineScenes && state.outlineScenes.length > 0);

  // removed old accordion renderer (unused)

  useEffect(() => {
    if (state.isOutlineStructured && sceneCount > 0 && sceneCount !== lastToastSceneCount.current) {
      setOutlineToastOpen(true);
      lastToastSceneCount.current = sceneCount;
    }
  }, [state.isOutlineStructured, sceneCount]);

  useEffect(() => {
    if (hasScenes) {
      setCurrentSceneIndex(0);
      setPageDirection(0);
    }
  }, [hasScenes]);

  const currentScene = hasScenes ? scenes[currentSceneIndex] : null;
  const canGoPrev = currentSceneIndex > 0;
  const canGoNext = hasScenes ? currentSceneIndex < scenes.length - 1 : false;
  
  // Get the current scene's image URL
  const currentSceneNumber = currentScene?.scene_number || currentSceneIndex + 1;
  const currentSceneImageUrl = sceneImages.get(currentSceneNumber);
  const hasImageLoadError = imageLoadError.has(currentSceneNumber);
  const currentSceneAudioUrl = sceneAudio.get(currentSceneNumber);
  const hasAudioLoadError = audioLoadError.has(currentSceneNumber);
  
  // Fetch image as blob with authentication
  useEffect(() => {
    if (!currentSceneImageUrl || hasImageLoadError || imageBlobUrls.has(currentSceneNumber)) {
      return;
    }
    
    const loadImage = async () => {
      try {
        // Use relative URL path directly (aiApiClient will add base URL and auth)
        const imageUrl = currentSceneImageUrl.startsWith('/') 
          ? currentSceneImageUrl 
          : `/${currentSceneImageUrl}`;
        // Use aiApiClient to get authenticated response with blob
        const response = await aiApiClient.get(imageUrl, {
          responseType: 'blob',
        });
        
        const blob = response.data;
        const blobUrl = URL.createObjectURL(blob);
        
        setImageBlobUrls((prev) => {
          const next = new Map(prev);
          next.set(currentSceneNumber, blobUrl);
          return next;
        });
      } catch (err) {
        console.error('Failed to load image:', err);
        setImageLoadError((prev) => new Set(prev).add(currentSceneNumber));
      }
    };
    
    loadImage();
  }, [currentSceneNumber, currentSceneImageUrl, hasImageLoadError]);
  
  // Cleanup blob URLs when component unmounts or scenes change
  useEffect(() => {
    return () => {
      // Revoke all blob URLs on unmount
      imageBlobUrls.forEach((blobUrl) => {
        URL.revokeObjectURL(blobUrl);
      });
      audioBlobUrls.forEach((blobUrl) => {
        URL.revokeObjectURL(blobUrl);
      });
    };
  }, []);
  
  const currentSceneImageFullUrl = imageBlobUrls.get(currentSceneNumber) || null;
  const currentSceneAudioFullUrl = audioBlobUrls.get(currentSceneNumber) || null;
  
  // Reset image load error when scene changes
  useEffect(() => {
    setImageLoadError((prev) => {
      const next = new Set(prev);
      next.delete(currentSceneNumber);
      return next;
    });
    setAudioLoadError((prev) => {
      const next = new Set(prev);
      next.delete(currentSceneNumber);
      return next;
    });
  }, [currentSceneNumber]);

  useEffect(() => {
    if (state.enableNarration) {
      return;
    }
    setAudioBlobUrls((prev) => {
      prev.forEach((url) => URL.revokeObjectURL(url));
      return new Map();
    });
    setAudioLoadError(new Set());
  }, [state.enableNarration]);

  // Fetch audio as blob for current scene
  useEffect(() => {
    if (!state.enableNarration) {
      return;
    }
    if (!currentSceneAudioUrl || !sceneAudio.has(currentSceneNumber)) {
      return;
    }
    if (currentSceneAudioFullUrl || hasAudioLoadError) {
      return;
    }

    const loadAudio = async () => {
      try {
        const audioPath = currentSceneAudioUrl.startsWith('/')
          ? currentSceneAudioUrl
          : `/${currentSceneAudioUrl}`;
        const response = await aiApiClient.get(audioPath, {
          responseType: 'blob',
        });
        const blob = response.data;
        const blobUrl = URL.createObjectURL(blob);

        setAudioBlobUrls((prev) => {
          const next = new Map(prev);
          const existing = next.get(currentSceneNumber);
          if (existing) {
            URL.revokeObjectURL(existing);
          }
          next.set(currentSceneNumber, blobUrl);
          return next;
        });
      } catch (err) {
        console.error('Failed to load audio:', err);
        setAudioLoadError((prev) => new Set(prev).add(currentSceneNumber));
      }
    };

    loadAudio();
  }, [currentSceneAudioUrl, currentSceneNumber, currentSceneAudioFullUrl, hasAudioLoadError, sceneAudio]);

  const handlePrevScene = () => {
    if (canGoPrev) {
      setPageDirection(-1);
      setCurrentSceneIndex((prev) => prev - 1);
    }
  };

  const handleNextScene = () => {
    if (canGoNext) {
      setPageDirection(1);
      setCurrentSceneIndex((prev) => prev + 1);
    }
  };

  const openEditModal = () => {
    setEditText(currentScene?.description || '');
    setAiFeedback('');
    setAiSuggestions([]);
    setIsEditModalOpen(true);
  };

  const openImageModal = () => {
    setImagePromptDraft(currentScene?.image_prompt || '');
    setIsImageModalOpen(true);
  };

  const openAudioModal = () => {
    setAudioScriptDraft(currentScene?.audio_narration || '');
    setIsAudioModalOpen(true);
  };
  const openCharactersModal = () => {
    setIsCharactersModalOpen(true);
  };
  const openKeyEventsModal = () => {
    setIsKeyEventsModalOpen(true);
  };
  const openTitleModal = () => {
    setTitleDraft(currentScene?.title || '');
    setIsTitleModalOpen(true);
  };

  const handleSaveUpdatedSection = () => {
    if (!hasScenes || !currentScene) {
      setIsEditModalOpen(false);
      return;
    }
    const updatedScenes = [...scenes];
    const idx = currentSceneIndex;
    const original = updatedScenes[idx];
    updatedScenes[idx] = {
      ...original,
      description: editText,
    };
    (state.setOutlineScenes as (s: any[] | null) => void)(updatedScenes);
    const formattedOutline = updatedScenes
      .map((scene, idx2) => `Scene ${scene.scene_number || idx2 + 1}: ${scene.title}\n${scene.description}`)
      .join('\n\n');
    state.setOutline(formattedOutline);
    setIsEditModalOpen(false);
  };

  const handleGenerateAISuggestions = async () => {
    setAiLoading(true);
    try {
      const base = (editText || currentScene?.description || '').trim();
      const suggestion1 = `${base}\n\n[Variant A] Improved pacing and clarity, preserving key events.`;
      const suggestion2 = `${base}\n\n[Variant B] Richer sensory details and stronger character emotion.`;
      setAiSuggestions([suggestion1, suggestion2]);
    } finally {
      setAiLoading(false);
    }
  };

  const applySuggestion = (index: number) => {
    const chosen = aiSuggestions[index];
    if (chosen) {
      setEditText(chosen);
    }
  };

  const handleOutlineToastClose = (_?: unknown, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setOutlineToastOpen(false);
  };

  const handleGenerateOutline = async () => {
    if (!state.premise) {
      setError('Please generate a premise first');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request = state.getRequest();
      const response = await storyWriterApi.generateOutline(state.premise, request);
      
      if (response.success && response.outline) {
        // Handle structured outline (scenes) or plain text outline
        if (response.is_structured && Array.isArray(response.outline)) {
          // Structured outline with scenes
          const scenes = response.outline as any[]; // Assuming StoryScene is any[]
          state.setOutlineScenes(scenes);
          state.setIsOutlineStructured(true);
          // Also store as formatted text for backward compatibility
          const formattedOutline = scenes.map((scene, idx) => 
            `Scene ${scene.scene_number || idx + 1}: ${scene.title}\n${scene.description}`
          ).join('\n\n');
          state.setOutline(formattedOutline);
        } else {
          // Plain text outline
          state.setOutline(typeof response.outline === 'string' ? response.outline : String(response.outline));
          state.setOutlineScenes(null);
          state.setIsOutlineStructured(false);
        }
        state.setError(null);
      } else {
        throw new Error(typeof response.outline === 'string' ? response.outline : 'Failed to generate outline');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate outline';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleContinue = () => {
    if (state.outline || state.outlineScenes) {
      onNext();
    }
  };

  const handleGenerateImages = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }
    if (!state.enableIllustration) {
      setError('Illustration feature is disabled in Story Setup.');
      return;
    }

    setIsGeneratingImages(true);
    setError(null);

    try {
      const response = await storyWriterApi.generateSceneImages({
        scenes: state.outlineScenes,
        provider: state.imageProvider || undefined,
        width: state.imageWidth,
        height: state.imageHeight,
        model: state.imageModel || undefined,
      });
      
      if (response.success && response.images) {
        // Store image URLs by scene number
        const imagesMap = new Map<number, string>();
        response.images.forEach((image) => {
          if (image.image_url && !image.error) {
            imagesMap.set(image.scene_number, image.image_url);
          }
        });
        state.setSceneImages(imagesMap);
        state.setError(null);
      } else {
        throw new Error('Failed to generate images');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate images';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingImages(false);
    }
  };

  const handleGenerateAudio = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }
    if (!state.enableNarration) {
      setError('Narration feature is disabled in Story Setup.');
      return;
    }

    setIsGeneratingAudio(true);
    setError(null);

    try {
      const response = await storyWriterApi.generateSceneAudio({
        scenes: state.outlineScenes,
        provider: state.audioProvider,
        lang: state.audioLang,
        slow: state.audioSlow,
        rate: state.audioRate,
      });
      
      if (response.success && response.audio_files) {
        // Store audio URLs by scene number
        const audioMap = new Map<number, string>();
        response.audio_files.forEach((audio) => {
          if (audio.audio_url && !audio.error) {
            audioMap.set(audio.scene_number, audio.audio_url);
          }
        });
        state.setSceneAudio(audioMap);
        state.setError(null);
      } else {
        throw new Error('Failed to generate audio');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate audio';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const handleRegenerateCurrentSceneImage = async () => {
    if (!hasScenes || !currentScene) return;
    setIsRegeneratingSceneImage(true);
    try {
      const resp = await storyWriterApi.generateSceneImages({
        scenes: [currentScene],
        provider: state.imageProvider || undefined,
        width: state.imageWidth,
        height: state.imageHeight,
        model: state.imageModel || undefined,
      });
      if (resp.success && resp.images && resp.images.length > 0) {
        const img = resp.images[0];
        const sceneNum = currentScene.scene_number || currentSceneIndex + 1;
        const nextMap = new Map(state.sceneImages || []);
        nextMap.set(sceneNum, img.image_url);
        state.setSceneImages(nextMap);
      }
    } catch (e) {
      console.warn('Failed to regenerate image for current scene', e);
    } finally {
      setIsRegeneratingSceneImage(false);
    }
  };

  const handleRegenerateCurrentSceneAudio = async () => {
    if (!hasScenes || !currentScene) return;
    if (!state.enableNarration) return;
    setIsRegeneratingSceneAudio(true);
    try {
      const resp = await storyWriterApi.generateSceneAudio({
        scenes: [currentScene],
        provider: state.audioProvider,
        lang: state.audioLang,
        slow: state.audioSlow,
        rate: state.audioRate,
      });
      if (resp.success && resp.audio_files && resp.audio_files.length > 0) {
        const au = resp.audio_files[0];
        const sceneNum = currentScene.scene_number || currentSceneIndex + 1;
        const nextMap = new Map(state.sceneAudio || []);
        nextMap.set(sceneNum, au.audio_url);
        state.setSceneAudio(nextMap);
      }
    } catch (e) {
      console.warn('Failed to regenerate audio for current scene', e);
    } finally {
      setIsRegeneratingSceneAudio(false);
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <GlobalStyles
        styles={{
          '.tw-shadow-book': {
            boxShadow: '0 36px 80px rgba(45, 30, 15, 0.35)',
          },
          '.tw-rounded-book': {
            borderRadius: '20px',
          },
          '.tw-page-accent': {
            background: 'linear-gradient(120deg, #f9e6c8, #f2d8b4)',
          },
        }}
      />
      <Snackbar
        open={outlineToastOpen}
        autoHideDuration={4500}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        onClose={handleOutlineToastClose}
      >
        <Alert
          severity="success"
          variant="filled"
          sx={{ width: '100%', boxShadow: '0 8px 24px rgba(26, 22, 17, 0.25)' }}
          onClose={handleOutlineToastClose}
        >
          Structured outline with {sceneCount} scenes generated. Each scene includes image prompts and audio narration.
        </Alert>
      </Snackbar>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!state.premise && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Please generate a premise first in the Setup phase.
        </Alert>
      )}

      {(state.outline || state.outlineScenes) ? (
        <Box component="div">
          <BookPages
            currentScene={currentScene}
            currentSceneIndex={currentSceneIndex}
            scenesLength={scenes.length}
            canGoPrev={canGoPrev}
            canGoNext={canGoNext}
            pageDirection={pageDirection}
            onPrev={handlePrevScene}
            onNext={handleNextScene}
            imageUrl={currentSceneImageFullUrl}
            onImageError={() => setImageLoadError((prev) => new Set(prev).add(currentSceneNumber))}
            narrationEnabled={!!state.enableNarration}
            audioUrl={
              currentSceneAudioFullUrl || (state.sceneAudio && state.sceneAudio.get(currentSceneNumber)
                ? storyWriterApi.getAudioUrl(state.sceneAudio.get(currentSceneNumber) || '')
                : null)
            }
            onOpenImageModal={openImageModal}
            onOpenAudioModal={openAudioModal}
            onOpenCharactersModal={openCharactersModal}
            onOpenKeyEventsModal={openKeyEventsModal}
            onOpenTitleModal={openTitleModal}
            onOpenEditModal={openEditModal}
          />
          <OutlineActionsBar
            isGenerating={isGenerating}
            canRegenerateOutline={!!state.premise}
            onRegenerateOutline={handleGenerateOutline}
            showMediaActions={!!(state.isOutlineStructured && state.outlineScenes)}
            isGeneratingImages={isGeneratingImages}
            isGeneratingAudio={isGeneratingAudio}
            illustrationEnabled={!!state.enableIllustration && !!hasOutlineScenes}
            narrationEnabled={!!state.enableNarration && !!hasOutlineScenes}
            onGenerateImages={handleGenerateImages}
            onGenerateAudio={handleGenerateAudio}
            canContinue={!!(state.outline || state.outlineScenes) && !isGenerating && !isGeneratingImages && !isGeneratingAudio}
            onContinue={handleContinue}
          />
        </Box>
          ) : (
            <TextField
              fullWidth
              multiline
              rows={12}
              value={state.outline || ''}
              onChange={(e) => state.setOutline(e.target.value)}
              label="Story Outline"
              sx={{ mb: 3 }}
            />
          )}
      <EditSectionModal
        open={isEditModalOpen}
        sceneNumber={currentSceneNumber}
        editText={editText}
        onChangeEditText={setEditText}
        aiFeedback={aiFeedback}
        onChangeAiFeedback={setAiFeedback}
        aiLoading={aiLoading}
        onGenerateSuggestions={handleGenerateAISuggestions}
        suggestions={aiSuggestions}
        onPickSuggestion={applySuggestion}
        onClose={() => setIsEditModalOpen(false)}
        onSave={handleSaveUpdatedSection}
      />
      <ImageEditModal
        open={isImageModalOpen}
        sceneNumber={currentSceneNumber}
        value={imagePromptDraft}
        onChange={setImagePromptDraft}
        onClose={() => setIsImageModalOpen(false)}
        onSave={() => {
          if (!hasScenes || !currentScene) { setIsImageModalOpen(false); return; }
          const updated = [...scenes];
          updated[currentSceneIndex] = { ...updated[currentSceneIndex], image_prompt: imagePromptDraft };
          (state.setOutlineScenes as any)(updated);
          setIsImageModalOpen(false);
        }}
      />
      <AudioScriptModal
        open={isAudioModalOpen}
        sceneNumber={currentSceneNumber}
        value={audioScriptDraft}
        onChange={setAudioScriptDraft}
        onClose={() => setIsAudioModalOpen(false)}
        onSave={() => {
          if (!hasScenes || !currentScene) { setIsAudioModalOpen(false); return; }
          const updated = [...scenes];
          updated[currentSceneIndex] = { ...updated[currentSceneIndex], audio_narration: audioScriptDraft };
          (state.setOutlineScenes as any)(updated);
          setIsAudioModalOpen(false);
        }}
        audioProvider={state.audioProvider}
        audioLang={state.audioLang}
        audioSlow={state.audioSlow}
        audioRate={state.audioRate}
        onChangeProvider={state.setAudioProvider}
        onChangeLang={state.setAudioLang}
        onChangeSlow={state.setAudioSlow}
        onChangeRate={state.setAudioRate}
        audioUrl={
          (state.sceneAudio && state.sceneAudio.get(currentSceneNumber)
            ? storyWriterApi.getAudioUrl(state.sceneAudio.get(currentSceneNumber) || '')
            : currentSceneAudioFullUrl) || null
        }
      />
      <CharactersModal
        open={isCharactersModalOpen}
        sceneNumber={currentSceneNumber}
        characters={currentScene?.character_descriptions || []}
        onClose={() => setIsCharactersModalOpen(false)}
      />
      <KeyEventsModal
        open={isKeyEventsModalOpen}
        sceneNumber={currentSceneNumber}
        events={currentScene?.key_events || []}
        onClose={() => setIsKeyEventsModalOpen(false)}
      />
      <TitleEditModal
        open={isTitleModalOpen}
        sceneNumber={currentSceneNumber}
        value={titleDraft}
        onChange={setTitleDraft}
        onClose={() => setIsTitleModalOpen(false)}
        onSave={() => {
          if (!hasScenes || !currentScene) { setIsTitleModalOpen(false); return; }
          const updated = [...scenes];
          updated[currentSceneIndex] = { ...updated[currentSceneIndex], title: titleDraft };
          (state.setOutlineScenes as any)(updated);
          setIsTitleModalOpen(false);
        }}
      />
        </Box>
  );
};

export default StoryOutline;
