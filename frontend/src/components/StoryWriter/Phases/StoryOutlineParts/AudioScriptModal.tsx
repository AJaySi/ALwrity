import React from 'react';
import { Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField } from '@mui/material';

interface AudioScriptModalProps {
  open: boolean;
  sceneNumber: number;
  value: string;
  onChange: (v: string) => void;
  onClose: () => void;
  onSave: () => void;
  // audio settings
  audioProvider: string;
  audioLang: string;
  audioSlow: boolean;
  audioRate: number;
  onChangeProvider: (v: string) => void;
  onChangeLang: (v: string) => void;
  onChangeSlow: (v: boolean) => void;
  onChangeRate: (v: number) => void;
  audioUrl?: string | null;
}

const AudioScriptModal: React.FC<AudioScriptModalProps> = ({
  open, sceneNumber, value, onChange, onClose, onSave,
  audioProvider, audioLang, audioSlow, audioRate,
  onChangeProvider, onChangeLang, onChangeSlow, onChangeRate,
  audioUrl,
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: '#fff',
          borderRadius: 2,
          boxShadow: '0 24px 64px rgba(0,0,0,0.18)',
          border: '1px solid rgba(0,0,0,0.06)',
        },
      }}
    >
      <DialogTitle>Edit Audio Narration Script (Scene {sceneNumber})</DialogTitle>
      <DialogContent dividers sx={{ color: '#2C2416' }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            '& .MuiFormLabel-root': { color: '#6b5846' },
            '& .MuiInputBase-root': { color: '#2C2416' },
          }}
        >
          {audioUrl ? (
            <Box
              sx={{
                p: 1,
                backgroundColor: 'rgba(0,0,0,0.03)',
                borderRadius: 1,
                border: '1px solid rgba(0,0,0,0.06)',
              }}
            >
              <audio controls src={audioUrl || undefined} style={{ width: '100%' }}>
                Your browser does not support the audio element.
              </audio>
            </Box>
          ) : null}
          <TextField
            label="Audio Narration"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            multiline
            minRows={6}
            fullWidth
          />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              select
              label="Audio Provider"
              value={audioProvider}
              onChange={(e) => onChangeProvider(e.target.value)}
              SelectProps={{ native: true }}
            >
              <option value="gtts">gTTS</option>
              <option value="pyttsx3">pyttsx3</option>
            </TextField>
            <TextField
              label="Language (e.g., en, hi)"
              value={audioLang}
              onChange={(e) => onChangeLang(e.target.value)}
            />
            <TextField
              select
              label="Slow (gTTS)"
              value={audioSlow ? 'true' : 'false'}
              onChange={(e) => onChangeSlow(e.target.value === 'true')}
              SelectProps={{ native: true }}
            >
              <option value="false">Normal</option>
              <option value="true">Slow</option>
            </TextField>
            <TextField
              type="number"
              label="Rate (pyttsx3)"
              value={audioRate}
              onChange={(e) => onChangeRate(Number(e.target.value))}
              inputProps={{ min: 50, max: 300, step: 10 }}
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onSave}>Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default AudioScriptModal;

