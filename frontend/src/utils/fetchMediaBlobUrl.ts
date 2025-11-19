import { aiApiClient } from "../api/client";

export async function fetchMediaBlobUrl(pathOrUrl: string): Promise<string | null> {
  try {
    const rel = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
    const res = await aiApiClient.get(rel, { responseType: "blob" });
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


