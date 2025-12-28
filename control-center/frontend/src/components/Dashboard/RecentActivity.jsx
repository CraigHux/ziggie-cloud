import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
} from '@mui/material';
import { History as HistoryIcon } from '@mui/icons-material';
import Card from '../common/Card';
import EmptyState from '../common/EmptyState';

const formatTimeAgo = (timestamp) => {
  if (!timestamp) return 'Just now';
  const now = new Date();
  const then = new Date(timestamp);
  const seconds = Math.floor((now - then) / 1000);

  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

export const RecentActivity = ({ activities }) => {
  return (
    <Card title="Recent Activity">
      <List sx={{ py: 0 }}>
        {activities && activities.length > 0 ? (
          activities.map((activity, index) => (
            <React.Fragment key={activity.id || index}>
              {index > 0 && <Divider />}
              <ListItem sx={{ py: 2, alignItems: 'flex-start' }}>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                      <Typography variant="body2" fontWeight={600}>
                        {activity.title}
                      </Typography>
                      {activity.type && (
                        <Chip
                          label={activity.type}
                          size="small"
                          color={
                            activity.type === 'error' ? 'error' :
                            activity.type === 'warning' ? 'warning' :
                            activity.type === 'success' ? 'success' : 'default'
                          }
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {activity.description}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatTimeAgo(activity.timestamp)}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            </React.Fragment>
          ))
        ) : (
          <EmptyState
            icon={HistoryIcon}
            title="No recent activity"
            description="System events will appear here"
            compact
          />
        )}
      </List>
    </Card>
  );
};

export default RecentActivity;
