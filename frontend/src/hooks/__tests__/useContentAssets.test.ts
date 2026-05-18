import { renderHook, waitFor } from '@testing-library/react';
import { useContentAssets } from '../useContentAssets';

const getTokenMock = jest.fn();

jest.mock('@clerk/clerk-react', () => ({
  useAuth: () => ({ getToken: getTokenMock }),
}));

describe('useContentAssets', () => {
  beforeEach(() => {
    getTokenMock.mockResolvedValue('test-token');
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ assets: [], total: 0, limit: 100, offset: 0 }),
    } as Response);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('sends all source_module values as repeated query params', async () => {
    renderHook(() =>
      useContentAssets({ source_module: ['blog_writer', 'youtube'], limit: 50, offset: 0 })
    );

    await waitFor(() => expect(global.fetch).toHaveBeenCalled());

    const calledUrl = (global.fetch as jest.Mock).mock.calls[0][0] as string;
    const params = new URL(calledUrl).searchParams;

    expect(params.getAll('source_module')).toEqual(['blog_writer', 'youtube']);
  });
});
