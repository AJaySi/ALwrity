import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Stack,
  Typography,
  TextField,
  Alert,
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
  Chip,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import TransformIcon from '@mui/icons-material/Transform';
import UploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import InfoIcon from '@mui/icons-material/Info';
import {
  useImageStudio,
  FormatConversionRequest,
} from '../../../hooks/useImageStudio';
import { OperationButton } from '../../shared/OperationButton';

const readFileAsDataURL = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

export const FormatConverterTab: React.FC = () => {
  const {
    supportedFormats,
    loadSupportedFormats,
    getFormatRecommendations,
    processFormatConversion,
    isConvertingFormat,
    formatConversionResult,
    formatConversionError,
    formatRecommendations,
    clearFormatConversionResult,
  } = useImageStudio();

  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [originalFormat, setOriginalFormat] = useState<string>('');
  const [originalSize, setOriginalSize] = useState<number>(0);
  const [targetFormat, setTargetFormat] = useState<string>('webp');
  const [preserveTransparency, setPreserveTransparency] = useState(true);
  const [quality, setQuality] = useState<number | undefined>(85);
  const [stripMetadata, setStripMetadata] = useState(false);
  const [optimize, setOptimize] = useState(true);
  const [progressive, setProgressive] = useState(true);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    loadSupportedFormats();
  }, [loadSupportedFormats]);

  useEffect(() => {
    if (sourceImage && originalFormat) {
      getFormatRecommendations(originalFormat);
    }
  }, [sourceImage, originalFormat, getFormatRecommendations]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setOriginalSize(file.size / 1024); // KB
    const dataUrl = await readFileAsDataURL(file);
    setSourceImage(dataUrl);
    
    // Detect format from file
    const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
    setOriginalFormat(fileExtension);
    
    clearFormatConversionResult();
    setLocalError(null);
  };

  const handleConvert = async () => {
    if (!sourceImage) {
      setLocalError('Please upload an image first.');
      return;
    }

    setLocalError(null);
    try {
      const request: FormatConversionRequest = {
        image_base64: sourceImage,
        target_format: targetFormat,
        preserve_transparency: preserveTransparency,
        quality: quality,
        color_space: undefined,
        strip_metadata: stripMetadata,
        optimize,
        progressive,
      };
      await processFormatConversion(request);
    } catch {
      // Error handled in hook
    }
  };

  const handleDownload = () => {
    if (!formatConversionResult?.image_base64) return;
    const link = document.createElement('a');
    link.href = formatConversionResult.image_base64;
    link.download = `converted-image.${formatConversionResult.target_format}`;
    link.click();
  };

  const handleReset = () => {
    setSourceImage(null);
    setOriginalFormat('');
    setOriginalSize(0);
    clearFormatConversionResult();
    setLocalError(null);
  };

  const currentFormat = supportedFormats.find(f => f.id === targetFormat);
  const supportsQuality = currentFormat?.supports_lossy;

  return (
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
                        setOriginalFormat('');
                        setOriginalSize(0);
                        clearFormatConversionResult();
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
                      {originalFormat.toUpperCase()} • {originalSize.toFixed(2)} KB
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

          {/* Recommendations */}
          {formatRecommendations.length > 0 && (
            <Card sx={{ borderRadius: 3, background: 'rgba(255,255,255,0.05)' }}>
              <CardContent>
                <Stack spacing={1}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <InfoIcon sx={{ color: '#667eea', fontSize: 18 }} />
                    <Typography variant="subtitle2">Recommended Formats</Typography>
                  </Stack>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {formatRecommendations.map((rec, idx) => (
                      <Chip
                        key={idx}
                        label={`${rec.format.toUpperCase()}: ${rec.reason}`}
                        size="small"
                        onClick={() => setTargetFormat(rec.format)}
                        sx={{
                          borderColor: targetFormat === rec.format ? '#667eea' : 'rgba(255,255,255,0.2)',
                          bgcolor: targetFormat === rec.format ? alpha('#667eea', 0.2) : 'transparent',
                          color: targetFormat === rec.format ? '#667eea' : 'inherit',
                        }}
                      />
                    ))}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          )}

          {/* Format Selection */}
          <FormControl fullWidth>
            <InputLabel>Target Format</InputLabel>
            <Select
              value={targetFormat}
              label="Target Format"
              onChange={(e) => setTargetFormat(e.target.value)}
            >
              {supportedFormats.map((fmt) => (
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

          {/* Quality (for lossy formats) */}
          {supportsQuality && (
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="subtitle2" fontWeight={600}>
                  Quality
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {quality || 85}%
                </Typography>
              </Stack>
              <TextField
                type="number"
                value={quality || ''}
                onChange={(e) => setQuality(parseInt(e.target.value) || undefined)}
                inputProps={{ min: 1, max: 100 }}
                size="small"
                helperText="Higher quality = larger file size"
              />
            </Stack>
          )}

          {/* Advanced Options */}
          <Stack spacing={1}>
            <Typography variant="subtitle2" fontWeight={600}>
              Advanced Options
            </Typography>
            {currentFormat?.supports_transparency && (
              <FormControlLabel
                control={
                  <Switch
                    checked={preserveTransparency}
                    onChange={(e) => setPreserveTransparency(e.target.checked)}
                    size="small"
                  />
                }
                label={<Typography variant="body2">Preserve transparency</Typography>}
              />
            )}
            <FormControlLabel
              control={
                <Switch
                  checked={stripMetadata}
                  onChange={(e) => setStripMetadata(e.target.checked)}
                  size="small"
                />
              }
              label={<Typography variant="body2">Strip metadata (EXIF)</Typography>}
            />
            {targetFormat === 'jpeg' && (
              <FormControlLabel
                control={
                  <Switch
                    checked={progressive}
                    onChange={(e) => setProgressive(e.target.checked)}
                    size="small"
                  />
                }
                label={<Typography variant="body2">Progressive JPEG</Typography>}
              />
            )}
            <FormControlLabel
              control={
                <Switch
                  checked={optimize}
                  onChange={(e) => setOptimize(e.target.checked)}
                  size="small"
                />
              }
              label={<Typography variant="body2">Optimize encoding</Typography>}
            />
          </Stack>
        </Stack>
      </Grid>

      {/* Right Panel - Results */}
      <Grid item xs={12} md={7}>
        <Stack spacing={3}>
          {(localError || formatConversionError) && (
            <Alert
              severity="error"
              onClose={() => setLocalError(null)}
            >
              {localError || formatConversionError}
            </Alert>
          )}

          <OperationButton
            operation={{
              provider: 'local',
              operation_type: 'convert_format',
              actual_provider_name: 'pillow',
            }}
            label="Convert Format"
            startIcon={<TransformIcon />}
            onClick={handleConvert}
            disabled={!sourceImage}
            loading={isConvertingFormat}
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
                      <IconButton disabled={!formatConversionResult && !sourceImage} onClick={handleReset}>
                        <RestartAltIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                  <Tooltip title="Download">
                    <span>
                      <IconButton disabled={!formatConversionResult} onClick={handleDownload}>
                        <DownloadIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                </Stack>
              </Stack>

              {isConvertingFormat ? (
                <Stack alignItems="center" spacing={2} py={6}>
                  <CircularProgress />
                  <Typography variant="body2" color="text.secondary">
                    Converting format...
                  </Typography>
                </Stack>
              ) : formatConversionResult ? (
                <Stack spacing={2}>
                  {/* Before/After Comparison */}
                  <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                    <Box flex={1}>
                      <Typography variant="caption" color="text.secondary">Original ({formatConversionResult.original_format.toUpperCase()})</Typography>
                      <Box sx={{ mt: 1, borderRadius: 2, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <img src={sourceImage || ''} alt="Original" style={{ width: '100%', maxHeight: 250, objectFit: 'contain' }} />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {formatConversionResult.original_size_kb.toFixed(1)} KB
                      </Typography>
                    </Box>
                    <Box flex={1}>
                      <Typography variant="caption" color="text.secondary">Converted ({formatConversionResult.target_format.toUpperCase()})</Typography>
                      <Box sx={{ mt: 1, borderRadius: 2, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <img src={formatConversionResult.image_base64} alt="Converted" style={{ width: '100%', maxHeight: 250, objectFit: 'contain' }} />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {formatConversionResult.converted_size_kb.toFixed(1)} KB
                      </Typography>
                    </Box>
                  </Stack>

                  {/* Stats */}
                  <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
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
                        Format
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {formatConversionResult.original_format.toUpperCase()} → {formatConversionResult.target_format.toUpperCase()}
                      </Typography>
                    </Box>
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
                        Size Change
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {formatConversionResult.converted_size_kb > formatConversionResult.original_size_kb ? '+' : ''}
                        {((formatConversionResult.converted_size_kb - formatConversionResult.original_size_kb) / formatConversionResult.original_size_kb * 100).toFixed(1)}%
                      </Typography>
                    </Box>
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
                        Dimensions
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {formatConversionResult.width}×{formatConversionResult.height}
                      </Typography>
                    </Box>
                    {formatConversionResult.transparency_preserved && (
                      <Box
                        sx={{
                          borderRadius: 2,
                          background: 'rgba(255,255,255,0.08)',
                          px: 2,
                          py: 1,
                        }}
                      >
                        <Typography variant="caption" color="text.secondary">
                          Transparency
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          Preserved
                        </Typography>
                      </Box>
                    )}
                  </Stack>
                </Stack>
              ) : (
                <Stack alignItems="center" justifyContent="center" py={6}>
                  <Typography variant="body1" color="text.secondary">
                    Upload an image and select target format to see conversion results.
                  </Typography>
                </Stack>
              )}
            </CardContent>
          </Card>
        </Stack>
      </Grid>
    </Grid>
  );
};
