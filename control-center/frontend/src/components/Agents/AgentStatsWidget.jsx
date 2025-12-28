import React from 'react';
import { Grid, Paper, Box, Typography, Skeleton } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import LayersIcon from '@mui/icons-material/Layers';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import PsychologyIcon from '@mui/icons-material/Psychology';

const AgentStatsWidget = ({ stats, loading }) => {
  const statCards = [
    {
      label: 'Total Agents',
      value: stats?.total || 0,
      icon: SmartToyIcon,
      color: '#FF8C42',
    },
    {
      label: 'L1 Agents',
      value: stats?.by_level?.L1 || 0,
      icon: LayersIcon,
      color: '#E74C3C',
    },
    {
      label: 'L2 Agents',
      value: stats?.by_level?.L2 || 0,
      icon: AccountTreeIcon,
      color: '#3498DB',
    },
    {
      label: 'L3 Agents',
      value: stats?.by_level?.L3 || 0,
      icon: PsychologyIcon,
      color: '#2ECC71',
    },
  ];

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {statCards.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Paper
            elevation={2}
            sx={{
              p: 3,
              height: '100%',
              background: 'linear-gradient(135deg, rgba(255,140,66,0.1) 0%, rgba(0,0,0,0) 100%)',
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
                    variant="h4"
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
  );
};

export default AgentStatsWidget;
