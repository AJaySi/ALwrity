// Lightweight app-wide event bus to react to API activity
// Components can subscribe to refresh billing/monitoring data without polling

export type ApiEventDetail = {
  url: string;
  method: string;
  source?: 'billing' | 'monitoring' | 'other';
};

const apiEventTarget = new EventTarget();

export const emitApiEvent = (detail: ApiEventDetail): void => {
  try {
    apiEventTarget.dispatchEvent(new CustomEvent<ApiEventDetail>('api:response', { detail }));
  } catch {
    // no-op
  }
};

export const onApiEvent = (
  handler: (detail: ApiEventDetail) => void
): (() => void) => {
  const listener = (event: Event) => {
    const custom = event as CustomEvent<ApiEventDetail>;
    handler(custom.detail);
  };
  apiEventTarget.addEventListener('api:response', listener);
  return () => apiEventTarget.removeEventListener('api:response', listener);
};


