export const WIX_CLIENT_ID = process.env.REACT_APP_WIX_CLIENT_ID || '';

export const WIX_NGROK_ORIGIN = process.env.REACT_APP_NGROK_ORIGIN || '';

export function getWixRedirectOrigin(): string {
  if (typeof window === 'undefined') return WIX_NGROK_ORIGIN;
  return window.location.origin.includes('localhost') && WIX_NGROK_ORIGIN
    ? WIX_NGROK_ORIGIN
    : window.location.origin;
}

export function getWixTrustedOrigins(): string[] {
  if (typeof window === 'undefined') return WIX_NGROK_ORIGIN ? [WIX_NGROK_ORIGIN] : [];
  const origins = [window.location.origin];
  if (WIX_NGROK_ORIGIN) origins.push(WIX_NGROK_ORIGIN);
  return origins;
}