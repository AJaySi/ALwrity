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
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  async suggest(text: string): Promise<WASuggestion[]> {
    const resp = await fetch(`${this.baseUrl}/api/writing-assistant/suggest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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


