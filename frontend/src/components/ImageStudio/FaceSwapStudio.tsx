import React, { useEffect, useMemo, useState } from 'react';
import {
  Grid,
  Paper,
  Stack,
  Typography,
  Alert,
  Divider,
} from '@mui/material';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { motion, type Variants, type Easing } from 'framer-motion';
import {
  useImageStudio,
  FaceSwapRequestPayload,
} from '../../hooks/useImageStudio';
import { FaceSwapImageUploader } from './FaceSwapImageUploader';
import { FaceSwapResultViewer } from './FaceSwapResultViewer';
import { ImageStudioLayout } from './ImageStudioLayout';
import { OperationButton } from '../shared/OperationButton';
import { ModelSelector } from './ModelSelector';

const MotionPaper = motion.create(Paper);
const fadeEase: Easing = [0.4, 0, 0.2, 1];

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: fadeEase },
  },
};

export const FaceSwapStudio: React.FC = () => {
  const {
    loadFaceSwapModels,
    faceSwapModels,
    isLoadingFaceSwapModels,
    getFaceSwapModelRecommendation,
    faceSwapModelRecommendation,
    isLoadingFaceSwapRecommendation,
    processFaceSwap,
    isProcessingFaceSwap,
    faceSwapResult,
    faceSwapError,
    clearFaceSwapResult,
  } = useImageStudio();

  const [baseImage, setBaseImage] = useState<string | null>(null);
  const [faceImage, setFaceImage] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | undefined>(undefined);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    loadFaceSwapModels();
  }, [loadFaceSwapModels]);

  // Auto-detect model when images change
  useEffect(() => {
    if (baseImage && faceImage && !selectedModel) {
      // Get image dimensions
      const baseImg = new Image();
      const faceImg = new Image();
      
      baseImg.onload = () => {
        faceImg.onload = async () => {
          const recommendation = await getFaceSwapModelRecommendation(
            { width: baseImg.width, height: baseImg.height },
            { width: faceImg.width, height: faceImg.height },
            undefined,
            { prioritize_cost: true }
          );
          // Auto-select recommended model if available
          if (recommendation?.recommended_model) {
            setSelectedModel(recommendation.recommended_model);
          }
        };
        faceImg.src = faceImage;
      };
      baseImg.src = baseImage;
    }
  }, [baseImage, faceImage, selectedModel, getFaceSwapModelRecommendation]);

  const canSubmit = useMemo(() => {
    return !!(baseImage && faceImage);
  }, [baseImage, faceImage]);

  const buildPayload = (): FaceSwapRequestPayload | null => {
    if (!baseImage) {
      setLocalError('Please upload a base image.');
      return null;
    }
    if (!faceImage) {
      setLocalError('Please upload a face image.');
      return null;
    }

    const payload: FaceSwapRequestPayload = {
      base_image_base64: baseImage,
      face_image_base64: faceImage,
      model: selectedModel,
    };
    return payload;
  };

  const handleSwap = async () => {
    setLocalError(null);
    try {
      const payload = buildPayload();
      if (!payload) return;
      await processFaceSwap(payload);
    } catch {
      // errors handled in hook
    }
  };

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
            Face Swap Studio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered face swapping with multiple models. Swap faces in photos with realistic, high-quality results.
          </Typography>
        </Stack>

        {(localError || faceSwapError) && (
          <Alert
            severity="error"
            sx={{ mb: 3 }}
            onClose={() => {
              setLocalError(null);
            }}
          >
            {localError || faceSwapError}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={5}>
            <Stack spacing={3}>
              <FaceSwapImageUploader
                baseImage={baseImage}
                faceImage={faceImage}
                onBaseImageChange={(img) => {
                  setBaseImage(img);
                  setLocalError(null);
                  clearFaceSwapResult();
                }}
                onFaceImageChange={(img) => {
                  setFaceImage(img);
                  setLocalError(null);
                  clearFaceSwapResult();
                }}
              />
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

              {/* Model Selection */}
              {faceSwapModels.length > 0 && (
                <Stack spacing={1.5}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <SwapHorizIcon sx={{ color: '#a78bfa' }} />
                    <Typography variant="subtitle1" fontWeight={700}>
                      AI Model Selection
                    </Typography>
                  </Stack>
                  <ModelSelector
                    models={faceSwapModels}
                    selectedModel={selectedModel}
                    recommendedModel={faceSwapModelRecommendation?.recommended_model}
                    recommendationReason={faceSwapModelRecommendation?.reason}
                    onModelSelect={(modelId) => {
                      setSelectedModel(modelId);
                      setLocalError(null);
                    }}
                    loading={isLoadingFaceSwapModels || isLoadingFaceSwapRecommendation}
                  />
                </Stack>
              )}
            </Stack>
          </Grid>

          <Grid item xs={12} md={7}>
            <Stack spacing={3}>
              <OperationButton
                operation={{
                  provider: 'wavespeed',
                  operation_type: 'face-swap',
                  actual_provider_name: 'wavespeed',
                }}
                label="Swap Face"
                startIcon={<SwapHorizIcon />}
                onClick={handleSwap}
                disabled={!canSubmit}
                loading={isProcessingFaceSwap}
                checkOnMount
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

              <FaceSwapResultViewer
                baseImage={baseImage}
                faceImage={faceImage}
                result={faceSwapResult}
                isProcessing={isProcessingFaceSwap}
                onReset={() => {
                  clearFaceSwapResult();
                  setBaseImage(null);
                  setFaceImage(null);
                  setSelectedModel(undefined);
                }}
              />
            </Stack>
          </Grid>
        </Grid>
      </MotionPaper>
    </ImageStudioLayout>
  );
};
