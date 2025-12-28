import React, { useState, useEffect } from 'react';
import { Grid, Box, Typography, Alert, Snackbar } from '@mui/material';
import { Folder as FolderIcon } from '@mui/icons-material';
import SystemStats from './SystemStats';
import QuickActions from './QuickActions';
import ServicesWidget from './ServicesWidget';
import RecentActivity from './RecentActivity';
import Card from '../common/Card';
import EmptyState from '../common/EmptyState';
import DashboardSkeleton from './DashboardSkeleton';
import { systemAPI, servicesAPI, agentsAPI, knowledgeAPI } from '../../services/api';
import { translateErrorMessage } from '../../utils/errorTranslations';
import { useNavigate } from 'react-router-dom';

export const Dashboard = ({ systemData, systemDataLoading }) => {
  const navigate = useNavigate();
  const [services, setServices] = useState([]);
  const [agents, setAgents] = useState(null);
  const [recentKnowledge, setRecentKnowledge] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [servicesRes, agentsRes, knowledgeRes] = await Promise.allSettled([
        servicesAPI.getAll(),
        agentsAPI.getSummary(),
        knowledgeAPI.getRecent(5),
      ]);

      if (servicesRes.status === 'fulfilled') {
        const data = servicesRes.value.data;
        setServices(data.services || data || []);
      }
      if (agentsRes.status === 'fulfilled') {
        const data = agentsRes.value.data;
        // Map backend format to frontend format
        setAgents({
          total: data.total || 0,
          l1: data.l1_count || 0,
          l2: data.l2_count || 0,
          l3: data.l3_count || 0,
        });
      }
      if (knowledgeRes.status === 'fulfilled') {
        const data = knowledgeRes.value.data;
        setRecentKnowledge(data.files || data || []);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError(translateErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (action) => {
    console.log('Quick action:', action);
    setSnackbar({
      open: true,
      message: `Action "${action}" triggered`,
      severity: 'info',
    });
  };

  const handleServiceAction = async (action, serviceName) => {
    try {
      if (action === 'start') {
        await servicesAPI.start(serviceName);
      } else if (action === 'stop') {
        await servicesAPI.stop(serviceName);
      } else if (action === 'restart') {
        await servicesAPI.restart(serviceName);
      }
      setSnackbar({
        open: true,
        message: `${serviceName} ${action} successful`,
        severity: 'success',
      });
      loadDashboardData();
    } catch (err) {
      setSnackbar({
        open: true,
        message: `Failed to ${action} ${serviceName}: ${translateErrorMessage(err)}`,
        severity: 'error',
      });
    }
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} mb={3}>
        Dashboard
      </Typography>

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

        {/* Services and Quick Actions */}
        <Grid item xs={12} md={6}>
          <ServicesWidget services={services} onAction={handleServiceAction} />
        </Grid>
        <Grid item xs={12} md={6}>
          <QuickActions onAction={handleQuickAction} />
        </Grid>

        {/* Agent Summary */}
        <Grid item xs={12} md={4}>
          <Card title="Agent Summary">
            <Box display="flex" flexDirection="column" gap={2}>
              <Box>
                <Typography variant="h3" fontWeight={700} color="primary">
                  {agents?.total || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Agents
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {agents?.l1 || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    L1 Agents
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {agents?.l2 || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    L2 Agents
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {agents?.l3 || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    L3 Agents
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Card>
        </Grid>

        {/* Recent Knowledge */}
        <Grid item xs={12} md={4}>
          <Card title="Recent Knowledge">
            {recentKnowledge.length > 0 ? (
              <Box display="flex" flexDirection="column" gap={1}>
                {recentKnowledge.map((item, index) => (
                  <Box key={index} py={1} borderBottom="1px solid" borderColor="divider">
                    <Typography variant="body2" fontWeight={600} noWrap>
                      {item.title || item.name || item.filename || 'Untitled'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {item.agent || item.type || 'Knowledge'} - {new Date(item.modified || item.timestamp || Date.now()).toLocaleDateString()}
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <EmptyState
                icon={FolderIcon}
                title="No knowledge files yet"
                description="Knowledge items will appear here"
                actionLabel="Browse Knowledge Base"
                onAction={() => navigate('/knowledge')}
                compact
              />
            )}
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <RecentActivity activities={recentActivity} />
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Dashboard;
