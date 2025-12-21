/**
 * Custom hook for loading avatar as blob URL from authenticated endpoints
 */

import { useState, useEffect } from 'react';
import { fetchMediaBlobUrl } from '../../../utils/fetchMediaBlobUrl';

interface UseAvatarBlobUrlResult {
  avatarBlobUrl: string | null;
  avatarLoading: boolean;
}

export const useAvatarBlobUrl = (avatarUrl: string | null | undefined): UseAvatarBlobUrlResult => {
  const [avatarBlobUrl, setAvatarBlobUrl] = useState<string | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(false);

  useEffect(() => {
    if (!avatarUrl) {
      setAvatarBlobUrl(null);
      setAvatarLoading(false);
      return;
    }

    // If it's a data URL, use it directly (no blob needed)
    if (avatarUrl.startsWith('data:')) {
      setAvatarBlobUrl(null);
      setAvatarLoading(false);
      return;
    }

    // If it's an authenticated YouTube image endpoint, load as blob
    const isYouTubeImage = avatarUrl.includes('/api/youtube/images/') || 
                          avatarUrl.includes('/api/youtube/avatar/');
    
    if (!isYouTubeImage) {
      setAvatarBlobUrl(null);
      setAvatarLoading(false);
      return;
    }

    // Fetch as blob for authenticated endpoints
    let isMounted = true;
    const currentAvatarUrl = avatarUrl;
    setAvatarLoading(true);

    const loadAvatarBlob = async () => {
      try {
        // Normalize path
        let imagePath = currentAvatarUrl.startsWith('/') 
          ? currentAvatarUrl 
          : `/${currentAvatarUrl}`;
        
        // Remove query parameters if present
        imagePath = imagePath.split('?')[0];

        const blobUrl = await fetchMediaBlobUrl(imagePath);
        
        if (!isMounted || avatarUrl !== currentAvatarUrl) {
          if (blobUrl) {
            URL.revokeObjectURL(blobUrl);
          }
          return;
        }
        
        setAvatarBlobUrl((prevBlobUrl) => {
          // Clean up previous blob URL if exists
          if (prevBlobUrl && prevBlobUrl !== blobUrl && prevBlobUrl.startsWith('blob:')) {
            URL.revokeObjectURL(prevBlobUrl);
          }
          return blobUrl;
        });
        setAvatarLoading(false);
      } catch (err) {
        console.error('[useAvatarBlobUrl] Failed to load avatar blob:', err);
        if (isMounted && avatarUrl === currentAvatarUrl) {
          setAvatarBlobUrl(null);
          setAvatarLoading(false);
        }
      }
    };

    loadAvatarBlob();

    return () => {
      isMounted = false;
      // Cleanup blob URL when component unmounts or URL changes
      setAvatarBlobUrl((prevBlobUrl) => {
        if (prevBlobUrl && prevBlobUrl.startsWith('blob:')) {
          URL.revokeObjectURL(prevBlobUrl);
        }
        return null;
      });
      setAvatarLoading(false);
    };
  }, [avatarUrl]);

  return { avatarBlobUrl, avatarLoading };
};

