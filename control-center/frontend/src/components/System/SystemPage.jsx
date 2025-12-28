import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  Alert,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import SystemStats from '../Dashboard/SystemStats';
import ProcessList from './ProcessList';
import PortScanner from './PortScanner';
import Card from '../common/Card';
import SystemMetricSkeleton from "./SystemMetricSkeleton";
import { systemAPI } from '../../services/api';
import { translateErrorMessage } from '../../utils/errorTranslations';

export const SystemPage = ({ systemData, systemDataLoading }) => {
  const [processes, setProcesses] = useState([]);
  const [ports, setPorts] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSystemData();
  }, []);

  const loadSystemData = async () => {
    setLoading(true);
    try {
      const [processesRes, portsRes, infoRes] = await Promise.allSettled([
        systemAPI.getProcesses(),
        systemAPI.getPorts(),
        systemAPI.getInfo(),
      ]);

      if (processesRes.status === 'fulfilled') {
        const data = processesRes.value.data;
        setProcesses(data.processes || data || []);
      }
      if (portsRes.status === 'fulfilled') {
        const data = portsRes.value.data;
        setPorts(data.ports || data || []);
      }
      if (infoRes.status === 'fulfilled') {
        setSystemInfo(infoRes.value.data);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to load system data:', err);
      setError(translateErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  if (loading && !systemInfo) {
    return <SystemMetricSkeleton />;
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h4" fontWeight={700}>
          System Monitor
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={loadSystemData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* System Stats */}
        <Grid item xs={12}>
          <SystemStats stats={systemData} loading={systemDataLoading} />
        </Grid>

        {/* System Information */}
        {systemInfo && (
          <Grid item xs={12} md={6}>
            <Card title="System Information">
              <Box display="flex" flexDirection="column" gap={1.5}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Platform
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {systemInfo.platform || 'Unknown'}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Architecture
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {systemInfo.arch || 'Unknown'}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Hostname
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {systemInfo.hostname || 'Unknown'}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Total Memory
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {systemInfo.totalMemory
                      ? `${(systemInfo.totalMemory / (1024 ** 3)).toFixed(2)} GB`
                      : 'Unknown'}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    CPU Cores
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {systemInfo.cpuCores || 'Unknown'}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Uptime
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {systemInfo.uptime
                      ? `${Math.floor(systemInfo.uptime / 3600)}h ${Math.floor((systemInfo.uptime % 3600) / 60)}m`
                      : 'Unknown'}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>
        )}

        {/* Quick Stats */}
        <Grid item xs={12} md={6}>
          <Card title="Quick Stats">
            <Box display="flex" flexDirection="column" gap={1.5}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">
                  Running Processes
                </Typography>
                <Typography variant="h6" fontWeight={600} color="primary">
                  {processes.length}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">
                  Open Ports
                </Typography>
                <Typography variant="h6" fontWeight={600} color="secondary">
                  {ports.length}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">
                  Top CPU Process
                </Typography>
                <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 200 }}>
                  {processes.length > 0
                    ? processes.reduce((max, proc) => (proc.cpu > max.cpu ? proc : max), processes[0]).name
                    : 'N/A'}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">
                  Top Memory Process
                </Typography>
                <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 200 }}>
                  {processes.length > 0
                    ? processes.reduce((max, proc) => (proc.memory > max.memory ? proc : max), processes[0]).name
                    : 'N/A'}
                </Typography>
              </Box>
            </Box>
          </Card>
        </Grid>

        {/* Port Scanner */}
        <Grid item xs={12}>
          <PortScanner ports={ports} />
        </Grid>

        {/* Process List */}
        <Grid item xs={12}>
          <ProcessList processes={processes} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemPage;
