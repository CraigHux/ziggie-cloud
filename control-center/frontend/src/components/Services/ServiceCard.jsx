import React from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Collapse,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Article as ArticleIcon,
} from '@mui/icons-material';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';

export const ServiceCard = ({ service, onAction, onViewLogs }) => {
  const [expanded, setExpanded] = React.useState(false);

  // Format uptime information
  const formatUptime = (uptimeSeconds) => {
    if (!uptimeSeconds || uptimeSeconds <= 0) return null;
    const days = Math.floor(uptimeSeconds / 86400);
    const hours = Math.floor((uptimeSeconds % 86400) / 3600);
    const minutes = Math.floor((uptimeSeconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  // Format status label with context
  const getStatusLabel = () => {
    if (service.status === 'running') {
      const uptime = formatUptime(service.uptime_seconds);
      return uptime ? `Running (${uptime} uptime)` : 'Running';
    } else if (service.status === 'stopped' && service.last_run_time) {
      const lastRun = new Date(service.last_run_time);
      const now = new Date();
      const diffMs = now - lastRun;
      const diffHours = Math.floor(diffMs / 3600000);
      const diffMins = Math.floor((diffMs % 3600000) / 60000);

      const timeAgo = diffHours > 0 ? `${diffHours}h ago` : `${diffMins}m ago`;
      return `Stopped - Last run: ${timeAgo}`;
    }
    return null;
  };

  return (
    <Card
      sx={{
        transition: 'all 0.3s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
    >
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Box>
          <Typography variant="h6" fontWeight={600}>
            {service.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {service.description || 'No description'}
          </Typography>
        </Box>
        <StatusBadge status={service.status} label={getStatusLabel()} />
      </Box>

      <Box display="flex" alignItems="center" gap={2} mb={2}>
        {service.port && (
          <Chip label={`Port: ${service.port}`} size="small" variant="outlined" />
        )}
        {service.pid && (
          <Chip label={`PID: ${service.pid}`} size="small" variant="outlined" />
        )}
      </Box>

      <Box display="flex" gap={1} flexWrap="wrap">
        {service.status === 'running' ? (
          <Button
            variant="contained"
            color="error"
            startIcon={<StopIcon />}
            onClick={() => onAction('stop', service.name)}
            size="small"
            aria-label={`Stop ${service.name} service`}
          >
            Stop
          </Button>
        ) : (
          <Button
            variant="contained"
            color="success"
            startIcon={<PlayArrowIcon />}
            onClick={() => onAction('start', service.name)}
            size="small"
            aria-label={`Start ${service.name} service`}
          >
            Start
          </Button>
        )}
        <Button
          variant="outlined"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={() => onAction('restart', service.name)}
          size="small"
          aria-label={`Restart ${service.name} service`}
        >
          Restart
        </Button>
        <Button
          variant="outlined"
          color="info"
          startIcon={<ArticleIcon />}
          onClick={() => onViewLogs(service.name)}
          size="small"
          aria-label={`View logs for ${service.name} service`}
        >
          Logs
        </Button>
      </Box>

      {service.env && Object.keys(service.env).length > 0 && (
        <Box mt={2}>
          <Button
            size="small"
            endIcon={
              <ExpandMoreIcon
                sx={{
                  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s',
                }}
              />
            }
            onClick={() => setExpanded(!expanded)}
            aria-label={expanded ? 'Hide environment variables' : 'Show environment variables'}
            aria-expanded={expanded}
          >
            Environment Variables
          </Button>
          <Collapse in={expanded}>
            <Box mt={1} p={2} bgcolor="action.hover" borderRadius={1} role="region" aria-label="Environment variables">
              {Object.entries(service.env).map(([key, value]) => (
                <Typography key={key} variant="caption" display="block">
                  <strong>{key}:</strong> {value}
                </Typography>
              ))}
            </Box>
          </Collapse>
        </Box>
      )}
    </Card>
  );
};

export default ServiceCard;
