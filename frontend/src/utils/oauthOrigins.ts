const OAUTH_TARGET_ORIGIN_STORAGE_PREFIX = 'oauth_postmessage_target_origin_';

export type OAuthProvider = 'gsc' | 'bing' | 'wordpress' | 'wix';

const toUniqueOrigins = (origins: string[]) => Array.from(new Set(origins.filter(Boolean)));

const getStorageKey = (provider: OAuthProvider): string => `${OAUTH_TARGET_ORIGIN_STORAGE_PREFIX}${provider}`;

export const setOAuthTargetOrigin = (provider: OAuthProvider, origin: string): void => {
  if (!origin) return;
  try {
    sessionStorage.setItem(getStorageKey(provider), origin);
  } catch {
    // Ignore storage failures in private mode or blocked storage contexts.
  }
};

export const getStoredOAuthTargetOrigin = (provider: OAuthProvider): string | null => {
  try {
    return sessionStorage.getItem(getStorageKey(provider));
  } catch {
    return null;
  }
};

export const clearOAuthTargetOrigin = (provider: OAuthProvider): void => {
  try {
    sessionStorage.removeItem(getStorageKey(provider));
  } catch {
    // Ignore storage failures.
  }
};

export const getTrustedOrigins = (provider: OAuthProvider, backendOrigins: string[] = []): string[] => {
  const storedOrigin = getStoredOAuthTargetOrigin(provider);
  return toUniqueOrigins([window.location.origin, ...backendOrigins, ...(storedOrigin ? [storedOrigin] : [])]);
};

export const getOAuthPostMessageTargetOrigin = (
  provider: OAuthProvider,
  backendOrigins: string[] = []
): string => {
  const trustedOrigins = getTrustedOrigins(provider, backendOrigins);
  const storedOrigin = getStoredOAuthTargetOrigin(provider);

  if (storedOrigin && trustedOrigins.includes(storedOrigin)) {
    return storedOrigin;
  }

  return window.location.origin;
};

export const isTrustedOAuthMessageEvent = (
  event: MessageEvent,
  expectedSource: Window | null,
  trustedOrigins: string[]
): boolean => {
  if (!event?.data || typeof event.data !== 'object') return false;
  if (!trustedOrigins.includes(event.origin)) return false;
  if (!expectedSource || event.source !== expectedSource) return false;
  return true;
};
