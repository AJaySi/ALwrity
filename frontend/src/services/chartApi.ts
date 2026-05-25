import { aiApiClient, getAuthTokenGetter } from '../api/client';
import { getApiBaseUrl } from '../utils/apiUrl';

export interface ChartGenerateRequest {
  chart_data?: Record<string, any>;
  chart_type?: string;
  title?: string;
  subtitle?: string;
  text?: string;
  section_heading?: string;
  section_key_points?: string[];
}

export interface ChartGenerateResponse {
  preview_url: string;
  chart_id: string;
  chart_type?: string;
  chart_data?: Record<string, any>;
  title?: string;
  warnings?: string[];
}

class ChartApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = getApiBaseUrl();
  }

  async generateChartExplicit(params: {
    chart_data: Record<string, any>;
    chart_type: string;
    title?: string;
    subtitle?: string;
  }): Promise<ChartGenerateResponse> {
    const { data } = await aiApiClient.post('/api/charts/generate', {
      chart_data: params.chart_data,
      chart_type: params.chart_type,
      title: params.title || '',
      subtitle: params.subtitle || '',
    });
    return data;
  }

  async generateChartFromText(text: string, title?: string, section_heading?: string, section_key_points?: string[]): Promise<ChartGenerateResponse> {
    const { data } = await aiApiClient.post('/api/charts/generate', {
      text,
      title: title || '',
      section_heading,
      section_key_points,
    });
    return data;
  }

  /**
   * Build the full preview URL for a chart image.
   * Appends auth token as query param so browser <img> tags can load it.
   */
  async getPreviewUrl(previewUrl: string): Promise<string> {
    if (!previewUrl) return '';
    const fullUrl = previewUrl.startsWith('http') ? previewUrl : `${this.baseUrl}${previewUrl}`;
    const tokenGetter = getAuthTokenGetter();
    if (!tokenGetter) return fullUrl;
    try {
      const token = await tokenGetter();
      if (token) {
        const separator = fullUrl.includes('?') ? '&' : '?';
        return `${fullUrl}${separator}token=${encodeURIComponent(token)}`;
      }
    } catch {}
    return fullUrl;
  }
}

export const chartApi = new ChartApiService();
export default chartApi;