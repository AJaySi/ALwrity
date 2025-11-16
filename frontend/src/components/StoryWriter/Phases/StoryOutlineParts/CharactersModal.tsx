import React from 'react';
import { Box, Dialog, DialogActions, DialogContent, DialogTitle, Button, Chip, Typography } from '@mui/material';

interface CharactersModalProps {
  open: boolean;
  sceneNumber: number;
  characters: string[];
  onClose: () => void;
}

const CharactersModal: React.FC<CharactersModalProps> = ({ open, sceneNumber, characters, onClose }) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
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
      <DialogTitle>Characters (Scene {sceneNumber})</DialogTitle>
      <DialogContent dividers sx={{ color: '#2C2416' }}>
        {characters && characters.length > 0 ? (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.25 }}>
            {characters.map((c, idx) => (
              <Chip
                key={idx}
                label={c}
                variant="outlined"
                sx={{ bgcolor: '#fff', color: '#2C2416', borderColor: 'rgba(0,0,0,0.15)' }}
              />
            ))}
          </Box>
        ) : (
          <Typography variant="body2">No characters provided for this scene.</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default CharactersModal;

