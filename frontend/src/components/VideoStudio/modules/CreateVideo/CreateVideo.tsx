import React from 'react';
import { Grid } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useCreateVideo } from './hooks/useCreateVideo';
import { GenerationSettingsPanel, VideoExamplesPanel } from './components';
import { handleExampleClick, handleAssetClick } from './utils/exampleHandlers';
import { createVideoExamples } from '../../dashboard/constants';
import type { ContentAsset } from '../../../../hooks/useContentAssets';

export const CreateVideo: React.FC = () => {
  const {
    mode,
    setMode,
    prompt,
    setPrompt,
    negativePrompt,
    setNegativePrompt,
    duration,
    setDuration,
    resolution,
    setResolution,
    aspect,
    setAspect,
    motion,
    setMotion,
    audioAttached,
    setAudioAttached,
    selectedModel,
    setSelectedModel,
    selectedExample,
    setSelectedExample,
    selectedAssetId,
    setSelectedAssetId,
    promptPlaceholderIndex,
    setPromptPlaceholderIndex,
    negativePlaceholderIndex,
    setNegativePlaceholderIndex,
    promptFocused,
    setPromptFocused,
    negativeFocused,
    setNegativeFocused,
    canGenerate,
    costHint,
    libraryVideos,
    loadingLibraryVideos,
    handleFileSelect,
  } = useCreateVideo();

  const handleExampleClickWrapper = (index: number) => {
    const example = createVideoExamples[index];
    handleExampleClick(
      index,
      example,
      setPrompt,
      setAspect,
      setSelectedExample,
      setSelectedAssetId
    );
  };

  const handleAssetClickWrapper = (asset: ContentAsset) => {
    handleAssetClick(
      asset,
      setPrompt,
      setAspect,
      setResolution,
      setSelectedAssetId,
      setSelectedExample
    );
  };

  const handleGenerate = () => {
    // Placeholder: hook preflight + job creation later
    alert('This is a UI preview. Backend generation will be wired in the next step.');
  };

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Create Studio',
        subtitle: 'AI-Powered Video Generation for Content Creators. Turn your ideas into engaging videos for Instagram, TikTok, YouTube, LinkedIn, and more.',
      }}
    >
      <Grid container spacing={3}>
        {/* Left Panel - Generation Controls */}
        <Grid item xs={12} lg={5}>
          <GenerationSettingsPanel
            mode={mode}
            prompt={prompt}
            negativePrompt={negativePrompt}
            duration={duration}
            resolution={resolution}
            aspect={aspect}
            motion={motion}
            audioAttached={audioAttached}
            costHint={costHint}
            canGenerate={canGenerate}
            promptFocused={promptFocused}
            negativeFocused={negativeFocused}
            promptPlaceholderIndex={promptPlaceholderIndex}
            negativePlaceholderIndex={negativePlaceholderIndex}
            selectedModel={selectedModel}
            onModeChange={setMode}
            onPromptChange={setPrompt}
            onNegativePromptChange={setNegativePrompt}
            onDurationChange={setDuration}
            onResolutionChange={setResolution}
            onAspectChange={setAspect}
            onMotionChange={setMotion}
            onModelChange={setSelectedModel}
            onFileSelect={handleFileSelect}
            onPromptFocus={() => setPromptFocused(true)}
            onPromptBlur={() => setPromptFocused(false)}
            onNegativeFocus={() => setNegativeFocused(true)}
            onNegativeBlur={() => setNegativeFocused(false)}
            onPromptPlaceholderChange={setPromptPlaceholderIndex}
            onNegativePlaceholderChange={setNegativePlaceholderIndex}
            onGenerate={handleGenerate}
          />
        </Grid>

        {/* Right Panel - Video Preview & Examples */}
        <Grid item xs={12} lg={7}>
          <VideoExamplesPanel
            examples={createVideoExamples}
            libraryVideos={libraryVideos}
            loadingLibraryVideos={loadingLibraryVideos}
            selectedExample={selectedExample}
            selectedAssetId={selectedAssetId}
            prompt={prompt}
            onExampleClick={handleExampleClickWrapper}
            onAssetClick={handleAssetClickWrapper}
          />
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default CreateVideo;
