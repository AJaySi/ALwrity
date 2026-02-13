import { renderHook, act, waitFor } from '@testing-library/react';
import { useBingOAuth } from '../useBingOAuth';
import { bingOAuthAPI } from '../../api/bingOAuth';

jest.mock('../../api/bingOAuth', () => ({
  bingOAuthAPI: {
    getAuthUrl: jest.fn(),
    getStatus: jest.fn(),
    disconnectSite: jest.fn(),
  },
}));

describe('useBingOAuth postMessage trust checks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
    jest.spyOn(window, 'setInterval').mockImplementation(((handler: TimerHandler) => {
      if (typeof handler === 'function') {
        handler();
      }
      return 1;
    }) as typeof window.setInterval);
    jest.spyOn(window, 'clearInterval').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('rejects success messages from untrusted origins', async () => {
    const popup = { close: jest.fn(), closed: false } as unknown as Window;
    jest.spyOn(window, 'open').mockReturnValue(popup);

    (bingOAuthAPI.getAuthUrl as jest.Mock).mockResolvedValue({
      auth_url: 'https://bing.example/oauth',
      state: 'state-1',
      trusted_origins: ['https://trusted.example'],
    });
    (bingOAuthAPI.getStatus as jest.Mock).mockResolvedValue({
      connected: false,
      sites: [],
      total_sites: 0,
    });

    const { result } = renderHook(() => useBingOAuth());

    await act(async () => {
      await result.current.connect();
    });

    window.dispatchEvent(
      new MessageEvent('message', {
        origin: 'https://evil.example',
        source: popup,
        data: { type: 'BING_OAUTH_SUCCESS', success: true },
      })
    );

    await waitFor(() => {
      expect(popup.close).not.toHaveBeenCalled();
    });
  });

  it('accepts success messages from trusted origin + popup source', async () => {
    const popup = { close: jest.fn(), closed: false } as unknown as Window;
    jest.spyOn(window, 'open').mockReturnValue(popup);

    (bingOAuthAPI.getAuthUrl as jest.Mock).mockResolvedValue({
      auth_url: 'https://bing.example/oauth',
      state: 'state-1',
      trusted_origins: [window.location.origin],
    });
    (bingOAuthAPI.getStatus as jest.Mock).mockResolvedValue({
      connected: true,
      sites: [],
      total_sites: 0,
    });

    const { result } = renderHook(() => useBingOAuth());

    await act(async () => {
      await result.current.connect();
    });

    window.dispatchEvent(
      new MessageEvent('message', {
        origin: window.location.origin,
        source: popup,
        data: { type: 'BING_OAUTH_SUCCESS', success: true },
      })
    );

    await waitFor(() => {
      expect(popup.close).toHaveBeenCalled();
    });
  });
});
