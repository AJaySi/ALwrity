import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';

export interface Collection {
  id: number;
  user_id: string;
  name: string;
  description?: string;
  is_public: boolean;
  cover_asset_id?: number;
  asset_count: number;
  created_at: string;
  updated_at: string;
}

export interface CollectionCreateRequest {
  name: string;
  description?: string;
  is_public?: boolean;
}

export interface CollectionUpdateRequest {
  name?: string;
  description?: string;
  is_public?: boolean;
  cover_asset_id?: number;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const useCollections = () => {
  const { getToken } = useAuth();
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCollections = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = await getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/collections`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch collections: ${response.statusText}`);
      }

      const data = await response.json();
      setCollections(data.collections || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch collections');
      setCollections([]);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    fetchCollections();
  }, [fetchCollections]);

  const createCollection = useCallback(async (data: CollectionCreateRequest): Promise<Collection> => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/collections`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to create collection');
      }

      const collection = await response.json();
      setCollections(prev => [...prev, collection]);
      return collection;
    } catch (err) {
      console.error('Error creating collection:', err);
      throw err;
    }
  }, [getToken]);

  const updateCollection = useCallback(async (
    collectionId: number,
    data: CollectionUpdateRequest
  ): Promise<Collection> => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/collections/${collectionId}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to update collection');
      }

      const collection = await response.json();
      setCollections(prev =>
        prev.map(c => c.id === collectionId ? collection : c)
      );
      return collection;
    } catch (err) {
      console.error('Error updating collection:', err);
      throw err;
    }
  }, [getToken]);

  const deleteCollection = useCallback(async (collectionId: number): Promise<boolean> => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/collections/${collectionId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete collection');
      }

      setCollections(prev => prev.filter(c => c.id !== collectionId));
      return true;
    } catch (err) {
      console.error('Error deleting collection:', err);
      throw err;
    }
  }, [getToken]);

  const addAssetsToCollection = useCallback(async (
    collectionId: number,
    assetIds: number[]
  ): Promise<number> => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/collections/${collectionId}/assets`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ asset_ids: assetIds }),
      });

      if (!response.ok) {
        throw new Error('Failed to add assets to collection');
      }

      const result = await response.json();
      // Refresh collections to update asset counts
      await fetchCollections();
      return result.assets_added || 0;
    } catch (err) {
      console.error('Error adding assets to collection:', err);
      throw err;
    }
  }, [getToken, fetchCollections]);

  const removeAssetsFromCollection = useCallback(async (
    collectionId: number,
    assetIds: number[]
  ): Promise<number> => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/collections/${collectionId}/assets`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ asset_ids: assetIds }),
      });

      if (!response.ok) {
        throw new Error('Failed to remove assets from collection');
      }

      const result = await response.json();
      // Refresh collections to update asset counts
      await fetchCollections();
      return result.assets_removed || 0;
    } catch (err) {
      console.error('Error removing assets from collection:', err);
      throw err;
    }
  }, [getToken, fetchCollections]);

  return {
    collections,
    loading,
    error,
    refetch: fetchCollections,
    createCollection,
    updateCollection,
    deleteCollection,
    addAssetsToCollection,
    removeAssetsFromCollection,
  };
};
