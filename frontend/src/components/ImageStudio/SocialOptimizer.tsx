import React, { useState, useMemo, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Stack,
  Typography,
  Button,
  Alert,
  Checkbox,
  FormControlLabel,
  ToggleButtonGroup,
  ToggleButton,
  Chip,
  Card,
  CardContent,
  CardMedia,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import ShareIcon from '@mui/icons-material/Share';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/DeleteOutline';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { motion, type Variants, type Easing } from 'framer-motion';
import { useImageStudio, PlatformFormat } from '../../hooks/useImageStudio';
import { ImageStudioLayout } from './ImageStudioLayout';
import { OperationButton } from '../shared/OperationButton';

const MotionPaper = motion(Paper);
const fadeEase: Easing = [0.4, 0, 0.2, 1];

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: fadeEase },
  },
};

const PLATFORMS = [
  { value: 'instagram', label: 'Instagram', icon: '📷' },
  { value: 'facebook', label: 'Facebook', icon: '👥' },
  { value: 'twitter', label: 'Twitter/X', icon: '🐦' },
  { value: 'linkedin', label: 'LinkedIn', icon: '💼' },
  { value: 'youtube', label: 'YouTube', icon: '📺' },
  { value: 'pinterest', label: 'Pinterest', icon: '📌' },
  { value: 'tiktok', label: 'TikTok', icon: '🎵' },
];

const CROP_MODES = [
  { value: 'smart', label: 'Smart Crop', description: 'Preserve important content' },
  { value: 'center', label: 'Center Crop', description: 'Crop from center' },
  { value: 'fit', label: 'Fit', description: 'Fit with padding' },
];

const readFileAsDataURL = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

export const SocialOptimizer: React.FC = () => {
  const {
    optimizeForSocial,
    getPlatformFormats,
    isOptimizing,
    optimizeResult,
    optimizeError,
    clearOptimizeResult,
  } = useImageStudio();

  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [formatSelections, setFormatSelections] = useState<Record<string, string>>({});
  const [platformFormats, setPlatformFormats] = useState<Record<string, PlatformFormat[]>>({});
  const [cropMode, setCropMode] = useState<string>('smart');
  const [showSafeZones, setShowSafeZones] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // Load formats when platforms are selected
  useEffect(() => {
    const loadFormats = async () => {
      const formats: Record<string, PlatformFormat[]> = {};
      for (const platform of selectedPlatforms) {
        if (!platformFormats[platform]) {
          const formatsList = await getPlatformFormats(platform);
          formats[platform] = formatsList;
        }
      }
      if (Object.keys(formats).length > 0) {
        setPlatformFormats((prev) => ({ ...prev, ...formats }));
        // Set default format for each platform
        setFormatSelections((prev) => {
          const updated = { ...prev };
          Object.entries(formats).forEach(([platform, formatList]) => {
            if (!updated[platform] && formatList.length > 0) {
              updated[platform] = formatList[0].name;
            }
          });
          return updated;
        });
      }
    };
    if (selectedPlatforms.length > 0) {
      loadFormats();
    }
  }, [selectedPlatforms, getPlatformFormats]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const dataUrl = await readFileAsDataURL(file);
      setSourceImage(dataUrl);
      clearOptimizeResult();
      setLocalError(null);
    } catch (err) {
      setLocalError('Failed to read image file');
    }
  };

  const handlePlatformToggle = (platform: string) => {
    setSelectedPlatforms((prev) => {
      if (prev.includes(platform)) {
        const updated = prev.filter((p) => p !== platform);
        const newSelections = { ...formatSelections };
        delete newSelections[platform];
        setFormatSelections(newSelections);
        return updated;
      } else {
        return [...prev, platform];
      }
    });
  };

  const handleOptimize = async () => {
    setLocalError(null);
    if (!sourceImage) {
      setLocalError('Please upload a source image.');
      return;
    }
    if (selectedPlatforms.length === 0) {
      setLocalError('Please select at least one platform.');
      return;
    }

    try {
      const formatNames: Record<string, string> = {};
      selectedPlatforms.forEach((platform) => {
        const format = formatSelections[platform];
        if (format) {
          formatNames[platform] = format;
        }
      });

      await optimizeForSocial({
        image_base64: sourceImage,
        platforms: selectedPlatforms,
        format_names: Object.keys(formatNames).length > 0 ? formatNames : undefined,
        show_safe_zones: showSafeZones,
        crop_mode: cropMode,
        output_format: 'png',
      });
    } catch {
      // Error handled in hook
    }
  };

  const handleDownload = (imageBase64: string, filename: string) => {
    const link = document.createElement('a');
    link.href = imageBase64;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadAll = () => {
    if (!optimizeResult) return;
    optimizeResult.results.forEach((result, index) => {
      const filename = `${result.platform}_${result.format.replace(/\s+/g, '_')}_${index + 1}.png`;
      handleDownload(result.image_base64, filename);
    });
  };

  const canOptimize = sourceImage && selectedPlatforms.length > 0 && !isOptimizing;

  const socialOperation = useMemo(
    () => ({
      provider: 'internal',
      operation_type: 'image_processing',
      actual_provider_name: 'internal',
    }),
    []
  );

  return (
    <ImageStudioLayout>
      <MotionPaper
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        elevation={0}
        sx={{
          maxWidth: 1400,
          mx: 'auto',
          background: 'rgba(15,23,42,0.7)',
          borderRadius: 4,
          border: '1px solid rgba(255,255,255,0.08)',
          p: { xs: 3, md: 4 },
          backdropFilter: 'blur(20px)',
        }}
      >
        <Stack spacing={0.5} mb={3}>
          <Typography
            variant="h4"
            fontWeight={800}
            sx={{
              background: 'linear-gradient(90deg, #ede9fe, #c7d2fe)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Social Optimizer
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Optimize images for all major social platforms with smart cropping, safe zones, and batch export.
          </Typography>
        </Stack>

        {(localError || optimizeError) && (
          <Alert
            severity="error"
            sx={{ mb: 3 }}
            onClose={() => {
              setLocalError(null);
            }}
          >
            {localError || optimizeError}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Stack spacing={3}>
              {/* Image Upload */}
              <Paper
                variant="outlined"
                sx={{
                  borderRadius: 3,
                  background: alpha('#0f172a', 0.7),
                  borderColor: 'rgba(255,255,255,0.05)',
                  p: 3,
                }}
              >
                <Stack spacing={2}>
                  <Typography variant="subtitle1" fontWeight={700}>
                    Source Image
                  </Typography>
                  {sourceImage ? (
                    <Box sx={{ position: 'relative' }}>
                      <Box
                        sx={{
                          borderRadius: 2,
                          overflow: 'hidden',
                          border: '1px solid rgba(255,255,255,0.2)',
                        }}
                      >
                        <img
                          src={sourceImage}
                          alt="Source"
                          style={{ width: '100%', display: 'block' }}
                        />
                      </Box>
                      <IconButton
                        onClick={() => {
                          setSourceImage(null);
                          clearOptimizeResult();
                        }}
                        sx={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          bgcolor: alpha('#000', 0.5),
                          color: '#fff',
                          '&:hover': { bgcolor: alpha('#000', 0.7) },
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  ) : (
                    <Button
                      component="label"
                      variant="outlined"
                      startIcon={<CloudUploadIcon />}
                      fullWidth
                      sx={{
                        borderStyle: 'dashed',
                        borderColor: alpha('#667eea', 0.5),
                        color: 'text.secondary',
                        py: 3,
                        '&:hover': {
                          borderColor: alpha('#667eea', 0.8),
                          background: alpha('#667eea', 0.05),
                        },
                      }}
                    >
                      Upload Image
                      <input type="file" accept="image/*" hidden onChange={handleFileUpload} />
                    </Button>
                  )}
                </Stack>
              </Paper>

              {/* Platform Selection */}
              <Paper
                variant="outlined"
                sx={{
                  borderRadius: 3,
                  background: alpha('#0f172a', 0.7),
                  borderColor: 'rgba(255,255,255,0.05)',
                  p: 3,
                }}
              >
                <Stack spacing={2}>
                  <Typography variant="subtitle1" fontWeight={700}>
                    Select Platforms
                  </Typography>
                  <Stack spacing={1}>
                    {PLATFORMS.map((platform) => (
                      <FormControlLabel
                        key={platform.value}
                        control={
                          <Checkbox
                            checked={selectedPlatforms.includes(platform.value)}
                            onChange={() => handlePlatformToggle(platform.value)}
                            sx={{ color: '#667eea' }}
                          />
                        }
                        label={
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Typography>{platform.icon}</Typography>
                            <Typography>{platform.label}</Typography>
                          </Stack>
                        }
                      />
                    ))}
                  </Stack>
                </Stack>
              </Paper>

              {/* Format Selection */}
              {selectedPlatforms.length > 0 && (
                <Paper
                  variant="outlined"
                  sx={{
                    borderRadius: 3,
                    background: alpha('#0f172a', 0.7),
                    borderColor: 'rgba(255,255,255,0.05)',
                    p: 3,
                  }}
                >
                  <Stack spacing={2}>
                    <Typography variant="subtitle1" fontWeight={700}>
                      Format Selection
                    </Typography>
                    {selectedPlatforms.map((platform) => {
                      const formats = platformFormats[platform] || [];
                      if (formats.length === 0) return null;
                      return (
                        <FormControl key={platform} fullWidth size="small">
                          <InputLabel>{PLATFORMS.find((p) => p.value === platform)?.label}</InputLabel>
                          <Select
                            value={formatSelections[platform] || formats[0].name}
                            label={PLATFORMS.find((p) => p.value === platform)?.label}
                            onChange={(e) =>
                              setFormatSelections((prev) => ({
                                ...prev,
                                [platform]: e.target.value,
                              }))
                            }
                          >
                            {formats.map((format) => (
                              <MenuItem key={format.name} value={format.name}>
                                {format.name} ({format.width}x{format.height})
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      );
                    })}
                  </Stack>
                </Paper>
              )}

              {/* Options */}
              <Paper
                variant="outlined"
                sx={{
                  borderRadius: 3,
                  background: alpha('#0f172a', 0.7),
                  borderColor: 'rgba(255,255,255,0.05)',
                  p: 3,
                }}
              >
                <Stack spacing={2}>
                  <Typography variant="subtitle1" fontWeight={700}>
                    Options
                  </Typography>
                  <Box>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Crop Mode
                    </Typography>
                    <ToggleButtonGroup
                      value={cropMode}
                      exclusive
                      onChange={(_, value) => value && setCropMode(value)}
                      fullWidth
                      size="small"
                    >
                      {CROP_MODES.map((mode) => (
                        <ToggleButton key={mode.value} value={mode.value}>
                          <Stack spacing={0.5} alignItems="center">
                            <Typography variant="caption" fontWeight={600}>
                              {mode.label}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
                              {mode.description}
                            </Typography>
                          </Stack>
                        </ToggleButton>
                      ))}
                    </ToggleButtonGroup>
                  </Box>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={showSafeZones}
                        onChange={(e) => setShowSafeZones(e.target.checked)}
                        sx={{ color: '#667eea' }}
                      />
                    }
                    label={
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Typography>Show Safe Zones</Typography>
                        <Tooltip title="Display text safe zone overlays on optimized images">
                          <IconButton size="small" sx={{ p: 0.5 }}>
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    }
                  />
                </Stack>
              </Paper>

              <OperationButton
                operation={socialOperation}
                label="Optimize Images"
                startIcon={<ShareIcon />}
                onClick={handleOptimize}
                disabled={!canOptimize}
                loading={isOptimizing}
                checkOnMount={false}
                showCost={false}
                sx={{
                  borderRadius: 999,
                  alignSelf: 'flex-start',
                  px: 4,
                  py: 1.5,
                  textTransform: 'none',
                  fontWeight: 700,
                  background: 'linear-gradient(90deg, #7c3aed, #2563eb)',
                }}
              />
            </Stack>
          </Grid>

          <Grid item xs={12} md={8}>
            {optimizeResult && optimizeResult.results.length > 0 && (
              <Stack spacing={3}>
                <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
                  <Typography variant="h6" fontWeight={700}>
                    Optimized Images ({optimizeResult.total_optimized})
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownloadAll}
                    sx={{ borderRadius: 999 }}
                  >
                    Download All
                  </Button>
                </Stack>
                <Grid container spacing={2}>
                  {optimizeResult.results.map((result, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Card
                        sx={{
                          borderRadius: 2,
                          background: alpha('#0f172a', 0.7),
                          border: '1px solid rgba(255,255,255,0.1)',
                        }}
                      >
                        <CardMedia
                          component="img"
                          image={result.image_base64}
                          alt={`${result.platform} ${result.format}`}
                          sx={{ height: 200, objectFit: 'contain' }}
                        />
                        <CardContent>
                          <Stack spacing={1}>
                            <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                              <Chip
                                label={result.platform}
                                size="small"
                                sx={{
                                  bgcolor: alpha('#667eea', 0.2),
                                  color: '#c7d2fe',
                                }}
                              />
                              <Chip
                                label={`${result.width}x${result.height}`}
                                size="small"
                                variant="outlined"
                              />
                            </Stack>
                            <Typography variant="caption" color="text.secondary">
                              {result.format}
                            </Typography>
                            <Button
                              size="small"
                              startIcon={<DownloadIcon />}
                              onClick={() =>
                                handleDownload(
                                  result.image_base64,
                                  `${result.platform}_${result.format.replace(/\s+/g, '_')}.png`
                                )
                              }
                              fullWidth
                              sx={{ mt: 1 }}
                            >
                              Download
                            </Button>
                          </Stack>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Stack>
            )}
            {!optimizeResult && (
              <Paper
                variant="outlined"
                sx={{
                  borderRadius: 3,
                  background: alpha('#0f172a', 0.5),
                  borderColor: 'rgba(255,255,255,0.05)',
                  p: 6,
                  textAlign: 'center',
                }}
              >
                <Typography variant="body1" color="text.secondary">
                  Upload an image and select platforms to see optimized results here.
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </MotionPaper>
    </ImageStudioLayout>
  );
};

