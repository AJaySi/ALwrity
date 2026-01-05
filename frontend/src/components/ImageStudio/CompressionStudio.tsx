import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Stack,
  Typography,
  TextField,
  Alert,
  Slider,
  Divider,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  CircularProgress,
  Button,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import CompressIcon from '@mui/icons-material/Compress';
import UploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import InfoIcon from '@mui/icons-material/Info';
import { motion, type Variants, type Easing } from 'framer-motion';
import {
  useImageStudio,
  CompressionRequest,
} from '../../hooks/useImageStudio';
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

const readFileAsDataURL = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

export const CompressionStudio: React.FC = () => {
  const {
    compressionFormats,
    compressionPresets,
    loadCompressionFormats,
    loadCompressionPresets,
    estimateCompression,
    processCompression,
    isCompressing,
    compressionResult,
    compressionError,
    compressionEstimate,
    clearCompressionResult,
  } = useImageStudio();

  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [originalSize, setOriginalSize] = useState<number>(0);
  const [quality, setQuality] = useState<number>(85);
  const [format, setFormat] = useState<string>('jpeg');
  const [targetSizeEnabled, setTargetSizeEnabled] = useState(false);
  const [targetSizeKb, setTargetSizeKb] = useState<number>(200);
  const [stripMetadata, setStripMetadata] = useState(true);
  const [progressive, setProgressive] = useState(true);
  const [optimize, setOptimize] = useState(true);
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    loadCompressionFormats();
    loadCompressionPresets();
  }, [loadCompressionFormats, loadCompressionPresets]);

  // Auto-estimate when image or settings change
  useEffect(() => {
    if (sourceImage && !isCompressing) {
      const timer = setTimeout(() => {
        estimateCompression(sourceImage, format, quality);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [sourceImage, format, quality, estimateCompression, isCompressing]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setOriginalSize(file.size / 1024); // KB
    const dataUrl = await readFileAsDataURL(file);
    setSourceImage(dataUrl);
    clearCompressionResult();
    setLocalError(null);
  };

  const handlePresetSelect = (presetId: string) => {
    const preset = compressionPresets.find(p => p.id === presetId);
    if (preset) {
      setSelectedPreset(presetId);
      setFormat(preset.format);
      setQuality(preset.quality);
      setStripMetadata(preset.strip_metadata);
      if (preset.target_size_kb) {
        setTargetSizeEnabled(true);
        setTargetSizeKb(preset.target_size_kb);
      } else {
        setTargetSizeEnabled(false);
      }
    }
  };

  const handleCompress = async () => {
    if (!sourceImage) {
      setLocalError('Please upload an image first.');
      return;
    }

    setLocalError(null);
    try {
      const request: CompressionRequest = {
        image_base64: sourceImage,
        quality,
        format,
        target_size_kb: targetSizeEnabled ? targetSizeKb : undefined,
        strip_metadata: stripMetadata,
        progressive,
        optimize,
      };
      await processCompression(request);
    } catch {
      // Error handled in hook
    }
  };

  const handleDownload = () => {
    if (!compressionResult?.image_base64) return;
    const link = document.createElement('a');
    link.href = compressionResult.image_base64;
    link.download = `compressed-image.${compressionResult.format}`;
    link.click();
  };

  const handleReset = () => {
    setSourceImage(null);
    setOriginalSize(0);
    clearCompressionResult();
    setLocalError(null);
    setSelectedPreset('');
  };

  const currentFormat = compressionFormats.find(f => f.id === format);

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
            Compression Studio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Optimize images for web, email, and social media with smart compression.
          </Typography>
        </Stack>

        {(localError || compressionError) && (
          <Alert
            severity="error"
            sx={{ mb: 3 }}
            onClose={() => setLocalError(null)}
          >
            {localError || compressionError}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Left Panel - Settings */}
          <Grid item xs={12} md={5}>
            <Stack spacing={3}>
              {/* Image Upload */}
              <Card
                variant="outlined"
                sx={{
                  borderRadius: 3,
                  borderStyle: sourceImage ? 'solid' : 'dashed',
                  borderColor: sourceImage ? alpha('#667eea', 0.4) : alpha('#cbd5f5', 0.8),
                  background: sourceImage ? alpha('#667eea', 0.08) : alpha('#667eea', 0.02),
                }}
              >
                <CardContent>
                  <Stack spacing={2}>
                    <Stack direction="row" alignItems="center" justifyContent="space-between">
                      <Typography variant="subtitle2" fontWeight={700}>
                        Source Image
                      </Typography>
                      {sourceImage && (
                        <Tooltip title="Remove">
                          <IconButton size="small" onClick={() => {
                            setSourceImage(null);
                            setOriginalSize(0);
                            clearCompressionResult();
                          }}>
                            <RestartAltIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Stack>
                    {sourceImage ? (
                      <Box sx={{ borderRadius: 2, overflow: 'hidden' }}>
                        <img
                          src={sourceImage}
                          alt="Source"
                          style={{ width: '100%', maxHeight: 200, objectFit: 'contain' }}
                        />
                        <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                          Original size: {originalSize.toFixed(2)} KB
                        </Typography>
                      </Box>
                    ) : (
                      <Button
                        variant="outlined"
                        component="label"
                        startIcon={<UploadIcon />}
                        sx={{
                          borderRadius: 2,
                          borderStyle: 'dashed',
                          py: 3,
                          color: '#667eea',
                          borderColor: alpha('#667eea', 0.6),
                        }}
                      >
                        Upload Image
                        <input hidden type="file" accept="image/*" onChange={handleFileUpload} />
                      </Button>
                    )}
                  </Stack>
                </CardContent>
              </Card>

              <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

              {/* Presets */}
              <Stack spacing={1.5}>
                <Typography variant="subtitle1" fontWeight={700}>
                  Quick Presets
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {compressionPresets.map((preset) => (
                    <Chip
                      key={preset.id}
                      label={preset.name}
                      onClick={() => handlePresetSelect(preset.id)}
                      variant={selectedPreset === preset.id ? 'filled' : 'outlined'}
                      sx={{
                        borderColor: selectedPreset === preset.id ? '#667eea' : 'rgba(255,255,255,0.2)',
                        bgcolor: selectedPreset === preset.id ? alpha('#667eea', 0.2) : 'transparent',
                        color: selectedPreset === preset.id ? '#667eea' : 'inherit',
                      }}
                    />
                  ))}
                </Stack>
              </Stack>

              <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

              {/* Format Selection */}
              <FormControl fullWidth>
                <InputLabel>Output Format</InputLabel>
                <Select
                  value={format}
                  label="Output Format"
                  onChange={(e) => {
                    setFormat(e.target.value);
                    setSelectedPreset('');
                  }}
                >
                  {compressionFormats.map((fmt) => (
                    <MenuItem key={fmt.id} value={fmt.id}>
                      <Stack>
                        <Typography variant="body2">{fmt.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {fmt.description}
                        </Typography>
                      </Stack>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Quality Slider */}
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="subtitle2" fontWeight={600}>
                    Quality
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {quality}%
                  </Typography>
                </Stack>
                <Slider
                  value={quality}
                  onChange={(_, val) => {
                    setQuality(val as number);
                    setSelectedPreset('');
                  }}
                  min={1}
                  max={100}
                  sx={{ color: '#667eea' }}
                />
                <Typography variant="caption" color="text.secondary">
                  Lower quality = smaller file size. Recommended: 80-85 for web.
                </Typography>
              </Stack>

              {/* Target Size */}
              <Stack spacing={1}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={targetSizeEnabled}
                      onChange={(e) => setTargetSizeEnabled(e.target.checked)}
                      sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: '#667eea' } }}
                    />
                  }
                  label="Target file size"
                />
                {targetSizeEnabled && (
                  <TextField
                    type="number"
                    value={targetSizeKb}
                    onChange={(e) => setTargetSizeKb(parseInt(e.target.value) || 100)}
                    InputProps={{
                      endAdornment: <Typography variant="caption">KB</Typography>,
                    }}
                    size="small"
                    helperText="Quality will auto-adjust to meet target size"
                  />
                )}
              </Stack>

              {/* Advanced Options */}
              <Stack spacing={1}>
                <Typography variant="subtitle2" fontWeight={600}>
                  Advanced Options
                </Typography>
                <FormControlLabel
                  control={<Switch checked={stripMetadata} onChange={(e) => setStripMetadata(e.target.checked)} size="small" />}
                  label={<Typography variant="body2">Strip metadata (EXIF)</Typography>}
                />
                {format === 'jpeg' && (
                  <FormControlLabel
                    control={<Switch checked={progressive} onChange={(e) => setProgressive(e.target.checked)} size="small" />}
                    label={<Typography variant="body2">Progressive JPEG</Typography>}
                  />
                )}
                <FormControlLabel
                  control={<Switch checked={optimize} onChange={(e) => setOptimize(e.target.checked)} size="small" />}
                  label={<Typography variant="body2">Optimize encoding</Typography>}
                />
              </Stack>
            </Stack>
          </Grid>

          {/* Right Panel - Results */}
          <Grid item xs={12} md={7}>
            <Stack spacing={3}>
              {/* Estimation */}
              {compressionEstimate && !compressionResult && (
                <Card sx={{ borderRadius: 3, background: 'rgba(255,255,255,0.05)' }}>
                  <CardContent>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <InfoIcon sx={{ color: '#667eea' }} />
                      <Box flex={1}>
                        <Typography variant="subtitle2">Estimated Result</Typography>
                        <Typography variant="body2" color="text.secondary">
                          ~{compressionEstimate.estimated_size_kb.toFixed(1)} KB ({compressionEstimate.estimated_reduction_percent.toFixed(0)}% smaller)
                        </Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              )}

              <OperationButton
                operation={{
                  provider: 'local',
                  operation_type: 'compress',
                  actual_provider_name: 'pillow',
                }}
                label="Compress Image"
                startIcon={<CompressIcon />}
                onClick={handleCompress}
                disabled={!sourceImage}
                loading={isCompressing}
                checkOnMount={false}
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

              {/* Result Viewer */}
              <Card
                sx={{
                  borderRadius: 3,
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  minHeight: 300,
                }}
              >
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" fontWeight={700}>
                      Results
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      <Tooltip title="Reset">
                        <span>
                          <IconButton disabled={!compressionResult && !sourceImage} onClick={handleReset}>
                            <RestartAltIcon />
                          </IconButton>
                        </span>
                      </Tooltip>
                      <Tooltip title="Download">
                        <span>
                          <IconButton disabled={!compressionResult} onClick={handleDownload}>
                            <DownloadIcon />
                          </IconButton>
                        </span>
                      </Tooltip>
                    </Stack>
                  </Stack>

                  {isCompressing ? (
                    <Stack alignItems="center" spacing={2} py={6}>
                      <CircularProgress />
                      <Typography variant="body2" color="text.secondary">
                        Compressing image...
                      </Typography>
                    </Stack>
                  ) : compressionResult ? (
                    <Stack spacing={2}>
                      {/* Before/After Comparison */}
                      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                        <Box flex={1}>
                          <Typography variant="caption" color="text.secondary">Original</Typography>
                          <Box sx={{ mt: 1, borderRadius: 2, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                            <img src={sourceImage || ''} alt="Original" style={{ width: '100%', maxHeight: 250, objectFit: 'contain' }} />
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {compressionResult.original_size_kb.toFixed(1)} KB
                          </Typography>
                        </Box>
                        <Box flex={1}>
                          <Typography variant="caption" color="text.secondary">Compressed</Typography>
                          <Box sx={{ mt: 1, borderRadius: 2, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                            <img src={compressionResult.image_base64} alt="Compressed" style={{ width: '100%', maxHeight: 250, objectFit: 'contain' }} />
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {compressionResult.compressed_size_kb.toFixed(1)} KB
                          </Typography>
                        </Box>
                      </Stack>

                      <Divider />

                      {/* Stats */}
                      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                        <StatChip label="Reduction" value={`${compressionResult.compression_ratio.toFixed(1)}%`} />
                        <StatChip label="Format" value={compressionResult.format.toUpperCase()} />
                        <StatChip label="Dimensions" value={`${compressionResult.width}×${compressionResult.height}`} />
                        <StatChip label="Quality" value={`${compressionResult.quality_used}%`} />
                        <StatChip label="Metadata" value={compressionResult.metadata_stripped ? 'Stripped' : 'Kept'} />
                      </Stack>
                    </Stack>
                  ) : (
                    <Stack alignItems="center" justifyContent="center" py={6}>
                      <Typography variant="body1" color="text.secondary">
                        Upload an image and configure settings to see compression results.
                      </Typography>
                    </Stack>
                  )}
                </CardContent>
              </Card>
            </Stack>
          </Grid>
        </Grid>
      </MotionPaper>
    </ImageStudioLayout>
  );
};

const StatChip: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <Box
    sx={{
      borderRadius: 2,
      background: 'rgba(255,255,255,0.08)',
      px: 2,
      py: 1,
      minWidth: 100,
    }}
  >
    <Typography variant="caption" color="text.secondary">
      {label}
    </Typography>
    <Typography variant="body2" fontWeight={600}>
      {value}
    </Typography>
  </Box>
);
