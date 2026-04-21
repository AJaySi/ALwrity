const isDev = process.env.NODE_ENV === 'development';

export const devLog = {
  log: (...args: any[]) => { if (isDev) console.log(...args); },
  warn: (...args: any[]) => { if (isDev) console.warn(...args); },
  error: (...args: any[]) => { console.error(...args); },
  info: (...args: any[]) => { if (isDev) console.info(...args); },
};

export const sanitizeUrl = (url: string): string => {
  try {
    const parsed = new URL(url, window.location.origin);
    if (parsed.searchParams.has('token')) {
      parsed.searchParams.set('token', '***');
    }
    return parsed.pathname + (parsed.search ? parsed.search : '');
  } catch {
    return url.split('?')[0];
  }
};