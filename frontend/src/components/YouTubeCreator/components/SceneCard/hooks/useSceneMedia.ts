// Hook for managing scene media (images and audio)
import { useState, useEffect } from 'react';
import { fetchMediaBlobUrl } from '../../../../../utils/fetchMediaBlobUrl';

interface UseSceneMediaProps {
  imageUrl?: string | null;
  audioUrl?: string | null;
}

export const useSceneMedia = ({ imageUrl, audioUrl }: UseSceneMediaProps) => {
  const [imageBlobUrl, setImageBlobUrl] = useState<string | null>(null);
  const [imageLoading, setImageLoading] = useState(false);
  const [audioBlobUrl, setAudioBlobUrl] = useState<string | null>(null);
  const [audioLoading, setAudioLoading] = useState(false);

  useEffect(() => {
    if (imageUrl) {
      setImageLoading(true);
      fetchMediaBlobUrl(imageUrl)
        .then(setImageBlobUrl)
        .catch(console.error)
        .finally(() => setImageLoading(false));
    } else {
      setImageBlobUrl(null);
    }

    return () => {
      if (imageBlobUrl) URL.revokeObjectURL(imageBlobUrl);
    };
  }, [imageUrl]);

  useEffect(() => {
    if (audioUrl) {
      setAudioLoading(true);
      fetchMediaBlobUrl(audioUrl)
        .then(setAudioBlobUrl)
        .catch(console.error)
        .finally(() => setAudioLoading(false));
    } else {
      setAudioBlobUrl(null);
    }

    return () => {
      if (audioBlobUrl) URL.revokeObjectURL(audioBlobUrl);
    };
  }, [audioUrl]);

  return {
    imageBlobUrl,
    imageLoading,
    audioBlobUrl,
    audioLoading,
  };
};
