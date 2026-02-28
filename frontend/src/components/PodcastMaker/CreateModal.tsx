import React, { useState, useEffect, useMemo } from "react";
import { Stack, Paper, Box } from "@mui/material";
import { CreateProjectPayload, Knobs } from "./types";
import { useSubscription } from "../../contexts/SubscriptionContext";
import { podcastApi } from "../../services/podcastApi";
import { fetchMediaBlobUrl } from "../../utils/fetchMediaBlobUrl";
import { getLatestBrandAvatar } from "../../api/brandAssets";

// Imported Components
import { CreateHeader } from "./CreateStep/CreateHeader";
import { TopicUrlInput, TOPIC_PLACEHOLDERS } from "./CreateStep/TopicUrlInput";
import { PodcastConfiguration } from "./CreateStep/PodcastConfiguration";
import { AvatarSelector } from "./CreateStep/AvatarSelector";
import { CreateActions } from "./CreateStep/CreateActions";

interface CreateModalProps {
  onCreate: (payload: CreateProjectPayload) => void;
  open: boolean;
  defaultKnobs: Knobs;
  isSubmitting?: boolean;
}

export const CreateModal: React.FC<CreateModalProps> = ({ onCreate, open, defaultKnobs, isSubmitting = false }) => {
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
  const [knobs, setKnobs] = useState<Knobs>({ ...defaultKnobs });
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [avatarTab, setAvatarTab] = useState(0);
  const [loadingBrandAvatar, setLoadingBrandAvatar] = useState(false);
  const [brandAvatarFromDb, setBrandAvatarFromDb] = useState<string | null>(null);

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

  // Handle AI Details button click
  const handleAIDetailsClick = async () => {
    if (!topicInput.trim() || makingPresentable) return;
    
    try {
      setMakingPresentable(true);
      // We pass the current Bible context if we have it (unlikely here as it's generated in analysis)
      // But the backend will generate it from onboarding data if missing
      const result = await podcastApi.enhanceIdea({
        idea: topicInput,
      });
      
      if (result.enhanced_idea) {
        setTopicInput(result.enhanced_idea);
      }
    } catch (error) {
      console.error("Failed to enhance idea with AI:", error);
    } finally {
      setMakingPresentable(false);
    }
  };

  // Show AI details button when user starts typing (and it's not a URL)
  useEffect(() => {
    setShowAIDetailsButton(topicInput.trim().length > 0 && !isUrl);
  }, [topicInput, isUrl]);

  // Calculate estimated cost
  const estimatedCost = useMemo(() => {
    const chars = Math.max(1000, duration * 900); // ~900 chars per minute
    const scenes = Math.ceil((duration * 60) / (knobs.scene_length_target || 45));
    const secs = duration * 60;
    
    const ttsCost = (chars / 1000) * 0.05;
    const avatarCost = speakers * 0.15;
    const videoRate = knobs.bitrate === 'hd' ? 0.06 : 0.03;
    const videoCost = secs * videoRate;
    const researchCost = 0.3; // Fixed research cost
    
    return {
      ttsCost: +ttsCost.toFixed(2),
      avatarCost: +avatarCost.toFixed(2),
      videoCost: +videoCost.toFixed(2),
      researchCost: +researchCost.toFixed(2),
      total: +(ttsCost + avatarCost + videoCost + researchCost).toFixed(2),
    };
  }, [duration, speakers, knobs.bitrate, knobs.scene_length_target]);

  const canSubmit = Boolean(topicInput.trim());

  const submit = async () => {
    if (!canSubmit || isSubmitting) return;
    
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
    
    onCreate({
      ideaOrUrl: finalUrl || finalIdea,
      speakers,
      duration,
      knobs,
      budgetCap,
      files: { voiceFile, avatarFile },
      avatarUrl: finalAvatarUrl,
    });
  };

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
    setKnobs({ ...defaultKnobs });
    setPlaceholderIndex(0);
  };

  const handleAvatarSelectFromLibrary = React.useCallback((url: string) => {
    setAvatarFile(null);
    setAvatarPreview(url);
    setAvatarUrl(url);
  }, []);

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
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
  };

  const handleRemoveAvatar = () => {
    setAvatarFile(null);
    setAvatarPreview(null);
    setAvatarUrl(null);
    if (avatarPreviewBlobUrl && avatarPreviewBlobUrl.startsWith("blob:")) {
      URL.revokeObjectURL(avatarPreviewBlobUrl);
    }
    setAvatarPreviewBlobUrl(null);
    setMakingPresentable(false);
  };

  const handleUseBrandAvatar = async () => {
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
  };

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

  const handleMakePresentable = async () => {
    if (!avatarUrl || makingPresentable) return;
    
    try {
      setMakingPresentable(true);
      const { podcastApi } = await import("../../services/podcastApi");
      const result = await podcastApi.makeAvatarPresentable(avatarUrl);
      
      // Fetch the transformed image as blob to display
      const { aiApiClient } = await import("../../api/client");
      const response = await aiApiClient.get(result.avatar_url, { responseType: 'blob' });
      const blobUrl = URL.createObjectURL(response.data);
      setAvatarPreview(blobUrl);
      setAvatarUrl(result.avatar_url);
    } catch (error) {
      console.error('Failed to make avatar presentable:', error);
      // Could show error message to user
    } finally {
      setMakingPresentable(false);
    }
  };

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
        <CreateHeader
          subscription={subscription}
          duration={duration}
          speakers={speakers}
          knobs={knobs}
          estimatedCost={estimatedCost}
        />

        <Stack direction={{ xs: "column", md: "row" }} spacing={3} alignItems="stretch">
          <Box sx={{ flex: 1 }}>
            <TopicUrlInput
              value={topicInput}
              onChange={setTopicInput}
              isUrl={isUrl}
              showAIDetailsButton={showAIDetailsButton}
              onAIDetailsClick={handleAIDetailsClick}
              placeholderIndex={placeholderIndex}
              loading={makingPresentable}
            />
          </Box>

          <Box sx={{ width: { xs: "100%", md: "320px" } }}>
            <PodcastConfiguration
              duration={duration}
              setDuration={setDuration}
              speakers={speakers}
              setSpeakers={setSpeakers}
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
          handleRemoveAvatar={handleRemoveAvatar}
          handleMakePresentable={handleMakePresentable}
          makingPresentable={makingPresentable}
          avatarPreviewBlobUrl={avatarPreviewBlobUrl}
          brandAvatarFromDb={brandAvatarFromDb}
          brandAvatarBlobUrl={brandAvatarBlobUrl}
        />

        <CreateActions
          reset={reset}
          submit={submit}
          canSubmit={canSubmit}
          isSubmitting={isSubmitting}
        />
      </Stack>
    </Paper>
  );
};
