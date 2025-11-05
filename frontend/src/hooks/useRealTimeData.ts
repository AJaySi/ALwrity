import { useState, useEffect, useCallback, useRef } from 'react';

interface RealTimeDataOptions {
  strategyId: number;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (data: any) => void;
}

interface RealTimeDataState {
  data: any;
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  reconnectAttempts: number;
}

export const useRealTimeData = (options: RealTimeDataOptions) => {
  const {
    strategyId,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
    onConnect,
    onDisconnect,
    onError,
    onMessage
  } = options;

  const [state, setState] = useState<RealTimeDataState>({
    data: null,
    isConnected: false,
    isConnecting: false,
    error: null,
    reconnectAttempts: 0
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      // Build WebSocket URL from environment variables
      // Consistent with API URL pattern - no hardcoded localhost
      const apiUrl = process.env.REACT_APP_API_URL || process.env.REACT_APP_BACKEND_URL || '';
      
      // In development, use proxy (empty string means use same origin)
      // In production, derive WebSocket URL from API URL
      let wsUrl: string;
      if (!apiUrl || apiUrl === '') {
        // Development: use proxy (same origin WebSocket)
        wsUrl = `ws://${window.location.host}/ws/strategy/${strategyId}/live`;
      } else {
        // Production: derive from API URL
        const wsProtocol = apiUrl.startsWith('https://') ? 'wss://' : 'ws://';
        const wsHost = apiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '');
        wsUrl = `${wsProtocol}${wsHost}/ws/strategy/${strategyId}/live`;
      }

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
          reconnectAttempts: 0
        }));
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setState(prev => ({ ...prev, data }));
          onMessage?.(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false
        }));
        onDisconnect?.();

        // Attempt to reconnect if not a clean close
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          setState(prev => ({ 
            ...prev, 
            reconnectAttempts: reconnectAttemptsRef.current 
          }));

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        setState(prev => ({
          ...prev,
          error: 'WebSocket connection error',
          isConnecting: false
        }));
        onError?.(error);
      };

    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to create WebSocket connection',
        isConnecting: false
      }));
    }
  }, [strategyId, reconnectInterval, maxReconnectAttempts, onConnect, onDisconnect, onError, onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000); // Clean close
      wsRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
      isConnecting: false,
      reconnectAttempts: 0
    }));
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Connect on mount and when strategyId changes
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage
  };
};

// Mock real-time data for development
export const useMockRealTimeData = (strategyId: number) => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      const mockData = {
        timestamp: new Date().toISOString(),
        strategyId,
        metrics: {
          traffic_growth: Math.random() * 20 + 5, // 5-25%
          engagement_rate: Math.random() * 10 + 5, // 5-15%
          conversion_rate: Math.random() * 3 + 1, // 1-4%
          content_quality_score: Math.random() * 20 + 80, // 80-100%
          strategy_adoption_rate: Math.random() * 20 + 80, // 80-100%
          roi_ratio: Math.random() * 2 + 2, // 2-4x
          competitive_position_rank: Math.floor(Math.random() * 5) + 1, // 1-5
          audience_growth_percentage: Math.random() * 15 + 8, // 8-23%
          confidence_score: Math.random() * 20 + 80 // 80-100%
        },
        alerts: Math.random() > 0.8 ? [
          {
            type: 'warning',
            message: 'Engagement rate dropped below target',
            timestamp: new Date().toISOString()
          }
        ] : [],
        trends: {
          daily: Array.from({ length: 7 }, (_, i) => ({
            date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            traffic_growth: Math.random() * 20 + 5,
            engagement_rate: Math.random() * 10 + 5,
            conversion_rate: Math.random() * 3 + 1,
            content_quality_score: Math.random() * 20 + 80
          }))
        }
      };

      setData(mockData);
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [strategyId]);

  return {
    data,
    isConnected: true,
    isConnecting: false,
    error: null,
    reconnectAttempts: 0,
    connect: () => {},
    disconnect: () => {},
    sendMessage: () => {}
  };
};

// Export both hooks
export default useRealTimeData;
