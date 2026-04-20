import React, { useState, useEffect, useMemo, useCallback } from "react";
import { Stack, Paper, Box, Chip, Typography } from "@mui/material";
import { CreateProjectPayload, Knobs, PodcastMode } from "./types";
import { useSubscription } from "../../contexts/SubscriptionContext";
import { podcastApi } from "../../services/podcastApi";
import { fetchMediaBlobUrl, clearMediaCache } from "../../utils/fetchMediaBlobUrl";
import { getLatestBrandAvatar } from "../../api/brandAssets";
import { VoiceSelector } from "../shared/VoiceSelector";

// Imported Components
import { TopicUrlInput, TOPIC_PLACEHOLDERS } from "./CreateStep/TopicUrlInput";
import { PodcastConfiguration } from "./CreateStep/PodcastConfiguration";
import { AvatarSelector } from "./CreateStep/AvatarSelector";
import { CreateActions } from "./CreateStep/CreateActions";
import { EnhancedTopicChoicesModal } from "./EnhancedTopicChoicesModal";

const ENHANCE_TOPIC_PROGRESS_MESSAGES = [
  "Analyzing your topic idea...",
  "Enhancing clarity and hook...",
  "Aligning language for podcast listeners...",
];

interface CreateModalProps {
  onCreate: (payload: CreateProjectPayload) => void;
  open: boolean;
  defaultKnobs: Knobs;
  isSubmitting?: boolean;
  announcement?: string;
  onAnnouncementClear?: () => void;
}

export const CreateModal: React.FC<CreateModalProps> = ({ onCreate, open, defaultKnobs, isSubmitting = false, announcement, onAnnouncementClear }) => {
  const { subscription } = useSubscription();
  const [topicInput, setTopicInput] = useState("");
  const [showAIDetailsButton, setShowAIDetailsButton] = useState(false);
  const [speakers, setSpeakers] = useState<number>(1);
  const [duration, setDuration] = useState<number>(1);
  const [budgetCap, setBudgetCap] = useState<number>(50);
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [avatarPreviewBlobUrl, setAvatarPreviewBlobUrl] = useState<string | null>(null);
  const [makingPresentable, setMakingPresentable] = useState(false);
  const [enhancingTopic, setEnhancingTopic] = useState(false);
  const [enhanceTopicProgressIndex, setEnhanceTopicProgressIndex] = useState(0);
  const [knobs, setKnobs] = useState<Knobs>({ ...defaultKnobs });
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("Wise_Woman");
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [avatarTab, setAvatarTab] = useState(0);
  const [loadingBrandAvatar, setLoadingBrandAvatar] = useState(false);
  const [brandAvatarFromDb, setBrandAvatarFromDb] = useState<string | null>(null);
  const [cameraSelfieOpen, setCameraSelfieOpen] = useState(false);
  const [podcastMode, setPodcastMode] = useState<PodcastMode>("audio_video");
  
  // Enhanced topic choices state
  const [enhancedChoices, setEnhancedChoices] = useState<string[]>([]);
  const [enhancedRationales, setEnhancedRationales] = useState<string[]>([]);
  const [choicesModalOpen, setChoicesModalOpen] = useState(false);
  const [editedChoices, setEditedChoices] = useState<string[]>([]);

  // Rotate placeholder every 3 seconds
  useEffect(() => {
    if (!topicInput) {
      const interval = setInterval(() => {
        setPlaceholderIndex((prev) => (prev + 1) % TOPIC_PLACEHOLDERS.length);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [topicInput]);

  // Fetch Brand Avatar on mount but don't select it
  useEffect(() => {
    const fetchBrandAvatar = async () => {
      try {
        setLoadingBrandAvatar(true);
        const result = await getLatestBrandAvatar();
        if (result.success && result.image_url) {
          setBrandAvatarFromDb(result.image_url);
        }
      } catch (error) {
        console.error("Failed to pre-fetch brand avatar:", error);
      } finally {
        setLoadingBrandAvatar(false);
      }
    };
    fetchBrandAvatar();
  }, []);

  useEffect(() => {
    if (!avatarPreview) {
      setAvatarPreviewBlobUrl(null);
      return;
    }

    if (avatarPreview.startsWith("data:") || avatarPreview.startsWith("blob:")) {
      setAvatarPreviewBlobUrl(null);
      return;
    }

    const isInternal =
      avatarPreview.includes("/api/podcast/") ||
      avatarPreview.includes("/api/youtube/") ||
      avatarPreview.includes("/api/story/") ||
      (avatarPreview.startsWith("/") && !avatarPreview.startsWith("//"));

    if (!isInternal) {
      setAvatarPreviewBlobUrl(null);
      return;
    }

    let isMounted = true;
    const currentPreview = avatarPreview;

    const loadBlob = async () => {
      try {
        const blobUrl = await fetchMediaBlobUrl(currentPreview);

        if (!isMounted || avatarPreview !== currentPreview) {
          if (blobUrl && blobUrl.startsWith("blob:")) {
            URL.revokeObjectURL(blobUrl);
          }
          return;
        }

        setAvatarPreviewBlobUrl((prev) => {
          if (prev && prev !== blobUrl && prev.startsWith("blob:")) {
            URL.revokeObjectURL(prev);
          }
          return blobUrl;
        });
      } catch {
        if (isMounted && avatarPreview === currentPreview) {
          setAvatarPreviewBlobUrl(null);
        }
      }
    };

    loadBlob();

    return () => {
      isMounted = false;
      setAvatarPreviewBlobUrl((prev) => {
        if (prev && prev.startsWith("blob:")) {
          URL.revokeObjectURL(prev);
        }
        return null;
      });
    };
  }, [avatarPreview]);

  // Handle blob URL for the potential brand avatar preview (not selected yet)
  const [brandAvatarBlobUrl, setBrandAvatarBlobUrl] = useState<string | null>(null);
  useEffect(() => {
    if (!brandAvatarFromDb) {
      setBrandAvatarBlobUrl(null);
      return;
    }
    
    let isMounted = true;
    const loadBrandBlob = async () => {
      try {
        // Clear cache for this URL to ensure fresh data
        if (brandAvatarFromDb) {
          clearMediaCache(brandAvatarFromDb);
        }
        
        const blobUrl = await fetchMediaBlobUrl(brandAvatarFromDb);
        if (isMounted) setBrandAvatarBlobUrl(blobUrl);
      } catch (err) {
        console.error("Failed to load brand avatar blob:", err);
      }
    };
    loadBrandBlob();
    return () => {
      isMounted = false;
      if (brandAvatarBlobUrl && brandAvatarBlobUrl.startsWith("blob:")) {
        URL.revokeObjectURL(brandAvatarBlobUrl);
      }
    };
  }, [brandAvatarFromDb]);

  // Ensure duration and speakers are within limits
  useEffect(() => {
    if (duration > 10) {
      setDuration(10);
    }
    if (speakers > 2) {
      setSpeakers(2);
    }
  }, [duration, speakers]);

  // URL detection helper
  const detectUrl = (text: string): boolean => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return urlRegex.test(text);
  };

  const isUrl = useMemo(() => detectUrl(topicInput), [topicInput]);
  const enhanceTopicMessage = enhancingTopic ? ENHANCE_TOPIC_PROGRESS_MESSAGES[enhanceTopicProgressIndex] : undefined;

  useEffect(() => {
    if (!enhancingTopic) {
      setEnhanceTopicProgressIndex(0);
      return;
    }

    const interval = setInterval(() => {
      setEnhanceTopicProgressIndex((prev) => (prev + 1) % ENHANCE_TOPIC_PROGRESS_MESSAGES.length);
    }, 1200);

    return () => clearInterval(interval);
  }, [enhancingTopic]);

  // Handle AI Details button click
  const handleAIDetailsClick = async () => {
    if (!topicInput.trim() || enhancingTopic) return;
    
    try {
      setEnhancingTopic(true);
      // We pass the current Bible context if we have it (unlikely here as it's generated in analysis)
      // But the backend will generate it from onboarding data if missing
      const result = await podcastApi.enhanceIdea({
        idea: topicInput,
      });
      
      if (result.enhanced_ideas && result.enhanced_ideas.length === 3) {
        setEnhancedChoices(result.enhanced_ideas);
        setEnhancedRationales(result.rationales || []);
        setEditedChoices(result.enhanced_ideas); // Initialize editable versions
        setChoicesModalOpen(true);
      }
    } catch (error) {
      console.error("Failed to enhance idea with AI:", error);
    } finally {
      setEnhancingTopic(false);
    }
  };

  // Handle enhanced topic choice selection
  const handleChoiceSelection = (selectedIndex: number, editedChoice: string) => {
    const selectedTopic = editedChoice;
    setTopicInput(selectedTopic);
    setChoicesModalOpen(false);
    // Reset choices state
    setEnhancedChoices([]);
    setEnhancedRationales([]);
    setEditedChoices([]);
  };

  // Show AI details button when user starts typing (and it's not a URL)
  useEffect(() => {
    setShowAIDetailsButton(topicInput.trim().length > 0 && !isUrl);
  }, [topicInput, isUrl]);

  // Check if avatar is present (from any source: upload, selfie, brand avatar, or asset library)
  const hasAvatar = Boolean(
    avatarFile ||                         // User uploaded an image
    avatarUrl ||                         // Already processed avatar URL
    avatarPreview ||                      // Avatar preview available
    brandAvatarFromDb ||                  // Brand avatar from database
    brandAvatarBlobUrl                    // Brand avatar blob URL
  );

  // Check if all required inputs are provided
  const hasTopic = Boolean(topicInput.trim());
  const hasVoice = Boolean(selectedVoiceId);
  const hasDuration = Boolean(duration > 0 && duration <= 10);
  const hasSpeakers = Boolean(speakers >= 1 && speakers <= 2);
  const hasPodcastMode = Boolean(podcastMode);

  // Required: topic, duration, speakers, voice, podcastMode, presenter avatar
  // Avatar required for video modes; for audio_only, still require avatar for presenter display
  const canSubmit = Boolean(hasTopic && hasVoice && hasDuration && hasSpeakers && hasPodcastMode && hasAvatar);

  const [submitError, setSubmitError] = useState<string | null>(null);

  const submit = useCallback(async () => {
    if (!canSubmit || isSubmitting) return;
    
    setSubmitError(null);
    
    // Determine if input is idea or URL
    // For URL, we extract the first URL found or use the whole string if it's a direct URL
    let finalIdea = "";
    let finalUrl = "";

    if (isUrl) {
      // Simple extraction: if the input contains a URL, we treat the input as the URL (or extract it)
      // For now, let's assume the user pasted a URL. 
      // If there's mixed text, we might want to just send the whole thing as 'url' if the backend handles extraction,
      // or extract it here. 
      // The previous logic used specific 'url' state.
      const urlMatch = topicInput.match(/(https?:\/\/[^\s]+)/);
      if (urlMatch) {
        finalUrl = urlMatch[0];
      } else {
        // Fallback
        finalUrl = topicInput;
      }
    } else {
      finalIdea = topicInput;
    }
    
    // If avatar was uploaded but not yet uploaded to server, upload it now
    let finalAvatarUrl: string | null = avatarUrl;
    if (avatarFile && !avatarUrl) {
      try {
        const { podcastApi } = await import("../../services/podcastApi");
        const uploadResult = await podcastApi.uploadAvatar(avatarFile);
        finalAvatarUrl = uploadResult.avatar_url;
      } catch (error) {
        console.error('Avatar upload failed:', error);
        // Continue without avatar
      }
    }
    
    // Include selected voice in knobs
    const finalKnobs = {
      ...knobs,
      voice_id: selectedVoiceId,
    };
    
    try {
      await onCreate({
        ideaOrUrl: finalUrl || finalIdea,
        speakers,
        duration,
        knobs: finalKnobs,
        budgetCap,
        files: { voiceFile, avatarFile },
        avatarUrl: finalAvatarUrl,
        podcastMode,
      });
    } catch (err: any) {
      console.error("[CreateModal] Submit error:", err);
      setSubmitError(err?.message || String(err) || "Failed to create project");
    }
  }, [canSubmit, isSubmitting, isUrl, topicInput, avatarFile, avatarUrl, knobs, selectedVoiceId, speakers, duration, budgetCap, podcastMode, onCreate]);

  const reset = () => {
    setTopicInput("");
    setSpeakers(1);
    setDuration(1);
    setBudgetCap(50);
    setVoiceFile(null);
    setAvatarFile(null);
    setAvatarPreview(null);
    setAvatarUrl(null);
    setMakingPresentable(false);
    setEnhancingTopic(false);
    setEnhanceTopicProgressIndex(0);
    setKnobs({ ...defaultKnobs });
    setSelectedVoiceId("Wise_Woman");
    setPlaceholderIndex(0);
    setPodcastMode("audio_video");
  };

  const handleAvatarSelectFromLibrary = React.useCallback((url: string) => {
    setAvatarFile(null);
    setAvatarPreview(url);
    setAvatarUrl(url);
  }, []);

  const handleAvatarChange = React.useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        console.error('Please select an image file');
        return;
      }
      // Validate file size (e.g., max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        console.error('Image file size must be less than 5MB');
        return;
      }
      setAvatarFile(file);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      
      // Upload image immediately to get URL (for "Make Presentable" feature)
      try {
        const { podcastApi } = await import("../../services/podcastApi");
        const uploadResult = await podcastApi.uploadAvatar(file);
        setAvatarUrl(uploadResult.avatar_url);
      } catch (error) {
        console.error('Avatar upload failed:', error);
        // Continue with local preview - upload will happen on submit
      }
    }
  }, []);

  const handleCameraSelfie = React.useCallback(async (imageDataUrl: string) => {
    try {
      // Convert dataURL to File object
      const response = await fetch(imageDataUrl);
      const blob = await response.blob();
      const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });
      
      // Set the file and preview
      setAvatarFile(file);
      setAvatarPreview(imageDataUrl);
      
      // Upload image immediately to get URL (for "Make Presentable" feature)
      try {
        const { podcastApi } = await import("../../services/podcastApi");
        const uploadResult = await podcastApi.uploadAvatar(file);
        setAvatarUrl(uploadResult.avatar_url);
      } catch (error) {
        console.error('Avatar upload failed:', error);
        // Continue with local preview - upload will happen on submit
      }
      
      // Close camera dialog
      setCameraSelfieOpen(false);
    } catch (error) {
      console.error('Failed to process selfie:', error);
    }
  }, []);

  const handleRemoveAvatar = React.useCallback(() => {
    setAvatarFile(null);
    setAvatarPreview(null);
    setAvatarUrl(null);
    if (avatarPreviewBlobUrl && avatarPreviewBlobUrl.startsWith("blob:")) {
      URL.revokeObjectURL(avatarPreviewBlobUrl);
    }
    setAvatarPreviewBlobUrl(null);
    setMakingPresentable(false);
  }, [avatarPreviewBlobUrl]);

  const handleUseBrandAvatar = React.useCallback(async () => {
    if (brandAvatarFromDb) {
      setAvatarFile(null);
      setAvatarPreview(brandAvatarFromDb);
      setAvatarUrl(brandAvatarFromDb);
      // Ensure the blob URL is set for the preview logic
      if (brandAvatarBlobUrl) {
        setAvatarPreviewBlobUrl(brandAvatarBlobUrl);
      }
      return;
    }
    
    if (loadingBrandAvatar) return;
    try {
      setLoadingBrandAvatar(true);
      const result = await getLatestBrandAvatar();
      if (result.success && result.image_url) {
        setAvatarFile(null);
        setAvatarPreview(result.image_url);
        setAvatarUrl(result.image_url);
        setBrandAvatarFromDb(result.image_url);
      } else {
        console.error(result.error || result.message || "No brand avatar found");
      }
    } catch (error) {
      console.error("Failed to load brand avatar:", error);
    } finally {
      setLoadingBrandAvatar(false);
    }
  }, [brandAvatarFromDb, brandAvatarBlobUrl, loadingBrandAvatar]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setAvatarTab(newValue);
    if (newValue === 0) {
      // Switch to brand avatar tab - it's already pre-fetched on mount
    } else if (newValue === 1) {
      // Asset Library tab - clear current selection so user must choose
      setAvatarUrl(null);
      setAvatarPreview(null);
      setAvatarFile(null);
    } else if (newValue === 2) {
      // Upload tab - clear if no file uploaded yet to show dropzone clean state
      if (!avatarFile) {
        setAvatarUrl(null);
        setAvatarPreview(null);
      }
    }
  };

  // Initialize with Brand Avatar removed - user must explicitly choose or it's AI generated
  useEffect(() => {
    // We used to auto-load here, but now we leave it empty to allow AI generation later
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleMakePresentable = React.useCallback(async () => {
    if (!avatarUrl || makingPresentable) return;
    
    try {
      setMakingPresentable(true);
      const { podcastApi } = await import("../../services/podcastApi");
      const result = await podcastApi.makeAvatarPresentable(avatarUrl);
      
      if (result.avatar_url) {
        // Fetch the transformed image as blob to display
        const { aiApiClient } = await import("../../api/client");
        const response = await aiApiClient.get(result.avatar_url, { responseType: 'blob' });
        const blobUrl = URL.createObjectURL(response.data);
        
        // Revoke old blob URL if exists
        if (avatarPreviewBlobUrl && avatarPreviewBlobUrl.startsWith("blob:")) {
          URL.revokeObjectURL(avatarPreviewBlobUrl);
        }
        
        setAvatarPreviewBlobUrl(blobUrl);
        setAvatarPreview(result.avatar_url);
        setAvatarUrl(result.avatar_url);
      }
    } catch (error) {
      console.error('Failed to make avatar presentable:', error);
      // Could show error message to user
    } finally {
      setMakingPresentable(false);
    }
  }, [avatarUrl, makingPresentable, avatarPreviewBlobUrl]);

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 3,
        border: "1px solid rgba(15, 23, 42, 0.08)",
        background: "#ffffff",
        boxShadow: "0 1px 3px rgba(15, 23, 42, 0.06), 0 8px 24px rgba(15, 23, 42, 0.08)",
        p: { xs: 3, md: 4.5 },
      }}
    >
      <Stack spacing={3.5}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={3} alignItems="stretch">
          <Box sx={{ flex: 1 }}>
            <TopicUrlInput
              value={topicInput}
              onChange={setTopicInput}
              isUrl={isUrl}
              showAIDetailsButton={showAIDetailsButton}
              onAIDetailsClick={handleAIDetailsClick}
              placeholderIndex={placeholderIndex}
              loading={enhancingTopic}
              loadingMessage={enhanceTopicMessage}
              estimatedCost={null}
              duration={duration}
              speakers={speakers}
              knobs={knobs}
            />
          </Box>

          <Box sx={{ width: { xs: "100%", md: "320px" } }}>
            <PodcastConfiguration
              duration={duration}
              setDuration={setDuration}
              speakers={speakers}
              setSpeakers={setSpeakers}
              podcastMode={podcastMode}
              setPodcastMode={setPodcastMode}
            />
          </Box>
        </Stack>
        
        <AvatarSelector
          avatarTab={avatarTab}
          setAvatarTab={handleTabChange}
          avatarFile={avatarFile}
          avatarPreview={avatarPreview}
          avatarUrl={avatarUrl}
          loadingBrandAvatar={loadingBrandAvatar}
          handleUseBrandAvatar={handleUseBrandAvatar}
          handleAvatarSelectFromLibrary={handleAvatarSelectFromLibrary}
          handleAvatarChange={handleAvatarChange}
          handleCameraSelfie={handleCameraSelfie}
          handleRemoveAvatar={handleRemoveAvatar}
          handleMakePresentable={handleMakePresentable}
          makingPresentable={makingPresentable}
          avatarPreviewBlobUrl={avatarPreviewBlobUrl}
          brandAvatarFromDb={brandAvatarFromDb}
          brandAvatarBlobUrl={brandAvatarBlobUrl}
          cameraSelfieOpen={cameraSelfieOpen}
          setCameraSelfieOpen={setCameraSelfieOpen}
          podcastMode={podcastMode}
        />

        <VoiceSelector
          value={selectedVoiceId}
          onChange={setSelectedVoiceId}
          showVoiceClone={true}
        />

        <CreateActions
          reset={reset}
          submit={submit}
          canSubmit={canSubmit}
          isSubmitting={isSubmitting}
          announcement={announcement}
          onAnnouncementClear={onAnnouncementClear}
          error={submitError}
        />

        {/* Enhanced Topic Choices Modal */}
        <EnhancedTopicChoicesModal
          open={choicesModalOpen}
          onClose={() => setChoicesModalOpen(false)}
          enhancedChoices={enhancedChoices}
          enhancedRationales={enhancedRationales}
          onSelectChoice={handleChoiceSelection}
          loading={enhancingTopic}
        />
      </Stack>
    </Paper>
  );
};
