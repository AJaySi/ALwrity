/**
 * Podcast Image Regenerate Modal
 * 
 * A Podcast-specific wrapper around the shared ImageGenerationModal.
 * Provides Podcast-optimized presets, recommendations, and branding.
 * 
 * This maintains backward compatibility with existing usage while
 * leveraging the shared component infrastructure.
 */

import React from "react";
import {
  ImageGenerationModal,
  ImageGenerationSettings as SharedImageGenerationSettings,
} from '../../shared/ImageGenerationModal';
import {
  PODCAST_PRESETS,
  PODCAST_THEME,
  PODCAST_RECOMMENDATIONS,
} from '../../shared/ImageGenerationPresets';

// Re-export settings type for backward compatibility
// Podcast doesn't use model selection, so model is optional
export interface ImageGenerationSettings {
  prompt: string;
  style: "Auto" | "Fiction" | "Realistic";
  renderingSpeed: "Default" | "Turbo" | "Quality";
  aspectRatio: "1:1" | "16:9" | "9:16" | "4:3" | "3:4";
}

interface ImageRegenerateModalProps {
  open: boolean;
  onClose: () => void;
  onRegenerate: (settings: ImageGenerationSettings) => void;
  initialPrompt: string;
  initialStyle?: "Auto" | "Fiction" | "Realistic";
  initialRenderingSpeed?: "Default" | "Turbo" | "Quality";
  initialAspectRatio?: "1:1" | "16:9" | "9:16" | "4:3" | "3:4";
  isGenerating?: boolean;
}

export const ImageRegenerateModal: React.FC<ImageRegenerateModalProps> = ({
  open,
  onClose,
  onRegenerate,
  initialPrompt,
  initialStyle = "Realistic",
  initialRenderingSpeed = "Quality",
  initialAspectRatio = "16:9",
  isGenerating = false,
}) => {
  // Adapter to convert shared settings to Podcast-specific settings
  const handleGenerate = (settings: SharedImageGenerationSettings) => {
    const podcastSettings: ImageGenerationSettings = {
      prompt: settings.prompt,
      style: settings.style,
      renderingSpeed: settings.renderingSpeed,
      aspectRatio: settings.aspectRatio,
    };
    onRegenerate(podcastSettings);
  };

  return (
    <ImageGenerationModal
      // Core props
      open={open}
      onClose={onClose}
      onGenerate={handleGenerate}
      initialPrompt={initialPrompt}
      isGenerating={isGenerating}
      
      // Podcast-specific context
      title="Regenerate Image with Custom Settings"
      promptLabel="Generation Prompt"
      promptHelp="The prompt describes what you want to see in the generated image. It should include scene context, visual elements, and style preferences. The AI will use this along with your base avatar to create a consistent character in the scene."
      generateButtonLabel="Regenerate Image"
      
      // Podcast presets
      presets={PODCAST_PRESETS}
      presetsLabel="Podcast-ready presets"
      presetsHelp="Quickly apply a podcast-friendly look. Each preset adjusts lighting, background, and ratio while keeping your base avatar consistent."
      
      // Model selection disabled for Podcast (uses default)
      showModelSelection={false}
      
      // Default values
      defaultStyle={initialStyle}
      defaultRenderingSpeed={initialRenderingSpeed}
      defaultAspectRatio={initialAspectRatio}
      
      // Podcast theming
      theme={PODCAST_THEME}
      
      // Podcast-specific recommendations
      recommendations={PODCAST_RECOMMENDATIONS}
    />
  );
};
