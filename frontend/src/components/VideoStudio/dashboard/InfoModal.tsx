import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  Stack,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';
import { alpha } from '@mui/material/styles';

export interface AIModel {
  name: string;
  provider: string;
  capabilities: string[];
  pricing: {
    model: 'per_second' | 'per_video' | 'flat_rate' | 'free';
    rate?: number;
    min?: number;
    max?: number;
    unit?: string;
    description: string;
  };
  features: string[];
}

export interface PerfectForUseCase {
  title: string;
  description: string;
  examples: string[];
}

export interface CostDetail {
  factors: string[];
  typicalRange?: string;
  examples: Array<{
    scenario: string;
    cost: string;
  }>;
}

interface InfoModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  type: 'perfect-for' | 'cost' | 'ai-models';
  perfectFor?: PerfectForUseCase[];
  costDetails?: CostDetail;
  aiModels?: AIModel[];
}

export const InfoModal: React.FC<InfoModalProps> = ({
  open,
  onClose,
  title,
  type,
  perfectFor,
  costDetails,
  aiModels,
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: '#ffffff',
          border: '2px solid rgba(139,92,246,0.3)',
          borderRadius: 4,
          boxShadow: '0 24px 48px rgba(0,0,0,0.3), 0 0 0 1px rgba(0,0,0,0.05)',
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '2px solid rgba(139,92,246,0.2)',
          pb: 2.5,
          background: 'linear-gradient(135deg, rgba(139,92,246,0.1), rgba(99,102,241,0.08))',
        }}
      >
        <Typography variant="h6" fontWeight={800} sx={{ color: '#1e293b', fontSize: '1.25rem' }}>
          {title}
        </Typography>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{
            color: '#64748b',
            '&:hover': {
              background: 'rgba(239,68,68,0.1)',
              color: '#ef4444',
            },
          }}
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ pt: 3, backgroundColor: '#ffffff' }}>
        {type === 'perfect-for' && perfectFor && (
          <Stack spacing={3}>
            {perfectFor.map((useCase, index) => (
              <Box key={index}>
                <Typography
                  variant="subtitle1"
                  fontWeight={800}
                  sx={{ color: '#6366f1', mb: 1.5, fontSize: '1.1rem' }}
                >
                  {useCase.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ color: '#334155', mb: 1.5, lineHeight: 1.8, fontSize: '0.95rem' }}
                >
                  {useCase.description}
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {useCase.examples.map((example, idx) => (
                    <Chip
                      key={idx}
                      label={example}
                      size="small"
                    sx={{
                      background: 'rgba(139,92,246,0.1)',
                      color: '#6366f1',
                      border: '1px solid rgba(139,92,246,0.3)',
                      fontWeight: 600,
                    }}
                    />
                  ))}
                </Stack>
                {index < perfectFor.length - 1 && (
                  <Divider sx={{ mt: 2, borderColor: 'rgba(255,255,255,0.1)' }} />
                )}
              </Box>
            ))}
          </Stack>
        )}

        {type === 'cost' && costDetails && (
          <Stack spacing={3}>
            <Box>
              <Typography
                variant="subtitle1"
                fontWeight={800}
                sx={{ color: '#0ea5e9', mb: 1.5, fontSize: '1.1rem' }}
              >
                Cost Factors
              </Typography>
              <Stack spacing={1.5}>
                {costDetails.factors.map((factor, idx) => (
                  <Box
                    key={idx}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: 'rgba(14,165,233,0.08)',
                      border: '1px solid rgba(56,189,248,0.2)',
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{ color: '#334155', fontWeight: 600, lineHeight: 1.7 }}
                    >
                      • {factor}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Box>

            {costDetails.typicalRange && (
              <Box>
                <Typography
                  variant="subtitle1"
                  fontWeight={700}
                  sx={{ color: '#c7d2fe', mb: 1.5 }}
                >
                  Typical Cost Range
                </Typography>
                <Chip
                  label={costDetails.typicalRange}
                  sx={{
                    background: 'linear-gradient(120deg, rgba(16,185,129,0.15), rgba(34,197,94,0.1))',
                    color: '#059669',
                    border: '1px solid rgba(34,197,94,0.3)',
                    fontWeight: 700,
                    fontSize: '0.9rem',
                    p: 1,
                  }}
                />
              </Box>
            )}

            {costDetails.examples && costDetails.examples.length > 0 && (
              <Box>
                <Typography
                  variant="subtitle1"
                  fontWeight={700}
                  sx={{ color: '#c7d2fe', mb: 1.5 }}
                >
                  Cost Examples
                </Typography>
                <TableContainer
                  component={Paper}
                  sx={{
                    background: '#f8fafc',
                    border: '1px solid rgba(0,0,0,0.1)',
                  }}
                >
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ background: 'rgba(139,92,246,0.05)' }}>
                        <TableCell sx={{ color: '#1e293b', fontWeight: 700 }}>Scenario</TableCell>
                        <TableCell align="right" sx={{ color: '#1e293b', fontWeight: 700 }}>
                          Estimated Cost
                        </TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {costDetails.examples.map((example, idx) => (
                        <TableRow key={idx}>
                          <TableCell sx={{ color: '#334155' }}>
                            {example.scenario}
                          </TableCell>
                          <TableCell align="right" sx={{ color: '#059669', fontWeight: 700 }}>
                            {example.cost}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Stack>
        )}

        {type === 'ai-models' && aiModels && (
          <Stack spacing={3}>
            {aiModels.map((model, index) => (
              <Box
                key={index}
                sx={{
                  p: 2.5,
                  borderRadius: 2,
                  background: 'rgba(99,102,241,0.05)',
                  border: '1px solid rgba(139,92,246,0.2)',
                }}
              >
                <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="h6" fontWeight={800} sx={{ color: '#6366f1' }}>
                    {model.name}
                  </Typography>
                  <Chip
                    label={model.provider}
                    size="small"
                    sx={{
                      background: 'rgba(139,92,246,0.1)',
                      color: '#6366f1',
                      fontWeight: 600,
                    }}
                  />
                </Stack>

                <Box sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    fontWeight={800}
                    sx={{ color: '#6366f1', mb: 1.5, fontSize: '0.95rem' }}
                  >
                    Capabilities
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {model.capabilities.map((capability, idx) => (
                      <Chip
                        key={idx}
                        label={capability}
                        size="small"
                        sx={{
                          background: 'rgba(14,165,233,0.1)',
                          color: '#0ea5e9',
                          border: '1px solid rgba(56,189,248,0.2)',
                          fontWeight: 600,
                        }}
                      />
                    ))}
                  </Stack>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    fontWeight={800}
                    sx={{ color: '#99f6e4', mb: 1.5, fontSize: '0.95rem' }}
                  >
                    Pricing
                  </Typography>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: 'rgba(16,185,129,0.08)',
                      border: '2px solid rgba(34,197,94,0.2)',
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{ color: '#059669', fontWeight: 700, mb: 1, fontSize: '1rem' }}
                    >
                      {model.pricing.description}
                    </Typography>
                    {model.pricing.rate && (
                      <Typography variant="body2" sx={{ color: '#334155', fontWeight: 600 }}>
                        Rate: <span style={{ color: '#059669' }}>${model.pricing.rate}</span>
                        {model.pricing.unit || '/second'}
                        {model.pricing.min && ` (min: $${model.pricing.min})`}
                        {model.pricing.max && ` (max: $${model.pricing.max})`}
                      </Typography>
                    )}
                  </Box>
                </Box>

                <Box>
                  <Typography
                    variant="subtitle2"
                    fontWeight={800}
                    sx={{ color: '#6366f1', mb: 1.5, fontSize: '0.95rem' }}
                  >
                    Key Features
                  </Typography>
                  <Stack spacing={1}>
                    {model.features.map((feature, idx) => (
                      <Typography
                        key={idx}
                        variant="body2"
                        sx={{ color: '#334155', pl: 1.5, lineHeight: 1.7 }}
                      >
                        • {feature}
                      </Typography>
                    ))}
                  </Stack>
                </Box>

                {index < aiModels.length - 1 && (
                  <Divider sx={{ mt: 2, borderColor: 'rgba(255,255,255,0.1)' }} />
                )}
              </Box>
            ))}
          </Stack>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2, borderTop: '1px solid rgba(0,0,0,0.1)', backgroundColor: '#f8fafc' }}>
        <Box sx={{ flex: 1 }} />
        <IconButton
          onClick={onClose}
          sx={{
            background: 'rgba(139,92,246,0.1)',
            color: '#6366f1',
            '&:hover': {
              background: 'rgba(139,92,246,0.2)',
            },
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogActions>
    </Dialog>
  );
};
