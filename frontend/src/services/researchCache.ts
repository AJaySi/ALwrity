/**
 * Frontend Research Cache Service
 * 
 * Provides persistent caching for research results to survive page refreshes,
 * browser restarts, and internet disconnections.
 */

import { BlogResearchResponse } from './blogWriterApi';

interface CachedResearchEntry {
  result: BlogResearchResponse;
  keywords: string[];
  industry: string;
  target_audience: string;
  created_at: string;
  expires_at: string;
  cache_key: string;
}

interface CacheStats {
  total_entries: number;
  expired_entries: number;
  valid_entries: number;
  cache_size_mb: number;
}

class ResearchCacheService {
  private readonly CACHE_KEY_PREFIX = 'alwrity_research_';
  private readonly CACHE_VERSION = '1.0';
  private readonly DEFAULT_TTL_HOURS = 24;
  private readonly MAX_CACHE_SIZE_MB = 50; // 50MB max cache size

  /**
   * Generate a cache key for research parameters
   */
  private generateCacheKey(keywords: string[], industry: string, target_audience: string): string {
    const normalized_keywords = keywords.map(k => k.toLowerCase().trim()).sort();
    const normalized_industry = (industry || 'general').toLowerCase().trim();
    const normalized_audience = (target_audience || 'general').toLowerCase().trim();
    
    const cache_string = `${normalized_keywords.join(',')}|${normalized_industry}|${normalized_audience}`;
    const hash = this.simpleHash(cache_string);
    
    return `${this.CACHE_KEY_PREFIX}${this.CACHE_VERSION}_${hash}`;
  }

  /**
   * Simple hash function for cache keys
   */
  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }

  /**
   * Check if a cache entry is still valid
   */
  private isEntryValid(entry: CachedResearchEntry): boolean {
    const now = new Date();
    const expiresAt = new Date(entry.expires_at);
    return now < expiresAt;
  }

  /**
   * Clean up expired entries
   */
  private cleanupExpiredEntries(): void {
    const keys = Object.keys(localStorage);
    const expiredKeys: string[] = [];

    keys.forEach(key => {
      if (key.startsWith(this.CACHE_KEY_PREFIX)) {
        try {
          const entry = JSON.parse(localStorage.getItem(key) || '{}') as CachedResearchEntry;
          if (!this.isEntryValid(entry)) {
            expiredKeys.push(key);
          }
        } catch (error) {
          // Invalid JSON, remove it
          expiredKeys.push(key);
        }
      }
    });

    expiredKeys.forEach(key => {
      localStorage.removeItem(key);
      console.log(`Removed expired cache entry: ${key}`);
    });
  }

  /**
   * Get cache size in MB
   */
  private getCacheSizeMB(): number {
    let totalSize = 0;
    const keys = Object.keys(localStorage);
    
    keys.forEach(key => {
      if (key.startsWith(this.CACHE_KEY_PREFIX)) {
        const value = localStorage.getItem(key) || '';
        totalSize += key.length + value.length;
      }
    });

    return totalSize / (1024 * 1024); // Convert to MB
  }

  /**
   * Evict oldest entries if cache is too large
   */
  private evictOldestEntries(): void {
    const keys = Object.keys(localStorage);
    const cacheEntries: Array<{ key: string; created_at: string }> = [];

    keys.forEach(key => {
      if (key.startsWith(this.CACHE_KEY_PREFIX)) {
        try {
          const entry = JSON.parse(localStorage.getItem(key) || '{}') as CachedResearchEntry;
          cacheEntries.push({
            key,
            created_at: entry.created_at
          });
        } catch (error) {
          // Invalid entry, remove it
          localStorage.removeItem(key);
        }
      }
    });

    // Sort by creation time (oldest first)
    cacheEntries.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());

    // Remove oldest entries until we're under the limit
    const maxSizeMB = this.MAX_CACHE_SIZE_MB;
    while (this.getCacheSizeMB() > maxSizeMB && cacheEntries.length > 0) {
      const oldest = cacheEntries.shift();
      if (oldest) {
        localStorage.removeItem(oldest.key);
        console.log(`Evicted oldest cache entry: ${oldest.key}`);
      }
    }
  }

  /**
   * Get cached research result
   */
  getCachedResult(keywords: string[], industry: string, target_audience: string): BlogResearchResponse | null {
    try {
      this.cleanupExpiredEntries();
      
      const cacheKey = this.generateCacheKey(keywords, industry, target_audience);
      const cachedData = localStorage.getItem(cacheKey);
      
      if (!cachedData) {
        console.log(`Cache miss for keywords: ${keywords.join(', ')}`);
        return null;
      }

      const entry = JSON.parse(cachedData) as CachedResearchEntry;
      
      if (!this.isEntryValid(entry)) {
        localStorage.removeItem(cacheKey);
        console.log(`Cache entry expired for keywords: ${keywords.join(', ')}`);
        return null;
      }

      console.log(`Cache hit for keywords: ${keywords.join(', ')} (saved API call)`);
      return entry.result;
    } catch (error) {
      console.error('Error retrieving cached result:', error);
      return null;
    }
  }

  /**
   * Cache a research result
   */
  cacheResult(
    keywords: string[], 
    industry: string, 
    target_audience: string, 
    result: BlogResearchResponse,
    ttlHours: number = this.DEFAULT_TTL_HOURS
  ): void {
    try {
      this.cleanupExpiredEntries();
      this.evictOldestEntries();

      const cacheKey = this.generateCacheKey(keywords, industry, target_audience);
      const now = new Date();
      const expiresAt = new Date(now.getTime() + (ttlHours * 60 * 60 * 1000));

      const entry: CachedResearchEntry = {
        result,
        keywords,
        industry,
        target_audience,
        created_at: now.toISOString(),
        expires_at: expiresAt.toISOString(),
        cache_key: cacheKey
      };

      localStorage.setItem(cacheKey, JSON.stringify(entry));
      console.log(`Cached research result for keywords: ${keywords.join(', ')}`);
    } catch (error) {
      console.error('Error caching result:', error);
    }
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): CacheStats {
    this.cleanupExpiredEntries();
    
    const keys = Object.keys(localStorage);
    let totalEntries = 0;
    let expiredEntries = 0;
    let validEntries = 0;

    keys.forEach(key => {
      if (key.startsWith(this.CACHE_KEY_PREFIX)) {
        totalEntries++;
        try {
          const entry = JSON.parse(localStorage.getItem(key) || '{}') as CachedResearchEntry;
          if (this.isEntryValid(entry)) {
            validEntries++;
          } else {
            expiredEntries++;
          }
        } catch (error) {
          expiredEntries++;
        }
      }
    });

    return {
      total_entries: totalEntries,
      expired_entries: expiredEntries,
      valid_entries: validEntries,
      cache_size_mb: this.getCacheSizeMB()
    };
  }

  /**
   * Clear all cached research results
   */
  clearCache(): void {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(this.CACHE_KEY_PREFIX)) {
        localStorage.removeItem(key);
      }
    });
    console.log('Research cache cleared');
  }

  /**
   * Get all cached entries (for debugging)
   */
  getAllCachedEntries(): CachedResearchEntry[] {
    const entries: CachedResearchEntry[] = [];
    const keys = Object.keys(localStorage);

    keys.forEach(key => {
      if (key.startsWith(this.CACHE_KEY_PREFIX)) {
        try {
          const entry = JSON.parse(localStorage.getItem(key) || '{}') as CachedResearchEntry;
          entries.push(entry);
        } catch (error) {
          console.error(`Error parsing cache entry ${key}:`, error);
        }
      }
    });

    return entries.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }
}

// Export singleton instance
export const researchCache = new ResearchCacheService();
export default researchCache;
