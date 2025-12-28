import React from 'react';
import { Grid, Paper, Box, Typography, Skeleton, IconButton, Tooltip } from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import PeopleIcon from '@mui/icons-material/People';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import UpdateIcon from '@mui/icons-material/Update';
import RefreshIcon from '@mui/icons-material/Refresh';

const KnowledgeStatsWidget = ({ stats, loading, onRefresh }) => {
  const statCards = [
    {
      label: 'Total KB Files',
      value: stats?.total_files || 0,
      icon: FolderIcon,
      color: '#8B5CF6',
    },
    {
      label: 'YouTube Creators',
      value: stats?.total_creators || 0,
      icon: PeopleIcon,
      color: '#E74C3C',
    },
    {
      label: 'Videos Processed',
      value: stats?.total_videos || 0,
      icon: VideoLibraryIcon,
      color: '#3498DB',
    },
    {
      label: 'Last Scan',
      value: stats?.last_scan ? new Date(stats.last_scan).toLocaleDateString() : 'Never',
      icon: UpdateIcon,
      color: '#2ECC71',
      isText: true,
    },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#8B5CF6' }}>
          Knowledge Base Overview
        </Typography>
        <Tooltip title="Refresh stats">
          <IconButton
            onClick={onRefresh}
            aria-label="Refresh knowledge base statistics"
            sx={{
              color: '#8B5CF6',
              '&:hover': {
                bgcolor: 'rgba(139, 92, 246, 0.1)',
              },
            }}
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                height: '100%',
                background: 'linear-gradient(135deg, rgba(139,92,246,0.1) 0%, rgba(0,0,0,0) 100%)',
                borderLeft: `4px solid ${stat.color}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: `${stat.color}20`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2,
                  }}
                >
                  <stat.icon sx={{ fontSize: 32, color: stat.color }} />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ fontWeight: 500 }}
                  >
                    {stat.label}
                  </Typography>
                  {loading ? (
                    <Skeleton width={60} height={40} />
                  ) : (
                    <Typography
                      variant={stat.isText ? 'h6' : 'h4'}
                      sx={{
                        fontWeight: 700,
                        color: stat.color,
                      }}
                    >
                      {stat.value}
                    </Typography>
                  )}
                </Box>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default KnowledgeStatsWidget;