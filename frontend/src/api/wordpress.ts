/**
 * WordPress API client for ALwrity frontend.
 * Handles WordPress site connections, content publishing, and management.
 */

import { apiClient } from './client';

export interface WordPressSite {
  id: number;
  site_url: string;
  site_name: string;
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WordPressSiteRequest {
  site_url: string;
  site_name: string;
  username: string;
  app_password: string;
}

export interface WordPressPublishRequest {
  site_id: number;
  title: string;
  content: string;
  excerpt?: string;
  featured_image_path?: string;
  categories?: string[];
  tags?: string[];
  status?: 'draft' | 'publish' | 'private';
  meta_description?: string;
}

export interface WordPressPublishResponse {
  success: boolean;
  post_id?: number;
  post_url?: string;
  error?: string;
}

export interface WordPressPost {
  id: number;
  wp_post_id: number;
  title: string;
  status: string;
  published_at?: string;
  created_at: string;
  site_name: string;
  site_url: string;
}

export interface WordPressStatusResponse {
  connected: boolean;
  sites?: WordPressSite[];
  total_sites: number;
}

export interface WordPressHealthResponse {
  status: string;
  service: string;
  timestamp: string;
  version: string;
}

class WordPressAPI {
  private baseUrl = '/api/wordpress';
  private getAuthToken: (() => Promise<string | null>) | null = null;

  /**
   * Set authentication token getter
   */
  setAuthTokenGetter(getter: () => Promise<string | null>) {
    this.getAuthToken = getter;
  }

  /**
   * Get authenticated client with token
   */
  private async getAuthenticatedClient() {
    if (this.getAuthToken) {
      const token = await this.getAuthToken();
      if (token) {
        // Create a new client instance with the auth header
        return apiClient.create({
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      }
    }
    return apiClient;
  }

  /**
   * Get WordPress connection status
   */
  async getStatus(): Promise<WordPressStatusResponse> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/status`);
      return response.data;
    } catch (error: any) {
      // Handle 404 gracefully - endpoint may not exist yet
      if (error?.response?.status === 404) {
        // Return empty status instead of throwing
        return {
          connected: false,
          sites: [],
          total_sites: 0
        };
      }
      // Only log non-404 errors
      console.error('WordPress API: Error getting status:', error);
      throw error;
    }
  }

  /**
   * Add a new WordPress site connection
   */
  async addSite(siteData: WordPressSiteRequest): Promise<WordPressSite> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.post(`${this.baseUrl}/sites`, siteData);
      return response.data;
    } catch (error) {
      console.error('WordPress API: Error adding site:', error);
      throw error;
    }
  }

  /**
   * Get all WordPress sites for the current user
   */
  async getSites(): Promise<WordPressSite[]> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/sites`);
      return response.data;
    } catch (error) {
      console.error('WordPress API: Error getting sites:', error);
      throw error;
    }
  }

  /**
   * Disconnect a WordPress site
   */
  async disconnectSite(siteId: number): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.delete(`${this.baseUrl}/sites/${siteId}`);
      return response.data;
    } catch (error) {
      console.error('WordPress API: Error disconnecting site:', error);
      throw error;
    }
  }

  /**
   * Publish content to WordPress
   */
  async publishContent(publishData: WordPressPublishRequest): Promise<WordPressPublishResponse> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.post(`${this.baseUrl}/publish`, publishData);
      return response.data;
    } catch (error) {
      console.error('WordPress API: Error publishing content:', error);
      throw error;
    }
  }

  /**
   * Get published posts from WordPress sites
   */
  async getPosts(siteId?: number): Promise<WordPressPost[]> {
    try {
      const client = await this.getAuthenticatedClient();
      const params = siteId ? { site_id: siteId } : {};
      const response = await client.get(`${this.baseUrl}/posts`, { params });
      return response.data;
    } catch (error) {
      console.error('WordPress API: Error getting posts:', error);
      throw error;
    }
  }

  /**
   * Update post status (draft/publish/private)
   */
  async updatePostStatus(postId: number, status: string): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.put(`${this.baseUrl}/posts/${postId}/status`, null, {
        params: { status }
      });
      return response.data;
    } catch (error) {
      console.error('WordPress API: Error updating post status:', error);
      throw error;
    }
  }

  /**
   * Delete a WordPress post
   */
  async deletePost(postId: number, force: boolean = false): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.delete(`${this.baseUrl}/posts/${postId}`, {
        params: { force }
      });
      return response.data;
    } catch (error) {
      console.error('WordPress API: Error deleting post:', error);
      throw error;
    }
  }

  /**
   * Test WordPress site connection
   */
  async testConnection(siteData: WordPressSiteRequest): Promise<boolean> {
    try {
      // This would typically be a separate endpoint for testing connections
      // For now, we'll try to add the site and see if it succeeds
      await this.addSite(siteData);
      return true;
    } catch (error) {
      console.error('WordPress API: Connection test failed:', error);
      return false;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<WordPressHealthResponse> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('WordPress API: Health check failed:', error);
      throw error;
    }
  }

  /**
   * Validate WordPress site URL
   */
  validateSiteUrl(url: string): boolean {
    try {
      // Remove protocol if present
      const cleanUrl = url.replace(/^https?:\/\//, '');
      
      // Basic URL validation
      const urlPattern = /^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})$/;
      
      return urlPattern.test(cleanUrl) || cleanUrl.includes('localhost') || cleanUrl.includes('127.0.0.1');
    } catch (error) {
      return false;
    }
  }

  /**
   * Format WordPress site URL
   */
  formatSiteUrl(url: string): string {
    if (!url) return '';
    
    // Add protocol if missing
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      return `https://${url}`;
    }
    
    return url;
  }
}

// Export singleton instance
export const wordpressAPI = new WordPressAPI();
export default wordpressAPI;
