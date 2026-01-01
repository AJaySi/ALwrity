/**
 * IntentConfirmationPanel Component
 * 
 * Shows the AI-inferred research intent and allows user to confirm or modify.
 * Embedded in the existing ResearchInput component.
 */

import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Collapse,
  IconButton,
  Tooltip,
  Grid,
  Card,
  CardContent,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
} from '@mui/material';
import {
  Psychology as BrainIcon,
  CheckCircle as CheckIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  PlayArrow as PlayIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import {
  ResearchIntent,
  AnalyzeIntentResponse,
  ExpectedDeliverable,
  ResearchPurpose,
  ContentOutput,
  ResearchDepthLevel,
  DELIVERABLE_DISPLAY,
  PURPOSE_DISPLAY,
  DEPTH_DISPLAY,
  CONTENT_OUTPUT_DISPLAY,
} from '../../types/intent.types';

interface IntentConfirmationPanelProps {
  isAnalyzing: boolean;
  intentAnalysis: AnalyzeIntentResponse | null;
  confirmedIntent: ResearchIntent | null;
  onConfirm: (intent: ResearchIntent) => void;
  onUpdateField: <K extends keyof ResearchIntent>(field: K, value: ResearchIntent[K]) => void;
  onExecute: () => void;
  onDismiss: () => void;
  isExecuting: boolean;
}

export const IntentConfirmationPanel: React.FC<IntentConfirmationPanelProps> = ({
  isAnalyzing,
  intentAnalysis,
  confirmedIntent,
  onConfirm,
  onUpdateField,
  onExecute,
  onDismiss,
  isExecuting,
}) => {
  const [showDetails, setShowDetails] = React.useState(false);
  const [isEditing, setIsEditing] = React.useState(false);

  // Loading state
  if (isAnalyzing) {
    return (
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mt: 2,
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'primary.light',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
        }}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <CircularProgress size={24} />
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              🧠 Analyzing your research intent...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI is understanding what you want to accomplish
            </Typography>
          </Box>
        </Box>
      </Paper>
    );
  }

  // No analysis yet
  if (!intentAnalysis || !intentAnalysis.success) {
    return null;
  }

  const intent = intentAnalysis.intent;
  const confidence = intent.confidence;
  const isHighConfidence = confidence >= 0.8;

  return (
    <Paper
      elevation={0}
      sx={{
        mt: 2,
        borderRadius: 2,
        border: '1px solid',
        borderColor: isHighConfidence ? 'success.light' : 'warning.light',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: isHighConfidence 
            ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(67, 160, 71, 0.1) 100%)'
            : 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(251, 140, 0, 0.1) 100%)',
        }}
      >
        <Box display="flex" alignItems="center" gap={1.5}>
          <BrainIcon color={isHighConfidence ? 'success' : 'warning'} />
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              AI Understood Your Research
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {intentAnalysis.analysis_summary}
            </Typography>
          </Box>
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip
            size="small"
            label={`${Math.round(confidence * 100)}% confident`}
            color={isHighConfidence ? 'success' : 'warning'}
            variant="outlined"
          />
          <IconButton size="small" onClick={onDismiss}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ p: 2 }}>
        {/* Primary Question */}
        <Alert 
          severity="info" 
          sx={{ mb: 2 }}
          icon={<CheckIcon />}
        >
          <Typography variant="body2" fontWeight={500}>
            <strong>Main Question:</strong> {intent.primary_question}
          </Typography>
        </Alert>

        {/* Quick Summary Grid */}
        <Grid container spacing={2} mb={2}>
          {/* Purpose */}
          <Grid item xs={6} sm={3}>
            <Card variant="outlined" sx={{ height: '100%' }}>
              <CardContent sx={{ py: 1, px: 1.5, '&:last-child': { pb: 1 } }}>
                <Typography variant="caption" color="text.secondary">
                  Purpose
                </Typography>
                {isEditing ? (
                  <FormControl size="small" fullWidth sx={{ mt: 0.5 }}>
                    <Select
                      value={intent.purpose}
                      onChange={(e) => onUpdateField('purpose', e.target.value as ResearchPurpose)}
                    >
                      {Object.entries(PURPOSE_DISPLAY).map(([key, label]) => (
                        <MenuItem key={key} value={key}>{label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ) : (
                  <Typography variant="body2" fontWeight={500}>
                    {PURPOSE_DISPLAY[intent.purpose as ResearchPurpose] || intent.purpose}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Content Type */}
          <Grid item xs={6} sm={3}>
            <Card variant="outlined" sx={{ height: '100%' }}>
              <CardContent sx={{ py: 1, px: 1.5, '&:last-child': { pb: 1 } }}>
                <Typography variant="caption" color="text.secondary">
                  Creating
                </Typography>
                {isEditing ? (
                  <FormControl size="small" fullWidth sx={{ mt: 0.5 }}>
                    <Select
                      value={intent.content_output}
                      onChange={(e) => onUpdateField('content_output', e.target.value as ContentOutput)}
                    >
                      {Object.entries(CONTENT_OUTPUT_DISPLAY).map(([key, label]) => (
                        <MenuItem key={key} value={key}>{label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ) : (
                  <Typography variant="body2" fontWeight={500}>
                    {CONTENT_OUTPUT_DISPLAY[intent.content_output as ContentOutput] || intent.content_output}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Depth */}
          <Grid item xs={6} sm={3}>
            <Card variant="outlined" sx={{ height: '100%' }}>
              <CardContent sx={{ py: 1, px: 1.5, '&:last-child': { pb: 1 } }}>
                <Typography variant="caption" color="text.secondary">
                  Depth
                </Typography>
                {isEditing ? (
                  <FormControl size="small" fullWidth sx={{ mt: 0.5 }}>
                    <Select
                      value={intent.depth}
                      onChange={(e) => onUpdateField('depth', e.target.value as ResearchDepthLevel)}
                    >
                      {Object.entries(DEPTH_DISPLAY).map(([key, label]) => (
                        <MenuItem key={key} value={key}>{label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ) : (
                  <Typography variant="body2" fontWeight={500}>
                    {DEPTH_DISPLAY[intent.depth as ResearchDepthLevel] || intent.depth}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Queries */}
          <Grid item xs={6} sm={3}>
            <Card variant="outlined" sx={{ height: '100%' }}>
              <CardContent sx={{ py: 1, px: 1.5, '&:last-child': { pb: 1 } }}>
                <Typography variant="caption" color="text.secondary">
                  Queries
                </Typography>
                <Typography variant="body2" fontWeight={500}>
                  {intentAnalysis.suggested_queries?.length || 0} targeted
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* What we'll find */}
        <Box mb={2}>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            What I'll find for you:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            {intent.expected_deliverables.slice(0, 5).map((d) => (
              <Chip
                key={d}
                label={DELIVERABLE_DISPLAY[d as ExpectedDeliverable] || d}
                size="small"
                color="primary"
                variant="outlined"
              />
            ))}
            {intent.expected_deliverables.length > 5 && (
              <Chip
                label={`+${intent.expected_deliverables.length - 5} more`}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </Box>

        {/* Expandable Details */}
        <Collapse in={showDetails}>
          <Box sx={{ pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            {/* Secondary Questions */}
            {intent.secondary_questions.length > 0 && (
              <Box mb={2}>
                <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                  Also answering:
                </Typography>
                {intent.secondary_questions.slice(0, 3).map((q, idx) => (
                  <Typography key={idx} variant="body2" sx={{ ml: 1 }}>
                    • {q}
                  </Typography>
                ))}
              </Box>
            )}

            {/* Focus Areas */}
            {intent.focus_areas.length > 0 && (
              <Box mb={2}>
                <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                  Focus areas:
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={0.5}>
                  {intent.focus_areas.map((area, idx) => (
                    <Chip key={idx} label={area} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>
            )}

            {/* Research Angles */}
            {intentAnalysis.suggested_angles?.length > 0 && (
              <Box mb={2}>
                <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                  Research angles:
                </Typography>
                {intentAnalysis.suggested_angles.slice(0, 3).map((angle, idx) => (
                  <Typography key={idx} variant="body2" sx={{ ml: 1 }}>
                    • {angle}
                  </Typography>
                ))}
              </Box>
            )}
          </Box>
        </Collapse>

        {/* Action Buttons */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
          <Box>
            <Button
              size="small"
              onClick={() => setShowDetails(!showDetails)}
              endIcon={showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            >
              {showDetails ? 'Less details' : 'More details'}
            </Button>
            <Button
              size="small"
              startIcon={<EditIcon />}
              onClick={() => setIsEditing(!isEditing)}
              sx={{ ml: 1 }}
            >
              {isEditing ? 'Done editing' : 'Edit'}
            </Button>
          </Box>
          <Box display="flex" gap={1}>
            <Button
              variant="contained"
              color="primary"
              startIcon={isExecuting ? <CircularProgress size={16} color="inherit" /> : <PlayIcon />}
              onClick={() => {
                onConfirm(intent);
                onExecute();
              }}
              disabled={isExecuting}
            >
              {isExecuting ? 'Researching...' : 'Start Research'}
            </Button>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default IntentConfirmationPanel;
