import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  IconButton,
  Tooltip,
  Dialog,
  DialogContent,
} from '@mui/material';
import UploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/DeleteOutline';
import BrushIcon from '@mui/icons-material/Brush';
import { alpha } from '@mui/material/styles';
import { ImageMaskEditor } from './ImageMaskEditor';

interface EditImageUploaderProps {
  baseImage?: string | null;
  maskImage?: string | null;
  backgroundImage?: string | null;
  lightingImage?: string | null;
  requiresMask?: boolean;
  requiresBackground?: boolean;
  requiresLighting?: boolean;
  onBaseImageChange: (value: string | null) => void;
  onMaskImageChange: (value: string | null) => void;
  onBackgroundImageChange: (value: string | null) => void;
  onLightingImageChange: (value: string | null) => void;
  onOpenMaskEditor?: () => void;
}

const readFileAsDataURL = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

const UploadSlot: React.FC<{
  label: string;
  helper?: string;
  value?: string | null;
  onChange: (value: string | null) => void;
}> = ({ label, helper, value, onChange }) => {
  const handleFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const dataUrl = await readFileAsDataURL(file);
    onChange(dataUrl);
  };

  return (
    <Card
      variant="outlined"
      sx={{
        borderRadius: 3,
        borderStyle: value ? 'solid' : 'dashed',
        borderColor: value ? alpha('#667eea', 0.4) : alpha('#cbd5f5', 0.8),
        background: value ? alpha('#667eea', 0.08) : alpha('#667eea', 0.02),
        position: 'relative',
      }}
    >
      <CardContent>
        <Stack spacing={1.5}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography variant="subtitle2" fontWeight={700}>
                {label}
              </Typography>
              {helper && (
                <Typography variant="caption" color="text.secondary">
                  {helper}
                </Typography>
              )}
            </Box>
            {value && (
              <Tooltip title="Remove image">
                <IconButton size="small" onClick={() => onChange(null)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Stack>
          {value ? (
            <Box
              sx={{
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid rgba(255,255,255,0.2)',
              }}
            >
              <img
                src={value}
                alt={`${label} preview`}
                style={{ width: '100%', display: 'block', objectFit: 'cover' }}
              />
            </Box>
          ) : (
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadIcon />}
              sx={{
                borderRadius: 2,
                borderStyle: 'dashed',
                py: 2,
                color: '#667eea',
                borderColor: alpha('#667eea', 0.6),
              }}
            >
              Upload Image
              <input hidden type="file" accept="image/*" onChange={handleFile} />
            </Button>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
};

export const EditImageUploader: React.FC<EditImageUploaderProps> = ({
  baseImage,
  maskImage,
  backgroundImage,
  lightingImage,
  requiresMask,
  requiresBackground,
  requiresLighting,
  onBaseImageChange,
  onMaskImageChange,
  onBackgroundImageChange,
  onLightingImageChange,
  onOpenMaskEditor,
}) => {
  return (
    <Stack spacing={2.5}>
      <UploadSlot
        label="Primary Image"
        helper="Required. Upload the image you want to edit."
        value={baseImage}
        onChange={onBaseImageChange}
      />

      {requiresMask && (
        <>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              borderStyle: maskImage ? 'solid' : 'dashed',
              borderColor: maskImage ? alpha('#667eea', 0.4) : alpha('#cbd5f5', 0.8),
              background: maskImage ? alpha('#667eea', 0.08) : alpha('#667eea', 0.02),
              position: 'relative',
            }}
          >
            <CardContent>
              <Stack spacing={1.5}>
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="subtitle2" fontWeight={700}>
                      Mask (Optional)
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      White reveals areas to edit, black preserves original pixels.
                    </Typography>
                  </Box>
                  {maskImage && (
                    <Tooltip title="Remove mask">
                      <IconButton size="small" onClick={() => onMaskImageChange(null)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Stack>
                {maskImage ? (
                  <Box
                    sx={{
                      borderRadius: 2,
                      overflow: 'hidden',
                      border: '1px solid rgba(255,255,255,0.2)',
                    }}
                  >
                    <img
                      src={maskImage}
                      alt="Mask preview"
                      style={{ width: '100%', display: 'block', objectFit: 'cover' }}
                    />
                  </Box>
                ) : (
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<UploadIcon />}
                      sx={{
                        flex: 1,
                        borderRadius: 2,
                        borderStyle: 'dashed',
                        py: 2,
                        color: '#667eea',
                        borderColor: alpha('#667eea', 0.6),
                      }}
                    >
                      Upload Mask
                      <input hidden type="file" accept="image/*" onChange={async (e) => {
                        const file = e.target.files?.[0];
                        if (!file) return;
                        const dataUrl = await readFileAsDataURL(file);
                        onMaskImageChange(dataUrl);
                      }} />
                    </Button>
                    {baseImage && onOpenMaskEditor && (
                      <Button
                        variant="contained"
                        startIcon={<BrushIcon />}
                        onClick={onOpenMaskEditor}
                        sx={{
                          borderRadius: 2,
                          py: 2,
                          background: 'linear-gradient(90deg, #667eea, #764ba2)',
                          '&:hover': {
                            background: 'linear-gradient(90deg, #5568d3, #65408b)',
                          },
                        }}
                      >
                        Create Mask
                      </Button>
                    )}
                  </Stack>
                )}
              </Stack>
            </CardContent>
          </Card>
        </>
      )}

      {requiresBackground && (
        <UploadSlot
          label="Background Reference"
          helper="Provide a new background reference image."
          value={backgroundImage}
          onChange={onBackgroundImageChange}
        />
      )}

      {requiresLighting && (
        <UploadSlot
          label="Lighting Reference"
          helper="Optional. Match subject lighting to this reference."
          value={lightingImage}
          onChange={onLightingImageChange}
        />
      )}
    </Stack>
  );
};


