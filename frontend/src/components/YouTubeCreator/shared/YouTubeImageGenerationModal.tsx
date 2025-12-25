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
  Palette as PaletteIcon,
} from "@mui/icons-material";

type PresetKey = "engagingHost" | "cinematicScene" | "professionalPresenter" | "casualCreator";

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
  engagingHost: {
    title: "Engaging Host",
    subtitle: "Dynamic presenter in engaging video environment",
    prompt:
      "Professional video host in modern studio, dynamic lighting, engaging facial expression, high energy atmosphere, camera-ready appearance, confident posture, vibrant background elements",
    style: "Realistic",
    renderingSpeed: "Quality",
    aspectRatio: "16:9",
  },
  cinematicScene: {
    title: "Cinematic Scene",
    subtitle: "Dramatic, movie-like atmosphere with cinematic lighting",
    prompt:
      "Cinematic video scene, dramatic lighting, professional cinematography, engaging narrative atmosphere, high production value, cinematic depth of field, compelling visual storytelling",
    style: "Realistic",
    renderingSpeed: "Quality",
    aspectRatio: "16:9",
  },
  professionalPresenter: {
    title: "Professional Presenter",
    subtitle: "Corporate-style presentation with clean, polished look",
    prompt:
      "Professional corporate presenter, clean business attire, polished appearance, neutral background, professional lighting, trustworthy demeanor, business presentation setting",
    style: "Realistic",
    renderingSpeed: "Quality",
    aspectRatio: "16:9",
  },
  casualCreator: {
    title: "Casual Creator",
    subtitle: "Relaxed, approachable creator for vlogs and tutorials",
    prompt:
      "Casual content creator, friendly and approachable, comfortable setting, natural lighting, relaxed posture, authentic personality, everyday environment, genuine smile",
    style: "Realistic",
    renderingSpeed: "Quality",
    aspectRatio: "16:9",
  },
};

export interface YouTubeImageGenerationSettings {
  prompt: string;
  style: "Auto" | "Fiction" | "Realistic";
  renderingSpeed: "Default" | "Turbo" | "Quality";
  aspectRatio: "1:1" | "16:9" | "9:16" | "4:3" | "3:4";
  model: "ideogram-v3-turbo" | "qwen-image";
}

interface YouTubeImageGenerationModalProps {
  open: boolean;
  onClose: () => void;
  onGenerate: (settings: YouTubeImageGenerationSettings) => void;
  initialPrompt: string;
  initialStyle?: "Auto" | "Fiction" | "Realistic";
  initialRenderingSpeed?: "Default" | "Turbo" | "Quality";
  initialAspectRatio?: "1:1" | "16:9" | "9:16" | "4:3" | "3:4";
  initialModel?: "ideogram-v3-turbo" | "qwen-image";
  isGenerating?: boolean;
  sceneTitle?: string;
}

export const YouTubeImageGenerationModal: React.FC<YouTubeImageGenerationModalProps> = ({
  open,
  onClose,
  onGenerate,
  initialPrompt,
  initialStyle = "Realistic",
  initialRenderingSpeed = "Quality",
  initialAspectRatio = "16:9",
  initialModel = "ideogram-v3-turbo",
  isGenerating = false,
  sceneTitle,
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [style, setStyle] = useState<"Auto" | "Fiction" | "Realistic">(initialStyle);
  const [renderingSpeed, setRenderingSpeed] = useState<"Default" | "Turbo" | "Quality">(initialRenderingSpeed);
  const [aspectRatio, setAspectRatio] = useState<"1:1" | "16:9" | "9:16" | "4:3" | "3:4">(initialAspectRatio);
  const [model, setModel] = useState<"ideogram-v3-turbo" | "qwen-image">("ideogram-v3-turbo");

  // Update state when initial values change
  useEffect(() => {
    setPrompt(initialPrompt);
    setStyle(initialStyle);
    setRenderingSpeed(initialRenderingSpeed);
    setAspectRatio(initialAspectRatio);
    setModel(initialModel);
  }, [initialPrompt, initialStyle, initialRenderingSpeed, initialAspectRatio, initialModel]);

  const handleGenerate = () => {
    onGenerate({
      prompt,
      style,
      renderingSpeed,
      aspectRatio,
      model,
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
          background: alpha("#1a1a2e", 0.95),
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 4,
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" sx={{ color: "white", fontWeight: 600 }}>
              Generate Scene Image
            </Typography>
            {sceneTitle && (
              <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.6)", mt: 1 }}>
                Customize image generation for "{sceneTitle}"
              </Typography>
            )}
          </Box>
          <IconButton
            onClick={onClose}
            size="small"
            sx={{ color: "rgba(255,255,255,0.7)" }}
          >
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.6)", mt: 1 }}>
          Customize image generation parameters for the perfect YouTube scene visual
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          {/* YouTube-optimized Presets */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <PaletteIcon sx={{ color: "white", fontSize: "1.2rem" }} />
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                YouTube-ready presets
              </Typography>
              <Tooltip
                title="Quickly apply a YouTube-optimized look. Each preset adjusts lighting, composition, and style while keeping your avatar consistent."
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
                Visual Prompt
              </Typography>
              <Tooltip
                title="Describe what you want to see in the generated image. Include scene context, visual elements, mood, and style preferences. The AI will use this along with your base avatar to create a consistent character in the YouTube scene."
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
              placeholder="Describe the scene, visual elements, mood, and style..."
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
              This prompt will be combined with scene context to generate your YouTube-ready image. Be specific about visual elements, lighting, and atmosphere.
            </Typography>
          </Box>

          <Divider sx={{ borderColor: "rgba(255,255,255,0.1)" }} />

          {/* Style Selection */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Visual Style
              </Typography>
              <Tooltip
                title="Determines the artistic style of the character generation. Auto lets the AI choose, Fiction creates more stylized/artistic characters, and Realistic produces photorealistic results optimized for video content."
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
                      Photorealistic, professional video appearance
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
                    Style Impact for YouTube:
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>
                    <strong>Auto:</strong> Best for most YouTube content, balances professionalism and engagement<br />
                    <strong>Fiction:</strong> Great for creative content, gaming, or stylized presentations<br />
                    <strong>Realistic:</strong> Ideal for educational, corporate, or professional YouTube channels
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Box>

          {/* Rendering Speed */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Generation Speed
              </Typography>
              <Tooltip
                title="Controls the balance between generation speed, cost, and quality. Turbo is fastest and cheapest but lower quality. Quality is slowest and most expensive but produces the best results for professional YouTube content."
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
                      Fastest (~10-20s) • Cheapest • Good for quick iterations
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="Default">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Default ⚖️</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Balanced (~30-60s) • Moderate cost • Great for most YouTube content
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="Quality">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Quality ✨</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Slowest (~60-120s) • Highest quality • Perfect for professional videos
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
                    Speed vs Quality for YouTube:
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>
                    <strong>Turbo:</strong> Use for testing and quick iterations (~$0.02/image)<br />
                    <strong>Default:</strong> Best balance for regular YouTube production (~$0.04/image)<br />
                    <strong>Quality:</strong> Use for high-stakes, professional content (~$0.08/image)
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Box>

          {/* AI Model Selection */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                AI Model
              </Typography>
              <Tooltip
                title="Choose the AI model for image generation. Different models offer different quality levels and costs. Ideogram V3 Turbo provides superior text rendering and photorealism."
                arrow
              >
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <FormControl fullWidth>
              <Select
                value={model}
                onChange={(e) => setModel(e.target.value as "ideogram-v3-turbo" | "qwen-image")}
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
                <MenuItem value="ideogram-v3-turbo">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Ideogram V3 Turbo ✨</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Photorealistic • Superior text rendering • $0.10/image
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="qwen-image">
                  <Stack>
                    <Typography sx={{ color: "white" }}>Qwen Image ⚡</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Fast generation • High quality • $0.05/image
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
                    Model Recommendations:
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>
                    <strong>Ideogram V3 Turbo:</strong> Best for professional YouTube content with text, logos, or detailed scenes<br />
                    <strong>Qwen Image:</strong> Great for fast iterations and general content creation
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
                title="The width-to-height ratio of the generated image. Choose based on your YouTube format: 16:9 for standard videos, 9:16 for Shorts/mobile, 1:1 for thumbnails, or other formats as needed."
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
                      Standard YouTube videos, best for main content
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="9:16">
                  <Stack>
                    <Typography sx={{ color: "white" }}>9:16 (Vertical)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      YouTube Shorts, TikTok, Instagram Stories
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="1:1">
                  <Stack>
                    <Typography sx={{ color: "white" }}>1:1 (Square)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Thumbnails, Instagram posts, profile images
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="4:3">
                  <Stack>
                    <Typography sx={{ color: "white" }}>4:3 (Traditional)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      Classic format, presentations, older content
                    </Typography>
                  </Stack>
                </MenuItem>
                <MenuItem value="3:4">
                  <Stack>
                    <Typography sx={{ color: "white" }}>3:4 (Portrait)</Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                      LinkedIn, some social media formats
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
                    YouTube Format Recommendations:
                  </Typography>
                  <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>
                    <strong>16:9:</strong> Standard videos (recommended for most content)<br />
                    <strong>9:16:</strong> YouTube Shorts and mobile-optimized content<br />
                    <strong>1:1:</strong> Thumbnails and square-format promotional content
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Box>
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <IconButton
          onClick={onClose}
          disabled={isGenerating}
          sx={{ color: "rgba(255,255,255,0.7)", mr: 1 }}
        >
          <CloseIcon />
        </IconButton>
        <Box sx={{ flex: 1 }} />
        <IconButton
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          sx={{
            backgroundColor: isGenerating ? "rgba(255,255,255,0.1)" : "#667eea",
            color: "white",
            "&:hover": {
              backgroundColor: isGenerating ? "rgba(255,255,255,0.1)" : "#5a6fd8",
            },
            "&:disabled": {
              backgroundColor: "rgba(255,255,255,0.1)",
              color: "rgba(255,255,255,0.3)",
            },
            px: 3,
            py: 1,
            borderRadius: 2,
          }}
        >
          <Typography variant="button" sx={{ fontWeight: 600 }}>
            {isGenerating ? "Generating..." : "Generate Image"}
          </Typography>
        </IconButton>
      </DialogActions>
    </Dialog>
  );
};
