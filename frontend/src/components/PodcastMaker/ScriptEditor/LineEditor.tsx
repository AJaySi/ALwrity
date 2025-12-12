import React, { useEffect, useState } from "react";
import { Stack, Box, Typography, TextField, Button, Chip, alpha } from "@mui/material";
import { Line } from "../types";
import { GlassyCard, glassyCardSx } from "../ui";

interface LineEditorProps {
  line: Line;
  onChange: (l: Line) => void;
}

export const LineEditor: React.FC<LineEditorProps> = ({ line, onChange }) => {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(line.text);
  useEffect(() => setText(line.text), [line.text]);

  const handleSave = () => {
    onChange({ ...line, text });
    setEditing(false);
  };

  return (
    <GlassyCard
      whileHover={{ y: -2 }}
      sx={{
        ...glassyCardSx,
        p: 2.5,
        transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
        borderLeft: "3px solid transparent",
        "&:hover": {
          borderLeftColor: "#667eea",
          boxShadow: "0 4px 6px rgba(15, 23, 42, 0.08), 0 8px 24px rgba(15, 23, 42, 0.06)",
        },
      }}
    >
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            <Chip 
              label={line.speaker} 
              size="small" 
              sx={{ 
                mb: 1.5, 
                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                color: "#667eea", 
                fontWeight: 600,
                fontSize: "0.75rem",
                height: 24,
                border: "1px solid rgba(102, 126, 234, 0.2)",
                boxShadow: "0 1px 2px rgba(102, 126, 234, 0.05)",
              }} 
            />
            {editing ? (
              <TextField
                fullWidth
                multiline
                rows={3}
                value={text}
                onChange={(e) => setText(e.target.value)}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    color: "#0f172a",
                    backgroundColor: "#f8fafc",
                    borderRadius: 2,
                    "& fieldset": { 
                      borderColor: "rgba(15, 23, 42, 0.12)",
                      borderWidth: 1.5,
                    },
                    "&:hover fieldset": { 
                      borderColor: "rgba(102, 126, 234, 0.4)",
                    },
                    "&.Mui-focused fieldset": { 
                      borderColor: "#667eea",
                      borderWidth: 2,
                    },
                  },
                  "& .MuiInputBase-input": {
                    color: "#0f172a",
                    fontWeight: 400,
                    fontSize: "0.9375rem",
                    lineHeight: 1.6,
                  },
                }}
              />
            ) : (
              <Typography 
                variant="body2" 
                sx={{ 
                  lineHeight: 1.75, 
                  color: "#0f172a", 
                  fontWeight: 400,
                  fontSize: "0.9375rem",
                  letterSpacing: "0.01em",
                }}
              >
                {line.text}
              </Typography>
            )}
            {line.usedFactIds && line.usedFactIds.length > 0 && (
              <Stack direction="row" spacing={0.5} sx={{ mt: 1.5 }} flexWrap="wrap" useFlexGap>
                <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 500, fontSize: "0.75rem" }}>
                  Facts:
                </Typography>
                {line.usedFactIds.map((id) => (
                  <Chip 
                    key={id} 
                    label={id} 
                    size="small" 
                    variant="outlined" 
                    sx={{ 
                      fontSize: "0.6875rem", 
                      height: 22,
                      color: "#64748b",
                      borderColor: "rgba(15, 23, 42, 0.12)",
                      fontWeight: 500,
                    }} 
                  />
                ))}
              </Stack>
            )}
          </Box>
          <Box sx={{ ml: 2 }}>
            <Button
              size="small"
              variant={editing ? "contained" : "outlined"}
              onClick={editing ? handleSave : () => setEditing(true)}
              sx={{ 
                minWidth: 85,
                color: editing ? "white" : "#667eea",
                borderColor: editing ? "transparent" : "#667eea",
                backgroundColor: editing 
                  ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                  : "transparent",
                fontWeight: 600,
                fontSize: "0.8125rem",
                textTransform: "none",
                borderRadius: 2,
                borderWidth: editing ? 0 : 1.5,
                boxShadow: editing ? "0 2px 4px rgba(102, 126, 234, 0.2)" : "none",
                "&:hover": {
                  borderColor: editing ? "transparent" : "#5568d3",
                  backgroundColor: editing 
                    ? "linear-gradient(135deg, #5568d3 0%, #6b3fa0 100%)"
                    : alpha("#667eea", 0.08),
                  boxShadow: editing ? "0 4px 8px rgba(102, 126, 234, 0.3)" : "none",
                },
                transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
              }}
            >
              {editing ? "Save" : "Edit"}
            </Button>
          </Box>
        </Stack>
      </Stack>
    </GlassyCard>
  );
};

