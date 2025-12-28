import React from 'react';
import { Grid, Box, Typography } from '@mui/material';
import {
  FolderOpen,
  Description,
  VideoLibrary,
  Schedule,
} from '@mui/icons-material';
import Card from '../common/Card';
import { formatRelativeDate } from './utils/fileIcons';

/**
 * Display Knowledge Base statistics in card format
 */
export const KnowledgeStats = ({ stats, loading }) => {
  if (loading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card>
              <Box height={100} display="flex" alignItems="center" justifyContent="center">
                <Typography variant="body2" color="text.secondary">
                  Loading...
                </Typography>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  if (!stats) {
    return null;
  }

  const statCards = [
    {
      title: 'Total Files',
      value: stats.total_files || 0,
      icon: FolderOpen,
      color: 'primary',
    },
    {
      title: 'Documents',
      value: stats.by_type?.document || 0,
      icon: Description,
      color: 'primary',
    },
    {
      title: 'Videos',
      value: stats.by_type?.video || 0,
      icon: VideoLibrary,
      color: 'secondary',
    },
    {
      title: 'Last Scan',
      value: stats.last_scan ? formatRelativeDate(stats.last_scan) : 'Never',
      icon: Schedule,
      color: 'success',
      isText: true,
    },
  ];

  return (
    <Grid container spacing={3}>
      {statCards.map((stat, index) => {
        const IconComponent = stat.icon;
        return (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <Box display="flex" alignItems="center" gap={2}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: (theme) => `${stat.color}.main`,
                    color: 'white',
                  }}
                >
                  <IconComponent />
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {stat.title}
                  </Typography>
                  <Typography
                    variant={stat.isText ? 'body1' : 'h4'}
                    fontWeight={stat.isText ? 600 : 700}
                    color={stat.isText ? 'text.primary' : stat.color}
                  >
                    {stat.value}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );
};

export default KnowledgeStats;
