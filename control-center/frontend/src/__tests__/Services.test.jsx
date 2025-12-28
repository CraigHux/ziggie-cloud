/**
 * Tests for Services component
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Services from '../components/Services';
import * as api from '../services/api';

jest.mock('../services/api');

describe('Services Component', () => {
  const mockServices = {
    comfyui: {
      name: 'ComfyUI',
      status: 'running',
      pid: 12345,
      port: 8188,
      uptime: 3600
    },
    'knowledge-base': {
      name: 'Knowledge Base',
      status: 'stopped',
      pid: null,
      port: 5000,
      uptime: 0
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    api.getServices = jest.fn().mockResolvedValue(mockServices);
  });

  test('renders services list', async () => {
    render(<Services />);

    await waitFor(() => {
      expect(screen.getByText(/comfyui/i)).toBeInTheDocument();
      expect(screen.getByText(/knowledge base/i)).toBeInTheDocument();
    });
  });

  test('displays service status correctly', async () => {
    render(<Services />);

    await waitFor(() => {
      expect(screen.getByText(/running/i)).toBeInTheDocument();
      expect(screen.getByText(/stopped/i)).toBeInTheDocument();
    });
  });

  test('starts a stopped service', async () => {
    api.startService = jest.fn().mockResolvedValue({
      success: true,
      message: 'Service started',
      pid: 12346
    });

    render(<Services />);

    await waitFor(() => {
      expect(screen.getByText(/knowledge base/i)).toBeInTheDocument();
    });

    // Click start button for stopped service
    const startButton = screen.getAllByRole('button', { name: /start/i })[0];
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(api.startService).toHaveBeenCalledWith('knowledge-base');
    });
  });

  test('stops a running service', async () => {
    api.stopService = jest.fn().mockResolvedValue({
      success: true,
      message: 'Service stopped'
    });

    render(<Services />);

    await waitFor(() => {
      expect(screen.getByText(/comfyui/i)).toBeInTheDocument();
    });

    // Click stop button for running service
    const stopButton = screen.getAllByRole('button', { name: /stop/i })[0];
    fireEvent.click(stopButton);

    await waitFor(() => {
      expect(api.stopService).toHaveBeenCalledWith('comfyui');
    });
  });

  test('restarts a service', async () => {
    api.restartService = jest.fn().mockResolvedValue({
      success: true,
      message: 'Service restarted',
      pid: 12347
    });

    render(<Services />);

    await waitFor(() => {
      expect(screen.getByText(/comfyui/i)).toBeInTheDocument();
    });

    // Click restart button
    const restartButton = screen.getAllByRole('button', { name: /restart/i })[0];
    fireEvent.click(restartButton);

    await waitFor(() => {
      expect(api.restartService).toHaveBeenCalledWith('comfyui');
    });
  });

  test('shows loading state during service operation', async () => {
    api.startService = jest.fn().mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 1000))
    );

    render(<Services />);

    await waitFor(() => {
      const startButton = screen.getAllByRole('button', { name: /start/i })[0];
      fireEvent.click(startButton);
    });

    // Button should be disabled or show loading state
    const startButton = screen.getAllByRole('button', { name: /start/i })[0];
    expect(startButton).toBeDisabled();
  });

  test('displays error message on service operation failure', async () => {
    api.startService = jest.fn().mockRejectedValue(new Error('Failed to start service'));

    render(<Services />);

    await waitFor(() => {
      const startButton = screen.getAllByRole('button', { name: /start/i })[0];
      fireEvent.click(startButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/error/i) || screen.getByText(/failed/i)).toBeInTheDocument();
    });
  });

  test('displays service details (PID, port, uptime)', async () => {
    render(<Services />);

    await waitFor(() => {
      expect(screen.getByText(/12345/)).toBeInTheDocument(); // PID
      expect(screen.getByText(/8188/)).toBeInTheDocument();  // Port
    });
  });

  test('refreshes service list', async () => {
    render(<Services />);

    await waitFor(() => {
      expect(api.getServices).toHaveBeenCalledTimes(1);
    });

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(api.getServices).toHaveBeenCalledTimes(2);
    });
  });

  test('filters services by status', async () => {
    render(<Services />);

    await waitFor(() => {
      expect(screen.getByText(/comfyui/i)).toBeInTheDocument();
    });

    // Filter to show only running services
    const filterSelect = screen.getByLabelText(/filter/i) ||
                        screen.getByRole('combobox');
    fireEvent.change(filterSelect, { target: { value: 'running' } });

    // Should only show running services
    expect(screen.getByText(/comfyui/i)).toBeInTheDocument();
    expect(screen.queryByText(/knowledge base/i)).not.toBeInTheDocument();
  });

  test('displays service logs', async () => {
    const mockLogs = {
      logs: [
        { timestamp: '2025-11-07T12:00:00', level: 'INFO', message: 'Server started' }
      ]
    };

    api.getServiceLogs = jest.fn().mockResolvedValue(mockLogs);

    render(<Services />);

    await waitFor(() => {
      const logsButton = screen.getAllByRole('button', { name: /logs/i })[0];
      fireEvent.click(logsButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/server started/i)).toBeInTheDocument();
    });
  });

  test('confirms before stopping critical service', async () => {
    window.confirm = jest.fn(() => true);

    render(<Services />);

    await waitFor(() => {
      const stopButton = screen.getAllByRole('button', { name: /stop/i })[0];
      fireEvent.click(stopButton);
    });

    expect(window.confirm).toHaveBeenCalled();
  });
});
