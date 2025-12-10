import React, { useEffect, useState } from "react";
import { Stack, Box, Typography, TextField, Button, Chip, CircularProgress, alpha } from "@mui/material";
import { VolumeUp as VolumeUpIcon } from "@mui/icons-material";
import { Line } from "../types";
import { GlassyCard, glassyCardSx } from "../ui";

interface LineEditorProps {
  line: Line;
  onChange: (l: Line) => void;
  onPreview: (text: string) => Promise<{ ok: boolean; message: string; audioUrl?: string }>;
}

export const LineEditor: React.FC<LineEditorProps> = ({ line, onChange, onPreview }) => {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(line.text);
  const [previewing, setPreviewing] = useState(false);
  useEffect(() => setText(line.text), [line.text]);

  const handleSave = () => {
    onChange({ ...line, text });
    setEditing(false);
  };

  const handlePreview = async () => {
    setPreviewing(true);
    try {
      const res = await onPreview(text);
      if (res.audioUrl) {
        window.open(res.audioUrl, "_blank");
      } else {
        alert(res.message);
      }
    } finally {
      setPreviewing(false);
    }
  };

  return (
    <GlassyCard
      whileHover={{ y: -2 }}
      sx={{
        ...glassyCardSx,
        p: 2,
        transition: "all 0.2s",
      }}
    >
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            <Chip label={line.speaker} size="small" sx={{ mb: 1, background: alpha("#667eea", 0.2), color: "#a78bfa" }} />
            {editing ? (
              <TextField
                fullWidth
                multiline
                rows={3}
                value={text}
                onChange={(e) => setText(e.target.value)}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                  },
                }}
              />
            ) : (
              <Typography variant="body2" sx={{ lineHeight: 1.7, color: "rgba(255,255,255,0.9)" }}>
                {line.text}
              </Typography>
            )}
            {line.usedFactIds && line.usedFactIds.length > 0 && (
              <Stack direction="row" spacing={0.5} sx={{ mt: 1 }} flexWrap="wrap" useFlexGap>
                <Typography variant="caption" color="text.secondary">
                  Facts:
                </Typography>
                {line.usedFactIds.map((id) => (
                  <Chip key={id} label={id} size="small" variant="outlined" sx={{ fontSize: "0.65rem", height: 20 }} />
                ))}
              </Stack>
            )}
          </Box>
          <Stack spacing={1} sx={{ ml: 2 }}>
            <Button
              size="small"
              variant={editing ? "contained" : "outlined"}
              onClick={editing ? handleSave : () => setEditing(true)}
              sx={{ minWidth: 80 }}
            >
              {editing ? "Save" : "Edit"}
            </Button>
            <Button
              size="small"
              variant="outlined"
              startIcon={previewing ? <CircularProgress size={14} /> : <VolumeUpIcon />}
              onClick={handlePreview}
              disabled={previewing || editing}
              sx={{ minWidth: 120 }}
            >
              Preview TTS
            </Button>
          </Stack>
        </Stack>
      </Stack>
    </GlassyCard>
  );
};

