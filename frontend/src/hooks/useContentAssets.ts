import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
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
  asset_metadata: Record<string, any>;
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
  source_module?: string | string[]; // Support single or multiple source modules
  search?: string;
  tags?: string[];
  favorites_only?: boolean;
  collection_id?: number;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface AssetListResponse {
  assets: ContentAsset[];
  total: number;
  limit: number;
  offset: number;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const useContentAssets = (filters: AssetFilters = {}) => {
  const { getToken } = useAuth();
  const [assets, setAssets] = useState<ContentAsset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const isFetchingRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Memoize filters to create stable reference - only changes when actual values change
  const apiParams = useMemo(() => {
  const tagsString = filters.tags?.join(',');
  
  return {
    asset_type: filters.asset_type,
    source_module: filters.source_module,
    search: filters.search,
    tags: tagsString,
    favorites_only: filters.favorites_only,
    collection_id: filters.collection_id,
    date_from: filters.date_from,
    date_to: filters.date_to,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
    limit: filters.limit,
    offset: filters.offset,
  };
  }, [
    filters.asset_type,
    filters.source_module,
    filters.search,
    filters.tags,
    filters.favorites_only,
    filters.collection_id,
    filters.date_from,
    filters.date_to,
    filters.sort_by,
    filters.sort_order,
    filters.limit,
    filters.offset,
  ]);

  // Create stable filter key for comparison
  const filterKey = useMemo(() => {
    return JSON.stringify(apiParams);
  }, [apiParams]);

  // Store latest filters in ref for use in fetch function
  const filtersRef = useRef(apiParams);
  useEffect(() => {
    filtersRef.current = apiParams;
  }, [apiParams]);

  // Fetch function - exposed for manual retry, not called automatically on errors
  const fetchAssets = useCallback(async () => {
    // Prevent concurrent fetches
    if (isFetchingRef.current) {
      return;
    }

    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller for this request
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      isFetchingRef.current = true;
      setLoading(true);
      setError(null);

      const token = await getToken();
      if (!token) {
        setLoading(false);
        isFetchingRef.current = false;
        return;
      }

      // Use ref to get latest filters
      const currentFilters = filtersRef.current;
      const params = new URLSearchParams();
      if (currentFilters.asset_type) params.append('asset_type', currentFilters.asset_type);
      if (currentFilters.source_module) {
        // Handle both string and array cases
        if (Array.isArray(currentFilters.source_module)) {
          // For arrays, use the first value (backend doesn't support multiple yet)
          params.append('source_module', currentFilters.source_module[0]);
        } else {
          params.append('source_module', currentFilters.source_module);
        }
      }
      if (currentFilters.search) params.append('search', currentFilters.search);
      if (currentFilters.tags && Array.isArray(currentFilters.tags) && currentFilters.tags.length > 0) params.append('tags', currentFilters.tags.join(','));
      if (currentFilters.favorites_only) params.append('favorites_only', 'true');
      if (currentFilters.collection_id) params.append('collection_id', String(currentFilters.collection_id));
      if (currentFilters.date_from) params.append('date_from', currentFilters.date_from);
      if (currentFilters.date_to) params.append('date_to', currentFilters.date_to);
      if (currentFilters.sort_by) params.append('sort_by', currentFilters.sort_by);
      if (currentFilters.sort_order) params.append('sort_order', currentFilters.sort_order);
      params.append('limit', String(currentFilters.limit || 100));
      params.append('offset', String(currentFilters.offset || 0));

      const response = await fetch(`${API_BASE_URL}/api/content-assets/?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        signal: abortController.signal,
      });

      if (!response.ok) {
        if (response.status === 429) {
          setError('Rate limit exceeded. Please try again later.');
          setAssets([]);
          setTotal(0);
          setLoading(false);
          isFetchingRef.current = false;
          return;
        }
        throw new Error(`Failed to fetch assets: ${response.statusText}`);
      }

      const data: AssetListResponse = await response.json();
      setAssets(data.assets);
      setTotal(data.total);
    } catch (err) {
      // Don't set error for aborted requests
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Network error. Please check your connection.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to fetch assets');
      }
      setAssets([]);
    } finally {
      setLoading(false);
      isFetchingRef.current = false;
    }
  }, [getToken]); // Only depend on getToken, use ref for filters

  // Fetch on mount and when filters change - but only once per filter change
  // NO automatic retry on errors - user must call refetch() manually
  useEffect(() => {
    fetchAssets();
    
    // Cleanup: abort on unmount or filter change
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [filterKey, fetchAssets]); // Include fetchAssets but it's stable due to ref usage

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

