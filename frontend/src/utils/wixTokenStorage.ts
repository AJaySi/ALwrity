const STORAGE_PREFIX = 'wix_ek_';
const IV_LENGTH = 12;
const SALT_LENGTH = 16;

async function _deriveKey(): Promise<CryptoKey> {
  const raw = process.env.REACT_APP_WIX_CLIENT_ID || 'alwrity-wix-encryption-key';
  const encoded = new TextEncoder().encode(raw);
  const salt = new TextEncoder().encode('wix-token-encryption-salt-v1');
  const baseKey = await crypto.subtle.importKey('raw', encoded, { name: 'PBKDF2' }, false, ['deriveKey']);
  return crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    baseKey,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt'],
  );
}

let _keyPromise: Promise<CryptoKey> | null = null;
function getKey(): Promise<CryptoKey> {
  if (!_keyPromise) _keyPromise = _deriveKey();
  return _keyPromise;
}

export async function encryptToken(plaintext: string): Promise<string> {
  const key = await getKey();
  const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));
  const encoded = new TextEncoder().encode(plaintext);
  const cipherBuf = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, encoded);
  const cipher = new Uint8Array(cipherBuf);
  const combined = new Uint8Array(IV_LENGTH + cipher.length);
  combined.set(iv, 0);
  combined.set(cipher, IV_LENGTH);
  return btoa(String.fromCharCode(...combined));
}

export async function decryptToken(stored: string): Promise<string> {
  const key = await getKey();
  const raw = Uint8Array.from(atob(stored), c => c.charCodeAt(0));
  const iv = raw.slice(0, IV_LENGTH);
  const cipher = raw.slice(IV_LENGTH);
  const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, cipher);
  return new TextDecoder().decode(decrypted);
}

export async function storeEncrypted(key: string, value: string): Promise<void> {
  try {
    const encrypted = await encryptToken(value);
    localStorage.setItem(`${STORAGE_PREFIX}${key}`, encrypted);
  } catch {
    localStorage.setItem(key, value);
  }
}

export function storeEncryptedSync(key: string, value: string): void {
  const combined = btoa(value);
  localStorage.setItem(`${STORAGE_PREFIX}${key}`, combined);
}

export async function readEncrypted(key: string): Promise<string | null> {
  const prefixedKey = `${STORAGE_PREFIX}${key}`;
  const prefixed = localStorage.getItem(prefixedKey);
  if (prefixed) {
    try {
      return await decryptToken(prefixed);
    } catch {
      try { return atob(prefixed); } catch { return prefixed; }
    }
  }
  const legacy = localStorage.getItem(key);
  if (legacy) {
    try {
      await storeEncrypted(key, legacy);
      localStorage.removeItem(key);
    } catch {}
    return legacy;
  }
  return null;
}

export function isSecureStorageAvailable(): boolean {
  return typeof crypto !== 'undefined' && typeof crypto.subtle !== 'undefined';
}