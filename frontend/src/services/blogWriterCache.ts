/**
 * Blog Writer Cache Service
 * 
 * Provides persistent caching for outline and content to survive page refreshes
 * and avoid unnecessary API calls. Shared by both CopilotKit and manual flows.
 */

class BlogWriterCacheService {
  private readonly OUTLINE_CACHE_KEY = 'blog_outline';
  private readonly TITLE_OPTIONS_CACHE_KEY = 'blog_title_options';
  private readonly CONTENT_CACHE_PREFIX = 'blog_content_';

  /**
   * Get cached outline for research keywords
   */
  getCachedOutline(researchKeywords: string[]): { outline: any[]; title_options?: string[] } | null {
    try {
      if (typeof window === 'undefined') return null;

      const savedOutline = localStorage.getItem(this.OUTLINE_CACHE_KEY);
      const savedTitleOptions = localStorage.getItem(this.TITLE_OPTIONS_CACHE_KEY);

      if (!savedOutline) {
        return null;
      }

      const parsedOutline = JSON.parse(savedOutline);
      if (!Array.isArray(parsedOutline) || parsedOutline.length === 0) {
        return null;
      }

      // Basic validation: if we have an outline saved and it has sections, use it
      // More sophisticated matching could compare research keywords if needed
      const titleOptions = savedTitleOptions ? JSON.parse(savedTitleOptions) : undefined;

      console.log(`Cache hit for outline (${parsedOutline.length} sections)`);
      return {
        outline: parsedOutline,
        title_options: titleOptions
      };
    } catch (error) {
      console.error('Error retrieving cached outline:', error);
      return null;
    }
  }

  /**
   * Cache outline result
   */
  cacheOutline(outline: any[], titleOptions?: string[]): void {
    try {
      if (typeof window === 'undefined') return;

      localStorage.setItem(this.OUTLINE_CACHE_KEY, JSON.stringify(outline));
      if (titleOptions) {
        localStorage.setItem(this.TITLE_OPTIONS_CACHE_KEY, JSON.stringify(titleOptions));
      }
      console.log(`Cached outline (${outline.length} sections)`);
    } catch (error) {
      console.error('Error caching outline:', error);
    }
  }

  /**
   * Generate cache key for content based on outline section IDs
   */
  private generateContentCacheKey(outlineIds: string[]): string {
    const sortedIds = [...outlineIds].sort().join('|');
    return `${this.CONTENT_CACHE_PREFIX}${sortedIds}`;
  }

  /**
   * Get cached content for outline sections
   */
  getCachedContent(outlineIds: string[]): Record<string, string> | null {
    try {
      if (typeof window === 'undefined') return null;

      const cacheKey = this.generateContentCacheKey(outlineIds);
      const cachedContent = localStorage.getItem(cacheKey);

      if (!cachedContent) {
        return null;
      }

      const parsedSections = JSON.parse(cachedContent);
      if (!parsedSections || typeof parsedSections !== 'object' || Object.keys(parsedSections).length === 0) {
        return null;
      }

      // Verify that cached sections match outline structure
      const cachedIds = new Set(Object.keys(parsedSections));
      const outlineIdsSet = new Set(outlineIds.map(id => String(id)));
      const idsMatch = outlineIdsSet.size === cachedIds.size &&
                      Array.from(outlineIdsSet).every(id => cachedIds.has(id));

      if (!idsMatch) {
        console.log('Cached content does not match outline structure');
        return null;
      }

      console.log(`Cache hit for content (${Object.keys(parsedSections).length} sections)`);
      return parsedSections;
    } catch (error) {
      console.error('Error retrieving cached content:', error);
      return null;
    }
  }

  /**
   * Cache content sections
   */
  cacheContent(sections: Record<string, string>, outlineIds: string[]): void {
    try {
      if (typeof window === 'undefined') return;
      if (!sections || Object.keys(sections).length === 0) return;

      const cacheKey = this.generateContentCacheKey(outlineIds);
      localStorage.setItem(cacheKey, JSON.stringify(sections));
      console.log(`Cached content (${Object.keys(sections).length} sections)`);
    } catch (error) {
      console.error('Error caching content:', error);
    }
  }

  /**
   * Check if content exists in state (helper for manual flow)
   */
  contentExistsInState(sections: Record<string, string>, outlineIds: string[]): boolean {
    if (!sections || Object.keys(sections).length === 0) {
      return false;
    }

    const existingIds = new Set(Object.keys(sections));
    const outlineIdsSet = new Set(outlineIds.map(id => String(id)));
    return outlineIdsSet.size === existingIds.size &&
           Array.from(outlineIdsSet).every(id => existingIds.has(id));
  }
}

// Export singleton instance
export const blogWriterCache = new BlogWriterCacheService();
export default blogWriterCache;

