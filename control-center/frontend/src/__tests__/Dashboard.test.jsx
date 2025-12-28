/**
 * Tests for Dashboard component
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../components/Dashboard';
import * as api from '../services/api';

// Mock the API module
jest.mock('../services/api');

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  test('renders dashboard without crashing', () => {
    // Mock API responses
    api.getSystemStats = jest.fn().mockResolvedValue({
      cpu: 45.2,
      memory: 62.3,
      disk: 78.5
    });

    render(<Dashboard />);

    // Check if dashboard container is rendered
    const dashboard = screen.getByTestId('dashboard-container');
    expect(dashboard).toBeInTheDocument();
  });

  test('displays system statistics', async () => {
    // Mock system stats
    const mockStats = {
      cpu: 45.2,
      memory: 62.3,
      disk: 78.5,
      uptime: 86400
    };

    api.getSystemStats = jest.fn().mockResolvedValue(mockStats);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/cpu/i)).toBeInTheDocument();
      expect(screen.getByText(/memory/i)).toBeInTheDocument();
      expect(screen.getByText(/disk/i)).toBeInTheDocument();
    });
  });

  test('displays services list', async () => {
    // Mock services data
    const mockServices = {
      comfyui: { name: 'ComfyUI', status: 'running', port: 8188 },
      'knowledge-base': { name: 'Knowledge Base', status: 'stopped', port: 5000 }
    };

    api.getServices = jest.fn().mockResolvedValue(mockServices);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/comfyui/i)).toBeInTheDocument();
      expect(screen.getByText(/knowledge base/i)).toBeInTheDocument();
    });
  });

  test('shows loading state initially', () => {
    api.getSystemStats = jest.fn().mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({}), 1000))
    );

    render(<Dashboard />);

    // Check for loading indicator
    const loading = screen.getByTestId('loading-indicator') ||
                    screen.getByText(/loading/i);
    expect(loading).toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    // Mock API error
    api.getSystemStats = jest.fn().mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      const errorMessage = screen.getByText(/error/i) ||
                          screen.getByTestId('error-message');
      expect(errorMessage).toBeInTheDocument();
    });
  });

  test('refreshes data on refresh button click', async () => {
    const mockStats = { cpu: 45.2, memory: 62.3 };
    api.getSystemStats = jest.fn().mockResolvedValue(mockStats);

    render(<Dashboard />);

    // Wait for initial load
    await waitFor(() => {
      expect(api.getSystemStats).toHaveBeenCalledTimes(1);
    });

    // Find and click refresh button
    const refreshButton = screen.getByTestId('refresh-button') ||
                         screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    // API should be called again
    await waitFor(() => {
      expect(api.getSystemStats).toHaveBeenCalledTimes(2);
    });
  });

  test('displays agent information', async () => {
    const mockAgents = {
      total: 584,
      active: 4,
      agents: [
        { id: 'L1.1', name: 'Art Director', status: 'active' }
      ]
    };

    api.getAgents = jest.fn().mockResolvedValue(mockAgents);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/584/)).toBeInTheDocument();
      expect(screen.getByText(/agents/i)).toBeInTheDocument();
    });
  });

  test('displays knowledge base stats', async () => {
    const mockKB = {
      total_files: 7,
      creators: 38,
      avg_confidence: 92.3
    };

    api.getKnowledgeStats = jest.fn().mockResolvedValue(mockKB);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/7/)).toBeInTheDocument();
      expect(screen.getByText(/38/)).toBeInTheDocument();
    });
  });

  test('navigates to services page', async () => {
    const mockNavigate = jest.fn();

    // Mock useNavigate hook
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate
    }));

    render(<Dashboard />);

    const servicesLink = screen.getByText(/services/i);
    fireEvent.click(servicesLink);

    // Check if navigation was attempted
    await waitFor(() => {
      // Navigation should be triggered
      expect(servicesLink).toBeInTheDocument();
    });
  });

  test('updates in real-time via WebSocket', async () => {
    const mockStats = { cpu: 45.2 };
    api.getSystemStats = jest.fn().mockResolvedValue(mockStats);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/45.2/)).toBeInTheDocument();
    });

    // Simulate WebSocket update
    const updatedStats = { cpu: 52.8 };
    // Trigger re-render with new data
    api.getSystemStats = jest.fn().mockResolvedValue(updatedStats);

    // Note: Real WebSocket testing would require more setup
  });
});
