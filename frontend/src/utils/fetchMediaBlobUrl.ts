import { aiApiClient } from "../api/client";

export async function fetchMediaBlobUrl(pathOrUrl: string): Promise<string> {
  const rel = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
  const res = await aiApiClient.get(rel, { responseType: "blob" });
  return URL.createObjectURL(res.data);
}


