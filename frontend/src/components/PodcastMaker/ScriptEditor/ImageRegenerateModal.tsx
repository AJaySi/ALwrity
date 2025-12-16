import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Box,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  alpha,
  Tooltip,
  IconButton,
  Paper,
} from "@mui/material";
import {
  Info as InfoIcon,
  HelpOutline as HelpOutlineIcon,
  Close as CloseIcon,
} from "@mui/icons-material";
import { PrimaryButton, SecondaryButton } from "../ui";

type PresetKey = "studioNeutral" | "warmBroadcast" | "techModern";

const PRESETS: Record<
  PresetKey,
  {
    title: string;
    subtitle: string;
    prompt: string;
    style: "Auto" | "Fiction" | "Realistic";
    renderingSpeed: "Default" | "Turbo" | "Quality";
    aspectRatio: "1:1" | "16:9" | "9:16" | "4:3" | "3:4";
  }
> = {
  studioNeutral: {
    title: "Studio Neutral",
    subtitle: "Clean, well-lit studio, neutral background",
    prompt:
      "Professional podcast studio, neutral light grey backdrop, soft key + fill lighting, subtle depth of field, clear microphone framing",
    style: "Realistic",
    renderingSpeed: "Quality",
    aspectRatio: "16:9",
  },
  warmBroadcast: {
    title: "Warm Broadcast",
    subtitle: "Warm tones, friendly and inviting broadcast desk",
    prompt:
      "Warm broadcast desk, soft amber lighting, cozy ambience, gentle vignette, inviting expression, polished but approachable look",
    style: "Realistic",
    renderingSpeed: "Quality",
    aspectRatio: "16:9",
  },
  techModern: {
    title: "Tech Modern",
    subtitle: "Crisp, modern look with cool accent lighting",
    prompt:
      "Modern tech podcast set, cool accent lights (teal/purple), minimal backdrop, crisp highlights, premium camera look, subtle bokeh",
    style: "Auto",
    renderingSpeed: "Quality",
    aspectRatio: "16:9",
  },
};

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
  const [prompt, setPrompt] = useState(initialPrompt);
  const [style, setStyle] = useState<"Auto" | "Fiction" | "Realistic">(initialStyle);
  const [renderingSpeed, setRenderingSpeed] = useState<"Default" | "Turbo" | "Quality">(initialRenderingSpeed);
  const [aspectRatio, setAspectRatio] = useState<"1:1" | "16:9" | "9:16" | "4:3" | "3:4">(initialAspectRatio);

  // Update state when initial values change
  useEffect(() => {
    setPrompt(initialPrompt);
    setStyle(initialStyle);
    setRenderingSpeed(initialRenderingSpeed);
    setAspectRatio(initialAspectRatio);
  }, [initialPrompt, initialStyle, initialRenderingSpeed, initialAspectRatio]);

  const handleRegenerate = () => {
    onRegenerate({
      prompt,
      style,
      renderingSpeed,
      aspectRatio,
    });
  };

  const applyPreset = (presetKey: PresetKey) => {
    const p = PRESETS[presetKey];
    // Combine the preset prompt with current scene prompt context
    setPrompt((current) => {
      // If user already customized, append; otherwise replace with preset
      if (!current || current.trim() === "" || current.trim() === initialPrompt.trim()) {
        return `${initialPrompt}\n${p.prompt}`.trim();
      }
      return `${current}\n${p.prompt}`.trim();
    });
    setStyle(p.style);
    setRenderingSpeed(p.renderingSpeed);
    setAspectRatio(p.aspectRatio);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: alpha("#0f172a", 0.95),
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 4,
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" sx={{ color: "white", fontWeight: 600 }}>
            Regenerate Image with Custom Settings
          </Typography>
          <IconButton
            onClick={onClose}
            size="small"
            sx={{ color: "rgba(255,255,255,0.7)" }}
          >
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.6)", mt: 1 }}>
          Customize the image generation parameters to get the perfect result for your scene
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          {/* Presets */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Podcast-ready presets
              </Typography>
              <Tooltip
                title="Quickly apply a podcast-friendly look. Each preset adjusts lighting, background, and ratio while keeping your base avatar consistent."
                arrow
              >
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
              {(
                Object.entries(PRESETS) as Array<[PresetKey, (typeof PRESETS)[PresetKey]]>
              ).map(([key, p]) => (
                <Paper
                  key={key}
                  onClick={() => applyPreset(key)}
                  sx={{
                    p: 1.5,
                    flex: 1,
                    cursor: "pointer",
                    backgroundColor: alpha("#ffffff", 0.04),
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 2,
                    transition: "all 0.2s ease",
                    "&:hover": {
                      borderColor: "rgba(102,126,234,0.7)",
                      boxShadow: "0 8px 24px rgba(0,0,0,0.25)",
                      backgroundColor: alpha("#667eea", 0.08),
                    },
                  }}
                >
                  <Typography variant="subtitle2" sx={{ color: "white", fontWeight: 700 }}>
                    {p.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.5, mb: 0.75 }}>
                    {p.subtitle}
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ color: "rgba(255,255,255,0.6)", fontSize: "0.8rem" }}>
                    <Typography variant="caption">Style: {p.style}</Typography>
                    <Typography variant="caption">Speed: {p.renderingSpeed}</Typography>
                    <Typography variant="caption">AR: {p.aspectRatio}</Typography>
                  </Stack>
                </Paper>
              ))}
            </Stack>
          </Box>

          {/* Prompt Section */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Generation Prompt
              </Typography>
              <Tooltip
                title="The prompt describes what you want to see in the generated image. It should include scene context, visual elements, and style preferences. The AI will use this along with your base avatar to create a consistent character in the scene."
                arrow
              >
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <TextField
              fullWidth
              multiline
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the scene, visual elements, and style..."
              sx={{
                "& .MuiOutlinedInput-root": {
                  backgroundColor: alpha("#ffffff", 0.05),
                  color: "white",
                  "& fieldset": {
                    borderColor: "rgba(255,255,255,0.2)",
                  },
                  "&:hover fieldset": {
                    borderColor: "rgba(255,255,255,0.3)",
                  },
                  "&.Mui-focused fieldset": {
                    borderColor: "#667eea",
                  },
                },
                "& .MuiInputBase-input": {
                  color: "white",
                },
              }}
            />
            <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.5)", mt: 0.5, display: "block" }}>
              This prompt will be combined with scene context to generate your image. Be specific about visual elements, mood, and composition.
            </Typography>
          </Box>

          <Divider sx={{ borderColor: "rgba(255,255,255,0.1)" }} />

          {/* Style Selection */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Character Style
              </Typography>
              <Tooltip
                title="Determines the artistic style of the character generation. Auto lets the AI choose, Fiction creates more stylized/artistic characters, and Realistic produces photorealistic results."
                arrow
              >
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <FormControl fullWidth>
              <Select
                value={style}
                onChange={(e) => setStyle(e.target.value as "Auto" | "Fiction" | "Realistic")}
                sx={{
                  backgroundColor: alpha("#ffffff", 0.05),
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(255,255,255,0.2)",
                  },
                  "&:hover .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(255,255,255,0.3)",
                  },
                  "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                    borderColor: "#667eea",
                  },
                  "& .MuiSvgIcon-root": {
                    color: "rgba(255,255,255,0.7)",
                  },
                }}
              >
                <MenuItem value="Auto">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Auto</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      AI automatically selects the best style
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="Fiction">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Fiction</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Stylized, artistic character appearance
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="Realistic">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Realistic</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Photorealistic, professional appearance
                    </Typography>
                  </Stack>
                </MenuItem>
              </Select>
            </FormControl>
            <Paper
              sx={{
                mt: 1.5,
                p: 1.5,
                backgroundColor: alpha("#667eea", 0.1),
                border: "1px solid rgba(102,126,234,0.3)",
                borderRadius: 2,
              }}
            >
              <Stack direction="row" spacing={1}>
                <InfoIcon sx={{ color: "#667eea", fontSize: "1.2rem", mt: 0.1 }} />
                <Box>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.9)", fontWeight: 500, mb: 0.5 }}>
                    Style Impact:
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>
                    <strong>Auto:</strong> Best for most cases, balances realism and style<br />
                    <strong>Fiction:</strong> Great for creative, artistic podcasts with stylized visuals<br />
                    <strong>Realistic:</strong> Ideal for professional, corporate, or news-style podcasts
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Box>

          {/* Rendering Speed */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Rendering Speed
              </Typography>
              <Tooltip
                title="Controls the balance between generation speed, cost, and quality. Turbo is fastest and cheapest but lower quality. Quality is slowest and most expensive but produces the best results. Default provides a balanced approach."
                arrow
              >
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <FormControl fullWidth>
              <Select
                value={renderingSpeed}
                onChange={(e) => setRenderingSpeed(e.target.value as "Default" | "Turbo" | "Quality")}
                sx={{
                  backgroundColor: alpha("#ffffff", 0.05),
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(255,255,255,0.2)",
                  },
                  "&:hover .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(255,255,255,0.3)",
                  },
                  "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                    borderColor: "#667eea",
                  },
                  "& .MuiSvgIcon-root": {
                    color: "rgba(255,255,255,0.7)",
                  },
                }}
              >
                <MenuItem value="Turbo">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Turbo ⚡</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Fastest (~10-20s) • Cheapest • Lower quality
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="Default">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Default ⚖️</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Balanced (~30-60s) • Moderate cost • Good quality
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="Quality">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Quality ✨</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Slowest (~60-120s) • Most expensive • Highest quality
                    </Typography>
                  </Stack>
                </MenuItem>
              </Select>
            </FormControl>
            <Paper
              sx={{
                mt: 1.5,
                p: 1.5,
                backgroundColor: alpha("#10b981", 0.1),
                border: "1px solid rgba(16,185,129,0.3)",
                borderRadius: 2,
              }}
            >
              <Stack direction="row" spacing={1}>
                <InfoIcon sx={{ color: "#10b981", fontSize: "1.2rem", mt: 0.1 }} />
                <Box>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.9)", fontWeight: 500, mb: 0.5 }}>
                    Speed vs Quality Trade-off:
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>
                    <strong>Turbo:</strong> Use for quick iterations and testing (~$0.02/image)<br />
                    <strong>Default:</strong> Best balance for most production use (~$0.04/image)<br />
                    <strong>Quality:</strong> Use for final, high-quality outputs (~$0.08/image)
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Box>

          {/* Aspect Ratio */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Aspect Ratio
              </Typography>
              <Tooltip
                title="The width-to-height ratio of the generated image. Choose based on your video format: 16:9 for standard widescreen, 9:16 for vertical/social media, 1:1 for square formats, or 4:3 for traditional formats."
                arrow
              >
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <FormControl fullWidth>
              <Select
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value as "1:1" | "16:9" | "9:16" | "4:3" | "3:4")}
                sx={{
                  backgroundColor: alpha("#ffffff", 0.05),
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(255,255,255,0.2)",
                  },
                  "&:hover .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(255,255,255,0.3)",
                  },
                  "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                    borderColor: "#667eea",
                  },
                  "& .MuiSvgIcon-root": {
                    color: "rgba(255,255,255,0.7)",
                  },
                }}
              >
                <MenuItem value="16:9">
                  <Stack>
                    <Typography sx={{ color: "white" }}>16:9 (Widescreen)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Standard video format, best for YouTube, web
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="9:16">
                  <Stack>
                    <Typography sx={{ color: "white" }}>9:16 (Vertical)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Mobile/social media format (TikTok, Instagram Stories)
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="1:1">
                  <Stack>
                    <Typography sx={{ color: "white" }}>1:1 (Square)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Instagram posts, profile images
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="4:3">
                  <Stack>
                    <Typography sx={{ color: "white" }}>4:3 (Traditional)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Classic TV format, presentations
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="3:4">
                  <Stack>
                    <Typography sx={{ color: "white" }}>3:4 (Portrait)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Portrait orientation, mobile apps
                    </Typography>
                  </Stack>
                </MenuItem>
              </Select>
            </FormControl>
            <Paper
              sx={{
                mt: 1.5,
                p: 1.5,
                backgroundColor: alpha("#f59e0b", 0.1),
                border: "1px solid rgba(245,158,11,0.3)",
                borderRadius: 2,
              }}
            >
              <Stack direction="row" spacing={1}>
                <InfoIcon sx={{ color: "#f59e0b", fontSize: "1.2rem", mt: 0.1 }} />
                <Box>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.9)", fontWeight: 500, mb: 0.5 }}>
                    Format Recommendation:
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>
                    <strong>16:9</strong> is recommended for most podcast videos as it matches standard video player dimensions and provides optimal viewing experience.
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Box>
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <SecondaryButton onClick={onClose} disabled={isGenerating}>
          Cancel
        </SecondaryButton>
        <PrimaryButton
          onClick={handleRegenerate}
          loading={isGenerating}
          disabled={!prompt.trim() || isGenerating}
        >
          {isGenerating ? "Generating..." : "Regenerate Image"}
        </PrimaryButton>
      </DialogActions>
    </Dialog>
  );
};

