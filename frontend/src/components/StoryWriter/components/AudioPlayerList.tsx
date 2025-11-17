import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { aiApiClient } from '../../../api/client';

interface AudioPlayerListProps {
  scenes: any[];
  sceneAudioMap: Map<number, string>;
}

export const AudioPlayerList: React.FC<AudioPlayerListProps> = ({ scenes, sceneAudioMap }) => {
  const [audioBlobUrls, setAudioBlobUrls] = useState<Map<number, string>>(new Map());

  useEffect(() => {
    if (!sceneAudioMap || sceneAudioMap.size === 0) {
      setAudioBlobUrls((prev) => {
        prev.forEach((url) => URL.revokeObjectURL(url));
        return new Map();
      });
      return;
    }

    let isMounted = true;

    const loadAudioBlobs = async () => {
      const entries = Array.from(sceneAudioMap.entries());
      const blobEntries: Array<[number, string]> = [];

      for (const [sceneNumber, audioPath] of entries) {
        if (!audioPath) continue;
        try {
          const normalizedPath = audioPath.startsWith('/') ? audioPath : `/${audioPath}`;
          const response = await aiApiClient.get(normalizedPath, {
            responseType: 'blob',
          });
          const blobUrl = URL.createObjectURL(response.data);
          blobEntries.push([sceneNumber, blobUrl]);
        } catch (err) {
          console.error('Failed to load audio blob:', err);
        }
      }

      if (!isMounted) {
        blobEntries.forEach(([, url]) => URL.revokeObjectURL(url));
        return;
      }

      setAudioBlobUrls((prev) => {
        prev.forEach((url) => URL.revokeObjectURL(url));
        return new Map(blobEntries);
      });
    };

    loadAudioBlobs();

    return () => {
      isMounted = false;
      setAudioBlobUrls((prev) => {
        prev.forEach((url) => URL.revokeObjectURL(url));
        return new Map();
      });
    };
  }, [sceneAudioMap]);

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="body2" sx={{ color: '#5D4037', fontSize: '0.875rem', mb: 2 }}>
        Audio narration generated for {sceneAudioMap.size} scene(s). Listen to audio for each scene:
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {scenes.map((scene: any, index: number) => {
          const sceneNumber = scene.scene_number || index + 1;
          const audioUrl = sceneAudioMap.get(sceneNumber);
          if (!audioUrl) return null;
          const blobUrl = audioBlobUrls.get(sceneNumber);

          return (
            <Box
              key={sceneNumber}
              sx={{
                p: 2,
                backgroundColor: '#FFFFFF',
                borderRadius: '8px',
                border: '1px solid rgba(120, 90, 60, 0.2)',
              }}
            >
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#1A1611' }}>
                Scene {sceneNumber}: {scene.title || `Scene ${sceneNumber}`}
              </Typography>
              <audio
                controls
                src={blobUrl ? blobUrl : storyWriterApi.getAudioUrl(audioUrl)}
                style={{ width: '100%' }}
              >
                Your browser does not support the audio element.
              </audio>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

