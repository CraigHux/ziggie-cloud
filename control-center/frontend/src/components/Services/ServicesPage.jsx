import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  Alert,
  Snackbar,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import ServiceCard from './ServiceCard';
import ServiceCardSkeleton from './ServiceCardSkeleton';
import LogViewer from './LogViewer';
import EmptyState from '../common/EmptyState';
import { servicesAPI } from '../../services/api';
import { translateErrorMessage } from '../../utils/errorTranslations';

export const ServicesPage = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [logViewer, setLogViewer] = useState({ open: false, serviceName: '' });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    setLoading(true);
    try {
      const response = await servicesAPI.getAll();
      const data = response.data;
      setServices(data.services || data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to load services:', err);
      setError(translateErrorMessage(err));
    } finally {
      setLoading(false);
    }
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
      // Reload services after action
      setTimeout(() => loadServices(), 1000);
    } catch (err) {
      setSnackbar({
        open: true,
        message: `Failed to ${action} ${serviceName}: ${translateErrorMessage(err)}`,
        severity: 'error',
      });
    }
  };

  const handleViewLogs = (serviceName) => {
    setLogViewer({ open: true, serviceName });
  };

  const filteredServices = services.filter(service =>
    service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (service.description && service.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h4" fontWeight={700}>
          Services
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={loadServices}
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

      <TextField
        fullWidth
        size="small"
        placeholder="Search services..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 3, maxWidth: 400 }}
      />

      <Grid container spacing={3}>
        {loading ? (
          <>
            <Grid item xs={12} md={6} lg={4}>
              <ServiceCardSkeleton />
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <ServiceCardSkeleton />
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <ServiceCardSkeleton />
            </Grid>
          </>
        ) : filteredServices.length > 0 ? (
          filteredServices.map((service) => (
            <Grid item xs={12} md={6} lg={4} key={service.name}>
              <ServiceCard
                service={service}
                onAction={handleServiceAction}
                onViewLogs={handleViewLogs}
              />
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <EmptyState
              icon={SettingsIcon}
              title="No services found"
              description={searchTerm ? 'Try adjusting your search terms' : 'No services configured'}
            />
          </Grid>
        )}
      </Grid>

      <LogViewer
        serviceName={logViewer.serviceName}
        open={logViewer.open}
        onClose={() => setLogViewer({ open: false, serviceName: '' })}
      />

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

export default ServicesPage;
