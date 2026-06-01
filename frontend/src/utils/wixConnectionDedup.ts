const DEDUP_KEY = 'wix_oauth_handled';
const DEDUP_TTL_MS = 5000;

let _moduleLevelHandled = false;

export function markConnectionHandled(): void {
  _moduleLevelHandled = true;
  try {
    sessionStorage.setItem(DEDUP_KEY, Date.now().toString());
  } catch {}
}

export function isAlreadyHandled(): boolean {
  if (_moduleLevelHandled) return true;
  try {
    const ts = sessionStorage.getItem(DEDUP_KEY);
    if (ts) {
      const elapsed = Date.now() - parseInt(ts, 10);
      if (elapsed < DEDUP_TTL_MS) return true;
      sessionStorage.removeItem(DEDUP_KEY);
    }
  } catch {}
  return false;
}

export function clearConnectionHandled(): void {
  _moduleLevelHandled = false;
  try {
    sessionStorage.removeItem(DEDUP_KEY);
  } catch {}
}