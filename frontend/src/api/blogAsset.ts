import { apiClient } from './client';

export interface BlogAsset {
  id: number;
  title: string | null;
  description: string | null;
  tags: string[];
  phase: string;
  research_keywords: string | null;
  topic: string | null;
  selected_title: string | null;
  word_count_target: number | null;
  has_research: boolean;
  has_outline: boolean;
  has_content: boolean;
  has_seo: boolean;
  has_publish: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface BlogAssetFull extends BlogAsset {
  research_data?: any;
  outline_data?: any;
  content_data?: any;
  seo_data?: any;
  publish_data?: any;
}

export interface CreateAssetParams {
  research_keywords: string;
  topic?: string;
  word_count_target?: number;
}

export interface UpdateAssetParams {
  phase?: 'research' | 'outline' | 'content' | 'seo' | 'publish';
  topic?: string;
  selected_title?: string;
  word_count_target?: number;
  research_data?: any;
  outline_data?: any;
  content_data?: any;
  seo_data?: any;
  publish_data?: any;
}

class BlogAssetAPI {
  async create(params: CreateAssetParams): Promise<{ success: boolean; asset: BlogAsset; existing: boolean }> {
    const res = await apiClient.post('/api/blog/asset', params);
    return res.data;
  }

  async update(assetId: number, params: UpdateAssetParams): Promise<{ success: boolean; asset: BlogAsset }> {
    const res = await apiClient.put(`/api/blog/asset/${assetId}`, params);
    return res.data;
  }

  async get(assetId: number): Promise<{ success: boolean; asset: BlogAssetFull }> {
    const res = await apiClient.get(`/api/blog/asset/${assetId}`);
    return res.data;
  }
}

export const blogAssetAPI = new BlogAssetAPI();
