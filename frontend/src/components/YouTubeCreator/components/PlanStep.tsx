/**
 * Plan Step Component
 */

import React from 'react';
import {
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  CircularProgress,
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { inputSx, labelSx, helperSx, selectSx } from '../styles';
import { DurationType } from '../constants';

interface PlanStepProps {
  userIdea: string;
  durationType: DurationType;
  referenceImage: string;
  loading: boolean;
  onIdeaChange: (idea: string) => void;
  onDurationChange: (duration: DurationType) => void;
  onReferenceImageChange: (image: string) => void;
  onGeneratePlan: () => void;
}

export const PlanStep: React.FC<PlanStepProps> = React.memo(({
  userIdea,
  durationType,
  referenceImage,
  loading,
  onIdeaChange,
  onDurationChange,
  onReferenceImageChange,
  onGeneratePlan,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Paper
        sx={{
          p: 4,
          backgroundColor: 'white',
          border: '1px solid #e5e5e5',
        }}
      >
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          1️⃣ Plan Your Video
        </Typography>

        <Stack spacing={3}>
          <TextField
            label="What's your video about?"
            placeholder="Example: 'AI explains black holes in 60 seconds' or 'Budget travel guide for Tokyo'"
            value={userIdea}
            onChange={(e) => onIdeaChange(e.target.value)}
            multiline
            rows={4}
            fullWidth
            required
            helperText="Describe the story in one to two sentences. Include audience, outcome, and hook. Tip: name the platform goal (views, subs, clicks)."
            sx={inputSx}
            InputLabelProps={{ sx: labelSx }}
            FormHelperTextProps={{ sx: helperSx }}
          />

          <FormControl fullWidth>
            <InputLabel sx={labelSx}>Video Duration</InputLabel>
            <Select
              value={durationType}
              label="Video Duration"
              onChange={(e) => onDurationChange(e.target.value as DurationType)}
              sx={selectSx}
            >
              <MenuItem value="shorts">Shorts (15-60 seconds)</MenuItem>
              <MenuItem value="medium">Medium (1-4 minutes)</MenuItem>
              <MenuItem value="long">Long (4-10 minutes)</MenuItem>
            </Select>
            <FormHelperText>
              Shorts = vertical bite-sized (≤60s). Medium = quick explainers. Long = deep dives.
            </FormHelperText>
          </FormControl>

          <TextField
            label="Reference Image Description (Optional)"
            placeholder="Example: 'neon-lit Tokyo alley, rainy night, cinematic bokeh' or paste image keywords"
            value={referenceImage}
            onChange={(e) => onReferenceImageChange(e.target.value)}
            multiline
            rows={2}
            fullWidth
            helperText="Optional: Describe visual cues or style you want the visuals to follow."
            sx={inputSx}
            InputLabelProps={{ sx: labelSx }}
            FormHelperTextProps={{ sx: helperSx }}
          />

          <Button
            variant="contained"
            color="error"
            size="large"
            onClick={onGeneratePlan}
            disabled={loading || !userIdea.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
            sx={{ alignSelf: 'flex-start', px: 4 }}
          >
            {loading ? 'Generating Plan...' : 'Generate Video Plan'}
          </Button>
        </Stack>
      </Paper>
    </motion.div>
  );
});

PlanStep.displayName = 'PlanStep';

