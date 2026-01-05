/**
 * IntentSummaryGrid Component
 * 
 * Quick summary grid showing Purpose, Content Type, Depth, and Queries Count.
 */

import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  ResearchIntent,
  ResearchPurpose,
  ContentOutput,
  ResearchDepthLevel,
  PURPOSE_DISPLAY,
  CONTENT_OUTPUT_DISPLAY,
  DEPTH_DISPLAY,
} from '../../../types/intent.types';
import { EditableField } from './EditableField';

interface IntentSummaryGridProps {
  intent: ResearchIntent;
  queriesCount: number;
  onUpdateField: <K extends keyof ResearchIntent>(field: K, value: ResearchIntent[K]) => void;
}

export const IntentSummaryGrid: React.FC<IntentSummaryGridProps> = ({
  intent,
  queriesCount,
  onUpdateField,
}) => {
  return (
    <Grid container spacing={2} mb={2}>
      {/* Purpose */}
      <Grid item xs={6} sm={3}>
        <Card variant="outlined" sx={{ height: '100%', backgroundColor: '#ffffff', border: '1px solid #e5e7eb' }}>
          <CardContent sx={{ py: 1.5, px: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Typography variant="caption" color="#666" fontWeight={500} display="block" mb={0.5}>
              Purpose
            </Typography>
            <EditableField
              field="purpose"
              value={intent.purpose}
              displayValue={PURPOSE_DISPLAY[intent.purpose as ResearchPurpose] || intent.purpose}
              options={Object.entries(PURPOSE_DISPLAY).map(([key, label]) => ({ key, label }))}
              onSave={(val) => onUpdateField('purpose', val as ResearchPurpose)}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* Content Type */}
      <Grid item xs={6} sm={3}>
        <Card variant="outlined" sx={{ height: '100%', backgroundColor: '#ffffff', border: '1px solid #e5e7eb' }}>
          <CardContent sx={{ py: 1.5, px: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Typography variant="caption" color="#666" fontWeight={500} display="block" mb={0.5}>
              Creating
            </Typography>
            <EditableField
              field="content_output"
              value={intent.content_output}
              displayValue={CONTENT_OUTPUT_DISPLAY[intent.content_output as ContentOutput] || intent.content_output}
              options={Object.entries(CONTENT_OUTPUT_DISPLAY).map(([key, label]) => ({ key, label }))}
              onSave={(val) => onUpdateField('content_output', val as ContentOutput)}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* Depth */}
      <Grid item xs={6} sm={3}>
        <Card variant="outlined" sx={{ height: '100%', backgroundColor: '#ffffff', border: '1px solid #e5e7eb' }}>
          <CardContent sx={{ py: 1.5, px: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Typography variant="caption" color="#666" fontWeight={500} display="block" mb={0.5}>
              Depth
            </Typography>
            <EditableField
              field="depth"
              value={intent.depth}
              displayValue={DEPTH_DISPLAY[intent.depth as ResearchDepthLevel] || intent.depth}
              options={Object.entries(DEPTH_DISPLAY).map(([key, label]) => ({ key, label }))}
              onSave={(val) => onUpdateField('depth', val as ResearchDepthLevel)}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* Queries Count */}
      <Grid item xs={6} sm={3}>
        <Card variant="outlined" sx={{ height: '100%', backgroundColor: '#ffffff', border: '1px solid #e5e7eb' }}>
          <CardContent sx={{ py: 1.5, px: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Typography variant="caption" color="#666" fontWeight={500} display="block" mb={0.5}>
              Queries
            </Typography>
            <Typography variant="body2" fontWeight={500} color="#333">
              {queriesCount} targeted
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
