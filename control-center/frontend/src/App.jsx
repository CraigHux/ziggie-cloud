import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createAppTheme } from './theme';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import LoginPage from './components/Auth/LoginPage';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import ServicesPage from './components/Services/ServicesPage';
import SystemPage from './components/System/SystemPage';
import AgentsPage from './components/Agents/AgentsPage';
import KnowledgePage from './components/Knowledge/KnowledgePage';
import LLMTestPage from './components/LLM/LLMTestPage';
import useWebSocket from './hooks/useWebSocket';

// AppRouter component - renders INSIDE Router context
function AppRouter({ darkMode, onToggleDarkMode }) {
  const location = useLocation();
  const [systemDataLoading, setSystemDataLoading] = useState(true);
  const [systemData, setSystemData] = useState({
    cpu: { usage: 0, history: [] },
    memory: { percent: 0, history: [] },
    disk: { percent: 0, history: [] },
  });

  // Only initialize WebSocket on pages that need real-time system stats
  const needsWebSocket = ['/', '/system', '/services'].some(path =>
    location.pathname === path || location.pathname.startsWith(path)
  );

  // WebSocket connection for real-time updates (conditional)
  const { isConnected: wsConnected } = useWebSocket(needsWebSocket ? (data) => {
    if (data.type === 'system_stats') {
      // Backend sends usage_percent instead of usage
      const cpuUsage = data.cpu?.usage_percent || data.cpu?.usage || 0;
      const memoryPercent = data.memory?.percent || 0;
      const diskPercent = data.disk?.percent || 0;

      setSystemData(prevData => ({
        cpu: {
          usage: cpuUsage,
          usage_percent: cpuUsage,
          history: [...(prevData.cpu?.history || []).slice(-29), { value: cpuUsage }],
        },
        memory: {
          percent: memoryPercent,
          history: [...(prevData.memory?.history || []).slice(-29), { value: memoryPercent }],
        },
        disk: {
          percent: diskPercent,
          history: [...(prevData.disk?.history || []).slice(-29), { value: diskPercent }],
        },
      }));

      // First data received, stop showing loading state
      if (systemDataLoading) {
        setSystemDataLoading(false);
      }
    }
  } : null);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout
              darkMode={darkMode}
              onToggleDarkMode={onToggleDarkMode}
              wsConnected={wsConnected}
            >
              <Routes>
                <Route path="/" element={<Dashboard systemData={systemData} systemDataLoading={systemDataLoading} />} />
                <Route path="/services" element={<ServicesPage />} />
                <Route path="/agents" element={<AgentsPage />} />
                <Route path="/knowledge" element={<KnowledgePage />} />
                <Route path="/system" element={<SystemPage systemData={systemData} systemDataLoading={systemDataLoading} />} />
                <Route path="/llm-test" element={<LLMTestPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

// App component - top-level provider wrapper
function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [theme, setTheme] = useState(createAppTheme('dark'));

  const handleToggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    setTheme(createAppTheme(newMode ? 'dark' : 'light'));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <AppRouter darkMode={darkMode} onToggleDarkMode={handleToggleDarkMode} />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
