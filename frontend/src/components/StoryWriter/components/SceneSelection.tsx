import React from 'react';
import {
  Box,
  Typography,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Collapse,
  IconButton,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

interface SceneSelectionProps {
  scenes: any[];
  selectedScenes: Set<number>;
  onSelectedScenesChange: (scenes: Set<number>) => void;
  sceneAudioMap?: Map<number, string> | null;
  showSceneSelection: boolean;
  onShowSceneSelectionChange: (show: boolean) => void;
}

export const SceneSelection: React.FC<SceneSelectionProps> = ({
  scenes,
  selectedScenes,
  onSelectedScenesChange,
  sceneAudioMap,
  showSceneSelection,
  onShowSceneSelectionChange,
}) => {
  const handleSceneSelectionToggle = (sceneNumber: number) => {
    const next = new Set(selectedScenes);
    if (next.has(sceneNumber)) {
      next.delete(sceneNumber);
    } else {
      next.add(sceneNumber);
    }
    onSelectedScenesChange(next);
  };

  const handleSelectAllScenes = () => {
    const allSceneNumbers = new Set(
      scenes.map((scene: any, index: number) => scene.scene_number || index + 1)
    );
    onSelectedScenesChange(allSceneNumbers);
  };

  const handleDeselectAllScenes = () => {
    onSelectedScenesChange(new Set());
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" sx={{ color: '#5D4037', fontWeight: 500 }}>
          Select scenes to generate audio for:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            size="small"
            variant="text"
            onClick={handleSelectAllScenes}
            sx={{ minWidth: 'auto', px: 1, fontSize: '0.75rem' }}
          >
            Select All
          </Button>
          <Button
            size="small"
            variant="text"
            onClick={handleDeselectAllScenes}
            sx={{ minWidth: 'auto', px: 1, fontSize: '0.75rem' }}
          >
            Deselect All
          </Button>
          <IconButton
            size="small"
            onClick={() => onShowSceneSelectionChange(!showSceneSelection)}
            sx={{ p: 0.5 }}
          >
            {showSceneSelection ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Box>
      <Collapse in={showSceneSelection}>
        <FormGroup sx={{ pl: 1 }}>
          {scenes.map((scene: any, index: number) => {
            const sceneNumber = scene.scene_number || index + 1;
            const hasAudioForScene = sceneAudioMap?.has(sceneNumber);
            return (
              <FormControlLabel
                key={sceneNumber}
                control={
                  <Checkbox
                    checked={selectedScenes.has(sceneNumber)}
                    onChange={() => handleSceneSelectionToggle(sceneNumber)}
                    size="small"
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2">
                      Scene {sceneNumber}: {scene.title || `Scene ${sceneNumber}`}
                    </Typography>
                    {hasAudioForScene && (
                      <CheckCircleIcon sx={{ fontSize: 16, color: '#4caf50' }} />
                    )}
                  </Box>
                }
              />
            );
          })}
        </FormGroup>
      </Collapse>
    </Box>
  );
};

