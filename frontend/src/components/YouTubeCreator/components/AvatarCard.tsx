/**
 * Avatar Card Component with Enlarge Modal
 */

import React, { useState } from 'react';
import { Box, Typography, Dialog, DialogContent, IconButton, Paper, Stack } from '@mui/material';
import { Close, ZoomIn, Refresh, AutoAwesome } from '@mui/icons-material';
import { PlanDetailsCard } from './PlanDetailsCard';
import { OperationButton } from '../../shared/OperationButton';

interface AvatarCardProps {
  avatarUrl: string | null | undefined;
  avatarBlobUrl: string | null;
  avatarLoading: boolean;
  avatarReused?: boolean;
  avatarPrompt?: string;
  onImageError?: () => void;
  onRegenerate?: () => void;
  regenerating?: boolean;
}

export const AvatarCard: React.FC<AvatarCardProps> = React.memo(({
  avatarUrl,
  avatarBlobUrl,
  avatarLoading,
  avatarReused = false,
  avatarPrompt,
  onImageError,
  onRegenerate,
  regenerating = false,
}) => {
  const [modalOpen, setModalOpen] = useState(false);

  if (!avatarUrl) {
    return null;
  }

  const imageSrc = avatarBlobUrl || (avatarUrl.startsWith('data:') ? avatarUrl : undefined);
  const canDisplayImage = avatarBlobUrl || avatarUrl.startsWith('data:');

  return (
    <>
      <PlanDetailsCard title="Creator Avatar" fullHeight={false}>
        <Box
          sx={{
            position: 'relative',
            width: '100%',
            maxWidth: 200,
            aspectRatio: '1',
            borderRadius: 2,
            border: '2px solid #e5e7eb',
            overflow: 'hidden',
            bgcolor: '#f9fafb',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              borderColor: '#d1d5db',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              '& .zoom-icon': {
                opacity: 1,
              },
            },
          }}
          onClick={() => setModalOpen(true)}
        >
          {avatarLoading ? (
            <Box
              sx={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: '#f9fafb',
              }}
            >
              <Typography variant="body2" sx={{ color: '#6b7280', fontWeight: 500 }}>
                Loading...
              </Typography>
            </Box>
          ) : (
            <>
              {canDisplayImage && (
                <Box
                  component="img"
                  src={imageSrc}
                  alt="Generated creator avatar"
                  onError={onImageError}
                  sx={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    display: 'block',
                  }}
                />
              )}
              <Box
                className="zoom-icon"
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  bgcolor: 'rgba(0, 0, 0, 0.6)',
                  borderRadius: '50%',
                  p: 0.75,
                  opacity: 0,
                  transition: 'opacity 0.2s ease-in-out',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ZoomIn sx={{ color: '#ffffff', fontSize: '1.25rem' }} />
              </Box>
            </>
          )}
        </Box>

        {/* Regenerate Button and Avatar Prompt */}
        <Stack spacing={1.5} sx={{ mt: 2 }}>
          {onRegenerate && (
            <Box>
              <OperationButton
                operation={{
                  provider: 'stability',
                  model: 'default',
                  operation_type: 'image_generation',
                  tokens_requested: 0,
                  actual_provider_name: 'stability',
                }}
                label="Regenerate Avatar"
                variant="outlined"
                size="small"
                startIcon={<Refresh />}
                onClick={onRegenerate}
                disabled={regenerating}
                loading={regenerating}
                checkOnHover={true}
                checkOnMount={false}
                showCost={true}
                fullWidth
              />
            </Box>
          )}

          {/* AI Prompt Used for Avatar Generation */}
          {avatarPrompt && (
            <Box>
              <Typography
                variant="caption"
                sx={{
                  color: "#64748b",
                  fontWeight: 600,
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                  mb: 0.75,
                }}
              >
                <AutoAwesome sx={{ fontSize: 14 }} />
                AI Generation Prompt
              </Typography>
              <Paper
                sx={{
                  p: 1.5,
                  background: "#f8fafc",
                  border: "1px solid rgba(0,0,0,0.08)",
                  borderRadius: 1.5,
                  maxHeight: 150,
                  overflow: "auto",
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: "#475569",
                    fontFamily: "monospace",
                    fontSize: "0.75rem",
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    display: "block",
                  }}
                >
                  {avatarPrompt}
                </Typography>
              </Paper>
            </Box>
          )}
        </Stack>

        {avatarReused && (
          <Typography
            variant="caption"
            sx={{
              color: '#059669',
              mt: 1,
              display: 'block',
              fontWeight: 500,
              fontSize: '0.75rem',
            }}
          >
            ♻️ Reused from previous generation
          </Typography>
        )}
      </PlanDetailsCard>

      {/* Enlarge Modal */}
      <Dialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            bgcolor: '#000000',
          },
        }}
      >
        <DialogContent sx={{ p: 0, position: 'relative', bgcolor: '#000000' }}>
          <IconButton
            onClick={() => setModalOpen(false)}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              zIndex: 1,
              bgcolor: 'rgba(0, 0, 0, 0.6)',
              color: '#ffffff',
              '&:hover': {
                bgcolor: 'rgba(0, 0, 0, 0.8)',
              },
            }}
          >
            <Close />
          </IconButton>
          {canDisplayImage ? (
            <Box
              component="img"
              src={imageSrc}
              alt="Generated creator avatar (full size)"
              sx={{
                width: '100%',
                height: 'auto',
                display: 'block',
                maxHeight: '90vh',
                objectFit: 'contain',
              }}
            />
          ) : (
            <Box
              sx={{
                width: '100%',
                minHeight: 400,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
              }}
            >
              <Typography>Loading image...</Typography>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
});

AvatarCard.displayName = 'AvatarCard';

