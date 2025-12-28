import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';

export const ServicesWidget = ({ services, onAction }) => {
  return (
    <Card title="Services Status">
      <List sx={{ py: 0 }}>
        {services && services.length > 0 ? (
          services.map((service, index) => (
            <React.Fragment key={service.name}>
              {index > 0 && <Divider />}
              <ListItem
                secondaryAction={
                  <Box display="flex" gap={1}>
                    {service.status === 'running' ? (
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={() => onAction && onAction('stop', service.name)}
                        color="error"
                        aria-label={`Stop ${service.name}`}
                      >
                        <StopIcon />
                      </IconButton>
                    ) : (
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={() => onAction && onAction('start', service.name)}
                        color="success"
                        aria-label={`Start ${service.name}`}
                      >
                        <PlayArrowIcon />
                      </IconButton>
                    )}
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={() => onAction && onAction('restart', service.name)}
                      color="primary"
                      aria-label={`Restart ${service.name}`}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </Box>
                }
                sx={{ py: 2 }}
              >
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={2}>
                      <Typography variant="body1" fontWeight={600}>
                        {service.name}
                      </Typography>
                      <StatusBadge status={service.status} />
                    </Box>
                  }
                  secondary={
                    service.port && `Port: ${service.port}` || service.description
                  }
                />
              </ListItem>
            </React.Fragment>
          ))
        ) : (
          <Box py={4} textAlign="center">
            <Typography variant="body2" color="text.secondary">
              No services configured
            </Typography>
          </Box>
        )}
      </List>
    </Card>
  );
};

export default ServicesWidget;
