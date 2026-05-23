import { useState, useCallback, useRef } from 'react';
import { blogAssetAPI, BlogAssetFull, BlogAsset } from '../api/blogAsset';
import { debug } from '../utils/debug';

export function useBlogAsset() {
  const [assetId, setAssetId] = useState<number | null>(null);
  const [asset, setAsset] = useState<BlogAssetFull | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const createInProgressRef = useRef(false);

  const createAsset = useCallback(async (
    researchKeywords: string,
    topic?: string,
    wordCountTarget?: number,
  ): Promise<number | null> => {
    if (createInProgressRef.current) return assetId;
    createInProgressRef.current = true;
    setLoading(true);
    setError(null);
    try {
      const result = await blogAssetAPI.create({
        research_keywords: researchKeywords,
        topic,
        word_count_target: wordCountTarget,
      });
      const newId = result.asset.id;
      setAssetId(newId);
      setAsset(result.asset as BlogAssetFull);
      debug.log('[BlogAsset] Created:', newId, 'existing:', result.existing);
      return newId;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to create asset';
      setError(msg);
      debug.error('[BlogAsset] Create failed:', msg);
      return null;
    } finally {
      setLoading(false);
      createInProgressRef.current = false;
    }
  }, [assetId]);

  const updatePhase = useCallback(async (
    phase: 'research' | 'outline' | 'content' | 'seo' | 'publish',
    data?: any,
    extra?: Record<string, any>,
  ) => {
    if (assetId === null || assetId === undefined) return;
    setLoading(true);
    try {
      const payload: any = { phase };
      if (data) payload[`${phase}_data`] = data;
      if (extra) Object.assign(payload, extra);
      const result = await blogAssetAPI.update(assetId, payload);
      setAsset((prev: BlogAssetFull | null) => ({
        ...(prev || {}),
        ...result.asset,
        ...(data ? { [`${phase}_data`]: data } : {}),
      }) as BlogAssetFull);
      debug.log('[BlogAsset] Updated phase:', phase, 'asset_id:', assetId);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to update asset';
      setError(msg);
      debug.error('[BlogAsset] Update failed:', msg);
    } finally {
      setLoading(false);
    }
  }, [assetId]);

  const loadAsset = useCallback(async (id: number): Promise<BlogAssetFull | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await blogAssetAPI.get(id);
      setAssetId(id);
      setAsset(result.asset);
      debug.log('[BlogAsset] Loaded:', id, 'phase:', result.asset.phase);
      return result.asset;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load asset';
      setError(msg);
      debug.error('[BlogAsset] Load failed:', msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const resetAsset = useCallback(() => {
    setAssetId(null);
    setAsset(null);
    setError(null);
  }, []);

  return {
    assetId,
    asset,
    loading,
    error,
    createAsset,
    updatePhase,
    loadAsset,
    resetAsset,
  };
}
