import { renderHook, act, waitFor } from '@testing-library/react';
import { useBlogWriterResearchPolling } from '../../../hooks/usePolling';
import { blogWriterApi } from '../../../services/blogWriterApi';

jest.mock('../../../services/blogWriterApi', () => ({
  blogWriterApi: {
    pollResearchStatus: jest.fn()
  }
}));

jest.mock('../../../api/client', () => ({
  triggerSubscriptionError: jest.fn().mockResolvedValue(true)
}));

describe('Polling Integration', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('polls until completion and calls completion callbacks with final result', async () => {
    const mockPollStatus = blogWriterApi.pollResearchStatus as jest.Mock;
    const onProgress = jest.fn();
    const onComplete = jest.fn();

    const completedResult = {
      success: true,
      sources: [],
      keyword_analysis: {},
      competitor_analysis: {},
      suggested_angles: []
    };

    mockPollStatus
      .mockResolvedValueOnce({
        task_id: 'test-task-123',
        status: 'running',
        progress_messages: [
          { timestamp: '2024-01-01T10:00:00Z', message: 'Starting research...' }
        ]
      })
      .mockResolvedValueOnce({
        task_id: 'test-task-123',
        status: 'completed',
        progress_messages: [
          { timestamp: '2024-01-01T10:00:05Z', message: 'Research complete' }
        ],
        result: completedResult
      });

    const { result } = renderHook(() =>
      useBlogWriterResearchPolling({
        interval: 100,
        onProgress,
        onComplete
      })
    );

    act(() => {
      result.current.startPolling('test-task-123');
    });

    await waitFor(() => {
      expect(mockPollStatus).toHaveBeenCalledTimes(1);
    });

    expect(mockPollStatus).toHaveBeenNthCalledWith(1, 'test-task-123');

    act(() => {
      jest.advanceTimersByTime(110);
    });

    await waitFor(() => {
      expect(mockPollStatus).toHaveBeenCalledTimes(2);
    });

    expect(mockPollStatus).toHaveBeenNthCalledWith(2, 'test-task-123');

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalledWith(completedResult);
    });

    expect(onProgress).toHaveBeenCalledWith('Starting research...');
    expect(onProgress).toHaveBeenCalledWith('Research complete');
    expect(result.current.currentStatus).toBe('completed');
    expect(result.current.isPolling).toBe(false);
    expect(result.current.result).toEqual(completedResult);
  });

  it('stops polling and reports error for task-not-found failures', async () => {
    const mockPollStatus = blogWriterApi.pollResearchStatus as jest.Mock;
    const onError = jest.fn();

    mockPollStatus.mockRejectedValue(new Error('404 Task not found'));

    const { result } = renderHook(() =>
      useBlogWriterResearchPolling({
        interval: 100,
        onError
      })
    );

    act(() => {
      result.current.startPolling('missing-task-123');
    });

    await waitFor(() => {
      expect(mockPollStatus).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith('Task not found - it may have expired or been cleaned up');
    });

    expect(result.current.error).toBe('Task not found - it may have expired or been cleaned up');
    expect(result.current.isPolling).toBe(false);
  });
});
