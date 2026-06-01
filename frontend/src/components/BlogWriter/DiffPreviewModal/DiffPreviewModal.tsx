import React from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Typography, Box, Chip, IconButton, Divider
} from '@mui/material';
import { Close as CloseIcon, Check as CheckIcon } from '@mui/icons-material';
import type { DiffPreviewData, DiffSegment } from '../../../utils/getSectionDiffs';

interface DiffPreviewModalProps {
  isOpen: boolean;
  diffData: DiffPreviewData | null;
  onAccept: () => void;
  onReject: () => void;
  loading?: boolean;
}

function renderDiffSegments(segments: DiffSegment[]): React.ReactNode {
  return segments.map((seg, i) => {
    if (seg.added) {
      return (
        <Box
          component="span"
          key={i}
          sx={{
            bgcolor: '#dcfce7',
            color: '#166534',
            px: 0.5,
            borderRadius: '3px',
            fontWeight: 600,
          }}
        >
          {seg.value}
        </Box>
      );
    }
    if (seg.removed) {
      return (
        <Box
          component="span"
          key={i}
          sx={{
            bgcolor: '#fee2e2',
            color: '#991b1b',
            px: 0.5,
            borderRadius: '3px',
            textDecoration: 'line-through',
            textDecorationColor: '#dc2626',
          }}
        >
          {seg.value}
        </Box>
      );
    }
    return <span key={i}>{seg.value}</span>;
  });
}

export const DiffPreviewModal: React.FC<DiffPreviewModalProps> = ({
  isOpen,
  diffData,
  onAccept,
  onReject,
  loading = false,
}) => {
  if (!diffData) return null;

  const hasAnyChange = diffData.introductionChanged || diffData.sectionDiffs.some(s => s.changed);

  return (
    <Dialog open={isOpen} maxWidth="lg" fullWidth fullScreen>
      <Box
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 10,
          bgcolor: 'white',
          borderBottom: '2px solid #e2e8f0',
        }}
      >
        <DialogTitle sx={{ pb: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, flexGrow: 1 }}>
            SEO Recommendations — Review Changes
          </Typography>
          <IconButton onClick={onReject} size="small"><CloseIcon /></IconButton>
        </DialogTitle>
        <Box sx={{ px: 3, pb: 1.5, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            icon={<CheckIcon />}
            label={`${diffData.sectionDiffs.filter(s => s.changed).length} section(s) changed`}
            color="warning"
            size="small"
            variant="outlined"
          />
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', ml: 'auto' }}>
            <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center', fontSize: '0.75rem', color: '#166534' }}>
              <Box sx={{ width: 14, height: 14, bgcolor: '#dcfce7', border: '1px solid #86efac', borderRadius: '2px' }} />
              <span>Added</span>
            </Box>
            <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center', fontSize: '0.75rem', color: '#991b1b' }}>
              <Box sx={{ width: 14, height: 14, bgcolor: '#fee2e2', border: '1px solid #fca5a5', borderRadius: '2px' }} />
              <span>Removed</span>
            </Box>
          </Box>
        </Box>
      </Box>

      <DialogContent sx={{ py: 3, bgcolor: '#f8fafc' }}>
        {!hasAnyChange && (
          <Typography sx={{ textAlign: 'center', py: 4, color: '#64748b' }}>
            No changes detected between original and recommended content.
          </Typography>
        )}

        {diffData.introductionChanged && (
          <Box sx={{ mb: 4 }}>
            <Typography sx={{ fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#475569', mb: 1 }}>
              Introduction
            </Typography>
            <Box sx={{ bgcolor: 'white', border: '1px solid #e2e8f0', borderRadius: 2, p: 2.5, fontFamily: 'Georgia, serif', fontSize: '1rem', lineHeight: 1.8, color: '#1e293b' }}>
              {renderDiffSegments(diffData.introductionDiff!)}
            </Box>
          </Box>
        )}

        {diffData.sectionDiffs.map((section, idx) => {
          if (!section.changed) return null;
          return (
            <Box key={section.heading || idx} sx={{ mb: 3 }}>
              <Typography sx={{ fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#475569', mb: 0.5 }}>
                {section.heading}
              </Typography>
              <Box sx={{ bgcolor: 'white', border: '1px solid #e2e8f0', borderRadius: 2, p: 2.5, fontFamily: 'Georgia, serif', fontSize: '1rem', lineHeight: 1.8, color: '#1e293b' }}>
                {renderDiffSegments(section.segments)}
              </Box>
            </Box>
          );
        })}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e2e8f0', bgcolor: 'white' }}>
        <Button
          onClick={onReject}
          disabled={loading}
          variant="outlined"
          color="error"
          sx={{ textTransform: 'none', fontWeight: 600 }}
        >
          Reject Changes
        </Button>
        <Button
          onClick={onAccept}
          disabled={loading}
          variant="contained"
          color="primary"
          sx={{ textTransform: 'none', fontWeight: 600 }}
        >
          Accept Changes
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DiffPreviewModal;
