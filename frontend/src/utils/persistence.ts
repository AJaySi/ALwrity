/**
 * Shared persistence utilities.
 *
 * Provides generic localStorage read/write helpers used by BlogWriter,
 * StoryWriter, and other feature modules for synchronous state
 * serialization and deserialization.
 */

export function readLS<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function readLSString(key: string, fallback: string): string {
  try {
    const raw = localStorage.getItem(key);
    return raw !== null ? raw : fallback;
  } catch {
    return fallback;
  }
}

export function readLSBool(key: string, fallback: boolean): boolean {
  try {
    const raw = localStorage.getItem(key);
    return raw !== null ? raw === 'true' : fallback;
  } catch {
    return fallback;
  }
}

export function writeLS<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch { /* noop */ }
}

export function writeLSString(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch { /* noop */ }
}

export function writeLSBool(key: string, value: boolean): void {
  try {
    localStorage.setItem(key, String(value));
  } catch { /* noop */ }
}

export function removeLS(key: string): void {
  try {
    localStorage.removeItem(key);
  } catch { /* noop */ }
}

/**
 * Persist any value to localStorage each time it changes.
 * Returns a cleanup function that removes the key.
 */
export function persistToLS<T>(key: string, value: T): () => void {
  writeLS(key, value);
  return () => removeLS(key);
}
