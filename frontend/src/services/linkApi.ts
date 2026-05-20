import { aiApiClient } from '../api/client';

export interface LinkSearchRequest {
  query: string;
  link_type: 'internal' | 'external';
  site_url?: string;
  num_results?: number;
}

export interface LinkSearchResult {
  title: string;
  url: string;
  text: string;
  publishedDate: string;
  author: string;
  score: number;
}

export interface LinkSearchResponse {
  results: LinkSearchResult[];
  warnings: string[];
}

export interface RewordRequest {
  section_text: string;
  selected_text?: string;
  section_heading?: string;
  links: Array<{ url: string; title: string }>;
}

export interface RewordResponse {
  reworded_text: string;
  warnings: string[];
}

class LinkApiService {
  private baseUrl: string;

  constructor() {
    const url = process.env.REACT_APP_API_URL;
    if (process.env.NODE_ENV === 'production' && !url) {
      throw new Error('REACT_APP_API_URL environment variable is required for production');
    }
    this.baseUrl = url || 'http://localhost:8000';
  }

  async searchLinks(params: LinkSearchRequest): Promise<LinkSearchResponse> {
    const { data } = await aiApiClient.post('/api/links/search', {
      query: params.query,
      link_type: params.link_type,
      site_url: params.site_url || '',
      num_results: params.num_results || 5,
    });
    return data;
  }

  async rewordWithLinks(params: RewordRequest): Promise<RewordResponse> {
    const { data } = await aiApiClient.post('/api/links/reword', {
      section_text: params.section_text,
      selected_text: params.selected_text,
      section_heading: params.section_heading,
      links: params.links,
    });
    return data;
  }
}

export const linkApi = new LinkApiService();
export default linkApi;