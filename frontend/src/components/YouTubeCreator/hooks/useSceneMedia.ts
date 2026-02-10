// Hook for managing scene media (images and audio)
import { useState, useEffect } from 'react';
import { fetchMediaBlobUrl } from '../../../utils/fetchMediaBlobUrl';

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
    console.log('[useSceneMedia] Image URL changed:', imageUrl);
    let revokedUrl: string | null = null;

    const fetchImage = async () => {
      if (!imageUrl) {
        console.log('[useSceneMedia] No imageUrl, clearing blob');
        setImageBlobUrl(null);
        return;
      }

      setImageLoading(true);
      console.log('[useSceneMedia] Starting to fetch image blob for:', imageUrl);
      try {
        const blobUrl = await fetchMediaBlobUrl(imageUrl);
        if (blobUrl) {
          console.log('[useSceneMedia] Image blob loaded:', blobUrl);
          setImageBlobUrl(blobUrl);
          revokedUrl = blobUrl;
          return;
        }
        // Fallback: use direct URL if blob could not be created (e.g., 404/401 handled upstream)
        console.warn('[useSceneMedia] Blob URL unavailable, falling back to direct imageUrl');
        setImageBlobUrl(imageUrl);
      } catch (error) {
        console.error('[useSceneMedia] Failed to load image:', error);
        // Fallback to direct URL so UI still shows something while we investigate auth/serving
        setImageBlobUrl(imageUrl);
      } finally {
        setImageLoading(false);
      }
    };

    fetchImage();

    return () => {
      if (revokedUrl && revokedUrl.startsWith('blob:')) {
        URL.revokeObjectURL(revokedUrl);
      }
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
  }, [audioUrl, audioBlobUrl]);

  return {
    imageBlobUrl,
    imageLoading,
    audioBlobUrl,
    audioLoading,
  };
};
