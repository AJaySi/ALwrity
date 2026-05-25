import { getApiBaseUrl } from '../utils/apiUrl';

export interface WASource {
  title: string;
  url: string;
  text?: string;
  author?: string;
  published_date?: string;
  score: number;
}

export interface WASuggestion {
  text: string;
  confidence: number;
  sources: WASource[];
}

export interface WASuggestResponse {
  success: boolean;
  suggestions: WASuggestion[];
}

class WritingAssistantService {
  private baseUrl: string;
  private authTokenGetter: (() => Promise<string | null>) | null = null;
  constructor() {
    this.baseUrl = getApiBaseUrl();
  }

  setAuthTokenGetter(getter: (() => Promise<string | null>) | null) {
    this.authTokenGetter = getter;
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.authTokenGetter) {
      const token = await this.authTokenGetter();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return headers;
  }

  async suggest(text: string): Promise<WASuggestion[]> {
    const resp = await fetch(`${this.baseUrl}/api/writing-assistant/suggest`, {
      method: 'POST',
      headers: await this.getAuthHeaders(),
      body: JSON.stringify({ text, max_results: 1 })
    });
    if (!resp.ok) {
      const t = await resp.text();
      throw new Error(`WA HTTP ${resp.status}: ${t}`);
    }
    const data: WASuggestResponse = await resp.json();
    return data.suggestions || [];
  }
}

export const writingAssistantService = new WritingAssistantService();
export default writingAssistantService;


