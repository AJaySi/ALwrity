export async function hashContent(text: string): Promise<string> {
  try {
    const enc = new TextEncoder().encode(text);
    const digest = await crypto.subtle.digest('SHA-256', enc);
    const bytes = Array.from(new Uint8Array(digest));
    return bytes.map(b => b.toString(16).padStart(2, '0')).join('');
  } catch {
    let h = 0;
    for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) | 0;
    return String(h);
  }
}

export function getSeoCacheKey(contentHash: string, title?: string): string {
  return `seo_cache:${contentHash}:${title || ''}`;
}
