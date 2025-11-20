import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import BoltIcon from '@mui/icons-material/Bolt';
import { alpha } from '@mui/material/styles';
import { EditOperationMeta } from '../../hooks/useImageStudio';

interface EditOperationsToolbarProps {
  operations: Record<string, EditOperationMeta>;
  selectedOperation: string;
  onSelect: (key: string) => void;
  loading?: boolean;
}

export const EditOperationsToolbar: React.FC<EditOperationsToolbarProps> = ({
  operations,
  selectedOperation,
  onSelect,
  loading,
}) => {
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 160,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  const entries = Object.entries(operations);

  return (
    <Grid container spacing={2}>
      {entries.map(([key, meta]) => {
        const isSelected = selectedOperation === key;
        return (
          <Grid item xs={12} md={6} key={key}>
            <Card
              onClick={() => onSelect(key)}
              sx={{
                cursor: 'pointer',
                borderRadius: 3,
                borderWidth: 2,
                borderStyle: 'solid',
                borderColor: isSelected ? alpha('#667eea', 0.8) : 'transparent',
                background: isSelected
                  ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2))'
                  : 'rgba(255,255,255,0.08)',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: alpha('#667eea', 0.6),
                },
              }}
            >
              <CardContent>
                <Stack spacing={1.2}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle1" fontWeight={700}>
                      {meta.label}
                    </Typography>
                    <Chip
                      size="small"
                      icon={<AutoAwesomeIcon sx={{ fontSize: 16 }} />}
                      label={meta.provider}
                      sx={{
                        textTransform: 'capitalize',
                        background: alpha('#1f2937', 0.6),
                        color: '#fff',
                      }}
                    />
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {meta.description}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    {meta.async && (
                      <Chip
                        size="small"
                        icon={<BoltIcon sx={{ fontSize: 16 }} />}
                        label="Async"
                        sx={{
                          background: alpha('#f59e0b', 0.15),
                          color: '#f59e0b',
                          fontWeight: 600,
                        }}
                      />
                    )}
                    {meta.fields?.mask && (
                      <Chip
                        size="small"
                        label="Mask"
                        sx={{
                          background: alpha('#10b981', 0.15),
                          color: '#10b981',
                          fontWeight: 600,
                        }}
                      />
                    )}
                    {meta.fields?.background && (
                      <Chip
                        size="small"
                        label="Background"
                        sx={{
                          background: alpha('#6366f1', 0.2),
                          color: '#6366f1',
                          fontWeight: 600,
                        }}
                      />
                    )}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );
};


