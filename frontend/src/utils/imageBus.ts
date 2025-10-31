type ImagePayload = { base64: string; provider?: string; model?: string };

const subscribers = new Set<(p: ImagePayload) => void>();

export function publishImage(payload: ImagePayload) {
  subscribers.forEach((cb) => {
    try { cb(payload); } catch {}
  });
}

export function subscribeImage(cb: (p: ImagePayload) => void) {
  subscribers.add(cb);
  return () => {
    subscribers.delete(cb);
  };
}


