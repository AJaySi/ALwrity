import { aiApiClient } from "../api/client";

// Optional token getter - will be set by the app
let authTokenGetter: (() => Promise<string | null>) | null = null;

export const setMediaAuthTokenGetter = (getter: (() => Promise<string | null>) | null) => {
  authTokenGetter = getter;
};

export async function fetchMediaBlobUrl(pathOrUrl: string): Promise<string | null> {
  try {
    // If full URL (http/https), use as-is; otherwise ensure leading slash
    const isAbsolute = /^https?:\/\//i.test(pathOrUrl);
    const rel = isAbsolute ? pathOrUrl : pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
    
    // Try to get token and add as query parameter as fallback for endpoints that support it
    // This helps with endpoints that use get_current_user_with_query_token
    let url = rel;
    if (authTokenGetter) {
      try {
        const token = await authTokenGetter();
        if (token) {
          // Add token as query parameter for endpoints that support it
          const separator = url.includes('?') ? '&' : '?';
          url = `${url}${separator}token=${encodeURIComponent(token)}`;
        }
      } catch (tokenError) {
        console.warn(`[fetchMediaBlobUrl] Failed to get token for query param:`, tokenError);
      }
    }
    
    const res = await aiApiClient.get(url, { responseType: "blob" });
    return URL.createObjectURL(res.data);
  } catch (err: any) {
    // Gracefully handle 404s and other errors - file might not exist or was regenerated
    if (err?.response?.status === 404) {
      console.warn(`Media file not found (404): ${pathOrUrl}`);
      return null;
    }
    // Re-throw other errors
    throw err;
  }
}


