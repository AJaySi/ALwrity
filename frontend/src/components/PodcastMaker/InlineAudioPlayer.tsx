import React, { useEffect, useState } from "react";
import { Paper, Stack, Typography, IconButton, Tooltip, alpha } from "@mui/material";
import { VolumeUp as VolumeUpIcon, PlayCircle as PlayCircleIcon, PauseCircle as PauseCircleIcon, Download as DownloadIcon } from "@mui/icons-material";

interface InlineAudioPlayerProps {
  audioUrl: string;
  title?: string;
}

export const InlineAudioPlayer: React.FC<InlineAudioPlayerProps> = ({ audioUrl, title }) => {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnd = () => setPlaying(false);

    audio.addEventListener("timeupdate", updateTime);
    audio.addEventListener("loadedmetadata", updateDuration);
    audio.addEventListener("ended", handleEnd);

    return () => {
      audio.removeEventListener("timeupdate", updateTime);
      audio.removeEventListener("loadedmetadata", updateDuration);
      audio.removeEventListener("ended", handleEnd);
    };
  }, [audioUrl]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (playing) {
      audio.pause();
    } else {
      audio.play();
    }
    setPlaying(!playing);
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
        <Stack direction="row" spacing={2} alignItems="center">
          <IconButton onClick={togglePlay} sx={{ color: "#a78bfa" }} size="large">
            {playing ? <PauseCircleIcon fontSize="large" /> : <PlayCircleIcon fontSize="large" />}
          </IconButton>
          <Stack flex={1}>
            <input
              type="range"
              min={0}
              max={duration || 0}
              value={currentTime}
              onChange={handleSeek}
              style={{ width: "100%", cursor: "pointer" }}
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
                const link = document.createElement("a");
                link.href = audioUrl;
                link.download = title || "podcast-audio.mp3";
                link.click();
              }}
              sx={{ color: "rgba(255,255,255,0.7)" }}
            >
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Stack>
        <audio ref={audioRef} src={audioUrl} preload="metadata" />
      </Stack>
    </Paper>
  );
};

