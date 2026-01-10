/**
 * ExpandableDetails Component
 * 
 * Collapsible section showing secondary questions, focus areas, and research angles.
 * Now with editable "Also Answering" and "Focus Areas" sections.
 */

import React from 'react';
import {
  Box,
  Typography,
  Collapse,
} from '@mui/material';
import { AnalyzeIntentResponse, ResearchIntent } from '../../../types/intent.types';
import { EditableListField } from './EditableListField';

interface ExpandableDetailsProps {
  intentAnalysis: AnalyzeIntentResponse;
  expanded: boolean;
  intent: ResearchIntent;
  onUpdateField: <K extends keyof ResearchIntent>(field: K, value: ResearchIntent[K]) => void;
}

export const ExpandableDetails: React.FC<ExpandableDetailsProps> = ({
  intentAnalysis,
  expanded,
  intent,
  onUpdateField,
}) => {
  return (
    <Collapse in={expanded}>
      <Box sx={{ pt: 2, borderTop: '1px solid #e5e7eb', mt: 2 }}>
        {/* Also Answering (Secondary Questions) - Editable */}
        <EditableListField
          label="Also Answering"
          items={intent.also_answering || []}
          onUpdate={(items) => onUpdateField('also_answering', items)}
          placeholder="Add a question or topic to also answer..."
          tooltip="Additional questions or topics that should be addressed in the research results, even if not explicitly asked."
          maxItems={10}
        />

        {/* Focus Areas - Editable */}
        <EditableListField
          label="Focus Areas"
          items={intent.focus_areas || []}
          onUpdate={(items) => onUpdateField('focus_areas', items)}
          placeholder="Add a focus area..."
          tooltip="Specific aspects or areas to focus on during research (e.g., 'academic research', 'industry trends', 'company analysis')."
          maxItems={10}
        />

        {/* Secondary Questions (Read-only, for reference) */}
        {intent.secondary_questions.length > 0 && (
          <Box mb={2}>
            <Typography variant="caption" color="#666" fontWeight={600} gutterBottom display="block">
              Secondary Questions:
            </Typography>
            {intent.secondary_questions.map((q, idx) => (
              <Typography key={idx} variant="body2" color="#333" sx={{ ml: 1, mb: 0.5 }}>
                • {q}
              </Typography>
            ))}
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
