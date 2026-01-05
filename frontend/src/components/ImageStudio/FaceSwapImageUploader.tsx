import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  IconButton,
  Tooltip,
} from '@mui/material';
import UploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/DeleteOutline';
import FaceIcon from '@mui/icons-material/Face';
import ImageIcon from '@mui/icons-material/Image';
import { alpha } from '@mui/material/styles';

interface FaceSwapImageUploaderProps {
  baseImage?: string | null;
  faceImage?: string | null;
  onBaseImageChange: (value: string | null) => void;
  onFaceImageChange: (value: string | null) => void;
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
  helper: string;
  icon: React.ReactNode;
  value?: string | null;
  onChange: (value: string | null) => void;
}> = ({ label, helper, icon, value, onChange }) => {
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
            <Stack direction="row" spacing={1} alignItems="center">
              {icon}
              <Box>
                <Typography variant="subtitle2" fontWeight={700}>
                  {label}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {helper}
                </Typography>
              </Box>
            </Stack>
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
                style={{ width: '100%', display: 'block', objectFit: 'cover', maxHeight: 300 }}
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

export const FaceSwapImageUploader: React.FC<FaceSwapImageUploaderProps> = ({
  baseImage,
  faceImage,
  onBaseImageChange,
  onFaceImageChange,
}) => {
  return (
    <Stack spacing={2.5}>
      <UploadSlot
        label="Base Image"
        helper="Required. The image where the face will be swapped."
        icon={<ImageIcon sx={{ color: '#667eea' }} />}
        value={baseImage}
        onChange={onBaseImageChange}
      />

      <UploadSlot
        label="Face Image"
        helper="Required. The face to swap into the base image."
        icon={<FaceIcon sx={{ color: '#a78bfa' }} />}
        value={faceImage}
        onChange={onFaceImageChange}
      />
    </Stack>
  );
};
