/**
 * Media Cache Utility
 * 
 * Provides intelligent caching for images, videos, and audio to prevent
 * unnecessary network requests when navigating between phases.
 * 
 * Enhanced with scene-specific cache keys to prevent cross-contamination
 * between different podcasts and scenes.
 */

interface CacheEntry {
  blobUrl: string;
  timestamp: number;
  originalUrl: string;
  mediaType: 'image' | 'video' | 'audio';
  size?: number;
  sceneId?: string;
  projectId?: string;
}

class MediaCache {
  private cache = new Map<string, CacheEntry>();
  private readonly maxAge = 10 * 60 * 1000; // 10 minutes
  private readonly maxSize = 50; // Maximum number of cached items
  private blobCleanupMap = new Map<string, string>(); // Maps blobUrl to cache key

  /**
   * Generate a unique cache key that includes scene and project context
   */
  private generateCacheKey(url: string, sceneId?: string, projectId?: string): string {
    // Create a composite key that prevents cross-contamination
    const parts = [url];
    if (sceneId) parts.push(`scene:${sceneId}`);
    if (projectId) parts.push(`project:${projectId}`);
    return parts.join('|');
  }

  /**
   * Extract original URL from cache key
   */
  private extractOriginalUrl(cacheKey: string): string {
    return cacheKey.split('|')[0];
  }

  /**
   * Get cached blob URL for a media resource with optional scene context
   */
  get(url: string, sceneId?: string, projectId?: string): string | null {
    const cacheKey = this.generateCacheKey(url, sceneId, projectId);
    const entry = this.cache.get(cacheKey);
    
    if (!entry) {
      // Try without scene context for backwards compatibility
      const fallbackKey = this.generateCacheKey(url);
      const fallbackEntry = this.cache.get(fallbackKey);
      if (fallbackEntry) {
        console.log(`[MediaCache] Cache hit (fallback) for ${fallbackEntry.mediaType}:`, url);
        return fallbackEntry.blobUrl;
      }
      return null;
    }

    // Check if cache entry is still valid
    if (Date.now() - entry.timestamp > this.maxAge) {
      this.invalidate(cacheKey);
      return null;
    }

    console.log(`[MediaCache] Cache hit for ${entry.mediaType}:`, url, 
      sceneId ? `(scene: ${sceneId})` : '', 
      projectId ? `(project: ${projectId})` : '');
    return entry.blobUrl;
  }

  /**
   * Set cached blob URL for a media resource with scene context
   */
  set(url: string, blobUrl: string, mediaType: 'image' | 'video' | 'audio', size?: number, sceneId?: string, projectId?: string): void {
    const cacheKey = this.generateCacheKey(url, sceneId, projectId);
    
    // Clean up existing blob URL if it exists
    const existingEntry = this.cache.get(cacheKey);
    if (existingEntry && existingEntry.blobUrl !== blobUrl) {
      this.revokeBlob(existingEntry.blobUrl);
    }
    
    const entry: CacheEntry = {
      blobUrl,
      timestamp: Date.now(),
      originalUrl: url,
      mediaType,
      size,
      sceneId,
      projectId
    };

    this.cache.set(cacheKey, entry);
    this.blobCleanupMap.set(blobUrl, cacheKey);

    // Enforce cache size limit
    if (this.cache.size > this.maxSize) {
      this.evictOldest();
    }

if (process.env.NODE_ENV === 'development') {
      console.log(`[MediaCache] Cached ${mediaType}:`, url.split('?')[0],
        sceneId ? `(scene: ${sceneId})` : '',
        projectId ? `(project: ${projectId})` : '');
    }
  }

  /**
   * Check if URL is cached (with optional scene context)
   */
  has(url: string, sceneId?: string, projectId?: string): boolean {
    const cacheKey = this.generateCacheKey(url, sceneId, projectId);
    const entry = this.cache.get(cacheKey);
    if (!entry) return false;
    
    // Check if still valid
    if (Date.now() - entry.timestamp > this.maxAge) {
      this.invalidate(cacheKey);
      return false;
    }
    
    return true;
  }

  /**
   * Invalidate cache entry for a specific URL (with optional scene context)
   */
  invalidate(url: string, sceneId?: string, projectId?: string): void {
    const cacheKey = this.generateCacheKey(url, sceneId, projectId);
    const entry = this.cache.get(cacheKey);
    if (entry) {
      this.revokeBlob(entry.blobUrl);
      this.cache.delete(cacheKey);
      this.blobCleanupMap.delete(entry.blobUrl);
    }
  }

  /**
   * Clear all cache
   */
  clear(): void {
    // Revoke all blob URLs
    for (const entry of this.cache.values()) {
      this.revokeBlob(entry.blobUrl);
    }
    
    this.cache.clear();
    this.blobCleanupMap.clear();
    console.log('[MediaCache] Cache cleared');
  }

  /**
   * Clear cache for specific scene
   */
  clearScene(sceneId: string): void {
    const toDelete: string[] = [];
    
    for (const [cacheKey, entry] of this.cache.entries()) {
      if (entry.sceneId === sceneId) {
        toDelete.push(cacheKey);
      }
    }

    toDelete.forEach(cacheKey => {
      const entry = this.cache.get(cacheKey);
      if (entry) {
        this.revokeBlob(entry.blobUrl);
        this.cache.delete(cacheKey);
        this.blobCleanupMap.delete(entry.blobUrl);
      }
    });

    if (toDelete.length > 0) {
      console.log(`[MediaCache] Cleared ${toDelete.length} cache entries for scene: ${sceneId}`);
    }
  }

  /**
   * Clear cache for specific project
   */
  clearProject(projectId: string): void {
    const toDelete: string[] = [];
    
    for (const [cacheKey, entry] of this.cache.entries()) {
      if (entry.projectId === projectId) {
        toDelete.push(cacheKey);
      }
    }

    toDelete.forEach(cacheKey => {
      const entry = this.cache.get(cacheKey);
      if (entry) {
        this.revokeBlob(entry.blobUrl);
        this.cache.delete(cacheKey);
        this.blobCleanupMap.delete(entry.blobUrl);
      }
    });

    if (toDelete.length > 0) {
      console.log(`[MediaCache] Cleared ${toDelete.length} cache entries for project: ${projectId}`);
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const stats = {
      totalEntries: this.cache.size,
      entriesByType: {} as Record<string, number>,
      entriesByScene: {} as Record<string, number>,
      entriesByProject: {} as Record<string, number>,
      totalSize: 0,
      oldestEntry: 0,
      newestEntry: 0
    };

    let oldest = Date.now();
    let newest = 0;

    for (const entry of this.cache.values()) {
      // Count by type
      stats.entriesByType[entry.mediaType] = (stats.entriesByType[entry.mediaType] || 0) + 1;
      
      // Count by scene
      if (entry.sceneId) {
        stats.entriesByScene[entry.sceneId] = (stats.entriesByScene[entry.sceneId] || 0) + 1;
      }
      
      // Count by project
      if (entry.projectId) {
        stats.entriesByProject[entry.projectId] = (stats.entriesByProject[entry.projectId] || 0) + 1;
      }
      
      // Sum sizes
      if (entry.size) {
        stats.totalSize += entry.size;
      }
      
      // Track ages
      oldest = Math.min(oldest, entry.timestamp);
      newest = Math.max(newest, entry.timestamp);
    }

    stats.oldestEntry = oldest > 0 ? Date.now() - oldest : 0;
    stats.newestEntry = newest > 0 ? Date.now() - newest : 0;

    return stats;
  }

  /**
   * Clean up expired entries
   */
  cleanup(): void {
    const now = Date.now();
    const toDelete: string[] = [];

    for (const [cacheKey, entry] of this.cache.entries()) {
      if (now - entry.timestamp > this.maxAge) {
        toDelete.push(cacheKey);
      }
    }

    toDelete.forEach(cacheKey => this.invalidate(this.extractOriginalUrl(cacheKey)));
    
    if (toDelete.length > 0) {
      console.log(`[MediaCache] Cleaned up ${toDelete.length} expired entries`);
    }
  }

  /**
   * Revoke blob URL safely
   */
  private revokeBlob(blobUrl: string): void {
    try {
      if (blobUrl.startsWith('blob:')) {
        URL.revokeObjectURL(blobUrl);
      }
    } catch (error) {
      console.warn('[MediaCache] Failed to revoke blob URL:', error);
    }
  }

  /**
   * Evict oldest cache entry
   */
  private evictOldest(): void {
    let oldestKey = '';
    let oldestTime = Date.now();

    for (const [cacheKey, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTime) {
        oldestTime = entry.timestamp;
        oldestKey = cacheKey;
      }
    }

    if (oldestKey) {
      const entry = this.cache.get(oldestKey);
      if (entry) {
        console.log('[MediaCache] Evicted oldest entry:', this.extractOriginalUrl(oldestKey), 
          entry.sceneId ? `(scene: ${entry.sceneId})` : '');
      }
      this.invalidate(this.extractOriginalUrl(oldestKey));
    }
  }
}

// Export singleton instance
export const mediaCache = new MediaCache();

// Set up periodic cleanup
setInterval(() => {
  mediaCache.cleanup();
}, 5 * 60 * 1000); // Clean up every 5 minutes

// Export utility functions with enhanced scene-aware signatures
export const getCachedMedia = (url: string, sceneId?: string, projectId?: string): string | null => {
  return mediaCache.get(url, sceneId, projectId);
};

export const setCachedMedia = (
  url: string, 
  blobUrl: string, 
  mediaType: 'image' | 'video' | 'audio', 
  size?: number,
  sceneId?: string,
  projectId?: string
): void => {
  mediaCache.set(url, blobUrl, mediaType, size, sceneId, projectId);
};

export const hasCachedMedia = (url: string, sceneId?: string, projectId?: string): boolean => {
  return mediaCache.has(url, sceneId, projectId);
};

export const invalidateMediaCache = (url: string, sceneId?: string, projectId?: string): void => {
  mediaCache.invalidate(url, sceneId, projectId);
};

export const clearMediaCache = (): void => {
  mediaCache.clear();
};

export const clearSceneMediaCache = (sceneId: string): void => {
  mediaCache.clearScene(sceneId);
};

export const clearProjectMediaCache = (projectId: string): void => {
  mediaCache.clearProject(projectId);
};

export const getMediaCacheStats = () => {
  return mediaCache.getStats();
};
