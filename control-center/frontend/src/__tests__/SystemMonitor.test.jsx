/**
 * Tests for SystemMonitor component
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SystemMonitor from '../components/SystemMonitor';
import * as api from '../services/api';

jest.mock('../services/api');

describe('SystemMonitor Component', () => {
  const mockSystemStats = {
    cpu: 45.2,
    memory: 62.3,
    disk: 78.5,
    uptime: 86400,
    timestamp: '2025-11-07T12:00:00'
  };

  const mockProcesses = [
    { pid: 1234, name: 'python.exe', cpu: 2.5, memory: 150 },
    { pid: 5678, name: 'comfyui.exe', cpu: 15.2, memory: 1024 }
  ];

  const mockPorts = {
    '8188': { service: 'ComfyUI', status: 'open' },
    '5000': { service: 'Knowledge Base', status: 'closed' }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    api.getSystemStats = jest.fn().mockResolvedValue(mockSystemStats);
    api.getProcesses = jest.fn().mockResolvedValue(mockProcesses);
    api.scanPorts = jest.fn().mockResolvedValue(mockPorts);
  });

  test('renders system monitor component', () => {
    render(<SystemMonitor />);

    expect(screen.getByTestId('system-monitor')).toBeInTheDocument();
  });

  test('displays CPU usage', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/cpu/i)).toBeInTheDocument();
      expect(screen.getByText(/45.2/)).toBeInTheDocument();
    });
  });

  test('displays memory usage', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/memory/i)).toBeInTheDocument();
      expect(screen.getByText(/62.3/)).toBeInTheDocument();
    });
  });

  test('displays disk usage', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/disk/i)).toBeInTheDocument();
      expect(screen.getByText(/78.5/)).toBeInTheDocument();
    });
  });

  test('displays process list', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/python.exe/i)).toBeInTheDocument();
      expect(screen.getByText(/comfyui.exe/i)).toBeInTheDocument();
    });
  });

  test('sorts processes by CPU usage', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/comfyui.exe/i)).toBeInTheDocument();
    });

    const cpuHeader = screen.getByText(/cpu/i);
    fireEvent.click(cpuHeader);

    // Processes should be sorted by CPU
    const processes = screen.getAllByTestId('process-row');
    expect(processes[0]).toHaveTextContent(/comfyui.exe/i); // Higher CPU first
  });

  test('sorts processes by memory usage', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/python.exe/i)).toBeInTheDocument();
    });

    const memoryHeader = screen.getByText(/memory/i);
    fireEvent.click(memoryHeader);

    // Processes should be sorted by memory
    const processes = screen.getAllByTestId('process-row');
    expect(processes[0]).toHaveTextContent(/comfyui.exe/i); // Higher memory first
  });

  test('displays port scan results', async () => {
    render(<SystemMonitor />);

    // Trigger port scan
    const scanButton = screen.getByRole('button', { name: /scan ports/i });
    fireEvent.click(scanButton);

    await waitFor(() => {
      expect(screen.getByText(/8188/)).toBeInTheDocument();
      expect(screen.getByText(/comfyui/i)).toBeInTheDocument();
      expect(screen.getByText(/open/i)).toBeInTheDocument();
    });
  });

  test('updates stats in real-time', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/45.2/)).toBeInTheDocument();
    });

    // Simulate real-time update
    const updatedStats = { ...mockSystemStats, cpu: 52.8 };
    api.getSystemStats = jest.fn().mockResolvedValue(updatedStats);

    // Wait for auto-refresh or trigger manual refresh
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(screen.getByText(/52.8/)).toBeInTheDocument();
    });
  });

  test('displays uptime formatted correctly', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      // 86400 seconds = 1 day
      expect(screen.getByText(/1 day/i) || screen.getByText(/24 hours/i)).toBeInTheDocument();
    });
  });

  test('handles error when fetching stats', async () => {
    api.getSystemStats = jest.fn().mockRejectedValue(new Error('Failed to fetch stats'));

    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/error/i) || screen.getByText(/failed/i)).toBeInTheDocument();
    });
  });

  test('filters processes by name', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/python.exe/i)).toBeInTheDocument();
    });

    const filterInput = screen.getByPlaceholderText(/filter/i) ||
                       screen.getByRole('textbox', { name: /search/i });
    fireEvent.change(filterInput, { target: { value: 'comfyui' } });

    // Should only show matching processes
    expect(screen.getByText(/comfyui.exe/i)).toBeInTheDocument();
    expect(screen.queryByText(/python.exe/i)).not.toBeInTheDocument();
  });

  test('displays network statistics', async () => {
    const mockNetwork = {
      bytes_sent: 1024000,
      bytes_recv: 2048000,
      packets_sent: 500,
      packets_recv: 1200
    };

    api.getNetworkStats = jest.fn().mockResolvedValue(mockNetwork);

    render(<SystemMonitor />);

    await waitFor(() => {
      expect(screen.getByText(/network/i)).toBeInTheDocument();
      expect(screen.getByText(/1024000/)).toBeInTheDocument();
    });
  });

  test('shows loading state while fetching data', () => {
    api.getSystemStats = jest.fn().mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockSystemStats), 1000))
    );

    render(<SystemMonitor />);

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('displays system uptime formatted', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      // Should format 86400 seconds nicely
      const uptimeElement = screen.getByTestId('uptime-display');
      expect(uptimeElement).toBeInTheDocument();
    });
  });

  test('visualizes CPU usage with chart', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      const chart = screen.getByTestId('cpu-chart') ||
                   screen.getByRole('img', { name: /cpu chart/i });
      expect(chart).toBeInTheDocument();
    });
  });

  test('visualizes memory usage with chart', async () => {
    render(<SystemMonitor />);

    await waitFor(() => {
      const chart = screen.getByTestId('memory-chart') ||
                   screen.getByRole('img', { name: /memory chart/i });
      expect(chart).toBeInTheDocument();
    });
  });

  test('highlights high resource usage', async () => {
    const highUsageStats = { ...mockSystemStats, cpu: 95.0 };
    api.getSystemStats = jest.fn().mockResolvedValue(highUsageStats);

    render(<SystemMonitor />);

    await waitFor(() => {
      const cpuElement = screen.getByText(/95.0/);
      // Should have warning/danger class
      expect(cpuElement.className).toMatch(/warning|danger|high/i);
    });
  });
});
