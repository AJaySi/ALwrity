import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';

export interface ContentAsset {
  id: number;
  user_id: string;
  asset_type: 'text' | 'image' | 'video' | 'audio';
  source_module: string;
  filename: string;
  file_url: string;
  file_path?: string;
  file_size?: number;
  mime_type?: string;
  title?: string;
  description?: string;
  prompt?: string;
  tags: string[];
  metadata: Record<string, any>;
  provider?: string;
  model?: string;
  cost: number;
  generation_time?: number;
  is_favorite: boolean;
  download_count: number;
  share_count: number;
  created_at: string;
  updated_at: string;
}

export interface AssetFilters {
  asset_type?: 'text' | 'image' | 'video' | 'audio';
  source_module?: string;
  search?: string;
  tags?: string[];
  favorites_only?: boolean;
  limit?: number;
  offset?: number;
}

export interface AssetListResponse {
  assets: ContentAsset[];
  total: number;
  limit: number;
  offset: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useContentAssets = (filters: AssetFilters = {}) => {
  const { getToken } = useAuth();
  const [assets, setAssets] = useState<ContentAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const fetchAssets = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const params = new URLSearchParams();
      if (filters.asset_type) params.append('asset_type', filters.asset_type);
      if (filters.source_module) params.append('source_module', filters.source_module);
      if (filters.search) params.append('search', filters.search);
      if (filters.tags && filters.tags.length > 0) params.append('tags', filters.tags.join(','));
      if (filters.favorites_only) params.append('favorites_only', 'true');
      params.append('limit', String(filters.limit || 100));
      params.append('offset', String(filters.offset || 0));

      // Add cache busting for fresh data
      params.append('_t', String(Date.now()));

      const response = await fetch(`${API_BASE_URL}/api/content-assets/?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch assets: ${response.statusText}`);
      }

      const data: AssetListResponse = await response.json();
      setAssets(data.assets);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch assets');
      setAssets([]);
    } finally {
      setLoading(false);
    }
  }, [getToken, filters]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  const toggleFavorite = useCallback(async (assetId: number) => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/${assetId}/favorite`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to toggle favorite');
      }

      const data = await response.json();
      
      // Update local state
      setAssets(prev =>
        prev.map(asset =>
          asset.id === assetId ? { ...asset, is_favorite: data.is_favorite } : asset
        )
      );

      return data.is_favorite;
    } catch (err) {
      console.error('Error toggling favorite:', err);
      throw err;
    }
  }, [getToken]);

  const deleteAsset = useCallback(async (assetId: number) => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/api/content-assets/${assetId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete asset');
      }

      // Remove from local state
      setAssets(prev => prev.filter(asset => asset.id !== assetId));
      setTotal(prev => prev - 1);

      return true;
    } catch (err) {
      console.error('Error deleting asset:', err);
      throw err;
    }
  }, [getToken]);

  const trackUsage = useCallback(async (assetId: number, action: 'download' | 'share' | 'access') => {
    try {
      const token = await getToken();
      if (!token) {
        return;
      }

      await fetch(`${API_BASE_URL}/api/content-assets/${assetId}/usage?action=${action}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
    } catch (err) {
      console.error('Error tracking usage:', err);
    }
  }, [getToken]);

  const updateAsset = useCallback(async (
    assetId: number,
    updates: { title?: string; description?: string; tags?: string[] }
  ) => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const body: any = {};
      if (updates.title !== undefined) body.title = updates.title;
      if (updates.description !== undefined) body.description = updates.description;
      if (updates.tags !== undefined) body.tags = updates.tags; // Send as array, not comma-separated

      const response = await fetch(`${API_BASE_URL}/api/content-assets/${assetId}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error('Failed to update asset');
      }

      const updatedAsset = await response.json();
      
      // Update local state
      setAssets(prev =>
        prev.map(asset =>
          asset.id === assetId ? { ...asset, ...updatedAsset } : asset
        )
      );

      return updatedAsset;
    } catch (err) {
      console.error('Error updating asset:', err);
      throw err;
    }
  }, [getToken]);

  return {
    assets,
    loading,
    error,
    total,
    refetch: fetchAssets,
    toggleFavorite,
    deleteAsset,
    updateAsset,
    trackUsage,
  };
};

