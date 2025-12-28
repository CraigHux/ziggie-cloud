/**
 * Tests for WebSocket hooks and functionality
 */
import { renderHook, act, waitFor } from '@testing-library/react';
import useWebSocket from '../hooks/useWebSocket';

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    this.onopen = null;
    this.onclose = null;
    this.onerror = null;
    this.onmessage = null;

    // Simulate connection
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) this.onopen(new Event('open'));
    }, 0);
  }

  send(data) {
    if (this.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) this.onclose(new CloseEvent('close'));
  }
}

global.WebSocket = MockWebSocket;

describe('WebSocket Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('establishes WebSocket connection', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });
  });

  test('handles connection errors', async () => {
    const errorUrl = 'ws://invalid-url';
    const { result } = renderHook(() => useWebSocket(errorUrl));

    // Simulate error
    act(() => {
      if (result.current.socket && result.current.socket.onerror) {
        result.current.socket.onerror(new Event('error'));
      }
    });

    expect(result.current.error).toBeDefined();
  });

  test('receives messages from WebSocket', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    const testMessage = { type: 'system_stats', data: { cpu: 45.2 } };

    act(() => {
      if (result.current.socket && result.current.socket.onmessage) {
        result.current.socket.onmessage(
          new MessageEvent('message', { data: JSON.stringify(testMessage) })
        );
      }
    });

    await waitFor(() => {
      expect(result.current.lastMessage).toEqual(testMessage);
    });
  });

  test('sends messages through WebSocket', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    const sendSpy = jest.spyOn(result.current.socket, 'send');

    const message = { type: 'subscribe', channel: 'system_stats' };

    act(() => {
      result.current.sendMessage(message);
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify(message));
  });

  test('reconnects on connection loss', async () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { reconnect: true })
    );

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    // Simulate connection loss
    act(() => {
      result.current.socket.close();
    });

    await waitFor(() => {
      expect(result.current.isConnected).toBe(false);
    });

    // Should attempt reconnection
    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    }, { timeout: 3000 });
  });

  test('cleans up on unmount', async () => {
    const { result, unmount } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    const closeSpy = jest.spyOn(result.current.socket, 'close');

    unmount();

    expect(closeSpy).toHaveBeenCalled();
  });

  test('handles subscription to channels', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    act(() => {
      result.current.subscribe('system_stats');
    });

    const sendSpy = jest.spyOn(result.current.socket, 'send');

    expect(sendSpy).toHaveBeenCalledWith(
      JSON.stringify({ type: 'subscribe', channel: 'system_stats' })
    );
  });

  test('handles unsubscription from channels', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    act(() => {
      result.current.unsubscribe('system_stats');
    });

    const sendSpy = jest.spyOn(result.current.socket, 'send');

    expect(sendSpy).toHaveBeenCalledWith(
      JSON.stringify({ type: 'unsubscribe', channel: 'system_stats' })
    );
  });

  test('queues messages when disconnected', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    // Try to send message before connection
    const message = { type: 'test', data: 'hello' };

    act(() => {
      result.current.sendMessage(message);
    });

    // Wait for connection
    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    // Queued message should be sent after connection
    const sendSpy = jest.spyOn(result.current.socket, 'send');
    expect(sendSpy).toHaveBeenCalled();
  });

  test('tracks connection state changes', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    expect(result.current.readyState).toBe(WebSocket.CONNECTING);

    await waitFor(() => {
      expect(result.current.readyState).toBe(WebSocket.OPEN);
    });

    act(() => {
      result.current.socket.close();
    });

    await waitFor(() => {
      expect(result.current.readyState).toBe(WebSocket.CLOSED);
    });
  });

  test('handles ping/pong keepalive', async () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { heartbeat: true })
    );

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    // Simulate receiving ping
    act(() => {
      if (result.current.socket && result.current.socket.onmessage) {
        result.current.socket.onmessage(
          new MessageEvent('message', { data: JSON.stringify({ type: 'ping' }) })
        );
      }
    });

    // Should respond with pong
    const sendSpy = jest.spyOn(result.current.socket, 'send');
    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({ type: 'pong' }));
  });

  test('handles multiple simultaneous subscriptions', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    const channels = ['system_stats', 'services', 'agents'];

    act(() => {
      channels.forEach(channel => result.current.subscribe(channel));
    });

    expect(result.current.subscriptions).toEqual(expect.arrayContaining(channels));
  });

  test('filters messages by channel', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws'));

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    const messages = [
      { type: 'system_stats', channel: 'system_stats', data: { cpu: 45 } },
      { type: 'service_update', channel: 'services', data: { status: 'running' } }
    ];

    act(() => {
      messages.forEach(msg => {
        if (result.current.socket && result.current.socket.onmessage) {
          result.current.socket.onmessage(
            new MessageEvent('message', { data: JSON.stringify(msg) })
          );
        }
      });
    });

    const systemStatsMessages = result.current.getMessagesByChannel('system_stats');
    expect(systemStatsMessages).toHaveLength(1);
    expect(systemStatsMessages[0].channel).toBe('system_stats');
  });
});
