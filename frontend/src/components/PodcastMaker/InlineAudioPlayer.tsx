import React, { useEffect, useState } from "react";
import { Paper, Stack, Typography, IconButton, Tooltip, alpha, Alert } from "@mui/material";
import { VolumeUp as VolumeUpIcon, PlayCircle as PlayCircleIcon, PauseCircle as PauseCircleIcon, Download as DownloadIcon } from "@mui/icons-material";
import { aiApiClient } from "../../api/client";

interface InlineAudioPlayerProps {
  audioUrl: string;
  title?: string;
}

export const InlineAudioPlayer: React.FC<InlineAudioPlayerProps> = ({ audioUrl, title }) => {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  // Load audio as blob if it's an authenticated endpoint
  useEffect(() => {
    if (!audioUrl) {
      setBlobUrl(null);
      setError(null);
      return;
    }

    // Check if this is a podcast audio endpoint that requires authentication
    const isPodcastAudio = audioUrl.includes('/api/podcast/audio/') || audioUrl.includes('/api/story/audio/');
    
    if (!isPodcastAudio) {
      // Regular URL, use directly
      setBlobUrl(audioUrl);
      setError(null);
      return;
    }

    // Fetch as blob for authenticated endpoints
    let isMounted = true;
    const currentAudioUrl = audioUrl;

    const loadAudioBlob = async () => {
      try {
        // Normalize path
        let audioPath = currentAudioUrl.startsWith('/') ? currentAudioUrl : `/${currentAudioUrl}`;
        
        // Convert /api/story/audio/ to /api/podcast/audio/ if needed
        if (audioPath.includes('/api/story/audio/')) {
          const filename = audioPath.split('/api/story/audio/').pop() || '';
          audioPath = `/api/podcast/audio/${filename}`;
        }
        
        // Ensure it's a podcast audio endpoint
        if (!audioPath.includes('/api/podcast/audio/')) {
          const filename = audioPath.split('/').pop() || currentAudioUrl;
          audioPath = `/api/podcast/audio/${filename}`;
        }

        // Remove query parameters if present
        audioPath = audioPath.split('?')[0];

        const response = await aiApiClient.get(audioPath, {
          responseType: 'blob',
        });
        
        if (!isMounted || audioUrl !== currentAudioUrl) {
          return;
        }
        
        const blob = response.data;
        const newBlobUrl = URL.createObjectURL(blob);
        
        setBlobUrl((prevBlobUrl) => {
          // Clean up previous blob URL if exists
          if (prevBlobUrl && prevBlobUrl !== newBlobUrl) {
            URL.revokeObjectURL(prevBlobUrl);
          }
          return newBlobUrl;
        });
        setError(null);
      } catch (err) {
        console.error('Failed to load audio blob:', err);
        if (isMounted && audioUrl === currentAudioUrl) {
          setError('Failed to load audio. Please try again.');
          setBlobUrl(null);
        }
      }
    };

    loadAudioBlob();

    return () => {
      isMounted = false;
      // Cleanup blob URL when component unmounts or URL changes
      setBlobUrl((prevBlobUrl) => {
        if (prevBlobUrl && prevBlobUrl.startsWith('blob:')) {
          URL.revokeObjectURL(prevBlobUrl);
        }
        return null;
      });
    };
  }, [audioUrl]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !blobUrl) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnd = () => setPlaying(false);
    const handleError = () => {
      setError('Audio playback error. Please try again.');
      setPlaying(false);
    };

    audio.addEventListener("timeupdate", updateTime);
    audio.addEventListener("loadedmetadata", updateDuration);
    audio.addEventListener("ended", handleEnd);
    audio.addEventListener("error", handleError);

    return () => {
      audio.removeEventListener("timeupdate", updateTime);
      audio.removeEventListener("loadedmetadata", updateDuration);
      audio.removeEventListener("ended", handleEnd);
      audio.removeEventListener("error", handleError);
    };
  }, [blobUrl]);

  const togglePlay = async () => {
    const audio = audioRef.current;
    if (!audio || !blobUrl) {
      setError('Audio not loaded. Please wait...');
      return;
    }

    try {
      if (playing) {
        audio.pause();
        setPlaying(false);
      } else {
        await audio.play();
        setPlaying(true);
        setError(null);
      }
    } catch (err) {
      console.error('Playback error:', err);
      setError('Failed to play audio. Please try again.');
      setPlaying(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;
    const newTime = parseFloat(e.target.value);
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const isPodcastAudio = audioUrl.includes('/api/podcast/audio/') || audioUrl.includes('/api/story/audio/');
  const effectiveAudioUrl = blobUrl || (!isPodcastAudio ? audioUrl : null);

  return (
    <Paper
      sx={{
        p: 2,
        background: alpha("#1e293b", 0.6),
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 2,
      }}
    >
      <Stack spacing={1.5}>
        {title && (
          <Typography variant="subtitle2" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <VolumeUpIcon fontSize="small" />
            {title}
          </Typography>
        )}
        
        {error && (
          <Alert severity="error" sx={{ py: 0.5 }}>
            <Typography variant="caption">{error}</Typography>
          </Alert>
        )}

        {!blobUrl && audioUrl && (
          <Alert severity="info" sx={{ py: 0.5 }}>
            <Typography variant="caption">Loading audio...</Typography>
          </Alert>
        )}

        <Stack direction="row" spacing={2} alignItems="center">
          <IconButton 
            onClick={togglePlay} 
            disabled={!effectiveAudioUrl || !!error}
            sx={{ color: "#a78bfa" }} 
            size="large"
          >
            {playing ? <PauseCircleIcon fontSize="large" /> : <PlayCircleIcon fontSize="large" />}
          </IconButton>
          <Stack flex={1}>
            <input
              type="range"
              min={0}
              max={duration || 0}
              value={currentTime}
              onChange={handleSeek}
              disabled={!effectiveAudioUrl}
              style={{ width: "100%", cursor: effectiveAudioUrl ? "pointer" : "not-allowed" }}
            />
            <Stack direction="row" justifyContent="space-between" sx={{ mt: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                {formatTime(currentTime)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatTime(duration)}
              </Typography>
            </Stack>
          </Stack>
          <Tooltip title="Download audio">
            <IconButton
              onClick={() => {
                if (!effectiveAudioUrl) return;
                const link = document.createElement("a");
                link.href = effectiveAudioUrl;
                link.download = title || "podcast-audio.mp3";
                link.click();
              }}
              disabled={!effectiveAudioUrl}
              sx={{ color: "rgba(255,255,255,0.7)" }}
            >
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Stack>
        {effectiveAudioUrl && (
          <audio ref={audioRef} src={effectiveAudioUrl} preload="metadata" />
        )}
      </Stack>
    </Paper>
  );
};

