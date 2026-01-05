/**
 * ExpandableDetails Component
 * 
 * Collapsible section showing secondary questions, focus areas, and research angles.
 */

import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Collapse,
} from '@mui/material';
import { AnalyzeIntentResponse } from '../../../types/intent.types';

interface ExpandableDetailsProps {
  intentAnalysis: AnalyzeIntentResponse;
  expanded: boolean;
}

export const ExpandableDetails: React.FC<ExpandableDetailsProps> = ({
  intentAnalysis,
  expanded,
}) => {
  const intent = intentAnalysis.intent;

  return (
    <Collapse in={expanded}>
      <Box sx={{ pt: 2, borderTop: '1px solid #e5e7eb', mt: 2 }}>
        {/* Secondary Questions */}
        {intent.secondary_questions.length > 0 && (
          <Box mb={2}>
            <Typography variant="caption" color="#666" fontWeight={600} gutterBottom display="block">
              Also answering:
            </Typography>
            {intent.secondary_questions.slice(0, 3).map((q, idx) => (
              <Typography key={idx} variant="body2" color="#333" sx={{ ml: 1, mb: 0.5 }}>
                • {q}
              </Typography>
            ))}
          </Box>
        )}

        {/* Focus Areas */}
        {intent.focus_areas.length > 0 && (
          <Box mb={2}>
            <Typography variant="caption" color="#666" fontWeight={600} gutterBottom display="block">
              Focus areas:
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={0.5}>
              {intent.focus_areas.map((area, idx) => (
                <Chip
                  key={idx}
                  label={area}
                  size="small"
                  sx={{
                    backgroundColor: '#f3f4f6',
                    border: '1px solid #d1d5db',
                    color: '#374151',
                  }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Research Angles */}
        {intentAnalysis.suggested_angles?.length > 0 && (
          <Box mb={2}>
            <Typography variant="caption" color="#666" fontWeight={600} gutterBottom display="block">
              Research angles:
            </Typography>
            {intentAnalysis.suggested_angles.slice(0, 3).map((angle, idx) => (
              <Typography key={idx} variant="body2" color="#333" sx={{ ml: 1, mb: 0.5 }}>
                • {angle}
              </Typography>
            ))}
          </Box>
        )}
      </Box>
    </Collapse>
  );
};
